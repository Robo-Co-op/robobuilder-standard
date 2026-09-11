# robobuilder (Standard edition)

**Robo Co-op standard development skill system.**

Primary distribution is a Claude Code plugin. The same skill source can also be
exported as an OpenClaw/Codex skill pack.

## Three editions

| Edition | Repo | Who it's for | Contents |
|---|---|---|---|
| **Lite** | [robobuilder-lite](https://github.com/Robo-Co-op/robobuilder-lite) | Beginners — learn the workflow with 4 commands | 4 merged mega-skills (`plan` / `build` / `improve` / `ship`) + the same hooks and review agents |
| **Standard** (this repo) | [robobuilder-standard](https://github.com/Robo-Co-op/robobuilder-standard) | Daily development | 41 skills / 9 agents / 6 hooks / 3 playbooks |
| **Pro** | [robobuilder-pro](https://github.com/Robo-Co-op/robobuilder-pro) | Loop & Graph Engineering — autonomous agent loops | Add-on installed **alongside Standard**: design, gate, audit, and compound loops built on native `/goal`, `/loop`, `/batch`, and Routines — then wire them into a graph with typed edges, arbitration, and champion-challenger promotion |

Standard covers the inner loop (L1 agent loop + L2 verification: tdd / diagnose / review).
Pro adds the outer loop (L3 event-driven + L4 self-improving loops), and above it L5 — a
*graph* of loops, where reliability lives in the edges: who watches whom, who can veto whom.
Lite is the on-ramp to Standard.

## The operating system above the editions

The three editions are the **toolbox** — *how* work gets done. *What must be true before work is
allowed to move forward* is defined once, for every Robo Co-op repository, in
**[robobuilder-os](https://github.com/Robo-Co-op/robobuilder-os)**.

> **Robo Builder = HOW.  Robo Builder OS = MUST / WHEN / DONE.**

Every project travels the same spine, and each state has to leave evidence behind before the next
one may begin:

```
DEFINE -> DESIGN -> ISSUE -> BRANCH -> TEST -> BUILD -> REVIEW -> STAGE -> DEPLOY -> VERIFY -> OPERATE
```

| This repo's workflow | OS state |
|---|---|
| Foundation / Investigate | DEFINE |
| Design, Prototype | DESIGN |
| Plan → issues | ISSUE |
| Implement (TDD) | BRANCH, TEST, BUILD |
| Refactor | BUILD |
| Review (`/diff-review`, `/cross-review`) | REVIEW |
| Ship | STAGE, DEPLOY, VERIFY |

Four gates block the transitions that matter: Definition of Ready, Merge Gate, Production Gate,
Definition of Done.

A repository declares which OS version it follows by copying
`robobuilder-os/templates/AGENTS.md` into its root. Coding standards stay here in
`CLAUDE.md.baseline`; lifecycle rules and gates live in the OS. If a rule is about taste, it
belongs in this repo — if it decides whether a change may advance, it belongs in the OS.

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

### Update

Installing tells you nothing about how to get the next version, and that gap is not
theoretical: a change can sit merged on `main` for days while every teammate still runs
the old skill, because nothing about their setup looks wrong.

```sh
/plugin marketplace update robo-coop-tools
/plugin update robobuilder@robo-coop-tools
/reload-plugins
```

Check it actually landed — the version in `/plugin` should match the top entry of this
repo's `CHANGELOG.md`. If it doesn't, the marketplace cache is stale, not you.

Two things that bite:

- **`/plugin` is CLI-only.** It does not exist in the web or desktop app. Those pick up
  skills through account-level registration instead.
- **A running session keeps the version it started with.** Plugins are snapshotted when
  the session opens, so `/reload-plugins` or a new session is required — updating the
  files under `~/.claude/plugins/` mid-session does not change what the current session
  reads.

If your copy under `~/.claude/plugins/<name>/` is a plain `git clone` rather than a
marketplace install, `/plugin update` will not touch it. Run `git pull` in that
directory instead, then `/reload-plugins`.

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

### Desktop app & Claude Code on the web

`/plugin` is terminal-CLI only — elsewhere it reports "isn't available in this
environment". Use the desktop app's plugin browser, or declare the plugin in
`.claude/settings.json`. See `docs/CLAUDE_CODE_WEB.md`.

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

## GitHub ↔ Asana Sync

EN: A GitHub repo's issues and an Asana project's tasks can link bidirectionally too — opening,
closing, and reopening an issue drives the task; completing the task in Asana closes the issue
back (polled, since most repos have no hosted webhook receiver).

JP: GitHub リポジトリの Issue と Asana プロジェクトのタスクも双方向にリンクできます — Issue の
オープン・クローズ・再オープンがタスクに反映され、Asana でタスクを完了にすると Issue もクローズされます
（多くのリポジトリにはホスティングされた Webhook 受信環境がないため、ポーリング方式です）。

```
   GitHub Issues (source of truth)
            ↕
   Asana tasks (stakeholder mirror)
```

Reference implementation: `Robo-Co-op/RoboDesk`. See `docs/GITHUB_ASANA_SYNC.md` for the full
adoption playbook.

## Attribution

- 🟢 Matt Pocock — [mattpocock/skills](https://github.com/mattpocock/skills) (MIT)
- 🟠 Garry Tan — [garrytan/gstack](https://github.com/garrytan/gstack) (MIT)
- 🔵 Jin Kim — Robo Co-op custom skills

Full license in `LICENSE`.

## Contributing

Found a repeatable pattern? Use `/robobuilder:write-a-skill` to draft it, then open a PR in the Robo-Co-op org. See `docs/CONTRIBUTING.md`.
