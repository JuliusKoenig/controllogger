from re import sub


def snake_case(s: str):
    """
    Convert a string to snake case.

    :param s: String to convert
    :return: String in snake case
    """

    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()
