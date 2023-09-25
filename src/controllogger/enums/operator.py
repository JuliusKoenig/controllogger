from enum import Enum


class Operator(str, Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    IN = "in"
    NOT_IN = "not_in"
