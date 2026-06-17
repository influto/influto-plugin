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

## 2. Dashboard config (the human must do this once)
The webhook is what actually drives attribution, so it must be confirmed on the InfluTo dashboard.

1. Open the InfluTo dashboard → **Settings → RevenueCat**.
2. Copy the webhook **URL** and the **webhook secret** shown there.
3. In the **RevenueCat dashboard** → project → **Integrations → Webhooks**, add a webhook:
   - **URL:** `https://influ.to/api/webhooks/revenuecat/{app_id}`
   - **Authorization header:** `Bearer <webhook_secret>` (the secret from step 2).
   - **Events to send:** `INITIAL_PURCHASE`, `RENEWAL`, `CANCELLATION`, `PRODUCT_CHANGE`.
4. Save. Send a test event from RevenueCat (or run a sandbox purchase) and confirm it lands.

Without this webhook configured, the SDK still tags subscribers correctly but **no conversions
are ever recorded** — the webhook is the server-side half of the path.

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

## 4. Verify it is live (do this last)
After a sandbox/test purchase, check `GET /api/apps/{app_id}/events/recent`:
- `webhooks[]` shows the RevenueCat-driven purchase with `"attributed": true` and the matching
  `referral_code` (an organic purchase shows `"organic": true`, `referral_code: null`).
- `sdk_events[]` shows each tracked event exactly once (deduped) with the right `platform`.

If the webhook entry is missing, the RevenueCat webhook URL / secret / events are misconfigured
(re-check step 2). If it appears but `"attributed"` is `false`, the subscriber attributes were not
set — most often `influto_referral` was sent as a boolean instead of the string `"true"`.

---

Full wire contract: [./contract.md](./contract.md) — Hosted: https://docs.influ.to/contract.md
