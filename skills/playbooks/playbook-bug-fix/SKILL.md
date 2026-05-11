---
name: playbook-bug-fix
description: Orchestrates a clean bug-fix workflow by invoking robobuilder skills in sequence. Steps diagnose → tdd → diff-review → ship. Use when user reports a bug and wants the guided fix flow rather than piecing it together.
---

# /robobuilder:playbook-bug-fix

## What
Guided bug-fix flow that enforces "reproduce first, fix second, regression test always."

## When
- User reports a bug (in code, in prod, in test)
- Bug is non-trivial — needs reproduction + investigation before patching
- Team wants consistent bug-fix discipline

Skip the playbook for trivial typo fixes; just edit directly.

## Why
Bugs without regression tests come back. Bugs without diagnosis get the symptom patched, not the cause. This playbook enforces both.

## How

### Step 1 — Diagnose
Invoke `/robobuilder:diagnose` via Skill tool.
Goal: reproduce the bug, minimize the trigger, form a hypothesis, instrument to confirm.

If diagnose fails 3 times: invoke `/gstack:investigate` as fallback (assumes gstack installed; otherwise re-run diagnose with fresh assumptions).

### Step 2 — Fix with regression test
Confirm: "Hypothesis confirmed. Move to /tdd to write the regression test first? (y/n)"
If y: invoke `/robobuilder:tdd`. The failing test must reproduce the bug. Then make it pass.

### Step 3 — Review
Confirm: "Run /diff-review on the fix? (y/n)"
If y: invoke `/robobuilder:diff-review`.

### Step 4 — Ship
Confirm: "Ship the fix? (y/n)"
If y: invoke `/robobuilder:ship`.

For prod bugs only: also recommend `/robobuilder:canary` post-deploy.

### Closing
Print summary. Recommend `/robobuilder:handoff` if the session was long, or `/robobuilder:btw` for follow-up notes.

## Example

```
User: /robobuilder:playbook-bug-fix
       Checkout flow throws 500 when cart has >10 items.
Claude: Bug-fix playbook. Step 1: /robobuilder:diagnose

[diagnose runs, identifies root cause: N+1 query in CartTotalCalculator]

Claude: Root cause confirmed (N+1 in CartTotalCalculator.summary()).
        Move to /tdd to write the regression test? (y/n)
User: y
[tdd runs: writes failing test for cart with 15 items, makes it pass]

Claude: Test green. Run /diff-review on the fix? (y/n)
User: y
[diff-review runs, 3 agents approve]

Claude: Ship the fix? (y/n)
User: y
[ship runs]

Claude: Done. Prod bug? Run /robobuilder:canary to monitor.
```

## Anti-pattern
- Don't skip Step 1 even if you "know" the cause. Diagnosis often reveals related bugs.
- Don't write the fix before the failing test (Step 2 is `/tdd`, not `/edit`).
- Don't ship without `/diff-review` even for one-line fixes.

## See Also
- Sibling: `/robobuilder:playbook-new-feature`, `/robobuilder:playbook-review-deep`
- Single skills: `/robobuilder:diagnose`, `/robobuilder:tdd`
- Bootcamp: M3.code.tdd + M3.code.diagnose
