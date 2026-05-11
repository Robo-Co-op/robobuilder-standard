#!/usr/bin/env python3
"""
memory_consolidate.py — PreCompact / SessionEnd hook for robobuilder.

Best-effort memory consolidation:
- PreCompact: snapshot last N user turns to episodic memory before context shrinks.
- SessionEnd: write today's episodic file if not already written.

Never blocks the harness. Silent on missing nexus/memory directory.

Memory location preference:
1. $ROBOBUILDER_MEMORY_DIR (if set)
2. $HOME/nexus/pc/memory/episodic/ (Jin's setup)
3. $HOME/.claude/projects/.../memory/episodic/ (fallback)
4. Skip (no-op) if none exist
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path


def find_memory_dir() -> Path | None:
    env = os.environ.get("ROBOBUILDER_MEMORY_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p
    home = Path.home()
    for candidate in [
        home / "nexus" / "pc" / "memory" / "episodic",
        home / ".claude" / "memory" / "episodic",
    ]:
        if candidate.exists():
            return candidate
    return None


def write_episodic(mem_dir: Path, event: str, payload: dict) -> None:
    today = dt.date.today().isoformat()
    path = mem_dir / f"{today}.md"
    timestamp = dt.datetime.now().isoformat(timespec="seconds")

    transcript = payload.get("transcript") or payload.get("summary") or ""
    user_text = payload.get("user") or payload.get("last_user_message") or ""

    note = f"\n## {timestamp} — {event}\n"
    if user_text:
        note += f"\n**Last user prompt:** {user_text[:300]}\n"
    if transcript:
        note += f"\n**Snapshot:** {transcript[:1500]}\n"

    # Decide header insertion BEFORE opening in append mode — `open(path, "a")` creates
    # the file as a side effect, so a post-open `stat().st_size` is always 0 on first run
    # and the header would be written every invocation.
    is_new = not path.exists()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(f"# Episodic — {today}\n")
            f.write(note)
    except Exception:
        pass


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "session-end"
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    mem_dir = find_memory_dir()
    if mem_dir is None:
        return 0  # silent no-op

    write_episodic(mem_dir, event, payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
