import logging
from types import FunctionType
from typing import Optional


def implement_post_init():
    def decorator(func: FunctionType):
        func.__post_init__implemented__ = True
        return func

    return decorator


class BaseLogHandler(logging.Handler):
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, '__post_init__'):
            # check if __post_init__ is abstract
            if getattr(cls.__post_init__, '__post_init__implemented__', False):
                # make method not abstract
                __init__ = cls.__init__

                def post_init_class_schema__init__(self, *a, **kw):
                    __init__(self, *a, **kw)
                    cls.__post_init__(self)

                cls.__init__ = post_init_class_schema__init__

        return super().__new__(cls)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        __init__ = cls.__init__

        def post_init_class_schema__init__(self, *a, **kw):
            __init__(self, *a, **kw)
            cls.__post_init__(self)

        if not hasattr(cls, '__post_init__'):
            raise NotImplementedError(f"Class '{cls.__name__}' must implement '__post_init__' method")
        else:
            # check if __post_init__ is callable
            if not callable(cls.__post_init__):
                raise ValueError(f"__post_init__ for '{cls.__name__}' is not callable")

            # check if __post_init__ is __post_init__implemented__
            if getattr(cls.__post_init__, '__post_init__implemented__', False):
                return  # skip if abstract

            cls.__init__ = post_init_class_schema__init__

    def __init__(self, level=logging.NOTSET):
        super().__init__(level=level)
        self.header_width: Optional[int] = None

    @implement_post_init()
    def __post_init__(self):
        self.header_width = 110

        # wrap self.handle
        backup_format = self.format

        def format_wrapper(record):
            if record.msg == "[HEADER]" and hasattr(record, "header"):
                return self.format_header(record)
            else:
                return backup_format(record)

        self.format = format_wrapper

    def format_header(self, record) -> str:
        name: str = record.header["name"]
        desc: str = record.header["desc"]
        lines: list[str] = record.header["lines"]

        # prepare lines
        def prepare_line(l: str) -> str:
            if "\n" in l:
                raise ValueError("Line can't contain new line character")

            l_len = len(l) + 4
            if l_len > self.header_width:
                l_trimmed = l[: self.header_width - 4]
                l_other = l[self.header_width - 4:]
                l_trimmed_prepared = prepare_line(l_trimmed)
                l_other_prepared = prepare_line(l_other)
                return l_trimmed_prepared + l_other_prepared
            else:
                return f"║ {l}" + f"{' ' * (self.header_width - len(l) - 3)}" + "║\n"

        lines_prepared = []
        if lines is not None:
            for line in lines:
                for new_line in line.split("\n"):
                    lines_prepared.append(prepare_line(new_line))

        desc_prepared = ""
        if desc is not None:
            desc_prepared = "╠" + f"{'═' * (self.header_width - 2)}" + "╣\n"
            desc = f"description: {desc}"
            for new_line in desc.split("\n"):
                desc_prepared += prepare_line(new_line)
            desc_prepared += prepare_line(f"logger: {record.name.strip()}")

        # prepare header
        header_str = ""
        # time
        time_str = "═ " + self.formatter.formatTime(record) + " ═"
        time_added = False
        header_sum = self.header_width - 2
        line_sum = self.header_width - 2
        if len(header_str) + len(time_str) <= self.header_width:
            header_str += time_str
            header_sum -= len(time_str)
            time_added = True
        # level
        if time_added:
            level_str = " " + record.levelname + " ═"
        else:
            level_str = "═ " + record.levelname + " ═"
        if len(header_str) + len(level_str) <= self.header_width:
            header_str += level_str
            header_sum -= len(level_str)

        header = f"╔{header_str + '═' * header_sum}" + "╗\n"
        header += prepare_line(name)
        header += desc_prepared
        if len(lines_prepared) > 0:
            header += "╠" + f"{'═' * line_sum}" + "╣\n"
            header += "".join(lines_prepared)
        header += "╚" + f"{'═' * line_sum}" + "╝"

        # replace msg with header
        return header
