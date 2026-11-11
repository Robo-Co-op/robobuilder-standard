---
name: diff-review
description: "[P4-1 Review] Daily-driver diff review. Reviews the current branch's diff with 3 parallel subagents (code-simplifier / test-writer / security-auditor) and merges their findings into one prioritized fix list"
user-invocable: true
argument-hint: "[--base <branch>] override the target branch/commit range"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
origin: jin-custom
bootcamp_module: M3.code.review
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase4)
> - **What**: Daily-driver diff review — 3 parallel subagents (simplification / tests / security) merged into one prioritized fix list.
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:cross-review, /robobuilder:grill, /robobuilder:playbook-review-deep
> - **Bootcamp**: M3.code.review
> - **Origin**: Robo Co-op (Jin Kim)


# /diff-review — 3-Agent Parallel Review

Review the current branch's diff (vs `main`) with **subagents running in parallel**.

## Steps
1. Get an overview with `git diff main...HEAD --stat` and `git diff main...HEAD`
2. **Ask the diff three questions.** Do not decide these from memory or from what the
   change felt like — run them:

   ```sh
   # Is it a defence? Added lines only, tests and docs skipped, whole words
   # (camelCase and snake_case are split first, so requireAuth still counts).
   git diff main...HEAD -U0 \
     | awk '/^\+\+\+ / { f = substr($0, 5); skip = f ~ /(^|\/)(docs?|tests?|__tests__|e2e|fixtures?)\// || f ~ /\.(md|mdx|txt|rst)$/ || f ~ /([._]test|[._]spec)\.[^\/]*$/ || f ~ /\/test_[^\/]*$/; next } /^\+/ && !skip' \
     | LC_ALL=C sed -E 's/([a-z0-9])([A-Z])/\1 \2/g; s/([A-Z])([A-Z][a-z])/\1 \2/g' \
     | tr 'A-Z_-' 'a-z  ' \
     | sed -E 's/token +(count|usage|budget|limit)s?//g' \
     | grep -qwE 'rate ?limit[a-z]*|throttl[a-z]*|quotas?|auth[nz]?|authenticat[a-z]*|authori[sz][a-z]*|token|passwords?|passwd|secrets?|credentials?|saniti[sz][a-z]*|escap[a-z]*|validat[a-z]*|permissions?|csrf|xsrf|cors|rls|polic(y|ies)|guards?|middlewares?|(allow|deny|white|black) ?lists?|hash(es|ed|ing)?|hmac|signatures?|nonces?|jwt|bearer|oauth[0-9]*|x forwarded for' \
     && echo DEFENCE

   # How big is it? (lines added + removed)
   git diff main...HEAD --numstat | awk '{ n += $1 + $2 } END { print n + 0 }'

   # Does it render?
   git diff main...HEAD --name-only \
     | grep -qE '\.(html|css|scss|sass|less|tsx|jsx|vue|svelte|astro)$' && echo RENDERS
   ```

3. Invoke the following agents **in parallel** (multiple Agent tool calls in a single message)
   — unless the inline path below applies:
   - `code-simplifier` — redundancy, over-abstraction, naming
   - `test-writer` — missing test coverage
   - `security-auditor` — OWASP perspective
   - `e2e-tester` — **whenever step 2 printed `RENDERS`.** Not "if it seems worth it":
     the diff already answered. Everything above reads the change; only this one opens it.

   The condition is a fact about the diff on purpose. Asking the author whether their
   own change counts as a UI change puts the decision back with the maker, and the
   answer is reliably "not really" — which is how a review ships a verdict about a page
   nobody rendered.

   **Give each agent the diff, not the repo.** Paste the `git diff main...HEAD` output
   into its prompt and tell it to review that diff without re-running `git diff`,
   opening a file only to confirm a specific finding (`test-writer` may also grep for
   the existing tests of the changed code). A reviewer that re-reads the codebase
   spends most of its budget on code nobody changed.

   **Small and harmless → review inline instead.** If neither `DEFENCE` nor `RENDERS`
   printed **and** the size is **≤ 50 lines**, skip the agents and make their three
   passes yourself, in one read of the diff: simplification (reuse, redundancy,
   nesting, naming), tests (does every changed behaviour have one?), security (input
   handling, access control, injection, secrets). If that read turns up a guard or a
   rendered surface the grep missed, stop and dispatch the agents. `DEFENCE` over-fires
   on purpose — renaming a variable called `token` prints it — because the cost of a
   false hit is one normal review, and the cost of a miss is a guard nobody attacked.

4. **If `e2e-tester` fired but could not actually run** — no dev server, no reachable
   URL, no browser available — that is a result, not a non-event. Carry
   `UNVERIFIED: rendered behaviour not checked (<reason>)` into the verdict below.
   A render check that vanishes quietly is an unmeasured thing counted as a pass.

5. Merge the outputs into a **prioritized fix list** at the end:
   ```
   ## Merged verdict
   ### Must fix (before merge)
   1. ...
   ### Should fix (recommended in this PR)
   1. ...
   ### Nice to have (can defer)
   1. ...
   ### Not checked
   - UNVERIFIED: <what nobody measured, and why> — omit this heading only when it is empty
   ## One-liner: SHIP / FIX FIRST
   ```

   `SHIP` on a diff that renders, with an `UNVERIFIED` render line still standing, is a
   verdict about a page nobody opened. Say so in the one-liner rather than letting the
   heading carry it alone.

`$ARGUMENTS` can override the target branch/commit range (e.g. `--base develop`).

$ARGUMENTS
