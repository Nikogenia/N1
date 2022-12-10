# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Export:
    """Export with name"""

    name: Token

