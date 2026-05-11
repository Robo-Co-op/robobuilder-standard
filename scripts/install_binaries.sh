#!/usr/bin/env bash
# install_binaries.sh — installs optional GStack binaries that back skills like /browse.
#
# Prereqs: bun (https://bun.sh)
#   On Windows PowerShell: irm bun.sh/install.ps1 | iex
#   On macOS/Linux:        curl -fsSL https://bun.sh/install | bash
#
# This script:
#   1. Clones the upstream gstack repo (if not present at ~/.claude/skills/gstack)
#   2. Runs gstack's own setup (compiles browse, find-browse, design, pdf binaries)
#   3. Installs Playwright Chromium for /browse
#
# Supply chain guard:
#   Before `bun install` + `bun run setup` execute third-party code, this script
#   prompts the user to verify the resolved commit SHA. Both fresh clones AND
#   upgrades go through the prompt.
#
# Non-interactive (CI / automated installs):
#   Set ROBOBUILDER_INSTALL_AUTO_YES=1 to skip prompts. Recommended only when
#   GSTACK_REF is pinned to an immutable SHA or signed tag.

set -euo pipefail

HOME_DIR="${HOME:-$USERPROFILE}"
GSTACK_DIR="$HOME_DIR/.claude/skills/gstack"

# Pin gstack to a known-good ref. Bump after manual review of upstream changes.
GSTACK_REF="${GSTACK_REF:-main}"     # Override: GSTACK_REF=v1.2.3 ./install_binaries.sh

AUTO_YES="${ROBOBUILDER_INSTALL_AUTO_YES:-0}"

# Combination guard: AUTO_YES on a moving branch ref defeats the supply-chain control.
# Refuse to proceed unless GSTACK_REF is pinned to a tag, SHA, or non-default branch.
if [ "$AUTO_YES" = "1" ]; then
    case "$GSTACK_REF" in
        main|master|HEAD|trunk|develop)
            echo "ERROR: ROBOBUILDER_INSTALL_AUTO_YES=1 with GSTACK_REF='$GSTACK_REF' is unsafe."
            echo "       Auto-confirming installs from a moving branch tip defeats the supply-chain guard."
            echo "       Pin GSTACK_REF to an immutable tag (e.g., v1.2.3) or commit SHA, then re-run."
            exit 1
            ;;
    esac
fi

confirm_sha() {
    local sha="$1"
    local action="$2"
    if [ "$AUTO_YES" = "1" ]; then
        echo "ROBOBUILDER_INSTALL_AUTO_YES=1 — skipping confirmation for $sha"
        return 0
    fi
    echo
    echo "Commit to $action: $sha"
    echo "Verify at: https://github.com/garrytan/gstack/commit/$sha"
    echo "The next step (bun install + bun run setup) executes code from this commit."
    read -p "Proceed? (y/N) " ans
    [ "$ans" = "y" ] || [ "$ans" = "Y" ]
}

if ! command -v bun >/dev/null 2>&1; then
    echo "ERROR: bun is required. Install from https://bun.sh and re-run."
    exit 1
fi

if [ -d "$GSTACK_DIR/.git" ]; then
    CURRENT=$(git -C "$GSTACK_DIR" rev-parse HEAD)
    echo "[1/3] gstack repo present (HEAD=$CURRENT). Checking for updates to ref '$GSTACK_REF'..."
    git -C "$GSTACK_DIR" fetch --tags origin
    TARGET=$(git -C "$GSTACK_DIR" rev-parse "origin/$GSTACK_REF" 2>/dev/null || \
             git -C "$GSTACK_DIR" rev-parse "$GSTACK_REF" 2>/dev/null || true)
    if [ -z "$TARGET" ]; then
        echo "WARN: Could not resolve ref '$GSTACK_REF'. Staying on current HEAD."
    elif [ "$CURRENT" != "$TARGET" ]; then
        echo "Upstream changed: $CURRENT → $TARGET"
        echo "Review the diff:"
        echo "  git -C $GSTACK_DIR log --oneline $CURRENT..$TARGET"
        if confirm_sha "$TARGET" "checkout + run"; then
            git -C "$GSTACK_DIR" checkout "$GSTACK_REF"
        else
            echo "Aborted. Staying on $CURRENT (will not run setup either)."
            exit 3
        fi
    else
        echo "Already at target ref."
        if ! confirm_sha "$CURRENT" "re-run setup"; then
            echo "Aborted. No changes."
            exit 3
        fi
    fi
else
    echo "[1/3] Cloning gstack at ref '$GSTACK_REF'..."
    mkdir -p "$(dirname "$GSTACK_DIR")"
    git clone --depth 1 --branch "$GSTACK_REF" https://github.com/garrytan/gstack "$GSTACK_DIR" || {
        # Fallback for non-branch refs (tags / SHAs)
        git clone https://github.com/garrytan/gstack "$GSTACK_DIR"
        git -C "$GSTACK_DIR" checkout "$GSTACK_REF"
    }
    HEAD=$(git -C "$GSTACK_DIR" rev-parse HEAD)
    echo "Cloned. HEAD=$HEAD"
    if ! confirm_sha "$HEAD" "first-time setup"; then
        echo "Aborted. The clone is at $GSTACK_DIR — review and re-run when ready."
        echo "For unattended installs: set ROBOBUILDER_INSTALL_AUTO_YES=1 (only when GSTACK_REF is a pinned SHA or signed tag)."
        exit 3
    fi
fi

echo "[2/3] Running gstack setup (this compiles browse/find-browse/design/pdf)..."
cd "$GSTACK_DIR"
bun install
bun run setup || echo "(setup script may report warnings; continuing)"

echo "[3/3] Verifying browse binary..."
if [ -f "$GSTACK_DIR/browse/dist/browse.exe" ] || [ -f "$GSTACK_DIR/browse/dist/browse" ]; then
    echo "OK — /robobuilder:browse is operational."
else
    echo "WARN — browse binary not found at expected location. /robobuilder:browse may not work."
fi

echo "Done. You can now use:"
echo "  /robobuilder:browse        — Playwright-driven QA"
echo "  /robobuilder:design-shotgun (if gstack design skills are also bundled)"
