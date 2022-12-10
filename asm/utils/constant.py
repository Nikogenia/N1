# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Constant:
    """Constant with name and value"""

    name: Token
    value: Token

