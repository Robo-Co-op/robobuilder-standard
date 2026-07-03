#!/usr/bin/env python3
"""Export RoboBuilder Claude Code skills as OpenClaw/Codex skills.

Claude Code remains the source of truth. This script generates an adapter pack
with prefixed skill names so OpenClaw/Codex users can install the same Robo
Co-op development standard without hand-maintaining a second skill tree.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = REPO_ROOT / "dist" / "openclaw-codex-skills"
SHARED_DIR_NAME = "_robobuilder_shared"


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")
    return text[4:end], text[end + 5 :]


def frontmatter_value(frontmatter: str, key: str) -> str:
    lines = frontmatter.splitlines()
    for idx, line in enumerate(lines):
        if not line.startswith(f"{key}:"):
            continue

        raw = line.split(":", 1)[1].strip()
        if raw in {"|", ">"}:
            block: list[str] = []
            for next_line in lines[idx + 1 :]:
                if next_line and not next_line.startswith((" ", "\t", "-")):
                    break
                block.append(next_line.strip())
            return " ".join(part for part in block if part).strip()

        return raw.strip("\"'")

    return ""


def skill_name(source: Path) -> str:
    frontmatter, _ = split_frontmatter(source.read_text(encoding="utf-8"))
    name = frontmatter_value(frontmatter, "name")
    if not name:
        raise ValueError(f"{source} is missing frontmatter name")
    return name


def generated_skill_text(source: Path) -> str:
    original = source.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(original)
    name = frontmatter_value(frontmatter, "name")
    description = frontmatter_value(frontmatter, "description")
    origin = frontmatter_value(frontmatter, "origin")
    rel_source = source.relative_to(REPO_ROOT).as_posix()

    adapted_name = f"robobuilder-{name}"
    adapted_description = (
        f"RoboBuilder/OpenClaw-Codex adapter for /robobuilder:{name}. "
        f"{description}"
    ).strip()

    generated_frontmatter = [
        "---",
        f"name: {adapted_name}",
        f"description: {json.dumps(adapted_description, ensure_ascii=False)}",
        f"source_skill: {rel_source}",
        "adapter: openclaw-codex",
    ]
    if origin:
        generated_frontmatter.append(f"origin: {json.dumps(origin, ensure_ascii=False)}")
    generated_frontmatter.append("---")

    adapter_note = f"""
# RoboBuilder OpenClaw/Codex Adapter

This skill is generated from `{rel_source}`. Do not edit this copy by hand;
update the source skill in the RoboBuilder repo and regenerate the adapter pack.

## Invocation Mapping

- Claude Code command `/robobuilder:{name}` maps to this skill: `robobuilder-{name}`.
- Claude Code "Skill tool" means: load or invoke the referenced RoboBuilder skill.
- Claude Code "Agent tool" means: use the host's subagent/delegation mechanism when available.
- Claude Code hook-only behavior is advisory in OpenClaw/Codex unless the host provides matching hooks.

## Shared Resources

Generated installs include shared RoboBuilder resources as a sibling directory:
`../{SHARED_DIR_NAME}/`.

Use that directory for bundled docs, runtime helper scripts, agents, hooks, and
`company.yaml` when the original instructions reference `${{CLAUDE_PLUGIN_ROOT}}`,
`bin/robobuilder-*`, `docs/...`, or `agents/...`.

---
"""

    return "\n".join(generated_frontmatter) + "\n" + adapter_note + body.lstrip()


def copy_shared_resources(target: Path) -> None:
    shared = target / SHARED_DIR_NAME
    if shared.exists():
        shutil.rmtree(shared)
    shared.mkdir(parents=True, exist_ok=True)

    for directory in ("docs", "bin", "agents", "hooks"):
        shutil.copytree(REPO_ROOT / directory, shared / directory)

    for filename in ("README.md", "CHANGELOG.md", "LICENSE", "company.yaml", "CLAUDE.md.baseline"):
        shutil.copy2(REPO_ROOT / filename, shared / filename)


def remove_managed_outputs(target: Path) -> None:
    for path in target.glob("robobuilder-*"):
        if path.is_dir():
            shutil.rmtree(path)
    shared = target / SHARED_DIR_NAME
    if shared.exists():
        shutil.rmtree(shared)


def export_skills(target: Path, replace_existing: bool) -> list[Path]:
    target.mkdir(parents=True, exist_ok=True)
    if replace_existing:
        remove_managed_outputs(target)

    copy_shared_resources(target)

    written: list[Path] = []
    for source in sorted((REPO_ROOT / "skills").rglob("SKILL.md")):
        name = skill_name(source)
        destination = target / f"robobuilder-{name}" / "SKILL.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(generated_skill_text(source), encoding="utf-8")
        written.append(destination)

    manifest = {
        "name": "robobuilder-openclaw-codex",
        "description": "Generated OpenClaw/Codex adapter pack for RoboBuilder skills.",
        "source": "https://github.com/Robo-Co-op/robobuilder-standard",
        "skills": [path.parent.name for path in written],
        "shared": SHARED_DIR_NAME,
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Directory to write generated skill directories into.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace previously generated robobuilder-* directories in the target.",
    )
    args = parser.parse_args()

    written = export_skills(args.target.expanduser().resolve(), args.replace_existing)
    print(f"Exported {len(written)} RoboBuilder skills to {args.target}")
    print(f"Shared resources: {args.target / SHARED_DIR_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
