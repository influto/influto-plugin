# InfluTo — React Native (TypeScript)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.0.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **React Native** app. Package `@influto/react-native-sdk`
(npm, v1.6.0). Source: https://github.com/influto/influto-react-native.

## 1. Install
```bash
npm install @influto/react-native-sdk
# AsyncStorage is a native module — install it in the app too
npm install @react-native-async-storage/async-storage
```

## 2. Initialize (once, at startup)
Call this exactly once when the app launches. **`initialize()` THROWS on failure** — surface the
error, do not swallow it. Read the API key from env/secrets; never hardcode it into committed source.
```tsx
import InfluTo from '@influto/react-native-sdk';

// Call once at startup (e.g. in App.tsx)
await InfluTo.initialize({
  apiKey: 'YOUR_API_KEY',
  debug: __DEV__,
});
// RevenueCat apps: nothing else to wire — if react-native-purchases is
// installed, the SDK sets the influto_code subscriber attribute itself.
```

## 3. Check attribution (at launch)
Detect a referred user and gate any special offer / extended trial on `attributed`.
```tsx
const attribution = await InfluTo.checkAttribution();
if (attribution.attributed) {
  // User came from a referral — show a special offer / extended trial.
  // The SDK also sets the RevenueCat attributes influto_code + influto_referral.
  console.log('Referred by', attribution.referralCode);
}
```

## 4. Manual referral-code entry (optional)
Let a user type a code. The prebuilt code field (`ReferralCodeInput` on React Native, Flutter and web;
`InfluToReferralCodeInput` on iOS and Android) shows only the field + a valid/invalid state by
default — the creator/campaign **names are OFF unless you opt in**. Free-access (comp) codes are
redeemed with `setReferralCode()` (`grantsAccess`); gate premium on `checkAccess()`.
```tsx
// Validate, then apply a code the user typed
const result = await InfluTo.applyCode('FITGURU30');
if (result.valid && result.applied) {
  // Unlock the offer
}

// Or drop in the ready-made UI:
import { ReferralCodeInput } from '@influto/react-native-sdk/ui';
<ReferralCodeInput onApplied={(result) => {/* ... */}} />

// Free-access codes (INFLU-… or your comp codes): redeem with
// setReferralCode(code, appUserId) — grantsAccess === true means unlock
// premium now — and gate premium on (await InfluTo.checkAccess()).hasAccess.
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
```tsx
// Store-direct only (no RevenueCat). With expo-iap or react-native-iap installed,
// purchases are captured automatically on store-direct apps. To report
// manually instead, pass the store-signed proof:
await InfluTo.reportPurchase({
  platform: 'ios',                 // or 'android'
  signedTransaction: jwsString,    // iOS: StoreKit 2 JWS
  // purchaseToken: token,         // Android: Play Billing purchaseToken
});
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

Per-stack bundle: https://docs.influ.to/llms/react-native.txt · Full guide: https://docs.influ.to/sdk/react-native.md · Wire contract: https://docs.influ.to/contract.md
