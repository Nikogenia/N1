# Standard
from typing import Self

# Local
from errors import *


class Instruction:
    """The instruction class representing one"""

    def __init__(self, name: str, args: list[str]) -> None:
        
        self.name: str = name
        self.args: list[str] = args

    @classmethod
    def text(cls, value: str) -> Self:

        name = value.split(" ")[0]
        args = [arg.strip() for arg in " ".join(value.split(" ")[1:]).strip().split(",")]

        return cls(name, args)

    def __repr__(self):
        return f"Instruction[name={self.name}, args={self.args}]"

