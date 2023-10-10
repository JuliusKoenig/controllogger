import logging
import sys
import traceback

from controllogger.enums.terminal_out_file import TerminalOutFile
from controllogger.handler.base import BaseLogHandler


class PythonConsoleHandler(logging.StreamHandler, BaseLogHandler):
    def __init__(self, console_outfile: TerminalOutFile, console_width: int):
        if TerminalOutFile.STDOUT == console_outfile:
            stream = sys.stdout
        elif TerminalOutFile.STDERR == console_outfile:
            stream = sys.stderr
        else:
            raise ValueError(f"Unknown console_outfile: {console_outfile}")

        super().__init__(stream=stream)

        self.console_outfile = console_outfile
        self.console_width = console_width

    def handle(self, record):
        # check if any msg line is longer than console_width
        reorganize_msg = False
        if isinstance(record.msg, str):
            for line in record.msg.splitlines():
                if len(line) > self.console_width:
                    reorganize_msg = True
                    break
        elif isinstance(record.msg, Exception):
            tb_str = "".join(traceback.format_tb(record.msg.__traceback__))
            for line in tb_str.splitlines():
                if len(line) > self.console_width:
                    reorganize_msg = True
                    break
        else:
            raise ValueError(f"Unknown record.msg type: {type(record.msg)}")

        # reorganize msg
        if reorganize_msg:
            new_msg_lines = []
            for line in str(record.msg).splitlines():
                if len(line) > self.console_width:
                    for i in range(0, len(line), self.console_width):
                        new_msg_lines.append(line[i:i + self.console_width])
                else:
                    new_msg_lines.append(line)
            new_msg = "\n".join(new_msg_lines)
            record.msg = new_msg
        logging.StreamHandler.handle(self, record)
