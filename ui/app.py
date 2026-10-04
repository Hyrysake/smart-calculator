<<<<<<< HEAD
"""Graphical interface of the calculator, built with CustomTkinter.

The window owns no arithmetic of its own: everything typed on the display
is handed to :func:`core.evaluator.evaluate`, and the function table comes
from :mod:`core.scientific`. The history store is optional, so the window
runs perfectly well on its own.

Author: Махнюк Андрій (Developer)
"""
=======
"""Графічний інтерфейс наукового калькулятора на CustomTkinter.

Обчислення виконує core.evaluator, наукові функції надає core.scientific.
Панель історії додається окремим модулем команди.
Частина Developer: Махнюк Андрій Сергійович, ІПЗ-22."""

import math
import re
>>>>>>> main

import customtkinter as ctk

from core.evaluator import EvaluationError, evaluate, format_result
from core.scientific import CONSTANTS, DEGREES, RADIANS, build_functions
<<<<<<< HEAD
from ui.history_panel import HistoryPanel

# Colours are kept in one place so the whole window can be restyled here.
# The four groups of keys are deliberately given different weights:
# scientific keys are the quietest, then digits, then operators, and the
# equals key is the brightest thing on screen.
=======

# Кольори кнопок зібрано в одному місці.
# Наукові функції, цифри та оператори мають різні кольори.
# Кнопка рівності виділена найяскравіше.
# Це допомагає швидко знайти потрібну дію.
>>>>>>> main
ACCENT = "#2f6bff"
ACCENT_HOVER = "#1d52d4"
SCIENTIFIC_COLOR = "#2b303b"
SCIENTIFIC_HOVER = "#363d4c"
DIGIT_COLOR = "#3a4150"
DIGIT_HOVER = "#474f61"
OPERATOR_COLOR = "#2f4a7a"
OPERATOR_HOVER = "#3a5b96"
DANGER = "#c0392b"
DANGER_HOVER = "#a33025"
<<<<<<< HEAD


class CalculatorApp(ctk.CTk):
    """Main application window.

    Args:
        store: optional object with ``add``, ``items`` and ``clear``
            methods used to remember past calculations. When it is None the
            calculator still works, simply without history.
    """
=======
MUTED = "#8b93a7"


def _error_message(message: str) -> str:
    """Перекладає відомі помилки ядра, зберігаючи українські повідомлення."""
    translations = {
        "Division by zero": "Ділення на нуль неможливе",
        "Result is too large": "Результат завеликий",
        "Result is not a real number": "Результат не є дійсним числом",
        "Unbalanced brackets": "Перевірте парність дужок",
        "Incomplete expression": "Вираз неповний або некоректний",
        "Expression is empty": "Введіть вираз",
        "math domain error": "Аргумент поза областю визначення функції",
        "math range error": "Результат завеликий",
        "float division by zero": "Ділення на нуль неможливе",
        "cannot convert float infinity to integer": "Результат не є скінченним числом",
        "cannot convert float NaN to integer": "Результат не є скінченним числом",
        "0.0 cannot be raised to a negative power": "Нуль не можна піднести до від’ємного степеня",
    }
    if message in translations:
        return translations[message]
    patterns = [
        (r"Unknown name '(.*)'", "Невідома назва: {}"),
        (r"Malformed number at position (\d+)", "Некоректне число, позиція {}"),
        (r"Unexpected character '(.*)' at position (\d+)", "Неприпустимий символ '{}', позиція {}"),
    ]
    for pattern, template in patterns:
        match = re.fullmatch(pattern, message)
        if match:
            return template.format(*match.groups())
    return message


class CalculatorApp(ctk.CTk):
    """Головне вікно. store — необов’язкове сховище з методом add."""
>>>>>>> main

    def __init__(self, store=None):
        super().__init__()

        self.store = store
        self.angle_mode = DEGREES

<<<<<<< HEAD
        self.title("Smart Calculator — ІПЗ-22 Dev Team")
=======
        self.title("Науковий калькулятор — ІПЗ-22")
>>>>>>> main
        self.geometry("880x620")
        self.minsize(820, 580)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

<<<<<<< HEAD
        # One row and two columns: the calculator on the left, the side
        # panel on the right. Only the calculator column stretches.
=======
        # Калькулятор ліворуч, майбутня панель історії праворуч.
        # Ліва колонка розтягується разом із вікном.
>>>>>>> main
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self._build_calculator()
        self._build_side_panel()
        self._bind_keyboard()

<<<<<<< HEAD
    # ------------------------------------------------------------------
    # Construction of the interface
    # ------------------------------------------------------------------

    def _build_calculator(self) -> None:
        """Create the display, the mode switch and both keypads."""
