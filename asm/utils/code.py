# Standard
from dataclasses import dataclass

# Local
from utils.token import Token, TokenType


@dataclass(repr=False, frozen=True, slots=True)
class Instruction:
    """Instruction with name and arguments"""

    name: Token
    arguments: list[Token]

    def __repr__(self):
        args = " - " if self.arguments else "  "
        for arg in self.arguments:
            args += repr(arg) + ", "
        return f"Instruction({self.name!r}" + args[:-2] + ")"


@dataclass(repr=False, frozen=True, slots=True)
class Label:
    """Label with name, pointer and optional function"""

    name: Token
    pointer: int
    function: bool = False

    def __repr__(self):
        func = " @func" if self.function else ""
        return f"Label({self.name!r}: {self.pointer}" + func + ")"

