import logging

from controllogger.enums.logger_event import LoggerEvent
from controllogger.logger.control import ControlLogger
from controllogger.logger.input import InputLogger
from controllogger.logger.output import OutputLogger
from controllogger.misc.easy_logger_config import EasyLoggerConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig
from controllogger.misc.easy_logger import easy_logger

easy_logger.setLevel(logging.DEBUG)


class TestInputLogger(InputLogger):
    @InputLogger.on_event("init")
    def i1(self):
        print("i1")

    @InputLogger.on_event(LoggerEvent.INIT)
    def i2(self):
        print("i2")

    @InputLogger.on_event("destroy")
    def ds1(self):
        print("ds1")

    @InputLogger.on_event(LoggerEvent.DESTROY)
    def ds2(self):
        print("ds2")

    @InputLogger.on_event("attach")
    def a1(self):
        print("a1")

    @InputLogger.on_event(LoggerEvent.ATTACH)
    def a1(self):
        print("a1")

    @InputLogger.on_event("detach")
    def dt1(self):
        print("dt1")

    @InputLogger.on_event(LoggerEvent.DETACH)
    def dt1(self):
        print("dt1")


class TestOutputLogger(OutputLogger):
    @OutputLogger.on_event("init")
    def i1(self):
        print("i1")

    @OutputLogger.on_event(LoggerEvent.INIT)
    def i1(self):
        print("i1")

    @OutputLogger.on_event("destroy")
    def ds1(self):
        print("ds1")

    @OutputLogger.on_event(LoggerEvent.DESTROY)
    def ds2(self):
        print("ds2")

    @OutputLogger.on_event("attach")
    def a1(self):
        print("a1")

    @OutputLogger.on_event(LoggerEvent.ATTACH)
    def dt1(self):
        print("dt1")

    @OutputLogger.on_event("detach")
    def dt2(self):
        print("dt2")

    @OutputLogger.on_event(LoggerEvent.DETACH)
    def dt2(self):
        print("dt2")


# control_logger = ControlLogger(easy_logger_config=EasyLoggerConfig(name="easy_logger", input_logger_cls=TestInputLogger, output_logger_cls=TestOutputLogger))
control_logger = ControlLogger(easy_logger_config=EasyLoggerConfig(name="easy_logger", log_events=True))


@control_logger.function_logger(start_msg="Function foo started with {qwe}", end_msg="Function foo ended with {qwe}")
def foo(qwe: str, logger):
    logger.info(f"qwe={qwe}")
    return qwe


if __name__ == '__main__':
    with control_logger("lc1", config=OutputLoggerConfig(name="lc1_output_logger", file=True)) as lc1:
        lc1_input_logger = ControlLogger.get_logger("lc1_input_logger")
    q = foo(1)
    q2 = foo(2)
    print()
