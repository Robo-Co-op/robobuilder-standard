# OpenClaw / Codex Distribution

RoboBuilder has one source of truth: the Claude Code plugin in this repository.
The OpenClaw/Codex edition is generated from the same `skills/*/SKILL.md` files
so the Robo Co-op development standard stays consistent across agents.

## What Ships

- `robobuilder-*` skill directories for OpenClaw/Codex
- A shared resource directory: `_robobuilder_shared/`
- The original RoboBuilder docs, runtime helper scripts, agents, hooks, and
  `company.yaml` bundled under that shared directory
- `manifest.json` describing the generated pack

## Generate Locally

```bash
python3 scripts/export_openclaw_codex_skills.py --replace-existing
```

Default output:

```text
dist/openclaw-codex-skills/
```

## Install Into OpenClaw

```bash
python3 scripts/export_openclaw_codex_skills.py \
  --target ~/.openclaw/skills \
  --replace-existing
```

Restart the OpenClaw runtime or reload skills so the new `robobuilder-*` skills
are discovered.

## Install Into Codex

```bash
python3 scripts/export_openclaw_codex_skills.py \
  --target "${CODEX_HOME:-$HOME/.codex}/skills" \
  --replace-existing
```

The generated skills follow Codex's standard `SKILL.md` directory shape:

```text
robobuilder-tdd/
  SKILL.md
robobuilder-diff-review/
  SKILL.md
_robobuilder_shared/
  docs/
  bin/
  agents/
  hooks/
  company.yaml
```

## Naming

Claude Code uses slash commands such as:

```text
/robobuilder:tdd
```

OpenClaw/Codex uses generated skill names such as:

```text
robobuilder-tdd
```

The prefix is intentional. It avoids collisions with local skills named `tdd`,
`ship`, `export`, `guard`, or `start`.

## Adapter Rules

Generated skills prepend a short adapter note:

- Claude Code command `/robobuilder:<name>` maps to `robobuilder-<name>`.
- Claude Code "Skill tool" means load or invoke the referenced RoboBuilder skill.
- Claude Code "Agent tool" maps to the host's subagent/delegation mechanism.
- Hook-only behavior is advisory unless the host provides matching hooks.
- `${CLAUDE_PLUGIN_ROOT}` maps to the sibling `_robobuilder_shared/` directory.

## Maintenance

Do not edit generated OpenClaw/Codex skills by hand. Edit the source skill under
`skills/`, then regenerate the adapter pack.

Validation:

```bash
pytest scripts/tests/test_openclaw_codex_export.py
```
