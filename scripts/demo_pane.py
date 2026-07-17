#!/usr/bin/env python3
"""Render one static fictional pane for the documentation capture."""

from __future__ import annotations

import signal
import sys
import time


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


def main() -> int:
    role = sys.argv[1] if len(sys.argv) > 1 else "shell"
    title, lines, accent = SCREENS.get(role, SCREENS["shell"])
    sys.stdout.write("\x1b[2J\x1b[H\x1b[?25l")
    sys.stdout.write(f"{accent}\x1b[1m  {title}\x1b[0m\n")
    sys.stdout.write("\x1b[38;5;240m  " + "─" * 48 + "\x1b[0m\n")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()

    signal.signal(signal.SIGTERM, lambda *_: raise_system_exit())
    try:
        while True:
            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        return 0


def raise_system_exit() -> None:
    raise SystemExit


if __name__ == "__main__":
    raise SystemExit(main())
