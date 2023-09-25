from rich.logging import RichHandler

from kdsm_api.classes.logging.base import BaseLogHandler
from kdsm_api.enums.terminal_out_file import TerminalOutFile
from kdsm_api.functions.get_rich_console import get_rich_console


class RichConsoleHandler(RichHandler, BaseLogHandler):
    def __init__(self, console_outfile: TerminalOutFile, console_width: int, console_force_terminal: bool):
        super().__init__(
            console=get_rich_console(out_file=console_outfile,
                                     width=console_width,
                                     force_terminal=console_force_terminal),
        )

    # def handle(self, record):
    #     if record.msg == "[HEADER]" and hasattr(record, "header"):
    #         print()
    #     super().handle(record)
