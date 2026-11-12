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


def test_replace_keeps_pro_lite_and_unmanaged_skills(tmp_path: Path):
    target = tmp_path / "skills"
    for name in ("robobuilder-pro-dev-loop", "robobuilder-lite-build", "robobuilder-local"):
        skill = target / name / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("local skill\n")
    run_export(target)
    for name in ("robobuilder-pro-dev-loop", "robobuilder-lite-build", "robobuilder-local"):
        assert (target / name / "SKILL.md").read_text() == "local skill\n"

import pytest


def tree_bytes(root):
    return {str(p.relative_to(root)): ('link', str(p.readlink())) if p.is_symlink()
            else ('file', p.read_bytes()) for p in root.rglob('*') if p.is_symlink() or p.is_file()}


@pytest.mark.parametrize('replace', [False, True])
@pytest.mark.parametrize('collision', ['local', 'directory-link', 'skill-link', 'manifest-link', 'shared-link'])
def test_collision_refuses_before_any_mutation(tmp_path, replace, collision):
    target = tmp_path / 'skills'
    run_export(target)  # Real product pack; detect partial cleanup, too.
    skill = target / 'robobuilder-tdd' / 'SKILL.md'
    outside = tmp_path / 'outside'; outside.mkdir()
    sentinel = outside / 'SKILL.md'; sentinel.write_bytes(b'LOCAL\r\nDO NOT OVERWRITE\r\n')
    if collision == 'local':
        skill.write_bytes(sentinel.read_bytes())
    elif collision == 'directory-link':
        import shutil
        shutil.rmtree(skill.parent); skill.parent.symlink_to(outside, target_is_directory=True)
    elif collision == 'skill-link':
        skill.unlink(); skill.symlink_to(sentinel)
    elif collision == 'manifest-link':
        (target / 'manifest.json').unlink(); (target / 'manifest.json').symlink_to(sentinel)
    else:
        import shutil
        shutil.rmtree(target / '_robobuilder_shared')
        (target / '_robobuilder_shared').symlink_to(outside, target_is_directory=True)
    before = tree_bytes(tmp_path)
    args = [sys.executable, str(EXPORT_SCRIPT), '--target', str(target)]
    if replace: args.append('--replace-existing')
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode != 0
    assert tree_bytes(tmp_path) == before


@pytest.mark.parametrize('replace', [False, True])
def test_managed_refresh_still_works(tmp_path, replace):
    target = tmp_path / 'skills'; run_export(target)
    skill = target / 'robobuilder-tdd' / 'SKILL.md'
    expected = skill.read_bytes(); skill.write_bytes(expected + b'\nold generated body\n')
    args = [sys.executable, str(EXPORT_SCRIPT), '--target', str(target)]
    if replace: args.append('--replace-existing')
    subprocess.run(args, check=True, capture_output=True)
    assert skill.read_bytes() == expected


@pytest.mark.parametrize('kind', ['target', 'ancestor', 'dangling-skill', 'dangling-directory', 'marker-in-body', 'empty-local-dir'])
def test_additional_unmanaged_paths_stay_untouched(tmp_path, kind):
    target = tmp_path / 'skills'
    outside = tmp_path / 'outside'; outside.mkdir()
    if kind in ('target', 'ancestor'):
        target.symlink_to(outside, target_is_directory=True)
        if kind == 'ancestor': target = target / 'child'
    else:
        skill = target / 'robobuilder-tdd' / 'SKILL.md'
        skill.parent.mkdir(parents=True)
        if kind == 'dangling-skill': skill.symlink_to(outside / 'missing')
        elif kind == 'dangling-directory':
            skill.parent.rmdir(); skill.parent.symlink_to(outside / 'missing-dir', target_is_directory=True)
        elif kind == 'marker-in-body':
            skill.write_text('local prose\nadapter: openclaw-codex\nsource_skill: skills/phase3/tdd/SKILL.md\n')
    before = tree_bytes(tmp_path)
    result = subprocess.run([sys.executable, str(EXPORT_SCRIPT), '--target', str(target), '--replace-existing'], capture_output=True)
    assert result.returncode != 0
    assert tree_bytes(tmp_path) == before
