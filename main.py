"""Entry point of Smart Calculator.

Run with::

    python main.py

Author: Махнюк Андрій (Developer); history wiring added by
Бардюк Станіслав Олександрович (QA).
"""

from core.history import HistoryStore
from ui.app import CalculatorApp


def main() -> None:
    """Create the history store, open the window and run the event loop."""
    store = HistoryStore()
    app = CalculatorApp(store=store)
    app.mainloop()


if name == "main":
    main()