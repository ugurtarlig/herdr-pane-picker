#!/usr/bin/env python3
"""Create a fictional demo tab in an isolated Herdr session.

The demo builds its panes in a NEW tab labeled ``pane-picker-demo`` and never
replaces an existing layout, so closing demo panes cannot destroy real work.
It refuses to run against the default session unless ``--force`` is given,
because documentation captures must not include personal tabs or pane content.

Usage:
    HERDR_SESSION=pane-picker-demo python3 scripts/demo_layout.py
    HERDR_SESSION=pane-picker-demo python3 scripts/demo_layout.py --close
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys


# Herdr exports HERDR_SOCKET_PATH into every pane, and the plugin prefers it
# over HERDR_SESSION. Run from inside a Herdr pane, that inherited value would
# silently redirect the demo to the LIVE session — the exact failure that once
# destroyed a real workspace. An explicit HERDR_SESSION must win here.
if os.environ.get("HERDR_SESSION"):
    os.environ.pop("HERDR_SOCKET_PATH", None)

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pane_picker", ROOT / "pane_picker.py")
assert SPEC is not None and SPEC.loader is not None
pane_picker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pane_picker)

DEMO_TAB_LABEL = "pane-picker-demo"


def demo_pane(role: str, label: str) -> dict:
    return {
        "type": "pane",
        "label": label,
        "cwd": str(ROOT),
        "command": [sys.executable, str(ROOT / "scripts" / "demo_pane.py"), role],
    }


def target_is_isolated() -> bool:
    if os.environ.get("HERDR_SOCKET_PATH"):
        return True
    session = os.environ.get("HERDR_SESSION")
    return bool(session) and session != "default"


def close_demo_tabs() -> int:
    tabs = pane_picker.api_request("tab.list", {}).get("tabs", [])
    demo_tabs = [tab for tab in tabs if tab.get("label") == DEMO_TAB_LABEL]
    for tab in demo_tabs:
        workspace_id = tab.get("workspace_id")
        siblings = [t for t in tabs if t.get("workspace_id") == workspace_id]
        if len(siblings) == 1:
            # Closing the last tab of a workspace is rejected; close the
            # workspace instead (a fresh capture session has only this one).
            pane_picker.api_request(
                "workspace.close", {"workspace_id": workspace_id}
            )
        else:
            pane_picker.api_request("tab.close", {"tab_id": tab["tab_id"]})
    print(f"closed {len(demo_tabs)} demo tab(s)")
    return 0


START_HINT = (
    "Start a fresh isolated session first, then rerun with HERDR_SESSION set:\n"
    "\n"
    "    herdr --session pane-picker-demo\n"
    "    HERDR_SESSION=pane-picker-demo python3 scripts/demo_layout.py\n"
)


def refuse(reason: str) -> int:
    sys.stderr.write(
        f"{reason}\n{START_HINT}\n"
        "Use --force only if you really want a demo tab in your live session.\n"
    )
    return 2


def main(argv: list) -> int:
    try:
        tabs = pane_picker.api_request("tab.list", {}).get("tabs", [])
    except RuntimeError:
        session = os.environ.get("HERDR_SESSION") or "default"
        sys.stderr.write(
            f"no running Herdr server for session '{session}'.\n{START_HINT}"
        )
        return 1

    if "--close" in argv:
        return close_demo_tabs()

    if "--force" not in argv:
        if not target_is_isolated():
            return refuse("refusing to run against the default Herdr session.")
        # A freshly started session has a single tab with a single shell pane.
        # More than that means the session holds real work, and documentation
        # captures must never include personal tabs or pane content.
        if len(tabs) > 1 or any(tab.get("pane_count", 0) > 1 for tab in tabs):
            session = os.environ.get("HERDR_SESSION") or "default"
            return refuse(
                f"session '{session}' already holds {len(tabs)} tab(s) — "
                "it does not look like a fresh capture session."
            )

    try:
        created = pane_picker.api_request(
            "tab.create", {"label": DEMO_TAB_LABEL, "focus": True}
        )
    except pane_picker.HerdrApiError:
        # A fresh headless session has no active workspace yet; creating one
        # yields the workspace together with its first tab.
        created = pane_picker.api_request(
            "workspace.create", {"label": DEMO_TAB_LABEL, "focus": True}
        )
        pane_picker.api_request(
            "tab.rename",
            {"tab_id": created["tab"]["tab_id"], "label": DEMO_TAB_LABEL},
        )
    tab_id = created["tab"]["tab_id"]
    pane_picker.api_request(
        "layout.apply",
        {
            "tab_id": tab_id,
            "tab_label": DEMO_TAB_LABEL,
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
    print(
        f"demo tab '{DEMO_TAB_LABEL}' created.\n"
        "Any keypress inside a demo pane closes it.\n"
        "Remove everything with: python3 scripts/demo_layout.py --close"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
