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
            file = "./tests/testcontainer/Dockerfile"
            labels["vendor"] = "bastelquartier.de"
        }

        push("bastelquartier.registry.jetbrains.space/p/fapi-el/testcontainer/testcontainer") {
            tags {
                +"0.0.1"
            }
        }
    }
}

job("Example shell script") {
    container(displayName = "Say Hello", image = "ubuntu") {
        shellScript {
            content = """
                echo Hello
                echo World!
                #python setup.py sdist
            """
        }
    }
}
