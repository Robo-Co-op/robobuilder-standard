---
name: tune-claude-md
description: "[Meta-2] Personalize the user's ~/.claude/CLAUDE.md by intelligently merging it with the Robo Co-op best-practice baseline. Classifies each baseline section as UPGRADE / KEEP / ADD, prompts for confirmation, backs up the original, and applies. Use when user invokes /robobuilder:tune-claude-md, after plugin install, or after plugin upgrade."
origin: robobuilder
---

# /robobuilder:tune-claude-md

## What
Interactive wizard that takes the Robo Co-op best-practice CLAUDE.md baseline (shipped with this plugin) and merges it into the user's existing `~/.claude/CLAUDE.md`, preserving personal/environment-specific entries.

## When
- First-time setup, right after `/robobuilder:start`
- After every `/robobuilder:upgrade` (baseline may have changed)
- When user senses their CLAUDE.md is stale or duplicating best practices already in robobuilder

## Why
A team-wide CLAUDE.md baseline ensures Claude behaves consistently across all Robo Co-op members. But individual members have personal paths, VPS IPs, vault names, etc. that must NOT be replaced. The wizard is the conflict-safe merge that preserves both.

## How

### Step 1 — Load both files
```
USER_FILE = ~/.claude/CLAUDE.md (or .codex/AGENTS.md, .cursor/rules — detect by env)
BASELINE  = ${CLAUDE_PLUGIN_ROOT}/CLAUDE.md.baseline
```

If `USER_FILE` does not exist: skip to Step 5 with `BASELINE` as the new file.

### Step 2 — Auto-classify into 3 buckets

Read both files. For each meaningful section/rule, classify:

**Bucket A — UPGRADE** (baseline supersedes user's current)
- User has older/weaker version of a baseline rule
- User's wording is redundant or wordy where baseline is concise
- User missing a deprecation note that baseline has

**Bucket B — KEEP** (preserve user's, do not touch)
- Concrete paths (`C:/Users/...`, nexus paths, `~/.claude/projects/`)
- IP addresses (VPS, internal services)
- Personal vault names (1Password vault paths)
- Email addresses
- Project-specific rules not in baseline (EA eval, AZTK MC, specific MCP servers)
- Custom hooks or skill references

**Bucket C — ADD** (baseline has knowledge user lacks)
- New best practices added to baseline since last tune
- New hook patterns
- New subagent activation rules

### Step 3 — Interactive confirmation

Present to user as a structured diff:

```
┌─ UPGRADE PROPOSALS (3) ─────────────────────────────────────
│ A1. "Coding standards" section — baseline has tighter ESM rules
│     [Show diff]
│     [Accept] [Skip] [Edit]
│ A2. ...
└──────────────────────────────────────────────────────────────

┌─ KEEP (these stay as-is — confirming for your awareness) ────
│ B1. VPS IP: 165.22.55.193
│ B2. Nexus path: C:/Users/jinta/nexus/
│ B3. EA evaluation rules (project-specific)
└──────────────────────────────────────────────────────────────

┌─ ADD PROPOSALS (2) ──────────────────────────────────────────
│ C1. "Feature Adoption Loop" section (new in baseline)
│     [Show preview]
│     [Add] [Skip]
│ C2. ...
└──────────────────────────────────────────────────────────────
```

Wait for user response on each A and C item. B items are read-only confirmation.

### Step 4 — Generate merged file

Write proposed merge to `~/.claude/CLAUDE.md.proposed`.
Show final diff vs `~/.claude/CLAUDE.md`.
Ask: "Apply this merge? (y/n)"

### Step 5 — Apply

If approved:
1. Move current `~/.claude/CLAUDE.md` → `~/.claude/CLAUDE.md.bak.YYYYMMDD-HHMMSS`
2. Move `~/.claude/CLAUDE.md.proposed` → `~/.claude/CLAUDE.md`
3. Print: "Revert anytime with `/robobuilder:tune-claude-md --revert`"

### --revert flag

Lists all `~/.claude/CLAUDE.md.bak.*` backups. User picks one. Swap back.

## Example

```
User: /robobuilder:tune-claude-md
Claude: Loading...
  USER:     ~/.claude/CLAUDE.md (217 lines)
  BASELINE: robobuilder CLAUDE.md.baseline (134 lines)

  Classifying differences...

  UPGRADE proposals: 3
  KEEP (preserve as-is): 8 (paths, IPs, vault names, EA rules)
  ADD proposals: 2

  Reviewing UPGRADE A1: "Coding standards"
  --- Your version (line 23-29) ---
  > JavaScript: use ES modules, ESLint
  > TypeScript: avoid any
  --- Baseline ---
  > JavaScript/TypeScript: ESM only. Use `unknown` over `any`.
  > Follow ESLint config in repo root.

  Accept this upgrade? (y/n/edit)
User: y
[...continues for A2, A3, C1, C2...]
Claude: Final diff:
  +14 lines (mostly ADD section "Feature Adoption Loop")
  -8 lines (consolidated wording in A1, A2)
  Preserved: 8 personal entries untouched

  Apply? (y/n)
User: y
Claude: Backup: ~/.claude/CLAUDE.md.bak.20260511-1530
        Applied: ~/.claude/CLAUDE.md
        Revert with: /robobuilder:tune-claude-md --revert
```

## Anti-pattern
- Never silently overwrite. Every UPGRADE and ADD requires explicit user approval.
- Never touch bucket B even if it looks duplicative — those are personal.
- Don't classify ambiguous sections as UPGRADE; default to KEEP if uncertain.

## See Also
- Trigger this after: `/robobuilder:start`, `/robobuilder:upgrade`
- Baseline file: `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md.baseline`
- Bootcamp: M6.compounding-engineering
