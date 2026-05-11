---
name: diff-review
description: "現ブランチの差分を俯瞰レビューし、サブエージェント3本（code-simplifier / test-writer / security-auditor）で多面評価する"
user-invocable: true
argument-hint: "[--base <branch>] 対象ブランチ/コミット範囲を上書き"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
origin: jin-custom
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase4)
> - **What**: 現ブランチの差分を俯瞰レビューし、サブエージェント3本（code-simplifier / test-writer / security-auditor）で多面評価する
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:cross-review, /robobuilder:grill, /robobuilder:playbook-review-deep
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /diff-review - 3エージェント並列レビュー

現ブランチ（`main` 比）の差分を **3つのサブエージェントで並列レビュー**してください。

## 手順
1. `git diff main...HEAD --stat` と `git diff main...HEAD` の概要を把握
2. 以下の **3エージェントを並列**で呼ぶ（同一メッセージ内で複数 Agent ツール）:
   - `code-simplifier` - 冗長・抽象化・命名の観点
   - `test-writer` - テスト不足の指摘
   - `security-auditor` - OWASP 観点
3. 3者の出力を統合し、**優先度順の修正リスト**を最後に出す:
   ```
   ## 統合判定
   ### Must fix（マージ前）
   1. ...
   ### Should fix（同PR内推奨）
   1. ...
   ### Nice to have（後回し可）
   1. ...
   ## 一言: SHIP / FIX FIRST
   ```

$ARGUMENTS で対象ブランチ/コミット範囲を上書きできる（例: `--base develop`）。

$ARGUMENTS
