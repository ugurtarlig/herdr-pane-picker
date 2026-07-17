#!/usr/bin/env python3
"""Replace the active tab in an isolated Herdr session with fictional panes."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pane_picker", ROOT / "pane_picker.py")
assert SPEC is not None and SPEC.loader is not None
pane_picker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pane_picker)


def demo_pane(role: str, label: str) -> dict:
    return {
        "type": "pane",
        "label": label,
        "cwd": str(ROOT),
        "command": [sys.executable, str(ROOT / "scripts" / "demo_pane.py"), role],
    }


def main() -> int:
    layout = pane_picker.api_request("pane.layout", {}).get("layout")
    if not isinstance(layout, dict):
        raise RuntimeError("Herdr did not return an active layout")
    pane_picker.api_request(
        "layout.apply",
        {
            "tab_id": layout.get("tab_id"),
            "tab_label": "pane-picker-demo",
            "focus": True,
            "root": {
                "type": "split",
                "direction": "down",
                "ratio": 0.5,
                "first": {
                    "type": "split",
                    "direction": "right",
                    "ratio": 0.5,
                    "first": demo_pane("editor", "editor"),
                    "second": demo_pane("tests", "tests"),
                },
                "second": {
                    "type": "split",
                    "direction": "right",
                    "ratio": 0.5,
                    "first": demo_pane("logs", "logs"),
                    "second": demo_pane("shell", "shell"),
                },
            },
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
