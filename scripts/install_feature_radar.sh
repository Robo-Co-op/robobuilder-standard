#!/usr/bin/env bash
# install_feature_radar.sh — sets up the robobuilder feature radar routine.
#
# This agent runs daily at 09:00 JST, checks:
#   - anthropics/claude-code releases
#   - claude-plugins-official catalog updates
#   - openai/codex-plugin-cc updates
#   - mattpocock/ai-engineering-skills updates
# and appends findings to a robobuilder-local feature_radar.md.
#
# Requires: Claude Code with the `schedule` skill enabled, or manual setup via your CC interface.
#
# This script generates the routine definition as a markdown file that you can paste into
# /anthropic-skills:schedule (or your harness's equivalent).

set -euo pipefail

HOME_DIR="${HOME:-$USERPROFILE}"
ROBOBUILDER_HOME="${ROBOBUILDER_HOME:-$HOME_DIR/.robobuilder}"
OUT="$ROBOBUILDER_HOME/feature_radar_routine.md"

mkdir -p "$ROBOBUILDER_HOME"

cat > "$OUT" <<'EOF'
# robobuilder-feature-radar

**Schedule:** Daily at 09:00 JST (cron: `0 0 * * *` UTC)

**Purpose:** Detect newly released Claude Code / plugin / Codex features. Surface for weekly human review.

**Routine prompt:**

```
You are robobuilder-feature-radar. Run a daily scan and append findings to robobuilder-local memory.

1. Check GitHub releases (use WebFetch or `gh release list -L 5`):
   - anthropics/claude-code
   - mattpocock/ai-engineering-skills
   - openai/codex (or codex-plugin-cc if used)

2. Check Claude Code official changelog if reachable.

3. For each new release since yesterday, write 1–3 bullets to:
   ${ROBOBUILDER_HOME:-$HOME/.robobuilder}/feature_radar.md
   under today's date heading.

4. Each bullet format:
   - [source]@[version] — [headline] — [why it might matter for Robo Co-op]

5. If nothing new, append "no changes" under today's heading.

6. Do NOT enable any new features automatically. Discovery only.
   Human review happens on Friday via /retro or weekly standup.
```

**Setup steps (manual, one time):**

1. Open Claude Code.
2. Run `/anthropic-skills:schedule` (or your harness's schedule tool).
3. Provide the prompt above and the cron `0 0 * * *`.
4. Approve.

**Verification:**

After 24 hours, check `${ROBOBUILDER_HOME:-$HOME/.robobuilder}/feature_radar.md` for the first entry.

**Pairing:**

Weekly on Friday, review `feature_radar.md` during robobuilder maintenance. For each promising feature, decide:
- TRY → assign owner, schedule a try-it session
- SKIP → record reason in `memory/feedback_*.md`
- DEFER → leave on radar
EOF

echo "Routine spec written to: $OUT"
echo "Open it and follow the manual setup steps to create the schedule."
