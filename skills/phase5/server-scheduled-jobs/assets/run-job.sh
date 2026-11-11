#!/bin/bash
# run-job.sh <job> -- run one scheduled job on this server instead of in GitHub Actions.
#
# Called by scheduled-job@<job>.service. Reads its settings from the environment, which
# systemd loads from /etc/scheduled-jobs/<job>.env (root-owned, 0600 -- it may hold secrets):
#   JOB_REPO      git@github.com:<org>/<repo>.git   (fetched with a READ-ONLY deploy key)
#   JOB_BRANCH    branch to run from (default: main)
#   JOB_COMMAND   command to run inside the checkout, e.g. "node scripts/asana-reverse-sync.js"
#   JOB_TIMEOUT   max run time in seconds (default: 600)
# Everything else in the .env file is passed through to JOB_COMMAND (API tokens etc.).
#
# Fails closed: if the fetch fails, the job does NOT run on an old checkout.
set -euo pipefail

JOB="${1:-}"
[[ "$JOB" =~ ^[a-z0-9][a-z0-9-]{0,62}$ ]] || { echo "bad job name: '$JOB'" >&2; exit 64; }
STATE="${SCHEDULED_JOBS_STATE:-/var/lib/scheduled-jobs}/$JOB"
: "${JOB_REPO:?JOB_REPO not set in /etc/scheduled-jobs/$JOB.env}"
: "${JOB_COMMAND:?JOB_COMMAND not set in /etc/scheduled-jobs/$JOB.env}"
BRANCH="${JOB_BRANCH:-main}"
[[ "$BRANCH" =~ ^[A-Za-z0-9._/-]+$ ]] || { echo "bad branch: '$BRANCH'" >&2; exit 64; }

mkdir -p "$STATE"
if [ -f "$STATE/deploy_key" ]; then
  export GIT_SSH_COMMAND="ssh -i $STATE/deploy_key -o IdentitiesOnly=yes -o UserKnownHostsFile=$STATE/known_hosts -o StrictHostKeyChecking=yes -o BatchMode=yes"
fi

exec 9>"$STATE/lock"
flock -n 9 || { echo "previous run of $JOB still going -- skipping this one"; exit 0; }

REPO="$STATE/repo"
if [ ! -d "$REPO/.git" ]; then
  git clone --quiet --no-checkout --single-branch --branch "$BRANCH" "$JOB_REPO" "$REPO"
fi
git -C "$REPO" fetch --quiet origin "$BRANCH"
git -C "$REPO" checkout --quiet --force --detach FETCH_HEAD
echo "$JOB: running $(git -C "$REPO" rev-parse --short HEAD) of $BRANCH"

cd "$REPO"
exec timeout --kill-after=30 "${JOB_TIMEOUT:-600}" bash -c "$JOB_COMMAND"
