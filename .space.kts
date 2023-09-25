/**
 * JetBrains Space Automation
 * This Kotlin script file lets you automate build activities
 * For more info, see https://www.jetbrains.com/help/space/automation.html
 */

job("Prepare testcontainer image") {
    // do not run on git push
    startOn {
        gitPush { enabled = false }
    }

    kaniko {
        build {
            dockerfile = "./tests/testcontainer/Dockerfile"
            labels["vendor"] = "bastelquartier.de"
        }

        push("bastelquartier.registry.jetbrains.space/p/fapi-el/testcontainer/testcontainer") {
            tags {
                +"0.0.1"
            }
        }
    }
}

job("Run tests") {
    startOn {
        gitPush { enabled = false }
    }

    container(image = "bastelquartier.registry.jetbrains.space/p/fapi-el/testcontainer/testcontainer:0.0.1") {
        env["URL"] = "https://pypi.pkg.jetbrains.space/bastelquartier/p/fapi-el/controllogger/legacy"
        shellScript {
            content = """
                #echo Run tests...
                #pytest ./tests/
            """
        }
    }
}

job("Build and publish to Space") {
    startOn {
        gitPush { enabled = false }
    }

    container(image = "bastelquartier.registry.jetbrains.space/p/fapi-el/testcontainer/testcontainer:0.0.1") {
        env["URL"] = "https://pypi.pkg.jetbrains.space/bastelquartier/p/fapi-el/controllogger/legacy"
        shellScript {
            content = """
                echo Build package...
                python setup.py -bV ${'$'}JB_SPACE_EXECUTION_NUMBER build
                echo Upload package...
                twine upload --repository-url ${'$'}URL -u ${'$'}JB_SPACE_CLIENT_ID -p ${'$'}JB_SPACE_CLIENT_SECRET dist/*
            """
        }
    }
}