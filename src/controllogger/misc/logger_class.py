from typing import NewType, Callable, Union

from controllogger.logger.input import InputLogger
from controllogger.misc.context import LoggerContext

LoggerContextImplementation = Union[NewType("LoggerContextImplementation", LoggerContext), Callable]
InputLoggerImplementation = NewType("InputLoggerImplementation", InputLogger)


class LoggerClass:
    logger_context: LoggerContextImplementation
    logger: InputLoggerImplementation
