# Backup, restore, and key-custody procedure v1

## Purpose and scope

This procedure recovers the Phase-1 control plane on a clean host. It requires a user-entered startup passphrase, keeps the recovery key offline, preserves local-first media handling, and requires fresh device pairing and connector authorization after every restore.

Back up data, not runtime: source is restored from Git; archives contain service state and host-held encrypted media/export data. Docker images, WSL state, caches, logs, rebuildable indexes, and live credentials are excluded.

## Archive policy

- Create one encrypted, versioned archive at a user-selected local or removable destination outside the repository and Docker volumes. Its manifest is encrypted inside the archive.
- `control-plane` scope is required: PostgreSQL logical dump, Hermes persistent data, enabled MQTT persistent state, Jarvis state/media metadata, and required configuration templates.
- `media` scope is opt-in per run. The default excludes development raw media; media inclusion requires distinct owner approval.
- Maintain an append-only backup ledger containing archive ID, time, scope, schema/tool versions, checksum, destination class, approval reference, and status. It contains no secrets, raw media, contact names, or precise storage paths.
- Retain the newest seven successful control-plane archives. Retain media archives only when explicitly pinned. Pruning is an owner-approved, audited action.

## Encrypted manifest

```json
{
  "format": "jarvis-backup/v1",
  "archive_id": "uuid",
  "created_at": "RFC3339 UTC",
  "scope": {"control_plane": true, "media": false, "media_policy": "excluded|pinned_only|all"},
  "source": {"jarvis_version": "git commit", "compose_schema": "version", "postgres_major": 0, "hermes_version": "image digest", "mqtt_version": "image digest"},
  "contents": [{"logical_name": "postgres.dump", "kind": "postgres-logical-dump", "sha256": "hex", "bytes": 0}],
  "encryption": {"scheme": "approved tool", "key_id": "non-secret fingerprint", "manual_unlock_required": true},
  "compatibility": {"minimum_restore_version": "...", "migration_required": false},
  "restore_requirements": ["empty-target", "re-pair-devices", "re-authorize-connectors"],
  "integrity": {"manifest_sha256": "hex", "archive_sha256": "hex"}
}
```

Logical names are generic service categories and never personal filenames or secret values.

## Backup procedure

1. Present scope, media inclusion, destination class, free-space estimate, and retention consequence to the owner.
2. On explicit approval, enter maintenance/read-only mode while devices buffer locally; record the approval in the ledger.
3. Capture a consistent PostgreSQL logical dump, service data, and approved host data; generate per-entry and archive checksums; encrypt and verify before publishing the archive.
4. Use encrypted host staging. If secure deletion cannot be assured, warn the operator that temporary plaintext may remain and rely on approved host-disk encryption.
5. Report archive ID, scope, checksum prefix, byte size, and outcome only. Jarvis never uploads or synchronizes archives automatically.

## Restore procedure

1. The owner explicitly approves initialization of a new, empty Jarvis data root after reviewing archive ID, version, scope, and compatibility.
2. The owner enters the primary passphrase locally. The offline recovery key is used only after an explicit choice and is never displayed, logged, or transmitted.
3. Verify the archive checksum and encrypted manifest before extraction; restore compatible state in maintenance mode.
4. Rotate local service credentials, invalidate device credentials, leave connectors disabled, and require every device to re-pair and every connector to receive fresh authorization.
5. Record restore completion in the ledger after the owner reviews restored state.

## Key custody and manual acceptance

Generate one recovery key only during user-attended setup. Keep it offline (for example, a printed record or hardware-encrypted removable storage) and never store it in the repository, Docker environment, archive, logs, or a device. Recovery-key use is an operator-entered audit event with timestamp, reason, and archive ID only.

Manual checks: verify a control-plane archive is encrypted and excludes media by default; restore a disposable clean data root and confirm devices/connectors remain disabled; reject a corrupt archive before target data is written; and require distinct approval for media inclusion.

## Installation-gated confirmations

Before implementation, the owner must approve the encryption/archive tool, host staging encryption, backup destination policy, PostgreSQL major-version/migration policy, and exact persistent-directory ownership after Compose topology is finalized.
