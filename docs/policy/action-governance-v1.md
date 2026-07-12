# Action governance v1

## Authority and invariants

Jarvis is the sole authority for policy evaluation, owner approval, revocation, timeout, and the permanent audit trail. An adapter may request or record execution but cannot bypass a Jarvis decision. PostgreSQL is authoritative; raw media, secrets, tokens, recovery material, and unredacted action payloads never enter decisions or audit metadata.

`POST /v1/policy/decide` creates a proposal, never an execution command. Each proposal is canonicalized and redacted before persistence, receives a `payload_hash`, and may authorize only that exact hash. Unknown action types, unauthorized principals, malformed input, raw-media routing, and missing policy prerequisites are rejected with a redacted audit record.

## Deny-by-default evaluation

1. Authenticate the owner, device, or approved internal-service principal and confirm exact `action.execute:<action_type>` capability for device execution.
2. Validate a registered action type, allow-listed parameters, and routing classification; wildcard action types and capability grants are forbidden.
3. Persist the redacted proposal and audit record atomically.
4. Deny when no enabled rule permits the action, context/routing violates a rule, or cloud routing includes anything other than explicitly approved `derived_text` or `metadata`. Raw media always denies.
5. Move a matching action to `awaiting_approval` unless the exact owner-approved rule grants auto-approval for that action, target, and context. Ambiguous, new, or consequential actions always await approval.

No connector, OAuth flow, or adapter action type is enabled by this design.

## State machine and dispatch

| From | Allowed transition | Condition |
|---|---|---|
| `proposed` | `awaiting_approval` | matching non-auto policy |
| `proposed` | `approved` | explicit owner auto-approval grant |
| `proposed` | `revoked` | invalidated before settlement |
| `awaiting_approval` | `approved` | owner approves matching hash before expiry |
| `awaiting_approval` | `revoked` | owner/policy/device revocation or timeout |
| `approved` | `executed` or `failed` | adapter reports matching hash before expiry |
| `approved` | `revoked` | revocation or expiry before dispatch |
| terminal | none | immutable |

Public states are exactly `proposed`, `awaiting_approval`, `approved`, `executed`, `failed`, and `revoked`. Row locks and state/expiry comparison ensure one approval, revocation, or expiry winner. Before an external effect, an adapter atomically reserves dispatch against an unexpired decision. Revocation during a reservation returns `409 execution_in_progress`; the eventual external result is recorded truthfully.

## Approval, timeout, and revocation

Owner approval submits the displayed decision ID and payload hash; stale, mismatched, or expired approval returns `409`. Every pending or approved decision has an explicit expiry. Sweeps and all approval/dispatch paths enforce it, revoking undispatched work with an auditable reason.

The owner may revoke an undispatched decision or a policy grant. Policy or device revocation immediately invalidates matching undispatched decisions, each with its own audit event. Completed or failed actions retain their history and cannot be rewritten.

Approval views show operation/target, redacted parameter summary, source principal, policy reason, expiry, linked context IDs, payload hash, and execution warning—never credentials, raw media, or unredacted sensitive values.

## Redacted append-only audit and manual checks

Every proposal, rejection, evaluation, transition, reservation, outcome, expiry, and revocation appends a permanent record with timestamp, correlation ID, principal, resource, outcome, reason code, relevant IDs, payload hash, and allow-listed redacted metadata. No audit update/delete API exists.

Manual HIL checks: ambiguous actions await approval without side effects; invalid/revoked/raw-media requests reject with one redacted record; only the exact displayed hash can be approved or reported; expiry and all revocation types block undispatched execution; and audit history remains chronological, irreversible, and redacted.

Before enabling adapters, separately decide Hermes-to-Jarvis service authorization plus device and MQTT credential/ACL design.
