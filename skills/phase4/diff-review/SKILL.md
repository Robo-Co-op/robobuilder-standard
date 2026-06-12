---
name: diff-review
description: "[P4-1 Review] Daily-driver diff review. Reviews the current branch's diff with 3 parallel subagents (code-simplifier / test-writer / security-auditor) and merges their findings into one prioritized fix list"
user-invocable: true
argument-hint: "[--base <branch>] override the target branch/commit range"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
origin: jin-custom
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase4)
> - **What**: Daily-driver diff review — 3 parallel subagents (simplification / tests / security) merged into one prioritized fix list.
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:cross-review, /robobuilder:grill, /robobuilder:playbook-review-deep
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /diff-review — 3-Agent Parallel Review

Review the current branch's diff (vs `main`) with **3 subagents running in parallel**.

## Steps
1. Get an overview with `git diff main...HEAD --stat` and `git diff main...HEAD`
2. Invoke the following **3 agents in parallel** (multiple Agent tool calls in a single message):
   - `code-simplifier` — redundancy, over-abstraction, naming
   - `test-writer` — missing test coverage
   - `security-auditor` — OWASP perspective
3. Merge the three outputs into a **prioritized fix list** at the end:
   ```
   ## Merged verdict
   ### Must fix (before merge)
   1. ...
   ### Should fix (recommended in this PR)
   1. ...
   ### Nice to have (can defer)
   1. ...
   ## One-liner: SHIP / FIX FIRST
   ```

`$ARGUMENTS` can override the target branch/commit range (e.g. `--base develop`).

$ARGUMENTS
