# robobuilder (Standard edition)

**Robo Co-op standard development skill system.**

Primary distribution is a Claude Code plugin. The same skill source can also be
exported as an OpenClaw/Codex skill pack.

## Three editions

| Edition | Repo | Who it's for | Contents |
|---|---|---|---|
| **Lite** | [robobuilder-lite](https://github.com/Robo-Co-op/robobuilder-lite) | Beginners — learn the workflow with 4 commands | 4 merged mega-skills (`plan` / `build` / `improve` / `ship`) + the same hooks and review agents |
| **Standard** (this repo) | [robobuilder-standard](https://github.com/Robo-Co-op/robobuilder-standard) | Daily development | 41 skills / 9 agents / 6 hooks / 3 playbooks |
| **Pro** | [robobuilder-pro](https://github.com/Robo-Co-op/robobuilder-pro) | Loop Engineering — autonomous agent loops | Add-on installed **alongside Standard**: design, gate, audit, and compound loops built on native `/goal`, `/loop`, `/batch`, and Routines |

Standard covers the inner loop (L1 agent loop + L2 verification: tdd / diagnose / review).
Pro adds the outer loop (L3 event-driven + L4 self-improving loops). Lite is the on-ramp to Standard.

One install gives every team member:
- 41 curated dev skills across 6 phases (Investigate → Design → Prototype → Implement → Refactor → Review → Ship)
- 9 phase-specific subagents
- 3 multi-skill playbooks
- An onboarding wizard, a CLAUDE.md tuning wizard, and a semver upgrade flow
- Robo Co-op intelligence layer (`company.yaml`) — Teams / Asana / Notion / 1Password / Vercel / Supabase / Stripe / Azure SQL
- Hooks for 6 lifecycle events (SessionStart / PreToolUse / PostToolUse / Notification / PreCompact / SessionEnd)
- Bidirectional link to Bootcamp v3 in Notion — updating Notion immediately improves CC usage quality

## What this plugin is

A meta-curation of three upstream skill packs (Matt Pocock 🟢, GStack 🟠, Jin Custom 🔵) plus new robobuilder-original meta-skills, deduplicated and reorganized around the 6-phase Robo Co-op dev workflow.

Every skill follows a uniform 7-section pedagogical format (What / When / Why / How / Example / Anti-pattern / See Also) so it doubles as training material.

## What this plugin is NOT

Not knowledge-work skills (PPTx, docx, sales, brand-voice, etc.) — install those separately via `/robobuilder:install-companions <preset>` (see `docs/COMPANION_SKILLS.md`).

Not personal-projects scaffolding — use Skill Creator for one-off skills you discover yourself.

## Install

### Claude Code

```sh
/plugin marketplace add Robo-Co-op/robobuilder-standard
/plugin install robobuilder@robo-coop-tools
/reload-plugins
```

On first install, run:

```sh
/robobuilder:start              # onboarding — points you to your first 3 skills
/robobuilder:tune-claude-md     # personalize your CLAUDE.md with Robo Co-op best practices
```

See `docs/INSTALL.md` for full setup including the optional robobuilder feature radar routine.

### OpenClaw / Codex

Generate and install adapter skills:

```sh
python3 scripts/export_openclaw_codex_skills.py \
  --target ~/.openclaw/skills \
  --replace-existing
```

For Codex, use `--target "${CODEX_HOME:-$HOME/.codex}/skills"` instead.

See `docs/OPENCLAW_CODEX.md`.

### Claude Desktop

See `docs/CLAUDE_DESKTOP.md` for MCP bridge setup, Projects-based usage, and feature comparison across all versions.

## Quick reference

| Goal | Skill |
|---|---|
| Start a session | `/robobuilder:start` |
| Quick question | `/robobuilder:btw` |
| New feature | `/robobuilder:playbook-new-feature` |
| Bug fix | `/robobuilder:playbook-bug-fix` |
| Deep review | `/robobuilder:playbook-review-deep` |
| Ship it | `/robobuilder:ship` → `/robobuilder:land-and-deploy` → `/robobuilder:canary` |
| End session | `/robobuilder:handoff` |

Full chart: `docs/WORKFLOW.md`. Decision tree: `docs/DECISION_FLOW.md`. Runtime helper contract: `docs/RUNTIME.md`.

## All 41 skills, in workflow order

Every skill description starts with a phase tag (e.g. `[P1-1 Design]`) so the alphabetical `/plugin` list still reads in workflow order. Within each phase, skills are ordered by practical usage order and frequency.

| Phase | Skills (in order) |
|---|---|
| Meta | `start` → `tune-claude-md` → `upgrade` → `install-companions` |
| P0 Foundation | `setup` → `ubiquitous-language` |
| P0.5 Investigate | `zoom-out` → `diagnose` → `health` |
| P1 Design | `grill-me` → `grill-with-docs` → `design-an-interface` → `plan-eng-review` → `to-prd` → `to-issues` |
| P2 Prototype | `prototype` |
| P3 Implement | `triage` → `tdd` → `caveman` → `browse` → `learn` |
| P3.5 Refactor | `improve-codebase-architecture` → `request-refactor-plan` |
| P4 Review | `diff-review` → `cross-review` → `grill` → `cso` |
| P5 Ship | `ship` → `land-and-deploy` → `canary` → `handoff` → `write-a-skill` |
| Utilities | `guard` → `blueprint-sync` → `context-save` → `context-restore` → `btw` → `export` |
| Playbooks | `playbook-new-feature` → `playbook-bug-fix` → `playbook-review-deep` |

## Living Knowledge Loop

robobuilder skills link bidirectionally to the Bootcamp v3 Notion hub:

```
   Notion Bootcamp v3 (theory)
            ↕
   robobuilder skills (practice)
```

Updating Notion best-practice content immediately improves CC usage quality across the team — no plugin re-release needed. See `docs/BOOTCAMP_LINK.md`.

## Attribution

- 🟢 Matt Pocock — [mattpocock/skills](https://github.com/mattpocock/skills) (MIT)
- 🟠 Garry Tan — [garrytan/gstack](https://github.com/garrytan/gstack) (MIT)
- 🔵 Jin Kim — Robo Co-op custom skills

Full license in `LICENSE`.

## Contributing

Found a repeatable pattern? Use `/robobuilder:write-a-skill` to draft it, then open a PR in the Robo-Co-op org. See `docs/CONTRIBUTING.md`.
