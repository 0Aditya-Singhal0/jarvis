# Manual operations acceptance playbook

This project uses owner-led acceptance, not automated tests. For every completed scenario, record date, operator, commit/image references, observed result, correlation IDs where applicable, and any deliberate deferral.

## Before runtime work

- Owner has approved exact image digests, package locks, secret/data paths, and commands.
- Docker reports a reachable Linux-container engine and Compose v2.
- Rendered Compose configuration has no secret value, only loopback Caddy exposure, no Docker socket/host networking, and only approved volumes/mounts.

## Control-plane startup

- Owner performs manual unlock and starts the approved Compose project.
- Local `Caddy /healthz` succeeds; direct host access to PostgreSQL, EMQX, Hermes, and Caddy administration fails.
- Restart/stop behavior does not bypass manual unlock/start policy.
- Named volumes persist approved state across container recreation; no raw-media or secret value appears in logs.

## API, policy, and audit

- Invalid configuration/database/schema state yields only the redacted API unavailable result.
- Exact duplicate event backfill is acknowledged without a second record; altered idempotency replay conflicts.
- New/ambiguous consequential actions await owner approval; stale, mismatched, expired, revoked, and already-dispatched decisions do not execute.
- Approval, execution outcome, timeout, and revocation create chronological redacted append-only audit entries.
- A revoked device is rejected by the control plane even if a broker-side operation is pending.

## EMQX and device lifecycle

- A provisioned device reaches only its own permitted MQTT topics; cross-device, shared/system, wildcard, retained-event, and unauthorized QoS operations are denied.
- Rotation activates only after acknowledged delivery; old credentials cannot reconnect.
- Revocation records broker completion or a truthfully pending broker reconciliation state.
- Restore/reconciliation identifies unexpected or mismatched broker records and requires owner approval before remediation.

## Privacy, retention, and recovery

- Dashboard shows only redacted metadata and opaque identifiers; it exposes no raw media, credentials, paths, tokens, or recovery material.
- Expired event/media data is absent by default; pin/unpin respects policy and is audited.
- A control-plane archive is encrypted, integrity-verified, and excludes raw media by default.
- Corrupt archive restore is refused before target writes; clean restore starts with devices revoked and connectors disabled until re-paired/re-authorized.

## Connectors and future integrations

For every later connector, Android capability, camera, Frigate, Home Assistant, model provider, LAN listener, or cloud route: record the exact owner approval, the minimal granted scope, the manual action/result, the failure/revocation path, and whether raw media remained local. A successful integration never implies approval for a broader connector, contact, device, or destination.
