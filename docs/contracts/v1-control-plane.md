# Jarvis control-plane contract v1

## Cross-cutting rules

- Requests and responses carry `schema_version: "v1"`; timestamps are RFC 3339 UTC and identifiers are opaque UUIDv7 strings.
- PostgreSQL is authoritative. A successful mutation is transactional and appends a redacted audit record; MQTT is transport only.
- Each request resolves an authenticated `owner`, `device`, or approved internal-service principal. Device credential issuance, MQTT ACLs, and Hermes authorization are follow-on security decisions.
- Raw media bytes, secrets, bearer credentials, and recovery material are forbidden in API payloads, timeline results, policy inputs, and audit metadata. `media_ref` is opaque local encrypted-storage metadata only.
- Unknown fields are ignored. Invalid versions, required fields, enums, or timestamps return `400 invalid_request` with no state change.

## Event ingestion

`POST /v1/events` accepts one immutable source event:

```json
{
  "schema_version": "v1",
  "event_id": "uuid",
  "device_id": "uuid",
  "occurred_at": "2026-07-11T12:34:56Z",
  "observed_range": {"started_at": "...", "ended_at": "..."},
  "modality": "audio|video|image|text|notification|location|activity|device_state|home_event|system",
  "media_ref": {"storage_key": "opaque", "content_type": "audio/...", "ciphertext_sha256": "hex", "bytes": 123},
  "observations": [{"kind": "transcript|object|notification|location|activity|state|custom", "value": {}, "confidence": 0.0, "derived_at": "...", "producer": "device|local-service"}],
  "access_classification": "private|sensitive|restricted",
  "retention": {"expires_at": "...", "pinned": false},
  "source_sequence": 42,
  "idempotency_key": "opaque"
}
```

Required fields are version, IDs, occurrence time, modality, observations, classification, retention expiry, and idempotency key. A range must include `occurred_at`; confidence is 0–1. A media reference is optional and must identify a locally validated encrypted object.

Only active, unrevoked devices with the exact `event.ingest:<modality>` capability may ingest. Deduplicate on `(device_id, idempotency_key)`: an exact replay returns the original result with `duplicate: true`; a changed replay returns `409 idempotency_conflict`. Reused event IDs return `409 event_exists`. Out-of-order events are accepted and ordered later by occurrence time then event ID.

## Device lifecycle

- Owner-only `POST /v1/devices/enrollment-tokens` creates a single-use, expiring bootstrap token for a device type and requested capabilities; persist only its hash.
- `POST /v1/devices/enroll` consumes that token with device metadata and a public key, creating a `pending` device only when the request matches the token.
- Owner-only `POST /v1/devices/{id}/approve` grants an explicit capability set and transitions `pending` to `active`.
- Owner-only `POST /v1/devices/{id}/revoke` transitions `pending` or `active` to `revoked`, blocks all future actions, and records a reason. Revocation is permanent; re-enrollment creates a new identity.

Supported v1 capabilities are exact-match namespaced values: `event.ingest:<modality>`, `action.execute:<action_type>`, `media.upload`, and `status.report`. Wildcard grants are prohibited.

## Timeline query

`POST /v1/timeline/query` is owner or internal-policy authorized; devices have no timeline-read capability in v1. It requires `from` and `to`, with optional device, modality, observation-kind, classification, expiration, and media-reference filters. Results are paginated (`limit` defaults to 100, maximum 500) with an opaque query-bound cursor.

Expired events are excluded by default. Returning media references requires owner authorization and never yields media bytes or a downloadable URL. Ordering is `occurred_at ASC, event_id ASC`.

## Policy decision and execution record

`POST /v1/policy/decide` accepts an action proposal, never an execution command. It records actor, action type/target/parameters, context event IDs, requested time, and routing classification. Parameters are canonicalized and redacted before persistence; unregistered action types are rejected.

States are `proposed`, `awaiting_approval`, `approved`, `executed`, `failed`, and `revoked`. New consequential or ambiguous actions default to `awaiting_approval`. Owner-only approval and revocation endpoints transition a decision; adapters may only record `executed` or `failed` for the proposal's exact payload hash. Expired or revoked decisions cannot execute.

Cloud routing is denied unless a recorded explicit owner policy permits it and content consists exclusively of `derived_text` or `metadata`. Any raw-media reference is rejected and audited.

## Audit and retention

Audit records are append-only and permanent: principal, operation, resource, outcome, correlation ID, related IDs, reason code, payload hash, and allow-listed redacted metadata. No update or delete API exists.

Retention rules scope by device, modality, and classification; they specify raw-media TTL, optional event/derived TTLs, and pin permission. The resolved rule/version and concrete expiry are stored at ingestion, so later rule changes do not rewrite existing events. Owner-only pinning is audited. Expiry deletes raw media first and records only a redacted outcome.

## Errors and manual acceptance

Use `400` validation, `401` unauthenticated, `403` authorization/policy rejection, `404` undiscoverable resource, `409` conflict, `410` expired token/decision, `422` semantic invalidity, `429` rate limit, and `5xx` transient failure. Errors contain only `{code, message, correlation_id}`.

Manual checks: exact duplicate backfill creates no second record; altered replay conflicts; a revoked device is rejected; raw-media cloud routing is denied; an ambiguous action awaits approval; expired/revoked decisions cannot execute; expired timeline data is hidden; and audit transitions are irreversible and redacted.
