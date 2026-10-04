"""Tests for the tokenizer and the expression evaluator.

Run from the project root with::

    python -m pytest -v

Author: Бардюк Станіслав Олександрович (QA)
"""

import pytest

from core.evaluator import EvaluationError, evaluate, format_result
from core.scientific import CONSTANTS, build_functions
from core.tokenizer import NUMBER, OPERATOR, TokenizeError, tokenize


def calculate(expression: str, angle_mode: str = "deg") -> float:
    """Evaluate an expression with the full function table available."""
    return evaluate(expression, functions=build_functions(angle_mode), constants=CONSTANTS)


class TestTokenizer:
    """The lexical stage: text in, tokens out."""

    def test_splits_numbers_and_operators(self):
        tokens = tokenize("12+5")
        assert [token.type for token in tokens] == [NUMBER, OPERATOR, NUMBER]
        assert tokens[0].value == 12.0

    def test_ignores_spaces(self):
        assert len(tokenize("  2  +  2  ")) == 3

    def test_marks_leading_minus_as_unary(self):
        tokens = tokenize("-5")
        assert tokens[0].value == "u-"

    def test_keeps_minus_between_numbers_binary(self):
        tokens = tokenize("7-5")
        assert tokens[1].value == "-"

    def test_rejects_unknown_character(self):
        with pytest.raises(TokenizeError):
            tokenize("2 $ 3")

    def test_rejects_empty_expression(self):
        with pytest.raises(TokenizeError):
            tokenize("   ")


class TestArithmetic:
    """Basic operations and the order in which they are applied."""

    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("2+2", 4),
            ("10-3", 7),
            ("6*7", 42),
            ("9/2", 4.5),
            ("10%3", 1),
            ("2^10", 1024),
        ],
    )
    def test_single_operations(self, expression, expected):
        assert calculate(expression) == pytest.approx(expected)

    def test_multiplication_before_addition(self):
        assert calculate("2+3*4") == pytest.approx(14)

    def test_brackets_change_the_order(self):
        assert calculate("(2+3)*4") == pytest.approx(20)

    def test_power_is_right_associative(self):
        # 2^(3^2) = 512, not (2^3)^2 = 64.
        assert calculate("2^3^2") == pytest.approx(512)

    def test_nested_brackets(self):
        assert calculate("2+3*(4-1)^2") == pytest.approx(29)

    def test_unary_minus(self):
        assert calculate("-5+3") == pytest.approx(-2)

    def test_unary_minus_after_operator(self):
        assert calculate("4*-2") == pytest.approx(-8)

    def test_unary_minus_before_bracket(self):
        assert calculate("-(3+2)") == pytest.approx(-5)

    def test_decimal_numbers(self):
        assert calculate("0.1+0.2") == pytest.approx(0.3)


class TestErrors:
    """Wrong input must produce a clear error, never a crash."""

    def test_division_by_zero(self):
        with pytest.raises(EvaluationError, match="Division by zero"):
            calculate("5/0")

    def test_modulo_by_zero(self):
        with pytest.raises(EvaluationError):
            calculate("5%0")

    def test_unbalanced_opening_bracket(self):
        with pytest.raises(EvaluationError, match="Unbalanced"):
            calculate("(2+3")

    def test_unbalanced_closing_bracket(self):
        with pytest.raises(EvaluationError, match="Unbalanced"):
            calculate("2+3)")

    def test_incomplete_expression(self):
        with pytest.raises(EvaluationError):
            calculate("2+")

    def test_unknown_function_name(self):
        with pytest.raises(EvaluationError, match="Unknown name"):
            calculate("foo(2)")


class TestScientificFunctions:
    """Trigonometry, logarithms, roots and factorial."""

    def test_sin_in_degrees(self):
        assert calculate("sin(30)") == pytest.approx(0.5)

    def test_sin_in_radians(self):
        assert calculate("sin(0)", angle_mode="rad") == pytest.approx(0)

    def test_cos_in_degrees(self):
        assert calculate("cos(60)") == pytest.approx(0.5)

    def test_square_root(self):
        assert calculate("sqrt(16)") == pytest.approx(4)

    def test_logarithm_base_ten(self):
        assert calculate("log(1000)") == pytest.approx(3)

    def test_natural_logarithm(self):
        assert calculate("ln(e)") == pytest.approx(1)

    def test_factorial(self):
        assert calculate("fact(5)") == pytest.approx(120)

    def test_constant_pi(self):
        assert calculate("pi") == pytest.approx(3.14159265, abs=1e-8)

    def test_function_inside_arithmetic(self):
        assert calculate("2*sqrt(9)+1") == pytest.approx(7)

    def test_square_root_of_negative_is_rejected(self):
        with pytest.raises(EvaluationError):
            calculate("sqrt(-4)")

    def test_factorial_of_fraction_is_rejected(self):
        with pytest.raises(EvaluationError):
            calculate("fact(2.5)")

    def test_logarithm_of_zero_is_rejected(self):
        with pytest.raises(EvaluationError):
            calculate("log(0)")


class TestFormatting:
    """The display should look like a calculator, not like a float dump."""

    def test_whole_number_loses_decimal_part(self):
        assert format_result(4.0) == "4"

    def test_floating_point_noise_is_rounded_away(self):
        assert format_result(0.1 + 0.2) == "0.3"

    def test_negative_whole_number(self):
        assert format_result(-7.0) == "-7"
