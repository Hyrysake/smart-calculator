"""Наукові функції калькулятора та математичні константи.

Словник функцій передається обчислювачу, тому ядро не залежить від цього
модуля. Частина Developer: Махнюк Андрій Сергійович, ІПЗ-22.
"""

import math
from typing import Callable

# Ці назви можна використовувати у виразі, наприклад 2*pi.
CONSTANTS: dict[str, float] = {"pi": math.pi, "e": math.e}
DEGREES = "deg"
RADIANS = "rad"


def _factorial(value: float) -> float:
    """Обчислює факторіал цілого числа від 0 до 170 включно."""
    # Нескінченне значення не можна перетворити на ціле число.
    if not math.isfinite(value):
        raise ValueError("Аргумент має бути скінченним числом")
    if value < 0:
        raise ValueError("Факторіал від’ємного числа не визначений")
    if value != int(value):
        raise ValueError("Факторіал визначений лише для цілих чисел")
    if value > 170:
        raise ValueError("Факторіал завеликий: допустимі числа від 0 до 170")
    return float(math.factorial(int(value)))


def _safe_sqrt(value: float) -> float:
    """Перевіряє область визначення квадратного кореня."""
    if value < 0:
        raise ValueError("Корінь від’ємного числа не визначений у дійсних числах")
    return math.sqrt(value)


def _safe_log10(value: float) -> float:
    """Обчислює десятковий логарифм додатного числа."""
    if value <= 0:
        raise ValueError("Логарифм визначений лише для додатних чисел")
    return math.log10(value)


def _safe_ln(value: float) -> float:
    """Обчислює натуральний логарифм додатного числа."""
    if value <= 0:
        raise ValueError("Логарифм визначений лише для додатних чисел")
    return math.log(value)


def _safe_asin(value: float) -> float:
    """Повертає арксинус у радіанах для аргументу від -1 до 1."""
    if not -1 <= value <= 1:
        raise ValueError("Для asin аргумент має бути від -1 до 1")
    return math.asin(value)


def _safe_acos(value: float) -> float:
    """Повертає арккосинус у радіанах для аргументу від -1 до 1."""
    if not -1 <= value <= 1:
        raise ValueError("Для acos аргумент має бути від -1 до 1")
    return math.acos(value)


def _checked(function: Callable[[float], float]) -> Callable[[float], float]:
    """Перевіряє скінченність аргументу й результату наукової функції."""
    def calculate(value: float) -> float:
        """Виконує одну функцію і пояснює переповнення українською."""
        if not math.isfinite(value):
            raise ValueError("Аргумент має бути скінченним числом")
        try:
            result = function(value)
        except OverflowError as error:
            raise ValueError("Результат завеликий") from error
        if not math.isfinite(result):
            raise ValueError("Результат не є скінченним числом")
        return result
    return calculate


def build_functions(angle_mode: str = DEGREES) -> dict[str, Callable[[float], float]]:
    """Створює таблицю функцій для режиму deg або rad.

    math працює в радіанах: у DEG прямі функції отримують перетворений
    аргумент, а результати обернених функцій переводяться у градуси.
    Наприклад, build_functions('deg')['sin'](30) наближено дорівнює 0.5.
    """
    if angle_mode not in (DEGREES, RADIANS):
        raise ValueError("Невідомий режим кутів: використайте deg або rad")
    if angle_mode == DEGREES:
        to_internal = math.radians
        from_internal = math.degrees
    else:
        # У режимі RAD перетворення одиниць не потрібне.
        def to_internal(value: float) -> float:
            """Залишає аргумент у радіанах."""
            return value

        def from_internal(value: float) -> float:
            """Залишає результат у радіанах."""
            return value

    functions = {
        "sin": lambda value: math.sin(to_internal(value)),
        "cos": lambda value: math.cos(to_internal(value)),
        "tan": lambda value: math.tan(to_internal(value)),
        "asin": lambda value: from_internal(_safe_asin(value)),
        "acos": lambda value: from_internal(_safe_acos(value)),
        "atan": lambda value: from_internal(math.atan(value)),
        "sqrt": _safe_sqrt,
        "log": _safe_log10,
        "ln": _safe_ln,
        "exp": math.exp,
        "abs": abs,
        "fact": _factorial,
    }
    # Однакова перевірка застосовується до всіх наукових функцій.
    return {name: _checked(function) for name, function in functions.items()}
