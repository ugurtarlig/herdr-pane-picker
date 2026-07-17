#!/usr/bin/env python3
"""Render one static fictional pane for the documentation capture.

The pane ends on any keypress, on stdin EOF, and on SIGINT/SIGTERM/SIGHUP, so
demo panes never trap the user inside a layout they cannot close.
"""

from __future__ import annotations

import os
import select
import signal
import sys
import termios
import tty


SCREENS = {
    "editor": (
        "EDITOR  src/search.py",
        [
            "",
            "  12  async def build_index(source):",
            "  13      docs = await source.read()",
            "  14      return index_documents(docs)",
            "  18  results = await index.search(query)",
        ],
        "\x1b[38;5;117m",
    ),
    "tests": (
        "TESTS  python -m unittest",
        [
            "",
            "  test_build_index ............. ok",
            "  test_empty_query ............. ok",
            "  test_ranked_results .......... ok",
            "",
            "  Ran 42 tests in 1.28s",
            "  OK",
        ],
        "\x1b[38;5;150m",
    ),
    "logs": (
        "LOGS  development server",
        [
            "",
            "  12:41:03  index loaded: 128 docs",
            "  12:41:04  watcher ready",
            "  12:41:11  GET /health      200",
            "  12:41:16  POST /search     200",
        ],
        "\x1b[38;5;215m",
    ),
    "shell": (
        "SHELL  atlas-search",
        [
            "",
            "  demo@herdr ~/projects/atlas-search",
            "  $ git status --short",
            "   M src/search.py",
            "   M tests/test_search.py",
            "  $ _",
        ],
        "\x1b[38;5;183m",
    ),
}


def raise_system_exit(*_: object) -> None:
    raise SystemExit


def wait_for_exit() -> None:
    """Block until any keypress, stdin EOF, or a termination signal.

    A wakeup pipe closes the race where a signal lands after the interpreter's
    last signal check but before read() blocks, which would otherwise leave the
    pane alive until the next keypress.
    """
    fd = sys.stdin.fileno()
    saved = None
    try:
        saved = termios.tcgetattr(fd)
        tty.setcbreak(fd)
    except (termios.error, OSError, ValueError):
        saved = None
    wake_r, wake_w = os.pipe()
    os.set_blocking(wake_w, False)
    previous_wakeup = signal.set_wakeup_fd(wake_w)
    try:
        ready, _, _ = select.select([fd, wake_r], [], [])
        if fd in ready:
            # One byte on any keypress, b"" on EOF; both end the pane.
            os.read(fd, 1)
    except OSError:
        pass
    finally:
        signal.set_wakeup_fd(previous_wakeup)
        os.close(wake_r)
        os.close(wake_w)
        if saved is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, saved)


def main() -> int:
    role = sys.argv[1] if len(sys.argv) > 1 else "shell"
    title, lines, accent = SCREENS.get(role, SCREENS["shell"])
    sys.stdout.write("\x1b[2J\x1b[H\x1b[?25l")
    sys.stdout.write(f"{accent}\x1b[1m  {title}\x1b[0m\n")
    sys.stdout.write("\x1b[38;5;240m  " + "─" * 48 + "\x1b[0m\n")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()

    signal.signal(signal.SIGTERM, raise_system_exit)
    signal.signal(signal.SIGHUP, raise_system_exit)
    try:
        wait_for_exit()
    except (KeyboardInterrupt, SystemExit):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
