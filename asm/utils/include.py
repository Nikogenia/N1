# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Include:
    """Include with path"""

    path: Token | list[Token]

