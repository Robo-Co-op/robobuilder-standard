# COMPANION_SKILLS

robobuilder covers the **development** workflow. For knowledge work, sales, design, and other roles, install Anthropic's official skill packs as companions.

## Install presets

```
/robobuilder:install-companions dev
/robobuilder:install-companions pm
/robobuilder:install-companions sales
/robobuilder:install-companions design
/robobuilder:install-companions marketing
/robobuilder:install-companions ops
```

Each preset is defined in `company.yaml` → `companion_presets`. Edit `company.yaml` to customize.

## What each preset installs

### `dev` (developer)
- `anthropic-skills:pptx` — generate slide decks
- `anthropic-skills:docx` — generate Word documents
- `anthropic-skills:doc-coauthoring` — collaborative doc editing
- `codex` — OpenAI Codex bridge for second opinions

### `pm` (product manager)
- `product-management:write-spec`
- `product-management:roadmap-update`
- `product-management:sprint-planning`
- `product-management:competitive-brief`
- `product-management:metrics-review`
- `design:user-research`
- `design:research-synthesis`

### `sales`
- `sales:account-research`
- `sales:call-prep`
- `sales:call-summary`
- `sales:draft-outreach`
- `sales:competitive-intelligence`
- `brand-voice:enforce-voice`

### `design`
- `design:design-system`
- `design:design-critique`
- `design:accessibility-review`
- `design:design-handoff`
- `design:ux-copy`
- `brand-voice:enforce-voice`

### `marketing`
- `marketing:campaign-plan`
- `marketing:content-creation`
- `marketing:email-sequence`
- `marketing:seo-audit`
- `marketing:performance-report`
- `marketing:brand-review`

### `ops` (operations, finance, legal, HR)
- `operations:runbook`
- `operations:process-doc`
- `finance:variance-analysis`
- `finance:reconciliation`
- `legal:review-contract`
- `legal:vendor-check`
- `human-resources:performance-review`
- `human-resources:onboarding`

## Cross-pack standards

When you install companions:

- The robobuilder `company.yaml` is still authoritative for stack defaults (Vercel, Supabase, Notion, etc.).
- The robobuilder `CLAUDE.md.baseline` still governs conduct and tool preferences.
- Companion skills will see the same `${CLAUDE_PROJECT_DIR}` and inherit your harness config.

## When NOT to install everything

A single user does not need all presets. Pick by your daily role. You can always run `/robobuilder:install-companions <preset>` later when your work expands.

## Custom companions

For one-off needs, use `/anthropic-skills:skill-creator` or `/robobuilder:write-a-skill` to author your own. If a custom skill becomes broadly useful at Robo Co-op, contribute it back via the process in `CONTRIBUTING.md`.
