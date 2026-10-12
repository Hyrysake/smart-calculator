"""Calculation history and calculator memory.

Two small classes live here. :class:`HistoryStore` remembers what was
calculated and survives a restart by writing itself to a JSON file, and
:class:`Memory` implements the classic M+ / MR / MC keys.

Author: Бардюк Станіслав Олександрович (QA)
"""

import json
from pathlib import Path

# Where the history file is kept when no other path is given. Putting it in
# the user's home directory means the program never writes inside its own
# folder, so nothing accidental ends up in the repository.
DEFAULT_PATH = Path.home() / ".smart_calculator_history.json"

# Older entries are dropped once this many are stored.
MAX_ENTRIES = 50


class HistoryStore:
    """A list of past calculations backed by a JSON file.

    Args:
        path: file to load from and save to. Defaults to
            ``~/.smart_calculator_history.json``.
        max_entries: how many records to keep before discarding the oldest.
    """

    def __init__(self, path: Path | None = None, max_entries: int = MAX_ENTRIES):
        self.path = Path(path) if path is not None else DEFAULT_PATH
        self.max_entries = max_entries
        self._entries: list[dict] = []
        self.load()

    def add(self, expression: str, result: str) -> None:
        """Remember one calculation and save the history to disk.

        Args:
            expression: what the user typed, e.g. ``"2+2"``.
            result: what the calculator answered, e.g. ``"4"``.
        """
        self._entries.append({"expression": expression, "result": result})

        # Keep only the newest records so the file cannot grow without end.
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]

        self.save()

    def items(self) -> list[dict]:
        """Return the history, newest first.

        Returns:
            A new list of dictionaries with ``expression`` and ``result``
            keys. A copy is returned so callers cannot modify the store by
            accident.
        """
        return list(reversed(self._entries))

    def clear(self) -> None:
        """Forget everything and update the file on disk."""
        self._entries = []
        self.save()

    def load(self) -> None:
        """Read the history file if it exists.

        A missing, empty or damaged file is not an error: the calculator
        simply starts with an empty history instead of refusing to open.
        """
        if not self.path.exists():
            self._entries = []
            return

        try:
            text = self.path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (OSError, json.JSONDecodeError):
            self._entries = []
            return

        if isinstance(data, list):
            # Ignore anything in the file that is not shaped like a record.
            self._entries = [
                entry for entry in data
                if isinstance(entry, dict) and "expression" in entry and "result" in entry
            ]
        else:
            self._entries = []

    def save(self) -> None:
        """Write the history to disk, ignoring a read-only filesystem."""
        try:
            self.path.write_text(
                json.dumps(self._entries, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            # Losing the history file must never crash the calculator.
            pass


class Memory:
    """The M+ / MR / MC keys of a pocket calculator.

    The stored value lives only while the program is running, exactly as it
    does on a physical calculator.
    """

    def __init__(self):
        self._value = 0.0

    @property
    def value(self) -> float:
        """The number currently held in memory."""
        return self._value

    def add(self, number: float) -> float:
        """Add ``number`` to the stored value (the M+ key).

        Args:
            number: the value to accumulate.

        Returns:
            The new contents of memory.
        """
        self._value += float(number)
        return self._value

    def recall(self) -> float:
        """Return the stored value without changing it (the MR key)."""
        return self._value

    def clear(self) -> None:
        """Reset the stored value to zero (the MC key)."""
        self._value = 0.0

    def is_empty(self) -> bool:
        """Report whether memory holds nothing."""
        return self._value == 0.0
