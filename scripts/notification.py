#!/usr/bin/env python3
"""
notification.py — Notification + SessionStart hook for robobuilder.

Cross-platform notifier:
- macOS: osascript via `say` or visual notification
- Windows: PowerShell BurntToast / System.Media.SystemSounds
- Linux: notify-send fallback

Reads JSON event payload on stdin. Best-effort, never blocks the harness.
"""
from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import sys


# Strip everything that could break quote contexts in PowerShell / AppleScript / shell.
# Keep only safe printable ASCII the notifier needs to display.
_SAFE_CHARS = re.compile(r"[^A-Za-z0-9 .,!?\-]")


def _sanitize(s: str, limit: int = 120) -> str:
    return _SAFE_CHARS.sub("", s or "")[:limit]


def beep_windows(title: str, message: str) -> None:
    # No string interpolation into the command. Just play the sound; the title/message
    # come back to the user via the dedicated notifier paths if a real toast is wired up.
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "[System.Media.SystemSounds]::Asterisk.Play()",
    ]
    subprocess.run(cmd, capture_output=True, check=False, timeout=4)


def beep_macos(title: str, message: str) -> None:
    # AppleScript injection vector — sanitize before embedding.
    safe_title = _sanitize(title, 60)
    safe_msg = _sanitize(message, 120)
    script = (
        f'display notification "{safe_msg}" '
        f'with title "{safe_title}" sound name "Submarine"'
    )
    subprocess.run(["osascript", "-e", script], capture_output=True, check=False, timeout=4)


def beep_linux(title: str, message: str) -> None:
    if shutil.which("notify-send"):
        # notify-send takes args as separate list items; no shell interpolation.
        # Still sanitize to keep desktop notification UIs clean.
        subprocess.run(
            ["notify-send", _sanitize(title, 60), _sanitize(message, 120)],
            capture_output=True,
            check=False,
            timeout=4,
        )


def notify(title: str, message: str) -> None:
    # Centralized dispatch. Each platform implementation is responsible for its own
    # sanitization (see beep_macos / beep_linux). The Windows path no longer
    # interpolates user content into the command line.
    system = platform.system()
    try:
        if system == "Windows":
            beep_windows(title, message)
        elif system == "Darwin":
            beep_macos(title, message)
        else:
            beep_linux(title, message)
    except Exception:
        pass


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "notification"

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    if event == "session-start":
        notify("robobuilder", "Session started — try /robobuilder:start if you're new here.")
    else:
        msg = payload.get("message") or payload.get("text") or "Claude is waiting."
        notify("Claude Code", msg[:120])

    return 0


if __name__ == "__main__":
    sys.exit(main())
