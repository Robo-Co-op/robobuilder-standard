#!/usr/bin/env python3
"""
block_secrets.py — PreToolUse hook for robobuilder.

Blocks Edit/Write/MultiEdit operations on files matching secret-bearing patterns,
and scans incoming content for likely credential strings.

Hook input: JSON on stdin with tool_name and tool_input.
Hook output:
  - exit 0 → allow
  - exit 2 with stderr message → block

Coverage:
  - File patterns: .env*, credentials*, *_credentials*, *.pem/.key, id_rsa, .aws, .ssh, .netrc, gcloud
  - Content patterns: OpenAI, Anthropic, AWS, Google, GitHub (all token types),
    Slack, Stripe (live/test), Supabase JWT, Azure connection strings,
    1Password SA tokens, PEM/private keys
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path, PurePosixPath


# --- File path patterns ---
# Match any path segment that contains the sensitive token, with optional prefix/suffix
# (e.g., db_credentials.json, app.credentials.yaml, .env.production all match).
# Doc extensions that legitimately contain words like "credentials" or "secrets"
# in their filename (architecture docs, runbooks, READMEs). Skip these.
_DOC_EXT_SUFFIX = r"(?<!\.md)(?<!\.rst)(?<!\.adoc)(?<!\.html)(?<!\.txt)"

SECRET_FILE_PATTERNS = [
    re.compile(r"(^|/)\.env(\.[^/]+)?$"),
    re.compile(r"(^|/)\.envrc$"),
    re.compile(rf"(^|/)[^/]*credentials[^/]*{_DOC_EXT_SUFFIX}$", re.IGNORECASE),
    re.compile(rf"(^|/)[^/]*secrets?[^/]*{_DOC_EXT_SUFFIX}$", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx|jks|keystore)$", re.IGNORECASE),
    re.compile(r"(^|/)id_(rsa|ed25519|ecdsa|dsa)(\.pub)?$"),
    re.compile(r"(^|/)\.aws/credentials$"),
    re.compile(r"(^|/)\.ssh/config$"),
    re.compile(r"(^|/)\.netrc$"),
    re.compile(r"(^|/)gcloud/.+\.json$"),
]

# --- Content patterns ---
SECRET_CONTENT_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                              # OpenAI
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),                        # Anthropic
    re.compile(r"AKIA[0-9A-Z]{16}"),                                 # AWS access key
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),                            # Google API key
    re.compile(r"gh[psoru]_[A-Za-z0-9]{36,}"),                       # GitHub tokens (p/s/o/r/u variants)
    re.compile(r"xox[bpsr]-[A-Za-z0-9-]{10,}"),                      # Slack tokens
    re.compile(r"sk_(live|test)_[A-Za-z0-9]{24,}"),                  # Stripe live/test secret keys
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\."),   # JWT (Supabase service role etc.)
    re.compile(r"DefaultEndpointsProtocol=https;AccountName="),       # Azure Storage connection string
    re.compile(r"ops_[A-Za-z0-9]{60,}"),                              # 1Password service account token
    re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
]

# Paths under which CONTENT-pattern matching is skipped because they legitimately
# contain secret-shaped strings (test fixtures, sample payloads, regex demos).
# File-name (SECRET_FILE_PATTERNS) checks still apply — a fixture file named
# `.env` is still blocked.
TEST_FIXTURE_PATTERNS = [
    re.compile(r"(^|/)tests?/"),
    re.compile(r"(^|/)__tests?__/"),
    re.compile(r"(^|/)fixtures?/"),
    re.compile(r"(^|/)test_[^/]+\.py$"),
    re.compile(r"(^|/)[^/]+_test\.py$"),
    re.compile(r"(^|/)conftest\.py$"),
    re.compile(r"(^|/)[^/]+\.spec\.(ts|js|tsx|jsx)$"),
    re.compile(r"(^|/)[^/]+\.test\.(ts|js|tsx|jsx)$"),
]


def is_test_fixture(path_str: str) -> bool:
    """True if the path looks like a test fixture / mock data location."""
    if not path_str:
        return False
    s = path_str.replace("\\", "/")
    return any(pat.search(s) for pat in TEST_FIXTURE_PATTERNS)


def _audit_log(reason: str, path: str | None) -> None:
    """Append a one-line audit entry. Silent if logging fails.

    Uses Path.home() which resolves via OS APIs (pwd.getpwuid on POSIX, registry on
    Windows) — not directly hijackable by HOME/USERPROFILE env manipulation.
    """
    try:
        log_dir = Path.home() / ".claude" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "block_secrets.log", "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now().isoformat()} BLOCKED path={path!r} reason={reason}\n")
    except Exception:
        pass


def block(reason: str, path: str | None = None) -> None:
    _audit_log(reason, path)
    sys.stderr.write(f"[robobuilder/block_secrets] BLOCKED: {reason}\n")
    sys.exit(2)


def path_matches_secret(path_str: str) -> str | None:
    if not path_str:
        return None
    p = PurePosixPath(path_str.replace("\\", "/"))
    s = str(p)
    for pat in SECRET_FILE_PATTERNS:
        if pat.search(s):
            return pat.pattern
    return None


def content_has_secret(content: str) -> str | None:
    if not content:
        return None
    for pat in SECRET_CONTENT_PATTERNS:
        if pat.search(content):
            return f"matches {pat.pattern!r}"
    return None


def _check(path: str, content: str) -> None:
    """Run both path and content checks for a single (path, content) pair.

    Test fixtures (`tests/`, `fixtures/`, `*_test.py`, etc.) skip CONTENT scanning
    because they legitimately contain secret-shaped strings for testing. The
    file-name check still applies — a fixture literally named `.env` is still
    blocked.

    NOTE: SECRET_FILE_PATTERNS doc-extension exclusion uses negative lookbehinds
    for `.md`/`.rst`/`.adoc`/`.html`/`.txt`. Compound extensions like `.md.bak`
    bypass the exclusion (the lookbehind sees `.bak`, not `.md`). Accepted as a
    low-frequency edge case — see docs/CONTRIBUTING.md.
    """
    hit = path_matches_secret(path)
    if hit:
        block(f"file path {path!r} matches secret-file pattern {hit!r}. Use 1Password CLI (`op`) instead.", path)
    if is_test_fixture(path):
        return
    hit = content_has_secret(content)
    if hit:
        block(f"content {hit}; likely contains a credential. Use 1Password CLI (`op`) and reference at runtime.", path)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed input → don't block

    tool_name = payload.get("tool_name") or payload.get("tool") or ""
    params = payload.get("tool_input") or payload.get("params") or {}

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        return 0

    path = params.get("file_path") or params.get("path") or ""

    if tool_name == "MultiEdit":
        # MultiEdit packs N edits into an array; _check() with empty content runs
        # path-only validation, then we scan each edit's new content individually.
        _check(path, "")
        for edit in params.get("edits") or []:
            _check(path, edit.get("new_string", "") or edit.get("new_text", ""))
        return 0

    # Edit / Write: single content field
    content = (
        params.get("content")
        or params.get("new_string")
        or params.get("new_text")
        or ""
    )
    _check(path, content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
