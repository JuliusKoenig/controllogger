from enum import Enum


class TerminalOutFile(str, Enum):
    """
    Terminal output file
    """
    STDOUT = "stdout"
    STDERR = "stderr"
