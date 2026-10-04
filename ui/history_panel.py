"""Side panel widget: calculator memory and calculation history.

The panel knows nothing about how a calculation is performed. It only
displays what the store gives it and calls back into the main window when
the user wants to reuse a value.

Author: Бардюк Станіслав Олександрович (QA)
"""

import customtkinter as ctk

from core.evaluator import format_result
from core.history import Memory

MUTED = "#8b93a7"
CARD = "#2b303b"
CARD_HOVER = "#353b49"


class HistoryPanel(ctk.CTkFrame):
    """Memory buttons plus a scrollable list of past calculations.

    Args:
        parent: the widget this panel is placed in.
        store: a :class:`core.history.HistoryStore`, or None to show an
            empty, disabled panel.
        on_reuse: callable invoked with a string when the user clicks a
            history record or recalls memory.
    """

    def __init__(self, parent, store=None, on_reuse=None):
        super().__init__(parent, fg_color="transparent")

        self.store = store
        self.on_reuse = on_reuse
        self.memory = Memory()

        self._build_memory_section()
        self._build_history_section()
        self.refresh()

    def _build_memory_section(self) -> None:
        """Create the memory readout and the M+ / MR / MC buttons."""
        ctk.CTkLabel(
            self, text="MEMORY", font=ctk.CTkFont(size=12, weight="bold"), text_color=MUTED,
        ).pack(anchor="w", pady=(0, 4))

        self.memory_label = ctk.CTkLabel(
            self, text="0", font=ctk.CTkFont(size=20, weight="bold"), anchor="e",
        )
        self.memory_label.pack(fill="x", pady=(0, 6))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", pady=(0, 12))
        buttons.grid_columnconfigure((0, 1, 2), weight=1)

        for column, (caption, handler) in enumerate(
            [("M+", self._memory_add), ("MR", self._memory_recall), ("MC", self._memory_clear)]
        ):
            ctk.CTkButton(
                buttons, text=caption, command=handler, height=34, corner_radius=8,
                fg_color=CARD, hover_color=CARD_HOVER,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(row=0, column=column, sticky="ew", padx=3)

    def _build_history_section(self) -> None:
        """Create the history heading, the scrollable list and Clear."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text="HISTORY", font=ctk.CTkFont(size=12, weight="bold"), text_color=MUTED,
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Clear", command=self._clear_history, width=60, height=26,
            corner_radius=8, fg_color=CARD, hover_color=CARD_HOVER,
            font=ctk.CTkFont(size=12),
        ).pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=(6, 0))

    def refresh(self) -> None:
        """Redraw the history list from the store.

        Called once at start-up and again after every calculation.
        """
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        entries = self.store.items() if self.store is not None else []

        if not entries:
            ctk.CTkLabel(
                self.list_frame, text="No calculations yet",
                text_color=MUTED, font=ctk.CTkFont(size=12),
            ).pack(pady=12)
            return

        for entry in entries:
            self._add_entry_widget(entry["expression"], entry["result"])

    def _add_entry_widget(self, expression: str, result: str) -> None:
        """Render one history record as a clickable card."""
        card = ctk.CTkButton(
            self.list_frame,
            text=f"{expression}\n= {result}",
            command=lambda value=result: self._reuse(value),
            anchor="e",
            height=48,
            corner_radius=8,
            fg_color=CARD,
            hover_color=CARD_HOVER,
            font=ctk.CTkFont(size=13),
        )
        card.pack(fill="x", pady=3)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _reuse(self, value: str) -> None:
        """Send a stored value back to the display."""
        if self.on_reuse is not None:
            self.on_reuse(value)

    def _memory_add(self) -> None:
        """Add the newest result to memory (M+)."""
        entries = self.store.items() if self.store is not None else []
        if not entries:
            return

        try:
            self.memory.add(float(entries[0]["result"]))
        except ValueError:
            # The last result was not a plain number, so there is nothing
            # sensible to accumulate.
            return

        self._update_memory_label()

    def _memory_recall(self) -> None:
        """Put the stored value on the display (MR)."""
        self._reuse(format_result(self.memory.recall()))

    def _memory_clear(self) -> None:
        """Empty the memory (MC)."""
        self.memory.clear()
        self._update_memory_label()

    def _clear_history(self) -> None:
        """Delete every history record."""
        if self.store is not None:
            self.store.clear()
        self.refresh()

    def _update_memory_label(self) -> None:
        """Show the current memory contents above the memory buttons."""
        self.memory_label.configure(text=format_result(self.memory.value))
