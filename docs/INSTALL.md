# INSTALL

Step-by-step install for **robobuilder**.

## 1. Preflight

Before installing, check for conflicts:

```bash
bash ~/.claude/plugins/robobuilder/scripts/preflight_check.sh
```

Resolve any `[ERROR]` lines. `[WARN]` lines are advisory.

## 2. Install via Claude Code's plugin manager

Two-step: add the marketplace, then install the plugin.

```
/plugin marketplace add Roboco-op/robobuilder
/plugin install robobuilder@robo-coop-tools
```

(or for local dev/testing: `claude --plugin-dir ~/.claude/plugins/robobuilder`)

After install, run `/reload-plugins` once so skills, agents, and hooks register.

### Team auto-install via project settings

To enroll an entire repo's contributors, add to your project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "robo-coop-tools": {
      "source": { "source": "github", "repo": "Roboco-op/robobuilder" }
    },
    "enabledPlugins": {
      "robobuilder@robo-coop-tools": true
    }
  }
}
```

Team members get prompted to install on next session.

## 3. First-time setup

```
/robobuilder:start
```

This wizard asks 3 questions and points you at your first 3 skills.

## 4. Personalize CLAUDE.md

```
/robobuilder:tune-claude-md
```

Merges the Robo Co-op baseline into your `~/.claude/CLAUDE.md`. Preserves personal entries (paths, IPs, vaults).

## 5. (Optional) Compile browser binaries

`/robobuilder:browse` and any other Playwright-backed skills require GStack's compiled binaries.

```bash
bash ~/.claude/plugins/robobuilder/scripts/install_binaries.sh
```

Prereq: [bun](https://bun.sh) installed.

## 6. (Optional) Enable Feature Adoption Loop

```bash
bash ~/.claude/plugins/robobuilder/scripts/install_feature_radar.sh
```

Generates a scheduled-routine spec at `~/.claude/plugins/robobuilder/feature_radar_routine.md`. Follow the manual setup steps inside it (paste into `/anthropic-skills:schedule`).

## 7. (Optional) Install companion plugins by role

```
/robobuilder:install-companions dev      # PPTx, docx, codex
/robobuilder:install-companions pm        # product-management, design
/robobuilder:install-companions sales     # sales, brand-voice
/robobuilder:install-companions design    # design, brand-voice
```

(see `docs/COMPANION_SKILLS.md` for the full list)

## 8. Verify

```
/robobuilder:start            → should run onboarding
/robobuilder:btw "test"       → should respond instantly
/robobuilder:tdd              → should engage TDD flow
/plugin                       → should list robobuilder as installed
```

## Troubleshooting

- **Hooks not firing**: confirm `~/.claude/settings.json` references `${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json`, or copy hook scripts to your global hooks.
- **`/browse` errors**: re-run `install_binaries.sh`.
- **Skill collision**: robobuilder uses `/robobuilder:<name>` namespace by default — global `/<name>` still works if you had it before. No collision.
- **CLAUDE.md merge wrong**: revert with `/robobuilder:tune-claude-md --revert`.

## Updating

```
/robobuilder:upgrade
```

Pulls the latest from the upstream Roboco-op repo, shows a diff, applies on approval. If the baseline changes, prompts to re-run `tune-claude-md`.
