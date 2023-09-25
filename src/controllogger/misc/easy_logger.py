import logging

from controllogger.logger.base_easy import BaseEasyLogger


class EasyLogger(BaseEasyLogger):
    def __init__(self):
        super().__init__(name="easylogger", level=logging.WARNING)

        self.easy_logger_handler = logging.StreamHandler()
        self.easy_logger_handler_formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s] %(srcRelativePathname)s(%(srcLineno)s) -> %(relativePathname)s(%(lineno)s) - %(message)s')
        self.easy_logger_handler.setFormatter(self.easy_logger_handler_formatter)
        self.addHandler(self.easy_logger_handler)


easy_logger = EasyLogger()
