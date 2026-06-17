---
name: influto-integration
description: >-
  Wire InfluTo referral/affiliate attribution into a mobile app and verify it is live. InfluTo
  attributes app installs and in-app purchases to influencer referral codes for iOS, Android,
  React Native, and Flutter apps. Use this skill when the user asks to add, integrate, set up, or
  debug InfluTo, or asks how to add affiliate, referral, or influencer attribution / referral-code
  tracking to their app, or to attribute RevenueCat or store purchases to a referral. It detects
  the app's stack, installs the right SDK, picks RevenueCat vs store-direct validation, and
  verifies a real attributed conversion arrived.
---

# Integrate InfluTo

InfluTo is a referral & affiliate **attribution** platform for mobile apps. A developer creates an
app + campaign at https://influ.to, drops in one of four native SDKs, initializes with an API key,
and InfluTo attributes installs and in-app purchases to influencer referral codes — via **either**
RevenueCat (webhook) **or** store-direct (Apple App Store Server API / Google Play service account).

## Before you start — gather these

1. **The host app's stack.** Detect it (don't ask if you can tell):
   - `package.json` with `react-native`/`expo` → React Native (`references/react-native.md`)
   - `*.xcodeproj` / `Package.swift` / Swift sources → iOS (`references/ios.md`)
   - `build.gradle(.kts)` + Kotlin/Java → Android (`references/android.md`)
   - `pubspec.yaml` → Flutter (`references/flutter.md`)

   (React Native overrides the bare `ios/`+`android/` folders inside an RN app.)
2. **The InfluTo API key.** It comes from https://influ.to → create an app (or use the
   `influto` MCP's `influto_provision` if it is connected). Read it from env/secrets — never
   hardcode it into committed source.
3. **The validation path.** Detect, then confirm with the user:
   - RevenueCat present (`react-native-purchases`, the `RevenueCat`/`Purchases` pod,
     `purchases_flutter`, `com.revenuecat.purchases`) → **RevenueCat path** (`references/revenuecat.md`).
   - No RevenueCat but real StoreKit 2 / Play Billing usage → **store-direct**
     (`references/store-direct.md`).
   - **NEVER wire both — that double-reports conversions.**

## Steps (read the matching `references/*.md`, then apply)

1. **Install** the SDK (reference §1). Add the listed peer dependencies.
2. **`initialize()` ONCE at startup** with the API key (reference §2). This call **THROWS** on
   failure — surface the error, do not swallow it.
3. **`checkAttribution()` at launch** (reference §3); gate any referred-user offer / extended trial
   on `attributed`.
4. *(Optional)* add the manual `ReferralCodeInput` UI (reference §4). Privacy default: the
   referrer/campaign names are OFF — leave them off unless the user asks.
5. **Wire the chosen validation path:**
   - **RevenueCat:** confirm the InfluTo webhook is set on the dashboard (Settings → RevenueCat).
     The SDK sets the `influto_code` and `influto_referral` subscriber attributes automatically —
     nothing else to call. `influto_referral` is the STRING `"true"`, never a boolean.
   - **Store-direct:** auto-capture is ON by default for store-direct apps — usually nothing to
     call. Add manual `reportPurchase()` only if you disabled auto-capture (then set
     `autoCapture:false` so exactly ONE path runs). `reportPurchase()` THROWS; a 503 means retry
     (FX rate). One-time Android products must pass `productId` (+ price/currency).

## Invariants you must respect (see `references/contract.md`)

- All local state lives under the `@influto/` key prefix.
- Referral codes are `trim()` + `UPPERCASE` before sending.
- Network calls fail-soft (benign return) **EXCEPT** `initialize()` and `reportPurchase()`, which throw.
- RevenueCat `influto_referral` is the STRING `"true"`, never a boolean.
- Never wire both RevenueCat and store-direct.

## Verify it is live (do this last — do not claim success without it)

Run `scripts/verify_integration.py --app-id <APP_ID>`. It reads `INFLUTO_API_KEY` from **your**
shell env (the script, not the model, holds the credential) and prints a checklist from the live
`integration-status`. Or, if the `influto` MCP is connected, call `influto_integration_status`.
Confirm:

- `sdk_initialized` is true with the right `last_sdk_platform`;
- `sdk_events` show each tracked event once with the right `referral_code` + `platform`;
- after a sandbox purchase, `attributed_conversion_count >= 1`.

Golden expected wire shapes are in `fixtures/`.

> **Security:** never put a secret (`.p8`, service-account JSON, RevenueCat key, webhook secret) or
> any `it_*` API key into a chat message or a tool argument. Credentials go into env/secrets or the
> InfluTo dashboard's write-only form (via the `influto` MCP's signed deep-link). The verify script
> reads the key from your own env, never from the model.
