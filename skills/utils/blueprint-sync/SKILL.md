---
name: blueprint-sync
version: 1.0.0
description: |
  [Util-2] Detects drift between the codebase and its design documents (PRD, architecture docs,
  ADRs, README), then updates or creates docs to reflect reality. Use when: code has
  drifted from the blueprint, after landing a big feature, running a retrospective after
  ship, or maintaining living documentation. Modes: drift-check (detect gaps),
  update-docs (fix docs), retrospective (post-ship review + doc update),
  living-doc (lightweight incremental update).
user-invocable: true
argument-hint: "[drift-check|update-docs|retrospective|living-doc]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
preamble-tier: 3
origin: robobuilder
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: Keep design docs in sync with the implementation as you build — detect drift, classify it, update the docs.
> - **When**: Whenever you notice the code drifting from the design; after landing a slice or feature; post-ship retrospective; whenever docs feel stale.
> - **See Also**: /robobuilder:to-prd, /robobuilder:tdd, /robobuilder:ship, /robobuilder:handoff
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (robobuilder original)


# Blueprint Sync

Keeps your design documents honest. As code evolves, blueprints drift. This skill detects the gap and closes it.

---

## Modes

| Mode | When to use |
|------|-------------|
| `drift-check` | Audit how far docs have drifted from the code |
| `update-docs` | Rewrite/update docs to match current reality |
| `retrospective` | Post-ship: reflect on what changed + update docs |
| `living-doc` | After a small PR: lightweight one-pass doc touch |

If no mode is specified, auto-detect from context:
- After `/ship` → `retrospective`
- User says "update docs" / "docs are stale" → `update-docs`
- User says "what's drifted" / "is the design up to date" → `drift-check`
- Small PR just landed → `living-doc`

---

## Step 0: Discover documents

Locate all design artifacts in the repo:

```bash
# Find candidate documents
find . -maxdepth 4 \( \
  -name "PRD.md" -o -name "ARCHITECTURE.md" -o -name "DESIGN.md" \
  -o -name "README.md" -o -name "BLUEPRINT.md" -o -name "SPEC.md" \
  -o -name "DECISIONS.md" -o -name "CHANGELOG.md" \
  -o -iname "*.adr.md" \
\) \
  ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null
```

Also check for an `docs/` or `design/` directory:

```bash
ls docs/ design/ 2>/dev/null | head -20
```

If no documents found → print "No design documents found. Create a PRD first with `robobuilder-to-prd`, or create `ARCHITECTURE.md` manually." Stop.

List the found documents with a one-line summary of each (first non-empty heading or first sentence).

---

## Mode: drift-check

### 1. Snapshot current code shape

```bash
# High-level structure
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.rb" -o -name "*.py" -o -name "*.go" \) \
  ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/dist/*" ! -path "*/.next/*" \
  | sort | head -80

# API routes / endpoints
grep -rE "(get|post|put|patch|delete)\s*\(" --include="*.ts" --include="*.rb" --include="*.py" \
  -l 2>/dev/null | head -20

# Data models / schemas
find . -name "schema.prisma" -o -name "schema.rb" -o -name "models.py" \
  ! -path "*/node_modules/*" 2>/dev/null | head -10
```

### 2. Read each design document

For each document found in Step 0, read it fully (or the first 200 lines if long).

### 3. Compare and classify drift

For each document, identify drift across these categories:

**Structural drift** — code exists that the doc doesn't mention:
- New modules, services, or directories
- New API routes or endpoints
- New data models or DB tables
- Removed components still described in docs

**Terminology drift** — names in docs don't match code:
- Class/function names renamed
- Concept renamed (e.g., "User" → "Account")
- Architecture pattern changed

**Flow drift** — described flows no longer match implementation:
- Auth flow changed
- Data pipeline changed
- Integration points changed

**Decision drift** — ADRs or design decisions overridden without record:
- Chose X in the doc, implemented Y
- Constraint mentioned in doc no longer applies

Then decide the **resolution direction** for each drift item — this is the core judgment:

| Direction | Meaning | Action |
|---|---|---|
| **stale-doc** | The implementation is right; the design is outdated | Update the design doc to match reality |
| **violation** | The design is right; the code drifted incorrectly | Flag it — do NOT silently change the doc. File an issue (or list it for the user) |
| **pivot** | The direction changed on purpose during development | Update the design doc AND record the decision as an ADR entry (what changed, why, when) |

When unsure between **stale-doc** and **violation**, ask the user — never guess; they point in opposite directions. Silently "fixing" the doc for a violation launders a bug into a spec.

### 4. Output drift report

