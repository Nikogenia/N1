# Standard
from typing import Self, Callable

# Local
from utils.error import Error, ErrorType
from utils.token import Token, TokenType


class Module:
    """Module for parsing"""

    def __init__(self, code: str) -> None:
        
        # General data
        self.code: str = code
        self.lines: list[str] = code.splitlines()
        self.tokens: list[TokenType] = []

        # Temporary data
        self.tokenize_mode: Callable[[Module, int, str, int, str], bool] = self.tokenize_mode_normal
        self.tokenize_data: dict = {}

        self.tokenize()

        for token in self.tokens:
            print(repr(token))

        """
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
        """

    def tokenize(self) -> None:
        """Tokenize the lines"""
        
        for line, code in enumerate(self.lines):

            self.tokenize_mode = self.tokenize_mode_normal
            self.tokenize_data.clear()

            for column, char in enumerate(code):

                if self.tokenize_mode(line, code, column, char):
                    break

    def tokenize_mode_normal(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in normal mode"""

        if char in ("'", '"'):
            self.tokenize_data["value"] = ""
            self.tokenize_mode = self.tokenize_mode_string

        if char == ";":
            self.tokens.append(Token(TokenType.COMMENT, line, column, code[column + 1:]))
            return True

        if char == ":":
            self.tokens.append(Token(TokenType.COLON, line, column))

        if char in ("\t", " ") and "space" not in self.tokenize_data:
            self.tokens.append(Token(TokenType.SPACE, line, column))
            self.tokenize_data["space"] = None
        else:
            if "space" in self.tokenize_data:
                del self.tokenize_data["space"]

    def tokenize_mode_string(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in string mode"""

        if char in ("'", '"'):
            self.tokens.append(Token(TokenType.STRING, line,
                                     column - len(self.tokenize_data["value"]),
                                     self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
        else:
            self.tokenize_data["value"] += char

        return False

    def tokenize_mode_constant(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in constant mode"""


    @classmethod
    def file(cls, path: str) -> Self:
        """Load a module from file"""

        with open(path, "r", encoding="utf-8") as f:
            cls(f.read())

