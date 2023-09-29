import logging
from abc import ABC
from pathlib import Path
from typing import Union

import controllogger


class BaseEasyLogger(logging.Logger, ABC):

    @staticmethod
    def _pars_relative_path(path: Union[Path, str], relative_path: Union[Path, str]) -> tuple[bool, str]:
        try:
            relative_path_name = str(Path(path).relative_to(relative_path))
        except ValueError:
            return False, path
        return True, relative_path_name

    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)

        i = 1
        previous_frame = None
        while True:
            frame = self.findCaller(stacklevel=i)
            if previous_frame is not None:
                if previous_frame == frame:
                    break
            if controllogger.__script_start_file__ in frame[0]:
                break
            previous_frame = frame
            i += 1
        _, src_relative_path_name = self._pars_relative_path(frame[0], controllogger.__script_start_file__)
        result, relative_path_name = self._pars_relative_path(path=record.pathname, relative_path=controllogger.__script_start_file__)
        if not result:
            result, relative_path_name = self._pars_relative_path(path=record.pathname, relative_path=controllogger.__module_path__)
            if not result:
                result, relative_path_name = self._pars_relative_path(path=record.pathname, relative_path=controllogger.__lib_path__)
                if not result:
                    result, relative_path_name = self._pars_relative_path(path=record.pathname, relative_path=controllogger.__site_packages_path__)
                    if not result:
                        relative_path_name = record.pathname

        for key, value in {
            "relativePathname": relative_path_name,
            "srcPathname": frame[0],
            "srcRelativePathname": src_relative_path_name,
            "srcFilename": Path(frame[0]).name,
            "srcLineno": frame[1],
            "srcFunctionName": frame[2],
            "srcStackLevel": i
        }.items():
            if hasattr(record, key):
                raise ValueError(f"Record already has attribute '{key}'.")
            setattr(record, key, value)
        return record
