# Standard
from dataclasses import dataclass
from enum import StrEnum, auto


class TokenType(StrEnum):
    """Type of a token"""

    SPACE = auto()
    NEWLINE = auto()
    COMMENT = auto()
    ARGUMENT = auto()
    COLON = auto()
    COMMA = auto()
    SLASH = auto()
    AT = auto()
    DOLLAR = auto()
    INCLUDE = auto()
    EXPORT = auto()
    CODE = auto()
    CONSTANT = auto()
    VARIABLE = auto()
    RESOURCE = auto()
    NAME = auto()
    STRING = auto()
    DECIMAL = auto()
    HEXADECIMAL = auto()
    OCTAL = auto()
    BINARY = auto()
    REGISTER = auto()


@dataclass(frozen=True, slots=True)
class Token:
    """Token with type, line and column number and optional value"""

    type: TokenType
    line: int
    column: int
    value: int | str = None

