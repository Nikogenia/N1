# Standard
from dataclasses import dataclass
from enum import StrEnum, auto


class TokenType(StrEnum):
    """Type of a token"""

    SPACE = auto()
    NEWLINE = auto()
    COMMENT = auto()
    ARGUMENT = auto()
    COLON = auto()
    COMMA = auto()
    SLASH = auto()
    AT = auto()
    DOLLAR = auto()
    ASTERISK = auto()
    INCLUDE = auto()
    EXPORT = auto()
    CODE = auto()
    CONSTANT = auto()
    VARIABLE = auto()
    RESOURCE = auto()
    NAME = auto()
    STRING = auto()
    DECIMAL = auto()
    HEXADECIMAL = auto()
    OCTAL = auto()
    BINARY = auto()
    REGISTER = auto()


@dataclass(repr=False, frozen=True, slots=True)
class Token:
    """Token with type, line and column number and optional value"""

    type: TokenType
    line: int
    column: int
    value: int | str = None

    def __repr__(self):
        value = "" if self.value is None else f" = {self.value!r}"
        return f"Token({self.line}:{self.column} | {self.type.name}" + value + ")"

    def __str__(self):
        value = "" if self.value is None else repr(self.value)
        return f"{f'{self.line}:{self.column}':<7}{self.type.name:<12}{value}"


def token_list_type(token_list: list[Token]) -> list[TokenType]:
    """Get a list with the types of the tokens in the list"""
    return [token.type for token in token_list]


def token_list_contains(token_list: list[Token], token_type: TokenType) -> bool:
    """Check for a token of a given type is in a list"""
    return token_type in token_list_type(token_list)


def token_list_remove(token_list: list[Token], token_type: TokenType) -> list[Token]:
    """Remove all tokens of a given type from the list"""
    return [token for token in token_list if token.type != token_type]


def token_list_split(token_list: list[Token], token_type: TokenType) -> list[list[Token]]:
    """Split a list of tokens into sublists, separated by a token of a given type"""

    # Generate a split index
    split_index = [i + 1 for i, token in enumerate(token_list) if token.type == token_type]
    if len(split_index) == 0:
        return [token_list]

    # Slice all lists from index
    slicing_end = [len(token_list)] if split_index[-1] != len(token_list) else []
    splitted = [token_list[i:j] for i, j in zip([0] + split_index, split_index + slicing_end)]
    return splitted if splitted[-1] else splitted[:-1]

