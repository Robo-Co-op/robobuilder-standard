# robobuilder hook script tests

Unit tests for the 4 Python scripts that back the plugin's lifecycle hooks.

## Run

```bash
cd ~/.claude/plugins/robobuilder/scripts
python -m pytest tests/ -v
```

## Coverage

- `test_block_secrets.py` — the PreToolUse hook that blocks secret writes
- `test_auto_format.py` — the PostToolUse hook that runs language formatters
- `test_memory_consolidate.py` — the PreCompact / SessionEnd hook
- `test_notification.py` — the Notification / SessionStart hook (includes injection-sanitization tests)

## Conventions

- **Secret-shaped fixtures built at runtime.** The tests construct attack strings (e.g., `"AKIA" + "I"*16`) inside the test functions rather than embedding the literal patterns. This prevents `block_secrets.py` from blocking edits to the test files themselves when Claude works on this codebase in-session.
- **No real subprocess.** External formatters (ruff, prettier, etc.) are monkey-patched. Tests do not require `ruff`, `prettier`, etc. to be installed.
- **Per-test temp dirs.** Memory and filesystem outputs use `tmp_path` fixtures; tests don't write to the user's home.

## Adding tests

Follow the conventions above and put them under `tests/test_<script>.py`. The `conftest.py` provides the `run_script` and `tmp_memory_dir` fixtures.
