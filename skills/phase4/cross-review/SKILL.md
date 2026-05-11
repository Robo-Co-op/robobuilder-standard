---
name: cross-review
description: "AIクロスレビュー - 4視点で並列レビューし、指摘ゼロになるまでラウンドを回す。重要なマージ前にだけ使う（コスト高い）"
user-invocable: true
argument-hint: "[対象ブランチ/コミット範囲]"
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
> - **What**: AIクロスレビュー - 4視点で並列レビューし、指摘ゼロになるまでラウンドを回す。重要なマージ前にだけ使う（コスト高い）
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:diff-review, /robobuilder:grill
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /cross-review - 多視点ラウンドレビュー

`/diff-review` の強化版。**指摘ゼロになるまでラウンドを回す**のが特徴。

## 手順

### Round 0: 状況把握
- `git diff main...HEAD --stat`
- 対象ファイル一覧と規模を確認

### Round 1〜N: 並列レビュー → 修正 → 再レビュー
各ラウンドで以下のサブエージェントを**並列**で呼ぶ:
1. `code-simplifier` - 冗長・抽象化・命名
2. `test-writer` - テスト不足
3. `security-auditor` - OWASP
4. （任意）`e2e-tester` - UI機能の場合のみ

各エージェントの出力を集約し:
- **致命** → 即修正してから次ラウンド
- **中** → 修正してから次ラウンド
- **軽微** → このラウンドで記録、最終判定で持ち越し可

### 終了条件
- 致命 0 件 かつ 中 0 件 を**2ラウンド連続**で満たす
- または最大5ラウンドで打ち切り（それ以上回しても発散する）

## 出力（最終ラウンド後）
```
## 総ラウンド数: N
## 検出指摘の総数: X件
- 致命: A件 → 全て解消
- 中: B件 → 全て解消
- 軽微: C件 → 残置（リスト）
## 最終判定: SHIP / FIX FIRST
## 学び
- 今回繰り返した失敗パターン（次回に活かす）
```

## 注意
- ラウンド数や指摘数を**KPIにしない**。少ないほど良い
- 同じ指摘が3ラウンド以上続いたら、レビュアー側のfalse positiveを疑う
- このスキルはコスト高い。重要なマージ前にだけ使う

$ARGUMENTS
