# DECISION_FLOW

When to invoke what. Branch by your current situation.

## Bug?

```
Cause known?
├─ YES → /robobuilder:tdd            (write failing regression test, then fix)
├─ NO  → /robobuilder:diagnose       (reproduce → minimize → hypothesize → confirm)
│        └─ 3 failures? → /robobuilder:investigate (if available) or restart with fresh assumptions
└─ In prod? → /robobuilder:diagnose → /robobuilder:tdd → /robobuilder:ship → /robobuilder:canary

Quick path: /robobuilder:playbook-bug-fix
```

## New feature?

```
Requirements clarity?
├─ Vague     → /robobuilder:grill-me            (then to-prd, to-issues)
├─ Clear     → /robobuilder:to-issues           (parallel TDD via Agent teams)
└─ Need feel → /robobuilder:prototype           (validate hands-on first)

UI involved?
├─ YES → /robobuilder:design-an-interface       (3-5 design alternatives)
│        └─ Pick one → optionally ask for visual variants in the same prototype flow
└─ NO  → straight to /robobuilder:to-prd

Quick path: /robobuilder:playbook-new-feature
```

## Review?

```
Stakes level?
├─ Daily            → /robobuilder:diff-review  (3 agents, fast)
├─ Critical merge   → /robobuilder:cross-review (4 agents, rounds)
├─ Maximum confidence → /robobuilder:playbook-review-deep (diff → cross → grill)
├─ Design decision  → /robobuilder:grill-me     (or design-critic agent)
├─ Domain alignment → /robobuilder:grill-with-docs
└─ Security-sensitive → /robobuilder:cso         (OWASP + STRIDE)
```

## Ship?

```
Stage?
├─ Just created PR        → /robobuilder:ship                  (tests + coverage + PR body)
├─ PR approved            → /robobuilder:land-and-deploy        (merge + CI + deploy + health)
├─ Just deployed          → /robobuilder:canary                  (monitor for regressions)
├─ Want metrics baseline  → /robobuilder:benchmark               (Core Web Vitals)
└─ Session ending         → /robobuilder:handoff                 (or handoff --light = recap)
```

## Unfamiliar codebase?

```
Big picture     → /robobuilder:zoom-out
Health check    → /robobuilder:health
Quick question  → /robobuilder:btw
Explore deeply  → Agent: codebase-explorer
```

## Tech debt?

```
Identify hotspots         → /robobuilder:improve-codebase-architecture
Plan safe refactor        → /robobuilder:request-refactor-plan
Execute                   → /robobuilder:tdd (tiny commits)
```

## Stuck?

```
Lost in context           → /robobuilder:zoom-out
Approaching context limit → /robobuilder:caveman (compress) or /compact
Need a fresh approach     → run /clear, start new session, summarize via /robobuilder:handoff
Want a second opinion     → /codex:rescue (separate provider)
```

## Onboarding / first time?

```
Just installed → /robobuilder:start         (wizard picks your 3 starter skills)
Got my path    → /robobuilder:tune-claude-md (personalize CLAUDE.md)
Days later     → /robobuilder:upgrade        (stay current)
```
