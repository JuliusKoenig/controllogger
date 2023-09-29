import logging
from datetime import datetime
from typing import Union

from controllogger.enums.log_levels import LogLevels
from controllogger.enums.operator import Operator
from controllogger.handler.python_console_handler import PythonConsoleHandler
from controllogger.handler.tar_rotating_file_handler import TarRotatingFileHandler
from controllogger.logger.base import BaseLogger
from controllogger.misc.easy_logger import easy_logger
from controllogger.misc.output_logger_config import OutputLoggerConfig

# try to import rich console handler
try:
    from controllogger.handler.rich_console_handler import RichConsoleHandler
except Exception:
    RichConsoleHandler = None
    pass  # todo for now its okay but later we need to handle this


class OutputLogger(BaseLogger):
    _ConfigClass = OutputLoggerConfig
    _my_type = "Output Logger"
    _control_logger_type_field = "output_logger_type"

    def __init__(self, name: str = None, level: Union[LogLevels, int] = logging.NOTSET, config: Union[_ConfigClass, dict[str, any]] = None):
        self._use_control_logger_name = True
        super().__init__(name=name, level=level, config=config)

        # check if logger already exists
        if self.name in self.manager.loggerDict:
            raise ValueError(f"Logger '{self.name}' already exists.")

        # add logger to logging.root.manager.loggerDict
        self.manager.loggerDict[self.name] = self

        self._disable_filter = False

        # if console
        if self.config.console:
            # try to create rich console handler
            if RichConsoleHandler is not None:
                self.console_handler = RichConsoleHandler(console_outfile=self.config.console_outfile,
                                                          console_width=self.config.console_width,
                                                          console_force_terminal=self.config.console_force_terminal)
            else:
                self.console_handler = PythonConsoleHandler(console_outfile=self.config.console_outfile,
                                                            console_width=self.config.console_width)

            # set console_header_width to config.console_width if console_header_width is greater than config.console_width
            console_header_width = self.config.header_width
            if console_header_width > self.config.console_width:
                console_header_width = self.config.console_width

            # set console header width
            self.console_handler.header_width = console_header_width

            # set console handler level to NOTSET to allow all records to be passed to console handler
            self.console_handler.setLevel(logging.NOTSET)

            # create console handler formatter
            self.console_formatter = logging.Formatter(self.config.console_format)

            # set console handler formatter
            self.console_handler.setFormatter(self.console_formatter)

            # add console handler to self
            self.addHandler(self.console_handler)

        # if file
        if self.config.file:
            # create directory if not exists
            self.config.file_path.parent.mkdir(parents=True, exist_ok=True)

            # create file handler
            self.file_handler = TarRotatingFileHandler(
                filename=self.config.file_path,
                backup_count=self.config.file_backup_count,
                max_bytes=self.config.file_max_size,
                archive_backup_count=self.config.file_archive_backup_count,
                encoding=self.config.file_encoding,
                delay=self.config.file_delay,
                mode=self.config.file_mode,
            )

            # set file_header_width
            self.file_handler.header_width = self.config.header_width

            # set file handler level to NOTSET to allow all records to be passed to file handler
            self.file_handler.setLevel(logging.NOTSET)

            # create file handler formatter
            self.file_formatter = logging.Formatter(self.config.file_format)

            # set file handler formatter
            self.file_handler.setFormatter(self.file_formatter)

            # add file handler to self
            self.addHandler(self.file_handler)

        # if db
        if self.config.db:
            # create db handler
            self.db_handler = DbLogHandler(log_document=self.config.db_document,
                                           buffer_max_lines=self.config.db_buffer_max_lines,
                                           buffer_max_time=self.config.db_buffer_max_time)

            # set db_header_width
            self.db_handler.header_width = self.config.header_width

            # set db handler level to NOTSET to allow all records to be passed to db handler
            self.db_handler.setLevel(logging.NOTSET)

            # create db handler formatter
            self.db_formatter = logging.Formatter(self.config.db_format)

            # set db handler formatter
            self.db_handler.setFormatter(self.db_formatter)

            # add db handler to self
            self.addHandler(self.db_handler)

        # add logger to control logger
        self.attach()

    def __del__(self):
        # remove logger from control logger
        if not self.open:
            return
        super().__del__()
        self.detach()
        # delete logger from logging.root.manager.loggerDict
        del self.control_logger.all_logger[self.name]

    def __str__(self) -> str:
        r = f"{self.__class__.__name__}(name={self.name}, level={LogLevels(self.level).name}, "
        if self.closed:
            r = r[:-2]
            r += ") CLOSED"
            return r
        if not self.attached:
            r = r[:-2]
            r += ") DETACHED"
            return r
        if len(self.contexts) > 0:
            r += f"contexts=({', '.join([str(context) for context in self.contexts])}), "
        if self.config.console:
            console = self.config.console_outfile.value
            r += f"console --> {console}, "

        if self.config.file:
            file_path = str(self.config.file_path)
            r += f"file --> {file_path}, "
        if self.config.db:
            db_document = "self.db_document.__class__.__name__"
            r += f"db --> {db_document}, "
        r = r[:-2]
        r += ")"

        return r

    def print_logger_initialized(self):
        if self.config.log_init:
            self._disable_filter = True
            self.print_header(
                name=f"{self._my_type} '{self.name}' initialized at {datetime.now()}",
                level=LogLevels.DEBUG,
                lines=[str(self)],
            )
            self._disable_filter = False

    def attach(self) -> None:
        """
        Attach the output logger to the control logger
        :return: None
        """

        if self.attached:
            raise ValueError(f"Logger '{self.name}' already attached.")
        if self.name in self.control_logger.output_loggers.keys():
            raise ValueError(f"Output logger for '{self.name}' already exists.")
        self.control_logger.output_loggers[self.name] = self
        super().attach()

    def detach(self) -> None:
        """
        Detach the output logger from the control logger
        :return: None
        """

        if not self.attached:
            raise ValueError(f"Logger '{self.name}' already detached.")
        if self.name not in self.control_logger.output_loggers.keys():
            raise ValueError(f"Output logger for '{self.name}' not found.")
        super().detach()
        del self.control_logger.output_loggers[self.name]

    @property
    def attached(self) -> bool:
        """
        Checks if output logger is attached to control logger

        :return: True if attached, False if not
        """

        for logger_name in self.control_logger.output_loggers.keys():
            if logger_name == self.name:
                return True
        return False

    def handle(self, record):
        # check if last resort enabled and set level to 999
        backup_last_resort_level = logging.lastResort.level
        if not self.config.last_resort:
            logging.lastResort.level = 999

        if (not self.disabled) and self.filter(record):
            self.callHandlers(record)

        # reset last resort level
        if not self.config.last_resort:
            logging.lastResort.level = backup_last_resort_level

    def filter(self, record) -> bool:
        if self._disable_filter:
            return True
        if self.config.filter:
            return self._filter(record)
        else:
            return True

    def _filter(self, record) -> bool:
        out = False
        for log_filter in self.config.filter:
            try:
                record_value = getattr(record, log_filter.key)

                # ToDo: at the moment this simple implementation is enough but but we have plans to conquer the whole world with this filter so keep gespannt wie n Flitzebogen

                # EQUALS
                if log_filter.operator == Operator.EQUALS:
                    if log_filter.value == record_value:
                        out = True
                        break
                # NOT_EQUALS
                elif log_filter.operator == Operator.NOT_EQUALS:
                    if log_filter.value != record_value:
                        out = True
                        break
                # CONTAINS
                elif log_filter.operator == Operator.CONTAINS:
                    if log_filter.value in record_value:
                        out = True
                        break
                # NOT_CONTAINS
                elif log_filter.operator == Operator.NOT_CONTAINS:
                    if log_filter.value not in record_value:
                        out = True
                        break
                # STARTS_WITH
                elif log_filter.operator == Operator.STARTS_WITH:
                    if record_value.startswith(log_filter.value):
                        out = True
                        break
                # ENDS_WITH
                elif log_filter.operator == Operator.ENDS_WITH:
                    if record_value.endswith(log_filter.value):
                        out = True
                        break
                # GREATER_THAN
                elif log_filter.operator == Operator.GREATER_THAN:
                    if log_filter.value > record_value:
                        out = True
                        break
                # GREATER_THAN_OR_EQUAL
                elif log_filter.operator == Operator.GREATER_THAN_OR_EQUAL:
                    if log_filter.value >= record_value:
                        out = True
                        break
                # LESS_THAN
                elif log_filter.operator == Operator.LESS_THAN:
                    if log_filter.value < record_value:
                        out = True
                        break
                # LESS_THAN_OR_EQUAL
                elif log_filter.operator == Operator.LESS_THAN_OR_EQUAL:
                    if log_filter.value <= record_value:
                        out = True
                        break
                else:
                    raise ValueError(f"Operator '{log_filter.operator}' not supported")

            except Exception as e:
                easy_logger.exception(f"Error while filtering log record: {e}")
                out = True

        return out
