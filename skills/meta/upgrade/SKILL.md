---
name: upgrade
description: Semver-aware upgrade of robobuilder. Pulls latest from the official repo, shows a diff preview of skills/agents/hooks that changed, prompts for approval per change, then applies. Re-runs tune-claude-md if baseline updated. Use when user invokes /robobuilder:upgrade or when they ask "is robobuilder up to date?".
---

# /robobuilder:upgrade

## What
Upgrades robobuilder to the latest version from the official Roboco-op GitHub repo. Shows a diff preview before applying.

## When
- User wants to pick up the latest team-curated skills, agents, or baseline CLAUDE.md
- After a teammate announces a new skill landed
- Quarterly check-in to stay current

## Why
Without a controlled upgrade flow, the team fragments: some on old skill versions, some on new. The Living Knowledge Loop (Notion ↔ skills) only works if everyone is roughly synchronized.

## How

### Step 1 — Detect current version

Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` → `version` field.

### Step 2 — Fetch latest

```bash
git -C "${CLAUDE_PLUGIN_ROOT}" fetch origin
LATEST=$(git -C "${CLAUDE_PLUGIN_ROOT}" describe --tags --abbrev=0 origin/main 2>/dev/null || \
         git -C "${CLAUDE_PLUGIN_ROOT}" rev-parse --short origin/main)
```

If latest == current: print "Already on the latest version (vX.Y.Z)" and exit.

### Step 3 — Preview diff

Show:
- Skills changed (added / modified / removed)
- Agents changed
- Hook config changed
- `CLAUDE.md.baseline` changed
- `company.yaml` changed (rare)

```
robobuilder vX.Y.Z → vX.Y.Z+1
─────────────────────────────────────────
SKILLS
  + meta/new-skill (added)
  ~ phase3/tdd (modified)        [show diff]
  - phase5/old-skill (removed)
AGENTS
  ~ design-critic (modified)     [show diff]
HOOKS
  ~ hooks.json: added PreSubmit  [show diff]
BASELINE
  ~ CLAUDE.md.baseline: +12 -3   [show diff]
```

### Step 4 — Per-section approval

For each non-trivial change, prompt:
- `[Apply] [Skip] [Show full diff]`

User can apply selectively (e.g., skip baseline changes if they like their current CLAUDE.md).

### Step 5 — Apply

```bash
git -C "${CLAUDE_PLUGIN_ROOT}" pull --ff-only origin main
```

If applied changes include `CLAUDE.md.baseline`:
Prompt: "Baseline changed. Run /robobuilder:tune-claude-md now to re-merge? (y/n)"

### Step 6 — Post-upgrade

Print:
- New version
- CHANGELOG link
- Highlights from changes the user just accepted
- Reminder: "If anything broke, `git -C ${CLAUDE_PLUGIN_ROOT} reset --hard <prev-sha>`"

## Example

```
User: /robobuilder:upgrade
Claude: Current: v1.0.0
        Latest:  v1.0.2

  Changes:
    + meta/install-companions (added)
    ~ phase4/diff-review (modified — added cross-review handoff)
    ~ CLAUDE.md.baseline (+8 lines: subagent activation rules tightened)
    + agents/release-notes-writer.md (added)

  Review changes? (y/n)
User: y
[shows each diff, accepts each in turn]
Claude: Applied: v1.0.0 → v1.0.2
        Baseline changed. Run /robobuilder:tune-claude-md to re-merge? (y/n)
User: y
[invokes tune-claude-md skill via Skill tool]
```

## Anti-pattern
- Don't auto-apply without showing diffs (silent breakage is worse than out-of-date).
- Don't pull without `--ff-only` (merge commits in a plugin repo are confusing).
- Don't skip the tune-claude-md prompt if baseline changed — that's the whole point of the team baseline.

## See Also
- After this: `/robobuilder:tune-claude-md` (if baseline changed)
- Companion: `/robobuilder:install-companions <preset>`
- Bootcamp: M6.compounding-engineering
