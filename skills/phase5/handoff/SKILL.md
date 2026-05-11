---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
origin: jin-custom
bootcamp_module: M3.code.ship
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase5)
> - **What**: Compact the current conversation into a handoff document for another agent to pick up
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:context-save, /robobuilder:write-a-skill
> - **Bootcamp**: M3.code.ship
> - **Origin**: Robo Co-op (Jin Kim)


Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to a path produced by `mktemp -t handoff-XXXXXX.md` (read the file before you write to it).

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
