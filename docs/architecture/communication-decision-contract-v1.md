# Communication decision and scoped-permission contract (v1)

## Purpose and boundary

This contract decides whether a proposed communication or life-management action is drafted, requires approval, may use a narrowly scoped owner permission, or is denied. It is layered on the action-policy lifecycle: a recommendation is never an authorization, and a connector/executor cannot send, call, create, or modify anything without a valid API reservation.

V1 covers outbound messaging/calls, calendar requests, task/reminder changes, and constrained WhatsApp/deep-link flows. It does not enable Hermes, Gmail, Calendar, WhatsApp, OAuth, contacts, or external delivery.

## Decision inputs

The policy accepts a redacted request description and opaque references:

| Input | Rule |
| --- | --- |
| `operation` | A narrow requested verb, such as draft, send, call, propose calendar change, or open a user-confirmed deep link. |
| `principal_ref` | Opaque relationship/contact reference; raw address book data is not present in the decision view. |
| `task_context_ref` | Opaque task/calendar context reference, if any. |
| `channel_class` | Coarse channel, never a credential or provider token. |
| `change_signals` | Safe flags for new relationship, changed task, changed target, ambiguous identity, formal context, conflict, or connector uncertainty. |
| `risk_suggestion` | A model/rule suggestion with rationale category and confidence. It cannot skip policy or owner approval. |
| `request_fingerprint` | Immutable normalized payload fingerprint from the action-policy contract. |

Raw message text, contact identifiers, tokens, full calendar contents, private attachments, and model prompts are not returned in policy/audit/dashboard responses.

## Default decision matrix

| Condition | Required disposition |
| --- | --- |
| New or ambiguous relationship | Draft plus owner notification. |
| Formal, consequential, externally visible, or changed task context | Draft plus owner approval. |
| First use of a channel or target pattern | Draft plus owner approval. |
| Calendar conflict or unavailable availability data | Draft; never silently schedule. |
| Connector failure/unknown delivery status | No resend; mark outcome uncertain and require review. |
| User-confirmed deep-link flow | Present the link/action summary for foreground owner confirmation; no background call/send claim. |
| Explicit, matching, unexpired owner permission with unchanged context | May transition to approved through action policy, subject to all current safety checks. |
| Lock, emergency stop, privacy restriction, expired rule, or policy uncertainty | Deny or await approval; never auto-send. |

A casual relationship is not sufficient by itself for automatic delivery. Permission must match the exact principal, operation, channel class, task/context constraints, risk ceiling, and expiry.

## Scoped permissions

A permission is a revocable owner grant, not a blanket contact trust flag. It has an opaque `permission_id`, principal reference, allowed operation/channel, context constraints, maximum risk class, issue/expiry times, and status. The request fingerprint is not permanently whitelisted; a materially changed target, content class, schedule, task, or routing posture invalidates the match and re-enters draft/approval flow.

Permissions cannot authorize a call, external message, calendar mutation, deletion/export, device control, or cloud routing unless their exact scoped operation explicitly allows it. They expire automatically and can be revoked at any time. Policy reevaluates current lock, emergency, privacy, consent, connector, and context state at dispatch.

## Lifecycle and outcomes

The decision produces a redacted disposition that feeds the action-policy contract:

- `draft_required`: a draft may be prepared locally but cannot dispatch.
- `approval_required`: the owner must confirm the displayed immutable action ID and fingerprint.
- `permission_match`: a narrow permission matched; action policy still evaluates current safety conditions.
- `denied`: policy forbids the request.
- `uncertain`: input/connector/context is insufficient; no dispatch decision is made.
- `conflict`: a calendar/task conflict needs owner resolution.
- `delivery_unknown`: the executor cannot truthfully establish delivery; automatic retry is disabled.

A connector report of “sent” is an executor result, not a policy conclusion. Duplicate sends are prevented by the action ID/fingerprint and execution-reservation rules; a user who wants a new send creates a new action.

## Owner review and audit

A review surface shows safe operation/channel/target classes, decision disposition, reason categories, permission expiry/status, conflict/uncertainty, action expiry, and payload fingerprint. It does not show secrets, OAuth material, personal contact data, raw message bodies, message identifiers, attachments, or internal model traces.

The API appends redacted, immutable audit records for suggestion, policy decision, permission creation/revocation/expiry, owner approval/denial, reservation, connector result, and delivery uncertainty. An audit record never becomes proof that a call was placed, a message reached a recipient, or a calendar change took effect unless a later verified executor result explicitly says so.

Hermes skill configuration, OAuth, message drafting/sending, calls, calendar/task implementation, WhatsApp integration, UI/API routes, data schema, and automated tests are out of scope. Later implementation must preserve draft-first defaults, exact permission matching, re-evaluation on change, and truthful delivery handling.
