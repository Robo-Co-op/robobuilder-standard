#!/usr/bin/env bash
# install_feature_radar.sh — sets up the cc-feature-radar scheduled remote agent.
#
# This agent runs daily at 09:00 JST, checks:
#   - anthropics/claude-code releases
#   - claude-plugins-official catalog updates
#   - openai/codex-plugin-cc updates
#   - garrytan/gstack updates
#   - mattpocock/ai-engineering-skills updates
# and appends findings to your nexus feature_radar.md.
#
# Requires: Claude Code with the `schedule` skill enabled, or manual setup via your CC interface.
#
# This script generates the routine definition as a markdown file that you can paste into
# /anthropic-skills:schedule (or your harness's equivalent).

set -euo pipefail

HOME_DIR="${HOME:-$USERPROFILE}"
OUT="$HOME_DIR/.claude/plugins/robobuilder/feature_radar_routine.md"

cat > "$OUT" <<'EOF'
# cc-feature-radar

**Schedule:** Daily at 09:00 JST (cron: `0 0 * * *` UTC)

**Purpose:** Detect newly released Claude Code / plugin / Codex features. Surface for weekly human review.

**Routine prompt:**

```
You are cc-feature-radar. Run a daily scan and append findings to nexus.

1. Check GitHub releases (use WebFetch or `gh release list -L 5`):
   - anthropics/claude-code
   - garrytan/gstack
   - mattpocock/ai-engineering-skills
   - openai/codex (or codex-plugin-cc if used)

2. Check Claude Code official changelog if reachable.

3. For each new release since yesterday, write 1–3 bullets to:
   $HOME/nexus/pc/memory/feature_radar.md
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

After 24 hours, check `$HOME/nexus/pc/memory/feature_radar.md` for the first entry.

**Pairing:**

Weekly on Friday, run `/gstack:retro` or read `feature_radar.md` directly. For each promising feature, decide:
- TRY → assign owner, schedule a try-it session
- SKIP → record reason in `memory/feedback_*.md`
- DEFER → leave on radar
EOF

echo "Routine spec written to: $OUT"
echo "Open it and follow the manual setup steps to create the schedule."
