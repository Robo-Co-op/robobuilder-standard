# Changelog

All notable changes to robobuilder.

## [1.10.0] — 2026-11-11

`diff-review` spent three subagent runs on every diff, including one-line fixes, and
each agent re-read the repo to find a diff it could have been handed. Ported from
robobuilder-lite 1.5.0.

### Changed
- **Small, harmless diffs are reviewed inline.** If the diff is ≤ 50 lines (by
  `--numstat`) and neither `DEFENCE` nor `RENDERS` fires, `diff-review` does the three
  review passes itself and dispatches no agents. `DEFENCE` is a new mechanical check
  that matches whole words on added lines, splits camelCase and snake_case first so
  `requireAuth` still fires, and skips test and doc files. It over-fires on purpose,
  so a small guard change still gets the full agent review.
  `scripts/tests/test_defence_trigger.py` runs that pipeline against 21 concrete
  diffs: guards that must fire and lookalikes that must not.
- **Agents get the diff, not the repo**, in `diff-review` and in every `cross-review`
  round. `code-simplifier`, `test-writer` and `security-auditor` now start from the diff
  in their prompt instead of re-running `git diff` or reading whole files.
- **`code-simplifier` runs on haiku.**

## [1.9.0] — 2026-11-11

Secrets had no sanctioned way onto a server, so the unsanctioned ones won: keys pasted into
chat, and CI workflows that uploaded secrets as base64 artifacts readable by anyone with
download access. One of those was found and replaced in a Robo Co-op product repo this week.

### Added
- **`secret-transfer`** (P5 Ship). Delivers GitHub Actions secrets to a machine's `.env`
  encrypted end to end: the recipient keeps its own RSA-4096 key, and GitHub encrypts only the
  named secrets to its certificate (OpenSSL CMS, AES-256-GCM). Ships the workflow, a one-command
  sender and a receiver that never prints values. The workflow fails closed unless it runs from
  the default branch, the actor is allowlisted and the recipient's fingerprint is approved
- `scripts/tests/test_secret_transfer.py` runs the workflow's own shell steps (extracted
  from the YAML) against fake secrets. It checks that only the named secrets are encrypted, that
  no value is logged, that every guard fails closed, and that a wrong key or a tampered
  ciphertext does not decrypt
- CI installs `pyyaml` so that suite runs instead of skipping

## [1.8.0] — 2026-08-11

Closes out the execution sweep: all 51 confirmed findings are fixed.

### Fixed
- **`guard` enforced nothing.** It sold "full safety mode" while its three PreToolUse
  hooks pointed at `careful/` and `freeze/` skill directories that exist in no
  robobuilder edition. Both hooks are now implemented (`scripts/check_careful.py`,
  `scripts/check_freeze.py`), fail closed on unparseable input, and are tested by
  behaviour — 10 command cases, multi-edit escape, and a check that every declared hook
  target resolves
- **`learn`'s dedup kept the oldest entry.** It compared `new Date(e.ts)` and no writer
  emits `ts`, so `NaN > NaN` was always false. Also: `AVG_CONFIDENCE` divided by zero
  and printed `NaN` as a result, and an empty log reported `TOTAL: 0` as a measurement
- **`to-issues` discarded its own HITL/AFK classification** at the publish step, and its
  issue template had no Type field, so the classification had no output channel
- **`plan-eng-review` offered `/office-hours`**, which exists nowhere, then re-checked
  for a design doc that nothing writes — and read the inevitable miss as "user cancelled"
- **`install-companions` advertised six presets and defined four**
- 34 further defects: dangling command and doc references, unreachable `|| echo`
  fallbacks after a helper that exits 0, a documented flag no phase branched on,
  thresholds a skill stated two ways, and `tdd` gating its independent check on the
  self-judgement that check exists to replace

### Added
- `scripts/tests/test_guard_hooks.py` — guard's hooks must block, not merely exist
- Fixed `scripts/dev/update_skill_frontmatter.py`, which returned the literal YAML
  block-scalar indicator; 11 shipped skills carried a pedagogy header reading
  `**What**: |`. Regenerated all eleven

## [1.7.0] — 2026-08-11

Eleven skills persisted nothing when robobuilder was installed the supported way.

