# Standard
from typing import Self, Callable
import string

# Local
from utils.definition import Include, Export, Constant, Variable, Resource, Macro
from utils.code import Instruction, Label
from utils.error import Error, ErrorType
from utils.token import Token, TokenType


class Module:
    """Module for parsing"""

    def __init__(self, code: str, path: str) -> None:

        # General data
        self.path: str = path

        # Text data
        self.code: str = code
        self.lines: list[str] = [line + "\n" for line in code.splitlines()]

        # Token data
        self.tokens: list[Token] = []
        self.token_lines: list[list[Token]] = []

        # Parse data
        self.includes: list[Include] = []
        self.exports: list[Export] = []
        self.constants: list[Constant] = []
        self.variables: list[Variable] = []
        self.resources: list[Resource] = []
        self.macros: list[Macro] = []
        self.instructions: list[Instruction] = []
        self.labels: list[Label] = []
        self.namespace: dict[str, Label | Resource | Variable | Constant] = {}

        # Temporary data
        self.tokenize_mode: Callable[[Module, int, str, int, str], bool] = self.tokenize_mode_normal
        self.tokenize_data: dict = {}
        self.parse_mode: Callable[[Module, list[Token], list[Token]], None] = self.parse_mode_definition
        self.parse_data: dict = {}

    def tokenize(self) -> None:
        """Tokenize the lines"""

        line_index = []

        for line, code in enumerate(self.lines):

            self.tokenize_mode = self.tokenize_mode_normal
            self.tokenize_data.clear()

            for column, char in enumerate(code):

                if self.tokenize_mode(line, code, column, char):
                    break

            line_index.append(len(self.tokens))

        for i, j in zip([0] + line_index, line_index):
            self.token_lines.append(self.tokens[i:j])

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
            case "$":
                self.tokens.append(Token(TokenType.DOLLAR, line, column))
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

        elif char in string.ascii_letters + "_.":
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

        if char == "_":
            return False

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

        if char not in string.ascii_letters + string.digits + "_.":
            keywords = {"include": TokenType.INCLUDE, "export": TokenType.EXPORT,
                        "code": TokenType.CODE, "const": TokenType.CONSTANT,
                        "var": TokenType.VARIABLE, "res": TokenType.RESOURCE}
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

    def parse(self) -> None:
        """Parse the tokens"""

        for tokens in self.token_lines:

            start = 0
            for index, token in enumerate(tokens):
                if token.type != TokenType.SPACE:
                    start = index
                    break
            end = len(tokens) - 1
            for index, token in enumerate(reversed(tokens)):
                if token.type != TokenType.SPACE and token.type != TokenType.NEWLINE:
                    end = len(tokens) - index
                    break

            stripped = list(filter(lambda x: x.type != TokenType.COMMENT, tokens[start:end]))

            if not stripped:
                continue

            self.parse_mode(tokens, stripped)

    def parse_mode_definition(self, tokens: list[Token], stripped: list[Token]) -> None:

        if "macro" in self.parse_data:
            self.parse_mode_macro(tokens, stripped)
            return

        line_length = {TokenType.CODE: (1, 0, False, "It has no arguments."),
                       TokenType.INCLUDE: (0, 1, False, ""),
                       TokenType.EXPORT: (3, 1, True, "It takes 1 argument, which is the name of the thing to export."),
                       TokenType.CONSTANT: (5, 2, True, "It takes 2 arguments, the name and the value."),
                       TokenType.VARIABLE: (5, 2, True, "It takes 2 arguments, the name and the size."),
                       TokenType.RESOURCE: (5, 2, True, "It takes 2 arguments, the name and the value.")}

        for token_type, (length, check_space, check_name, description) in line_length.items():
            if list(filter(lambda x: x.type == token_type, stripped)):
                if stripped[0].type != token_type:
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          f"Invalid usage of the {token_type.value} keyword!\n" +
                          f"The keyword need to be at the beginning of the line.").exit()
                if len(stripped) != length and length != 0:
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          f"Invalid usage of the {token_type.value} keyword!\n" +
                          description).exit()
                if (check_space != 0 and stripped[1].type != TokenType.SPACE) or \
                   (check_space == 2 and stripped[3].type != TokenType.SPACE):
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          f"Invalid usage of the {token_type.value} keyword!\n" +
                          f"The {'argument needs' if check_space == 1 else 'arguments need'} " +
                          f"to be separated with {'a space' if check_space == 1 else 'spaces'}.").exit()

                if check_name and stripped[2].type != TokenType.NAME:
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          f"Invalid usage of the {token_type.value} keyword!\n" +
                          "The first argument needs to be a name.").exit()

        match stripped[0].type:
            case TokenType.CODE:
                self.parse_mode = self.parse_mode_code
            case TokenType.INCLUDE:
                if len(stripped) < 3:
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          "Invalid usage of the include keyword!\n" +
                          "It takes one or more names and slashes, alternatively also a single string.").exit()
                self.includes.append(Include(stripped[2:]))
            case TokenType.EXPORT:
                self.exports.append(Export(stripped[2]))
            case TokenType.CONSTANT:
                self.constants.append(Constant(stripped[2], stripped[4]))
            case TokenType.VARIABLE:
                self.variables.append(Variable(stripped[2], stripped[4]))
            case TokenType.RESOURCE:
                self.resources.append(Resource(stripped[2], stripped[4]))
            case TokenType.AT:
                if len(stripped) != 2 or stripped[1].type != TokenType.NAME:
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          "Invalid decorator! An '@' needs to be followed by a name without a space.").exit()
                if stripped[1].value not in ("macro", "func"):
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          "Unknown decorator! Possible decorators: @macro, @func").exit()
                if stripped[1].value != "macro":
                    Error(self, stripped[0].line, ErrorType.SYNTAX,
                          "Wrong section for decorator! The definition section can only contain macros.").exit()
                self.parse_data["macro"] = False
            case _:
                value = "" if stripped[0].value is None else f" (value: {stripped[0].value})"
                Error(self, stripped[0].line, ErrorType.SYNTAX,
                      f"Invalid token '{stripped[0].type.value}'{value}\n" +
                      "at the beginning of the line in the definition section!").exit()

    def parse_mode_macro(self, tokens: list[Token], stripped: list[Token]) -> None:

        if stripped[0].type == TokenType.NAME:
            del self.parse_data["macro"]
            self.parse_mode_definition(tokens, stripped)

    def parse_mode_code(self, tokens: list[Token], stripped: list[Token]) -> None:

        pass

    @classmethod
    def file(cls, path: str) -> Self:
        """Load a module from file"""

        with open(path, "r", encoding="utf-8") as f:
            return cls(f.read(), path)

