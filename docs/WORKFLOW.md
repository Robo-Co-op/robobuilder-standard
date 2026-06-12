# WORKFLOW

The Robo Co-op 6-phase dev workflow, end-to-end.

```
Legend: 🟢 Matt Pocock  🟠 GStack  🔵 Jin Custom  🟣 robobuilder-original  💡 Optional

┌─────────────────────────────────────────────────────────────┐
│  Phase 0: Foundation (once per repo)                         │
├─────────────────────────────────────────────────────────────┤
│  🟢 /robobuilder:setup                                       │
│  🔵 /robobuilder:ubiquitous-language                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 0.5: Investigate (existing codebases)                 │
├─────────────────────────────────────────────────────────────┤
│  🟢 /robobuilder:zoom-out                                    │
│  🟢 /robobuilder:diagnose       (calls investigate at 3x)    │
│  🟠 /robobuilder:health                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Design                                              │
├─────────────────────────────────────────────────────────────┤
│  🟢 /robobuilder:grill-me        (decision-tree interview)   │
│  🟢 /robobuilder:grill-with-docs                             │
│  🔵 /robobuilder:design-an-interface                         │
│  💡🟠 /robobuilder:plan-eng-review                           │
│  🟢 /robobuilder:to-prd                                      │
│  🟢 /robobuilder:to-issues                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Prototype                                           │
├─────────────────────────────────────────────────────────────┤
│  🟢 /robobuilder:prototype                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Implement                                           │
├─────────────────────────────────────────────────────────────┤
│  🟢 /robobuilder:triage                                      │
│  🟢 /robobuilder:tdd                                         │
│  🟢 /robobuilder:caveman          (late-context compression) │
│  🟠 /robobuilder:browse           (Playwright QA)            │
│  🟠 /robobuilder:learn                                       │
│                                                              │
│  Agent teams (parallel TDD per slice):                        │
│  • Agent (worktree isolation)                                │
│  • /codex:rescue (heavy slices to OpenAI Codex)              │
│                                                              │
│  After each slice: 🟣 /robobuilder:blueprint-sync             │
│  (update PRD/DESIGN/ADR if the implementation diverged)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3.5: Refactor                                          │
├─────────────────────────────────────────────────────────────┤
│  🟢 /robobuilder:improve-codebase-architecture               │
│  🔵 /robobuilder:request-refactor-plan                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Review (escalating depth)                          │
├─────────────────────────────────────────────────────────────┤
│  🔵 /robobuilder:diff-review     (3 agents, daily)          │
│  🔵 /robobuilder:cross-review    (4 agents, critical merge) │
│  🔵 /robobuilder:grill           (adversarial deepest)       │
│  🟠 /robobuilder:cso             (OWASP + STRIDE security)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: Ship                                                │
├─────────────────────────────────────────────────────────────┤
│  🟠 /robobuilder:ship                                        │
│  🟠 /robobuilder:land-and-deploy                             │
│  🟠 /robobuilder:canary                                      │
│  🔵 /robobuilder:handoff         (--light for recap mode)    │
│  🟢 /robobuilder:write-a-skill                               │
└─────────────────────────────────────────────────────────────┘

Cross-cutting utilities (any phase):
  🟠 /robobuilder:guard           — careful + freeze combined
  🟣 /robobuilder:blueprint-sync  — keep design docs in sync with reality
  🟠 /robobuilder:context-save / context-restore
  🔵 /robobuilder:btw             — quick one-shot question
  🔵 /robobuilder:export          — flatten codebase for sharing

Playbooks (multi-skill orchestrators):
  🟣 /robobuilder:playbook-new-feature
  🟣 /robobuilder:playbook-bug-fix
  🟣 /robobuilder:playbook-review-deep

Meta:
  🟣 /robobuilder:start           — onboarding wizard
  🟣 /robobuilder:tune-claude-md  — personalize your CLAUDE.md
  🟣 /robobuilder:upgrade         — semver upgrade with diff preview
```

## How to read this chart

- Each phase has a primary skill or two; the rest are situational.
- 🟢/🟠/🔵/🟣 markers tell you the origin (Matt Pocock / GStack / Jin Custom / robobuilder-original).
- 💡 marks optional skills you don't need on every project.
- Arrows show typical ordering, but you can jump phases (e.g., Phase 3 → Phase 2 if you discover a missing prototype need).

## Standard flows

**New feature**: Phase 0.5 → 1 → 2 → 3 → 4 → 5. Use `/robobuilder:playbook-new-feature` for the full guided sequence.

**Bug fix**: Phase 0.5 (diagnose) → 3 (tdd) → 4 (diff-review) → 5 (ship). Use `/robobuilder:playbook-bug-fix`.

**High-stakes merge**: All of Phase 4. Use `/robobuilder:playbook-review-deep`.

**Refactor**: Phase 0.5 → 3.5 → 3 → 4. Tiny commits.

**Knowledge work (no code)**: install companion plugin with `/robobuilder:install-companions <preset>`.
