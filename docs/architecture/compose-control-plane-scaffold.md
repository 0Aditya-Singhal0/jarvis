# Compose control-plane scaffold specification

## Purpose

This specifies the first single-host Compose topology without authorizing Compose-file implementation, image pulls, container startup, secret generation, external integrations, LAN/Internet exposure, or observability.

The Compose project name is `jarvis`. Image references must be reviewed immutable digests; floating tags are prohibited.

## Services and boundaries

| Service | Networks | Persistent storage | Host exposure | Initial role |
|---|---|---|---|---|
| Caddy | `edge`, `control` | none; read-only config | `127.0.0.1:${JARVIS_HTTP_PORT}:80` only | static status and future local proxy |
| Jarvis API | `control` | `${JARVIS_DATA_ROOT}` bind mount | none | future policy, enrollment, audit, and metadata authority |
| PostgreSQL | `control` | `postgres-data` | none | authoritative structured state |
| EMQX | `control` | `emqx-data`; read-only config | none | MQTT event transport and future device authorization |
| Hermes | `control` | `hermes-data:/opt/data` | none | reused orchestration, initially inactive externally |

`edge` and `control` are Compose-managed internal networks. Caddy is the sole published service; direct host access to Hermes, PostgreSQL, MQTT, Caddy administration, or diagnostics is prohibited. Caddy initially returns a non-sensitive scaffold status and `/healthz`; it does not expose Hermes as a substitute UI.

## Persistence, configuration, and secrets

- Use named volumes only for Caddy, PostgreSQL, EMQX, and Hermes state. Do not use anonymous volumes.
- Bind-mount media and encrypted export roots only into Jarvis API from a user-selected location outside the repository and Docker volumes.
- Commit only non-secret `compose.yaml`, `.env.example`, Caddy configuration, EMQX configuration template, and secret-file instructions.
- `.env.example` contains only project name, localhost port, data-root path, and image-digest variables.
- Actual single-purpose secret files remain outside the repository; they are never copied to `.env`, labels, logs, backups, or Git. Hermes receives no secret initially.
- Named-volume and host-directory encryption details remain governed by the backup/key-custody procedure.

## Security posture

- Hermes has no Docker socket, host-secret mount, published port, public API, connector, or OAuth configuration.
- PostgreSQL accepts no trust authentication and is reachable only by Jarvis API using a file-backed password.
- EMQX has anonymous access disabled and no device enrollment until its authentication and topic-ACL design is approved. Its richer authorization integrations are the reason it is preferred over Mosquitto for Jarvis.
- Caddy serves explicit local HTTP only; it has no automatic HTTPS, remote administration, certificate state, or persistent volume.
- No service has general outbound application egress. Future model-provider or connector egress requires a separate approved network rule.

## Startup and operations

All services use bounded local stdout logging and `on-failure:3` restart behavior so a Docker restart cannot bypass the manual unlock/start process. No service automatically runs migrations, restores data, enables connectors, enrolls devices, or sends actions.

PostgreSQL health must pass before Jarvis API starts. EMQX health and Hermes readiness are finalized only after inspecting their approved image documentation; do not invent health commands. Jarvis API will later expose an internal redacted `/healthz`; Caddy proxies user routes only after that signal passes.

## Human-in-the-loop gate

Before any Compose implementation or execution, present the owner with the exact images/digests, required secret files, host data paths, generated non-secret diff, and any image-pull/start command. The owner performs or explicitly approves every installation, image pull, secret creation, and service startup.

Manual review of a rendered future Compose configuration must confirm: only loopback Caddy access is published; no Docker socket or host networking exists; only the three named data volumes persist; no secret is rendered or logged; and services remain stopped until owner unlock/start action.

## Deferred decisions

EMQX authentication/authorization and MQTT topic-ACL policy, Hermes-to-Jarvis authorization, exact image commands and health signals, at-rest encryption implementation, Jarvis API implementation, dashboard routes, model routing, OAuth, observability, and external access are separate work.
