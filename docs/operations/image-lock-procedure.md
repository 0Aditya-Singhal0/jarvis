# Image lock and approval procedure

Every runtime image must be pinned to an approved `linux/amd64` OCI digest before it appears in a runnable Compose configuration. Tags are discovery aids only; `latest`, major-only tags, and mutable references are prohibited.

## Current resolved record

The repository-root [`images.lock`](../../images.lock) contains the currently resolved Caddy, PostgreSQL, EMQX, and Hermes Linux/amd64 child digests, source URLs, and compressed sizes. It records metadata only: no image has been pulled and no service has been started. The future Jarvis API image remains pending its separately approved build.

Compose consumes full `repository@sha256:<64-hex-digest>` values through `.env`; never replace a lock with a tag. For multi-platform images, lock the selected `linux/amd64` child digest, not merely the manifest-list digest.

## Owner approval checklist

Before pulling each image, present:

1. Official registry/repository and publisher.
2. Selected version tag, full digest, platform, approximate download size, release notes, and security-relevant changes.
3. Runtime privileges, persisted paths, published ports, healthcheck, and network membership.
4. The exact pull command and expected local storage impact.

The owner explicitly approves each download. Approval for one digest does not authorize a tag update, a new platform, or a replacement image.

## Update procedure

Image upgrades are a dedicated change: review the changelog and security impact, update `images.lock` and the Compose value together, confirm backup status, receive owner approval, then pull and recreate only the affected service. Never silently repull or recreate services.

## Constraints

Resolving a digest does not authorize an image pull. Pulling an image does not authorize a service start. No image may receive host networking, a Docker socket, unreviewed host mounts, or secrets beyond its documented need.
