---
name: grill
description: "直近の変更（diff）を厳しく問い詰めて、見落とし・前提誤り・脆弱性を炙り出す敵対的レビュー"
user-invocable: true
argument-hint: "[対象ファイル/コミット範囲]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
origin: jin-custom
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase4)
> - **What**: 直近の変更（diff）を厳しく問い詰めて、見落とし・前提誤り・脆弱性を炙り出す敵対的レビュー
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:diff-review, /robobuilder:cross-review, /robobuilder:grill-me
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /grill - 敵対的レビュー

直近の変更（`git diff` または `$ARGUMENTS` で指定された対象）を**敵対的レビュー**してください。媚びず、容赦なく。

## やること
1. **前提を疑う** - このコードが暗黙に仮定していること（環境、入力、状態）を列挙し、それぞれ破る入力を考える
2. **失敗モード列挙** - 5つ以上の「これで壊れる」シナリオ（並行性、ネットワーク失敗、partial failure、リトライ、null/undefined、空配列、上限超過）
3. **ロジック検証** - 条件分岐の網羅性、off-by-one、境界、競合状態
4. **代替案** - 「私ならこう書く」を1〜2案、なぜそちらが良いか理由つきで
5. **副作用** - このコードがコミットされた時に変わる外部状態（DB、API、ファイル、ログ、課金、メール送信）

## 出力フォーマット
```
## レビュー対象
## 暗黙の前提（破られたら壊れる）
1. ...
2. ...
## 失敗モード
1. [致命] ...
2. [中] ...
## ロジック上の懸念
- ...
## 代替案
- 案A: ...
- 案B: ...
## 副作用
- ...
## 一言判定: SHIP / PATCH FIRST / REWRITE
```

擁護するな。批判を求めている。「概ね問題ない」と言いたくなったら、もう一段深く掘れ。

$ARGUMENTS
