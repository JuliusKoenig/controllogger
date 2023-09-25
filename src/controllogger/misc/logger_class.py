from typing import NewType, Callable

from controllogger.logger.input import InputLogger
from controllogger.misc.context import LoggerContext

LoggerContextImplementation = NewType("LoggerContextImplementation", LoggerContext) | Callable
InputLoggerImplementation = NewType("InputLoggerImplementation", InputLogger)


class LoggerClass:
    logger_context: LoggerContextImplementation
    logger: InputLoggerImplementation
