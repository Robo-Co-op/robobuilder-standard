---
name: playbook-new-feature
description: Orchestrates the full new-feature workflow by invoking robobuilder skills in sequence via the Skill tool. Steps grill-me → to-prd → to-issues → tdd (parallel via Agent teams) → diff-review → cross-review → grill → ship. Use this when a user wants to build a new feature end-to-end and asks for the full flow rather than piecing it together.
---

# /robobuilder:playbook-new-feature

## What
End-to-end orchestrator for building a new feature. Invokes 8 skills in sequence, asking for user confirmation at each transition.

## When
- User says "I want to build X" and wants the full guided flow
- Team agreed on a feature and wants consistent execution across members
- Onboarding scenario where the user hasn't internalized the phase chart yet

Do NOT use when the user already knows which skill to invoke next — direct invocation is faster.

## Why
Playbooks turn the multi-skill workflow from "what do I do next?" into a guided sequence. Same flow → same quality → easier review across team members.

## How

This playbook is a skill that invokes other skills via the Skill tool. At each step, pause for user confirmation before proceeding.

### Step 1 — Clarify requirements
Invoke `/robobuilder:grill-me` via Skill tool.
Wait for completion (user has resolved ambiguity).

### Step 2 — Document as PRD
Confirm: "Move to PRD? (y/n/edit)"
If y: invoke `/robobuilder:to-prd`.

### Step 3 — Decompose into vertical-slice issues
Confirm: "Decompose to issues? (y/n)"
If y: invoke `/robobuilder:to-issues`.

### Step 4 — Implement (parallel TDD with Agent teams)
For each independent issue created in Step 3, recommend launching parallel agents:
- Use `Agent` tool with `isolation: "worktree"` for one agent per issue
- Each agent invokes `/robobuilder:tdd` on its assigned issue
- Heavy slices: offer `/codex:rescue`

This step is NOT automated — recommend the agents to spawn, then wait for the user to merge results.

### Step 5 — Daily diff review
Confirm: "Run /diff-review on the merged slices? (y/n)"
If y: invoke `/robobuilder:diff-review`.

### Step 6 — Critical merge review
Confirm: "Run /cross-review before merging to main? (y/n)"
If y: invoke `/robobuilder:cross-review`.

### Step 7 — Adversarial deepest review
Confirm: "Run /grill for final adversarial pass? (y/n)"
If y: invoke `/robobuilder:grill`.

### Step 8 — Ship
Confirm: "Ship it? (y/n)"
If y: invoke `/robobuilder:ship` → then suggest `/robobuilder:land-and-deploy` → then `/robobuilder:canary`.

### Closing
Print a summary of which steps ran, then:
"Session complete. `/robobuilder:handoff` will capture this for your future self."

## Example

```
User: /robobuilder:playbook-new-feature
Claude: New feature playbook. 8 steps. I'll pause between each.
        Starting Step 1: /robobuilder:grill-me

[grill-me runs to completion]

Claude: Step 1 done. Requirements clarified. Move to PRD? (y/n)
User: y
Claude: Invoking /robobuilder:to-prd

[continues through all 8 steps...]
```

## Anti-pattern
- Don't skip user confirmation between steps — that defeats the "guided" purpose.
- Don't try to parallelize Step 4 within this playbook — recommend Agent teams but let the user drive that explicitly.
- Don't run all 8 steps for a 1-hour task; playbook is for multi-session features.

## See Also
- Other playbooks: `/robobuilder:playbook-bug-fix`, `/robobuilder:playbook-review-deep`
- Manual mode: skip the playbook and invoke skills directly
- Bootcamp: M3.code (entire 7-layer flow)
