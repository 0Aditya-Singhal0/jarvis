# Image lock and approval procedure

Every runtime image must be pinned to an approved `linux/amd64` OCI digest before it appears in a runnable Compose configuration. Tags are discovery aids only; `latest`, major-only tags, and mutable references are prohibited.

## Lock record

Record one entry for each image in the future `images.lock` file:

| Service | Official repository | Selected tag | Full OCI digest | Source URL | Platform | Size | Approval date |
|---|---|---|---|---|---|---|---|
| Caddy | `caddy` | pending | pending | pending | `linux/amd64` | pending | pending |
| PostgreSQL | `postgres` | pending | pending | pending | `linux/amd64` | pending | pending |
| EMQX | `emqx/emqx` | pending | pending | pending | `linux/amd64` | pending | pending |
| Hermes | `nousresearch/hermes-agent` | pending | pending | pending | `linux/amd64` | pending | pending |
| Jarvis API | local project image | pending | pending | repository build | `linux/amd64` | pending | pending |

The final Compose values must use the full `repository@sha256:<64-hex-digest>` form. For multi-platform images, record both the inspected manifest-list context and the selected `linux/amd64` child digest.

## Owner approval checklist

Before resolving or pulling each image, present:

1. Official registry/repository and publisher.
2. Selected version tag, full digest, platform, approximate download size, release notes, and security-relevant changes.
3. Runtime privileges, persisted paths, published ports, healthcheck, and network membership.
4. The exact pull command and expected local storage impact.

The owner explicitly approves the image reference and download. Approval for one digest does not authorize a tag update, a new platform, or a replacement image.

## Update procedure

Image upgrades are a dedicated change: review the changelog and security impact, update the lock record and Compose value together, confirm backup status, receive owner approval, then pull and recreate only the affected service. Never silently repull or recreate services.

## Constraints

Resolving a digest does not authorize an image pull. Pulling an image does not authorize a service start. No image may receive host networking, a Docker socket, unreviewed host mounts, or secrets beyond its documented need.
