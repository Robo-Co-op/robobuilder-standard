#!/usr/bin/env python3
"""
auto_format.py — PostToolUse hook for Edit/Write/MultiEdit.

Runs the appropriate formatter for the edited file's language, if available.
Best-effort: never blocks the harness, never raises.

Supported:
- .py            → ruff format (preferred) or black
- .js/.ts/.jsx/.tsx → prettier
- .json           → prettier
- .md             → prettier
- .go             → gofmt
- .rs             → rustfmt

To opt out: set env var ROBOBUILDER_NO_AUTOFORMAT=1
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


FORMATTERS: dict[str, list[list[str]]] = {
    ".py": [["ruff", "format"], ["black", "-q"]],
    ".js": [["prettier", "--write", "--log-level=silent"]],
    ".jsx": [["prettier", "--write", "--log-level=silent"]],
    ".ts": [["prettier", "--write", "--log-level=silent"]],
    ".tsx": [["prettier", "--write", "--log-level=silent"]],
    ".json": [["prettier", "--write", "--log-level=silent"]],
    ".md": [["prettier", "--write", "--log-level=silent"]],
    ".go": [["gofmt", "-w"]],
    ".rs": [["rustfmt"]],
}


def main() -> int:
    if os.environ.get("ROBOBUILDER_NO_AUTOFORMAT"):
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    params = payload.get("tool_input") or payload.get("params") or {}
    path_str = params.get("file_path") or params.get("path")
    if not path_str:
        return 0

    path = Path(path_str)
    if not path.exists():
        return 0

    candidates = FORMATTERS.get(path.suffix.lower())
    if not candidates:
        return 0

    for cmd in candidates:
        if shutil.which(cmd[0]):
            try:
                subprocess.run([*cmd, str(path)], capture_output=True, timeout=10, check=False)
            except Exception:
                pass
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
