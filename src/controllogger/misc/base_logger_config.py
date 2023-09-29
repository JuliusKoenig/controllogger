import dataclasses
import logging
from typing import Type, Union, Optional

from controllogger.enums.log_levels import LogLevels
from controllogger.misc.base_dataclass import BaseDataclass
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig


@dataclasses.dataclass
class BaseLoggerConfig(BaseDataclass):
    name: str  # Name of logger
    level: Union[LogLevels, int, None] = None  # Level of logger

    # log events
    log_events: Optional[bool] = None  # Log events for logger. Is used to log events to logger. Default is False.
    log_init: Optional[bool] = None  # Log init for input for logger. Is used to log the init event to loggers. Default is False.
    log_attach: Optional[bool] = None  # Log attach for logger. Is used to log the attach event to logger. Default is False.
    log_detach: Optional[bool] = None  # Log detach for logger. Is used to log the detach event to logger. Default is False.
    log_destroy: Optional[bool] = None  # Log destroy for logger. Is used to log the destroy event to logger. Default is False.

    # custom logger cls
    logger_cls: Type[logging.Logger] = None

    def __default_init__(self, logger_defaults_config: LoggerDefaultsConfig):
        # setup None values

        # level
        if self.level is None:
            self.level = logger_defaults_config.level

        # log_events
        if self.log_events is None:
            self.log_events = logger_defaults_config.log_events

        # log_init
        if self.log_init is None:
            if logger_defaults_config.log_init is None:
                self.log_init = self.log_events
            else:
                self.log_init = logger_defaults_config.log_init

        # log_attach
        if self.log_attach is None:
            if logger_defaults_config.log_attach is None:
                self.log_attach = self.log_events
            else:
                self.log_attach = logger_defaults_config.log_attach

        # log_detach
        if self.log_detach is None:
            if logger_defaults_config.log_detach is None:
                self.log_detach = self.log_events
            else:
                self.log_detach = logger_defaults_config.log_detach

        # log_destroy
        if self.log_destroy is None:
            if logger_defaults_config.log_destroy is None:
                self.log_destroy = self.log_events
            else:
                self.log_destroy = logger_defaults_config.log_destroy
