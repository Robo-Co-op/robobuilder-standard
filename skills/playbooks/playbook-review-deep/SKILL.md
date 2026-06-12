---
name: playbook-review-deep
description: "[PB-3] Three-tier escalating review for critical merges. Runs diff-review → cross-review → grill in sequence, with user confirmation between tiers. Use before merging high-impact branches (security, payments, auth, multi-system migrations)."
origin: robobuilder
---

# /robobuilder:playbook-review-deep

## What
Three-tier escalating adversarial review:
- Tier 1: `/diff-review` (3 agents, daily-quality)
- Tier 2: `/cross-review` (4 agents, round-based, critical-merge)
- Tier 3: `/grill` (adversarial, failure-mode enumeration)

## When
- Branch touches: auth, payments, database migrations, security policy, multi-tenant data, billing
- Branch is "the last one before launch"
- Customer-facing change with no easy rollback
- Senior reviewer wants maximum confidence

Do NOT use for routine feature work — `/diff-review` alone is enough.

## Why
Some changes don't get a second chance. Defense in depth: each tier catches different failure modes. Tier 1 surfaces obvious issues; Tier 2 surfaces design issues; Tier 3 surfaces hidden assumptions.

## How

### Tier 1 — diff-review
Invoke `/robobuilder:diff-review` via Skill tool.
3 agents in parallel: code-simplifier, test-writer, security-auditor.

If Tier 1 surfaces blocking issues: stop, fix, restart Tier 1.

### Tier 2 — cross-review
Confirm: "Tier 1 clean. Escalate to /cross-review (4 agents, round-based)? (y/n)"
If y: invoke `/robobuilder:cross-review`.

If Tier 2 surfaces blocking issues: stop, fix, restart from Tier 1 (not just Tier 2 — Tier 1 might re-surface).

### Tier 3 — grill
Confirm: "Tier 2 clean. Run /grill for adversarial deepest pass? (y/n)"
If y: invoke `/robobuilder:grill`.

`/grill` MUST enumerate at least 5 failure modes for this change. If fewer than 5, push it harder before accepting.

### Closing
Print: "Triple-reviewed. Merge with high confidence."
Recommend immediate `/robobuilder:ship` if not blocked.

## Example

```
User: /robobuilder:playbook-review-deep
       PR #847 swaps the Stripe integration from one-time to subscription billing.
Claude: Deep-review playbook. Tier 1: /robobuilder:diff-review

[diff-review: 1 issue found — missing retry on webhook timeout. User fixes.]

Claude: Tier 1 re-run. Clean. Escalate to /cross-review? (y/n)
User: y
[cross-review: 4 agents over 2 rounds — agent debate surfaces edge case for partial refunds]

Claude: Cross-review identified partial-refund edge case. Fixed in commit abc123.
        Restart from Tier 1 to confirm? (y/n)
User: y
[Tier 1 + Tier 2 re-run, clean]

Claude: Tier 2 clean. Run /grill for final adversarial pass? (y/n)
User: y
[grill enumerates 7 failure modes: clock skew, webhook replay, currency change, etc. 2 require code changes.]

Claude: Grill surfaced 2 must-fix items. After fixing, the third pass should clear.
        ...
        [eventually all 3 tiers clean]
Claude: Triple-reviewed. Merge with high confidence. /robobuilder:ship?
```

## Anti-pattern
- Don't run Tier 3 first to "save time" — Tier 3 finds different things than Tier 1, not strictly deeper.
- Don't accept a `/grill` that returns fewer than 5 failure modes for a critical change.
- Don't restart from Tier 2 after a Tier 2 fix; always restart from Tier 1 (Tier 1 issues can re-emerge from Tier 2 fixes).

## See Also
- Sibling: `/robobuilder:playbook-new-feature`, `/robobuilder:playbook-bug-fix`
- Individual tiers: `/robobuilder:diff-review`, `/robobuilder:cross-review`, `/robobuilder:grill`
- For security-specific: also run `/robobuilder:cso`
- Bootcamp: M3.code.review + M4.security
