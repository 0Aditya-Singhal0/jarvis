# Versioned local event-ingestion contract (v1)

## Purpose and boundary

This is the canonical contract for events entering the Jarvis control plane from Android companions, room satellites, NVR/Home Assistant adapters, and future local sources. It makes PostgreSQL and the authenticated Jarvis API authoritative for acceptance, idempotency, retention, policy, and audit. MQTT is transport only: delivery to a broker is not evidence that an event was accepted.

An event describes a derived observation or an opaque reference to locally encrypted media. It is not a raw-media upload protocol, a credential exchange, a device-enrollment protocol, or a remote/cloud API.

## Required envelope

Every accepted envelope is JSON encoded, UTF-8, and has these fields.

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | string | Exact version, initially `jarvis.event.v1`. Unknown major versions are rejected. |
| `event_id` | string | Globally unique, stable across retries and exports. A producer must never reuse it for different content. |
| `source_id` | string | Opaque enrolled-source identifier. Never a name, phone number, room name, MAC address, or credential. |
| `occurred_at` | RFC 3339 UTC instant | When the underlying occurrence happened. |
| `observed_at` | RFC 3339 UTC instant | When this producer formed the observation. |
| `modality` | enum | One of `audio`, `vision`, `notification`, `location`, `activity`, `device_state`, `automation`, or `other`. |
| `classification` | enum | `derived`, `sensitive_derived`, or `restricted`; drives policy and query redaction. |
| `observations` | array | Derived, redacted facts only. No raw transcript, face embedding, raw action parameter, or personal contact data. |
| `retention` | object | Expiry and optional immutable pin declaration. |
| `provenance` | object | Producer version, capture window, and clock-quality declaration. |
| `media_ref` | object or null | Optional opaque local encrypted-media reference only. It must never contain a filesystem path, URL, key, or raw-media bytes. |

Optional context may include an opaque correlation ID and an opaque prior-event ID. Both remain data, not authorization.

## Minimal safe example

```json
{
  "schema_version": "jarvis.event.v1",
  "event_id": "evt_01JEXAMPLE7Y0P4FQK3W6V2H8A",
  "source_id": "src_01JEXAMPLE0A4G2HDV",
  "occurred_at": "2026-07-13T12:00:00Z",
  "observed_at": "2026-07-13T12:00:03Z",
  "modality": "device_state",
  "classification": "derived",
  "observations": [
    {
      "kind": "battery_state",
      "summary": "Battery level reported",
      "confidence": 1.0,
      "attributes": { "level_bucket": "medium" }
    }
  ],
  "retention": {
    "expires_at": "2026-07-20T12:00:00Z",
    "pinned": false
  },
  "provenance": {
    "producer_version": "1.0.0",
    "capture_window": {
      "start": "2026-07-13T12:00:00Z",
      "end": "2026-07-13T12:00:00Z"
    },
    "clock_quality": "synchronized"
  },
  "media_ref": null
}
```

This example intentionally contains no personal identity, location, raw transcript, media path, device credential, or transport topic.

## Semantics

### Identity and idempotency

The tuple `(source_id, event_id)` is the producer idempotency key. A retry with byte-equivalent canonical content returns the original accepted outcome. A retry with the same key but semantically different content is rejected as `event_id_conflict` and produces an audit record. The server may additionally retain a content fingerprint to diagnose producer faults; that fingerprint is not a substitute for the idempotency key.

Acceptance is owned by the API transaction. A broker ACK, HTTP connection close, local spool deletion, or queue dequeue is never an acceptance acknowledgement.

### Ordering and clocks

Producers may be offline and clocks may drift. The API stores receive time separately from `occurred_at` and `observed_at`; it must not silently rewrite producer times. `clock_quality` is one of `synchronized`, `estimated`, or `unknown`. Timeline ordering defaults to occurrence time with a stable server sequence tie-breaker and preserves the quality signal for review.

A capture window may be zero-length for instantaneous events. Its end cannot precede its start. An event may arrive after its retention expiry; the API records a redacted rejection or accepts it only under a policy explicitly designed for historical import.

### Observation and media boundary

Each observation has a producer-defined `kind`, safe human-readable `summary`, confidence in the closed interval 0..1 or `null`, and a tightly allow-listed attributes object. V1 does not permit arbitrary raw payload blobs.

`media_ref`, if supplied, contains only an opaque stable reference, encryption domain identifier, and coarse presence indicator. The ingest API verifies policy and reference shape but does not accept raw media. Media transfer, encryption keys, playback, and path resolution are separate local-only protocols.

### Retention and access

`retention.expires_at` is mandatory. `pinned` is a requested state, not an automatic permission; a policy decision must independently approve or deny pinning and audit that decision. Expired events are hidden from normal timeline queries and handled by the retention worker. Classification controls redaction and access decisions; it does not override consent, privacy-zone, owner-lock, or emergency-stop policy.

## Producer spooling and replay

A source maintains an encrypted local spool while the control plane is unavailable. It retains the same event ID and content across attempts, transmits oldest eligible entries first, and deletes an entry only after a durable API acceptance acknowledgement. Exponential backoff, bounded disk use, and source-local expiry are producer responsibilities.

On reconnect, a producer may replay out of order. The API accepts valid idempotent events independently, returns one outcome per event, and does not infer a contiguous sequence from arrival order. A revoked source is rejected before any new event becomes visible. Rejected entries remain locally inspectable only as safe, redacted operational metadata; they must never be rewrapped with a new identity to evade revocation or expiry.

## Outcomes

The future authenticated endpoint returns a redacted outcome:

| Outcome | Meaning |
| --- | --- |
| `accepted` | Durable server acceptance; includes the server receipt ID and a redacted sequence reference. |
| `duplicate` | Existing event is equivalent; includes the original acceptance reference. |
| `event_id_conflict` | Same source/event key with conflicting content; nothing new accepted. |
| `invalid_envelope` | Required field, type, clock, schema, or allow-list violation. |
| `policy_denied` | Source, classification, consent, privacy, lock, or emergency policy denied it. |
| `source_revoked` | Source is not currently permitted to submit. |
| `expired` | Retention policy rejects the event at ingestion. |
| `temporarily_unavailable` | No durable decision was made; safe to retry unchanged. |

No outcome contains sensitive stored data, media location, credentials, policy internals, or unredacted event content.

## Validation and audit invariants

The API must validate schema compatibility, opaque identifier syntax, UTC timestamps, capture-window ordering, confidence range, retention expiry, classification/attribute allow-lists, source capability, consent/privacy policy, and idempotency before acceptance. It appends a redacted audit record for acceptance, duplicate conflict, policy denial, revocation rejection, and expiry rejection.

The database schema, authenticated endpoint, migrations, replay tooling, Android agent, MQTT adapter, and timeline query implementation are intentionally out of scope for this contract. They must conform to this document in later reviewed changes.
