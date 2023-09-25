from enum import Enum


class LoggerEvent(str, Enum):
    INIT = "init"
    ATTACH = "attach"
    DETACH = "detach"
    DESTROY = "destroy"
