# GITHUB_ASANA_SYNC — Two-way Issue/Task Mirror

## The idea / 概要

EN: A GitHub repo's issues and an Asana project's tasks are designed to be **bidirectionally
linked**, the same way robobuilder skills and the Bootcamp v3 Notion hub are (see
`docs/BOOTCAMP_LINK.md`). Nobody creates a task by hand, pastes a link, or double-marks something
done — the two systems just reflect each other.

JP: GitHub リポジトリの Issue と Asana プロジェクトのタスクは、robobuilder スキルと Bootcamp v3 の
Notion ハブが連携しているのと同様に、**双方向にリンク**するよう設計されています（`docs/BOOTCAMP_LINK.md`
参照）。タスクを手動で作成したり、リンクを貼り付けたり、二重に完了マークを付けたりする必要はなく、
2つのシステムが互いを反映します。

```
   ┌──────────────────────────────────────────┐
   │   GitHub Issues                            │
   │   (source of truth for the dev lifecycle) │
   └────────┬─────────────────────▲────────────┘
            │ Direction A          │ Direction D
            │ issue opened →        │ task completed in Asana →
            │ task created           │ issue closed (polled)
            ▼                       │
   ┌──────────────────────────────────────────┐
   │   Asana project                            │
   │   (stakeholder-facing mirror)              │
   └────────┬─────────────────────▲────────────┘
            │ Direction B          │ Direction C
            │ issue closed →        │ issue reopened →
            │ task completed         │ task un-completed
            ▼                       │
       (same task) ─────────────────┘
```

> Status / ステータス: implemented and running in production since 2026-09-11 / 2026年9月11日より
> 本番稼働中。Reference implementation / リファレンス実装:
> [`Robo-Co-op/RoboDesk`](https://github.com/Robo-Co-op/RoboDesk) — see
> `.github/workflows/asana-github-sync.yml` and `.github/workflows/asana-github-reverse-sync.yml`,
> and `docs/github-asana-sync.md` in that repo for the bilingual team-facing version of this doc /
> 同リポジトリのバイリンガル版チーム向けドキュメントは `docs/github-asana-sync.md` を参照してください。

## Direction A: issue opened → Asana task created

EN: A GitHub Actions workflow, triggered on `issues: opened`, calls the Asana API to create a task
in a designated project, then writes the task's link back into the issue body under an
"## Asana task" heading. If the issue already has an Asana link (e.g. pasted manually, or from an
import), creation is skipped rather than duplicated.

JP: `issues: opened` イベントをトリガーとする GitHub Actions ワークフローが Asana API を呼び出し、
指定されたプロジェクトにタスクを作成します。その後、タスクのリンクを Issue 本文の「## Asana task」欄に
書き込みます。Issue に既に Asana リンクがある場合（手動で貼り付けた、またはインポートされた場合など）は、
重複作成を避けるためタスク作成をスキップします。

## Direction B: issue closed → Asana task completed

EN: Triggered on `issues: closed`. Skipped if the issue was closed as **"not planned"** rather than
completed — that distinction matters, since "not planned" isn't "done."

JP: `issues: closed` イベントでトリガーされます。Issue が「completed（完了）」ではなく
**「not planned（対応しない）」** としてクローズされた場合はスキップされます。この区別は重要です。
「対応しない」は「完了」ではないためです。

## Direction C: issue reopened → Asana task un-completed

EN: Triggered on `issues: reopened`. Keeps the task's completion state honest if work turns out to
be unfinished after all.

JP: `issues: reopened` イベントでトリガーされます。作業が実際には未完了だった場合に、タスクの完了状態を
正しく保ちます。

## Direction D: Asana task completed → GitHub issue closed

EN: Asana has no outgoing webhook here, because that needs a small hosted receiver — nothing this
lightweight has one by default. Instead, a second workflow runs on a schedule (every ~15 minutes,
plus `workflow_dispatch` for an on-demand run), lists the repo's open issues, and for each one with
an Asana link, checks whether that task is now complete. If it is, the workflow closes the issue
(as completed) and leaves a comment pointing back to the task.

JP: この方向には Asana からの Webhook を使用していません。Webhook の受信には小規模なホスティング環境が
必要ですが、この軽量な仕組みにはデフォルトで用意されていないためです。代わりに、2つ目のワークフローが
スケジュール実行（約15分ごと、加えて `workflow_dispatch` によるオンデマンド実行も可能）され、リポジトリの
オープンな Issue を一覧化し、Asana リンクを持つものについてタスクが完了しているかを確認します。完了して
いれば、Issue を（completed として）クローズし、タスクへのリンクを含むコメントを残します。

> EN: If your repo *does* have a hosted endpoint (a Vercel/Supabase function, a small server), an
> Asana webhook (`POST /webhooks` on a task or project, with a signature you validate) makes
> Direction D instant instead of polled. Not implemented anywhere yet — a candidate for a future
> skill.
>
> JP: もしリポジトリにホスティング環境（Vercel/Supabase の関数や小規模なサーバーなど）がある場合は、
> Asana の Webhook（タスクやプロジェクトに対する `POST /webhooks`。署名検証が必要）を使うことで、
> Direction D をポーリングではなく即時反映にできます。現時点ではどこにも実装されていません — 今後の
> スキル候補です。

## How to adopt this in a repo / 他のリポジトリへの導入方法

1. **Pick or create an Asana project** for the repo's issues. Note its GID (the number in its
   Asana URL, e.g. `.../project/1218379972947930`).
   / **リポジトリの Issue 用に Asana プロジェクトを選ぶか新規作成します。** その GID（Asana の URL に
   含まれる数字、例: `.../project/1218379972947930`）を控えておきます。
