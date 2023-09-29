import logging
from typing import Union

from controllogger.enums.log_levels import LogLevels
from controllogger.logger.base import BaseLogger
from controllogger.misc.input_logger_config import InputLoggerConfig


class InputLogger(BaseLogger):
    _ConfigClass = InputLoggerConfig
    _my_type: str = "InputLogger"
    _control_logger_type_field = "input_logger_type"

    def __init__(self, name: str = None, level: Union[LogLevels, int] = logging.NOTSET, config: Union[_ConfigClass, dict[str, any]] = None):
        super().__init__(name=name, level=level, config=config)

        self.attach()

    def __del__(self):
        if not self.open:
            return
        super().__del__()
        self.detach()
        del self.control_logger.all_logger[self.name]

    def __str__(self) -> str:
        name = self.name
        level = LogLevels(self.level).name
        context_str = ", ".join([str(context) for context in self.contexts])
        r = f"{self.__class__.__name__}({name=}, {level=}, "
        if self.closed:
            r = r[:-2]
            r += ") CLOSED"
            return r
        if not self.attached:
            r = r[:-2]
            r += ") DETACHED"
            return r
        if len(self.contexts) > 0:
            r += f"contexts=[{context_str}], "
        r = r[:-2]
        r += ")"

        return r

    def attach(self) -> None:
        """
        Attach the input logger to the control logger
        :return: None
        """

        if self.attached:
            return None

        if self.name in self.control_logger.input_loggers.keys():
            raise ValueError(f"Input logger for '{self.name}' already exists.")
        self.control_logger.input_loggers[self.name] = self
        super().attach()

    def detach(self) -> None:
        """
        Detach the input logger from the control logger
        :return: None
        """

        if not self.attached:
            return None

        if self.name not in self.control_logger.input_loggers.keys():
            raise ValueError(f"Input logger for '{self.name}' not found.")
        super().detach()
        del self.control_logger.input_loggers[self.name]

    @property
    def attached(self) -> bool:
        for logger_name in self.control_logger.input_loggers.keys():
            if logger_name == self.name:
                return True
        return False

    def reconfigure(self):
        self.setLevel(self.control_logger.level)
        self.propagate = self.control_logger.propagate
        self.disabled = self.control_logger.disabled

    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)

        # set context
        record.contexts = self.contexts

        return record

    def handle(self, record):
        self._skip_handle = True
        super().handle(record)
        # handle record by control logger
        return self.control_logger.handle(record)

    def isEnabledFor(self, level):
        self.reconfigure()
        return super().isEnabledFor(level)
