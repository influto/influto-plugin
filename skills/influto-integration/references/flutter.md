# InfluTo — Flutter (Dart)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.0.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **Flutter** app. Package `influto`
(pub.dev, v1.0.0). Source: https://github.com/influto/influto-flutter.

## 1. Install
```bash
flutter pub add influto
# optional: automatic store-direct purchase capture
flutter pub add influto_iap
```

## 2. Initialize (once, at startup)
Call this exactly once when the app launches. **`initialize()` THROWS on failure** — surface the
error, do not swallow it. Read the API key from env/secrets; never hardcode it into committed source.
```dart
import 'package:influto/influto.dart';

// Call once at startup
await InfluTo.instance.initialize(
  const InfluToConfig(apiKey: 'YOUR_API_KEY'),
);
```

## 3. Check attribution (at launch)
Detect a referred user and gate any special offer / extended trial on `attributed`.
```dart
final attribution = await InfluTo.instance.checkAttribution();
if (attribution.attributed) {
  // User came from a referral — show a special offer.
  print('Referred by ${attribution.referralCode}');
}
```

## 4. Manual referral-code entry (optional)
Let a user type a code. The prebuilt `ReferralCodeInput` shows only the field + a valid/invalid
state by default — the influencer/campaign **names are OFF unless you opt in**.
```dart
// Validate + apply a code the user typed
final result = await InfluTo.instance.applyCode('FITGURU30');
if (result.success) {
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
```dart
// Store-direct only (no RevenueCat). Add the influto_iap companion for automatic
// capture, or report manually:
await InfluTo.instance.reportPurchase(
  platform: 'ios',                 // or 'android'
  signedTransaction: jws,          // iOS: StoreKit 2 JWS
  // purchaseToken: token,         // Android: Play Billing purchaseToken
);
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

_Per-stack bundle: https://docs.influ.to/llms/flutter.txt — Full contract: https://docs.influ.to/contract.md_
