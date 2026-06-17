# InfluTo — Android (Kotlin)

> Generated from `frontend/lib/sdk.ts` (wire contract v1.0.0). Do not edit by hand.

Add InfluTo referral/affiliate attribution to a **Android** app. Package `to.influ:android-sdk`
(Maven Central, v1.0.0). Source: https://github.com/influto/influto-android.

## 1. Install
```bash
// build.gradle.kts
dependencies {
    implementation("to.influ:android-sdk:1.0.0")
    // optional: Compose UI (ReferralCodeInput)
    implementation("to.influ:android-sdk-ui:1.0.0")
    // optional: store-direct purchase auto-capture
    implementation("to.influ:android-sdk-billing:1.0.0")
}
```

## 2. Initialize (once, at startup)
Call this exactly once when the app launches. **`initialize()` THROWS on failure** — surface the
error, do not swallow it. Read the API key from env/secrets; never hardcode it into committed source.
```kotlin
import to.influ.sdk.InfluTo
import to.influ.sdk.InfluToConfig

// Call once (e.g. in Application.onCreate)
InfluTo.initialize(context, InfluToConfig(apiKey = "YOUR_API_KEY"))
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
Let a user type a code. The prebuilt `ReferralCodeInput` shows only the field + a valid/invalid
state by default — the influencer/campaign **names are OFF unless you opt in**.
```kotlin
// Validate + apply a code the user typed
val result = InfluTo.applyCode("FITGURU30")   // suspend
if (result.valid) {
  // Unlock the offer
}
```

## 5. Purchase validation — pick exactly ONE path
- **RevenueCat**: the SDK sets the `influto_code` + `influto_referral` ("true", a STRING) subscriber
  attributes automatically; you only confirm the webhook on the InfluTo dashboard. Nothing to call here.
- **Store-direct** (no RevenueCat): auto-capture is ON by default — usually nothing to call. Report
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
After running the app once, check `GET /api/apps/{app_id}/events/recent`:
- `sdk_events[]` shows each tracked event once, with the right `referral_code` + `platform`;
- if store-direct, `webhooks[]` shows a purchase with `"attributed": true` + the referral code.

_Per-stack bundle: https://docs.influ.to/llms/android.txt — Full contract: https://docs.influ.to/contract.md_
