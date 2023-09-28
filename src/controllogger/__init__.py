import os
from pathlib import Path

import setuptools

__script_start_file__ = os.getcwd()
__site_packages_path__ = str(Path(setuptools.__file__).parent.parent)
__lib_path__ = str(Path(os.__file__).parent)
__module_path__ = os.path.dirname(os.path.abspath(__file__))
__module_files__ = []
__author__ = "Julius Koenig"
__version_file__ = str(Path(__module_path__) / "__version__")
__version__ = open(__version_file__).read()
