# RoboBuilder on Claude Code (web)

Claude Code on the web (claude.ai/code) is a separate runtime from the local CLI.
The plugin-marketplace flow in [INSTALL.md](./INSTALL.md) (`/plugin marketplace add`
+ `/plugin install`) assumes a local `~/.claude/plugins/` directory and does **not**
carry over to web sessions. Two things actually work there:

## Option 1: Commit skills into the repo (per-project, most reliable)

A web session clones your repo and reads `.claude/skills/` (and `.claude/agents/`)
from whichever branch it actually checks out — normally the repo's default branch.

1. Copy the skill(s) you want from `skills/<phase>/<name>/SKILL.md` into your
   project repo under `.claude/skills/<name>/SKILL.md` (and `.claude/agents/` for
   any agents the skill uses).
2. Commit and merge to the **default branch**. Skills on a feature branch are
   invisible to a fresh web session until that branch is merged — a PR sitting
   open is not enough.
3. Start a new web session on the project; the skill appears in the skill list
   immediately, no `/reload-plugins` equivalent needed.

This is scoped to that one repo. For multiple projects, repeat per repo, or see
Option 2.

## Option 2: Register as an account-level skill (works across all projects)

claude.ai's **Customize > スキル (Skills) > 追加 > スキルの指示を記述** flow
creates a skill tied to your account rather than a repo, and it **is** picked up
by Claude Code web sessions (confirmed 2026-07-18 — this was previously assumed
to be a Desktop/Cowork-only feature; it is not).

1. Open a `SKILL.md`, and split its frontmatter `description` and body into the
   form's **説明** (description) and **手順** (instructions) fields.
2. Drop references to `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}`,
   `bin/robobuilder-*`, and sibling doc files (`LANGUAGE.md`, `AGENT-BRIEF.md`,
   etc.) — none of those exist outside the plugin, so the standalone skill
   should be self-contained prose.
3. If the source `SKILL.md` is large (the textarea has practical limits well
   under some skills' size, e.g. `ship.md` at 120K+ chars), condense to the
   essential process/decision-logic/anti-patterns rather than pasting verbatim.
4. **Name collisions return HTTP 400** ("This skill name is already in use") —
   this includes reserved words (a name containing the literal word `claude` is
   rejected) and collisions with any other skill already registered to the
   account (including a different RoboBuilder edition's same-named skill, e.g.
   Lite's `ship` vs Standard's `ship`). Rename defensively when this happens
   (`ship` → `robobuilder-ship`, `tune-claude-md` → `tune-agents-md`, etc.) and
   keep a note of the renames somewhere your team can find them.
5. This is a manual, one-skill-at-a-time process — there's no bulk import from a
   plugin today, so it does not scale as gracefully as Option 1 for a whole
   edition's worth of skills.

## Which to use

- Working in one repo, want the team on the same skills → Option 1 (commit to
  the repo).
- Want a personal skill available across every project you open in Claude Code
  web → Option 2 (account-level).
- Either way, `/robobuilder:*`-style slash-command namespacing does not apply
  outside the plugin system — invoke by the skill's bare name in both cases.
