"""
Shared pytest fixtures for robobuilder hook script tests.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def run_script():
    """Run a script via subprocess with a JSON stdin payload.

    Returns (exit_code, stdout, stderr).
    """
    def _run(script_name: str, payload: Any, args: list[str] | None = None,
             env_overrides: dict[str, str] | None = None) -> tuple[int, str, str]:
        cmd = [sys.executable, str(SCRIPTS_DIR / script_name)]
        if args:
            cmd.extend(args)
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        stdin = payload if isinstance(payload, str) else json.dumps(payload)
        proc = subprocess.run(
            cmd, input=stdin, capture_output=True, text=True, env=env, timeout=15,
        )
        return proc.returncode, proc.stdout, proc.stderr
    return _run


@pytest.fixture
def tmp_memory_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate memory_consolidate output to a temp dir."""
    monkeypatch.setenv("ROBOBUILDER_MEMORY_DIR", str(tmp_path))
    return tmp_path


def _build_attack_string(prefix: str, char: str, length: int) -> str:
    """Build a secret-shaped string at runtime so test files don't themselves contain literal secrets
    that would trip block_secrets.py when Claude edits the test file."""
    return prefix + char * length
