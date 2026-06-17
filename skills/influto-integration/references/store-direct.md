# InfluTo — Purchase Validation via Store-Direct

> Wire contract v1.0.0. One of two validation paths. Pick exactly ONE — never wire both.

This is the path to choose when the app does **NOT** use RevenueCat. InfluTo validates purchases
directly against the stores: Apple via the App Store Server API (a StoreKit 2 signed transaction
JWS), Google via Play (a Play Billing `purchaseToken`). The SDK POSTs the store proof to
`/sdk/purchase`; InfluTo verifies it with the store, then records the attributed conversion.

If the app already uses RevenueCat, use **[revenuecat](./revenuecat.md)** instead.

## When to choose this path
- The app sells IAP / subscriptions with native StoreKit 2 (iOS) and/or Play Billing (Android),
  no RevenueCat in the stack.
- You want InfluTo to validate purchases server-side against Apple/Google directly.
- `/sdk/init` returns `store_direct:true` for this app once the dashboard credentials are green.

## How it works (auto-capture is ON by default)
For store-direct apps, **you usually call nothing**. `initialize()` starts auto-capture when
`/sdk/init` returns `store_direct:true` AND config `autoCapture` is not `false`. Auto-capture
observes new store purchases, back-syncs unfinished ones, sends each to `/sdk/purchase`, and
dedups so a purchase is reported exactly once. (Auto-capture NEVER runs for RevenueCat apps, so
it can't double-report against the webhook path.)

```ts
// Illustrative. For store-direct apps this is the whole integration —
// initialize() auto-starts capture when /sdk/init reports store_direct:true.
await InfluTo.initialize({ apiKey: 'YOUR_API_KEY' });
// ...nothing else to call at purchase time.
```

Per-platform observers: RN/iOS run in-core (RN dynamic-requires `expo-iap`→`react-native-iap`,
Expo-Go-safe; iOS observes StoreKit 2 `Transaction.updates`). Android starts the separate
`to.influ:android-sdk-billing` artifact reflectively if present. Flutter uses the separate
`influto_iap` `InfluToPurchaseObserver`. Exact APIs:
[react-native](./react-native.md) · [ios](./ios.md) · [android](./android.md) · [flutter](./flutter.md).

## Manual reporting (only if you disable auto-capture)
Drive `reportPurchase()` yourself only if you turn auto-capture off. If you do, set
`autoCapture:false` so exactly ONE path runs — never auto-capture AND manual.

```ts
// Disable auto-capture, then report each purchase yourself.
await InfluTo.initialize({ apiKey: 'YOUR_API_KEY', autoCapture: false });

// iOS — StoreKit 2 signed transaction (JWS):
await InfluTo.reportPurchase({ platform: 'ios', signedTransaction: jwsString });

// Android subscription — purchaseToken only (OMIT productId):
await InfluTo.reportPurchase({ platform: 'android', purchaseToken: token });

// Android ONE-TIME product — MUST send productId, SHOULD send price+currency:
await InfluTo.reportPurchase({
  platform: 'android',
  purchaseToken: token,
  productId: 'coins_100',           // required for one-time (Google products.get needs it)
  price: 4.99, currency: 'USD',     // from ProductDetails (a one-time ProductPurchase has no price)
});
```

- `reportPurchase()` **THROWS** on failure (it does not fail-soft). Surface the error.
- A **503** means the FX rate was unavailable → **retry** (the report is retryable + idempotent).
- The SDK defaults `referralCode` to the stored `@influto/influto_code`, binding the first
  transaction to the referral.

## Attribution binding & dedup identity
- On the FIRST transaction the SDK sends the stored `influto_code` so the conversion binds to the
  referral. The conversion is keyed on the **store identity**, not the referral.
- Dedup / conversion key: Apple **`originalTransactionId`** / Google **`purchaseToken`**. The
  **backend is the final dedup anchor** — repeated reports of the same identity are idempotent.
- Set the store identity so it is stable across renewals: StoreKit 2 **`appAccountToken`** (iOS)
  / Play **`obfuscatedAccountId`** (Android) at purchase time, in the host's purchase flow.
- One-time / consumable / non-renewing purchases route to `NON_RENEWING_PURCHASE` — one
  conversion PER distinct transaction.

## Dashboard config (the human must do this once)
`/sdk/purchase` returns **400** until the platform is configured for store-direct
(`ios_validation_provider='apple'` / `android_validation_provider='google'`), so the SDK is safe
to ship dormant. Configure credentials on the InfluTo dashboard and pass the green
**validate-store-credentials** check before the provider activates:

- **Apple** (App Store Server API): **Issuer ID** + **Key ID** + the **.p8** private key +
  the **numeric App Store ID** (the app's Apple ID — required for production).
- **Google** (Play): a **service-account JSON** with Play Developer API access.

Until the relevant check is green, `/sdk/init` keeps `store_direct:false` for that platform and
`/sdk/purchase` returns 400.

## Invariants you must respect
- **Pick exactly ONE path.** Do NOT also wire RevenueCat. If you wire manual `reportPurchase`,
  set `autoCapture:false`. Two reporting paths double-report conversions.
- `reportPurchase()` THROWS (only `initialize` + `reportPurchase` throw; everything else
  fail-softs). A 503 = FX-unavailable → retry.
- Android one-time products MUST send `productId`; OMIT `productId` for subscriptions.
- `validated` in the response is a **string** (`"apple"` / `"google"`), not a boolean.
- The sent-set (RN/Flutter `@influto/reported_purchases`, iOS `@influto/sent_purchases`, Android
  `influto_billing_sync_prefs`) is additive and is **NOT** cleared by `clearAttribution` — a
  returning user must not re-report old purchases.
- Premium gate (if you also use comp codes): `RC-entitlement OR checkAccess().hasAccess`.

## Verify it is live (do this last)
After a sandbox purchase, check `GET /api/apps/{app_id}/events/recent`:
- `webhooks[]` shows the `reportPurchase` with `"attributed": true` and the matching
  `referral_code` (an organic purchase shows `"organic": true`, `referral_code: null`).
- `sdk_events[]` shows each tracked event exactly once (deduped) with the right `platform`.

If nothing appears, the platform is not yet configured for store-direct (the
validate-store-credentials check is not green, so `/sdk/purchase` is returning 400).

---

Full wire contract: [./contract.md](./contract.md) — Hosted: https://docs.influ.to/contract.md
