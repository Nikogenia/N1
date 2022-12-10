# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Variable:
    """Variable with name and size"""

    name: Token
    size: Token

