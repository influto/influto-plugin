# InfluTo plugin

Integrate **InfluTo** — referral & affiliate **attribution** for mobile apps (iOS, Android, React
Native, Flutter) — directly from your AI coding agent, and manage your affiliate program without
leaving the editor.

This plugin bundles **two skills** and the **InfluTo MCP server**:

| Skill | What it does |
|---|---|
| `influto-integration` | Detects your app's stack, installs the right SDK, picks RevenueCat vs store-direct validation, writes the version-correct code, and verifies a real *attributed* conversion arrived. Works offline (no account needed). |
| `influto-platform` | Drives the InfluTo control-plane via the MCP: create an app, mint its API key + webhook secret, create/activate an affiliate campaign, configure store credentials (via a signed deep-link — secrets never touch the agent), and verify the integration is live. |

## Install (Claude Code)

```bash
# From a local checkout (dev):
claude --plugin-dir /path/to/influto-plugin

# Or add the marketplace and install:
/plugin marketplace add https://github.com/influto/influto-plugin
/plugin install influto
```

Then connect the MCP server with an agent key:

1. Go to **https://influ.to → Connect AI Agent** and create an `it_mcp_*` agent key (shown once).
2. Export it where your agent runs:
   ```bash
   export INFLUTO_API_KEY=it_mcp_...
   ```
   The bundled `.mcp.json` points at `https://influ.to/mcp` with
   `Authorization: Bearer ${INFLUTO_API_KEY}`.

The `influto-integration` skill works **without** the MCP (it only needs your app's API key to write
code); the `influto-platform` skill and the live-verify tools need the MCP connected.

## Security

- **No secret or `it_*` key is ever a tool argument or chat message.** Store credentials (Apple
  `.p8`, Google service-account JSON, RevenueCat key, webhook secret) are uploaded by you in the
  browser via the dashboard's write-only form — the agent only hands you a signed deep-link and
  polls the green-check.
- The agent key authorizes only your own organizations, with least-privilege scopes. Billing,
  payouts, admin, deletes, and reading raw credentials are **hard-denied** to agent keys.
- `scripts/verify_integration.py` reads `INFLUTO_API_KEY` from **your** shell env — never the model.

## Other editors

`skills/*/SKILL.md` follows the cross-agent Agent Skills format and also works in Cursor, Codex CLI,
Gemini CLI and Windsurf. Remote-MCP configuration is editor-specific — see your editor's MCP docs;
point it at `https://influ.to/mcp` with the same `Authorization: Bearer ${INFLUTO_API_KEY}` header.

## Docs

Full integration docs + the machine-readable wire contract: **https://docs.influ.to**
(`llms.txt` / `llms-full.txt` for agents).
