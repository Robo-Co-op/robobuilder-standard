"""Tests for auto_format.py — the PostToolUse hook that runs language formatters."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import auto_format  # noqa: E402


def _make_payload(file_path: str) -> dict:
    return {"tool_name": "Edit", "tool_input": {"file_path": file_path}}


def test_no_autoformat_env_returns_early(run_script, tmp_path, monkeypatch):
    target = tmp_path / "x.py"
    target.write_text("print(1)\n")
    code, _, _ = run_script(
        "auto_format.py",
        _make_payload(str(target)),
        env_overrides={"ROBOBUILDER_NO_AUTOFORMAT": "1"},
    )
    assert code == 0


def test_missing_file_exits_zero(run_script):
    code, _, _ = run_script("auto_format.py", _make_payload("/does/not/exist.py"))
    assert code == 0


def test_malformed_json_stdin_exits_zero(run_script):
    code, _, _ = run_script("auto_format.py", "not-json-at-all")
    assert code == 0


def test_unknown_extension_no_subprocess(run_script, tmp_path):
    target = tmp_path / "x.rb"
    target.write_text("puts 'hi'\n")
    code, _, _ = run_script("auto_format.py", _make_payload(str(target)))
    assert code == 0


def test_uppercase_extension_still_selected(tmp_path, monkeypatch):
    """`.JSON` (uppercase) should match `.json` formatter via suffix.lower()."""
    target = tmp_path / "x.JSON"
    target.write_text('{"a":1}')

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(auto_format, "shutil",
                        type("S", (), {"which": staticmethod(lambda x: f"/fake/{x}")})())
    monkeypatch.setattr(auto_format.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "stdin", type("S", (), {"read": staticmethod(
        lambda: json.dumps(_make_payload(str(target))))})())

    # Direct invocation
    monkeypatch.setattr("json.load", lambda f: _make_payload(str(target)))
    auto_format.main()
    assert any("prettier" in c[0] for c in calls)


def test_python_ruff_preferred_over_black(tmp_path, monkeypatch):
    target = tmp_path / "x.py"
    target.write_text("x = 1\n")
    seen = []

    def fake_which(name):
        seen.append(("which", name))
        return f"/fake/{name}" if name == "ruff" else None

    def fake_run(cmd, **kwargs):
        seen.append(("run", cmd))
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(auto_format.shutil, "which", fake_which)
    monkeypatch.setattr(auto_format.subprocess, "run", fake_run)
    monkeypatch.setattr("json.load", lambda f: _make_payload(str(target)))

    auto_format.main()
    run_cmds = [s for s in seen if s[0] == "run"]
    assert len(run_cmds) == 1
    assert run_cmds[0][1][0] == "ruff"


def test_python_black_fallback(tmp_path, monkeypatch):
    target = tmp_path / "x.py"
    target.write_text("x = 1\n")
    seen = []

    def fake_which(name):
        return f"/fake/{name}" if name == "black" else None

    def fake_run(cmd, **kwargs):
        seen.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(auto_format.shutil, "which", fake_which)
    monkeypatch.setattr(auto_format.subprocess, "run", fake_run)
    monkeypatch.setattr("json.load", lambda f: _make_payload(str(target)))

    auto_format.main()
    assert len(seen) == 1
    assert seen[0][0] == "black"


def test_formatter_timeout_still_exits_zero(tmp_path, monkeypatch):
    target = tmp_path / "x.py"
    target.write_text("x=1")

    def fake_which(name):
        return "/fake/ruff"

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ruff", timeout=10)

    monkeypatch.setattr(auto_format.shutil, "which", fake_which)
    monkeypatch.setattr(auto_format.subprocess, "run", fake_run)
    monkeypatch.setattr("json.load", lambda f: _make_payload(str(target)))

    code = auto_format.main()
    assert code == 0


def test_both_file_path_and_path_keys_work(tmp_path, monkeypatch):
    target = tmp_path / "x.py"
    target.write_text("x=1")

    # tool_input uses "path" instead of "file_path"
    payload = {"tool_name": "Edit", "tool_input": {"path": str(target)}}
    seen = []
    monkeypatch.setattr(auto_format.shutil, "which", lambda n: f"/fake/{n}")
    monkeypatch.setattr(auto_format.subprocess, "run",
                        lambda cmd, **kw: seen.append(cmd) or subprocess.CompletedProcess(cmd, 0, b"", b""))
    monkeypatch.setattr("json.load", lambda f: payload)

    auto_format.main()
    assert len(seen) == 1
