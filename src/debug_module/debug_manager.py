"""Unified debug management for MatterCraft."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import tkinter as tk
from tkinter import ttk


DEBUG_LEVEL_ORDER: dict[str, int] = {
    "debug": 10,
    "info": 20,
    "warning": 30,
    "error": 40,
}


@dataclass(slots=True)
class DebugEvent:
    """
    Function:
        Represent one structured debug event inside the unified debug module.
    Args:
        timestamp: UTC timestamp in ISO-8601 format.
        level: Log level name.
        module: Source module name.
        message: Human-readable log message.
        context: Optional structured context payload.
    Implementation Logic:
        The debug module keeps every event in one normalized dataclass so that
        memory buffering, filtering and window rendering all work on the same
        shape.
    """

    timestamp: str
    level: str
    module: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


class TkDebugWindowAdapter:
    """
    Function:
        Render the MatterCraft debug window with a Tkinter toplevel window.
    Args:
        None.
    Implementation Logic:
        Tkinter is available in the standard library, so this adapter gives the
        project a zero-dependency debug window while keeping window ownership in
        the debug module as required by the docs.
    """

    def __init__(self) -> None:
        """
        Function:
            Initialize the debug window adapter state.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Window widgets are created lazily after a root window is supplied so
            the debug module can stay inactive when debug mode is off.
        """

        self._root: tk.Misc | None = None
        self._window: tk.Toplevel | None = None
        self._manager: DebugManager | None = None
        self._minimum_level = tk.StringVar(value="debug")
        self._module_filter = tk.StringVar(value="")
        self._log_text: tk.Text | None = None
        self._state_text: tk.Text | None = None
        self._error_text: tk.Text | None = None

    def attach(self, root: tk.Misc, manager: "DebugManager") -> None:
        """
        Function:
            Attach the debug window to the main UI loop.
        Args:
            root: Main Tk root or another Tk widget owning the event loop.
            manager: Shared debug manager instance.
        Returns:
            None.
        Implementation Logic:
            The adapter creates one toplevel window and schedules periodic UI
            refreshes via Tk's event loop so the rest of the project does not
            manipulate debug widgets directly.
        """

        self._root = root
        self._manager = manager
        self._ensure_window()
        self._schedule_refresh()

    def close(self) -> None:
        """
        Function:
            Close the debug window if it is open.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The adapter owns the toplevel window lifecycle, matching the
            documentation rule that other modules must not control debug layout.
        """

        if self._window is not None and self._window.winfo_exists():
            self._window.destroy()
        self._window = None

    def _ensure_window(self) -> None:
        """
        Function:
            Create the Tk widgets for the debug window if needed.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Widget creation is isolated here so repeated attach calls remain
            idempotent and the rest of the adapter can assume widgets exist.
        """

        if self._root is None:
            return
        if self._window is not None and self._window.winfo_exists():
            return

        self._window = tk.Toplevel(self._root)
        self._window.title("MatterCraft Debug")
        self._window.geometry("980x680")

        container = ttk.Frame(self._window, padding=8)
        container.pack(fill=tk.BOTH, expand=True)

        filter_row = ttk.Frame(container)
        filter_row.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_row, text="Min Level").pack(side=tk.LEFT)
        ttk.OptionMenu(
            filter_row,
            self._minimum_level,
            self._minimum_level.get(),
            *DEBUG_LEVEL_ORDER.keys(),
        ).pack(side=tk.LEFT, padx=(8, 16))

        ttk.Label(filter_row, text="Module Filter").pack(side=tk.LEFT)
        ttk.Entry(filter_row, textvariable=self._module_filter, width=30).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        content = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(content)
        right_panel = ttk.Frame(content)
        content.add(left_panel, weight=3)
        content.add(right_panel, weight=2)

        ttk.Label(left_panel, text="Logs").pack(anchor=tk.W)
        self._log_text = tk.Text(left_panel, wrap=tk.NONE, font=("Consolas", 10))
        self._log_text.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right_panel, text="Runtime State").pack(anchor=tk.W)
        self._state_text = tk.Text(right_panel, height=16, font=("Consolas", 10))
        self._state_text.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        ttk.Label(right_panel, text="Errors").pack(anchor=tk.W)
        self._error_text = tk.Text(right_panel, height=12, font=("Consolas", 10))
        self._error_text.pack(fill=tk.BOTH, expand=True)

        self._window.protocol("WM_DELETE_WINDOW", self.close)

    def _schedule_refresh(self) -> None:
        """
        Function:
            Schedule the next refresh tick for the debug window.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Periodic polling keeps the adapter simple and robust while still
            giving the user a live debug surface.
        """

        if self._root is None:
            return
        self._render()
        self._root.after(250, self._schedule_refresh)

    def _render(self) -> None:
        """
        Function:
            Repaint the debug window using the current manager state.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The adapter requests filtered events and runtime state from the
            manager, then replaces widget contents atomically for readability.
        """

        if self._manager is None:
            return
        if self._window is None or not self._window.winfo_exists():
            return
        if self._log_text is None or self._state_text is None or self._error_text is None:
            return

        minimum_level = self._minimum_level.get()
        module_filter = self._module_filter.get().strip()
        events = self._manager.get_events(
            minimum_level=minimum_level,
            module_filter=module_filter,
        )
        errors = [event for event in events if event.level == "error"]

        self._replace_text(
            self._log_text,
            "\n".join(self._format_event(event) for event in events[-200:]),
        )
        self._replace_text(
            self._state_text,
            self._manager.format_runtime_state(),
        )
        self._replace_text(
            self._error_text,
            "\n".join(self._format_event(event) for event in errors[-50:]),
        )

    @staticmethod
    def _replace_text(widget: tk.Text, content: str) -> None:
        """
        Function:
            Replace the full content of a Tk text widget.
        Args:
            widget: Target text widget.
            content: New text content.
        Returns:
            None.
        Implementation Logic:
            Full replacement keeps the view deterministic and avoids partial
            update complexity in the first implementation.
        """

        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)

    @staticmethod
    def _format_event(event: DebugEvent) -> str:
        """
        Function:
            Format one debug event as a single-line display string.
        Args:
            event: Event to format.
        Returns:
            str: Human-readable event line.
        Implementation Logic:
            The formatter keeps timestamps, levels and module names aligned so
            the debug window remains scannable during active development.
        """

        context_suffix = ""
        if event.context:
            context_suffix = f" | context={event.context}"
        return f"[{event.timestamp}] {event.level.upper():7s} {event.module}: {event.message}{context_suffix}"


class DebugManager:
    """
    Function:
        Manage structured debug events, runtime state and the optional debug window.
    Args:
        None.
    Implementation Logic:
        This class is the only owner of debug buffering, filtering and UI
        presentation so that business modules can submit logs through one stable
        interface.
    """

    def __init__(self, capacity: int = 1000) -> None:
        """
        Function:
            Initialize the shared debug manager.
        Args:
            capacity: Maximum number of in-memory events to retain.
        Returns:
            None.
        Implementation Logic:
            The manager keeps a bounded list of recent events so long-running
            sessions do not grow without limit.
        """

        self._capacity = capacity
        self._enabled = False
        self._events: list[DebugEvent] = []
        self._runtime_state: dict[str, Any] = {}
        self._window_adapter: TkDebugWindowAdapter | None = None

    def configure(self, enable_window: bool = False, root: tk.Misc | None = None) -> None:
        """
        Function:
            Configure debug behavior for the current application session.
        Args:
            enable_window: Whether the debug window should be opened.
            root: Tk root used to host the optional debug window.
        Returns:
            None.
        Implementation Logic:
            Debug logging always remains callable, while the actual window is
            only attached when debug mode is enabled and a UI root exists.
        """

        self._enabled = enable_window
        if enable_window and root is not None:
            self._window_adapter = TkDebugWindowAdapter()
            self._window_adapter.attach(root=root, manager=self)
            self.log(level="info", module="debug", message="Debug window attached.")

    def log(
        self,
        level: str,
        module: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> DebugEvent:
        """
        Function:
            Record one debug event.
        Args:
            level: Log level name.
            module: Source module name.
            message: Human-readable log message.
            context: Optional structured context payload.
        Returns:
            DebugEvent: Newly recorded event.
        Implementation Logic:
            All modules submit debug information here so the project avoids
            scattered print statements and keeps one canonical debug pipeline.
        """

        normalized_level = level.lower()
        if normalized_level not in DEBUG_LEVEL_ORDER:
            raise ValueError(f"Unsupported debug level: {level}")

        event = DebugEvent(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            level=normalized_level,
            module=module,
            message=message,
            context=context or {},
        )
        self._events.append(event)
        if len(self._events) > self._capacity:
            self._events = self._events[-self._capacity :]
        return event

    def get_events(
        self,
        minimum_level: str = "debug",
        module_filter: str = "",
    ) -> list[DebugEvent]:
        """
        Function:
            Return recent debug events with optional filtering.
        Args:
            minimum_level: Lowest level to include.
            module_filter: Optional substring filter on module name.
        Returns:
            list[DebugEvent]: Filtered event list.
        Implementation Logic:
            Filtering lives in the manager so the window and future consumers use
            the same event selection rules.
        """

        threshold = DEBUG_LEVEL_ORDER[minimum_level.lower()]
        normalized_module_filter = module_filter.lower()
        return [
            event
            for event in self._events
            if DEBUG_LEVEL_ORDER[event.level] >= threshold
            and normalized_module_filter in event.module.lower()
        ]

    def set_runtime_state(self, key: str, value: Any) -> None:
        """
        Function:
            Update one runtime state entry displayed in the debug window.
        Args:
            key: Stable runtime state key.
            value: Runtime value to store.
        Returns:
            None.
        Implementation Logic:
            Runtime state is kept separate from logs so high-frequency status
            changes do not flood the event list.
        """

        self._runtime_state[key] = value

    def update_runtime_state(self, values: dict[str, Any]) -> None:
        """
        Function:
            Merge a batch of runtime state values into the debug state map.
        Args:
            values: State entries to merge.
        Returns:
            None.
        Implementation Logic:
            Batch updates keep call sites concise when a module publishes
            several related debug metrics together.
        """

        self._runtime_state.update(values)

    def format_runtime_state(self) -> str:
        """
        Function:
            Format runtime state into a human-readable multiline string.
        Args:
            None.
        Returns:
            str: Formatted runtime state.
        Implementation Logic:
            The state formatter uses deterministic key ordering to keep the
            debug panel stable between refreshes.
        """

        if not self._runtime_state:
            return "No runtime state."
        lines: list[str] = []
        for key in sorted(self._runtime_state.keys()):
            value = self._runtime_state[key]
            if hasattr(value, "__dataclass_fields__"):
                value = asdict(value)
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

    @property
    def enabled(self) -> bool:
        """
        Function:
            Expose whether the debug window mode is enabled.
        Args:
            None.
        Returns:
            bool: Current debug mode flag.
        Implementation Logic:
            Business modules sometimes need to publish richer runtime state only
            when debug mode is active.
        """

        return self._enabled


DEBUG_MANAGER = DebugManager()


def log(
    level: str,
    module: str,
    message: str,
    context: dict[str, Any] | None = None,
) -> DebugEvent:
    """
    Function:
        Proxy module-level debug logging to the shared debug manager.
    Args:
        level: Log level name.
        module: Source module name.
        message: Human-readable log message.
        context: Optional structured context payload.
    Returns:
        DebugEvent: Newly created debug event.
    Implementation Logic:
        A lightweight proxy keeps call sites short while still enforcing the
        unified debug module rule from the documentation.
    """

    return DEBUG_MANAGER.log(level=level, module=module, message=message, context=context)
