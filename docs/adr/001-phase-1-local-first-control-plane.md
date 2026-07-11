# ADR-001: Phase-1 local-first control-plane boundaries

## Status

Accepted — 2026-07-11

## Context

Jarvis is a portable, local-first personal-assistant platform hosted on a Windows PC through Docker Desktop and WSL. Phase 1 establishes the control plane without enabling broad integrations, remote access, or cloud media transfer.

## Decisions

- Bind the dashboard and Caddy proxy to localhost only. Serve HTTP locally; defer LAN, public exposure, TLS, and remote administration.
- Run Hermes with persistent `/opt/data`, no host Docker socket, no forwarded host secrets, and its public API disabled initially.
- Use PostgreSQL as the authoritative store for Jarvis identities, device capabilities, policies, action and audit metadata, event metadata, and retention rules.
- Use named volumes for PostgreSQL, Hermes, and MQTT. Keep encrypted exports and media outside the repository in a documented host directory.
- Require a manual passphrase unlock on host startup and maintain an offline recovery key. Restore requires device re-pairing and connector re-authorization.
- Treat action and audit metadata as append-only and permanent; exclude raw-media payloads and secrets.
- Permit cloud routing only after explicit policy approval and only for derived text or metadata. Raw media stays local.
- Defer observability to a dedicated later issue.

## Boundaries

- The custom control plane owns enrollment, policy enforcement, audit records, event metadata, retention rules, and Hermes adapters.
- Hermes remains a reused agent-orchestration component; Phase 1 does not fork or externally expose it.
- MQTT carries device and event traffic only; it is not the authoritative state store.
- Media resides in local encrypted storage; databases and audit records hold references and metadata, not media payloads.
- Google OAuth, connector enablement, Docker or WSL distribution installation, and external integrations are excluded from this decision.

## Acceptance criteria

- The Compose topology can be documented with only localhost-reachable user-facing endpoints.
- Hermes persistence, PostgreSQL, and MQTT use named volumes; media and export paths are outside the repository.
- The design describes passphrase-gated startup, recovery, re-pairing, and connector re-authorization.
- Stored audit entries omit secrets and raw media while retaining immutable action metadata.
- Cloud-routing rules reject raw media and require a recorded approval before derived content leaves the host.

## Consequences and follow-on decisions

Phase 1 is intentionally single-host and unavailable while that host is down. External access, TLS, connector onboarding, and observability remain separately approved work.

Before the Compose implementation can begin, the following follow-on issues must resolve the named-volume encryption approach, MQTT authentication and topic ACLs, Hermes-to-control-plane authorization, and the exact recovery-key and host-directory policy.
