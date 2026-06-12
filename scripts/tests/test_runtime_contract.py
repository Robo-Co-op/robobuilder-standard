from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_skills_do_not_hardcode_robobuilder_home_paths():
    offenders = []
    for path in sorted((REPO_ROOT / "skills").rglob("SKILL.md")):
        text = path.read_text()
        for needle in ("~/.robobuilder", "$HOME/.robobuilder", "~/.robobuilder-dev"):
            if needle in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)} contains {needle}")

    assert offenders == []


def test_runtime_aware_skills_reference_runtime_contract():
    runtime_skills = [
        path
        for path in sorted((REPO_ROOT / "skills").rglob("SKILL.md"))
        if "ROBOBUILDER_STATE_ROOT" in path.read_text()
    ]

    assert runtime_skills
    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in runtime_skills
        if "docs/RUNTIME.md" not in path.read_text()
    ]

    assert missing == []


def test_runtime_state_paths_are_quoted_in_shell_snippets():
    offenders = []
    for path in sorted((REPO_ROOT / "skills").rglob("SKILL.md")):
        text = path.read_text()
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "$ROBOBUILDER_STATE_ROOT/projects/$SLUG/" not in line:
                continue
            stripped = line.strip()
            if not stripped.startswith(("if ", "[ ", "cat ", "echo ", "mkdir ", "tail ", "ls ")):
                continue
            if '"$ROBOBUILDER_STATE_ROOT/projects/$SLUG/' not in line:
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}: {stripped}")

    assert offenders == []
