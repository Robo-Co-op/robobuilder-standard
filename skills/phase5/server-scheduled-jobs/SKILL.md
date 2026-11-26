---
name: server-scheduled-jobs
description: "[P5-7 Ship] Run cron jobs, syncs and repo-to-server deploys from a timer on your own server instead of GitHub Actions schedules, so they stop spending the org's Actions minutes. Use when: \"run this every 15 minutes\", \"add a cron workflow\", \"sync Asana/Sheets/expenses on a schedule\", \"Actions minutes ran out\", \"keep the server in sync with main\"."
origin: robobuilder
bootcamp_module: M3.code.ship
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase5)
> - **What**: Scheduled work runs on a systemd timer on a server you already have, pulling code from `main` with a read-only deploy key — not as a GitHub Actions `schedule:`
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:secret-transfer, /robobuilder:land-and-deploy, /robobuilder:cso
> - **Bootcamp**: M3.code.ship
> - **Origin**: Robo Co-op

## What

Move recurring jobs (syncs, pollers, scanners, reminders, "keep the server in step with `main`")
off GitHub Actions `schedule:` and onto a **systemd timer** on a server the team already runs.
The server fetches the repo itself with a **read-only deploy key** and runs the job from the
latest `main`. GitHub never gets a key to the server, and no inbound port is opened.

## When

Use when:
- a workflow has `on: schedule:` more often than **daily**, or you are about to add one;
- a job "keeps the server in sync" with the repo (config, prompts, instruction files);
- the org's Actions minutes or budget ran out (Actions is then blocked for **every** repo).

Keep it in Actions when:
- it reacts to a GitHub event (`push`, `pull_request`, `issues`) — CI, issue-to-task sync;
- it runs **daily or less** and finishes in a minute or two;
- there is no server to run it on. Then schedule it **hourly at most** and say why in the workflow.

## Why

On a private repo, GitHub bills **every job as at least one full minute**, however short.
A 5-second poll on `*/15` can use up to 2,880 billed minutes a month by itself — more than the
2,000 free minutes a Free-plan org gets for all of its private repos together. When the budget
is spent, Actions stops for the whole org, including CI and deploys.

| Schedule | Max runs / month | Billed minutes (≥1 per job) |
|---|---|---|
| `*/15 * * * *` | 2,880 | 2,880+ |
| hourly | 720 | 720+ |
| every 6 h | 120 | 120+ |
| daily | 30 | 30+ |

A timer on a server costs nothing extra, runs on time (GitHub delays and drops scheduled runs
under load), and its logs stay with the machine it acts on.

Robo Co-op measured this in Nov 2026: three `*/15` jobs and one hourly job used ~700–900
minutes a month — over a third of the free allowance.

## How

### 1. Pick the server and the job

The server needs `git`, `systemd` and whatever the job runs (`node`, `python3`). One server can
run many jobs; each job gets its own folder, key and secrets file.

### 2. Install (once per job, as root)

Copy this skill's `assets/` folder to the server, then:

```bash
sudo ./install-job.sh asana-sync git@github.com:<org>/<repo>.git 'hourly'
```

It creates a `scheduled-jobs` system user, installs `run-job.sh` and the units, pins GitHub's
host key (refuses on mismatch), generates a deploy key, writes
`/etc/scheduled-jobs/<job>.env` (root-only, 0600) and sets the schedule. It prints the public key.

### 3. Add the deploy key — read-only

Repo → Settings → Deploy keys → Add. **Leave "Allow write access" unticked.** Adding a key is a
repo-admin action; ask the repo owner.

### 4. Configure the job

Edit `/etc/scheduled-jobs/<job>.env`:

```
JOB_REPO=git@github.com:<org>/<repo>.git
JOB_BRANCH=main
JOB_COMMAND=npm ci --omit=dev && node scripts/asana-reverse-sync.js
JOB_TIMEOUT=600
ASANA_PAT=…          # deliver with /robobuilder:secret-transfer (apply --env-file …), never paste
```

`JOB_COMMAND` is usually the same command the workflow's `run:` step used. Values the workflow
read from `secrets.*` go in this file instead.

### 5. Test, enable, then remove the Actions schedule

```bash
sudo systemctl start scheduled-job@asana-sync.service
sudo journalctl -u scheduled-job@asana-sync -n 30
sudo systemctl enable --now scheduled-job@asana-sync.timer
```

Then open a PR that deletes the `schedule:` block from the workflow. Keep `workflow_dispatch:`
if a manual run from GitHub is still handy. **Don't run both**: two schedulers doing the same
sync can double-post.

### Syncing files from `main` to the server

For "the server should always match `main`" (prompts, agent instructions, config), don't copy
blindly: the server may have its own edits. Worked example: `Robo-Co-op/sdc-claw` `deploy/`
copies only an allowlist of files, skips any file edited on the server since the last deploy
(drift), backs up before replacing, never deletes, and its tests cover each rule.

## Safety rules

- **Read-only deploy key**, one per job, kept in the job's state folder (0700).
- **Fails closed**: if the fetch fails, the job does not run on an old checkout.
- **No overlap**: a run still going makes the next one skip (`flock`).
- **Secrets** live only in `/etc/scheduled-jobs/<job>.env` (root, 0600), loaded by systemd. Jobs
  can't read each other's.
- **Hardened unit**: no new privileges, read-only system, no `/home`, private `/tmp`, timeout.
- Anyone who can merge to the branch changes what runs on the server — same as Actions
  `schedule:`, which also runs the default branch. Review those PRs.

## Checking on it

```bash
systemctl list-timers 'scheduled-job@*'
journalctl -u 'scheduled-job@*' --since today
```

## Anti-patterns

- `schedule: */5` or `*/15` in Actions "because it's free" — it is billed per job, rounded up.
- `on: push` to all branches **and** `pull_request` — every PR push runs twice. Either
  `push: branches: [main]` + `pull_request`, or keep push-everywhere and skip the job on
  same-repo PRs (`if: github.event_name == 'push' || github.event.pull_request.head.repo.fork`).
  Add `concurrency` with `cancel-in-progress` so a new push cancels the old run.
- A poller that only checks "did anything change?" every few minutes — prefer a webhook or event.
- Pasting the job's API token into the server by hand — use `/robobuilder:secret-transfer`.
