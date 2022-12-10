# Standard
from typing import Self, Callable
import string

# Local
from utils.error import Error, ErrorType
from utils.token import Token, TokenType


class Module:
    """Module for parsing"""

    def __init__(self, code: str, path: str) -> None:
        
        # General data
        self.path: str = path
        self.code: str = code
        self.lines: list[str] = [line + "\n" for line in code.splitlines()]
        self.tokens: list[Token] = []
        self.token_lines: list[list[Token]] = []

        # Temporary data
        self.tokenize_mode: Callable[[Module, int, str, int, str], bool] = self.tokenize_mode_normal
        self.tokenize_data: dict = {}

        self.tokenize()

        for token in self.tokens:
            print(repr(token))
            if token.type == TokenType.NEWLINE:
                print()

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

        processed = False

        match char:
            case ";":
                self.tokens.append(Token(TokenType.COMMENT, line, column, code[column + 1:-1]))
                self.tokens.append(Token(TokenType.NEWLINE, line, len(code) - 1))
                return True
            case "\n":
                self.tokens.append(Token(TokenType.NEWLINE, line, len(code) - 1))
                processed = True
            case ":":
                self.tokens.append(Token(TokenType.COLON, line, column))
                processed = True
            case ",":
                self.tokens.append(Token(TokenType.COMMA, line, column))
                processed = True
            case "/" | "\\":
                self.tokens.append(Token(TokenType.SLASH, line, column))
                processed = True
            case "@":
                self.tokens.append(Token(TokenType.AT, line, column))
                processed = True
            case "'" | '"':
                self.tokenize_data["value"] = ""
                self.tokenize_mode = self.tokenize_mode_string
                processed = True
            case "%":
                self.tokenize_data["value"] = ""
                self.tokenize_mode = self.tokenize_mode_argument
                processed = True
        
        if char in string.digits:
            self.tokenize_data["value"] = char
            self.tokenize_data["type"] = TokenType.DECIMAL
            self.tokenize_mode = self.tokenize_mode_value
            processed = True

        elif char in string.ascii_letters + "_":
            self.tokenize_data["value"] = char
            self.tokenize_mode = self.tokenize_mode_name
            processed = True

        if char in ("\t", " "):
            if "space" not in self.tokenize_data:
                self.tokens.append(Token(TokenType.SPACE, line, column))
                self.tokenize_data["space"] = None
            processed = True
        else:
            if "space" in self.tokenize_data:
                del self.tokenize_data["space"]

        if not processed:
            Error(self, line, ErrorType.SYNTAX, f"Unknown char {char!r}! Hint: Names are only allowed to contain\n" +
                  f"the following characters and can't start with a digit:\n_{string.ascii_letters}{string.digits}").exit()

        return False

    def tokenize_mode_string(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in string mode"""

        if char == "\n":
            Error(self, line, ErrorType.SYNTAX,
                  "String was not closed until the end of the line!").exit()
        elif char in ("'", '"'):
            self.tokens.append(Token(TokenType.STRING, line,
                column - len(self.tokenize_data["value"]), self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
        else:
            self.tokenize_data["value"] += char

        return False

    def tokenize_mode_value(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in value mode"""

        if len(self.tokenize_data["value"]) == 1 and self.tokenize_data["type"] == TokenType.DECIMAL:
            allowed = string.hexdigits + "xobXOB"
        else:
            allowed = string.hexdigits

        if char not in allowed:
            if len(self.tokenize_data["value"]) == 0:
                Error(self, line, ErrorType.SYNTAX, f"Empty {self.tokenize_data['type'].value} value definition!").exit()
            self.tokens.append(Token(self.tokenize_data["type"], line,
                column - len(self.tokenize_data["value"]), self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return self.tokenize_mode(line, code, column, char)

        if len(self.tokenize_data["value"]) == 1 and self.tokenize_data["type"] == TokenType.DECIMAL:

            if char in string.digits:
                self.tokenize_data["value"] += char
                return False

            if self.tokenize_data["value"] != "0":
                Error(self, line, ErrorType.SYNTAX, "The first digit of a non-decimal value definition" +
                      f" need to be 0, not {self.tokenize_data['value']!r}!").exit()
            
            token_type = {"x": TokenType.HEXADECIMAL, "o": TokenType.OCTAL, "b": TokenType.BINARY}
            if char.lower() not in token_type:
                Error(self, line, ErrorType.SYNTAX,
                    f"Invalid char {char!r} in decimal value definition!").exit()
            self.tokenize_data["type"] = token_type[char.lower()]
            self.tokenize_data["value"] = ""
            return False

        if self.tokenize_data["type"] != TokenType.HEXADECIMAL:
            allowed = {TokenType.DECIMAL: string.digits, TokenType.OCTAL: string.octdigits, TokenType.BINARY: "01"}
            if char not in allowed[self.tokenize_data["type"]]:
                Error(self, line, ErrorType.SYNTAX,
                      f"Invalid char {char!r} in {self.tokenize_data['type'].value} value definition!").exit()

        self.tokenize_data["value"] += char

        return False

    def tokenize_mode_name(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in name mode"""

        if char not in string.ascii_letters + string.digits + "_":
            keywords = {"include": TokenType.INCLUDE, "export": TokenType.EXPORT,
                        "const": TokenType.CONSTANT, "variable": TokenType.VARIABLE}
            if self.tokenize_data["value"].lower() in keywords:
                self.tokens.append(Token(keywords[self.tokenize_data["value"].lower()], line,
                    column - len(self.tokenize_data["value"])))
            elif len(self.tokenize_data["value"]) == 1 and self.tokenize_data["value"].lower() in "abcdhlzf":
                self.tokens.append(Token(TokenType.REGISTER, line, column - 1, self.tokenize_data["value"].lower()))
            else:
                self.tokens.append(Token(TokenType.NAME, line,
                    column - len(self.tokenize_data["value"]), self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return self.tokenize_mode(line, code, column, char)

        self.tokenize_data["value"] += char

        return False

    def tokenize_mode_argument(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in argument mode"""

        if len(self.tokenize_data["value"]) == 0:
            if char not in "ria":
                Error(self, line, ErrorType.SYNTAX,
                    f"The first char of a argument definition must be 'r', 'i' or 'a', not {char!r}!").exit()
        elif len(self.tokenize_data["value"]) == 1:
            if char not in string.digits:
                Error(self, line, ErrorType.SYNTAX,
                    f"The second char of a argument definition must be a digit, not {char!r}!").exit()
        else:
            self.tokens.append(Token(TokenType.ARGUMENT, line, column - 3, self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return self.tokenize_mode(line, code, column, char)

        self.tokenize_data["value"] += char

        return False

    @classmethod
    def file(cls, path: str) -> Self:
        """Load a module from file"""

        with open(path, "r", encoding="utf-8") as f:
            cls(f.read(), path)

