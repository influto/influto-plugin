# InfluTo — notes for AI coding agents

> InfluTo is a referral & affiliate ATTRIBUTION platform for mobile apps (iOS, Android,
> React Native, Flutter). A developer creates an app + campaign at https://influ.to, drops in
> one of four native SDKs, initializes with an API key, and InfluTo attributes installs and
> validates in-app purchases to influencer referral codes — via either RevenueCat (webhook)
> or store-direct (Apple App Store Server API / Google Play service account).

The fastest correct integration is: (1) pick the ONE SDK matching the host app's stack, (2)
initialize() once at startup with the app's API key, (3) checkAttribution() at launch to detect
referred users, (4) choose exactly ONE purchase-validation path — RevenueCat OR store-direct
(never both — wiring both double-reports conversions), (5) verify with
GET /api/apps/{id}/events/recent. All SDKs share one wire contract; local state lives under the
@influto/ key prefix; codes are trim()+UPPERCASE before sending; network calls fail-soft (return
benign values) EXCEPT initialize() and reportPurchase(), which throw. The RevenueCat attribute
influto_referral is the STRING "true", never a boolean.

## Pick exactly one SDK for the host stack

| Platform | Language | Package | Registry | Version |
|---|---|---|---|---|
| React Native | TypeScript | `@influto/react-native-sdk` | npm | v1.5.0 |
| iOS | Swift | `github.com/influto/influto-ios` | Swift Package Manager | v1.0.0 |
| Android | Kotlin | `to.influ:android-sdk` | Maven Central | v1.0.0 |
| Flutter | Dart | `influto` | pub.dev | v1.0.0 |

- Expo / React Native → React Native SDK · SwiftUI / UIKit → iOS · Kotlin / Java → Android · Dart → Flutter.

## The 5 things to get right
1. Install the ONE matching SDK (+ peer deps).
2. `initialize()` ONCE at startup with the API key (it THROWS on failure — surface it).
3. `checkAttribution()` at launch; gate referred-user offers on `attributed`.
4. Choose ONE validation path — RevenueCat webhook OR store-direct — never both.
5. Verify with `GET /api/apps/{id}/events/recent` (or the InfluTo MCP's `influto_integration_status`).

## Don't
- Don't hardcode the API key or put any `it_*` key / store secret in committed source or a tool argument.
- Don't set RevenueCat `influto_referral` to a boolean — it is the STRING `"true"`.

Full machine docs: https://docs.influ.to/llms.txt · Wire contract v1.0.0: https://docs.influ.to/contract.md
