# Standard
from dataclasses import dataclass
from enum import StrEnum, auto


class TokenType(StrEnum):
    """Type of a token"""

    SPACE = auto()
    COMMENT = auto()
    COLON = auto()
    COMMA = auto()
    AT = auto()
    INCLUDE = auto()
    CONST = auto()
    VAR = auto()
    NAME = auto()
    STRING = auto()
    DECIMAL = auto()
    HEXADECIMAL = auto()
    OCTAL = auto()
    BINARY = auto()


@dataclass(frozen=True, slots=True)
class Token:
    """Token with type, line and column number and optional value"""
    
    type: TokenType
    line: int
    column: int
    value: int | str = None

