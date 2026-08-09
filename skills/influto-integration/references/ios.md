# InfluTo — iOS (Swift)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.0.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **iOS** app. Package `github.com/influto/influto-ios`
(Swift Package Manager, v1.0.0). Source: https://github.com/influto/influto-ios.

## 1. Install
```bash
// Xcode → File → Add Package Dependencies →
//   https://github.com/influto/influto-ios   (from 1.0.0)
// Or in Package.swift:
.package(url: "https://github.com/influto/influto-ios.git", from: "1.0.0")
```

## 2. Initialize (once, at startup)
Call this exactly once when the app launches. **`initialize()` THROWS on failure** — surface the
error, do not swallow it. Read the API key from env/secrets; never hardcode it into committed source.
```swift
import InfluTo

// Call once at launch
try await InfluTo.initialize(
  InfluToConfig(apiKey: "YOUR_API_KEY", debug: true)
)
```

## 3. Check attribution (at launch)
Detect a referred user and gate any special offer / extended trial on `attributed`.
```swift
let attribution = await InfluTo.checkAttribution()
if attribution.attributed {
  // User came from a referral — show a special offer.
  print("Referred by \(attribution.referralCode ?? "")")
}
```

## 4. Manual referral-code entry (optional)
Let a user type a code. The prebuilt `ReferralCodeInput` shows only the field + a valid/invalid
state by default — the influencer/campaign **names are OFF unless you opt in**.
```swift
// Validate + apply a code the user typed
let result = await InfluTo.applyCode("FITGURU30")
if result.success {
  // Unlock the offer
}

// The same field also redeems creator free-access codes (INFLU-…) —
// grantsAccess / free_access in the result means unlock premium now.
```

## 5. Purchase validation — pick exactly ONE path
- **RevenueCat**: the SDK sets the `influto_code` + `influto_referral` ("true", a STRING) subscriber
  attributes automatically; you only confirm the webhook on the InfluTo dashboard. Nothing to call here.
- **Store-direct** (no RevenueCat): auto-capture is ON by default — usually nothing to call. Report
  manually only if you disabled auto-capture (then keep `autoCapture:false` so exactly one path runs).
  **`reportPurchase()` THROWS**; a 503 means retry (FX rate). Android one-time products must pass `productId`.
```swift
// Store-direct only (no RevenueCat). Purchases are captured AUTOMATICALLY
// on store-direct apps (StoreKit 2 Transaction.updates). To report manually:
if case .success(let verification) = try await product.purchase() {
  let r = try await InfluTo.reportPurchase(verification: verification)
}
```

## 6. Invariants you must respect (wire contract v1.0.0)
- All local state lives under the `@influto/` key prefix.
- Referral codes are `trim()` + `UPPERCASE` before sending.
- Network calls fail-soft (benign return) EXCEPT `initialize()` and `reportPurchase()`, which throw.
- RevenueCat `influto_referral` is the string `"true"`, never a boolean.
- Never wire both RevenueCat and store-direct — that double-reports conversions.

## 7. Verify it is live (do this last)
After running the app once, check `GET /api/agent/apps/{app_id}/events/recent` with an
`it_mcp_*` agent key (from https://influ.to/dashboard/connect-agent — the app's SDK key will
NOT work here), or call the MCP tool `influto_integration_status`:
- `sdk_events[]` shows each tracked event once, with the right `referral_code` + `platform`;
- if store-direct, `webhooks[]` shows a purchase with `"attributed": true` + the referral code;
- `GET /api/agent/apps/{app_id}/integration-status` rolls it all up into `{live, checklist[]}`.

_Per-stack bundle: https://docs.influ.to/llms/ios.txt — Full contract: https://docs.influ.to/contract.md_
