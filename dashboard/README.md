# Jarvis dashboard shell

This directory is a dependency-free, localhost-only static owner review surface. It deliberately contains no API URL, credentials, raw media, device control, telemetry, or cached control-plane data.

## Running boundary

The shell is not a service by itself. When the Compose scaffold is approved and merged, Caddy must mount this directory read-only at `/srv/dashboard` and include `Caddyfile.fragment` inside its existing localhost-only site block.

Do not expose this directory through a public listener, add remote administration, or render raw media/media paths. The future authenticated control API—not this static bundle—owns all live data and mutations.

## Honest-state contract

Until API integration is implemented, the shell must remain in its explicit unavailable state:

- no approval can be confirmed or revoked;
- no device or capture state is asserted;
- no timeline or audit data is cached;
- absence of a report is never presented as “off”;
- no browser response carries secrets, recovery material, ACL metadata, OAuth tokens, raw media, media paths, or unredacted action parameters.

No automated tests are included, per project policy.
