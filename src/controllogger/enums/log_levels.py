from enum import Enum


class LogLevels(int, Enum):
    """
    Available log levels for API
    """

    NOTSET = 0
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
