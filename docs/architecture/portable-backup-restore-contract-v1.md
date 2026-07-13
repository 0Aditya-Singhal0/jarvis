# Encrypted portable backup and restore contract (v1)

## Purpose and non-goals

This contract defines a reviewable format and ceremony for moving Jarvis state and locally encrypted media between owner-controlled hosts. It preserves local-first operation, prevents silent authority cloning, and makes verification precede activation.

It does not generate an archive, create or export keys, dump a database, copy media, connect a device, or execute a restore. Those are later owner-approved runtime operations.

## Backup unit

A backup is an encrypted, versioned package with an unencrypted **minimal manifest** and encrypted content segments. The manifest is deliberately insufficient to access any protected data.

| Manifest field | Rule |
| --- | --- |
| `format_version` | Exact version, initially `jarvis.backup.v1`; unknown major versions are rejected. |
| `backup_id` | Fresh opaque identifier; never a host name, person, path, or device ID. |
| `created_at` | UTC creation instant. |
| `source_instance_id` | Opaque installation identity, not an authorization credential. |
| `content_set` | Coarse declared sections: state, configuration metadata, audit, and optional encrypted media segments. |
| `segment_index` | For each segment: opaque ID, ciphertext byte size, content type class, digest, and encryption-domain identifier. |
| `integrity_root` | Manifest-bound digest over canonical manifest data and segment digests. |
| `compatibility` | Minimum supported control-plane/data schema versions. |

The manifest contains no secret values, recovery material, database connection values, raw media paths, contact data, device labels, tokens, ACLs, or plaintext event/action data.

## Encrypted segments

All state, audit, configuration values, device records, policy definitions, and optional media are encrypted segments. Segment encryption uses authenticated encryption with a distinct data-encryption key per backup. The key is wrapped only for the owner-approved recovery mechanism; it is not embedded as plaintext, a reusable API token, or an environment variable.

Media remains encrypted at rest. The format may preserve opaque media references and retention metadata, but no viewer, playback, downloader, or cloud copy is implied. A backup does not grant a restore host access until its recovery ceremony succeeds.

## Export ceremony

1. The authenticated owner requests a backup plan that declares included content classes, retention effect, storage destination class, and expected size—not secret material.
2. Policy checks owner lock, emergency state, privacy/consent restrictions, media-export rules, and available storage.
3. The exporter creates a point-in-time, internally consistent state view and records an append-only redacted audit event.
4. It emits encrypted segments plus the minimal manifest, validates every segment digest and integrity root, then marks the package complete.
5. A failure leaves the source authoritative state unchanged and produces a redacted audit outcome. Partial packages are never restorable.

The export must not contain active credentials in a usable form. A later restore issues new local credential lineages rather than copying live client authority.

## Restore staging and verification

Restore always begins in a **staging** state on the destination host:

1. Owner selects a package and provides recovery authorization through the separately approved mechanism.
2. The restorer checks format, compatibility, canonical manifest integrity, every ciphertext digest, and authentication tags before importing any authoritative state.
3. It reconstructs state into an isolated staging store; it does not replace a running authority or expose a Caddy/dashboard/API endpoint.
4. It performs semantic verification: schema compatibility, audit chain consistency, policy/document versions, expiry handling, media-reference consistency, and absence of active copied credentials.
5. The owner reviews a redacted restore report. Only an explicit activation ceremony may promote the staged instance.

On any failed check, staging is discarded or retained only as encrypted forensic material under owner policy. The existing active instance remains unchanged.

## Activation, device reconciliation, and rollback

A restored instance receives a new `instance_id`. Devices are not silently transferred: their prior credentials are invalid for the new authority until each follows a fresh owner-approved reconciliation/enrollment flow. Offline spools remain subject to event ID, device state, credential version, capability, retention, and policy validation.

Activation creates an append-only redacted audit record and an owner-visible recovery point. If post-activation verification fails, rollback restores the prior destination authority from its own verified recovery point; it never rewrites audit history or resurrects revoked device credentials.

A backup is not a replication protocol. Concurrent independent instances must not exchange writes or claim shared device authority without a future explicit federation design.

## Retention, deletion, and audit

Backup retention is an explicit policy. Expiry/deletion removes packages and their associated wrapped data keys according to the owner-approved retention process, then appends a redacted audit event. A failed deletion reports truthfully; it must not claim cryptographic erasure before the key/segment deletion conditions are met.

Audit records include operation class, backup ID, source/destination instance IDs, stage, outcome code, and safe reason category. They exclude recovery material, segment contents, media locations, secrets, tokens, and personal data.

Database dumps, encryption implementation, key management, backup CLI/UI, object storage, device reconciliation endpoint, Compose wiring, and automated tests are out of scope. Later implementations must preserve verification-before-activation, new-instance identity, fresh device authority, and rollback invariants.
