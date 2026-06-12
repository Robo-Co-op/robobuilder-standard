---
name: btw
description: "[Util-5] Lightweight one-shot question. Answers immediately with minimal context — no heavy reviews, no investigations, no subagents"
user-invocable: true
argument-hint: "<question>"
allowed-tools:
  - Read
  - Glob
  - Grep
origin: jin-custom
bootcamp_module: M6.compounding-engineering
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: Lightweight one-shot question — answer immediately with minimal tool use, no subagents.
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:start, /robobuilder:handoff
> - **Bootcamp**: M6.compounding-engineering
> - **Origin**: Robo Co-op (Jin Kim)


# /btw — Lightweight One-Shot Question

Answer the question in `$ARGUMENTS` concisely, with **minimal tool use**.

## Rules
- Do not invoke subagents (no grill, cross-review, diff-review, etc.)
- Open at most 1–2 files
- Reasoning/explanation within 3–5 lines
- If you show a code example, keep it **minimal** (1–10 lines)
- Close with "Is this enough, or should I dig deeper?"

## Typical use cases
- "What does this function do?"
- "Should I use TypeScript's Pick or Omit here?"
- "What's the difference between git rebase and merge?"
- "Is this config syntax correct?"

If the question looks like it needs heavy work (review, refactor proposal, test generation), **first suggest "this is better handled by /grill or /diff-review"** and let the user decide.

$ARGUMENTS
