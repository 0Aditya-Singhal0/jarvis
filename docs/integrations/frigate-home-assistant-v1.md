# Frigate and Home Assistant integration boundary v1

## Ownership

- **Frigate** owns cameras, RTSP, detection, recordings, snapshots/clips, and native retention.
- **Home Assistant** owns physical-device state, integrations, automations, scenes, scripts, and hardware execution.
- **Jarvis** owns policy, approval/revocation, redacted audit, derived event index, and its retention metadata.

Jarvis treats Frigate/HA input as untrusted and EMQX as transport only. v1 has event/status ingestion and a tightly governed opt-in Home Assistant action adapter. It excludes Frigate media/UI/API proxying, live feeds, clips, snapshots, thumbnails, identity recognition, raw-media transfer, and remote access.

## EMQX boundary

Frigate and HA each require their own owner-approved service identity and deny-by-default ACL; neither inherits device permissions. They receive no `$SYS`, `$share`, discovery, wildcard, retained-event, or broker-administration access.

Frigate uses a unique `jarvis/v1/frigate/<instance-id>` prefix and may publish only availability, event/review, and camera-role status topics. It subscribes to nothing in v1; restart/detection/recording/snapshot commands are denied. Snapshot publication is disabled. Jarvis allow-lists source/camera/object IDs, change type, timestamps, severity, labels, and confidence, discarding paths, URLs, media fields, and unrecognized data.

HA may publish only reviewed derived projections under `jarvis/v1/ha/<instance-id>/events` and `status`; no MQTT discovery or Frigate media topics. Jarvis is the only subscriber and validates source identity, topic, schema, size, classification, and allowed fields before creating a redacted record.

## Event and retention behavior

Frigate change feeds can emit `new`, `update`, and `end` for one source ID. Jarvis creates one immutable event for each canonicalized/redacted source revision using a derived idempotency key; exact redelivery is duplicate and a changed revision is a related new event. Availability/status becomes low-sensitivity state with a staleness marker; missing status means unknown, never safe/off.

Frigate media remains in Frigate local storage and outside Jarvis media references/backups in v1. Jarvis derived-event retention resolves independently at ingestion and never changes Frigate retention. Any camera retention increase, pin, audio, snapshot, or privacy-mask choice is a separate owner approval.

## Home Assistant actions

Jarvis reaches HA through an authenticated local REST/WebSocket adapter, not MQTT commands. The HA bearer token is a high-value external secret stored only in the approved local secret store.

v1 accepts only registered `home_assistant.run_script` actions. Each stable Jarvis action key maps to one pre-approved `script.jarvis_*` entity with allow-listed parameters. The adapter cannot call arbitrary services/entities, URLs, YAML, scenes, shell commands, or `automation.trigger`. Every call follows the action-governance payload-hash and approval lifecycle. `executed` means HA accepted dispatch, not physical-device completion; a later approved status projection is separate evidence.

## Failures, restore, and HIL

Broker/Frigate/camera/HA failure never implies no activity or safe state. Duplicates are deduplicated; unavailable sources become stale/unknown; external effects never retry automatically. Credential/ACL mismatch disables the integration rather than enabling fallback access.

On restore, Frigate/HA identities, tokens, and ACLs are invalidated and both integrations start disabled until owner reauthorization and explicit re-enable.

Owner approval is required for every image/add-on pull, source/camera/HA connection, service identity/ACL/token, camera privacy/retention setting, selected event/projection, HA script mapping change, consequential action, rotation/reconciliation, listener/TLS change, or future media/notification integration.

Manual acceptance checks review ACLs and sanitized events, verify duplicate/revision handling and unknown stale status, approve one exact HA script action while distinguishing dispatch from physical effect, revoke an undispatched action, and confirm restore leaves both integrations disabled.
