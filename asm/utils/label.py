# Standard
from dataclasses import dataclass, field

# Local
from utils.token import Token, TokenType


@dataclass(frozen=True, slots=True)
class Label:
    """Label with name, pointer and optional decorator and arguments"""

    name: Token
    pointer: int
    decorator: Token = None
    arguments: list[Token] = field(default_factory=list)

