# Standard
from typing import Self

# Local
import string
from errors import *
from instruction import Instruction


class Module:
    """The module class representing one module"""

    def __init__(self, lines: list[str]) -> None:
        
        self.namespace = {}
        self.instructions = []
        self.macros = {}
        self.modules = []
        self.lines = [line.replace("\t", " ").replace("\n", "").strip() for line in lines]

        decorators = []
        definitions = True
        macro = None
        for line, value in enumerate(self.lines):
            if ";" in value or value == "":
                continue
            if value.lower().startswith("include"):
                self.modules.append(value.split('"')[1])
            elif value.startswith("@"):
                decorators.append(value.replace("@", ""))
            elif value.endswith(":"):
                name = value.lower().replace(":", "").split(" ")[0]
                if "macro" in decorators:
                    args = ()
                    macro = (name, args)
                    if name not in self.macros:
                        self.macros[name] = {}
                    self.macros[name][args] = []
                else:
                    macro = None
                    self.namespace[value.lower().replace(":", "")] = len(self.instructions)
                decorators.clear()
                definitions = False
            else:
                if definitions:
                    raise InvalidSyntaxError(f"Instruction '{value}' in global scope (line {line + 1})")
                instruction = Instruction.text(value)
                if instruction is not None:
                    if macro is None:
                        self.instructions.append(instruction)
                    else:
                        self.macros[macro[0]][macro[1]].append(instruction)

    @classmethod
    def file(cls, path: str) -> Self:

        lines = []

        with open(path, "r", encoding="utf-8") as f:
            while True:
                lines.append(f.readline())
                if lines[-1] == "":
                    break

        return cls(lines)

