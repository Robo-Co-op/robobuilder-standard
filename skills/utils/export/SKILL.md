---
name: export
description: "[Util-6] Concatenate the entire repository's source code into a single file, for uploading to claude.ai Deep Research or sharing externally"
user-invocable: true
argument-hint: "[additional exclude patterns]"
allowed-tools:
  - Bash
  - Glob
origin: jin-custom
bootcamp_module: M6.compounding-engineering
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: Concatenate the entire repository's source code into one file for claude.ai Deep Research.
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:handoff
> - **Bootcamp**: M6.compounding-engineering
> - **Origin**: Robo Co-op (Jin Kim)


# /export — Concatenated Codebase Export

Concatenate all source code in the current repository into a single text file.

## Rules
- Exclude `node_modules/`, `.git/`, `.next/`, `dist/`, `build/`, `.turbo/`
- Exclude `*.lock`, `package-lock.json`
- Exclude images/binaries (`*.png`, `*.jpg`, `*.jpeg`, `*.ico`, `*.svg`, `*.gif`, `*.webp`, `*.woff*`, `*.ttf`, `*.eot`)
- Output each file in this format:

```
========== {file path} ==========
{file contents}

```

## Steps

Run the following command to save the output to a file, then tell the user the file path:

```bash
find . -type f \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  -not -path '*/.next/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/.turbo/*' \
  -not -name '*.lock' \
  -not -name 'package-lock.json' \
  -not -name '*.png' \
  -not -name '*.jpg' \
  -not -name '*.jpeg' \
  -not -name '*.ico' \
  -not -name '*.svg' \
  -not -name '*.gif' \
  -not -name '*.webp' \
  -not -name '*.woff' \
  -not -name '*.woff2' \
  -not -name '*.ttf' \
  -not -name '*.eot' \
  -not -name '*.map' \
  | sort | while read f; do
    echo "========== $f =========="
    cat "$f"
    echo ""
  done > /tmp/export-$(basename $(pwd))-$(date +%Y%m%d-%H%M%S).txt
```

After running the command:
1. Show the output file path and size
2. Show the number of files included
3. Tell the user: "Upload this file to claude.ai to enable Deep Research over the codebase"

$ARGUMENTS
