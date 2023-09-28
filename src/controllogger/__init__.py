import os
from pathlib import Path

import setuptools

__author__ = "Julius Koenig"
__version__ = "0.2.8"

# overwrite version if "__dev_version__" is set in environment
if "__dev_version__" in os.environ:
    __version__ = os.environ["__dev_version__"]

__script_start_file__ = os.getcwd()
__site_packages_path__ = str(Path(setuptools.__file__).parent.parent)
__lib_path__ = str(Path(os.__file__).parent)
__module_path__ = os.path.dirname(os.path.abspath(__file__))
__module_files__ = []
