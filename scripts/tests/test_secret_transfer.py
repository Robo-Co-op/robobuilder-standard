"""secret-transfer must keep secrets encrypted and fail closed -- tested by behaviour.

The skill ships a workflow whose job is to hand secrets to exactly one machine. A
workflow like that is dangerous in proportion to how quietly it can be wrong: a guard
that "exists" but lets an unknown actor through, or a bundle that includes every repo
secret instead of the named ones, looks identical to a working one until it leaks.

So these tests run the workflow's own shell steps (extracted from the YAML, not
re-typed) against fake secrets, then decrypt with the shipped receiver.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "skills" / "phase5" / "secret-transfer" / "assets"
WORKFLOW = ASSETS / "secret-transfer.yml"
RECEIVER = ASSETS / "secret-receive.py"

pytestmark = pytest.mark.skipif(
    sys.platform.startswith("win") or not all(shutil.which(t) for t in ("bash", "jq", "openssl")),
    reason="needs POSIX bash, jq and openssl (present on the CI runner)",
)


def _steps():
    wf = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return [s for s in wf["jobs"]["encrypt"]["steps"] if "run" in s]


GUARD, ENCRYPT = (s["run"] for s in _steps()[:2])


def _bash(script, cwd, env):
    full = {**os.environ, "GITHUB_STEP_SUMMARY": str(cwd / "summary.md"), **env}
    return subprocess.run(["bash", "-c", script], cwd=cwd, env=full, capture_output=True, text=True)


def _recv(*args, cwd):
    return subprocess.run([sys.executable, str(RECEIVER), *args], cwd=cwd, capture_output=True, text=True)


@pytest.fixture()
def recipient(tmp_path):
    keys = tmp_path / "keys"
    r = _recv("init", "--dir", str(keys), cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    fp = next(l.split("=", 1)[1] for l in r.stderr.splitlines() if "Fingerprint" in l)
    return {"dir": tmp_path, "keys": keys, "cert": r.stdout.strip().splitlines()[-1], "fp": fp}


def _guard_env(rc, **over):
    env = {"ACTOR": "alice", "REF": "refs/heads/main", "DEFAULT_REF": "refs/heads/main",
           "ALLOWED_ACTORS": "Alice, bob", "ALLOWED_CERTS": rc["fp"].lower(),
           "CERT_B64": rc["cert"], "NAMES": "A_KEY"}
    env.update(over)
    return env


def test_receiver_private_key_is_owner_only(recipient):
    assert oct((recipient["keys"] / "key.pem").stat().st_mode & 0o777) == "0o600"
    assert oct(recipient["keys"].stat().st_mode & 0o777) == "0o700"


def test_guard_passes_allowed_actor_and_recipient(recipient):
    r = _bash(GUARD, recipient["dir"], _guard_env(recipient))
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("override, why", [
    ({"REF": "refs/heads/feature"}, "non-default branch"),
    ({"ACTOR": "mallory"}, "actor not allowed"),
    ({"ALLOWED_ACTORS": ""}, "no actors configured"),
    ({"ALLOWED_CERTS": "AA:BB"}, "recipient not approved"),
    ({"ALLOWED_CERTS": ""}, "no recipients configured"),
])
def test_guard_fails_closed(recipient, override, why):
    r = _bash(GUARD, recipient["dir"], _guard_env(recipient, **override))
    assert r.returncode != 0, f"guard let through: {why}"


def _encrypt(rc, names, secrets):
    env = {"ALL_SECRETS": json.dumps(secrets), "NAMES": names, "CERT_B64": rc["cert"], "GITHUB_RUN_ID": "1"}
    return _bash(ENCRYPT, rc["dir"], env)


def test_only_named_secrets_are_encrypted_and_values_never_logged(recipient):
    secrets = {"github_token": "ghs_x", "A_KEY": "alpha-value-123", "B_KEY": "b value", "OTHER": "nope"}
    r = _encrypt(recipient, " A_KEY, B_KEY ", secrets)
    assert r.returncode == 0, r.stdout + r.stderr
    for v in secrets.values():
        assert v not in r.stdout + r.stderr
    out = _recv("export", "secrets.cms", "--dir", str(recipient["keys"]), "--out", "b.json", cwd=recipient["dir"])
    assert out.returncode == 0, out.stderr
    assert json.loads((recipient["dir"] / "b.json").read_text())["secrets"] == {"A_KEY": "alpha-value-123", "B_KEY": "b value"}
    listed = _recv("list", "secrets.cms", "--dir", str(recipient["keys"]), cwd=recipient["dir"])
    assert "alpha-value-123" not in listed.stdout and "A_KEY" in listed.stdout


@pytest.mark.parametrize("names", ["MISSING_KEY", "A_KEY;rm -rf /", ""])
def test_encrypt_rejects_unknown_or_malformed_names(recipient, names):
    r = _encrypt(recipient, names, {"A_KEY": "a"})
    assert r.returncode != 0
    assert not (recipient["dir"] / "secrets.cms").exists()


def test_apply_updates_env_file_with_backup_and_0600(recipient):
    assert _encrypt(recipient, "A_KEY,B_KEY", {"A_KEY": "fresh-9zq", "B_KEY": "with space"}).returncode == 0
    env = recipient["dir"] / "app.env"
    env.write_text("KEEP=1\nA_KEY=old\n")
    r = _recv("apply", "secrets.cms", "--dir", str(recipient["keys"]), "--env-file", str(env),
              "--map", "B_KEY=RENAMED", cwd=recipient["dir"])
    assert r.returncode == 0, r.stderr
    assert env.read_text() == "KEEP=1\nA_KEY=fresh-9zq\nRENAMED='with space'\n"
    assert oct(env.stat().st_mode & 0o777) == "0o600"
    assert list(recipient["dir"].glob("app.env.bak-secret-transfer-*"))
    assert "fresh-9zq" not in r.stdout + r.stderr and "with space" not in r.stdout + r.stderr


def test_wrong_key_and_tampered_ciphertext_do_not_decrypt(recipient):
    assert _encrypt(recipient, "A_KEY", {"A_KEY": "a"}).returncode == 0
    other = recipient["dir"] / "other"
    _recv("init", "--dir", str(other), cwd=recipient["dir"])
    assert _recv("list", "secrets.cms", "--dir", str(other), cwd=recipient["dir"]).returncode != 0
    blob = bytearray((recipient["dir"] / "secrets.cms").read_bytes())
    blob[-20] ^= 1
    (recipient["dir"] / "t.cms").write_bytes(bytes(blob))
    assert _recv("list", "t.cms", "--dir", str(recipient["keys"]), cwd=recipient["dir"]).returncode != 0
