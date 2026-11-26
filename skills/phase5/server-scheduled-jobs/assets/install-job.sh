#!/bin/bash
# install-job.sh <job> <git@github.com:org/repo.git> '<OnCalendar>' -- one-time setup, run as root.
#   e.g. sudo ./install-job.sh asana-sync git@github.com:Robo-Co-op/RoboDesk.git 'hourly'
# Idempotent: re-running updates the code/units/schedule and never replaces an existing key or .env.
# Prints the public deploy key -- add it to the repo as a READ-ONLY deploy key.
set -euo pipefail
JOB="${1:?job name}"; REPO_URL="${2:?repo ssh url}"; SCHEDULE="${3:?OnCalendar, e.g. hourly or *:0/15}"
[[ "$JOB" =~ ^[a-z0-9][a-z0-9-]{0,62}$ ]] || { echo "bad job name" >&2; exit 64; }
[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
GITHUB_ED25519="SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"   # docs.github.com/.../githubs-ssh-key-fingerprints

id scheduled-jobs >/dev/null 2>&1 || useradd --system --home-dir /var/lib/scheduled-jobs --shell /usr/sbin/nologin scheduled-jobs
install -d -m 0755 /opt/scheduled-jobs
install -m 0755 "$HERE/run-job.sh" /opt/scheduled-jobs/
install -m 0644 "$HERE/scheduled-job@.service" "$HERE/scheduled-job@.timer" /etc/systemd/system/
install -d -m 0700 /etc/scheduled-jobs
install -d -o scheduled-jobs -g scheduled-jobs -m 0700 /var/lib/scheduled-jobs "/var/lib/scheduled-jobs/$JOB"
S="/var/lib/scheduled-jobs/$JOB"

if [ ! -f "$S/deploy_key" ]; then
  sudo -u scheduled-jobs ssh-keygen -q -t ed25519 -N '' -C "$JOB@$(hostname)" -f "$S/deploy_key"
fi
if [ ! -s "$S/known_hosts" ]; then
  tmp=$(mktemp); ssh-keyscan -t ed25519 github.com 2>/dev/null > "$tmp"
  fp=$(ssh-keygen -lf "$tmp" | awk '{print $2}')
  [ "$fp" = "$GITHUB_ED25519" ] || { echo "github.com host key mismatch ($fp) -- refusing" >&2; rm -f "$tmp"; exit 1; }
  install -o scheduled-jobs -g scheduled-jobs -m 0600 "$tmp" "$S/known_hosts"; rm -f "$tmp"
fi

ENVF="/etc/scheduled-jobs/$JOB.env"
if [ ! -f "$ENVF" ]; then
  umask 077
  cat > "$ENVF" <<EOF
JOB_REPO=$REPO_URL
JOB_BRANCH=main
JOB_COMMAND=echo "set JOB_COMMAND in $ENVF"
JOB_TIMEOUT=600
# Secrets for the job go below. Deliver them with the secret-transfer skill
# (apply --env-file $ENVF), never by pasting.
EOF
fi

systemd-analyze calendar "$SCHEDULE" >/dev/null || { echo "bad OnCalendar: $SCHEDULE" >&2; exit 64; }
install -d -m 0755 "/etc/systemd/system/scheduled-job@$JOB.timer.d"
printf '[Timer]\nOnCalendar=\nOnCalendar=%s\n' "$SCHEDULE" > "/etc/systemd/system/scheduled-job@$JOB.timer.d/schedule.conf"
systemctl daemon-reload

echo
echo "Next:"
echo " 1. Add this as a READ-ONLY deploy key on the repo (Settings -> Deploy keys):"
echo "    $(cat "$S/deploy_key.pub")"
echo " 2. Set JOB_COMMAND (and deliver secrets) in $ENVF"
echo " 3. Test once:   systemctl start scheduled-job@$JOB.service && journalctl -u scheduled-job@$JOB -n 30"
echo " 4. Turn it on:  systemctl enable --now scheduled-job@$JOB.timer"
echo " 5. Delete the schedule: block from the GitHub workflow (keep workflow_dispatch if useful)."