=======
    # Побудова інтерфейсу
    # Побудова інтерфейсу
    # Побудова інтерфейсу

    def _build_calculator(self) -> None:
        """Створює поле виразу, перемикач кутів і кнопки."""
>>>>>>> main
        container = ctk.CTkFrame(self, corner_radius=12)
        container.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        container.grid_rowconfigure(6, weight=1)

        self.expression = ctk.StringVar(value="")
        self.display = ctk.CTkEntry(
            container,
            textvariable=self.expression,
            font=ctk.CTkFont(size=34, weight="bold"),
            justify="right",
            height=76,
            corner_radius=10,
        )
        self.display.grid(row=0, column=0, columnspan=4, sticky="ew", padx=12, pady=(14, 4))

<<<<<<< HEAD
        # A dedicated label for problems keeps error text off the display,
        # so a failed calculation never destroys what the user typed.
=======
        # Помилка показується окремо від виразу.
        # Користувач може виправити введення без повторного набору.
>>>>>>> main
        self.status = ctk.CTkLabel(
            container,
            text="",
            text_color="#ff6b6b",
            font=ctk.CTkFont(size=13),
            anchor="e",
        )
        self.status.grid(row=1, column=0, columnspan=4, sticky="ew", padx=14)

        self.angle_switch = ctk.CTkSegmentedButton(
            container,
            values=["DEG", "RAD"],
            command=self._on_angle_mode_changed,
        )
        self.angle_switch.set("DEG")
        self.angle_switch.grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(6, 10))

<<<<<<< HEAD
        # Scientific keys. Each entry is (caption, text inserted).
=======
        # Пари: напис кнопки та текст для вставлення.
>>>>>>> main
        scientific_keys = [
            ("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("√", "sqrt("),
            ("log", "log("), ("ln", "ln("), ("xʸ", "^"), ("n!", "fact("),
            ("π", "pi"), ("e", "e"), ("(", "("), (")", ")"),
        ]
        for position, (caption, inserted) in enumerate(scientific_keys):
            row = 3 + position // 4
            column = position % 4
            self._make_button(
                container, caption, lambda text=inserted: self._insert(text),
                row=row, column=column, fill=SCIENTIFIC_COLOR, hover=SCIENTIFIC_HOVER, height=40,
            )

        keypad = ctk.CTkFrame(container, fg_color="transparent")
        keypad.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=8, pady=(10, 12))
        keypad.grid_columnconfigure((0, 1, 2, 3), weight=1)
        keypad.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self._make_button(keypad, "C", self._clear, row=0, column=0,
                          fill=DANGER, hover=DANGER_HOVER)
        self._make_button(keypad, "←", self._backspace, row=0, column=1,
                          fill=SCIENTIFIC_COLOR, hover=SCIENTIFIC_HOVER)
        self._make_button(keypad, "%", lambda: self._insert("%"), row=0, column=2,
                          fill=OPERATOR_COLOR, hover=OPERATOR_HOVER)
        self._make_button(keypad, "÷", lambda: self._insert("/"), row=0, column=3,
                          fill=OPERATOR_COLOR, hover=OPERATOR_HOVER)

<<<<<<< HEAD
        # Each row pairs three digits with the operator that sits beside
        # them on a physical calculator. The tuple is (caption, inserted).
=======
        # Рядки цифрових кнопок із відповідним оператором.
        # Пари: напис кнопки та текст для вставлення.
>>>>>>> main
        digit_rows = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("×", "*")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("−", "-")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("+", "+")],
        ]
        for row_index, row_keys in enumerate(digit_rows, start=1):
            for column_index, (caption, inserted) in enumerate(row_keys):
                is_operator = column_index == 3
                self._make_button(
                    keypad, caption, lambda text=inserted: self._insert(text),
                    row=row_index, column=column_index,
                    fill=OPERATOR_COLOR if is_operator else DIGIT_COLOR,
                    hover=OPERATOR_HOVER if is_operator else DIGIT_HOVER,
                )

        self._make_button(keypad, "0", lambda: self._insert("0"), row=4, column=0, columnspan=2,
                          fill=DIGIT_COLOR, hover=DIGIT_HOVER)
        self._make_button(keypad, ".", lambda: self._insert("."), row=4, column=2,
                          fill=DIGIT_COLOR, hover=DIGIT_HOVER)
        self._make_button(keypad, "=", self._calculate, row=4, column=3,
                          fill=ACCENT, hover=ACCENT_HOVER)

    def _build_side_panel(self) -> None:
<<<<<<< HEAD
        """Create the right-hand panel with memory and calculation history."""
=======
        """Створює заглушку панелі історії для подальшої інтеграції."""
>>>>>>> main
        panel = ctk.CTkFrame(self, corner_radius=12, width=280)
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        panel.grid_propagate(False)

