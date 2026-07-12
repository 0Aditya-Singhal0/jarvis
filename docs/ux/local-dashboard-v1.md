# Local dashboard UX contract v1

## Boundary

The dashboard is the owner's local review and approval surface—not a chat UI, remote administration portal, broker console, or raw-media viewer. It is localhost-only through Caddy. Every action uses authenticated owner control-API access; the browser's locality is not authorization.

Never render recovery material, service/device/broker credentials, OAuth tokens, raw media, media paths, or unredacted action parameters. Locked or unavailable state exposes no cached sensitive detail and disables mutations.

## Navigation

Persistent header: **Local only**, lock state, control-plane availability, cloud-routing posture, and an explicit raw-media-local notice.

1. **Overview** — pending count, current exceptions, and links to detail; not an observability dashboard.
2. **Approvals** — default view when pending actions exist; current, settled, and expired/revoked queues.
3. **Devices** — enrollment state, exact capabilities, last report, transport state, and redacted credential/ACL metadata.
4. **Timeline & retention** — derived metadata and expiry/pin state; no media playback or download.
5. **Audit** — newest-first append-only redacted records, correlation navigation, and future export only if API-backed.

## Approval and revocation

An approval detail shows decision ID, operation/target, redacted parameters, source principal, policy reason, expiry, linked context IDs, payload-hash fingerprint, routing classification, and execution warning. Approve repeats target, expiry, and hash in a confirmation and submits the displayed ID/hash. Stale, mismatched, or expired responses remain unapproved.

Revoke requires a reason for undispatched pending/approved decisions. During dispatch reservation, display `Execution in progress — revocation cannot be guaranteed`; preserve a `409 execution_in_progress` outcome and show the eventual truthful result. Terminal actions are immutable: no edit, retry, delete, or state rewrite.

## Devices, privacy, and retention

Device detail shows type, opaque identity, exact granted capabilities, enrollment/credential/ACL versions, last status report, and broker reconciliation state. MQTT transport is labeled non-authoritative. Revocation immediately shows local revocation and separately reports broker completion or pending status.

Timeline rows show time, device, modality, classification, derived summary, expiry, pin state, and opaque media-reference presence only. Pin/unpin is audited and unavailable when policy forbids it. Expired content is absent by default. Audit records are chronological, permanent, redacted, and never editable.

Persistent privacy labels state localhost-only, manual unlock, raw-media-local, and cloud policy. Capture status is `unknown` or `last reported` when stale; absence never implies off. Panic-stop, privacy zones, remote access, and surveillance controls remain absent until their APIs exist.

## Error and manual acceptance states

- **Locked:** no cached detail; unlock locally.
- **Unavailable:** non-sensitive service status and correlation ID only; no destructive retry.
- **Empty approvals:** no action was approved or executed by implication.
- **Conflict/expired:** preserve state, require re-review/new proposal, link audit.
- **Policy denial:** redacted code/message/correlation only; no override.
- **Broker reconciliation pending:** distinguish local completion from broker completion.

Manual walkthrough: exact approve, stale approval, undispatched revoke, execution-in-progress conflict, device approval/revocation, redacted audit/timeline review, and locked/unavailable behavior. Verify localhost-only exposure and no secrets/raw media in rendered content or browser responses.
