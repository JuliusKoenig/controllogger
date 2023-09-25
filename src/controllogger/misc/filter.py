from controllogger.enums.operator import Operator
from controllogger.misc.base_dataclass import BaseDataclass


class Filter(BaseDataclass):
    key: str
    value: bool | int | float | str | list[bool | int | float | str] | dict[str, bool | int | float | str]
    operator: Operator = Operator.EQUALS
