"""Lexical analysis of arithmetic expressions.

The tokenizer turns a raw expression string such as ``2 + 3 * (4 - 1)^2``
into a flat list of tokens. It performs no arithmetic and knows nothing
about operator precedence -- that is the evaluator's job.

Author: Дмитрук Назар Сергійович (Team Lead)
"""

from typing import NamedTuple

# Token type names. Plain strings are used instead of an Enum to keep the
# module easy to read and to print during debugging.
NUMBER = "NUMBER"
IDENT = "IDENT"
OPERATOR = "OPERATOR"
LEFT_PAREN = "LEFT_PAREN"
RIGHT_PAREN = "RIGHT_PAREN"

# Every binary operator the calculator understands.
BINARY_OPERATORS = "+-*/%^"

# Internal name for a minus sign used as negation ("-5") rather than as
# subtraction ("7-5"). Marking it already at the tokenizer stage means the
# evaluator never has to guess which of the two meanings was intended.
UNARY_MINUS = "u-"


class Token(NamedTuple):
    """A single meaningful unit of an expression.

    Attributes:
        type: one of NUMBER, IDENT, OPERATOR, LEFT_PAREN, RIGHT_PAREN.
        value: the number itself for NUMBER, otherwise the raw text.
    """

    type: str
    value: object

    def __repr__(self) -> str:
        return f"{self.type}({self.value})"


class TokenizeError(ValueError):
    """Raised when the expression contains a character we cannot read."""


def _read_number(expression: str, start: int) -> tuple[float, int]:
    """Read one number starting at ``start``.

    Args:
        expression: the whole expression being scanned.
        start: index of the first digit or dot of the number.

    Returns:
        A tuple of the parsed number and the index of the first character
        after it.

    Raises:
        TokenizeError: if the number contains more than one decimal point.
    """
    index = start
    seen_dot = False

    while index < len(expression):
        char = expression[index]
        if char.isdigit():
            index += 1
        elif char == ".":
            if seen_dot:
                raise TokenizeError(f"Malformed number at position {start + 1}")
            seen_dot = True
            index += 1
        else:
            break

    text = expression[start:index]
    if text in (".",):
        raise TokenizeError(f"Malformed number at position {start + 1}")
    return float(text), index


def _read_identifier(expression: str, start: int) -> tuple[str, int]:
    """Read a function or constant name starting at ``start``.

    Returns:
        A tuple of the lowercase name and the index right after it.
    """
    index = start
    while index < len(expression) and (expression[index].isalpha() or expression[index].isdigit()):
        index += 1
    return expression[start:index].lower(), index


def _is_unary_context(tokens: list[Token]) -> bool:
    """Decide whether a minus sign at this point means negation.

    A minus is unary when it opens the expression, follows another
    operator, or follows an opening bracket. In every other case it is
    ordinary subtraction.
    """
    if not tokens:
        return True

    previous = tokens[-1]
    return previous.type in (OPERATOR, LEFT_PAREN)


def tokenize(expression: str) -> list[Token]:
    """Split an expression into tokens.

    Args:
        expression: raw text typed by the user, e.g. ``"2+3*(4-1)"``.

    Returns:
        The list of tokens in the order they appear.

    Raises:
        TokenizeError: on an empty expression or an unexpected character.

    Example:
        >>> tokenize("2+3")
        [NUMBER(2.0), OPERATOR(+), NUMBER(3.0)]
    """
    if not expression or not expression.strip():
        raise TokenizeError("Expression is empty")

    tokens: list[Token] = []
    index = 0

    while index < len(expression):
        char = expression[index]

        # Spaces carry no meaning and are simply skipped.
        if char.isspace():
            index += 1
            continue

        if char.isdigit() or char == ".":
            value, index = _read_number(expression, index)
            tokens.append(Token(NUMBER, value))
            continue

        if char.isalpha():
            name, index = _read_identifier(expression, index)
            tokens.append(Token(IDENT, name))
            continue

        if char in BINARY_OPERATORS:
            if char == "-" and _is_unary_context(tokens):
                tokens.append(Token(OPERATOR, UNARY_MINUS))
            else:
                tokens.append(Token(OPERATOR, char))
            index += 1
            continue

        if char == "(":
            tokens.append(Token(LEFT_PAREN, char))
            index += 1
            continue

        if char == ")":
            tokens.append(Token(RIGHT_PAREN, char))
            index += 1
            continue

        raise TokenizeError(f"Unexpected character '{char}' at position {index + 1}")

    return tokens
