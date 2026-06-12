---
name: blueprint-sync
description: "[Util-2] Keep design docs (PRD / DESIGN.md / ADRs / architecture docs) in sync with the implementation as you build. Diffs reality against the blueprint, classifies each divergence (stale doc / implementation violation / intentional pivot), and updates the docs so they stay living documents"
user-invocable: true
argument-hint: "[--since <ref>] commit range to compare; defaults to the last sync marker"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - Write
origin: robobuilder
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: Keep design docs in sync with the implementation as you build — diff reality vs blueprint, classify divergences, update the docs.
> - **When**: Whenever you notice the code drifting from the design; after completing a vertical slice; before review; as part of the ship checklist.
> - **See Also**: /robobuilder:to-prd, /robobuilder:tdd, /robobuilder:ship, /robobuilder:handoff
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (robobuilder original)


# /blueprint-sync — Keep the Blueprint Alive

As development progresses, the implementation inevitably diverges from the original design. A blueprint that nobody updates becomes a lie — worse than no blueprint at all. This skill makes design docs **living documents**: every time reality and blueprint disagree, resolve the disagreement explicitly, in the right direction.

Run it **during development, not just at the end**: after finishing a vertical slice, when you catch yourself implementing something the PRD doesn't describe, before a review round, or as part of the ship checklist.

## Steps

### 1. Locate the blueprints

Find the project's design artifacts. Look for (don't assume all exist):

- `PRD*.md`, `docs/prd/` — product requirements
- `DESIGN.md`, `docs/design/` — design system / technical design
- `docs/adr/` — architecture decision records
- `CONTEXT.md`, `CONTEXT-MAP.md` — domain language
- `ARCHITECTURE.md`, architecture diagrams (mermaid blocks in docs)

If no design docs exist at all, stop and tell the user — suggest `/robobuilder:to-prd` to create one first.

### 2. Diff reality vs blueprint

Determine the comparison range:

- If `$ARGUMENTS` contains `--since <ref>`, use that
- Else look for the last sync marker (`<!-- blueprint-sync: <commit-sha> <date> -->` at the bottom of each design doc)
- Else fall back to the merge-base with the default branch

Then read the implementation changes in that range (`git log --stat`, `git diff`) and compare against what the blueprint says. For each design doc section that touches changed code, ask: *does the doc still describe what the code actually does?*

### 3. Classify each divergence

For every disagreement found, classify it — this is the core judgment of the skill:

| Class | Meaning | Action |
|---|---|---|
| **(a) Stale doc** | The implementation is right; the design is outdated | Update the design doc to match reality |
| **(b) Implementation violation** | The design is right; the code drifted incorrectly | Flag it — do NOT silently change the doc. File an issue (or list it for the user) |
| **(c) Intentional pivot** | The direction changed on purpose during development | Update the design doc AND record the decision as an ADR entry (what changed, why, when) |

When unsure which class a divergence belongs to, ask the user — never guess between (a) and (b); they point in opposite directions.

### 4. Apply

1. Present the full divergence list with proposed classifications and doc edits
2. On approval: apply the doc edits, write ADR entries for class (c), file/record issues for class (b)
3. Stamp each touched design doc with a fresh sync marker: `<!-- blueprint-sync: <HEAD-sha> <YYYY-MM-DD> -->`

## Output format

```
## Blueprint sync — <range>
### Divergences found: N
1. [stale-doc] DESIGN.md §Auth — doc says session cookies, code uses JWT → doc updated
2. [violation] PRD §Rate limits — code skips limit on admin route → issue filed
3. [pivot] ADR-0007 added — switched queue from Redis to SQS (2026-06-12)
### Docs updated: ...
### Issues filed: ...
### Sync marker: <sha>
```

## Anti-patterns

- **Doc-only sync at release time** — by then nobody remembers *why* the code diverged. Sync while the context is fresh
- **Silently "fixing" the doc for a class (b) violation** — that launders a bug into a spec
- **Rewriting the whole design doc** — touch only the sections that diverged; the blueprint's history should stay readable

$ARGUMENTS
