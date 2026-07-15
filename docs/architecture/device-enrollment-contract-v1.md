# Device enrollment, capability, and revocation contract (v1)

## Authority and scope

The authenticated Jarvis API and its authoritative database decide whether a device exists, which credential version is current, what it may do, and whether it remains active. MQTT, an access token, a cached device record, or a successful transport connection never authorizes a device on its own.

This contract applies to Android companions, Pi satellites, NVR/Home Assistant adapters, and future local agents. It does not generate credentials, define a PKI, configure an MQTT ACL, enroll hardware, or provide remote administration.

## Opaque identity

A device has a server-generated opaque `device_id`. It must not encode a person, room, phone number, MAC address, serial number, IP address, hostname, or credential. Human-friendly labels are owner-local metadata and never used as an authorization key.

A device record has:

| Field | Meaning |
| --- | --- |
| `device_id` | Opaque stable identity. |
| `kind` | Coarse adapter class such as `android_companion`, `room_satellite`, `nvr_adapter`, or `automation_adapter`. |
| `state` | `enrolling`, `active`, `suspended`, `revoked`, or `retired`. |
| `credential_version` | Monotonic version currently accepted for this device. |
| `capability_set_version` | Monotonic declaration version, separately auditable from credentials. |
| `declared_capabilities` | Exact immutable capability names proposed by the device. |
| `granted_capabilities` | Owner/policy-approved subset of the declaration. |
| `last_reported_at` | A report timestamp, never proof that a device is presently on or off. |

A missing report is represented as unknown, not as offline, disabled, paused, or safe.

## Enrollment ceremony

Enrollment begins only from an authenticated owner-local control-plane session. The API creates a short-lived, single-use enrollment intent bound to a device kind, an allowed declared-capability envelope, and an owner acknowledgement. The intent contains no durable permission and expires without side effects if unused.

The candidate proves possession of fresh key material through the approved enrollment channel. The API verifies the ceremony, creates the opaque identity, records credential and capability versions, and enters `active` only after the owner/policy approves the requested capability set. Any optional platform attestation is evidence with an explicit verification status; it is not silently treated as universal trust.

No source may self-enroll by publishing to MQTT, replaying a prior event, presenting a device label, or using a broker connection.

## Capability model

A capability is a narrow verb/object pair. Examples include `event.publish.derived`, `status.report`, `command.receive.pause`, or `command.execute.speaker`; these names are illustrative only and not an executable ACL.

A device can perform only a granted capability, only while active, only using its current credential version, and only within the scope and policy conditions attached to that grant. Grants are deny-by-default. New hardware functionality requires a new declared capability and explicit approval; an updated application must not silently gain a broader grant.

Capability grants do not bypass action policy. A granted device command capability allows a device to receive an API-reserved dispatch, not to invent, approve, or execute a user-affecting action without the action-policy lifecycle.

## Credential rotation

Each device authenticates with a credential bound to exactly one `device_id` and credential version. Rotation issues a new version after owner/policy authorization and records a bounded overlap window if operationally needed. Once that window closes, prior versions are rejected. Credentials, public-key material, certificate details, token contents, and broker ACL values are never returned to dashboard or audit views.

A device that loses credentials re-enters an owner-approved recovery/enrollment process. It must never claim the old device identity through metadata or an event replay alone.

## Revocation, suspension, and retirement

- `suspended`: API rejects new privileged operations while preserving the record for investigation or restoration.
- `revoked`: terminal security decision for the current identity and credential lineage. New events and command acknowledgements are rejected before ingestion or side effects.
- `retired`: terminal administrative state; it remains auditable and cannot be silently reused.

Revocation immediately invalidates active credential versions and capability grants in the API authority. A broker/agent may learn it later, so MQTT connection state is operational telemetry only. The system records local revocation separately from remote/broker reconciliation. Until reconciliation is confirmed, the owner view says pending rather than claiming that a remote client stopped.

Undispatched action requests targeting a revoked device are revoked or denied by action policy. A request already in `execution_reserved` returns an execution-in-progress state; the system must not falsely claim that revocation cancelled a physical effect.

## Offline behavior

An active source may buffer its own derived events during host downtime under the event-ingestion contract. It keeps the original opaque identity and credential lineage; on reconnect the API checks the current device state, credential version, capabilities, consent/privacy policy, and event expiry before acceptance. A revoked or stale device cannot rewrap old spool entries under a new event identity to evade rejection.

Devices must not execute queued commands merely because they were locally received. A command requires a current API-bound execution reservation and remains subject to expiry, emergency stop, owner lock, and local safety checks.

## Redacted status and audit

The API records enrollment intent creation/expiry, enrollment decision, capability changes, rotation, suspension, revocation, retirement, rejected stale credentials, and broker reconciliation state in append-only redacted audit records. Device UI views may show opaque identity, exact granted capability names, credential/capability version numbers, last reported time, transport class, and reconciliation state. They must not show secret material, hardware identifiers, raw media, network addresses, full broker topics, or unredacted action parameters.

The database schema, enrollment endpoint, key generation, PKI, MQTT ACL implementation, Android/Pi/NVR/Home Assistant adapters, and automated tests are out of scope. Later implementations must preserve these authority, least-privilege, rotation, and revocation invariants.
