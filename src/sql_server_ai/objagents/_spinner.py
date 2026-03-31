"""Shared terminal spinner for displaying active agent progress.

A single module-level instance (``spinner``) is imported by both
``main.py`` (top-level agent events) and ``pillar_callbacks.py``
(sub-agent callbacks) so that all activity writes to one consistent
spinner line rather than flooding the terminal with verbose output.
"""

import sys
import threading
import itertools
import time as _time

_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


class AgentSpinner:
    """Thread-based spinner that shows the currently active agent name."""

    def __init__(self):
        self._cycle = itertools.cycle(_FRAMES)
        self._running = False
        self._label = ""
        self._thread = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, label: str) -> None:
        """Start spinning with *label*. No-op if already running."""
        with self._lock:
            self._label = label
            if self._running:
                return
            self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def set_label(self, label: str) -> None:
        """Update the displayed label without restarting the thread."""
        with self._lock:
            self._label = label

    def println(self, text: str) -> None:
        """Clear the spinner line, print *text*, then let the spinner resume."""
        with self._lock:
            sys.stdout.write(f"\r\033[K{text}\n")
            sys.stdout.flush()

    def stop(self) -> None:
        """Stop the spinner and clear the spinner line."""
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._running

    @property
    def label(self) -> str:
        with self._lock:
            return self._label

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    break
                label = self._label
                frame = next(self._cycle)
                sys.stdout.write(f"\r\033[K\033[1;33m{frame} {label}\033[0m")
                sys.stdout.flush()
            _time.sleep(0.1)


# Module-level singleton — import this instance everywhere.
spinner = AgentSpinner()


class CornerStatus:
    """Displays warm-up progress in the terminal window title bar.

    Writing to the title bar via OSC escape sequences (\033]0;...\007) is
    completely non-intrusive — it never touches terminal content or cursor
    position, so it cannot interfere with prompt_toolkit's input handling.
    """

    def __init__(self):
        self._running = False
        self._label = ""
        self._thread = None
        self._lock = threading.Lock()
        self._cycle = itertools.cycle(_FRAMES)

    def start(self, label: str) -> None:
        """Start the title-bar spinner with *label*. No-op if already running."""
        with self._lock:
            self._label = label
            if self._running:
                return
            self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def set_label(self, label: str) -> None:
        """Update the displayed label without restarting the thread."""
        with self._lock:
            self._label = label

    def stop(self, final_message: str = "") -> None:
        """Stop the spinner. Optionally flash *final_message* in the title."""
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        if final_message:
            self._set_title(final_message)
        else:
            self._set_title("ZeusAI")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _set_title(self, text: str) -> None:
        sys.stdout.write(f"\033]0;{text}\007")
        sys.stdout.flush()

    def _run(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    break
                frame = next(self._cycle)
                label = self._label
            self._set_title(f"{frame} {label}")
            _time.sleep(0.1)


corner_status = CornerStatus()
