import dataclasses

from controllogger.enums.log_levels import LogLevels
from controllogger.misc.base_dataclass import BaseDataclass


@dataclasses.dataclass
class LogFuntionConfig(BaseDataclass):
    header: bool = True  # Log function header. Default is True.
    footer: bool = True  # Log function footer. Default is True.
    header_footer_level: LogLevels = LogLevels.DEBUG  # Log function header and footer level. Default is DEBUG.
    start_msg: str | None = None  # Log function start message. Default is None.
    end_msg: str | None = None  # Log function end message. Default is None.
    start_end_msg_level: LogLevels = LogLevels.INFO  # Log function start message level. Default is DEBUG.
    measure_time: bool = False  # Log function measure time. Default is False.
