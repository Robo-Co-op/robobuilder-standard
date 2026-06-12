# CONTRIBUTING

How Robo Co-op members add new skills, agents, or improvements to **robobuilder**.

## Triggers for contributing

Open a PR when you've:
- Repeated the same multi-step workflow 3+ times → candidate for a new skill or playbook.
- Found a missing best practice that the team baseline should pick up → CLAUDE.md.baseline update.
- Discovered a new pattern via the Feature Adoption Loop and validated it → new skill or agent.
- Hit a recurring issue that hooks could prevent → new hook script.

## Step-by-step

### 1. Draft locally

```
/robobuilder:write-a-skill
```

This generates the SKILL.md scaffold with the 7-section pedagogical format.

### 2. Place in correct phase

Put your new skill under the appropriate phase directory:

```
~/.claude/plugins/robobuilder/skills/
├── phase0/   — repository foundation
├── phase05/  — investigation
├── phase1/   — design
├── phase2/   — prototype
├── phase3/   — implement
├── phase35/  — refactor
├── phase4/   — review
├── phase5/   — ship
├── utils/    — cross-cutting
├── meta/     — robobuilder management
└── playbooks/ — multi-skill orchestrators
```

### 3. Required frontmatter

```yaml
---
name: <skill-name>
description: <one-line>
origin: robobuilder      # or matt-pocock | gstack | jin-custom if forked
bootcamp_module: <M?.section>    # if a corresponding Notion module exists
bootcamp_url: <Notion URL>       # if a corresponding Notion module exists
---
```

### 4. Required body sections

- `## What` — one sentence
- `## When` — trigger conditions, when NOT to use
- `## Why` — principle / philosophy
- `## How` — concrete steps
- `## Example` — a real Robo Co-op scenario
- `## Anti-pattern` — common misuse
- `## See Also` — neighboring skills + Bootcamp link

### 5. Update the manifest

If your skill needs explicit listing (the manifest currently uses `"skills": "./skills/"` for auto-discovery, so usually not needed). If you add a new agent, edit `.claude-plugin/plugin.json` → `agents` array.

### 6. Local test

```
/plugin reload                  # reload robobuilder
/robobuilder:<your-skill>       # confirm it fires
```

### 7. Open a PR

```bash
cd ~/.claude/plugins/robobuilder
git checkout -b skill/<your-skill-name>
git add skills/phaseX/<your-skill>/
git commit -m "Add <skill> for <use case>"
gh pr create --title "Add /robobuilder:<your-skill>" --body "<context>"
```

PR body should include:
- The trigger you saw 3+ times
- A short demo (transcript snippet)
- Which Bootcamp module it links to (or "none — pure tool")

### 8. Review

A maintainer (or `/diff-review`) checks:
- 7-section format compliance
- No personal info leaks (paths, IPs, vault names)
- No license conflicts
- Bootcamp link is bidirectional (update Notion module too)

### 9. Release

Maintainer bumps semver in `.claude-plugin/plugin.json` and tags. Team picks it up via `/robobuilder:upgrade`.

## What NOT to contribute

- Personal one-off scripts (use Skill Creator for those).
- Anything secret-bearing (paths, tokens, vault names) — strip first.
- Forks of GStack or Matt Pocock skills with minor changes — prefer upstreaming those.
- Skills that duplicate an existing robobuilder skill (extend the existing one instead).

## Conventions

- File names: kebab-case (`my-new-skill/`).
- Skill descriptions: imperative, < 200 chars, mention trigger keywords for auto-activation.
- Examples in SKILL.md: real Robo Co-op scenarios (AZTK MC, EA eval, brand work, ASN training, etc.).
- Language: English. (Translation is on-demand via Claude.)

## Tooling for contributors

- `/robobuilder:write-a-skill` — scaffold a new SKILL.md
- `/robobuilder:diff-review` — review your PR locally before pushing
- `/robobuilder:grill` — adversarially test your own skill design
- `/codex:rescue` — second opinion from OpenAI

## Known limitations

- **block_secrets.py compound extensions** (e.g., `credentials.json.bak`): the doc-extension exclusion uses negative lookbehinds for `.md` / `.rst` / `.adoc` / `.html` / `.txt`. A path ending in another extension AFTER one of those (`.md.bak`, `.txt.old`) bypasses the exclusion and may either let a secret-file copy slip through or block a backup of a doc file. Low frequency in practice; accepted trade-off vs weakening the secret-file pattern. If you hit it, rename to drop the second extension before editing, or commit the file in your IDE and let pre-commit handle it.
- **block_secrets.py JWT pattern**: `eyJ.eyJ.` matches base64-encoded JWTs and any base64-shaped string starting with `{`. Test fixtures in `tests/` / `fixtures/` / `*_test.py` etc. are exempted from CONTENT scanning to avoid false positives on JWT-like sample payloads.
- **install_binaries.sh**: kept as a no-op compatibility shim. Do not add third-party clone/build steps here; robobuilder should stay free of external runtime binary installs.

## Maintenance cadence

- Weekly: maintainer reviews Feature Adoption Loop output (`feature_radar.md`) and decides if any upstream feature should land here.
- Monthly: drift check against upstream source packs and robobuilder-local maintenance notes.
- Quarterly: semver bump if non-trivial changes accumulated.
