import dataclasses

from controllogger.misc.base_logger_config import BaseLoggerConfig
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig


@dataclasses.dataclass
class InputLoggerConfig(BaseLoggerConfig):
    def __default_init__(self, logger_defaults_config: LoggerDefaultsConfig):
        super().__default_init__(logger_defaults_config)
