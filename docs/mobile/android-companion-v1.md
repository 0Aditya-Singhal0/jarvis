# Android companion v1

## Scope and components

The Kotlin companion collects explicitly enabled local signals, keeps an encrypted offline outbox, and submits immutable v1 envelopes after pairing. It is not a hidden recorder, device administrator, root client, lock-screen bypass, or autonomous UI automator. It has no direct database, Docker, Hermes, broker-admin, cloud-model, backup-key, or raw-media-upload authority.

1. **PairingActivity** — visible owner-mediated enrollment.
2. **CaptureController and source adapters** — each source is registered separately and disabled by default.
3. **EncryptedOutbox** — sole reader/writer for queued records, sealed credentials, and media segments.
4. **SyncWorker** — network-constrained flush of existing envelopes; it never begins capture or executes actions.

No capture/sync endpoint exists until owner approval of a device-reachable TLS control-plane listener. EMQX credentials/listener are likewise unavailable until their separate approval.

## Enrollment, outbox, and retention

Pairing generates a non-exportable Android Keystore identity key. An owner-issued single-use QR/token creates a pending device with public key and requested capabilities; no transport/action credential is received before owner approval. Later transport data is sealed to the device key and stored only in app-private encrypted storage.

Every source writes an immutable v1 envelope to the outbox before a network attempt. Sync uses bounded batches, preserves single-event idempotency, deletes only on accepted/exact-duplicate response, and uses backoff plus network constraints. Optional raw capture produces a separate encrypted media/reference event and derived-observation event; default raw TTL is 24 hours. Raw bytes never enter work data, intents, notifications, logs, cache, or shared storage.

All state is credential-protected app-private storage with Auto Backup/data transfer disabled. A per-install Keystore AES-GCM key encrypts records with fresh nonces and authenticated metadata. Interrupted writes are quarantined. Quota exhaustion stops the affected source and alerts visibly rather than silently evicting unexpired data. Reinstall/re-pair creates a new identity.

## Permissions and visible capture

Request each permission only after the user enables its named feature, with a rationale and cancel path. Re-check before use and fail closed after denial/revocation.

| Feature | v1 boundary |
|---|---|
| Notification metadata | Explicit notification-listener access; approved package/field allowlist only; never dismiss/click/reply/forward. |
| Location/activity | Foreground approximate location and separate activity recognition only; no background location in v1. |
| Ambient microphone/camera | Explicit user-started foreground service with matching runtime and foreground-service permissions. |
| Contacts/calendar | Deferred read-only scope; no writes. |
| Accessibility | Disabled by default; named low-trust fallback only after separate approval. |

`AmbientCaptureService` starts only from a visible user action, immediately displays a persistent notification naming active sensors/retention and a one-tap stop action, and never starts from boot, worker, push, alarm, receiver, or remote command. Process kill, permission loss, stop, or sensor failure ends capture and requires a new visible start. No continuous background location or silent microphone/camera activation exists.

## Locked-device and accessibility boundaries

When locked, the app may buffer/sync already-authorized data and show redacted notification only. It does not open apps, invoke intents, reply/send, inspect UI, request credentials, dismiss keyguard, or use accessibility. Actions become `requires_unlock`; after unlock, the user opens the app/notification and re-confirms the unchanged action.

When unlocked, every action requires matching unexpired Jarvis decision hash, exact device capability, and OS permission. Accessibility is a last resort for a named package/view/action allowlist with visible confirmation and a separate owner approval. It never unlocks, bypasses biometric/2FA/permission prompts, handles credentials, payments, security/account changes, settings, locked/background flow, or guessed retries.

## HIL gates and manual acceptance

Approve Android SDK/toolchain/dependency lock/signing before setup; TLS reachability and pairing before enrollment; each capability/source/permission separately; every ambient capture session; any retention/quota/allowlist change; and every accessibility flow/action grant.

Manual checks cover pending pairing, offline duplicate replay, host outage queueing, raw expiry, permission revocation, no boot/background ambient start, locked-action queueing, and safe notification/accessibility revocation. No Android SDK, Gradle, emulator, APK, or device action is authorized by this document.

## Deferred owner decisions

Android/target SDK and signing/distribution, endpoint/TLS/pinning/pairing transport, quota/default derived retention, notification allowlists, contacts/calendar scope, background-location policy, and whether any accessibility flow is needed.
