# Standard
from typing import Self, Callable
import string

# Local
from utils.definition import Include, Export, Constant, Variable, Resource, Macro
from utils.token import Token, TokenType, token_list_contains, token_list_remove, token_list_split
from utils.code import Instruction, Label
from utils.error import Error, ErrorType


class Module:
    """Module for parsing"""

    def __init__(self, code: str, path: str, modules: dict[str, Self], main: bool = False) -> None:

        # General data
        self.path: str = path
        self.main: bool = main
        self.modules: dict[str, Module] = modules

        # Text data
        self.code: str = code
        self.lines: list[str] = [line + "\n" for line in code.splitlines()]

        # Token data
        self.tokens: list[Token] = []
        self.token_lines: list[list[Token]] = []
        self.abstract_lines: list[list[Token]] = []

        # Parse data
        self.includes: list[Include] = []
        self.exports: list[Export] = []
        self.constants: list[Constant] = []
        self.variables: list[Variable] = []
        self.resources: list[Resource] = []
        self.macros: list[Macro] = []
        self.instructions: list[Instruction] = []
        self.labels: list[Label] = []

        # Reference data
        self.include_paths: list[str] = []

        # Temporary data
        self.tokenize_mode: Callable[[Module, int, str, int, str], bool] = self.tokenize_mode_normal
        self.tokenize_data: dict = {}
        self.parse_mode: Callable[[Module, list[Token], list[Token]], None] = self.parse_mode_definition
        self.parse_data: dict = {}

    def get_reference(name: str, private: bool = False) -> str:
        
        exported = [export.name for export in self.exports]




    def tokenize(self) -> None:
        """Tokenize the lines"""

        # Loop through each line
        for line, code in enumerate(self.lines):

            # Reset mode and data
            self.tokenize_mode = self.tokenize_mode_normal
            self.tokenize_data.clear()

            # Loop through each char
            for column, char in enumerate(code):

                # Handle char in mode and skip to next line, if true
                if self.tokenize_mode(line, code, column, char):
                    break

        # Split token lines
        self.token_lines = token_list_split(self.tokens, TokenType.NEWLINE)

        # Loop through each line
        for tokens in self.token_lines:

            # Find the abstract start of the line
            start = 0
            for index, token in enumerate(tokens):
                if token.type != TokenType.SPACE:
                    start = index
                    break

            # Find the abstract end of the line
            end = len(tokens) - 1
            for index, token in enumerate(reversed(tokens)):
                if token.type != TokenType.SPACE and token.type != TokenType.NEWLINE:
                    end = len(tokens) - index
                    break

            # Remove comments
            abstract = token_list_remove(tokens[start:end], TokenType.COMMENT)

            # Add the abstract line, if it is not empty
            if abstract:
                self.abstract_lines.append(abstract)

    def tokenize_mode_normal(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in normal mode"""

        processed = False

        # Match char
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
            case "*":
                self.tokens.append(Token(TokenType.ASTERISK, line, column))
                processed = True
            case "'" | '"':
                self.tokenize_data["value"] = ""
                self.tokenize_mode = self.tokenize_mode_string
                processed = True
            case "%":
                self.tokenize_data["value"] = ""
                self.tokenize_mode = self.tokenize_mode_argument
                processed = True

        # Check for value mode
        if char in string.digits:
            self.tokenize_data["value"] = char
            self.tokenize_data["type"] = TokenType.DECIMAL
            self.tokenize_mode = self.tokenize_mode_value
            processed = True

        # Check for name mode
        elif char in string.ascii_letters + "_.":
            self.tokenize_data["value"] = char
            self.tokenize_mode = self.tokenize_mode_name
            processed = True

        # Check for space
        if char in ("\t", " "):
            if "space" not in self.tokenize_data:
                self.tokens.append(Token(TokenType.SPACE, line, column))
                self.tokenize_data["space"] = None
            processed = True
        else:
            if "space" in self.tokenize_data:
                del self.tokenize_data["space"]

        # Raise error, if the char couldn't processed
        if not processed:
            Error(self, line, ErrorType.SYNTAX, f"Unknown char {char!r}! Hint: Names are only allowed to contain\n" +
                  f"the following characters and can't start with a digit:\n_{string.ascii_letters}{string.digits}").exit()

        return False

    def tokenize_mode_string(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in string mode"""

        # Raise error, if the string was not closed until the end of the line
        if char == "\n":
            Error(self, line, ErrorType.SYNTAX,
                  "String was not closed until the end of the line!").exit()

        # Check for string closing
        elif char in ("'", '"'):
            self.tokens.append(Token(TokenType.STRING, line,
                column - len(self.tokenize_data["value"]), self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return False

        # Add the char
        self.tokenize_data["value"] += char

        return False

    def tokenize_mode_value(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in value mode"""

        # Ignore underscore char
        if char == "_":
            return False

        # Define allowed chars
        if len(self.tokenize_data["value"]) == 1 and self.tokenize_data["type"] == TokenType.DECIMAL:
            allowed = string.hexdigits + "xobXOB"
        else:
            allowed = string.hexdigits

        # Check for the end of the value
        if char not in allowed:
            if len(self.tokenize_data["value"]) == 0:
                Error(self, line, ErrorType.SYNTAX, f"Empty {self.tokenize_data['type'].value} value definition!").exit()
            self.tokens.append(Token(self.tokenize_data["type"], line,
                column - len(self.tokenize_data["value"]), self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return self.tokenize_mode(line, code, column, char)

        # Check for value type definition
        if len(self.tokenize_data["value"]) == 1 and self.tokenize_data["type"] == TokenType.DECIMAL:

            # If the value type is decimal, add the char
            if char in string.digits:
                self.tokenize_data["value"] += char
                return False

            # Raise error, if the first char is not 0
            if self.tokenize_data["value"] != "0":
                Error(self, line, ErrorType.SYNTAX, "The first digit of a non-decimal value definition" +
                      f" need to be 0, not {self.tokenize_data['value']!r}!").exit()

            # If the type is valid, set it up, else, raise error
            token_type = {"x": TokenType.HEXADECIMAL, "o": TokenType.OCTAL, "b": TokenType.BINARY}
            if char.lower() not in token_type:
                Error(self, line, ErrorType.SYNTAX,
                    f"Invalid char {char!r} in decimal value definition!").exit()
            self.tokenize_data["type"] = token_type[char.lower()]
            self.tokenize_data["value"] = ""
            return False

        # Raise error, if the type don't support the char
        if self.tokenize_data["type"] != TokenType.HEXADECIMAL:
            allowed = {TokenType.DECIMAL: string.digits, TokenType.OCTAL: string.octdigits, TokenType.BINARY: "01"}
            if char not in allowed[self.tokenize_data["type"]]:
                Error(self, line, ErrorType.SYNTAX,
                      f"Invalid char {char!r} in {self.tokenize_data['type'].value} value definition!").exit()

        # Add the char
        self.tokenize_data["value"] += char

        return False

    def tokenize_mode_name(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in name mode"""

        # Check for the end of the name
        if char not in string.ascii_letters + string.digits + "_.":

            # Check for keywords
            keywords = {"include": TokenType.INCLUDE, "export": TokenType.EXPORT,
                        "code": TokenType.CODE, "const": TokenType.CONSTANT,
                        "var": TokenType.VARIABLE, "res": TokenType.RESOURCE}
            if self.tokenize_data["value"].lower() in keywords:
                self.tokens.append(Token(keywords[self.tokenize_data["value"].lower()], line,
                    column - len(self.tokenize_data["value"])))

            # Check for registers
            elif len(self.tokenize_data["value"]) == 1 and self.tokenize_data["value"].lower() in "abcdhlzf":
                self.tokens.append(Token(TokenType.REGISTER, line, column - 1, self.tokenize_data["value"].lower()))

            # Normal name
            else:
                self.tokens.append(Token(TokenType.NAME, line,
                    column - len(self.tokenize_data["value"]), self.tokenize_data["value"]))

            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return self.tokenize_mode(line, code, column, char)

        # Add the char
        self.tokenize_data["value"] += char

        return False

    def tokenize_mode_argument(self, line: int, code: str, column: int, char: str) -> bool:
        """Tokenize a char in argument mode"""

        # Check first char
        if len(self.tokenize_data["value"]) == 0:
            if char not in "ria":
                Error(self, line, ErrorType.SYNTAX,
                    f"The first char of a argument definition must be 'r', 'i' or 'a', not {char!r}!").exit()

        # Check second char
        elif len(self.tokenize_data["value"]) == 1:
            if char not in string.digits:
                Error(self, line, ErrorType.SYNTAX,
                    f"The second char of a argument definition must be a digit, not {char!r}!").exit()

        # Add the argument
        else:
            self.tokens.append(Token(TokenType.ARGUMENT, line, column - 3, self.tokenize_data["value"]))
            self.tokenize_data.clear()
            self.tokenize_mode = self.tokenize_mode_normal
            return self.tokenize_mode(line, code, column, char)

        # Add the char
        self.tokenize_data["value"] += char

        return False

    def parse(self) -> None:
        """Parse the tokens"""

        # Loop through each abstract line
        for abstract in self.abstract_lines:

            # Handle line in mode and pass the token and abstract line
            self.parse_mode(self.token_lines[abstract[0].line], abstract)

    def parse_mode_definition(self, tokens: list[Token], abstract: list[Token]) -> None:
        """Parse the tokens in definition section"""

        # Check for macro
        if "macro" in self.parse_data:
            if self.parse_mode_macro(tokens, abstract):
                return

        # Define check information for the different keywords
        checks = {TokenType.CODE: (1, 0, False, "It has no arguments."),
                  TokenType.INCLUDE: (0, 1, False, ""),
                  TokenType.EXPORT: (3, 1, True, "It takes 1 argument, which is the name of the thing to export."),
                  TokenType.CONSTANT: (5, 2, True, "It takes 2 arguments, the name and the value."),
                  TokenType.VARIABLE: (5, 2, True, "It takes 2 arguments, the name and the size."),
                  TokenType.RESOURCE: (5, 2, True, "It takes 2 arguments, the name and the value.")}

        # Check for all keywords
        for token_type, (length, check_space, check_name, description) in checks.items():

            if not token_list_contains(abstract, token_type):
                continue

            # Check for keyword position
            if abstract[0].type != token_type:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      f"Invalid usage of the {token_type.value} keyword!\n" +
                      f"The keyword need to be at the beginning of the line.").exit()

            # Check for keyword argument length
            if len(abstract) != length and length != 0:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      f"Invalid usage of the {token_type.value} keyword!\n" +
                      description).exit()

            # Check for spaces between the keyword and the arguments
            if (check_space != 0 and abstract[1].type != TokenType.SPACE) or \
               (check_space == 2 and abstract[3].type != TokenType.SPACE):
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      f"Invalid usage of the {token_type.value} keyword!\n" +
                      f"The {'argument needs' if check_space == 1 else 'arguments need'} " +
                      f"to be separated with {'a space' if check_space == 1 else 'spaces'}.").exit()

            # Check for name token type
            if check_name and abstract[2].type != TokenType.NAME:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      f"Invalid usage of the {token_type.value} keyword!\n" +
                      "The first argument needs to be a name.").exit()

        # Match token
        match abstract[0].type:
            case TokenType.CODE:
                self.parse_data.clear()
                self.parse_mode = self.parse_mode_code
            case TokenType.INCLUDE:
                if len(abstract) < 3:
                    Error(self, abstract[0].line, ErrorType.SYNTAX,
                          "Invalid usage of the include keyword!\n" +
                          "It takes one or more names and slashes, alternatively also a single string.").exit()
                self.includes.append(Include(abstract[2:]))
            case TokenType.EXPORT:
                self.exports.append(Export(abstract[2]))
            case TokenType.CONSTANT:
                self.constants.append(Constant(abstract[2], abstract[4]))
            case TokenType.VARIABLE:
                self.variables.append(Variable(abstract[2], abstract[4]))
            case TokenType.RESOURCE:
                self.resources.append(Resource(abstract[2], abstract[4]))
            case TokenType.AT:
                if len(abstract) != 2 or abstract[1].type != TokenType.NAME:
                    Error(self, abstract[0].line, ErrorType.SYNTAX,
                          "Invalid decorator! An '@' needs to be followed by a name without a space.").exit()
                if abstract[1].value not in ("macro", "func"):
                    Error(self, abstract[0].line, ErrorType.SYNTAX,
                          "Unknown decorator! Possible decorators: @macro, @func").exit()
                if abstract[1].value != "macro":
                    Error(self, abstract[0].line, ErrorType.SYNTAX,
                          "Wrong section for decorator! The definition section can only contain macros.").exit()
                self.parse_data["macro"] = False
            case _:
                value = "" if abstract[0].value is None else f" (value: {abstract[0].value})"
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      f"Invalid token '{abstract[0].type.value}'{value}\n" +
                      "at the beginning of the line in the definition section!").exit()

    def parse_mode_macro(self, tokens: list[Token], abstract: list[Token]) -> None:
        """Parse the tokens of a macro in the definition section"""

        # If the macro was created
        if self.parse_data["macro"]:

            if abstract[0].type != TokenType.NAME:
                del self.parse_data["macro"]
                return False

            if abstract[-1].type == TokenType.COLON:
                if len(abstract) != 2:
                    Error(self, abstract[0].line, ErrorType.SYNTAX,
                          f"Invalid label definition! A name directly followed by a colon ':' is expected.").exit()
                self.macros[-1].labels.append(Label(abstract[0], len(self.macros[0].instructions)))
                return True

            if len(abstract) == 1:
                self.macros[-1].instructions.append(Instruction(abstract[0], []))
                return True

            if len(abstract) < 3 or abstract[1].type != TokenType.SPACE:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      "Invalid instruction definition!\n" +
                      "Between the arguments and the name a space is expected.").exit()

            arguments = token_list_split(abstract[2:], TokenType.COMMA)
            arguments = [token_list_remove(token_list_remove(arg, TokenType.COMMA), TokenType.SPACE) for arg in arguments]
            for argument in arguments:
                if len(argument) != 1:
                    Error(self, abstract[0].line, ErrorType.SYNTAX,
                          "Invalid instruction definition!\n" +
                          "The arguments need to be separated with a comma.").exit()

            self.macros[-1].instructions.append(Instruction(abstract[0], [arg[0] for arg in arguments]))

            return True

        # Create the macro
        self.parse_data["macro"] = True

        if abstract[0].type != TokenType.NAME or abstract[-1].type != TokenType.COLON:
            Error(self, abstract[0].line, ErrorType.SYNTAX,
                  "Invalid macro definition! After @macro a label is expected.").exit()

        if len(abstract) == 2:
            self.macros.append(Macro(abstract[0], []))
            return True

        if abstract[1].type != TokenType.SPACE:
            Error(self, abstract[0].line, ErrorType.SYNTAX,
                  "Invalid macro label definition! The parameters need to be separated with a space.").exit()

        arguments = token_list_split(abstract[2:-1], TokenType.COMMA)
        arguments = [token_list_remove(token_list_remove(arg, TokenType.COMMA), TokenType.SPACE) for arg in arguments]
        for argument in arguments:
            if len(argument) != 1 or argument[0].type != TokenType.ARGUMENT:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      "Invalid macro label definition! Invalid parameters.").exit()

        self.macros.append(Macro(abstract[0], [arg[0] for arg in arguments]))

        return True

    def parse_mode_code(self, tokens: list[Token], abstract: list[Token]) -> None:
        """Parse the tokens in the code section"""

        if abstract[0].type not in (TokenType.NAME, TokenType.AT):
            value = "" if abstract[0].value is None else f" (value: {abstract[0].value})"
            Error(self, abstract[0].line, ErrorType.SYNTAX,
                  f"Invalid token '{abstract[0].type.value}'{value}\n" +
                  "at the beginning of the line in the code section!").exit()

        if abstract[-1].type == TokenType.COLON:
            if len(abstract) != 2 or abstract[0].type != TokenType.NAME:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      f"Invalid label definition! A name directly followed by a colon ':' is expected.").exit()
            self.labels.append(Label(abstract[0], len(self.instructions), "func" in self.parse_data))
            if "func" in self.parse_data:
                del self.parse_data["func"]
            return

        if "func" in self.parse_data:
            Error(self, self.parse_data["func"], ErrorType.SYNTAX,
                  "Floating decorator! A decorator needs to be followed by a label.").exit()

        if abstract[0].type == TokenType.AT:
            if len(abstract) != 2 or abstract[1].type != TokenType.NAME:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      "Invalid decorator! An '@' needs to be followed by a name without a space.").exit()
            if abstract[1].value not in ("macro", "func"):
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      "Unknown decorator! Possible decorators: @macro, @func").exit()
            if abstract[1].value == "macro":
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      "Wrong section for decorator! Macros need to be defined in the definition section.").exit()
            self.parse_data["func"] = abstract[0].line
            return

        if len(abstract) == 1:
            self.instructions.append(Instruction(abstract[0], []))
            return

        if len(abstract) < 3 or abstract[1].type != TokenType.SPACE:
            Error(self, abstract[0].line, ErrorType.SYNTAX,
                  "Invalid instruction definition!\n" +
                  "Between the arguments and the name a space is expected.").exit()

        arguments = token_list_split(abstract[2:], TokenType.COMMA)
        arguments = [token_list_remove(token_list_remove(arg, TokenType.COMMA), TokenType.SPACE) for arg in arguments]
        for argument in arguments:
            if len(argument) != 1:
                Error(self, abstract[0].line, ErrorType.SYNTAX,
                      "Invalid instruction definition!\n" +
                      "The arguments need to be separated with a comma.").exit()

        self.instructions.append(Instruction(abstract[0], [arg[0] for arg in arguments]))

    @classmethod
    def file(cls, path: str, modules: dict[str, Self], main: bool = False) -> Self:
        """Load a module from file"""

        with open(path, "r", encoding="utf-8") as f:
            return cls(f.read(), path, modules, main)

