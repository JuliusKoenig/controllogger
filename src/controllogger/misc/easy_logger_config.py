import dataclasses
from typing import Union

from controllogger.enums.log_levels import LogLevels
from controllogger.logger.input import InputLogger
from controllogger.logger.output import OutputLogger
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig


@dataclasses.dataclass
class EasyLoggerConfig(LoggerDefaultsConfig):
    name: str = "easy_logger"  # Name of the control logger and also used as base name for output loggers.
    level: Union[LogLevels, int] = LogLevels.DEBUG  # Log level for the control logger. All input loggers will automatically use this level.
    last_resort: bool = False  # Default last resort for the control logger.
    # Last resort is used when no output logger is found for a log record or the output logger is not able to handle the log record.

    raise_on_closed: bool = True  # Raise an exception if the logger is closed.
    raise_on_not_attached: bool = False  # Raise an exception if the logger is not attached to any output logger.

    # List of output loggers created by the control logger on startup.
    output_loggers: list[OutputLoggerConfig] = dataclasses.field(default_factory=lambda: [OutputLoggerConfig(name="console", console=True),
                                                                                          OutputLoggerConfig(name="file",
                                                                                                             file=True)])

    # define base classes
    input_logger_cls: type[InputLogger] = InputLogger
    output_logger_cls: type[OutputLogger] = OutputLogger
