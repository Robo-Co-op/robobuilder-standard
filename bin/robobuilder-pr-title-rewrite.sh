#!/usr/bin/env bash
set -euo pipefail

version="${1:-}"
title="${2:-}"
title="${title#v[0-9]* }"
if [ -n "$version" ]; then
  printf 'v%s %s\n' "$version" "$title"
else
  printf '%s\n' "$title"
fi
