import dataclasses
from pathlib import Path
from typing import Union, Optional

from controllogger.enums.log_levels import LogLevels
from controllogger.enums.terminal_out_file import TerminalOutFile
from controllogger.misc.base_dataclass import BaseDataclass


@dataclasses.dataclass
class LoggerDefaultsConfig(BaseDataclass):
    name: str = None  # Used as base name for output loggers.
    level: Union[LogLevels, int] = LogLevels.NOTSET  # Default log level for output loggers. Default is NOTSET.
    last_resort: bool = False  # Default last resort for output loggers. Last resort is used when the output logger is not able to handle the log record.
    log_events: bool = False  # Default log events for output loggers. Is used to log events to loggers. Default is False.
    log_init: Optional[bool] = None  # Default log init for input and output loggers. Is used to log the init event to loggers. Default is False.
    log_attach: Optional[bool] = None  # Default log attach for input and output loggers. Is used to log the attach event to loggers. Default is False.
    log_detach: Optional[bool] = None  # Default log detach for input and output loggers. Is used to log the detach event to loggers. Default is False.
    log_destroy: Optional[bool] = None  # Default log destroy for input and output loggers. Is used to log the destroy event to loggers. Default is False.

    # Default values for output logger
    header_width: int = 110  # Default header width. Default is 110.
    console: bool = False  # Default console. Default is False.
    console_format: str = "[%(asctime)s][%(name)s][%(levelname)s] %(srcRelativePathname)s(%(srcLineno)s) -> %(relativePathname)s(%(lineno)s) - %(message)s"  # Default console format. Default is %(name)s\t - %(message)s.
    console_outfile: TerminalOutFile = TerminalOutFile.STDOUT  # Default console outfile. Default is STDOUT.
    console_width: int = 160  # Default console width. Default is 160(my preferred width with 49 inch monitor ^^).
    console_rich_force_terminal: bool = False  # Default console rich force terminal. Default is False. Only used if rich is installed.
    file_path: Union[Path, str] = Path("logs")  # Base path for used by file output loggers. If a relative path is given, it will be relative to the current working directory.
    file_format: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"  # Default file format. Default is %(asctime)s - %(levelname)s - %(name)s - %(message)s.
    file_mode: str = "a"  # Default file mode. Default is a.
    file_max_size: int = 1024 * 1024 * 10  # Default file max size. Default is 10 MB.
    file_backup_count: int = 0  # Default file backup count. Default is 0.
    file_encoding: str = "utf-8"  # Default file encoding. Default is utf-8.
    file_delay: bool = False  # Default file delay. Default is False.
    file_archive_backup_count: int = 0  # Default file archive backup count. Default is 0.
    db_buffer_max_lines: int = 100  # Default db buffer max lines. Default is 100.
    db_buffer_max_time: int = 10  # Default db buffer max time. Default is 10.
