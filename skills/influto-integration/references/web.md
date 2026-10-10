# InfluTo — Web / Capacitor (TypeScript)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.6.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **Web / Capacitor** app. Package `@influto/web`
(npm, v1.0.1). Source: https://www.npmjs.com/package/@influto/web.

## 1. Install
```bash
npm install @influto/web
# Capacitor / Ionic apps (device info, storage, deep links):
npm install @capacitor/device @capacitor/preferences @capacitor/app
```

## 2. Initialize (once, at startup)
Call this exactly once when the app launches. **`initialize()` THROWS on failure** — surface the
error, do not swallow it. Read the API key from env/secrets; never hardcode it into committed source.
```ts
import InfluTo from '@influto/web';
import { capacitorAdapters } from '@influto/web/capacitor'; // Capacitor / Ionic only

// Call once at startup (Capacitor: after platform ready; PWA: on page load)
await InfluTo.initialize({
  apiKey: 'YOUR_API_KEY',
  appVersion: '1.2.3',
  ...(await capacitorAdapters()),   // omit in a plain PWA / browser
  // RevenueCat apps: revenueCat: revenueCatCapacitor(Purchases)  (from '@influto/web/revenuecat')
});
```

## 3. Check attribution (at launch)
Detect a referred user and gate any special offer / extended trial on `attributed`.
```ts
const attribution = await InfluTo.checkAttribution();
if (attribution.attributed) {
  // User came from a referral — show a special offer / extended trial.
  // With a RevenueCat binding the SDK also sets influto_code + influto_referral.
  console.log('Referred by', attribution.referralCode);
}

// Web deep links: referral links send web visitors to your app URL with
// ?influto_code=…&influto_click=… — the SDK claims them automatically.
```

## 4. Manual referral-code entry (optional)
Let a user type a code. The prebuilt code field (`ReferralCodeInput` on React Native, Flutter and web;
`InfluToReferralCodeInput` on iOS and Android) shows only the field + a valid/invalid state by
default — the creator/campaign **names are OFF unless you opt in**. Free-access (comp) codes are
redeemed with `setReferralCode()` (`grantsAccess`); gate premium on `checkAccess()`.
```ts
// Validate, then apply a code the user typed
const result = await InfluTo.applyCode('FITGURU30');
if (result.valid && result.applied) {
  // Unlock the offer
}

// React / Ionic React: drop in the ready-made field
import { ReferralCodeInput } from '@influto/web/react';
<ReferralCodeInput onCodeApplied={(code) => {/* ... */}} />

// Free-access codes: (await InfluTo.setReferralCode(code)).grantsAccess → unlock
// premium, and gate premium on (await InfluTo.checkAccess()).hasAccess.
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
```ts
// Store-direct only (no RevenueCat). Attach a purchase source and purchases are
// captured automatically — TWA/PWA on Play: digitalGoodsSource(); Capacitor:
// capgoNativePurchasesSource(); Cordova: cordovaPurchaseSource(). Or report manually:
await InfluTo.reportPurchase({
  platform: 'android',             // or 'ios'
  purchaseToken: token,            // Android: Play Billing purchaseToken
  // signedTransaction: jws,       // iOS: StoreKit 2 JWS
});
```

## 6. Invariants you must respect (wire contract v1.6.0)
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

Per-stack bundle: https://docs.influ.to/llms/web.txt · Full guide: https://docs.influ.to/sdk/web.md · Wire contract: https://docs.influ.to/contract.md
