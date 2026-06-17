#!/usr/bin/env python3
"""Local InfluTo integration self-verify — the offline twin of the MCP's influto_integration_status.

Reads the InfluTo agent key from the developer's OWN shell env (INFLUTO_API_KEY) and prints a live
integration checklist for an app. The credential is held by THIS SCRIPT, never by the model and
never passed as a command-line argument (C1) — so it cannot leak into a chat transcript or tool log.

Usage:
    export INFLUTO_API_KEY=it_mcp_xxx          # from https://influ.to -> Connect AI Agent
    python3 verify_integration.py --app-id <APP_ID>
    python3 verify_integration.py --app-id <APP_ID> --base-url https://influ.to

Exit code: 0 if the integration is live, 1 otherwise (so it can gate CI).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://influ.to"


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify an InfluTo integration is live.")
    ap.add_argument("--app-id", required=True, help="The InfluTo app id (UUID).")
    ap.add_argument("--base-url", default=os.environ.get("INFLUTO_BASE_URL", DEFAULT_BASE),
                    help="API base (default https://influ.to).")
    args = ap.parse_args()

    key = os.environ.get("INFLUTO_API_KEY") or os.environ.get("INFLUTO_TOKEN")
    if not key:
        print("ERROR: set INFLUTO_API_KEY in your environment (it_mcp_* agent key from "
              "https://influ.to -> Connect AI Agent). The key is read from env, never passed as "
              "an argument.", file=sys.stderr)
        return 2

    url = f"{args.base_url.rstrip('/')}/api/agent/apps/{args.app_id}/integration-status"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if e.code in (401, 403):
            print(f"ERROR {e.code}: the agent key was rejected. Check INFLUTO_API_KEY.", file=sys.stderr)
        elif e.code == 404:
            print(f"ERROR 404: app '{args.app_id}' not found for this key (wrong app or org).",
                  file=sys.stderr)
        else:
            print(f"ERROR {e.code}: {body[:300]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"ERROR: could not reach {args.base_url} ({e.reason}).", file=sys.stderr)
        return 1

    live = data.get("live") is True
    print(f"\nInfluTo integration status for app {args.app_id}")
    print("=" * 56)
    for step in data.get("checklist", []):
        mark = "✓" if step.get("done") else "·"
        print(f"  [{mark}] {step.get('step'):24} {step.get('detail', '')}")
    print("-" * 56)
    print(f"  SDK initialized : {data.get('sdk_installed')}  "
          f"(last: v{data.get('last_sdk_version')} / {data.get('last_sdk_platform')})")
    print(f"  SDK events      : {data.get('sdk_event_count')}")
    print(f"  Purchase webhooks: {data.get('webhook_count')}  "
          f"(attributed: {data.get('attributed_conversion_count')})")
    print(f"  Validation      : {data.get('validation')}")
    print("=" * 56)
    print(f"  LIVE: {live}\n")

    if not live:
        print("Not live yet. Run the app once so the SDK initializes, make a (sandbox) purchase, "
              "and re-run. The checklist above shows what is still missing.")
    return 0 if live else 1


if __name__ == "__main__":
    raise SystemExit(main())
