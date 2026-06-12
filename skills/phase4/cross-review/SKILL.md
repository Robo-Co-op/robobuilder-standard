---
name: cross-review
description: "[P4-2 Review] AI cross-review — multi-round parallel review with 4 perspectives that keeps iterating until zero findings (0 critical + 0 medium for 2 consecutive rounds, max 5 rounds). Expensive; use only before important merges"
user-invocable: true
argument-hint: "[target branch/commit range]"
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
> - **What**: Multi-round parallel review with 4 perspectives — iterate fix-and-review rounds until zero findings.
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:diff-review, /robobuilder:grill
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /cross-review — Multi-Round Multi-Perspective Review

The heavyweight version of `/diff-review`. Its defining trait: **keep running rounds until there are zero findings**.

## Steps

### Round 0: Situation check
- `git diff main...HEAD --stat`
- Confirm the list of affected files and the scale of the change

### Rounds 1–N: Parallel review → fix → re-review
In each round, invoke the following subagents **in parallel**:
1. `code-simplifier` — redundancy, abstraction, naming
2. `test-writer` — missing tests
3. `security-auditor` — OWASP
4. (optional) `e2e-tester` — only for UI features

Aggregate the agents' outputs:
- **Critical** → fix immediately, then start the next round
- **Medium** → fix, then start the next round
- **Minor** → record this round; may carry over to the final verdict

### Exit condition
- 0 critical AND 0 medium findings for **2 consecutive rounds**
- Or cut off at a maximum of 5 rounds (beyond that it diverges)

## Output (after the final round)
```
## Total rounds: N
## Total findings: X
- Critical: A → all resolved
- Medium: B → all resolved
- Minor: C → left as-is (list)
## Final verdict: SHIP / FIX FIRST
## Learnings
- Failure patterns repeated this time (apply next time)
```

## Notes
- Do **not** treat round count or finding count as KPIs. Fewer is better
- If the same finding persists for 3+ rounds, suspect a reviewer-side false positive
- This skill is expensive. Use it only before important merges

$ARGUMENTS
