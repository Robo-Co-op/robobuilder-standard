#!/usr/bin/env bash
# preflight_check.sh — run before installing robobuilder.
# Detects conflicts that the user should resolve first.
#
# Usage: bash scripts/preflight_check.sh
# Exit codes: 0 = clean, 1 = warnings, 2 = blockers

set -u

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-$USERPROFILE}"

errors=0
warnings=0

echo "robobuilder preflight check"
echo "==========================="

# 1. User CLAUDE.md exists?
if [ -f "$HOME_DIR/.claude/CLAUDE.md" ]; then
    bytes=$(wc -c < "$HOME_DIR/.claude/CLAUDE.md" 2>/dev/null || echo 0)
    echo "[INFO] Existing CLAUDE.md found (${bytes} bytes)."
    echo "       After install, run /robobuilder:tune-claude-md to merge with the baseline."
else
    echo "[INFO] No existing CLAUDE.md. Plugin baseline will be a clean start."
fi

# 2. User settings.json — flag if exists, do not modify
if [ -f "$HOME_DIR/.claude/settings.json" ]; then
    echo "[INFO] Existing settings.json found. robobuilder will NOT modify it."
    echo "       Reference: ${PLUGIN_ROOT}/settings.json.example"
fi

# 3. Other robobuilder install?
if [ -d "$HOME_DIR/.claude/plugins/robobuilder" ] && [ "$(realpath "$HOME_DIR/.claude/plugins/robobuilder" 2>/dev/null)" != "$(realpath "$PLUGIN_ROOT" 2>/dev/null)" ]; then
    echo "[WARN] Another robobuilder install detected at $HOME_DIR/.claude/plugins/robobuilder"
    echo "       Remove the old one before installing."
    warnings=$((warnings + 1))
fi

# 4. Conflicting global skills?
for skill in tdd diff-review cross-review grill handoff diagnose; do
    if [ -d "$HOME_DIR/.claude/skills/$skill" ]; then
        echo "[INFO] Global skill /$skill exists. robobuilder ships /robobuilder:$skill — no conflict."
    fi
done

# 5. Python available for hooks?
if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python not found. Hook scripts require Python 3.8+."
    errors=$((errors + 1))
fi

# 6. Git available?
if ! command -v git >/dev/null 2>&1; then
    echo "[ERROR] Git not found. Required for /robobuilder:upgrade."
    errors=$((errors + 1))
fi

# 7. Bun for optional binary skills (browse)?
if ! command -v bun >/dev/null 2>&1; then
    echo "[WARN] bun not found. Skill /browse requires GStack binaries — run scripts/install_binaries.sh after install."
    warnings=$((warnings + 1))
fi

echo
echo "Result: errors=${errors}, warnings=${warnings}"
if [ "$errors" -gt 0 ]; then
    echo "Resolve errors above before proceeding."
    exit 2
elif [ "$warnings" -gt 0 ]; then
    echo "Proceed with caution; review warnings above."
    exit 1
else
    echo "All clear."
    exit 0
fi
