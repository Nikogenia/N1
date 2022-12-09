# Standard
from typing import NoReturn
from dataclasses import dataclass
from enum import StrEnum, auto
import sys


class ErrorType(StrEnum):
    """Type of a error"""

    SYNTAX = "Syntax Error"
    VALUE = "Value Error"
    NAME = "Name Error"
    REFERENCE = "Reference Error"
    INSTRUCTION = "Instruction Error"


@dataclass(frozen=True, slots=True)
class Error:
    """Error with location, type and message"""

    module: str
    line: int
    type: ErrorType
    message: str

    def exit(self) -> NoReturn:

        print("-" * 20)
        print(f"{'FATAL ERROR':^20}")
        print(f"File '{self.module}' - Line {self.line}")
        print(f"{self.type.value}: {self.message}")
        print("-" * 20)

        sys.exit(1)