### Fixed
- **The runtime contract itself.** `docs/RUNTIME.md` prescribed calling the helpers as
  `bin/robobuilder-paths` — a bare relative path. But `bin/` ships *inside the plugin*,
  is never copied into the user's project and never added to `PATH`, and
  `settings.json.example` pins the shell's cwd to the user's project. The bare form
  resolves only when the working directory happens to be a checkout of this repo, which
  the supported install never produces.

  Eleven skills followed that contract across 124 call sites: `health`,
  `plan-eng-review`, `browse`, `learn`, `cso`, `canary`, `land-and-deploy`, `ship`,
  `context-save`, `context-restore`, `guard`.

  The failure was silent by construction. `eval "$(missing-command)"` leaves `SLUG` and
  `ROBOBUILDER_STATE_ROOT` **empty and exits 0**, so every read returned nothing —
  indistinguishable from a genuinely empty store — and every write landed in
  `/projects/…` and failed. Learnings, review records and context snapshots appeared to
  save and did not.

  Helpers are now addressed through `$RB`, rooted at `${CLAUDE_PLUGIN_ROOT}` (the form
  `hooks/hooks.json` and the meta skills already use), and every shell block that uses
  `$RB` defines it and refuses to continue when the helpers are absent.

### Added
- Tests on all three counts, because the path alone was never the point: no bare
  invocation, no `$RB` without its definition, no `$RB` without the existence check, and
  `docs/RUNTIME.md` must show both the bootstrap and the guard

Found by an execution sweep over the 46 skills that had never been run: 114 findings
raised, 63 refuted by independent verifiers, 51 confirmed. This was the root of two of
the eleven high-severity ones.

## [1.6.0] — 2026-08-11

Five of the nine bundled agents shipped with no skill calling them. They were
installed and invisible — reachable only if a user typed their name — and three of
them named the skill they belong to in their own description while that skill never
dispatched them.

### Fixed
- `requirements-validator` — "Use after `/to-prd` is generated" → now dispatched by
  `to-prd` on the draft, before publishing
- `tdd-pair` — "Use whenever `/tdd` is invoked" → now dispatched by `tdd` at the point
  where red gets skipped
- `codebase-explorer` — "for the Phase 0.5 workflow" → now dispatched by `zoom-out`,
  the Phase 0.5 skill, to build the map
- `design-critic` — "Complements the interactive `/grill-me`" → now dispatched by
  `grill-me` once the design is settled
- `release-notes-writer` — "Use during `/ship`" → now dispatched by `ship` Step 13 to
  group commits by theme

Each is wired where its own description points, with the reason stated rather than
just the call — an author is the worst reader of their own PRD, the agent deciding
whether it wrote a test first has an incentive to get that wrong, and mapping or
log-grouping belongs in a subagent to keep the reading out of the main context.

### Added
- Test: every agent in `agents/` must be dispatched by some skill. It strips fenced
  blocks and blockquotes first, because `upgrade` renders a mock console diff naming
  two of these agents as sample output — the first survey of this counted those as
  dispatches and concluded only three agents were unwired, i.e. it would have blessed
  the exact bug it exists to catch
- Test: `plugin.json`'s agent list must match `agents/` on disk

Found by running `zoom-out` and reading the map it produced: the agent whose job is
building that map was the one `zoom-out` did not call.

## [1.5.1] — 2026-08-09

Three unreachable audits, found by executing the skills' control flow rather than
reading it. A skill written as "Step 1 … Step 20" is a program and its forward jumps
are gotos; nothing checked where they landed.

### Fixed
- `ship` Step 6 sent both of its exits to Step 9, skipping the test coverage audit,
  the plan completion audit, plan verification and scope drift detection — roughly 450
  lines. The exit that fires is "no prompt-related files changed", which is the path
  every repo takes except the one Rails codebase Step 6 was written against. Step 6 is
  now labelled project-specific and hands off to Step 7
- `ship` Steps 9.3 and 10 sent three exits to Step 12, skipping Step 11 — titled
  "Adversarial review (always-on)" and opening "Every diff gets adversarial review".
  The exits that fire are "no issues found" and "no review comments", so the review
  was skipped exactly when nothing else had looked
- `land-and-deploy` sent both CI outcomes to Step 4 (Merge the PR), skipping Steps 3.4
  and 3.5. Step 3.5 is the pre-merge readiness gate — "the critical safety check before
  an irreversible merge" — and was unreachable on every path
- `land-and-deploy` Step 3.4 compared two empty strings when the repo has no `VERSION`
  file, which reads as "no drift" having measured nothing. It now reports n/a and
  resolves the version file the way `ship` Step 12 does

### Added
- Test: a forward jump that skips a section fails the suite unless the skip is in an
  allowlist with a written reason. A stale allowlist entry fails too — one matching no
  live jump would hide the next real skip. Ported to Pro and Lite, where it passes with
  an empty allowlist: neither has a section-skipping jump

## [1.5.0] — 2026-08-09

Four scoring and stopping-rule defects, all found by *executing* these skills rather
than reading them. Eleven rounds of prose review across the three repos found none of
them, and all four are the same shape: **a measurement that never happened counted as
a pass.**

