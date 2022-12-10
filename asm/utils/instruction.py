# Standard
from dataclasses import dataclass, field

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Instruction:
    """Instruction with name and optional arguments"""

    name: Token
    args: list[Token] = field(default_factory=list)

