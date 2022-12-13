# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Instruction:
    """Instruction with name and arguments"""

    name: Token
    arguments: list[Token]


@dataclass(frozen=True, slots=True)
class Label:
    """Label with name, pointer and optional function"""

    name: Token
    pointer: int
    function: bool = False

