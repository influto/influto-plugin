# InfluTo plugin

Integrate **InfluTo** — referral & affiliate **attribution** for mobile apps (iOS, Android, React
Native, Flutter) — directly from your AI coding agent, and run your affiliate program without
leaving the editor: campaigns with milestone bonuses, creator invites and join links,
fraud-filtered analytics, and live verification that conversions really attributed.

This plugin bundles **two skills** and the **InfluTo MCP server** (55 tools):

| Skill | What it does |
|---|---|
| `influto-integration` | Detects your app's stack, installs the right SDK, picks RevenueCat vs store-direct validation, writes the version-correct code, and verifies a real *attributed* conversion arrived. Works offline (no account needed). |
| `influto-platform` | Drives the InfluTo control-plane via the MCP: provision apps + campaigns (incl. milestone bonuses and localized copy), configure validation, verify the integration, invite creators, mint join links, review bonus awards, and read canonical analytics. |

## Install — two steps, no keys

```bash
# 1. Install the plugin:
/plugin marketplace add influto/influto-plugin
/plugin install influto

# 2. There is no step two you have to configure. On the agent's first InfluTo
#    tool call, your browser opens an InfluTo consent page — sign in, pick your
#    organization, click Approve. Done.
```

The MCP server (`https://influ.to/mcp`) authenticates with **OAuth 2.1**: browser consent with an
organization picker, auto-refreshing tokens, and one-click revocation at
**https://influ.to/dashboard/connect-agent → Connected agents**.

Without the plugin, the raw MCP connect is just as short:

```bash
claude mcp add --transport http influto https://influ.to/mcp   # Claude Code
codex mcp add influto --url https://influ.to/mcp               # Codex CLI
# Cursor / claude.ai / any MCP client: add https://influ.to/mcp as an HTTP (streamable) server
```

## CI / headless (optional key fallback)

Environments without a browser can use an `it_mcp_*` agent key instead of OAuth: mint one at
**https://influ.to/dashboard/connect-agent** (shown once) and add an Authorization header to your
own MCP config (the plugin's bundled `.mcp.json` intentionally ships without one):

```json
{
  "mcpServers": {
    "influto": {
      "type": "http",
      "url": "https://influ.to/mcp",
      "headers": { "Authorization": "Bearer ${INFLUTO_API_KEY}" }
    }
  }
}
```

Then `export INFLUTO_API_KEY=it_mcp_...` in the environment where the agent (or CI job) runs.
Same tools, same scopes, revocable on the dashboard. The bundled
`skills/influto-integration/scripts/verify_integration.py` reads the same env var and exit-codes
0/1, so it can gate CI.

## Security

- **No secret or `it_*` key is ever a tool argument or chat message.** Store credentials (Apple
  `.p8`, Google service-account JSON, RevenueCat key, webhook secret) are uploaded by you in the
  browser via the dashboard's write-only form — the agent only hands you a dashboard link and
  polls the green-check.
- Agent access is org-scoped and least-privilege. Money writes, payouts, deletes, admin, and
  reading raw credentials are **hard-denied** to agents — wallet top-ups happen via a dashboard
  link *you* open, never through the agent.
- Revoke a connected agent (OAuth grant) or key any time; access ends immediately.

## Other editors

`skills/*/SKILL.md` follows the cross-agent Agent Skills format and also works in Cursor, Codex
CLI, Gemini CLI and Windsurf. Point any MCP client at `https://influ.to/mcp` (HTTP / streamable) —
the same OAuth browser consent kicks in automatically; use the header config above only for
headless environments.

## Docs

Agent reference (connect, all tools, scopes, `/api/agent/*` REST): **https://docs.influ.to/agents**
· machine twin: `https://docs.influ.to/llms-agents.txt` · full docs: **https://docs.influ.to**
(`llms.txt` / `llms-full.txt` for agents).
