"""server-scheduled-jobs must run the latest main, never an old checkout -- tested by behaviour.

run-job.sh replaces a GitHub Actions cron. Its failure modes are quiet: a fetch that fails and
a job that keeps running yesterday's code, or two overlapping runs double-posting a sync. These
tests drive the shipped script against a local git "remote".
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "skills" / "phase5" / "server-scheduled-jobs" / "assets"
RUN = ASSETS / "run-job.sh"

pytestmark = pytest.mark.skipif(
    sys.platform.startswith("win") or not all(shutil.which(t) for t in ("bash", "git", "flock", "timeout")),
    reason="needs POSIX bash, git, flock and timeout (present on the CI runner)",
)


def _git(*a, cwd):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


@pytest.fixture()
def origin(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    _git("init", "-q", "-b", "main", cwd=src)
    (src / "job.sh").write_text('echo "ran v1" >> "$OUT"\n')
    _git("add", ".", cwd=src)
    _git("commit", "-q", "-m", "v1", cwd=src)
    return src


def _run(tmp_path, origin, job="demo", **env):
    out = tmp_path / "out.txt"
    full = {**os.environ, "SCHEDULED_JOBS_STATE": str(tmp_path / "state"), "OUT": str(out),
            "JOB_REPO": str(origin), "JOB_COMMAND": "bash job.sh", **env}
    r = subprocess.run(["bash", str(RUN), job], env=full, capture_output=True, text=True)
    return r, (out.read_text() if out.exists() else "")


def test_runs_the_job_from_the_latest_main(tmp_path, origin):
    r, out = _run(tmp_path, origin)
    assert r.returncode == 0, r.stderr
    assert out == "ran v1\n"
    (origin / "job.sh").write_text('echo "ran v2" >> "$OUT"\n')
    _git("commit", "-qam", "v2", cwd=origin)
    r, out = _run(tmp_path, origin)
    assert r.returncode == 0, r.stderr
    assert out.splitlines()[-1] == "ran v2"


def test_failed_fetch_does_not_run_an_old_checkout(tmp_path, origin):
    assert _run(tmp_path, origin)[0].returncode == 0
    shutil.rmtree(origin)
    r, out = _run(tmp_path, origin)
    assert r.returncode != 0
    assert out == "ran v1\n"


def test_overlapping_run_is_skipped_not_doubled(tmp_path, origin):
    assert _run(tmp_path, origin)[0].returncode == 0
    lock = tmp_path / "state" / "demo" / "lock"
    holder = subprocess.Popen(["flock", str(lock), "sleep", "5"])
    try:
        import time; time.sleep(0.5)
        r, out = _run(tmp_path, origin)
        assert r.returncode == 0 and "skipping" in r.stdout
        assert out == "ran v1\n"
    finally:
        holder.kill()


@pytest.mark.parametrize("job", ["../etc", "Bad", "", "a b", "x;rm"])
def test_rejects_bad_job_names(tmp_path, origin, job):
    r, out = _run(tmp_path, origin, job=job)
    assert r.returncode == 64 and out == ""


def test_timeout_stops_a_hung_job(tmp_path, origin):
    r, _ = _run(tmp_path, origin, JOB_COMMAND="sleep 30", JOB_TIMEOUT="1")
    assert r.returncode == 124


def test_units_point_at_the_shipped_paths():
    svc = (ASSETS / "scheduled-job@.service").read_text()
    assert "ExecStart=/opt/scheduled-jobs/run-job.sh %i" in svc
    assert "EnvironmentFile=/etc/scheduled-jobs/%i.env" in svc
    assert "User=scheduled-jobs" in svc and "NoNewPrivileges=yes" in svc
    inst = (ASSETS / "install-job.sh").read_text()
    assert "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU" in inst
    assert "Allow write access" not in inst or "READ-ONLY" in inst
