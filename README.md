# robobuilder

**Robo Co-op standard Claude Code dev plugin.**

One install gives every team member:
- 33 curated dev skills across 6 phases (Investigate → Design → Prototype → Implement → Refactor → Review → Ship)
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

```sh
/plugin marketplace add Robo-Co-op/robobuilder
/plugin install robobuilder@robo-coop-tools
/reload-plugins
```

On first install, run:

```sh
/robobuilder:start              # onboarding — points you to your first 3 skills
/robobuilder:tune-claude-md     # personalize your CLAUDE.md with Robo Co-op best practices
```

See `docs/INSTALL.md` for full setup including optional GStack binary compile (`browse`) and `cc-feature-radar` scheduled agent.

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

Full chart: `docs/WORKFLOW.md`. Decision tree: `docs/DECISION_FLOW.md`.

## Living Knowledge Loop

robobuilder skills link bidirectionally to the Bootcamp v3 Notion hub:

```
   Notion Bootcamp v3 (theory)
            ↕
   robobuilder skills (practice)
```

Updating Notion best-practice content immediately improves CC usage quality across the team — no plugin re-release needed. See `docs/BOOTCAMP_LINK.md`.

## Attribution

- 🟢 Matt Pocock — AI Engineering Skills (MIT)
- 🟠 Garry Tan — GStack (MIT)
- 🔵 Jin Kim — Robo Co-op custom skills

Full license in `LICENSE`.

## Contributing

Found a repeatable pattern? Use `/robobuilder:write-a-skill` to draft it, then open a PR in the Robo-Co-op org. See `docs/CONTRIBUTING.md`.
