"""Tests for the calculation history and the calculator memory.

Every test uses pytest's ``tmp_path`` fixture, so the real history file in
the home directory is never touched.

Author: Бардюк Станіслав Олександрович (QA)
"""

import json

from core.history import HistoryStore, Memory


def make_store(tmp_path, max_entries=50) -> HistoryStore:
    """Create a store backed by a throwaway file inside ``tmp_path``."""
    return HistoryStore(path=tmp_path / "history.json", max_entries=max_entries)


class TestHistoryStore:
    """Adding, reading, clearing and persisting records."""

    def test_new_store_is_empty(self, tmp_path):
        assert make_store(tmp_path).items() == []

    def test_add_stores_the_record(self, tmp_path):
        store = make_store(tmp_path)
        store.add("2+2", "4")

        entries = store.items()
        assert len(entries) == 1
        assert entries[0]["expression"] == "2+2"
        assert entries[0]["result"] == "4"

    def test_newest_record_comes_first(self, tmp_path):
        store = make_store(tmp_path)
        store.add("1+1", "2")
        store.add("2+2", "4")

        assert store.items()[0]["expression"] == "2+2"

    def test_clear_removes_everything(self, tmp_path):
        store = make_store(tmp_path)
        store.add("2+2", "4")
        store.clear()

        assert store.items() == []

    def test_oldest_records_are_dropped_past_the_limit(self, tmp_path):
        store = make_store(tmp_path, max_entries=3)
        for number in range(5):
            store.add(f"{number}+0", str(number))

        entries = store.items()
        assert len(entries) == 3
        # 0 and 1 were pushed out; 4 is the newest.
        assert entries[0]["result"] == "4"
        assert entries[-1]["result"] == "2"

    def test_history_survives_a_restart(self, tmp_path):
        first = make_store(tmp_path)
        first.add("7*6", "42")

        second = HistoryStore(path=tmp_path / "history.json")
        assert second.items()[0]["result"] == "42"

    def test_file_is_valid_json(self, tmp_path):
        store = make_store(tmp_path)
        store.add("2+2", "4")

        data = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
        assert data == [{"expression": "2+2", "result": "4"}]

    def test_damaged_file_does_not_crash(self, tmp_path):
        broken = tmp_path / "history.json"
        broken.write_text("this is not json at all", encoding="utf-8")

        assert HistoryStore(path=broken).items() == []

    def test_records_of_the_wrong_shape_are_ignored(self, tmp_path):
        path = tmp_path / "history.json"
        path.write_text(json.dumps([{"expression": "2+2", "result": "4"}, {"junk": 1}, 5]),
                        encoding="utf-8")

        assert len(HistoryStore(path=path).items()) == 1

    def test_items_returns_a_copy(self, tmp_path):
        store = make_store(tmp_path)
        store.add("2+2", "4")

        store.items().clear()
        assert len(store.items()) == 1


class TestMemory:
    """The M+ / MR / MC behaviour."""

    def test_starts_empty(self):
        memory = Memory()
        assert memory.recall() == 0
        assert memory.is_empty()

    def test_add_accumulates(self):
        memory = Memory()
        memory.add(5)
        memory.add(2.5)

        assert memory.recall() == 7.5
        assert not memory.is_empty()

    def test_add_returns_the_new_value(self):
        assert Memory().add(3) == 3

    def test_recall_does_not_change_the_value(self):
        memory = Memory()
        memory.add(9)
        memory.recall()

        assert memory.recall() == 9

    def test_clear_resets_to_zero(self):
        memory = Memory()
        memory.add(9)
        memory.clear()

        assert memory.recall() == 0
        assert memory.is_empty()