### Fixed
- `health`'s composite could not reach 10. The five weights (tests 28, type check 22,
  lint 18, dead code 13, shell 9) sum to **90**, so dividing by the raw total capped a
  clean codebase at 9.0, and "a `SKIPPED` tool redistributes its weight" never said
  what it redistributes into — one dataset produced three different composites
  depending on how a reader resolved that. Now
  `Σ(score × weight for active) ÷ Σ(weight for active)`, with a worked example
- `ship`'s quality score rose as review coverage fell: a specialist that never ran
  contributed silence, and silence read as quality. The score now travels with its
  denominator — `score (N of M specialists)`
- `ship` Step 12 assumed a `VERSION` file. None of the three robobuilder repos has
  one, so `ship` could not ship the repo it lives in, and the failure was quiet —
  computing a bump against a nonexistent base rather than stopping. It now resolves
  the version file across `VERSION`, `.claude-plugin/plugin.json`, `package.json`,
  `pyproject.toml`, `Cargo.toml`
- `cross-review`'s two stopping rules, both disproved by this project's own review
  history: the "max 5 rounds, beyond that it diverges" cap would have shipped four
  real defects found in rounds 6-9, and "the same finding in 3+ rounds is a false
  positive" would have dismissed six consecutive genuine findings. The cap now keys on
  whether a round surfaced anything *new*, and the heuristic distinguishes the same
  *finding* recurring from the same *area* yielding new defects

### Added
- Test: any skill that aggregates per-item measurements must state what it divides by
  and what happens to an input it could not measure. The registry is closed, so a new
  scoring skill fails until someone answers both
- Test: `plugin.json`'s version must match the CHANGELOG's newest entry. Ported from
  Pro, which was the only repo whose version was correct — because it alone had this
- CI: the suite runs on push and pull request instead of only by hand

### Changed
- `marketplace.json` catches up the Pro entry (pinned at 1.0.0, stale since Pro tagged
  1.1.0) to 1.2.0 for the L5 graph layer, and Lite to 1.1.0
- README: the Pro row and the loop-stack line cover L5, the graph of loops above L3/L4

## [1.4.0] — 2026-07-03

Three-editions release. This repo is now **Robo Builder Standard**.

### Changed
- GitHub repo renamed `Robo-Co-op/robobuilder` → `Robo-Co-op/robobuilder-standard` (old URL redirects). The plugin name stays `robobuilder`, so installed `/robobuilder:*` commands are unaffected
- README: "Three editions" comparison table (Lite / Standard / Pro) with the L1-L4 loop-stack positioning
- marketplace.json bumped to v2.0.0: `robo-coop-tools` now lists all three plugins — `robobuilder` (this repo), `robobuilder-lite` (4 merged mega-skills for beginners), `robobuilder-pro` (Loop Engineering add-on)
- plugin.json description marks this as the Standard edition

## [1.3.0] — 2026-06-12

Workflow-order release. All-English content; upstream attribution fixes; blueprint-sync polish.

### Added
- Phase/order tag at the start of every skill description (e.g. `[P1-1 Design]`, `[Util-2]`) so the alphabetical `/plugin` skill list reads in workflow order. Within each phase, ordering follows practical usage order and frequency (grill family adjacent, review skills light → heavy, etc.)
- `upstream:` frontmatter field (canonical source repo URL) on all ingested Matt Pocock / GStack skills
- `origin: robobuilder` frontmatter on the 4 meta skills, 3 playbooks, and `blueprint-sync` (previously undeclared or mislabeled)
- `blueprint-sync`: resolution-direction table (stale-doc / violation / pivot) in drift classification; robobuilder pedagogy preamble; wired into `playbook-new-feature` Step 4 and `docs/WORKFLOW.md`
- "All 41 skills, in workflow order" table in README

### Changed
- **All-English content**: `cross-review`, `diff-review`, `grill`, `btw`, `export` (descriptions and bodies) and test comments translated from Japanese to English
- `setup` skill renamed from `setup-matt-pocock-skills` to `setup` (frontmatter `name:`); all internal references updated
- README attribution now links to the canonical upstream repos

### Fixed
- **LICENSE**: Matt Pocock upstream URL corrected from the non-existent `mattpocock/ai-engineering-skills` to `mattpocock/skills` (verified live); all in-repo references updated
- plugin.json version was still 1.0.0 despite the v1.1.0 tag; now tracks releases (1.3.0)

## [1.2.0] — 2026-05-23

New skill: `blueprint-sync` — keeps design documents honest as code evolves.

### Added
- `skills/utils/blueprint-sync/` — new cross-cutting skill with 4 modes:
  - `drift-check`: detect gaps between docs and code, output a structured drift report
  - `update-docs`: surgically update docs to match current reality, commit changes
  - `retrospective`: post-ship review + doc sync + optional ADR creation
  - `living-doc`: lightweight single-pass update after small PRs
  - Auto-detects mode from context (post-ship → retrospective, etc.)
