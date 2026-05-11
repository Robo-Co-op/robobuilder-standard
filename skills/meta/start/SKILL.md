---
name: start
description: Onboarding wizard for first-time robobuilder users. Asks about role, experience level, and current task, then suggests the right starting skills. Use this when a user invokes /robobuilder:start, when they ask "how do I use this plugin?", or when they seem lost in the skill catalog.
---

# /robobuilder:start

## What
Interactive onboarding that turns the 33-skill catalog into a personalized 3-skill starter pack based on who the user is and what they're doing right now.

## When
- User just installed robobuilder for the first time
- User explicitly asks "where do I start?" or "how do I use this?"
- User invokes `/robobuilder:start`

Do NOT use this when the user already knows what skill they want — that wastes their time.

## Why
33 skills is overwhelming without guidance. Without a router, users either pick the wrong skill or default to plain chat. Compounding Engineering only works if the right skill fires in the right moment.

## How

Ask the user three short questions in sequence (one at a time, wait for answers):

### Q1 — Role
"What's your role today?"
- (a) Developer (writing code)
- (b) Product / PM (specifying, planning)
- (c) Designer
- (d) Sales / Marketing
- (e) Other

### Q2 — Experience with Claude Code
"How familiar are you with Claude Code?"
- (a) First week
- (b) Comfortable with `/clear`, `/compact`, basic slash commands
- (c) Power user — write my own skills, configure hooks

### Q3 — Today's task
"What are you trying to accomplish today, in one sentence?"

### Then route

Based on answers, recommend exactly **3 skills** + 1 playbook + 1 doc link:

```
Dev × New feature:
  → /robobuilder:playbook-new-feature
  → Key skills: grill-me, tdd, diff-review
  → Read: docs/WORKFLOW.md

Dev × Bug:
  → /robobuilder:playbook-bug-fix
  → Key skills: diagnose, tdd, diff-review
  → Read: docs/DECISION_FLOW.md

Dev × Ship:
  → /robobuilder:ship
  → Key skills: ship, land-and-deploy, canary
  → Read: docs/WORKFLOW.md (Phase 5)

Dev × Unfamiliar codebase:
  → /robobuilder:zoom-out
  → Key skills: zoom-out, health, btw
  → Read: docs/WORKFLOW.md (Phase 0.5)

PM × Specifying:
  → /robobuilder:to-prd
  → Key skills: grill-me, to-prd, to-issues
  → Read: docs/WORKFLOW.md (Phase 1)

Designer × New screen:
  → /robobuilder:design-an-interface
  → Key skills: design-an-interface
  → Companion plugins recommended: install via /robobuilder:install-companions design

Any × Learning:
  → /robobuilder:btw
  → Then point to Bootcamp v3 Notion hub for theory
```

### Close with

"Remember: `/robobuilder:tune-claude-md` will customize your CLAUDE.md with Robo Co-op best practices once you're ready. And `/robobuilder:upgrade` keeps you current."

## Example

```
User: /robobuilder:start
Claude: Welcome to robobuilder. Three quick questions to point you at the right skills.

  Q1: What's your role today? (a/b/c/d/e)
User: a (Developer)
Claude: Q2: Claude Code familiarity? (a/b/c)
User: b
Claude: Q3: What are you trying to do today?
User: Fix a flaky test in our checkout flow
Claude: Bug-fix scenario. Try this:

  → /robobuilder:playbook-bug-fix
  → Key skills you'll touch: diagnose, tdd, diff-review
  → Skim: docs/DECISION_FLOW.md (bug branch)

  When you're done, /robobuilder:handoff captures it for your future self.
```

## Anti-pattern
Don't dump all 33 skills as a list. Don't ask 10 questions — 3 is the budget. Don't recommend more than 3 skills + 1 playbook + 1 doc.

## See Also
- Next step (always): the 3 skills returned by this wizard
- Configuration: `/robobuilder:tune-claude-md`
- Bootcamp: M0.why + M1.chat