2. **Create an Asana Personal Access Token**: Asana → profile → Settings → Apps → "View developer
   console" → Personal access tokens → "+ Create new token". Copy it immediately - it's shown once.
   / **Asana のパーソナルアクセストークンを作成します**: Asana → プロフィール → Settings → Apps →
   「View developer console」→ Personal access tokens → 「+ Create new token」。表示は一度きりなので
   すぐにコピーしてください。
3. **Store it as a GitHub Actions secret** named `ASANA_PAT` on the repo (Settings → Secrets and
   variables → Actions → New repository secret).
   / **`ASANA_PAT` という名前で GitHub Actions のシークレットとして保存します**（Settings → Secrets
   and variables → Actions → New repository secret）。
4. **Copy both workflow files** from `Robo-Co-op/RoboDesk`'s `.github/workflows/`:
   `asana-github-sync.yml` and `asana-github-reverse-sync.yml`.
   / `Robo-Co-op/RoboDesk` の `.github/workflows/` から **両方のワークフローファイルをコピーします**:
   `asana-github-sync.yml` と `asana-github-reverse-sync.yml`。
5. **Replace the `ASANA_PROJECT_GID` value** in both files with your project's GID from step 1.
   (Not a secret — just an ID — safe to commit in plain text.)
   / 両方のファイル内の **`ASANA_PROJECT_GID` の値を手順1の GID に置き換えます**（シークレットではなく
   単なる ID なので、平文でコミットして問題ありません）。
6. Confirm the workflow permissions block grants `issues: write` (both files already declare it;
   it's what lets the workflow edit issue bodies and open/close/comment on issues).
   / ワークフローの permissions ブロックに `issues: write` が付与されていることを確認します（両ファイル
   とも既に宣言済みです。Issue 本文の編集や開閉・コメントに必要な権限です）。
7. (Optional) Add an "## Asana task" heading to your issue template, so the field has an obvious
   home in the rendered issue even though the workflow fills it in automatically.
   / （任意）Issue テンプレートに「## Asana task」の見出しを追加すると、ワークフローが自動的に値を
   埋める場合でも、表示された Issue 上でその欄の場所が分かりやすくなります。
8. Open a throwaway test issue, close it, reopen it, and manually complete its Asana task to watch
   all four directions fire - then delete the test issue and task. `docs/github-asana-sync.md` in
   RoboDesk shows exactly what each step's log output looks like when it works.
   / テスト用の使い捨て Issue を作成し、クローズ、再オープン、Asana 側での手動完了を行って、4つの方向すべてが
   動作することを確認してください。その後、テスト用の Issue とタスクは削除します。各ステップの正常時の
   ログ出力例は RoboDesk の `docs/github-asana-sync.md` を参照してください。

## Relationship to Robo Builder OS / Robo Builder OS との関係

EN: This is tooling (Robo Builder), not a lifecycle gate (Robo Builder OS). It does not change
which state an issue is in, and completing the Asana task does **not** by itself satisfy the
[Definition of Done](https://github.com/Robo-Co-op/robobuilder-os/blob/main/gates/definition-of-done.md) -
that gate still requires demonstrated acceptance criteria, a verification comment on the issue, and
so on. GitHub stays the system of record for the dev lifecycle; Asana is a downstream mirror for
stakeholders who live there. Closing the GitHub issue (by hand, or via Direction D above) is what
should reflect that the Definition of Done was actually met - not the other way around.

JP: これはツール（Robo Builder）であり、ライフサイクルのゲート（Robo Builder OS）ではありません。
Issue がどの状態にあるかを変えるものではなく、Asana タスクを完了にしただけでは
[Definition of Done](https://github.com/Robo-Co-op/robobuilder-os/blob/main/gates/definition-of-done.md)
を満たしたことにはなりません — そのゲートには、受け入れ基準の実証や Issue への検証コメントなどが依然として
必要です。GitHub は開発ライフサイクルの正のソースであり続け、Asana は Asana を利用するステークホルダー向けの
下流のミラーです。GitHub Issue のクローズ（手動、または上記 Direction D 経由）は、Definition of Done が
実際に満たされたことを反映するものであるべきで、その逆ではありません。

## Known limitations / 既知の制限事項

- EN: Only open/closed/reopened state and completion are mirrored - titles, descriptions, comments,
  assignees, and labels are not synced either direction.
  JP: 同期されるのは open/closed/reopened の状態と完了状態のみです。タイトル、説明、コメント、担当者、
  ラベルはどちらの方向にも同期されません。
- EN: Direction D is polled (~15 min), not instant, without a hosted webhook receiver.
  JP: ホスティングされた Webhook 受信環境がない限り、Direction D は約15分ごとのポーリングであり、
  即時反映ではありません。
- EN: Scoped to one Asana project per repo; doesn't fan out to multiple projects or workspaces.
  JP: リポジトリごとに1つの Asana プロジェクトに限定され、複数のプロジェクトやワークスペースには
  展開されません。
- EN: A task or issue deleted on one side isn't detected or cleaned up on the other.
  JP: 一方でタスクや Issue が削除されても、もう一方では検知・削除されません。
- EN: Extraction of the Asana task ID from the issue body is convention-based (regex on an
  `app.asana.com` URL) - if your team never pastes/receives that link in the issue body, nothing
  will sync.
  JP: Issue 本文からの Asana タスク ID の抽出は規約ベースです（`app.asana.com` の URL に対する正規表現）。
  チームが Issue 本文にそのリンクを一切貼り付けない・受け取らない場合は、何も同期されません。
