---
name: guard
version: 0.1.0
description: |
  [Util-1] Full safety mode: destructive command warnings + directory-scoped edits.
  Combines /careful (warns before rm -rf, DROP TABLE, force-push, etc.) with
  /freeze (blocks edits outside a specified directory). Use for maximum safety
  when touching prod or debugging live systems. Use when asked to "guard mode",
  "full safety", "lock it down", or "maximum safety". (robobuilder-local)
triggers:
  - full safety mode
  - guard against mistakes
  - maximum safety
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../careful/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
origin: gstack
upstream: https://github.com/garrytan/gstack
bootcamp_module: M6.compounding-engineering
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: |
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:context-save
> - **Bootcamp**: M6.compounding-engineering
> - **Origin**: Garry Tan upstream, adapted for RoboBuilder

<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /guard — Full Safety Mode

Activates both destructive command warnings and directory-scoped edit restrictions.
This is the combination of `/careful` + `/freeze` in a single command.

## RoboBuilder Runtime Notes

Use `bin/robobuilder-paths` for local state. Full contract: `docs/RUNTIME.md`.

**Dependency note:** This skill references hook scripts from the sibling `/careful`
and `/freeze` skill directories. Both must be installed (they are installed together
with the companion safety skills).

## Setup

Ask the user which directory to restrict edits to. Use AskUserQuestion:

- Question: "Guard mode: which directory should edits be restricted to? Destructive command warnings are always on. Files outside the chosen path will be blocked from editing."
- Text input (not multiple choice) — the user types a path.

Once the user provides a directory path:

1. Resolve it to an absolute path:
```bash
FREEZE_DIR=$(cd "<user-provided-path>" 2>/dev/null && pwd)
echo "$FREEZE_DIR"
```

2. Ensure trailing slash and save to the freeze state file:
```bash
FREEZE_DIR="${FREEZE_DIR%/}/"
eval "$(bin/robobuilder-paths)"
STATE_DIR="$ROBOBUILDER_STATE_ROOT"
mkdir -p "$STATE_DIR"
echo "$FREEZE_DIR" > "$STATE_DIR/freeze-dir.txt"
echo "Freeze boundary set: $FREEZE_DIR"
```

Tell the user:
- "**Guard mode active.** Two protections are now running:"
- "1. **Destructive command warnings** — rm -rf, DROP TABLE, force-push, etc. will warn before executing (you can override)"
- "2. **Edit boundary** — file edits restricted to `<path>/`. Edits outside this directory are blocked."
- "To remove the edit boundary, run `/unfreeze`. To deactivate everything, end the session."

## What's protected

See `/careful` for the full list of destructive command patterns and safe exceptions.
See `/freeze` for how edit boundary enforcement works.
