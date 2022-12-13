# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Include:
    """Include with path"""

    path: list[Token]


@dataclass(frozen=True, slots=True)
class Export:
    """Export with name"""

    name: Token


@dataclass(frozen=True, slots=True)
class Constant:
    """Constant with name and value"""

    name: Token
    value: Token


@dataclass(frozen=True, slots=True)
class Variable:
    """Variable with name and size"""

    name: Token
    size: Token


@dataclass(frozen=True, slots=True)
class Resource:
    """Resource with name and value"""

    name: Token
    value: Token


@dataclass(slots=True)
class Macro:
    """Macro with name, arguments and instructions"""

    name: Token
    arguments: list[Token]
    instructions: list[Token]

