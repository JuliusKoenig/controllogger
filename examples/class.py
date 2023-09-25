import asyncio
import logging

from pydantic import BaseModel

from controllogger.enums.logger_event import LoggerEvent
from controllogger.logger.control import ControlLogger
from controllogger.logger.input import InputLogger
from controllogger.logger.output import OutputLogger
from controllogger.misc.easy_logger_config import EasyLoggerConfig
from controllogger.misc.logger_class import LoggerClass
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig
from controllogger.misc.easy_logger import easy_logger

# easy_logger.setLevel(logging.DEBUG)

control_logger = ControlLogger(easy_logger_config=EasyLoggerConfig(name="easy_logger", log_events=False))


class MyParent(BaseModel, LoggerClass):
    var: str = "parent"

    def __init__(self, **data):
        super().__init__(**data)
        self.logger.info(f"init at parent {self.var}")

    def foo(self, arg1: int, arg2: str = "qwe") -> callable:
        self.logger.debug(f"foo at parent {self.var}")
        return arg1, arg2

    def foo2(self, arg1: int, arg2: str = "qwe"):
        self.logger.debug(f"foo2 at parent {self.var}")
        return arg1, arg2

    async def bar(self, arg1: int, arg2: str = "qwe"):
        self.logger.debug(f"bar at parent {self.var}")
        return arg1, arg2

    async def bar2(self, arg1: int, arg2: str = "qwe"):
        self.logger.debug(f"bar2 at parent {self.var}")
        return arg1, arg2

class MyParent2(MyParent):
    var: str = "parent2"

    def __init__(self, **data):
        super().__init__(**data)
        self.logger.info(f"init at parent2 {self.var}")

    def foo(self, arg1: int, arg2: str = "qwe") -> callable:
        self.logger.debug(f"foo at parent2 {self.var}")
        return arg1, arg2

    def foo2(self, arg1: int, arg2: str = "qwe"):
        self.logger.debug(f"foo2 at parent2 {self.var}")
        return arg1, arg2

    async def bar(self, arg1: int, arg2: str = "qwe"):
        self.logger.debug(f"bar at parent2 {self.var}")
        return arg1, arg2

    async def bar2(self, arg1: int, arg2: str = "qwe"):
        self.logger.debug(f"bar2 at parent2 {self.var}")
        return arg1, arg2


@control_logger.class_logger(logger_defaults_config=LoggerDefaultsConfig(log_events=True))
class MyClass(MyParent2):
    var: str = "child"

    def __init__(self, **data):
        super().__init__(**data)
        self.logger.info(f"init {self.var}")

    def foo2(self, arg1: int, arg2: str = "qwe"):
        arg1, arg2 = super().foo2(arg1, arg2)
        self.logger.debug(f"foo2 {self.var}")
        self.foo(1, arg2="asd")
        return arg1, arg2

    async def bar2(self, arg1: int, arg2: str = "qwe"):
        arg1, arg2 = await super().bar2(arg1, arg2)
        self.logger.debug(f"bar2 {self.var}")
        return arg1, arg2


if __name__ == '__main__':
    el = easy_logger
    my_class = MyClass()
    foo = my_class.foo(1, arg2="asd")
    foo2 = my_class.foo2(2, arg2="qwe")
    bar = asyncio.run(my_class.bar(3, arg2="zxc"))
    bar2 = asyncio.run(my_class.bar2(4, arg2="rty"))
    # del my_class
    print()
