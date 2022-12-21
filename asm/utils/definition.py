# Standard
from dataclasses import dataclass, field

# Local
from utils.token import Token, TokenType


@dataclass(repr=False, frozen=True, slots=True)
class Include:
    """Include with path"""

    path: list[Token]

    @property
    def string(self) -> bool:
        return self.path[0].type == TokenType.STRING and len(self.path) == 1

    def __repr__(self):
        path = "" if self.path else "  "
        for t in self.path:
            path += repr(t) + ", "
        return f"Include({path[:-2]})"


@dataclass(repr=False, frozen=True, slots=True)
class Export:
    """Export with name"""

    name: Token

    def __repr__(self):
        return f"Export({self.name!r})"


@dataclass(repr=False, frozen=True, slots=True)
class Constant:
    """Constant with name and value"""

    name: Token
    value: Token

    def __repr__(self):
        return f"Constant({self.name!r} = {self.value!r})"


@dataclass(repr=False, frozen=True, slots=True)
class Variable:
    """Variable with name and size"""

    name: Token
    size: Token

    def __repr__(self):
        return f"Variable({self.name!r} = {self.size!r})"


@dataclass(repr=False, frozen=True, slots=True)
class Resource:
    """Resource with name and value"""

    name: Token
    value: Token

    def __repr__(self):
        return f"Resource({self.name!r} = {self.value!r})"


@dataclass(repr=False, slots=True)
class Macro:
    """Macro with name, arguments and instructions"""

    name: Token
    arguments: list[Token]
    instructions: list[Token] = field(default_factory=list)
    labels: list[Token] = field(default_factory=list)

    def __repr__(self):
        args = " - " if self.arguments else "  "
        for arg in self.arguments:
            args += repr(arg) + ", "
        return f"Macro({self.name!r}" + args[:-2] + f": {self.instructions} | {self.labels})"

