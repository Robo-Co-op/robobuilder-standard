#!/usr/bin/env python3
"""
update_skill_frontmatter.py — dev helper to add robobuilder pedagogy to ingested SKILL.md files.

For each SKILL.md under skills/{phase0,phase05,phase1,phase2,phase3,phase35,phase4,phase5,utils}/:
  1. Add to frontmatter (if not present):
       - origin: matt-pocock | gstack | jin-custom
       - bootcamp_module: <phase mapping>
       - bootcamp_url: <Notion hub URL>
  2. Insert "robobuilder pedagogy" preamble block after frontmatter, before original body.

Skips meta/ and playbooks/ — those are robobuilder-original, already follow the
7-section format, frontmatter set during initial build.

Idempotent: re-running on a file that already has the preamble doesn't double-insert.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

# Phase → bootcamp module mapping
PHASE_BOOTCAMP = {
    "phase0":  "M3.code.foundation",
    "phase05": "M3.code.investigate",
    "phase1":  "M3.code.design",
    "phase2":  "M3.code.prototype",
    "phase3":  "M3.code.implement",
    "phase35": "M3.code.refactor",
    "phase4":  "M3.code.review",
    "phase5":  "M3.code.ship",
    "utils":   "M6.compounding-engineering",
}

# Origin classification: which upstream pack a skill came from
# (Map: skill_name → origin). Derived from the original build plan.
ORIGIN_BY_SKILL = {
    # Matt Pocock
    "setup": "matt-pocock",
    "zoom-out": "matt-pocock",
    "diagnose": "matt-pocock",
    "grill-me": "matt-pocock",
    "grill-with-docs": "matt-pocock",
    "to-prd": "matt-pocock",
    "to-issues": "matt-pocock",
    "prototype": "matt-pocock",
    "triage": "matt-pocock",
    "tdd": "matt-pocock",
    "caveman": "matt-pocock",
    "improve-codebase-architecture": "matt-pocock",
    "write-a-skill": "matt-pocock",
    # GStack
    "health": "gstack",
    "browse": "gstack",
    "learn": "gstack",
    "cso": "gstack",
    "ship": "gstack",
    "land-and-deploy": "gstack",
    "canary": "gstack",
    "plan-eng-review": "gstack",
    "guard": "gstack",
    "context-save": "gstack",
    "context-restore": "gstack",
    # Jin custom
    "ubiquitous-language": "jin-custom",
    "design-an-interface": "jin-custom",
    "request-refactor-plan": "jin-custom",
    "diff-review": "jin-custom",
    "cross-review": "jin-custom",
    "grill": "jin-custom",
    "handoff": "jin-custom",
    "btw": "jin-custom",
    "export": "jin-custom",
}

# Origin → human-readable attribution
ORIGIN_ATTRIBUTION = {
    "matt-pocock": "Matt Pocock (AI Engineering Skills, MIT)",
    "gstack": "Garry Tan (GStack, MIT)",
    "jin-custom": "Robo Co-op (Jin Kim)",
}

NOTION_HUB = "https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504"
PREAMBLE_MARKER = "robobuilder pedagogy"


# When → trigger keyword extraction (heuristic)
# When → see-also suggestions per skill (chained workflow neighbors)
SEE_ALSO = {
    "setup":                          ["/robobuilder:ubiquitous-language", "/robobuilder:zoom-out"],
    "ubiquitous-language":            ["/robobuilder:setup", "/robobuilder:to-prd"],
    "zoom-out":                       ["/robobuilder:diagnose", "/robobuilder:health"],
    "diagnose":                       ["/robobuilder:zoom-out", "/robobuilder:tdd", "/robobuilder:playbook-bug-fix"],
    "health":                         ["/robobuilder:zoom-out", "/robobuilder:diagnose"],
    "grill-me":                       ["/robobuilder:to-prd", "/robobuilder:design-an-interface"],
    "design-an-interface":            ["/robobuilder:grill-me", "/robobuilder:grill-with-docs", "/robobuilder:to-prd"],
    "grill-with-docs":                ["/robobuilder:to-prd", "/robobuilder:to-issues"],
    "to-prd":                         ["/robobuilder:grill-me", "/robobuilder:to-issues"],
    "to-issues":                      ["/robobuilder:to-prd", "/robobuilder:tdd"],
    "plan-eng-review":                ["/robobuilder:to-prd", "/robobuilder:tdd"],
    "prototype":                      ["/robobuilder:grill-me", "/robobuilder:tdd"],
    "triage":                         ["/robobuilder:to-issues", "/robobuilder:tdd"],
    "tdd":                            ["/robobuilder:diagnose", "/robobuilder:diff-review", "/robobuilder:playbook-new-feature"],
    "caveman":                        ["/robobuilder:handoff", "/robobuilder:context-save"],
    "browse":                         ["/robobuilder:canary", "/robobuilder:cso"],
    "learn":                          ["/robobuilder:write-a-skill"],
    "improve-codebase-architecture":  ["/robobuilder:request-refactor-plan", "/robobuilder:tdd"],
    "request-refactor-plan":          ["/robobuilder:improve-codebase-architecture", "/robobuilder:tdd"],
    "diff-review":                    ["/robobuilder:cross-review", "/robobuilder:grill", "/robobuilder:playbook-review-deep"],
    "cross-review":                   ["/robobuilder:diff-review", "/robobuilder:grill"],
    "grill":                          ["/robobuilder:diff-review", "/robobuilder:cross-review", "/robobuilder:grill-me"],
    "cso":                            ["/robobuilder:diff-review", "/robobuilder:cross-review"],
    "ship":                           ["/robobuilder:land-and-deploy", "/robobuilder:canary"],
    "land-and-deploy":                ["/robobuilder:ship", "/robobuilder:canary"],
    "canary":                         ["/robobuilder:land-and-deploy", "/robobuilder:browse"],
    "handoff":                        ["/robobuilder:context-save", "/robobuilder:write-a-skill"],
    "write-a-skill":                  ["/robobuilder:handoff", "/robobuilder:learn"],
    "guard":                          ["/robobuilder:context-save"],
    "context-save":                   ["/robobuilder:context-restore", "/robobuilder:handoff"],
    "context-restore":                ["/robobuilder:context-save"],
    "btw":                            ["/robobuilder:start", "/robobuilder:handoff"],
    "export":                         ["/robobuilder:handoff"],
}


class SkillFile(NamedTuple):
    path: Path
    skill_name: str
    phase: str


def discover_skills(plugin_root: Path) -> list[SkillFile]:
    out: list[SkillFile] = []
    skills_root = plugin_root / "skills"
    for phase in PHASE_BOOTCAMP:
        phase_dir = skills_root / phase
        if not phase_dir.is_dir():
            continue
        for skill_dir in sorted(phase_dir.iterdir()):
            sk_md = skill_dir / "SKILL.md"
            if sk_md.is_file():
                out.append(SkillFile(sk_md, skill_dir.name, phase))
    return out


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_block, rest). frontmatter_block includes both --- markers + a trailing newline."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[: end + 5], text[end + 5 :]


def extract_field(frontmatter: str, key: str) -> str | None:
    for line in frontmatter.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def ensure_frontmatter_fields(frontmatter: str, skill: SkillFile) -> str:
    """Append missing origin/bootcamp_module/bootcamp_url lines before the closing ---."""
    origin = ORIGIN_BY_SKILL.get(skill.skill_name)
    bootcamp_module = PHASE_BOOTCAMP[skill.phase]

    additions: list[str] = []
    if origin and not extract_field(frontmatter, "origin"):
        additions.append(f"origin: {origin}")
    if not extract_field(frontmatter, "bootcamp_module"):
        additions.append(f"bootcamp_module: {bootcamp_module}")
    if not extract_field(frontmatter, "bootcamp_url"):
        additions.append(f"bootcamp_url: {NOTION_HUB}")

    if not additions:
        return frontmatter

    # Insert before the closing --- line (which is the last `\n---\n` we matched).
    closing = frontmatter.rfind("\n---\n")
    return frontmatter[:closing] + "\n" + "\n".join(additions) + frontmatter[closing:]


def build_preamble(skill: SkillFile, description: str) -> str:
    """Build the robobuilder pedagogy preamble block."""
    origin = ORIGIN_BY_SKILL.get(skill.skill_name, "robobuilder")
    attribution = ORIGIN_ATTRIBUTION.get(origin, "robobuilder")
    bootcamp = PHASE_BOOTCAMP[skill.phase]
    see_also = SEE_ALSO.get(skill.skill_name, [])
    see_also_line = ", ".join(see_also) if see_also else "(see docs/WORKFLOW.md)"

    # Compress description to ~80 chars for the What line.
    what = description.split(". ", 1)[0].rstrip(".")
    if len(what) > 120:
        what = what[:117] + "..."

    return (
        f"> **{PREAMBLE_MARKER}** ({skill.phase})\n"
        f"> - **What**: {what}\n"
        f"> - **When**: see the description above for trigger keywords; details in the body below.\n"
        f"> - **See Also**: {see_also_line}\n"
        f"> - **Bootcamp**: {bootcamp}\n"
        f"> - **Origin**: {attribution}\n"
        f"\n"
    )


def process_skill(skill: SkillFile, dry_run: bool = False) -> str:
    text = skill.path.read_text(encoding="utf-8")
    if PREAMBLE_MARKER in text:
        return "skip:already-has-preamble"

    fm, body = split_frontmatter(text)
    if not fm:
        return "skip:no-frontmatter"

    description = extract_field(fm, "description") or skill.skill_name
    new_fm = ensure_frontmatter_fields(fm, skill)
    preamble = build_preamble(skill, description)
    new_text = new_fm + preamble + body

    if not dry_run:
        skill.path.write_text(new_text, encoding="utf-8")
    return "updated"


def main() -> int:
    plugin_root = Path(__file__).resolve().parent.parent.parent
    dry_run = "--dry-run" in sys.argv

    skills = discover_skills(plugin_root)
    print(f"Discovered {len(skills)} ingested SKILL.md files under {plugin_root / 'skills'}")
    print()

    counts: dict[str, int] = {}
    for sk in skills:
        result = process_skill(sk, dry_run=dry_run)
        counts[result] = counts.get(result, 0) + 1
        marker = "DRY" if dry_run else "OK"
        print(f"  [{marker}] {sk.phase}/{sk.skill_name}: {result}")

    print()
    print("Summary:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
