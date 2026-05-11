---
name: export
description: "現リポジトリの全ソースコードを1ファイルに連結出力。claude.ai Deep Research 用"
user-invocable: true
argument-hint: "[追加除外パターン]"
allowed-tools:
  - Bash
  - Glob
origin: jin-custom
bootcamp_module: M6.compounding-engineering
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: 現リポジトリの全ソースコードを1ファイルに連結出力。claude.ai Deep Research 用
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:handoff
> - **Bootcamp**: M6.compounding-engineering
> - **Origin**: Robo Co-op (Jin Kim)


# /export - コードベース連結出力

現在のリポジトリの全ソースコードを1つのテキストに連結して出力してください。

## ルール
- `node_modules/`, `.git/`, `.next/`, `dist/`, `build/`, `.turbo/` は除外
- `*.lock`, `package-lock.json` は除外
- 画像・バイナリ（`*.png`, `*.jpg`, `*.jpeg`, `*.ico`, `*.svg`, `*.gif`, `*.webp`, `*.woff*`, `*.ttf`, `*.eot`）は除外
- 各ファイルは以下の形式で出力:

```
========== {ファイルパス} ==========
{ファイル内容}

```

## 手順

以下のコマンドを実行して出力をファイルに保存し、ファイルパスをユーザーに伝えてください:

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

コマンド実行後:
1. 出力ファイルのパスとサイズを表示
2. 含まれたファイル数を表示
3. 「このファイルをclaude.aiにアップロードするとDeep Researchが可能です」と案内

$ARGUMENTS
