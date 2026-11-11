---
name: secret-transfer
description: "[P5-6 Ship] Deliver API keys, tokens and passwords from GitHub secrets to a server's .env without ever exposing them. Use when: \"add the key to the server\", \"update .env\", \"deploy secrets\", \"rotate a token\"."
origin: robobuilder
bootcamp_module: M3.code.ship
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase5)
> - **What**: Move secrets from GitHub Actions secrets to a machine encrypted end to end — never in chat, logs or artifacts
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:land-and-deploy, /robobuilder:guard, /robobuilder:cso
> - **Bootcamp**: M3.code.ship
> - **Origin**: Robo Co-op

## What

Deliver secrets (API keys, tokens, passwords, connection strings) from a repo's **GitHub Actions
secrets** to the machine that needs them, **encrypted end to end**. The plaintext value never
appears in chat, a terminal, CI logs, a CI artifact, or on the laptop that runs the transfer.

## When

Use when:
- a server (VM, bot host, self-hosted runner) needs a new or rotated value in its `.env`;
- someone is about to paste a key into Slack, an issue, a PR or an AI chat "just to move it";
- a workflow uploads secrets as an artifact, or "encodes" them with base64 (base64 is plaintext).

Do **not** use when:
- the platform already has a secret store wired to the deploy (Vercel/Netlify/Fly/Cloud Run env
  vars, GitHub Environments used directly by the deploy job). Set the value there instead;
- the value is not a secret (URLs, feature flags). Use repo **variables** for those.

## Why

A secret is exposed the moment it is readable anywhere it does not need to be. The common
"temporary" paths — pasting into chat, `echo`-ing in CI, uploading a base64 artifact — leave
copies in places nobody rotates or audits. Here the receiving machine generates its own keypair
and only its **public** certificate leaves it. GitHub encrypts the named secrets to that
certificate (OpenSSL CMS, RSA-4096 + AES-256-GCM), and only the receiving machine can open the
result. A tampered ciphertext fails to decrypt instead of producing a wrong value.

## How

Bundled files (copied into the project in step 1):

| Asset | Goes to | Role |
|---|---|---|
| `assets/secret-transfer.yml` | `.github/workflows/` | Encrypts only the named secrets, behind guardrails |
| `assets/send.sh` | `scripts/secret-transfer/` | Sender: one command does the whole round trip |
| `assets/secret-receive.py` | `scripts/secret-transfer/` | Receiver: `init` / `list` / `apply` / `export`; never prints values |

**1. Install into the project** (once per repo, through a normal branch and PR):

```bash
ST="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}/skills/phase5/secret-transfer/assets"
[ -f "$ST/send.sh" ] || { echo "secret-transfer assets not found at $ST"; return 1 2>/dev/null || exit 1; }
mkdir -p .github/workflows scripts/secret-transfer
cp "$ST/secret-transfer.yml" .github/workflows/secret-transfer.yml
cp "$ST/send.sh" "$ST/secret-receive.py" scripts/secret-transfer/
chmod +x scripts/secret-transfer/send.sh scripts/secret-transfer/secret-receive.py
```

**2. Set the guardrails** (repo variables, not secrets). The workflow **fails closed** without them:

```bash
# who may trigger transfers (GitHub logins)
gh variable set SECRET_TRANSFER_ALLOWED_ACTORS --body "login-one,login-two"
# which machines may receive: create the recipient keypair and read its public fingerprint
ssh <host> 'sudo python3 - init' < scripts/secret-transfer/secret-receive.py 2>&1 >/dev/null | grep -i fingerprint
gh variable set SECRET_TRANSFER_ALLOWED_CERTS --body "<fingerprint>[,<another>]"
```
It also only runs from the default branch, and every run writes an audit summary (who, which
recipient, which secret **names**).

**3. Transfer** (after the workflow is merged to the default branch):

```bash
scripts/secret-transfer/send.sh <host> NAME_ONE,NAME_TWO list          # names + lengths only
scripts/secret-transfer/send.sh <host> PROD_DB_URL apply \
  --env-file /srv/app/.env --map PROD_DB_URL=DATABASE_URL             # backup first, 0600, owner kept
scripts/secret-transfer/send.sh <host> GCP_SA_JSON export --out /root/sa.json   # multi-line values
```
`send.sh` dispatches the workflow, waits, downloads the ciphertext, copies it to the host,
decrypts there, then deletes the GitHub artifact and shreds the temp files. Use `local` as the
host to receive on the current machine.

**4. Make the service pick it up** the way its runbook says (reload, or a hot-reloadable config).
Do not cold-restart production just to load an env var if the service has a safer path.

**5. Verify by name, never by value**: `list`, or `grep -o '^[A-Z_]*=' <env-file>`, plus a real
health check of the feature that uses the secret.

**Rules while doing this:** never `echo`/`cat`/print a secret; never ask a human to paste one into
chat; if a value is ever exposed, rotate it at the provider and update the GitHub secret.

**Known limits (state them in the PR):** anyone with write access can still reach Actions secrets
by writing their own workflow, so keep write access small. On a paid GitHub plan, also put the
secrets in an Environment with **required reviewers**. On the server, `.env` is plaintext guarded
by file permissions. Use a managed secret store when the risk level calls for it.

## Example

A Robo Co-op Slack bot on a GCP VM needs a new Gemini API key. The engineer adds it as the GitHub
secret `BOT_GEMINI_KEY`, installs this skill's files into the bot repo through a PR, sets
`SECRET_TRANSFER_ALLOWED_ACTORS` to themselves and the tech lead, and approves the VM's
certificate fingerprint. Then:
`scripts/secret-transfer/send.sh bot-vm BOT_GEMINI_KEY apply --env-file /home/bot/.env --map BOT_GEMINI_KEY=GEMINI_API_KEY`.
The run page records who sent which name to which machine, and the key never appeared anywhere
readable.

## Anti-pattern

- "Just DM me the key" / pasting a token into an AI chat to have it set up the server.
- A workflow that `echo`s secrets, or uploads them as an artifact "base64-encoded for safety".
- Leaving `SECRET_TRANSFER_ALLOWED_CERTS` broad or stale. Remove fingerprints of retired machines.
- Printing a value to "check it arrived". Check the name and the length instead.
- Keeping the plaintext export file around after use (`shred -u` it).

## See Also

- `/robobuilder:land-and-deploy` — the deploy this usually precedes
- `/robobuilder:cso` — security review that should flag plaintext secret paths
- `/robobuilder:guard` — safety hooks for destructive commands
- Robo Builder OS hard rule `no-plaintext-secret-transit` and the Production Gate secrets item
- Bootcamp M3.code.ship
