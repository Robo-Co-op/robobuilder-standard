"""The DEFENCE grep has to fire on guards and stay quiet on words that only look like them.

`diff-review` reviews small diffs inline, without subagents, but only when the diff is
neither a defence nor something that renders. So DEFENCE is the gate that keeps a small
guard change from getting a one-pass review. Ported from robobuilder-lite 1.5.0, where
the first version of this grep over-fired on almost everything: hunk headers and file
paths, "auth" inside "author", "token" inside every LLM token count, and every changed
test and doc.

The fix has to cut those false hits without opening an under-fire hole. The likeliest
hole is camelCase: a naive word-boundary grep sees `requireAuth` or `csrfToken` as a
single word and stops matching it. So this suite runs the skill's own pipeline, taken
straight from SKILL.md, against concrete diffs. The tests check what the grep actually
does, not what the prose says it does.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "phase4" / "diff-review" / "SKILL.md"

BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash to run the skill's pipeline")


def defence_filter() -> str:
    """The DEFENCE pipeline from SKILL.md, minus its leading `git diff` stage."""
    text = SKILL.read_text(encoding="utf-8")
    block = re.search(r"# Is it a defence\?.*?&& echo DEFENCE", text, re.DOTALL)
    assert block, "diff-review/SKILL.md has no '# Is it a defence?' block ending in '&& echo DEFENCE'"
    lines = block.group(0).splitlines()
    first_pipe = next(i for i, line in enumerate(lines) if line.lstrip().startswith("|"))
    # Drop the comment and `git diff` lines. Keep the filter stages, so the test reads
    # the diff from stdin instead of from a repo.
    return "cat \\\n" + "\n".join(lines[first_pipe:])


def fires(diff: str) -> bool:
    out = subprocess.run(
        [BASH, "-c", defence_filter()], input=diff, capture_output=True, text=True
    )
    return "DEFENCE" in out.stdout


def hunk(path: str, *body: str) -> str:
    return (
        f"diff --git a/{path} b/{path}\n"
        f"--- a/{path}\n+++ b/{path}\n"
        "@@ -1,0 +1,1 @@\n" + "\n".join(body) + "\n"
    )


MUST_FIRE = {
    "camelCase guard call": ("src/api/route.ts", "+  await requireAuth(req);"),
    "camelCase token": ("src/api/route.ts", "+  const csrfToken = req.headers.get('x-csrf');"),
    "rate limiter class": ("src/lib/limit.ts", "+export class RateLimiter {"),
    "snake_case limiter": ("app/limits.py", "+def rate_limit(key):"),
    "forwarded header": ("src/lib/ip.ts", "+  const ip = h.get('X-Forwarded-For');"),
    "RLS policy": ("supabase/migrations/1.sql", "+create policy owner_only on notes"),
    "password hashing": ("src/auth.ts", "+  const hashed = await hashPassword(pw);"),
    "sanitiser": ("src/html.ts", "+  return sanitizeHtml(input);"),
    "JWT verify": ("src/session.ts", "+  const claims = verifyJwt(bearer);"),
    "SCREAMING secret": ("src/env.ts", "+const STRIPE_SECRET = process.env.S;"),
    "token bucket": ("src/bucket.go", "+type tokenBucket struct {"),
    # Deleting a guard is the most dangerous change a defence can get, and the
    # only one that shows up purely as removed lines.
    "deleted guard": ("src/api/route.ts", "-  await requireAuth(req);"),
    "deleted RLS policy": ("supabase/migrations/2.sql", "-create policy owner_only on notes"),
}

MUST_NOT_FIRE = {
    "author is not auth": ("src/blog.ts", "+  const author = post.author;"),
    "LLM token count": ("src/llm.ts", "+  const tokenCount = usage.tokenCount;"),
    "LLM max tokens": ("src/llm.ts", "+  max_tokens: 1024, inputTokens, outputTokens,"),
    "removed doc line": ("docs/SECURITY.md", "-Every route calls requireAuth first."),
    "test file": ("src/auth.test.ts", "+  expect(requireAuth).toThrow();"),
    "python test file": ("tests/test_auth.py", "+def test_rate_limit(): pass"),
    "doc file": ("docs/SECURITY.md", "+Every route calls requireAuth first."),
    "unrelated code": ("src/cart.ts", "+  const total = items.reduce(sum, 0);"),
}


@pytest.mark.parametrize("case", sorted(MUST_FIRE))
def test_defence_grep_fires_on_guards(case):
    path, line = MUST_FIRE[case]
    assert fires(hunk(path, line)), f"DEFENCE did not fire on {case}: {line!r} in {path}"


@pytest.mark.parametrize("case", sorted(MUST_NOT_FIRE))
def test_defence_grep_ignores_lookalikes(case):
    path, line = MUST_NOT_FIRE[case]
    assert not fires(hunk(path, line)), f"DEFENCE fired on {case}: {line!r} in {path}"


def test_headers_alone_do_not_fire():
    """File paths and hunk headers name auth code without changing it."""
    diff = (
        "diff --git a/src/auth/guard.ts b/src/auth/guard.ts\n"
        "--- a/src/auth/guard.ts\n+++ b/src/auth/guard.ts\n"
        "@@ -10,0 +11,1 @@ export function requireAuth(req) {\n"
        "+  const total = items.length;\n"
    )
    assert not fires(diff)


def test_deleted_file_header_does_not_fire_and_deleted_test_file_is_skipped():
    diff = (
        "diff --git a/src/auth/old.test.ts b/src/auth/old.test.ts\n"
        "deleted file mode 100644\n"
        "--- a/src/auth/old.test.ts\n+++ /dev/null\n"
        "@@ -1,1 +0,0 @@\n"
        "-  expect(requireAuth(req)).toThrow();\n"
    )
    assert not fires(diff)


def test_one_guard_line_among_tests_and_docs_still_fires():
    diff = (
        hunk("docs/README.md", "+requireAuth everywhere")
        + hunk("src/auth.spec.ts", "+it('rejects', () => requireAuth())")
        + hunk("src/api/route.ts", "+  if (!session) return deny(401);", "+  checkPermission(user);")
    )
    assert fires(diff)
