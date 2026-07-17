---
title: "Demo layout: lost-session incident and safety redesign"
date: 2026-07-17
created: "2026-07-17 Fri 23:15"
---

# Demo layout: lost-session incident and safety redesign

## Symptom

Running `scripts/demo_layout.py` in a live Herdr session replaced the active
tab with four fictional demo panes. The demo panes ignored every keypress, so
the user had to kill each pane individually; killing the last pane closed the
whole tab — destroying the real workspace (including a running agent session)
that the demo had replaced.

## Root causes

Two independent defects combined:

1. **No isolation.** `demo_layout.py` called `layout.apply` on the *active*
   tab of whatever session `HERDR_SESSION`/`HERDR_SOCKET_PATH` resolved to.
   In the default session that meant replacing the user's real layout. Herdr
   closes a tab when its last pane exits, so once the demo panes were killed,
   the original tab (and everything the layout replacement had displaced) was
   gone.
2. **Panes that could not be ended from the keyboard.** `demo_pane.py` slept
   forever and only exited on SIGINT/SIGTERM. Typing `q`, Enter, or anything
   else did nothing, which is why each pane had to be force-killed.

A third, subtler defect was found while verifying the fix: signals delivered
in the window after Python's last signal check but before `read()` blocks were
lost until the next keypress (confirmed with `sample`: the process sat in
kernel `read()` with the signal already delivered). Roughly 1-in-30 kills hit
this race under load.

## Fixes

- `demo_layout.py` creates a **new** tab labeled `pane-picker-demo`
  (`tab.create` + `layout.apply` on the new tab id) and never touches an
  existing layout. Closing demo panes can only ever close the demo tab.
- It **refuses to run** unless the target session is isolated
  (`HERDR_SESSION` set to a non-default name, or `HERDR_SOCKET_PATH` set
  explicitly). `--force` overrides deliberately.
- `demo_layout.py --close` removes all `pane-picker-demo` tabs.
- `demo_pane.py` ends on **any keypress**, on stdin EOF (PTY close), and on
  SIGINT/SIGTERM/SIGHUP. A `signal.set_wakeup_fd` pipe plus `select` over
  stdin and the pipe closes the lost-signal race.

## Validation

```sh
python3 -m unittest discover -s tests -v   # includes tests/test_demo_pane.py
```

`tests/test_demo_pane.py` spawns the pane on a real PTY and asserts exit on
keypress, PTY close, SIGTERM, and SIGHUP. The signal paths were additionally
stress-tested 30× each during development; pre-fix, SIGTERM/SIGHUP/SIGINT
each showed intermittent hangs.

## Safe capture workflow

```sh
herdr --session pane-picker-demo
HERDR_SESSION=pane-picker-demo python3 scripts/demo_layout.py
HERDR_SESSION=pane-picker-demo python3 pane_picker.py show
HERDR_SESSION=pane-picker-demo python3 scripts/demo_layout.py --close
```