<<<<<<< HEAD
        self.history_panel = HistoryPanel(panel, store=self.store, on_reuse=self._use_from_history)
        self.history_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def _make_button(self, parent, caption, command, row, column,
                     columnspan=1, fill=None, hover=None, height=52):
        """Create one styled button and place it on the grid.

        Args:
            parent: the frame the button belongs to.
            caption: the text shown on the button.
            command: the callable invoked on click.
            row, column, columnspan: grid placement.
            fill: background colour, or None for the theme default.
            hover: hover colour, or None for the theme default.
            height: button height in pixels.

        Returns:
            The created ``CTkButton``.
        """
=======
        ctk.CTkLabel(
            panel, text="ІСТОРІЯ", font=ctk.CTkFont(size=12, weight="bold"), text_color=MUTED,
        ).pack(anchor="w", padx=14, pady=(14, 4))

        ctk.CTkLabel(
            panel, text="Історію буде додано окремо", text_color=MUTED, font=ctk.CTkFont(size=12),
        ).pack(padx=14, pady=10)

    def _make_button(self, parent, caption, command, row, column,
                     columnspan=1, fill=None, hover=None, height=52):
        """Створює кнопку й розміщує її в сітці.
        
        parent — контейнер; caption — напис; command — дія.
        row, column, columnspan — позиція; fill/hover — кольори; height — висота.
        Повертає створену кнопку."""
>>>>>>> main
        button = ctk.CTkButton(
            parent,
            text=caption,
            command=command,
            height=height,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=fill,
            hover_color=hover,
        )
        button.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=4, pady=4)
        return button

    def _bind_keyboard(self) -> None:
<<<<<<< HEAD
        """Allow the calculator to be driven from the keyboard."""
=======
        """Прив’язує Enter до обчислення, Escape до очищення."""
>>>>>>> main
        self.bind("<Return>", lambda event: self._calculate())
        self.bind("<KP_Enter>", lambda event: self._calculate())
        self.bind("<Escape>", lambda event: self._clear())

<<<<<<< HEAD
    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------

    def _on_angle_mode_changed(self, value: str) -> None:
        """Switch between degrees and radians for trigonometry."""
=======
    # Обробка дій користувача
    # Обробка дій користувача
    # Обробка дій користувача

    def _on_angle_mode_changed(self, value: str) -> None:
        """Перемикає тригонометрію між градусами та радіанами."""
>>>>>>> main
        self.angle_mode = DEGREES if value == "DEG" else RADIANS
        self.status.configure(text="")

    def _insert(self, text: str) -> None:
<<<<<<< HEAD
        """Append ``text`` to the expression on the display."""
=======
        """Додає текст наприкінці виразу й пересуває курсор."""
>>>>>>> main
        self.status.configure(text="")
        self.expression.set(self.expression.get() + text)
        self.display.icursor("end")

    def _clear(self) -> None:
<<<<<<< HEAD
        """Wipe the display completely."""
=======
        """Очищає вираз і повідомлення про помилку."""
>>>>>>> main
        self.expression.set("")
        self.status.configure(text="")

    def _backspace(self) -> None:
<<<<<<< HEAD
        """Delete the last character of the expression."""
=======
        """Видаляє останній символ виразу."""
>>>>>>> main
        self.status.configure(text="")
        self.expression.set(self.expression.get()[:-1])

    def _use_from_history(self, text: str) -> None:
<<<<<<< HEAD
        """Put a value taken from the history or memory on the display."""
=======
        """Показує значення, взяте з історії або пам’яті."""
>>>>>>> main
        self.status.configure(text="")
        self.expression.set(text)
        self.display.icursor("end")

    def _calculate(self) -> None:
<<<<<<< HEAD
        """Evaluate the current expression and show the result.

        On success the expression is replaced by its result and the pair is
        written to the history store. On failure the expression is left
        untouched so it can be corrected, and the reason is shown below the
        display.
        """
=======
        """Обчислює вираз. При помилці зберігає введення та показує пояснення."""
>>>>>>> main
        expression = self.expression.get().strip()
        if not expression:
            return

        try:
            functions = build_functions(self.angle_mode)
            value = evaluate(expression, functions=functions, constants=CONSTANTS)
<<<<<<< HEAD
        except EvaluationError as error:
            self.status.configure(text=str(error))
            return

        result = format_result(value)
=======
            # Нескінченність не можна коректно показати як звичайне число.
            if not math.isfinite(value):
                raise EvaluationError("Результат не є скінченним числом")
            result = format_result(value)
        except (EvaluationError, ValueError, OverflowError) as error:
            self.status.configure(text=_error_message(str(error)))
            return
>>>>>>> main
        self.expression.set(result)
        self.status.configure(text="")

        if self.store is not None:
            self.store.add(expression, result)
<<<<<<< HEAD
            self.history_panel.refresh()
=======
>>>>>>> main
