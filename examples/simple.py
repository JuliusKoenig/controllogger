import logging

from controllogger.logger.control import ControlLogger
from controllogger.misc.easy_logger_config import EasyLoggerConfig
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig

easy_logger_config = EasyLoggerConfig(name="easy_logger")


class TestLogger(logging.Logger):
    def handle(self, record):
        return super().handle(record)


control_logger = ControlLogger(easy_logger_config=easy_logger_config)
with control_logger("lc1",
                    config=OutputLoggerConfig(name="lc1_output_logger", file=True),
                    logger_cls=TestLogger) as lc1:
    lc1_input_logger = ControlLogger.get_logger("lc1_input_logger")
    print()
    with control_logger("lc2", output_logger_defaults_config=LoggerDefaultsConfig(name="lc2_logger", file_path="logs/lc2")) as lc2:
        lc2_output_logger = control_logger.create_output_logger(config=OutputLoggerConfig(name="lc2_output_logger", file=True),
                                                                logger_cls=TestLogger)
        lc2_input_logger = ControlLogger.get_logger("lc2_input_logger")
        print()
        with control_logger("lc3", close=False) as lc3:
            lc3_output_logger = control_logger.create_output_logger(config=OutputLoggerConfig(name="lc3_output_logger", file=True),
                                                                    logger_cls=TestLogger)
            lc3_input_logger = ControlLogger.get_logger("lc3_input_logger")
            lc3.close()
print()
