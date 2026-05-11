---
name: btw
description: "軽量ワンショット質問。重いレビュー・調査を呼ばず、最小コンテキストで即答する"
user-invocable: true
argument-hint: "<質問>"
allowed-tools:
  - Read
  - Glob
  - Grep
origin: jin-custom
bootcamp_module: M6.compounding-engineering
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (utils)
> - **What**: 軽量ワンショット質問。重いレビュー・調査を呼ばず、最小コンテキストで即答する
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:start, /robobuilder:handoff
> - **Bootcamp**: M6.compounding-engineering
> - **Origin**: Robo Co-op (Jin Kim)


# /btw - 軽量ワンショット質問

`$ARGUMENTS` の質問に対して、**最小限のツール使用** で簡潔に答えてください。

## ルール
- サブエージェントを呼ばない（grill, cross-review, diff-review などは使わない）
- ファイルを開くのは最大1〜2ファイルまで
- 推論・解説は3〜5行以内
- コード例は提示するなら**最小**（1〜10行）
- 「これで足りますか？深掘りしますか？」で締める

## 想定ユースケース
- 「この関数何してる？」
- 「TypeScript の Pick と Omit どっち使うべき？」
- 「git rebase と merge の違いって？」
- 「この設定書き方合ってる？」

重い作業（レビュー・リファクタ提案・テスト生成）が必要そうな質問なら、**先に「これは /grill や /diff-review を使った方が良いです」と提案**してから判断を仰ぐ。

$ARGUMENTS
