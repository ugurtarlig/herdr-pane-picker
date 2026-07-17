"""Regression tests: demo panes must always be closable.

The original demo pane ignored keypresses and only exited on signals, which
once trapped a user inside a demo layout. Every deterministic exit path is
covered here; the signal paths are additionally guarded by the wakeup pipe in
``wait_for_exit``.
"""

from __future__ import annotations

import os
import pty
import signal
import sys
import time
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "demo_pane.py"
EXIT_TIMEOUT = 10.0


class DemoPaneExitTests(unittest.TestCase):
    def spawn(self):
        pid, fd = pty.fork()
        if pid == 0:
            os.execv(sys.executable, [sys.executable, str(SCRIPT), "shell"])
        # Wait for the initial screen so the child is inside wait_for_exit.
        os.read(fd, 65536)
        time.sleep(0.2)
        return pid, fd

    def assert_exits(self, pid):
        deadline = time.time() + EXIT_TIMEOUT
        while time.time() < deadline:
            done, status = os.waitpid(pid, os.WNOHANG)
            if done:
                return status
            time.sleep(0.05)
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
        self.fail("demo pane did not exit")

    def test_any_keypress_ends_the_pane(self):
        pid, fd = self.spawn()
        try:
            os.write(fd, b"q")
            status = self.assert_exits(pid)
            self.assertEqual(status, 0)
        finally:
            os.close(fd)

    def test_pty_close_ends_the_pane(self):
        pid, fd = self.spawn()
        os.close(fd)
        status = self.assert_exits(pid)
        self.assertEqual(os.waitstatus_to_exitcode(status), 0)

    def test_sigterm_ends_the_pane(self):
        pid, fd = self.spawn()
        try:
            os.kill(pid, signal.SIGTERM)
            status = self.assert_exits(pid)
            self.assertEqual(status, 0)
        finally:
            os.close(fd)

    def test_sighup_ends_the_pane(self):
        pid, fd = self.spawn()
        try:
            os.kill(pid, signal.SIGHUP)
            status = self.assert_exits(pid)
            self.assertEqual(status, 0)
        finally:
            os.close(fd)


if __name__ == "__main__":
    unittest.main()
