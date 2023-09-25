import os
from pathlib import Path

import setuptools

__script_start_file__ = os.getcwd()
__site_packages_path__ = str(Path(setuptools.__file__).parent.parent)
__lib_path__ = str(Path(os.__file__).parent)
__module_path__ = os.path.dirname(os.path.abspath(__file__))
__module_files__ = []

