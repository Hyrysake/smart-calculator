<<<<<<< HEAD
"""Entry point of Smart Calculator.

Run with::

    python main.py

Author: Махнюк Андрій (Developer); history wiring added by
Бардюк Станіслав Олександрович (QA).
"""

from core.history import HistoryStore
=======
"""Точка входу калькулятора. Запуск: python main.py.

Частина Developer: Махнюк Андрій Сергійович, ІПЗ-22.
"""

>>>>>>> main
from ui.app import CalculatorApp


def main() -> None:
<<<<<<< HEAD
    """Create the history store, open the window and run the event loop."""
    store = HistoryStore()
    app = CalculatorApp(store=store)
=======
    """Створює вікно й запускає цикл обробки подій."""
    app = CalculatorApp()
>>>>>>> main
    app.mainloop()


if __name__ == "__main__":
    main()
