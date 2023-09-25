import subprocess
import sys
from pathlib import Path

import codecs
import os.path


def setup_exit(exit_code: int = 0, message: str = None):
    if message is not None:
        print(message)
    raise SystemExit(exit_code)


def _read(rel_path: Path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path: str | Path) -> str:
    if isinstance(rel_path, str):
        rel_path = Path(rel_path)
    for line in _read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            v = line.split(delim)[1]
            break
    else:
        raise RuntimeError("Unable to find version string.")
    if build_version:
        v += f".{build_version}"
    return v


def print_version(rel_path: str | Path):
    print(f"Current version: {get_version(rel_path)}")
    setup_exit(0)


def _build():
    # run sdist
    cmd = ["python", "setup.py"]
    if build_version:
        cmd.append("--build-version")
        cmd.append(build_version)
    cmd.append("sdist")
    if subprocess.run(cmd).returncode != 0:
        setup_exit(1, "Building sdist failed.")


def _setup():
    from setuptools import setup
    setup(version=get_version("src/controllogger/__init__.py"))


if __name__ == "__main__":
    if "-v" in sys.argv or "--version" in sys.argv:
        print_version("src/controllogger/__init__.py")

    build_version = None
    if "-bV" in sys.argv or "--build-version" in sys.argv:
        index = sys.argv.index("-bV" if "-bV" in sys.argv else "--build-version") + 1
        if index >= len(sys.argv):
            setup_exit(1, "Missing version number.")
        if sys.argv[index].startswith("-"):
            setup_exit(1, "Missing version number.")
        build_version = sys.argv[index]
        sys.argv.pop(index)
        sys.argv.pop(index - 1)

    if "build" in sys.argv:
        _build()
    else:
        _setup()
