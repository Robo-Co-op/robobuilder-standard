---
name: grill
description: "[P4-3 Review] Adversarial review of the latest changes (diff). Interrogates the code mercilessly to expose oversights, false assumptions, and vulnerabilities — lists 5+ failure modes and ends with a SHIP / PATCH FIRST / REWRITE verdict"
user-invocable: true
argument-hint: "[target files/commit range]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
origin: jin-custom
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase4)
> - **What**: Adversarial review of the latest diff — expose oversights, false assumptions, and vulnerabilities.
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:diff-review, /robobuilder:cross-review, /robobuilder:grill-me
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /grill — Adversarial Review

Perform an **adversarial review** of the latest changes (`git diff`, or the target specified in `$ARGUMENTS`). No flattery. No mercy.

## What to do
1. **Question the assumptions** — enumerate everything this code implicitly assumes (environment, inputs, state) and devise an input that breaks each one
2. **Enumerate failure modes** — 5+ "this breaks it" scenarios (concurrency, network failure, partial failure, retries, null/undefined, empty arrays, exceeding limits)
3. **Verify the logic** — branch coverage, off-by-one, boundaries, race conditions
4. **Alternatives** — 1–2 "here's how I would write it" proposals, with reasons why they're better
5. **Side effects** — external state that changes when this code lands (DB, APIs, files, logs, billing, email sends)

## Output format
```
## Review target
## Implicit assumptions (break these and it breaks)
1. ...
2. ...
## Failure modes
1. [Critical] ...
2. [Medium] ...
## Logic concerns
- ...
## Alternatives
- Option A: ...
- Option B: ...
## Side effects
- ...
## One-word verdict: SHIP / PATCH FIRST / REWRITE
```

Do not defend the code. Criticism is what's being asked for. If you feel like saying "mostly fine," dig one level deeper.

$ARGUMENTS
