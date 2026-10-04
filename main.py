"""Точка входу калькулятора. Запуск: python main.py.

Частина Developer: Махнюк Андрій Сергійович, ІПЗ-22.
"""

from ui.app import CalculatorApp


def main() -> None:
    """Створює вікно й запускає цикл обробки подій."""
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
