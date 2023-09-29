import dataclasses
from pathlib import Path
from typing import Optional, Union

from controllogger.enums.terminal_out_file import TerminalOutFile
from controllogger.misc.base_logger_config import BaseLoggerConfig
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig
from controllogger.misc.filter import Filter


@dataclasses.dataclass
class OutputLoggerConfig(BaseLoggerConfig):
    filter: list[Filter] = dataclasses.field(default_factory=list)  # List of filters
    last_resort: Optional[bool] = None  # Last resort of output logger
    header_width: Optional[int] = None  # Header width of output logger
    console: bool = False  # Enable console output
    console_format: Optional[str] = None  # Console format of output logger
    console_outfile: Optional[TerminalOutFile] = None  # Console outfile of output logger
    console_width: Optional[int] = None  # Console width of output logger
    console_rich_force_terminal: Optional[bool] = None  # Default console rich force terminal. Only used if rich is installed.
    file: bool = False  # Enable file output
    file_format: Optional[str] = None  # File format of output logger
    file_path: Union[Path, str, None] = None  # File path of output logger
    file_mode: Optional[str] = None  # File mode of output logger
    file_max_size: Optional[int] = None  # File max size of output logger
    file_backup_count: Optional[int] = None  # File backup count of output logger
    file_encoding: Optional[str] = None  # File encoding of output logger
    file_delay: Optional[bool] = None  # File delay of output logger
    file_archive_backup_count: Optional[int] = None  # File archive backup count of output logger
    db: bool = False  # Enable db output
    db_format: Optional[str] = None  # DB format of output logger
    db_buffer_max_lines: Optional[int] = None  # DB buffer max lines of output logger
    db_buffer_max_time: Optional[int] = None  # DB buffer max time of output logger

    def __default_init__(self, logger_defaults_config: LoggerDefaultsConfig):
        super().__default_init__(logger_defaults_config)
        # setup None values

        # last_resort
        if self.last_resort is None:
            self.last_resort = logger_defaults_config.last_resort

        # header_width
        if self.header_width is None:
            self.header_width = logger_defaults_config.header_width

        # console
        if self.console:
            # console_format
            if self.console_format is None:
                self.console_format = logger_defaults_config.console_format
            # console_outfile
            if self.console_outfile is None:
                self.console_outfile = logger_defaults_config.console_outfile
            # console_width
            if self.console_width is None:
                self.console_width = logger_defaults_config.console_width
            # console_rich_force_terminal
            if self.console_rich_force_terminal is None:
                self.console_rich_force_terminal = logger_defaults_config.console_rich_force_terminal

        # file
        if self.file:
            # file_format
            if self.file_format is None:
                self.file_format = logger_defaults_config.file_format
            # file_path
            if self.file_path is None:
                self.file_path = Path(logger_defaults_config.file_path) / f"{self.name}.log"
            # file_mode
            if self.file_mode is None:
                self.file_mode = logger_defaults_config.file_mode
            # file_max_size
            if self.file_max_size is None:
                self.file_max_size = logger_defaults_config.file_max_size
            # file_backup_count
            if self.file_backup_count is None:
                self.file_backup_count = logger_defaults_config.file_backup_count
            # file_encoding
            if self.file_encoding is None:
                self.file_encoding = logger_defaults_config.file_encoding
            # file_delay
            if self.file_delay is None:
                self.file_delay = logger_defaults_config.file_delay
            # file_archive_backup_count
            if self.file_archive_backup_count is None:
                self.file_archive_backup_count = logger_defaults_config.file_archive_backup_count

        # db
        if self.db:
            # db_format
            if self.db_format is None:
                self.db_format = logger_defaults_config.db_format
            # db_buffer_max_lines
            if self.db_buffer_max_lines is None:
                self.db_buffer_max_lines = logger_defaults_config.db_buffer_max_lines
            # db_buffer_max_time
            if self.db_buffer_max_time is None:
                self.db_buffer_max_time = logger_defaults_config.db_buffer_max_time
