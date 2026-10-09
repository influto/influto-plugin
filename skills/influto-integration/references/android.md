# InfluTo — Android (Kotlin)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.0.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **Android** app. Package `to.influ:android-sdk`
(Maven Central, v1.1.0). Source: https://github.com/influto/influto-android.

## 1. Install
```bash
// build.gradle.kts
dependencies {
    implementation("to.influ:android-sdk:1.1.0")
    // optional: Compose code field (InfluToReferralCodeInput)
    implementation("to.influ:android-sdk-ui:1.1.0")
    // optional: store-direct purchase auto-capture
    implementation("to.influ:android-sdk-billing:1.1.0")
}
```

## 2. Initialize (once, at startup)
Call this exactly once when the app launches. **`initialize()` THROWS on failure** — surface the
error, do not swallow it. Read the API key from env/secrets; never hardcode it into committed source.
```kotlin
import to.influ.sdk.InfluTo
import to.influ.sdk.InfluToConfig

// Call once at startup. initialize() is a suspend function — launch it from a
// coroutine, or use the callback overload: InfluTo.initialize(context, config) { result -> }
lifecycleScope.launch {
  InfluTo.initialize(applicationContext, InfluToConfig(
    apiKey = "YOUR_API_KEY",
    // RevenueCat apps: optional explicit setter (otherwise found by reflection)
    // revenueCatAttributeSetter = { attrs -> Purchases.sharedInstance.setAttributes(attrs) },
  ))
}
```

## 3. Check attribution (at launch)
Detect a referred user and gate any special offer / extended trial on `attributed`.
```kotlin
val attribution = InfluTo.checkAttribution()   // suspend
if (attribution.attributed) {
  // User came from a referral — show a special offer.
  Log.d("App", "Referred by ${attribution.referralCode}")
}
```

## 4. Manual referral-code entry (optional)
Let a user type a code. The prebuilt code field (`ReferralCodeInput` on React Native, Flutter and web;
`InfluToReferralCodeInput` on iOS and Android) shows only the field + a valid/invalid state by
default — the creator/campaign **names are OFF unless you opt in**. Free-access (comp) codes are
redeemed with `setReferralCode()` (`grantsAccess`); gate premium on `checkAccess()`.
```kotlin
// Validate + apply a code the user typed
val result = InfluTo.applyCode("FITGURU30")   // suspend
if (result.valid && result.applied == true) {
  // Unlock the offer
}

// Or the Compose field (android-sdk-ui): InfluToReferralCodeInput(onApplied = { result -> … })
// Free-access codes: setReferralCode(code, appUserId = userId).grantsAccess == true
// → unlock premium, and gate premium on InfluTo.checkAccess().hasAccess.
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
```kotlin
// Store-direct only (no RevenueCat). With the android-sdk-billing artifact on the
// classpath, purchases are captured AUTOMATICALLY. To report manually:
InfluTo.reportPurchase(
  purchaseToken = purchase.purchaseToken,
  // productId = "coins_100",  // one-time / consumable products only
)
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

Per-stack bundle: https://docs.influ.to/llms/android.txt · Full guide: https://docs.influ.to/sdk/android.md · Wire contract: https://docs.influ.to/contract.md
