"""Tests for memory_consolidate.py — the PreCompact/SessionEnd hook."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import memory_consolidate  # noqa: E402


def _today() -> str:
    return dt.date.today().isoformat()


def test_env_var_destination(run_script, tmp_memory_dir):
    payload = {"transcript": "did some work today"}
    code, _, _ = run_script("memory_consolidate.py", payload, args=["session-end"])
    assert code == 0
    written = list(tmp_memory_dir.glob("*.md"))
    assert len(written) == 1
    assert written[0].name == f"{_today()}.md"


def test_no_dir_anywhere_silent_noop(run_script, tmp_path, monkeypatch):
    monkeypatch.delenv("ROBOBUILDER_MEMORY_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "fake-home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "fake-home"))
    code, _, _ = run_script("memory_consolidate.py", {"transcript": "x"}, args=["session-end"])
    assert code == 0


def test_header_written_once_two_invocations(run_script, tmp_memory_dir):
    """Regression test for the stat-after-open bug fixed in cross-review Round 1."""
    run_script("memory_consolidate.py", {"transcript": "first"}, args=["session-end"])
    run_script("memory_consolidate.py", {"transcript": "second"}, args=["pre-compact"])

    fp = tmp_memory_dir / f"{_today()}.md"
    body = fp.read_text(encoding="utf-8")
    header_count = body.count("# Episodic")
    section_count = body.count("## ")
    assert header_count == 1, f"header should appear once, got {header_count}\n{body}"
    assert section_count == 2, f"two sections expected, got {section_count}\n{body}"


def test_long_transcript_truncated(run_script, tmp_memory_dir):
    long_text = "X" * 2000
    run_script("memory_consolidate.py", {"transcript": long_text}, args=["session-end"])
    fp = tmp_memory_dir / f"{_today()}.md"
    body = fp.read_text(encoding="utf-8")
    # 1500 char limit per the script
    assert "XXXX" in body
    assert body.count("X") <= 1500 + 50  # some slack for header text


def test_default_event_session_end(run_script, tmp_memory_dir):
    # No event arg → defaults to "session-end"
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "memory_consolidate.py")],
        input='{"transcript":"hi"}', capture_output=True, text=True, timeout=10,
        env={**__import__("os").environ, "ROBOBUILDER_MEMORY_DIR": str(tmp_memory_dir)},
    )
    assert proc.returncode == 0
    fp = tmp_memory_dir / f"{_today()}.md"
    assert "session-end" in fp.read_text(encoding="utf-8")


def test_write_permission_denied_swallowed(run_script, tmp_path, monkeypatch):
    # Create a "directory" that is actually a file → mkdir/open will fail
    forbidden_parent = tmp_path / "forbidden"
    forbidden_parent.write_text("blocking file")  # not a dir
    monkeypatch.setenv("ROBOBUILDER_MEMORY_DIR", str(forbidden_parent))
    code, _, _ = run_script("memory_consolidate.py", {"transcript": "x"}, args=["session-end"])
    assert code == 0  # silent swallow


def test_user_text_in_output(run_script, tmp_memory_dir):
    payload = {"user": "tested the bug fix"}
    run_script("memory_consolidate.py", payload, args=["pre-compact"])
    fp = tmp_memory_dir / f"{_today()}.md"
    body = fp.read_text(encoding="utf-8")
    assert "tested the bug fix" in body
    assert "pre-compact" in body
