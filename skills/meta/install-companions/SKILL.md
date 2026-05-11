---
name: install-companions
description: Install a curated set of Anthropic official skill packs alongside robobuilder, by role. Presets defined in company.yaml. Use when user invokes /robobuilder:install-companions or asks "what skills should I install on top of robobuilder?".
---

# /robobuilder:install-companions

## What
Installs a curated bundle of companion plugins from the Anthropic official marketplace, scoped by role (dev / pm / sales / design / marketing / ops).

## When
- After `/robobuilder:start` identified the user's primary role
- When user expands into a new role (dev who starts doing sales)
- When the team rolls out robobuilder + role-specific companions in one sweep

Do NOT use when the user already has the plugins installed — `/plugin` shows what's currently active.

## Why
robobuilder covers the **development** workflow. Knowledge work (slides, docs, sales calls, design critiques) is handled by Anthropic's official skill packs. Bundling them under presets means each role's full toolkit is one command.

## How

### Step 1 — Read the preset

Load `${CLAUDE_PLUGIN_ROOT}/company.yaml` → `companion_presets[<preset>]`.

If the user did not pass an argument, ask which preset (show the list from `company.yaml`).

### Step 2 — Preview

Show the list of plugins that will be installed:

```
Preset: dev
Plugins to install:
  - anthropic-skills:pptx
  - anthropic-skills:docx
  - anthropic-skills:doc-coauthoring
  - codex

Already installed:
  - (none)

Proceed? (y/n)
```

### Step 3 — Install

For each plugin in the preset, invoke the install command:

```
/plugin marketplace add anthropics/claude-plugins-official    # if not already added
/plugin install <plugin>@claude-plugins-official
```

(For non-Anthropic plugins like `codex`, use the appropriate marketplace.)

### Step 4 — Reload + verify

```
/reload-plugins
```

Confirm each new skill is available by running a quick check (`/plugin` → Installed tab).

## Example

```
User: /robobuilder:install-companions dev
Claude: Preset 'dev'. Will install:
  - anthropic-skills:pptx
  - anthropic-skills:docx
  - anthropic-skills:doc-coauthoring
  - codex
Proceed? (y/n)
User: y
Claude: Installing... [chains through each /plugin install]
        Done. /reload-plugins → reloaded. 4 new skills available.
```

## Anti-pattern
- Don't blindly install every preset — pick by daily role.
- Don't bypass user confirmation; companion plugins can be heavy.
- Don't ignore "already installed" — skip duplicates.

## See Also
- `${CLAUDE_PLUGIN_ROOT}/company.yaml` (presets defined here)
- `${CLAUDE_PLUGIN_ROOT}/docs/COMPANION_SKILLS.md` (full preset reference)
- `/robobuilder:upgrade` (keep robobuilder + companions current)
- Bootcamp: M6.action+compounding
