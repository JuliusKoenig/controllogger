import dataclasses
from typing import Union

from controllogger.enums.operator import Operator
from controllogger.misc.base_dataclass import BaseDataclass


@dataclasses.dataclass
class Filter(BaseDataclass):
    key: str
    value: Union[bool, int, float, str, list[Union[bool, int, float, str]], dict[str, Union[bool, int, float, str]]]
    operator: Operator = Operator.EQUALS
