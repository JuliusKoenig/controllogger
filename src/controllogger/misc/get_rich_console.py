import sys

from rich.console import Console

from ..enums.terminal_out_file import TerminalOutFile

RICH_CONSOLE: dict[TerminalOutFile, Console] = {}


def get_rich_console(out_file: TerminalOutFile, width: int, force_terminal: bool) -> Console:
    """
    Get rich console, create if not exists

    :param out_file: terminal out file
    :param width: terminal width
    :param force_terminal: force terminal
    :return: rich console
    """

    global RICH_CONSOLE

    # check if rich console exists
    if out_file not in RICH_CONSOLE:
        # choose file
        if out_file == TerminalOutFile.STDOUT:
            file = sys.stdout
        elif out_file == TerminalOutFile.STDERR:
            file = sys.stderr
        else:
            file = sys.stderr

        # create rich console
        RICH_CONSOLE[out_file] = Console(file=file,
                                         force_terminal=force_terminal,
                                         width=width)

    rich_handler = RICH_CONSOLE[out_file]

    return rich_handler
