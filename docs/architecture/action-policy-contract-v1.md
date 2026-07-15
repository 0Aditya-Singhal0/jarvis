# Local action-policy and approval lifecycle contract (v1)

## Purpose and authority

This contract governs every proposed action that can affect a person, external system, device, schedule, message, stored data, or trust boundary. The authenticated Jarvis control API is the sole authority for lifecycle transitions and audit. Hermes, MQTT, Android, Home Assistant, and any connector are untrusted executors from this contract's perspective: they may receive a dispatch only after a valid API reservation.

V1 is local-only. It is not a permission to enable a connector, grant OAuth, send a message, create a calendar item, control a device, or make a cloud call.

## Immutable action request

A request is created once with a server-generated `action_id`, an opaque `principal_id`, an operation name, opaque target reference, redacted display parameters, risk and routing classifications, expiry, and an immutable canonical payload fingerprint.

The payload fingerprint is a domain-separated SHA-256 digest of the normalized executable payload. It binds an approval to exactly what the owner reviewed. Display parameters are a redacted projection only; credentials, tokens, recovery material, raw media, full message bodies, contact identifiers, and arbitrary connector payloads never enter the dashboard or audit display.

An API caller supplies an idempotency key when proposing an action. Reuse with equivalent content returns the original request. Reuse with different normalized content is rejected and audited as an idempotency conflict.

## States

| State | Meaning | Permitted next states |
| --- | --- | --- |
| `proposed` | Request recorded; policy has not completed. | `awaiting_approval`, `approved`, `denied`, `expired`, `revoked` |
| `awaiting_approval` | Owner confirmation is required. | `approved`, `denied`, `expired`, `revoked` |
| `approved` | A valid owner confirmation binds the current action ID and payload fingerprint. Not yet dispatched. | `execution_reserved`, `expired`, `revoked` |
| `execution_reserved` | Exactly one dispatcher holds the execution lease. | `executed`, `failed` |
| `executed` | Executor reported a terminal success. | none |
| `failed` | Executor reported terminal failure. | none |
| `denied` | Policy or owner denied dispatch. | none |
| `expired` | Approval window ended before an execution reservation. | none |
| `revoked` | Owner or safety policy revoked an undispatched request. | none |

Terminal records are immutable. A later desired action is a new request linked by an opaque predecessor reference, never an edit, retry, deletion, or state rewrite.

## Policy defaults

Policy evaluates before dispatch and must explain its outcome in a redacted, owner-visible reason category. V1 defaults to `awaiting_approval` for:

- every new or ambiguous relationship;
- formal, consequential, or externally visible task;
- message/call/send action, calendar mutation, data export/deletion, device control, or cloud-routing request;
- an action involving a changed target, changed context, uncertain identity, unavailable policy input, privacy zone, locked owner state, or emergency stop.

Only a narrowly scoped, explicit owner rule may produce a direct `approved` transition. A rule is bound to the principal, operation, target class, context/risk constraints, expiry, and a revocation handle. An executor never interprets a missing rule, cached approval, or broker delivery as permission.

## Owner confirmation and revocation

A live approval detail must show the action ID, operation, redacted target and parameters, principal/reason, expiry, context IDs, payload fingerprint, routing class, and execution warning. Confirmation submits the displayed action ID and fingerprint together.

The API approves only if all are true: the requester is the authenticated owner; the action is currently `awaiting_approval`; it is unexpired; the stored fingerprint matches; relevant policy, lock, privacy, and emergency state still permit it; and no dispatch reservation exists. Otherwise it returns a redacted error and leaves the request unapproved.

Revocation requires an owner-authenticated reason for an undispatched `proposed`, `awaiting_approval`, or `approved` request. It atomically sets `revoked`. A request already in `execution_reserved` returns `execution_in_progress` (HTTP 409 for an HTTP API); it must not falsely claim cancellation. Terminal actions cannot be revoked or altered.

## Dispatch and executor results

The dispatcher atomically transitions an eligible approved request to `execution_reserved` and issues a short-lived opaque execution grant bound to the action ID, fingerprint, executor identity, and lease. The grant is not a reusable bearer credential and is never shown in an audit/UI response.

The executor reports a terminal result against that reservation. Duplicate result reports are idempotent only when equivalent. An expired or mismatched reservation is rejected. A timeout becomes `failed` only through an explicit reconciler policy; lack of a broker message is not proof of failure or execution.

## Redacted outcome codes

| Code | Meaning |
| --- | --- |
| `approved` | Owner confirmation was accepted; action remains undispatched. |
| `policy_denied` | A policy or safety condition denied the request. |
| `approval_required` | Owner confirmation is required. |
| `stale_or_mismatched` | The submitted action ID/fingerprint no longer matches the current request. |
| `expired` | The request cannot be approved or dispatched after expiry. |
| `revoked` | The request was revoked before dispatch. |
| `execution_in_progress` | A dispatcher owns the execution reservation; no revocation claim is made. |
| `idempotency_conflict` | Caller reused its idempotency key for different content. |
| `temporarily_unavailable` | No lifecycle decision was made; caller may retry unchanged. |

Responses and audit entries must not expose secrets, raw payloads, personal contact data, raw media, media paths, OAuth material, executor grants, or unredacted policy internals.

## Audit invariants

Each proposal, policy result, owner confirmation attempt, revocation attempt, reservation, executor result, expiry, and reconciliation decision appends a redacted record. Audit is chronological, permanent, append-only, and non-editable. The audit identifies actor class, action ID, prior/new state, outcome code, timestamp, and safe reason category; it never stores the sensitive material required to execute an action.

Database schema, API routes, dashboard mutation controls, Hermes tools/connectors, OAuth, external communication, calendar integration, device control, and automated tests are intentionally out of scope. Later implementation must preserve these state and fingerprint invariants.
