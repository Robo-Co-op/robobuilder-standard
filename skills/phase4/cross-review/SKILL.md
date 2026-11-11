---
name: cross-review
description: "[P4-2 Review] AI cross-review — multi-round parallel review with 4 perspectives that keeps iterating until zero findings (0 critical + 0 medium for 2 consecutive rounds; stop when rounds stop surfacing new defects, typically around five). Expensive; use only before important merges"
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
- Settle, once, whether this change renders — by running the check, not by recalling
  what the work felt like:

  ```sh
  git diff main...HEAD --name-only \
    | grep -qE '\.(html|css|scss|sass|less|tsx|jsx|vue|svelte|astro)$' && echo RENDERS
  ```

### Rounds 1–N: Parallel review → fix → re-review
In each round, invoke the following subagents **in parallel**, giving each one the
round's current diff (`git diff main...HEAD`, re-taken after the last round's fixes) in
its prompt rather than having it re-read the repo — as `/diff-review` does:
1. `code-simplifier` — redundancy, abstraction, naming
2. `test-writer` — missing tests
3. `security-auditor` — OWASP
4. `e2e-tester` — **in every round, once Round 0 printed `RENDERS`.** The first three
   read the change; this is the only one that opens it. The trigger is a fact about the
   diff rather than a call on whether the change "counts as UI", because that call
   belongs to the maker and comes back "not really" almost every time — which is how a
   five-round review still never renders the page.

   If it fires and cannot run — no dev server, no reachable URL, no browser — record
   `UNVERIFIED: rendered behaviour not checked (<reason>)` and carry it into every
   subsequent round and the final verdict. It is not a Minor finding and it does not
   age out: an unrun check is not a clean one.

Aggregate the agents' outputs:
- **Critical** → fix immediately, then start the next round
- **Medium** → fix, then start the next round
- **Minor** → record this round; may carry over to the final verdict

### Exit condition
- 0 critical AND 0 medium findings for **2 consecutive rounds**
- Or cut off once rounds stop *earning* their cost. Five is the usual place that
  happens, but it is a prompt to check, not a hard stop: keep going while each round
  still surfaces **new** defects, and stop when a round repeats the previous one's
  findings without adding any. Divergence is rounds producing the same output, not
  rounds producing a high number.

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
- If **the same finding** persists for 3+ rounds, suspect a reviewer-side false
  positive. But distinguish that from **the same area** producing a *different* real
  defect each round — that is the opposite signal, and means the area is genuinely
  hard and deserves more attention, not less. Check which one you have before
  dismissing anything: re-read the actual findings side by side rather than pattern-
  matching on the topic.
- This skill is expensive. Use it only before important merges

$ARGUMENTS
