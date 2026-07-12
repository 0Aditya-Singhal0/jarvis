# Docker readiness gate

This gate verifies that the existing local Docker environment is ready for the Jarvis Compose work. It does not prescribe a host OS, WSL distribution, Docker installation path, or desktop configuration.

## Required state

- Docker is running and the CLI can reach its daemon.
- Docker Compose v2 is available.
- The daemon is configured for Linux containers.
- The current user can inspect Docker without elevation or configuration changes.

## Read-only verification

Run the following commands and attach the output to Issue #9:

```powershell
docker version
docker context show
docker compose version
docker info --format '{{.ServerVersion}} | {{.OperatingSystem}} | {{.OSType}}'
```

The expected result is Client and Server information, a usable Compose v2 command, and `OSType` equal to `linux`.

## Scope boundary

Passing this gate authorizes only subsequent review of the non-secret Compose configuration. It does not authorize image pulls, container startup, secret generation, OAuth, or external connector enablement; each remains an explicit human-in-the-loop checkpoint.
