# InfluTo — Flutter (Dart)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.0.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **Flutter** app. Package `influto`
(pub.dev, v1.1.0). Source: https://github.com/influto/influto-flutter.

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
  InfluToConfig(
    apiKey: 'YOUR_API_KEY',
    // RevenueCat apps: let the SDK tag the subscriber
    // revenueCatHook: (attrs) => Purchases.setAttributes(attrs),
  ),
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
Let a user type a code. The prebuilt code field (`ReferralCodeInput` on React Native, Flutter and web;
`InfluToReferralCodeInput` on iOS and Android) shows only the field + a valid/invalid state by
default — the creator/campaign **names are OFF unless you opt in**. Free-access (comp) codes are
redeemed with `setReferralCode()` (`grantsAccess`); gate premium on `checkAccess()`.
```dart
// Validate + apply a code the user typed
final result = await InfluTo.instance.applyCode('FITGURU30');
if (result.valid && result.applied == true) {
  // Unlock the offer
}

// Or the ready-made widget: ReferralCodeInput(onApplied: (result) { … })
// Free-access codes: (await setReferralCode(code, appUserId: userId)).grantsAccess
// == true → unlock premium, and gate premium on (await checkAccess()).hasAccess.
```

## 5. Purchase validation — pick exactly ONE path
- **RevenueCat**: the SDK sets the `influto_code` + `influto_referral` ("true", a STRING) subscriber
  attributes — automatically on React Native (when react-native-purchases is installed) and Android
  (reflection); on iOS pass `revenueCatAttributeSetter`, on Flutter `revenueCatHook`, on web a
  `revenueCat` binding. Then wire the webhook on the InfluTo dashboard (Setup & SDK → Webhook).
- **Store-direct** (no RevenueCat): auto-capture runs once the platform's capture code is present —
  iOS built in; React Native needs expo-iap or react-native-iap; Android needs to.influ:android-sdk-billing;
  Flutter needs influto_iap + InfluToPurchaseObserver().enable(); web needs a purchaseSource. Report
  manually only if you disabled auto-capture (then keep `autoCapture:false` so exactly one path runs).
  **`reportPurchase()` THROWS**; a 503 means retry (FX rate). Android one-time products must pass `productId`.
```dart
// Store-direct only (no RevenueCat). For automatic capture add influto_iap and
// call InfluToPurchaseObserver().enable() after initialize(). Or report manually:
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

Per-stack bundle: https://docs.influ.to/llms/flutter.txt · Full guide: https://docs.influ.to/sdk/flutter.md · Wire contract: https://docs.influ.to/contract.md
