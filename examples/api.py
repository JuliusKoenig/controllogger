import logging

from fastapi import FastAPI

from controllogger.logger.control import ControlLogger
from controllogger.misc.easy_logger import easy_logger
from controllogger.misc.easy_logger_config import EasyLoggerConfig
from controllogger.misc.log_function_config import LogFuntionConfig
from controllogger.misc.logger_class import LoggerClass

easy_logger.setLevel(logging.DEBUG)

control_logger = ControlLogger(easy_logger_config=EasyLoggerConfig(name="easy_logger"))


class TClass:
    @classmethod
    @control_logger.function_logger()
    def qwe(cls):
        cls.logger.info("init at class")

    @staticmethod
    @control_logger.function_logger()
    def qwe2():
        easy_logger.info("init at static")


@control_logger.class_logger(defaults_config={"log_events": True}, func_config=LogFuntionConfig(start_msg="init at api"),
                             func_configs={"prop_foo2": LogFuntionConfig(start_msg="prop_foo2 at api")})
class MyApi(FastAPI, LoggerClass):
    def __init__(self, qwe: TClass = TClass):
        super().__init__()
        self.logger.info("init at api from init")

    @staticmethod
    def static_foo(arg1: int, arg2: str = "qwe") -> callable:
        easy_logger.debug(f"static foo at api")
        return arg1, arg2

    @classmethod
    def class_foo(cls, arg1: int, arg2: str = "qwe") -> callable:
        easy_logger.debug(f"class foo at api")
        return arg1, arg2

    @control_logger.class_logger_method()
    def prop_foo(self) -> callable:
        self.logger.debug(f"prop foo at api from prop")
        return self

    def prop_foo2(self) -> callable:
        self.logger.debug(f"prop2 foo at api from prop")
        return self


app = MyApi()


@app.on_event("startup")
async def init_log():
    # with self.logger_context():
    #     self.logger.info("startup at api")
    static_foo = MyApi.static_foo(1, "qwe")
    class_foo = MyApi.class_foo(1, "qwe")
    prop_foo = app.prop_foo()
    print()


@app.on_event("startup")
async def init_log2():
    logger = app.logger
    print()


# oe = app.on_event

print()

# @control_logger.function_logger()
# def app(logger):
#     a = FastAPI()
#
#     @a.on_event("startup")
#     async def init_log():
#         print()
#
#     return a


if __name__ == '__main__':
    # with app.logger_context():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
