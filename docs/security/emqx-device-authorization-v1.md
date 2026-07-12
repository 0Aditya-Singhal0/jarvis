# EMQX device authentication and topic authorization v1

## Decision

Use EMQX built-in-database password authentication keyed by authenticated client ID. Each enrolled device receives `dev-` plus a lowercase UUIDv7 without separators and a unique random broker password. Validate client IDs against `^dev-[0-9a-f]{32}$`; reject separators, wildcards, whitespace, and nonmatching values before provisioning.

There is one client-ID authenticator, no anonymous/fallback authenticator, and no superusers. Use an EMQX built-in-database authorizer with a final deny-all file rule and `no_match = deny`. EMQX remains internal-only until a separately approved listener and TLS design exists.

## Topic namespace

All application topics begin `jarvis/v1`. `$SYS`, `$share`, bare wildcards, and every other namespace are denied. Raw media and credentials are never MQTT payloads.

| Principal | Publish | Subscribe | Constraints |
|---|---|---|---|
| Device `dev-…` | `jarvis/v1/devices/${clientid}/events`, `acks`, `status` | own `commands/#`, `config` | QoS 0–1; only `status` may be retained |
| `jarvis-control-v1` | concrete device `commands/#`, `config` | device `events`, `acks`, `status` | QoS 0–1; only config may be retained |

A device cannot read another device tree, publish commands/configuration, use shared/system topics, or retain events, acknowledgements, or commands. The control identity is non-superuser and has no broker-administration permissions. MQTT status remains transport telemetry, never authoritative device state.

## Owner-mediated provisioning

1. The owner-approved Jarvis enrollment flow creates a pending device and stable client ID.
2. The owner approves device identity, type, and capability request before a broker identity exists.
3. A distinct **Provision MQTT access** action displays exact topic permissions, listener posture, and credential policy for owner approval.
4. The adapter creates the EMQX client-ID user and generic ACL profile; Jarvis records credential/ACL versions and broker reference, never the plaintext password.
5. Jarvis seals the one-time connection package to the enrolled device public key and delivers it once through the approved pairing channel. Failed delivery disables the broker identity.
6. Only an acknowledged delivery enables MQTT for the device. Broker ACLs contain transport scope; Jarvis capabilities still govern application authorization.

## Rotation, revocation, and reconciliation

Credential state includes version, issue/expiry times, state, broker reference, ACL profile version, and redacted failure reason. Every operation is audited.

Rotation is owner-approved. Jarvis seals and delivers a replacement, requires a signed receipt, updates the EMQX credential, and disconnects the old session. If delivery fails, the existing credential remains active until the owner retries or revokes it.

Revocation first marks the device revoked in Jarvis, then disables/deletes its EMQX identity and terminates the session. A broker failure becomes `broker_revocation_pending`, is audited, and is retried; it is never reported as complete prematurely. On restart/restore, reconciliation detects missing, extra, stale, or mismatched broker records and requires owner approval before remediation.

## HIL and audit

Required checkpoints: enabling the authenticator/authorizer; each provision, rotation, revocation retry, ACL-profile change, listener/TLS change, and restore exception. Audit only actor, device/client ID, ACL/credential versions, decision/correlation ID, outcome, and reason code—not passwords, verifiers, keys, or payloads.

Manual checks include own-topic-only access, rejection of invalid identifiers and credentials, denied cross-device/system/shared-topic access, rotation receipt before activation, failed broker revocation truthfully marked pending, and reconciliation requiring approval.

## Deferred owner decisions

- Device listener topology, TLS/certificate lifecycle, allowed networks/firewall, and relay policy.
- Credential rotation interval, expiry/grace policy, and reconciliation cadence.
- Sealed credential-package pairing transport and device-side key storage.
- Future non-device identities for Home Assistant, Frigate, or workers; none inherit these permissions.
