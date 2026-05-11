"""Tests for notification.py — the Notification/SessionStart hook."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import notification  # noqa: E402


def test_sanitize_strips_quote_injection():
    # Build the attack string at runtime to avoid the test file itself containing the literal
    attack = "hello" + chr(39) + "; rm -rf /; echo " + chr(39)  # 39 = single quote
    result = notification._sanitize(attack)
    assert chr(39) not in result
    assert ";" not in result


def test_sanitize_strips_double_quote():
    attack = "x" + chr(34) + "y" + chr(34) + "z"  # 34 = double quote
    result = notification._sanitize(attack)
    assert chr(34) not in result


def test_sanitize_strips_backtick():
    attack = "ok" + chr(96) + "cmd" + chr(96) + "end"  # 96 = backtick
    result = notification._sanitize(attack)
    assert chr(96) not in result


def test_sanitize_strips_dollar_paren():
    attack = "ok$(cmd)end"
    result = notification._sanitize(attack)
    assert "$" not in result
    assert "(" not in result
    assert ")" not in result


def test_sanitize_truncates_to_limit():
    long_text = "A" * 500
    result = notification._sanitize(long_text)
    assert len(result) == 120


def test_sanitize_preserves_safe_text():
    safe = "Build complete. 5 tests passed, 0 failed!"
    result = notification._sanitize(safe)
    assert result == safe


def test_sanitize_empty_string():
    assert notification._sanitize("") == ""


def test_sanitize_handles_none():
    # `_sanitize(s or "")` handles falsy input
    assert notification._sanitize(None or "") == ""


def test_malformed_json_payload_no_crash(run_script):
    code, _, _ = run_script("notification.py", "garbage-not-json")
    assert code == 0


def test_message_truncated_to_120(monkeypatch):
    captured = {}

    def fake_notify(title, message):
        captured["title"] = title
        captured["message"] = message

    monkeypatch.setattr(notification, "notify", fake_notify)
    long_msg = "X" * 500
    monkeypatch.setattr("json.load", lambda f: {"message": long_msg})
    monkeypatch.setattr(sys, "argv", ["notification.py"])

    notification.main()
    assert len(captured["message"]) <= 120


def test_session_start_event_fixed_message(monkeypatch):
    captured = {}

    def fake_notify(title, message):
        captured["title"] = title
        captured["message"] = message

    monkeypatch.setattr(notification, "notify", fake_notify)
    monkeypatch.setattr("json.load", lambda f: {})
    monkeypatch.setattr(sys, "argv", ["notification.py", "session-start"])

    notification.main()
    assert captured["title"] == "robobuilder"
    assert "robobuilder:start" in captured["message"]


def test_default_message_when_missing(monkeypatch):
    captured = {}

    def fake_notify(title, message):
        captured["title"] = title
        captured["message"] = message

    monkeypatch.setattr(notification, "notify", fake_notify)
    monkeypatch.setattr("json.load", lambda f: {})
    monkeypatch.setattr(sys, "argv", ["notification.py"])

    notification.main()
    assert captured["message"] == "Claude is waiting."


def test_notify_swallows_subprocess_exceptions(monkeypatch):
    """notify() should not raise even if the platform notifier blows up."""
    def fake_beep(*a, **kw):
        raise RuntimeError("boom")

    monkeypatch.setattr(notification, "beep_windows", fake_beep)
    monkeypatch.setattr(notification, "beep_macos", fake_beep)
    monkeypatch.setattr(notification, "beep_linux", fake_beep)

    # Should not raise
    notification.notify("title", "msg")
