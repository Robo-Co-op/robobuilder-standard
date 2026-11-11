#!/usr/bin/env bash
# Sender side of the encrypted secret transfer (robobuilder `secret-transfer` skill).
#
# Moves GitHub Actions secrets to a recipient machine without the plaintext ever appearing
# in GitHub logs/artifacts, on this machine, or in chat:
#   1. recipient creates/keeps its keypair and hands back only its PUBLIC cert
#   2. the `secret-transfer.yml` workflow encrypts the named secrets to that cert
#   3. the ciphertext artifact is copied to the recipient and deleted from GitHub
#   4. the recipient decrypts locally and applies/lists/exports
#
# Usage:
#   send.sh <ssh-host|local> <SECRET[,SECRET...]> <receiver-cmd> [receiver args...]
#
# Examples:
#   # list what arrived (names + lengths only)
#   send.sh prod-server STRIPE_SECRET_KEY,DATABASE_URL list
#   # write into an env file, renaming on the way
#   send.sh prod-server PROD_DATABASE_URL apply \
#       --env-file /srv/app/.env --map PROD_DATABASE_URL=DATABASE_URL
#
# Env: REPO (default: the GitHub repo of the current checkout), RECV_SUDO (default "sudo"; set "" to run the
#      receiver as the ssh user, which then uses that user's own key dir).
# Needs: gh (authenticated, repo write access to dispatch workflows), ssh, python3 on recipient.
set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)}"
[ -n "$REPO" ] || { echo "cannot detect the GitHub repo; run inside a checkout or set REPO=owner/name" >&2; exit 2; }
RECV_SUDO="${RECV_SUDO-sudo}"
WORKFLOW="secret-transfer.yml"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECEIVER="$HERE/secret-receive.py"

[ $# -ge 3 ] || { sed -n '2,25p' "$0"; exit 2; }
HOST="$1"; NAMES="$2"; shift 2
[[ "$NAMES" =~ ^[A-Z0-9_]+(,[A-Z0-9_]+)*$ ]] || { echo "secret names must be UPPER_SNAKE_CASE, comma-separated" >&2; exit 2; }
[ -f "$RECEIVER" ] || { echo "missing $RECEIVER" >&2; exit 1; }

# Run the receiver (streamed from this checkout, so the recipient needs no install).
recv() {
  local q; q=$(printf ' %q' "$@")
  if [ "$HOST" = local ]; then
    $RECV_SUDO python3 - "$@" < "$RECEIVER"
  else
    ssh -o BatchMode=yes "$HOST" "$RECV_SUDO python3 -$q" < "$RECEIVER"
  fi
}

WORK="$(mktemp -d)"; chmod 700 "$WORK"
RUN_ID=""; REMOTE_FILE=""
cleanup() {
  rm -rf "$WORK"
  if [ -n "$RUN_ID" ]; then
    for a in $(gh api "repos/$REPO/actions/runs/$RUN_ID/artifacts" -q '.artifacts[].id' 2>/dev/null); do
      gh api -X DELETE "repos/$REPO/actions/artifacts/$a" >/dev/null 2>&1 && echo "deleted GitHub artifact $a" >&2
    done
  fi
  if [ -n "$REMOTE_FILE" ]; then
    if [ "$HOST" = local ]; then shred -u "$REMOTE_FILE" 2>/dev/null || rm -f "$REMOTE_FILE"
    else ssh -o BatchMode=yes "$HOST" "shred -u '$REMOTE_FILE' 2>/dev/null || rm -f '$REMOTE_FILE'"; fi
  fi
}
trap cleanup EXIT

echo "[1/4] recipient public certificate ($HOST)" >&2
CERT_B64="$(recv init | tail -n 1)"
[ -n "$CERT_B64" ] || { echo "no certificate returned" >&2; exit 1; }

echo "[2/4] dispatching $WORKFLOW for: $NAMES" >&2
START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
gh workflow run "$WORKFLOW" --repo "$REPO" -f secret_names="$NAMES" -f recipient_cert="$CERT_B64" >/dev/null
for _ in $(seq 1 30); do
  RUN_ID="$(gh run list --repo "$REPO" --workflow "$WORKFLOW" --event workflow_dispatch --limit 10 \
            --json databaseId,createdAt -q "[.[] | select(.createdAt >= \"$START\")] | last | .databaseId // empty")"
  [ -n "$RUN_ID" ] && break; sleep 2
done
[ -n "$RUN_ID" ] || { echo "could not find the workflow run" >&2; exit 1; }
echo "      run $RUN_ID" >&2
gh run watch "$RUN_ID" --repo "$REPO" --exit-status >/dev/null || { echo "workflow failed: gh run view $RUN_ID --repo $REPO --log-failed" >&2; exit 1; }

echo "[3/4] fetching ciphertext and moving it to $HOST" >&2
gh run download "$RUN_ID" --repo "$REPO" -n secrets-encrypted -D "$WORK" >/dev/null
if [ "$HOST" = local ]; then
  REMOTE_FILE="$(mktemp)"; cp "$WORK/secrets.cms" "$REMOTE_FILE"
else
  REMOTE_FILE="$(ssh -o BatchMode=yes "$HOST" 'f=$(mktemp); cat > "$f"; echo "$f"' < "$WORK/secrets.cms")"
fi

echo "[4/4] decrypting on $HOST: $*" >&2
CMD="$1"; shift
recv "$CMD" "$REMOTE_FILE" "$@"
