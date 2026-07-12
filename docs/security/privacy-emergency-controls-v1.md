# Privacy, consent, and emergency controls v1

## Default and precedence

Every capture source is disabled until an active owner consent grant exists. Consent authorizes future capture/processing only; it never grants action, cloud-routing, or raw-media access. Current privacy state and a redacted append-only audit transition commit atomically.

Effective state resolves: `global_panic` > `room_privacy` > `device_paused` > `source_paused` > `consent_missing|expired|revoked` > `active`. Higher state always suppresses lower grants; no device/source self-enables around suppression.

## Scopes and grants

V1 scopes are source (device + modality), device, room, and global. A versioned grant records opaque scope IDs, allowed modalities/purposes, effective/expiry times, retention rule/version, notice version/hash, owner, and state. It never stores guest identity, biometric/signature, raw media, precise address, credentials, or free-text personal rationale.

Source events require matching active consent and capability within occurrence range. Room privacy is enforced at capture nodes before storage/transmission; audio requires separate whole-room consent. Guest mode suppresses human-identifying audio/video/image/notification/location capture and never infers guest consent or identity.

## Visible pause and panic controls

Dashboard status shows effective state, consent expiry, retention, acknowledgement, and enforcement confirmation. Owner controls source/device pause, guest/room privacy, and global panic with explicit affected-scope confirmation. Every capable node must expose a visible local stop control and persist local suppression before reporting it.

Source pause stops new capture/media/ingestion/upload for that source; device pause also blocks device action dispatch. Room privacy suppresses mapped sources and revokes unexecuted room actions. Global panic blocks new capture acceptance, media upload, adapter dispatch, and outstanding nonterminal actions; it does not delete data, weaken audit, reboot hardware, or auto-resume.

Central commands are not proof of remote enforcement. Targets remain `pending` until acknowledgement of exact policy version and are visibly `unconfirmed` while offline; owners use local controls for offline devices. Local suppression survives restart/reconnect and takes precedence over outbox replay.

## Deletion, export, audit

Pause/revocation stops future collection only. Deletion requires an owner-confirmed scope/time preview; it deletes raw media first, then selected non-audit derived data. Backup copies are reported pending until their approved purge completes. Audit remains permanent and redacted, retaining only job/scope hashes, counts, actor, timestamp, and outcome.

Export is a separate encrypted owner-confirmed archive operation with explicit scope/destination. It excludes credentials, recovery keys, and live secrets by default. No automatic export or third-party sharing exists.

Audit every consent/control change, node acknowledgement/failure, post-pause rejection, action invalidation, and deletion/export outcome. Store opaque IDs/hashes, versions, reason, counts, and correlation only. Local notifications report state/failure without sensitive content on lock screens.

## Manual HIL acceptance

Verify exact-consent-only capture, precedence, offline local stop/outbox suppression, visible unconfirmed panic targets, source-level guest privacy, post-pause rejection, action invalidation, truthful in-progress actions, previewed deletion preserving redacted audit, and encrypted scoped export without secrets.

## Deferred owner decisions

Room/device mappings, signage/guest procedure, non-personal signals during guest mode, consent durations/notice, retention/quota, non-Android physical stops, backup purge/secure deletion, and any remote control surface.
