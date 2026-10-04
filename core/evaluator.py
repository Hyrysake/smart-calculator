"""Evaluation of arithmetic expressions.

The evaluator converts the token list produced by :mod:`core.tokenizer`
into Reverse Polish Notation using Dijkstra's shunting-yard algorithm and
then computes the result from that notation.

Python's built-in ``eval`` is deliberately not used: it would execute any
code the user types, which is a security hole, and it would teach us
nothing about how precedence actually works.

Functions and constants are injected by the caller, so this module has no
dependency on :mod:`core.scientific`.

Author: Дмитрук Назар Сергійович (Team Lead)
"""

import operator
from typing import Callable, NamedTuple

from core.tokenizer import (
    IDENT,
    LEFT_PAREN,
    NUMBER,
    OPERATOR,
    RIGHT_PAREN,
    UNARY_MINUS,
    Token,
    TokenizeError,
    tokenize,
)


class EvaluationError(ValueError):
    """Raised when a syntactically read expression cannot be computed."""


class Operator(NamedTuple):
    """Description of one operator.

    Attributes:
        precedence: higher binds tighter, so ``*`` beats ``+``.
        right_associative: True for power, where 2^3^2 == 2^(3^2).
        arity: 1 for negation, 2 for the ordinary operators.
        function: the callable that performs the arithmetic.
    """

    precedence: int
    right_associative: bool
    arity: int
    function: Callable


def _divide(left: float, right: float) -> float:
    """Divide, reporting division by zero in our own error type."""
    if right == 0:
        raise EvaluationError("Division by zero")
    return left / right


def _modulo(left: float, right: float) -> float:
    """Remainder of division, with the same zero check as division."""
    if right == 0:
        raise EvaluationError("Division by zero")
    return left % right


def _power(left: float, right: float) -> float:
    """Raise ``left`` to the power of ``right``, rejecting complex results."""
    try:
        result = left**right
    except OverflowError as error:
        raise EvaluationError("Result is too large") from error

    if isinstance(result, complex):
        raise EvaluationError("Result is not a real number")
    return float(result)


# The operator table drives the whole algorithm. Adding an operator here is
# enough for both the shunting-yard pass and the calculation pass to support
# it -- no other code has to change.
OPERATORS: dict[str, Operator] = {
    "+": Operator(1, False, 2, operator.add),
    "-": Operator(1, False, 2, operator.sub),
    "*": Operator(2, False, 2, operator.mul),
    "/": Operator(2, False, 2, _divide),
    "%": Operator(2, False, 2, _modulo),
    "^": Operator(3, True, 2, _power),
    UNARY_MINUS: Operator(4, True, 1, operator.neg),
}


def to_rpn(tokens: list[Token], functions: dict, constants: dict) -> list[Token]:
    """Reorder tokens from infix into Reverse Polish Notation.

    This is the shunting-yard algorithm. Numbers go straight to the output;
    operators wait on a stack until an operator of lower precedence arrives;
    brackets control when the stack is flushed.

    Args:
        tokens: tokens produced by :func:`core.tokenizer.tokenize`.
        functions: mapping of function name to callable.
        constants: mapping of constant name to its numeric value.

    Returns:
        The same tokens in postfix order.

    Raises:
        EvaluationError: on unbalanced brackets or an unknown name.
    """
    output: list[Token] = []
    stack: list[Token] = []

    for token in tokens:
        if token.type == NUMBER:
            output.append(token)

        elif token.type == IDENT:
            name = str(token.value)
            if name in constants:
                # A constant behaves exactly like a literal number.
                output.append(Token(NUMBER, float(constants[name])))
            elif name in functions:
                stack.append(token)
            else:
                raise EvaluationError(f"Unknown name '{name}'")

        elif token.type == OPERATOR:
            current = OPERATORS[str(token.value)]
            while stack and stack[-1].type == OPERATOR:
                previous = OPERATORS[str(stack[-1].value)]
                takes_priority = previous.precedence > current.precedence or (
                    previous.precedence == current.precedence and not current.right_associative
                )
                if not takes_priority:
                    break
                output.append(stack.pop())
            stack.append(token)

        elif token.type == LEFT_PAREN:
            stack.append(token)

        elif token.type == RIGHT_PAREN:
            while stack and stack[-1].type != LEFT_PAREN:
                output.append(stack.pop())
            if not stack:
                raise EvaluationError("Unbalanced brackets")
            stack.pop()  # discard the matching '('
            # A function name sitting directly before '(' applies to the
            # bracketed value, so it is emitted right after it.
            if stack and stack[-1].type == IDENT:
                output.append(stack.pop())

    while stack:
        token = stack.pop()
        if token.type in (LEFT_PAREN, RIGHT_PAREN):
            raise EvaluationError("Unbalanced brackets")
        output.append(token)

    return output


def evaluate_rpn(rpn: list[Token], functions: dict) -> float:
    """Compute the value of an expression written in postfix notation.

    Args:
        rpn: tokens in Reverse Polish Notation.
        functions: mapping of function name to callable.

    Returns:
        The numeric result.

    Raises:
        EvaluationError: if the expression is incomplete or malformed.
    """
    stack: list[float] = []

    for token in rpn:
        if token.type == NUMBER:
            stack.append(float(token.value))

        elif token.type == OPERATOR:
            definition = OPERATORS[str(token.value)]
            if len(stack) < definition.arity:
                raise EvaluationError("Incomplete expression")
            if definition.arity == 1:
                stack.append(definition.function(stack.pop()))
            else:
                right = stack.pop()
                left = stack.pop()
                stack.append(definition.function(left, right))

        elif token.type == IDENT:
            if not stack:
                raise EvaluationError("Incomplete expression")
            stack.append(functions[str(token.value)](stack.pop()))

    if len(stack) != 1:
        raise EvaluationError("Incomplete expression")
    return stack[0]


def evaluate(expression: str, functions: dict | None = None, constants: dict | None = None) -> float:
    """Calculate the value of an infix expression.

    Args:
        expression: text typed by the user, e.g. ``"2+3*(4-1)^2"``.
        functions: optional mapping of function name to callable.
        constants: optional mapping of constant name to value.

    Returns:
        The numeric result of the expression.

    Raises:
        EvaluationError: if the expression cannot be read or computed.

    Example:
        >>> evaluate("2+3*(4-1)^2")
        29.0
    """
    functions = functions or {}
    constants = constants or {}

    try:
        tokens = tokenize(expression)
    except TokenizeError as error:
        raise EvaluationError(str(error)) from error

    rpn = to_rpn(tokens, functions, constants)

    try:
        return evaluate_rpn(rpn, functions)
    except EvaluationError:
        raise
    except (ValueError, OverflowError, ZeroDivisionError) as error:
        # Anything a scientific function rejects (log of a negative number,
        # factorial of a fraction and so on) arrives here.
        raise EvaluationError(str(error)) from error


def format_result(value: float) -> str:
    """Render a result the way a calculator display should show it.

    Whole numbers lose the trailing ``.0`` and long fractions are rounded,
    so ``0.1 + 0.2`` reads as ``0.3`` instead of ``0.30000000000000004``.

    Args:
        value: the number to display.

    Returns:
        The string to put on the display.
    """
    rounded = round(value, 10)
    if rounded == int(rounded) and abs(rounded) < 1e16:
        return str(int(rounded))
    return f"{rounded:g}"
