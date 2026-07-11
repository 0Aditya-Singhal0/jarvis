# Hermes integration boundary v1

## Role split

Hermes is reused as the agent orchestration layer for approved tools, schedules, memory, messaging gateways, and later Google Workspace skills. The Jarvis control plane remains authoritative for device enrollment, capabilities, action policy, approval state, audit, timeline metadata, and retention.

Hermes may request a narrowly scoped Jarvis adapter operation; Jarvis evaluates authorization and policy, records the decision, and returns a redacted result. Hermes never directly owns device credentials, media, policy state, or authoritative audit records.

## Phase-1 runtime posture

- Use the official Hermes image with a persistent `/opt/data` data location.
- Do not fork Hermes, mount the host Docker socket, forward host secrets into Hermes terminal containers, or expose the Hermes public API.
- Keep any dashboard access localhost-only through the approved reverse-proxy boundary.
- Treat Hermes as stateless outside its persistent data; Jarvis business state stays in PostgreSQL.
- Keep terminal/container persistence disabled by default. Any future workspace mount or environment forwarding requires an explicit owner review.

## Adapter contract

Adapters are allow-listed by operation and never expose unrestricted database, shell, Docker, or host-file access. A request includes the internal caller identity, operation name, redacted arguments, correlation ID, and optional linked policy decision. Jarvis rejects unknown operations, denied policies, expired decisions, unapproved cloud routing, and malformed arguments before execution.

Results contain only status, approved derived data, redacted metadata, and correlation IDs. They never contain raw media, credentials, backup material, or unbounded timeline results.

## Google Workspace onboarding

Workspace uses Hermes' OAuth-backed skill and is not a Jarvis-owned connector. It is deferred until the control plane and approval lifecycle are operational. Enable one service and consent scope at a time in this order:

1. Calendar
2. Gmail drafting
3. Contacts
4. Drive
5. Docs
6. Sheets

Each service requires a separate owner checkpoint for Google Cloud API enablement, OAuth client configuration, consent, token storage, capability/policy mapping, and manual verification. Gmail sending remains draft-only until the action-governance issue explicitly authorizes approved sends.

## Deferred security decisions

Before any adapter is enabled, resolve internal Hermes-to-Jarvis authentication and authorization, exact image version/digest pinning, and the persistent-data backup coverage. No OAuth, image pull, container start, or external connector enablement is authorized by this document.
