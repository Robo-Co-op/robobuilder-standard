#!/usr/bin/env bash
# install_binaries.sh — compatibility shim for older robobuilder installs.
#
# robobuilder no longer installs or requires third-party runtime binaries.
# Browser automation should use the target project's own Playwright/browser
# tooling, or a robobuilder-local helper installed by that project.

set -euo pipefail

HOME_DIR="${HOME:-$USERPROFILE}"
ROBOBUILDER_HOME="${ROBOBUILDER_HOME:-$HOME_DIR/.robobuilder}"

mkdir -p "$ROBOBUILDER_HOME"

echo "No external runtime binaries are required for robobuilder."
echo "Created/verified robobuilder home: $ROBOBUILDER_HOME"
echo "This script is kept only so older setup docs and automation exit cleanly."
