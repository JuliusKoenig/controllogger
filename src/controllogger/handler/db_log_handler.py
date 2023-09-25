import logging

import io
import threading

from datetime import datetime

from controllogger.handler.base import BaseLogHandler


class DbLogHandler(logging.StreamHandler, BaseLogHandler):
    def __init__(
            self,
            log_document: BaseLogDocument,
            buffer_max_lines: int = 10,
            buffer_max_time: int = 60,
    ):
        super().__init__(stream=io.StringIO())

        self.log_document = log_document

        # check if log_document is a instance of BaseLogDocument
        if not isinstance(self.log_document, BaseLogDocument):
            raise TypeError(f"Expected log_document to be a instance of BaseLogDocument, got {type(self.log_document)}.")

        self.buffer_len = 0
        self.buffer_max_lines = buffer_max_lines
        self.buffer_max_time = buffer_max_time
        self.max_time_callback_timer = threading.Timer(self.buffer_max_time, self._max_time_callback)

    def close(self):
        super().close()

        # flush buffer
        if self.buffer_len > 0:
            self.flush()

    def emit(self, record: logging.LogRecord) -> None:
        # get log level
        level = dict(LogLevels.__members__)[record.levelname]
        msg = self.format(record)

        # create log line
        log_line = LogEntryModel(timestamp=datetime.now(), level=level, msg=msg)
        log_line_str = log_line.json()

        # add log line to stream
        self.stream.write(log_line_str + "\n")
        self.buffer_len += 1

        # flush buffer if full
        if self.buffer_len >= self.buffer_max_lines:
            self.flush()
        else:
            # setup timed callback to flush buffer
            if not self.max_time_callback_timer.is_alive():
                root_logger.debug(f"Setting up timed callback for '{self.log_document.name}'.")
                self.max_time_callback_timer = threading.Timer(self.buffer_max_time, self._max_time_callback)
                self.max_time_callback_timer.start()

    def _max_time_callback(self) -> None:
        if not self.max_time_callback_timer.is_alive():
            raise RuntimeError("Callback is not alive.")
        root_logger.debug(f"Callback timed out for '{self.log_document.name}'. -> Flushing buffer.")
        self.flush()

    def flush(self) -> None:
        # reset timed callback
        if self.max_time_callback_timer.is_alive():
            root_logger.debug(f"Resetting timed callback for '{self.log_document.name}'.")
            self.max_time_callback_timer.cancel()

        # check if buffer is empty
        if self.buffer_len == 0:
            root_logger.debug(f"Buffer is empty for '{self.log_document.name}'.")
            return

        root_logger.debug(f"Flushing buffer for '{self.log_document.name}'.")

        for buffer_line in self.buffer:
            line = LogEntryDocument(**buffer_line.dict())
            self.log_document.log_lines.append(line)
        self.reset_buffer()

        self.log_document.save()
        root_logger.debug(f"Buffer flushed for '{self.log_document.name}'.")

    def reset_buffer(self):
        root_logger.debug(f"Resetting buffer for '{self.log_document.name}'.")
        self.stream.seek(0)
        self.stream.truncate()
        self.buffer_len = 0

    @property
    def buffer(self) -> list[LogEntryModel]:
        stream_str = self.stream.getvalue()
        buffer_lines = []
        for line_str in stream_str.split("\n"):
            if line_str.strip() == "":
                continue
            buffer_lines.append(LogEntryModel.parse_raw(line_str))
        return buffer_lines
