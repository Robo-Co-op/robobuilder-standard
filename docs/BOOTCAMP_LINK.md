# BOOTCAMP_LINK — Living Knowledge Loop

## The idea

robobuilder skills and the Notion Bootcamp v3 hub are designed to be **bidirectionally linked**. Updating one improves the other without re-releasing the plugin.

```
   ┌──────────────────────────────────────────┐
   │   Notion Bootcamp v3                      │
   │   (theory, principles, why)                │
   │   https://www.notion.so/Claude-34e5a...   │
   └────────┬─────────────────────▲────────────┘
            │ Direction A          │ Direction D
            │ skill links back      │ new bestprac
            │ to its theory page    │ pushed to Notion
            ▼                       │
   ┌──────────────────────────────────────────┐
   │   robobuilder skills                       │
   │   (practice, tools, how)                   │
   └────────┬─────────────────────▲────────────┘
            │ Direction B          │ Direction C
            │ daily execution       │ where users get
            ▼                       │ stuck → new pattern
       daily dev work ──→ obstacle ┘
```

## Direction A: skill → Notion (live in v1.0)

Every SKILL.md will eventually carry a frontmatter pair:

```yaml
bootcamp_module: M3.code.tdd
bootcamp_url: https://www.notion.so/<page-id>
```

When a user is mid-flow and wants the *why* behind a skill, they click that URL.

> Status in v1.0: frontmatter scaffolding present in meta + playbook skills. The 33 ingested skills will be backfilled progressively.

## Direction B: Notion → skill (manual at v1.0)

Each Bootcamp v3 module page in Notion gets a section near the top:

```
## Corresponding robobuilder skills

- `/robobuilder:tdd` — practical execution
- `/robobuilder:diagnose` — when TDD reveals a real bug
- Agent: tdd-pair — for discipline enforcement
```

When a learner finishes a module, they know exactly which slash command to run to put it into practice.

> Status in v1.0: this section must be added manually to each Notion page. v2.0 will automate via Notion MCP.

## Direction C: stuck → improvement candidate

Pain points seen in daily use → captured via `/robobuilder:write-a-skill` or in `feedback_*` memories → escalated to the team retro.

## Direction D: new best-practice → Notion

The retro decides which patterns are worth adding. The Notion page gets the update. The next time anyone uses the related skill, they hit the updated theory.

**This is why the Loop matters**: a single Notion edit by Jin (or any team contributor) silently raises the floor for everyone.

## Bootcamp v3 modules and likely skill mappings

| Module | Theme | Suggested skill mappings |
|---|---|---|
| M0 Why | Why Claude Code | (no direct skill; meta) |
| M1 Chat | Conversation patterns | `/robobuilder:btw` |
| M2 Cowork | Working alongside Claude | `/robobuilder:start`, `/robobuilder:handoff` |
| M3 Code | The 7 layers (Explore → Plan → Code → Test → Review → Ship → Reflect) | All of Phases 0–5 |
| M4 Security | Threat-modeling AI workflows | `/robobuilder:cso`, agent: security-auditor |
| M5 Refugee Launchpad | Onboarding new teammates | `/robobuilder:start`, `/robobuilder:tune-claude-md` |
| M6 Action+Compounding | Loops, learning, durability | `/robobuilder:write-a-skill`, `/robobuilder:upgrade`, feature_radar |

## How to update Notion

1. Open the Bootcamp v3 hub: `company.yaml` → `docs.notion_hub`.
2. Navigate to the module page.
3. Add/update the "Corresponding robobuilder skills" section.
4. (Optional) Add the inverse: paste the Notion page URL into the matching SKILL.md `bootcamp_url` frontmatter. Open a PR to robobuilder.

The plugin does not need to be re-released. Notion content reaches every user instantly.
