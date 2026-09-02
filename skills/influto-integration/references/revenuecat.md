# InfluTo — Purchase Validation via RevenueCat

> Wire contract v1.0.0. One of two validation paths. Pick exactly ONE — never wire both.

This is the path to choose when the app **already uses RevenueCat** for purchases and
entitlements. Attribution is driven entirely by RevenueCat's server-to-server webhook: the SDK
tags the RevenueCat subscriber, RevenueCat fires its events to InfluTo, and InfluTo attributes
the conversion. There is **nothing to call at purchase time** in the app — no `reportPurchase`,
no auto-capture.

If the app does NOT use RevenueCat, use **[store-direct](./store-direct.md)** instead.

## When to choose this path
- The app uses RevenueCat (`Purchases.configure(...)`) for IAP / subscriptions.
- You want server-side attribution with zero purchase-time wiring in the app.
- `/sdk/init` returns `store_direct:false` for this app (auto-capture stays silent — see the
  store-direct invariant). RevenueCat apps are the default.

## How it works (data flow)
1. The SDK sets two RevenueCat **subscriber attributes** on the customer (on attribution found,
   and on `setReferralCode` / `applyCode`).
2. The user buys through RevenueCat as normal.
3. RevenueCat POSTs its webhook events to `https://influ.to/api/webhooks/revenuecat/{app_id}`.
4. InfluTo reads the `influto_code` + `influto_referral` attributes off the event and records the
   attributed conversion. No call from the app.

## 1. Subscriber attributes (the SDK does this for you)
The SDK sets these two attributes automatically — you do not set them by hand. They exist so the
InfluTo webhook + RevenueCat Targeting rules can read the referral off the customer:

| key | value |
|---|---|
| `influto_code` | the referral code, already trimmed + UPPERCASED |
| `influto_referral` | the literal **string** `"true"` |

> ⚠️ `influto_referral` MUST be the string `"true"`, NOT a boolean `true`. A boolean breaks
> RevenueCat Targeting **silently** — no error, just no attribution.

RevenueCat is an **optional** dependency — the SDK has no hard dependency on it. The recommended
cross-platform pattern is a **caller-injected attribute-setter callback** that the host wires to
`Purchases.setAttributes(...)`. Provide that callback at init so the SDK can tag the customer:

```ts
// Illustrative (see the per-SDK reference for exact API names/signatures).
import Purchases from 'react-native-purchases';

await InfluTo.initialize({
  apiKey: 'YOUR_API_KEY',
  // Wire RevenueCat's setter so InfluTo can tag the subscriber.
  setAttributes: (attrs) => Purchases.setAttributes(attrs),
});
```

The RN SDK additionally keeps a `require()`-based auto-detect of `react-native-purchases` for
back-compat, so on RN you can often skip the callback. On iOS / Android / Flutter, inject the
callback. Per-SDK exact signatures:
[react-native](./react-native.md) · [ios](./ios.md) · [android](./android.md) · [flutter](./flutter.md).

That is the entire app-side integration for this path. After init + `checkAttribution()` (and any
manual `applyCode`), there is nothing else to call for purchases.

## 2. Webhook config (once per app — headless if a RevenueCat MCP is available)
1. `influto_provision` (or `influto_regenerate_webhook_secret`) returned the **webhook secret** —
   it is shown once; keep it out of source files and out of chat.
2. `influto_setup_revenuecat` returns the webhook URL plus `headless.fields` and `dashboard_steps`.
3. **Headless:** if a RevenueCat MCP is connected, call its `create-webhook-integration` with
   name `InfluTo`, the returned URL, authorization header `Bearer <webhook_secret>`, environment
   both (production + sandbox), all apps, all events. No dashboard visit needed.
4. **Otherwise the human does it once** in RevenueCat → project → **Integrations → Webhooks →
   "Add new configuration"** — the form has exactly these fields:
   - **Webhook name:** anything, e.g. `InfluTo`.
   - **Webhook URL:** `https://influ.to/api/webhooks/revenuecat/{app_id}`.
   - **Authorization header value** — ONE field, no separate header-name field:
     `Bearer <webhook_secret>` (InfluTo also accepts the bare secret).
   - **Environment to send events for:** leave **Both Production and Sandbox**.
   - **Events filter:** leave **All apps** / **All events**. **HMAC webhook signing:** leave off.
   - Click **Add webhook**.
5. Verify without a device: `influto_test_integration` → `influto_integration_status`
   (`webhook_count > 0`, synthetic purchase attributed).

## 3. Invariants you must respect
- **Pick exactly ONE path.** Do NOT also wire store-direct (`reportPurchase` / auto-capture).
  Wiring both double-reports every conversion. For RevenueCat apps `/sdk/init` returns
  `store_direct:false`, so auto-capture stays off automatically — keep it that way.
- `influto_referral` is the string `"true"`, never a boolean.
- `influto_code` is set already trimmed + UPPERCASED (the SDK normalizes; the backend uppercases
  too, so cache keys agree).
- RevenueCat is optional — no hard dependency. Inject the attribute-setter callback; the SDK
  must not crash if RevenueCat is absent.
- The four `RENEWAL` / `CANCELLATION` / `PRODUCT_CHANGE` / `INITIAL_PURCHASE` events are the set
  InfluTo needs; enabling fewer drops recurring-commission events.
- Premium gate (if you also use comp codes): `RC-entitlement OR checkAccess().hasAccess`.
  Comp grants can ADDITIONALLY be mirrored into your own RevenueCat project as promotional
  entitlements — self-serve on the InfluTo dashboard: **App Settings → Validation → "Creator
  free-access codes"**. Paste the RC **secret** key (v1 or v2, version auto-detected on save);
  a **v2** key also needs `project_id` (`proj…`) + `entitlement_id` (`entl…`), a **v1** key
  needs the entitlement **lookup key** (e.g. `pro`). The `applyCode`/`setReferralCode` response
  carries an additive `rc_grant {attempted, ok, error}` diagnostic — native access is granted
  even when the RC mirror fails. If you gate ONLY on the RC entitlement, call
  `Purchases.invalidateCustomerInfoCache()` after a comp redemption (`getCustomerInfo()` may
  serve a cached result); the OR-gate sidesteps this entirely.

## 4. Verify it is live (do this last)
After a sandbox/test purchase, check `GET /api/agent/apps/{app_id}/events/recent` (Bearer
`it_mcp_*` agent key — `scripts/verify_integration.py` or the MCP's `influto_recent_events` do
this for you; the dashboard's `/api/apps/*` routes reject API keys):
- `webhooks[]` shows the RevenueCat-driven purchase with `"attributed": true` and the matching
  `referral_code` (an organic purchase shows `"organic": true`, `referral_code: null`).
- `sdk_events[]` shows each tracked event exactly once (deduped) with the right `platform`.

If the webhook entry is missing, the RevenueCat webhook URL / secret / events are misconfigured
(re-check step 2). If it appears but `"attributed"` is `false`, the subscriber attributes were not
set — most often `influto_referral` was sent as a boolean instead of the string `"true"`.

---

Full wire contract: [./contract.md](./contract.md) — Hosted: https://docs.influ.to/contract.md
