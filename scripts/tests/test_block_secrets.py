"""
Tests for block_secrets.py.

Design notes:
- block_secrets.py's main() depends on sys.stdin / sys.exit, so we
    import and test the internal functions path_matches_secret / content_has_secret / main directly.
- Subprocess CLI tests only assert on the exit code,
    passing JSON to a real process instead of mocking stdin (boundary tests).
- sys.stdin / sys.exit are mocked only in test_main_* (boundary only).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the script directly (no install needed)
_SCRIPT = Path(__file__).parent.parent / "block_secrets.py"
spec = importlib.util.spec_from_file_location("block_secrets", _SCRIPT)
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


# ── path_matches_secret ──────────────────────────────────────────────────────

class TestPathMatchesSecret:
    # .env family
    def test_dotenv_exact(self):
        assert bs.path_matches_secret("/project/.env") is not None

    def test_dotenv_with_suffix(self):
        assert bs.path_matches_secret("/project/.env.local") is not None

    def test_dotenv_production(self):
        assert bs.path_matches_secret(".env.production") is not None

    def test_envrc(self):
        assert bs.path_matches_secret("/home/user/.envrc") is not None

    # credentials / secrets
    def test_credentials_plain(self):
        assert bs.path_matches_secret("/home/.aws/credentials") is not None

    def test_credentials_with_suffix(self):
        assert bs.path_matches_secret("/app/db_credentials.json") is not None

    def test_secret_plural(self):
        assert bs.path_matches_secret("/app/secrets.yaml") is not None

    def test_secret_singular(self):
        assert bs.path_matches_secret("/vault/secret") is not None

    # Key-file extensions
    def test_pem(self):
        assert bs.path_matches_secret("/certs/server.pem") is not None

    def test_key(self):
        assert bs.path_matches_secret("/certs/private.key") is not None

    def test_p12(self):
        assert bs.path_matches_secret("/certs/bundle.p12") is not None

    def test_pfx(self):
        assert bs.path_matches_secret("/certs/bundle.pfx") is not None

    def test_jks(self):
        assert bs.path_matches_secret("/certs/store.jks") is not None

    def test_keystore(self):
        assert bs.path_matches_secret("/certs/app.keystore") is not None

    # SSH / AWS / gcloud
    def test_id_rsa(self):
        assert bs.path_matches_secret("/home/user/.ssh/id_rsa") is not None

    def test_id_rsa_pub(self):
        assert bs.path_matches_secret("/home/user/.ssh/id_rsa.pub") is not None

    def test_id_ed25519(self):
        assert bs.path_matches_secret("/home/user/.ssh/id_ed25519") is not None

    def test_id_ecdsa(self):
        assert bs.path_matches_secret("/home/user/.ssh/id_ecdsa") is not None

    def test_aws_credentials(self):
        assert bs.path_matches_secret("/home/user/.aws/credentials") is not None

    def test_ssh_config(self):
        assert bs.path_matches_secret("/home/user/.ssh/config") is not None

    def test_netrc(self):
        assert bs.path_matches_secret("/home/user/.netrc") is not None

    def test_gcloud_json(self):
        assert bs.path_matches_secret("/home/user/gcloud/service-account.json") is not None

    # Windows backslash -> forward slash conversion
    def test_windows_backslash_env(self):
        assert bs.path_matches_secret(r"C:\project\.env") is not None

    def test_windows_backslash_pem(self):
        assert bs.path_matches_secret(r"C:\certs\server.pem") is not None

    def test_windows_backslash_credentials(self):
        assert bs.path_matches_secret(r"C:\Users\jin\.aws\credentials") is not None

    # Non-secrets return None
    def test_normal_py(self):
        assert bs.path_matches_secret("/app/main.py") is None

    def test_normal_json(self):
        assert bs.path_matches_secret("/app/config.json") is None

    def test_readme(self):
        assert bs.path_matches_secret("/project/README.md") is None

    def test_env_in_dirname_only(self):
        # Cases where only a directory name contains .env (file name doesn't match)
        # Files under a directory named .env/ are outside the pattern
        assert bs.path_matches_secret("/project/env_config/settings.py") is None

    def test_dotenv_prefix_false_positive(self):
        # "environment.py" must not be blocked
        assert bs.path_matches_secret("/app/environment.py") is None


# ── content_has_secret ───────────────────────────────────────────────────────

class TestContentHasSecret:
    def test_openai_key(self):
        assert bs.content_has_secret("sk-abcdefghijklmnopqrstuvwxyz123456") is not None

    def test_anthropic_key(self):
        assert bs.content_has_secret("sk-ant-abcdefghijklmnopqrstu1234567890") is not None

    def test_aws_access_key(self):
        assert bs.content_has_secret("AKIAIOSFODNN7EXAMPLE") is not None

    def test_google_api_key(self):
        assert bs.content_has_secret("AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI") is not None

    def test_github_pat(self):
        assert bs.content_has_secret("ghp_" + "A" * 36) is not None

    def test_slack_token_xoxb(self):
        assert bs.content_has_secret("xoxb-1234567890-abcdefghij") is not None

    def test_slack_token_xoxp(self):
        assert bs.content_has_secret("xoxp-1234567890-abcdefghij") is not None

    def test_pem_private_key(self):
        assert bs.content_has_secret("-----BEGIN RSA PRIVATE KEY-----") is not None

    def test_pem_ec_private_key(self):
        assert bs.content_has_secret("-----BEGIN EC PRIVATE KEY-----") is not None

    def test_pem_openssh_private_key(self):
        assert bs.content_has_secret("-----BEGIN OPENSSH PRIVATE KEY-----") is not None

    def test_secret_in_middle_of_content(self):
        content = "some preamble\nAKIAIOSFODNN7EXAMPLE\nsome postamble"
        assert bs.content_has_secret(content) is not None

    # Non-secrets
    def test_empty_string(self):
        assert bs.content_has_secret("") is None

    def test_normal_python_code(self):
        code = "def hello():\n    return 'world'\n"
        assert bs.content_has_secret(code) is None

    def test_short_sk_prefix(self):
        # 19 or fewer chars after sk- must not match
        assert bs.content_has_secret("sk-short") is None


# -- main() — tool dispatch --------------------------------------------------

def _run_main(payload: dict) -> tuple[int, str]:
    """Call main() and return (exit_code, stderr_text)."""
    stdin_text = json.dumps(payload)
    stderr_buf = StringIO()
    with patch.object(sys, "stdin", StringIO(stdin_text)), \
         patch.object(sys, "stderr", stderr_buf):
        try:
            code = bs.main()
        except SystemExit as e:
            code = int(e.code)
    return code, stderr_buf.getvalue()


class TestMain:
    # Happy path: harmless files / tools
    def test_ignore_read_tool(self):
        code, _ = _run_main({"tool_name": "Read", "tool_input": {"file_path": "/app/.env"}})
        assert code == 0

    def test_ignore_bash_tool(self):
        code, _ = _run_main({"tool_name": "Bash", "tool_input": {"command": "cat .env"}})
        assert code == 0

    def test_edit_safe_file_passes(self):
        code, _ = _run_main({"tool_name": "Edit", "tool_input": {"file_path": "/app/main.py", "new_string": "x=1"}})
        assert code == 0

    def test_write_safe_file_passes(self):
        code, _ = _run_main({"tool_name": "Write", "tool_input": {"file_path": "/app/readme.md", "content": "hello"}})
        assert code == 0

    # Block: file path
    def test_edit_dotenv_blocked(self):
        code, stderr = _run_main({"tool_name": "Edit", "tool_input": {"file_path": "/project/.env"}})
        assert code == 2
        assert "BLOCKED" in stderr

    def test_write_dotenv_blocked(self):
        code, stderr = _run_main({"tool_name": "Write", "tool_input": {"file_path": "/project/.env", "content": "X=1"}})
        assert code == 2

    def test_multiedit_pem_blocked(self):
        code, _ = _run_main({"tool_name": "MultiEdit", "tool_input": {"file_path": "/certs/key.pem"}})
        assert code == 2

    # Block: content
    def test_write_with_aws_key_blocked(self):
        code, stderr = _run_main({
            "tool_name": "Write",
            "tool_input": {"file_path": "/app/config.py", "content": "KEY=AKIAIOSFODNN7EXAMPLE"},
        })
        assert code == 2
        assert "BLOCKED" in stderr

    def test_edit_new_string_openai_key_blocked(self):
        code, _ = _run_main({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/app/settings.py", "new_string": "API_KEY = 'sk-abcdefghijklmnopqrstuvwxyz'"},
        })
        assert code == 2

    # Alternate key names: "tool" / "params"
    def test_alt_key_tool_and_params(self):
        code, _ = _run_main({"tool": "Edit", "params": {"file_path": "/project/.env"}})
        assert code == 2

    # Malformed JSON -> do not block (exit 0)
    def test_malformed_json_passes(self):
        stderr_buf = StringIO()
        with patch.object(sys, "stdin", StringIO("{not valid json")), \
             patch.object(sys, "stderr", stderr_buf):
            try:
                code = bs.main()
            except SystemExit as e:
                code = int(e.code)
        assert code == 0

    # Empty stdin -> do not block
    def test_empty_stdin_passes(self):
        stderr_buf = StringIO()
        with patch.object(sys, "stdin", StringIO("")), \
             patch.object(sys, "stderr", stderr_buf):
            try:
                code = bs.main()
            except SystemExit as e:
                code = int(e.code)
        assert code == 0

    # Content scanning still runs when file_path is absent
    def test_no_path_but_secret_content_blocked(self):
        code, _ = _run_main({
            "tool_name": "Write",
            "tool_input": {"content": "AKIAIOSFODNN7EXAMPLE"},
        })
        assert code == 2

    # Neither file_path nor content has issues
    def test_no_path_no_secret_passes(self):
        code, _ = _run_main({"tool_name": "Write", "tool_input": {"content": "hello world"}})
        assert code == 0


# -- CLI boundary tests (real process) ---------------------------------------

class TestCLI:
    """
    Launch block_secrets.py directly in a subprocess and
    assert only on the exit code (the outermost boundary).
    """

    def _invoke(self, payload: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )

    def test_cli_safe_file_exit0(self):
        r = self._invoke({"tool_name": "Edit", "tool_input": {"file_path": "/app/main.py"}})
        assert r.returncode == 0

    def test_cli_dotenv_exit2(self):
        r = self._invoke({"tool_name": "Write", "tool_input": {"file_path": "/project/.env", "content": "X=1"}})
        assert r.returncode == 2
        assert "BLOCKED" in r.stderr

    def test_cli_malformed_json_exit0(self):
        r = subprocess.run(
            [sys.executable, str(_SCRIPT)],
            input="not-json",
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0
