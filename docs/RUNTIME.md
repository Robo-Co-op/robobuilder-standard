# RoboBuilder Runtime

RoboBuilder stores durable local workflow state under:

```bash
${ROBOBUILDER_HOME:-$HOME/.robobuilder}
```

Project-scoped state lives under:

```bash
${ROBOBUILDER_HOME:-$HOME/.robobuilder}/projects/<project-slug>
```

Use the helper scripts instead of repeating path and slug logic in skills:

```bash
eval "$(bin/robobuilder-slug 2>/dev/null)"
bin/robobuilder-paths
```

Available helpers:

- `bin/robobuilder-slug`: emits `SLUG=<project-slug>` for the current git repo or directory.
- `bin/robobuilder-paths`: prints the configured state root.
- `bin/robobuilder-config`: prints existing local config values.
- `bin/robobuilder-learnings-log` / `bin/robobuilder-learnings-search`: append and search project learnings.
- `bin/robobuilder-review-log` / `bin/robobuilder-review-read`: append and read review records.
- `bin/robobuilder-diff-scope`: summarize changed-file scope for review and ship workflows.
- `bin/robobuilder-next-version`: choose the next local semver when no release metadata exists.

Do not add third-party runtime binary installers here. If a target project needs browser automation, database clients, or build tools, use that project's own dependency setup.