- `ship` skill: added `/robobuilder:blueprint-sync` to See Also; added post-ship suggestion rule to Important Rules

## [1.1.0] — 2026-05-12

Polish & ship release. Same skill/agent/hook surface as v1.0; security and ergonomics hardening.

### Added
- robobuilder pedagogy preamble on all 33 ingested SKILL.md (What / When / See Also / Bootcamp / Origin) — propagated by `scripts/dev/update_skill_frontmatter.py`, idempotent on re-run
- `origin:`, `bootcamp_module:`, `bootcamp_url:` frontmatter fields on every ingested skill (Living Knowledge Loop scaffolding)
- 29 new unit tests under `scripts/tests/` covering `auto_format.py`, `memory_consolidate.py`, `notification.py` (90 tests total, all passing)
- `scripts/tests/conftest.py` with shared fixtures (`run_script`, `tmp_memory_dir`); runtime-built attack strings so tests don't trip block_secrets when edited in-session
- `scripts/pytest.ini` + `scripts/tests/README.md`
- Test-fixture exemption for content scanning in `block_secrets.py` — paths under `tests/`, `__tests__/`, `fixtures/`, `*_test.py`, `conftest.py`, `*.spec.{ts,js,tsx,jsx}`, `*.test.{ts,js,tsx,jsx}` skip CONTENT scanning (file-name scanning still applies)
- Legacy binary installer supply-chain guard in `install_binaries.sh` — refused to auto-confirm installs from moving branch tips before the installer was replaced by a no-op compatibility shim
- `## Security-sensitive code` section in `CLAUDE.md.baseline`
- Explicit precedence note in `settings.json.example` (deny → ask → allow, verified against docs)

### Changed
- `block_secrets.py` `_audit_log()` now uses `Path.home()` (OS-API resolution) instead of `HOME`/`USERPROFILE` env reads — not hijackable by env manipulation

### Documented
- `docs/CONTRIBUTING.md` — `.md.bak` and other compound-extension edge cases as known limitations

## [1.0.0] — 2026-05-11

Initial release. Built and reviewed in one session.

### Plugin surface
- 40 SKILL.md across 11 phase directories (meta, phase0, phase05, phase1, phase2, phase3, phase35, phase4, phase5, utils, playbooks)
  - 33 ingested from Matt Pocock (13, MIT), GStack (10, MIT), Jin custom (10)
  - 3 robobuilder-original meta-skills: `start`, `tune-claude-md`, `upgrade`, `install-companions`
  - 3 playbooks: `playbook-new-feature`, `playbook-bug-fix`, `playbook-review-deep`
- 9 phase-specific subagents (5 new for robobuilder: `codebase-explorer`, `design-critic`, `requirements-validator`, `tdd-pair`, `release-notes-writer`)
- 6 lifecycle hooks (SessionStart / PreToolUse / PostToolUse / Notification / PreCompact / SessionEnd)
- 4 Python hook scripts + 3 setup shell scripts
- 6 documentation files
- `CLAUDE.md.baseline` for `/robobuilder:tune-claude-md` personalization wizard
- `company.yaml` — Robo Co-op intelligence (Teams / Asana / 1Password / Vercel / Supabase / Stripe / Azure SQL / Notion)
- `marketplace.json` registering robobuilder under `robo-coop-tools` marketplace

### Security fixes (caught by `/cross-review` 5 rounds, before any release)
- PowerShell command injection in `notification.py` (no user content interpolation; sound-only)
- AppleScript injection in `notification.py` (`_sanitize()` strips non-printable + injection chars)
- Supply-chain pinning for `install_binaries.sh` (3-path coverage: fresh / upgrade / re-run + AUTO_YES env var for CI)
- `memory_consolidate.py` stat-after-open bug (header duplicated on every invocation; now checked before `open("a")`)
- `block_secrets.py` credentials regex prefix bug (`db_credentials.json` was bypassing)
- `block_secrets.py` MultiEdit content not scanned (now iterates `edits[*].new_string`)
- Expanded `block_secrets.py` SECRET_CONTENT_PATTERNS to cover: Stripe (live/test), GitHub variants (p/s/o/r/u), JWT, Azure connection strings, 1Password service-account tokens
- `block_secrets.py` doc-extension lookbehind so docs like `credentials-management-guide.md` are not blocked
- Tightened `settings.json.example` deny patterns (`.env.local`, `.envrc`, `id_rsa`, `wget -O- | sh`, etc.)
- Audit log to `~/.claude/logs/block_secrets.log` for blocked attempts

### Licensing
MIT, with attribution to Matt Pocock and Garry Tan for redistributed skills. See `LICENSE`.