```
BLUEPRINT DRIFT REPORT
══════════════════════════════════════════════════
Repo: {repo name}  |  Checked: {date}

ARCHITECTURE.md
  [DRIFT] Section "Authentication" describes JWT — code uses sessions (Devise)
  [DRIFT] "Redis queue" mentioned — Sidekiq jobs found instead
  [NEW]   app/services/billing/ — not documented anywhere
  [CLEAN] Database schema section matches schema.rb

PRD.md
  [STALE] Feature "Dashboard v2" described — not found in codebase
  [NEW]   /api/webhooks endpoint — not in PRD scope
  [CLEAN] Core user flows match implementation

README.md
  [DRIFT] Setup instructions reference .env.example — file doesn't exist
  [CLEAN] Tech stack section accurate

──────────────────────────────────────────────────
SUMMARY: 5 drift items, 3 new gaps, 3 clean sections
RECOMMENDATION: Run `blueprint-sync update-docs` to fix.
══════════════════════════════════════════════════
```

---

## Mode: update-docs

### 1. Run drift-check first (if not already done)

Get the full drift report. Confirm with user before making changes:

> "I found N drift items. I'll update the docs to match the current code.
> Docs I'll update: {list}
> A) Proceed  B) Review each change before applying  C) Cancel"

### 2. For each document with drift

Read the full doc. For each drift item:

- **[DRIFT]** — update the section to match current code reality
- **[STALE]** — either remove or move to an "Out of scope / History" section
- **[NEW]** — add a new section documenting the undocumented component

When writing updates:
- Match the document's existing tone and format
- Don't rewrite sections that are still accurate — surgical edits only
- Add a `<!-- last-synced: {date} by blueprint-sync -->` comment after updated sections

### 3. Commit

```bash
git add {changed doc files}
git commit -m "docs: sync blueprint with current implementation

Updated by robobuilder-blueprint-sync.
Drift items resolved: {N}
New sections added: {M}"
```

### 4. Output summary

```
DOCS UPDATED
────────────────────────────────
ARCHITECTURE.md  — 2 sections updated, 1 added
PRD.md           — 1 stale feature archived, 1 new endpoint added
README.md        — setup instructions corrected

Committed: docs: sync blueprint with current implementation
```

---

## Mode: retrospective

Run after `/ship`. Reviews what shipped vs what was planned, then updates docs.

### 1. What shipped?

```bash
# Get the diff vs base branch
git log --oneline -20
git diff origin/main --stat 2>/dev/null | tail -20
```

### 2. What was planned?

Read PRD.md and/or ARCHITECTURE.md. Identify the relevant sections for the shipped work.

### 3. Retrospective questions

For each significant change in the diff, ask:

- Did this match what the design doc described?
- Did we discover new constraints during implementation?
- Did we make a different architectural choice than planned? (→ log as ADR)
- Does anything in the docs now mislead a future reader?

### 4. Update docs

Apply updates same as `update-docs` mode.

### 5. Optionally create ADR

If a significant design decision was made during implementation that diverged from the plan:

```markdown
# ADR-{N}: {Decision title}

**Date:** {date}
**Status:** Accepted

## Context
{What was originally planned, what changed during implementation}

## Decision
{What we decided and why}

## Consequences
{Trade-offs and follow-up work}
```

Write to `docs/decisions/ADR-{N}.md` or `DECISIONS.md`.

---

## Mode: living-doc

Lightweight mode for small PRs. One pass, minimal changes.

### 1. Get the PR diff

```bash
git diff origin/main --name-only 2>/dev/null | head -30
git diff origin/main --stat 2>/dev/null | tail -5
```

### 2. Check if any changed component is documented

For each changed file, search the docs:

```bash
# Check if the changed filename/module is mentioned in docs
grep -r "{module_name}" docs/ README.md ARCHITECTURE.md 2>/dev/null | head -10
```

### 3. Apply minimal updates

Only update if there's a clear mismatch. Don't rewrite — just patch:
- Update a version number, a component name, a config example
- Add a one-liner about a new module if docs have a relevant section

### 4. If nothing needs updating

Print: "Docs are current for this change. No update needed."

---

## Integration with /ship

When called from `/ship` retrospective mode, insert after Step 19 (PR created):

```
Blueprint Sync (retrospective):
  Drift items found: {N}
  Docs updated: {list or "none"}
  ADRs created: {list or "none"}
```

Add to PR body:
```markdown
## Documentation
{docs updated or "No doc updates needed"}
```

---

## Tips

- Run `drift-check` at the start of a major sprint to see accumulated debt
- Run `retrospective` after every `/ship` — it's the lightest habit with the biggest payoff
- Run `update-docs` when onboarding someone new (fresh eyes will hit the stale docs hardest)
- Keep ADRs for any "we tried X but switched to Y" decisions — future you will thank you
