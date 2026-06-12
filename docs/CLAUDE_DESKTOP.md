# RoboBuilder for Claude Desktop

Claude Desktop does not use the Claude Code plugin system.
Instead, it uses **MCP (Model Context Protocol) servers** via `claude_desktop_config.json`.

RoboBuilder's skills and agents can be made available in Claude Desktop by running a lightweight MCP bridge.

---

## Option 1: MCP Bridge (Recommended)

### Install

```bash
# Clone RoboBuilder
git clone https://github.com/Robo-Co-op/robobuilder ~/.robobuilder-src

# Install the MCP bridge
cd ~/.robobuilder-src
npm install
npm run build:mcp
```

### Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "robobuilder": {
      "command": "node",
      "args": ["~/.robobuilder-src/mcp/server.js"],
      "env": {
        "ROBOBUILDER_STATE_ROOT": "~/.robobuilder"
      }
    }
  }
}
```

Restart Claude Desktop. You should see `robobuilder` as an available MCP tool.

---

## Option 2: Skills as System Prompt (Manual, No MCP)

If you just want the skill content without the MCP bridge:

1. Pick a skill from `skills/*/SKILL.md`
2. Copy the content into Claude Desktop's **Custom Instructions** or a **Project**
3. Claude will follow the skill's instructions for that conversation

This works for any single skill but doesn't give you the full multi-skill switching.

---

## Option 3: Claude Desktop Projects (Recommended for teams)

1. Create a **Project** in Claude Desktop
2. Upload relevant `SKILL.md` files as Project Knowledge
3. All conversations in that project get the skill context automatically

Best for: using 2–5 skills together without MCP setup.

---

## Supported Features by Version

| Feature | Claude Code | Desktop (MCP) | Desktop (Manual) | OpenClaw/Codex |
|---|---|---|---|---|
| Full skill switching | ✅ | ✅ | ❌ one at a time | ✅ |
| bin/ helpers (state, slug, etc.) | ✅ | ✅ | ❌ | ✅ |
| agents/ subagents | ✅ | ⚠️ partial | ❌ | ✅ |
| hooks/ | ✅ | ❌ | ❌ | ⚠️ partial |
| /robobuilder:* commands | ✅ | ❌ | ❌ | ❌ (use skill name) |
| Skill catalog auto-discovery | ✅ | ✅ | ❌ | ✅ |
| Install via marketplace | ✅ | ❌ | ❌ | via export script |

---

## Converting to OpenClaw/Codex

See [OPENCLAW_CODEX.md](./OPENCLAW_CODEX.md) for the full adapter export flow.

Short version:
```bash
python scripts/export_openclaw_codex_skills.py --target openclaw
# installs 40 skills to ~/.openclaw/skills/robobuilder-*
```

---

## Notes

- Claude Desktop's MCP support is evolving. Check [Anthropic MCP docs](https://docs.anthropic.com/en/docs/mcp) for latest.
- The MCP bridge (`mcp/server.js`) exposes each skill as a callable MCP tool, using its SKILL.md as the tool description.
- State files (`~/.robobuilder/`) are shared between CC and Desktop MCP modes — no re-initialization needed.
