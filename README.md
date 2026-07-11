# Jarvis

Jarvis is a local-first personal-assistant platform built around Hermes rather than a Hermes fork. It will combine a Docker Compose control plane with encrypted local storage, policy-governed device agents, and explicit human approval for consequential actions.

## Current status

The project is in Phase 1: repository governance and foundation design. No services, dependencies, credentials, or integrations have been installed or configured.

## Operating principles

- Reuse established components before building custom replacements: Hermes, Android, Frigate, Home Assistant, standard libraries, and approved dependencies.
- Keep raw media local by default; permit cloud reasoning only through explicit routing policy.
- Treat user approval as a required gate for installations, credentials, external integrations, task-list changes, and merges.
- Use GitHub Issues, one focused branch per issue, and pull requests for review. Do not use Git worktrees.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the delivery workflow.
