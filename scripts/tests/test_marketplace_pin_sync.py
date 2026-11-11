"""The pin-sync bot must never publish something that is not a version.

On 2026-08-27 robobuilder-bot committed this as robobuilder-pro's marketplace pin,
and the site printed it on both pages for months:

    ::error::robobuilder-pro returned an unparseable version: ''

robobuilder-pro is a private repo, so the anonymous raw.githubusercontent.com fetch
got a 404. `fetch_version` caught that, echoed its error to stdout and called
`exit 1`, but it was running inside `$(...)` in an `echo` argument. `set -e` does not
fire there, so the error text became the "version". Nothing downstream objected,
because the only pin test checked that a version was non-empty.

Two rules follow. A pin is a semver string or it is not a pin. And when the bot
cannot read a version, it leaves that pin alone and still syncs the others: failing
the whole job would block Lite's pin every six hours just because Pro is private.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "sync-marketplace-pins.yml"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CLAIMS = ROOT / "site" / "claims.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_every_marketplace_pin_is_a_version() -> None:
    plugins = json.loads(MARKETPLACE.read_text(encoding="utf-8"))["plugins"]
    bad = {p["name"]: p.get("version") for p in plugins if not SEMVER.match(str(p.get("version")))}
    assert not bad, f"marketplace.json pins that are not semver: {bad}"


def test_every_version_claim_is_a_version() -> None:
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    bad = {
        cid: c["value"]
        for cid, c in claims.items()
        if cid.endswith("_version") and not SEMVER.match(str(c["value"]))
    }
    assert not bad, f"site/claims.json version claims that are not semver: {bad}"


# --- the workflow's own steps, run against a fake `gh` --------------------------------

yaml = pytest.importorskip("yaml")
needs_bash = pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")


def _step(name_prefix: str) -> str:
    wf = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps = wf["jobs"]["sync"]["steps"]
    return next(s["run"] for s in steps if s.get("name", "").startswith(name_prefix))


def _fake_gh(bin_dir: Path, answers: dict[str, str | None]) -> None:
    """A `gh` that answers `gh api repos/Robo-Co-op/<repo>/...` per repo.

    None means the call fails (exit 1), as it does for a private repo the token
    cannot read.
    """
    cases = []
    for repo, version in answers.items():
        body = "exit 1" if version is None else f"echo '{version}'"
        cases.append(f"  *repos/Robo-Co-op/{repo}/*) {body} ;;")
    script = "#!/usr/bin/env bash\ncase \"$*\" in\n" + "\n".join(cases) + "\n  *) exit 1 ;;\nesac\n"
    gh = bin_dir / "gh"
    gh.write_text(script, encoding="utf-8", newline="\n")
    gh.chmod(0o755)


def _bin(tmp_path: Path) -> Path:
    """A PATH dir whose `python3` is this interpreter (Windows' python3 is a Store stub)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    shim = bin_dir / "python3"
    shim.write_text(
        f'#!/usr/bin/env bash\nexec "{Path(sys.executable).as_posix()}" "$@"\n',
        encoding="utf-8",
        newline="\n",
    )
    shim.chmod(0o755)
    return bin_dir


def _run_fetch(tmp_path: Path, answers: dict[str, str | None]) -> tuple[subprocess.CompletedProcess, dict]:
    bin_dir = _bin(tmp_path)
    _fake_gh(bin_dir, answers)
    out = tmp_path / "out"
    out.write_text("", encoding="utf-8")
    env = {**os.environ, "GITHUB_OUTPUT": str(out), "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    proc = subprocess.run(
        ["bash", "-c", _step("Read what")], env=env, capture_output=True, text=True
    )
    values = dict(line.split("=", 1) for line in out.read_text(encoding="utf-8").splitlines() if "=" in line)
    return proc, values


@needs_bash
def test_unreadable_repo_leaves_its_output_empty_and_still_reads_the_other(tmp_path):
    proc, values = _run_fetch(tmp_path, {"robobuilder-pro": None, "robobuilder-lite": "1.5.0"})
    assert proc.returncode == 0, proc.stderr
    assert values.get("pro") == "", f"pro output should be empty, got {values.get('pro')!r}"
    assert values.get("lite") == "1.5.0"
    assert "robobuilder-pro" in proc.stderr, "the skipped repo should be named in a warning"


@needs_bash
def test_garbage_version_is_not_passed_on(tmp_path):
    proc, values = _run_fetch(tmp_path, {"robobuilder-pro": "not-a-version", "robobuilder-lite": "1.5.0"})
    assert proc.returncode == 0, proc.stderr
    assert values.get("pro") == ""


def _run_update(tmp_path: Path, pro: str, lite: str) -> dict:
    for rel in (".claude-plugin/marketplace.json", "site/claims.json", "site/index.html", "site/ja/index.html"):
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, dest)
    out = tmp_path / "out"
    out.write_text("", encoding="utf-8")
    path = f"{_bin(tmp_path)}{os.pathsep}{os.environ['PATH']}"
    env = {**os.environ, "GITHUB_OUTPUT": str(out), "PRO_V": pro, "LITE_V": lite, "PATH": path, "PYTHONUTF8": "1"}
    proc = subprocess.run(
        ["bash", "-c", _step("Update the pins")], cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    plugins = json.loads((tmp_path / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))["plugins"]
    return {p["name"]: p["version"] for p in plugins}


@needs_bash
@pytest.mark.parametrize("pro", ["", "::error::robobuilder-pro returned an unparseable version: ''"])
def test_update_step_never_writes_a_non_version(tmp_path, pro):
    before = {p["name"]: p["version"] for p in json.loads(MARKETPLACE.read_text(encoding="utf-8"))["plugins"]}
    after = _run_update(tmp_path, pro=pro, lite="9.9.9")
    assert after["robobuilder-pro"] == before["robobuilder-pro"], f"pro pin changed to {after['robobuilder-pro']!r}"
    assert after["robobuilder-lite"] == "9.9.9", "a bad pro value must not stop lite from syncing"
