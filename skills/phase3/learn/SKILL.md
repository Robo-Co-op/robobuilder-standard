---
name: learn
preamble-tier: 2
version: 1.0.0
description: |
  Manage project learnings. Review, search, prune, and export what RoboBuilder
  has learned across sessions. Use when asked to "what have we learned",
  "show learnings", "prune stale learnings", or "export learnings".
  Proactively suggest when the user asks about past patterns or wonders
  "didn't we fix this before?"
triggers:
  - show learnings
  - what have we learned
  - manage project learnings
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Glob
  - Grep
origin: gstack
bootcamp_module: M3.code.implement
bootcamp_url: https://www.notion.so/Claude-34e5a7e135d2807daec1d83e41d93504
---
> **robobuilder pedagogy** (phase3)
> - **What**: |
> - **When**: see the description above for trigger keywords; details in the body below.
> - **See Also**: /robobuilder:write-a-skill
> - **Bootcamp**: M3.code.implement
> - **Origin**: Garry Tan upstream, adapted for RoboBuilder

<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

## RoboBuilder Runtime Notes

RoboBuilder uses a lightweight local state directory when a workflow needs durable scratch data:

```bash
RB_HOME="${ROBOBUILDER_HOME:-$HOME/.robobuilder}"
RB_SLUG=$(printf '%s' "$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9._-' '-')
RB_PROJECT="$RB_HOME/projects/${RB_SLUG:-unknown}"
RB_BRANCH=$(git branch --show-current 2>/dev/null || echo unknown)
mkdir -p "$RB_PROJECT"
echo "ROBOBUILDER_HOME: $RB_HOME"
echo "ROBOBUILDER_PROJECT: $RB_PROJECT"
echo "BRANCH: $RB_BRANCH"
```

## Detect command

Parse the user's input to determine which command to run:

- `/learn` (no arguments) → **Show recent**
- `/learn search <query>` → **Search**
- `/learn prune` → **Prune**
- `/learn export` → **Export**
- `/learn stats` → **Stats**
- `/learn add` → **Manual add**

---

## Show recent (default)

Show the most recent 20 learnings, grouped by type.

```bash
eval "$(bin/robobuilder-slug 2>/dev/null)"
bin/robobuilder-learnings-search --limit 20 2>/dev/null || echo "No learnings yet."
```

Present the output in a readable format. If no learnings exist, tell the user:
"No learnings recorded yet. As you use /review, /ship, /investigate, and other skills,
RoboBuilder can capture patterns, pitfalls, and insights it discovers."

---

## Search

```bash
eval "$(bin/robobuilder-slug 2>/dev/null)"
bin/robobuilder-learnings-search --query "USER_QUERY" --limit 20 2>/dev/null || echo "No matches."
```

Replace USER_QUERY with the user's search terms. Present results clearly.

---

## Prune

Check learnings for staleness and contradictions.

```bash
eval "$(bin/robobuilder-slug 2>/dev/null)"
bin/robobuilder-learnings-search --limit 100 2>/dev/null
```

For each learning in the output:

1. **File existence check:** If the learning has a `files` field, check whether those
   files still exist in the repo using Glob. If any referenced files are deleted, flag:
   "STALE: [key] references deleted file [path]"

2. **Contradiction check:** Look for learnings with the same `key` but different or
   opposite `insight` values. Flag: "CONFLICT: [key] has contradicting entries —
   [insight A] vs [insight B]"

Present each flagged entry via AskUserQuestion:
- A) Remove this learning
- B) Keep it
- C) Update it (I'll tell you what to change)

For removals, read the learnings.jsonl file and remove the matching line, then write
back. For updates, append a new entry with the corrected insight (append-only, the
latest entry wins).

---

## Export

Export learnings as markdown suitable for adding to CLAUDE.md or project documentation.

```bash
eval "$(bin/robobuilder-slug 2>/dev/null)"
bin/robobuilder-learnings-search --limit 50 2>/dev/null
```

Format the output as a markdown section:

```markdown
## Project Learnings

### Patterns
- **[key]**: [insight] (confidence: N/10)

### Pitfalls
- **[key]**: [insight] (confidence: N/10)

### Preferences
- **[key]**: [insight]

### Architecture
- **[key]**: [insight] (confidence: N/10)
```

Present the formatted output to the user. Ask if they want to append it to CLAUDE.md
or save it as a separate file.

---

## Stats

Show summary statistics about the project's learnings.

```bash
eval "$(bin/robobuilder-slug 2>/dev/null)"
eval "$(bin/robobuilder-paths)"
LEARN_FILE="$ROBOBUILDER_STATE_ROOT/projects/$SLUG/learnings.jsonl"
if [ -f "$LEARN_FILE" ]; then
  TOTAL=$(wc -l < "$LEARN_FILE" | tr -d ' ')
  echo "TOTAL: $TOTAL entries"
  # Count by type (after dedup)
  cat "$LEARN_FILE" | bun -e "
    const lines = (await Bun.stdin.text()).trim().split('\n').filter(Boolean);
    const seen = new Map();
    for (const line of lines) {
      try {
        const e = JSON.parse(line);
        const dk = (e.key||'') + '|' + (e.type||'');
        const existing = seen.get(dk);
        if (!existing || new Date(e.ts) > new Date(existing.ts)) seen.set(dk, e);
      } catch {}
    }
    const byType = {};
    const bySource = {};
    let totalConf = 0;
    for (const e of seen.values()) {
      byType[e.type] = (byType[e.type]||0) + 1;
      bySource[e.source] = (bySource[e.source]||0) + 1;
      totalConf += e.confidence || 0;
    }
    console.log('UNIQUE: ' + seen.size + ' (after dedup)');
    console.log('RAW_ENTRIES: ' + lines.length);
    console.log('BY_TYPE: ' + JSON.stringify(byType));
    console.log('BY_SOURCE: ' + JSON.stringify(bySource));
    console.log('AVG_CONFIDENCE: ' + (totalConf / seen.size).toFixed(1));
  " 2>/dev/null
else
  echo "NO_LEARNINGS"
fi
```

Present the stats in a readable table format.

---

## Manual add

The user wants to manually add a learning. Use AskUserQuestion to gather:
1. Type (pattern / pitfall / preference / architecture / tool)
2. A short key (2-5 words, kebab-case)
3. The insight (one sentence)
4. Confidence (1-10)
5. Related files (optional)

Then log it:

```bash
bin/robobuilder-learnings-log '{"skill":"learn","type":"TYPE","key":"KEY","insight":"INSIGHT","confidence":N,"source":"user-stated","files":["FILE1"]}'
```
