from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPORT_SCRIPT = REPO_ROOT / "scripts" / "export_openclaw_codex_skills.py"


def run_export(target: Path) -> None:
    subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT), "--target", str(target), "--replace-existing"],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )


def test_openclaw_codex_export_generates_one_adapter_per_source_skill(tmp_path: Path):
    target = tmp_path / "skills"
    run_export(target)

    source_count = len(list((REPO_ROOT / "skills").rglob("SKILL.md")))
    generated = sorted(target.glob("robobuilder-*/SKILL.md"))

    assert len(generated) == source_count
    assert source_count >= 30


def test_openclaw_codex_export_prefixes_skill_names_and_adds_adapter_note(tmp_path: Path):
    target = tmp_path / "skills"
    run_export(target)

    for skill_file in target.glob("robobuilder-*/SKILL.md"):
        text = skill_file.read_text(encoding="utf-8")
        assert text.startswith("---\nname: robobuilder-")
        assert "adapter: openclaw-codex" in text
        assert "# RoboBuilder OpenClaw/Codex Adapter" in text
        assert "../_robobuilder_shared/" in text


def test_openclaw_codex_export_includes_shared_resources_and_manifest(tmp_path: Path):
    target = tmp_path / "skills"
    run_export(target)

    shared = target / "_robobuilder_shared"
    assert (shared / "docs" / "RUNTIME.md").exists()
    assert (shared / "bin" / "robobuilder-paths").exists()
    assert (shared / "company.yaml").exists()

    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "robobuilder-openclaw-codex"
    assert manifest["shared"] == "_robobuilder_shared"
    assert "robobuilder-tdd" in manifest["skills"]
