# Local capacity profiler

## Purpose and boundary

The capacity profiler supports owner decisions before increasing camera count, retention, capture quality, device count, or model workload. It records local aggregate operational measurements only; it exports no telemetry and captures no raw media, prompts, payloads, credentials, device names, or precise locations.

## Measurement windows

Measure an explicit owner-selected workload window with a fixed local sampling interval. Every report records software/image versions, hardware class, active approved sources, window start/end, configuration revision, and whether the window is representative. A report is not a benchmark claim outside its recorded conditions.

## Metrics

| Area | Local aggregate measurement |
|---|---|
| Capture | event count/rate, encoded bytes, dropped/late counts, queue depth, source availability/staleness |
| Storage | total/free bytes, per-retention-class growth rate, volume/data-root utilization, archive size/count |
| Compute | process/container CPU, memory, GPU utilization/memory if available, inference/transcription latency percentiles |
| Network/sync | outbox backlog count/bytes/age, delivery success/failure/duplicate counts, reconnect count |
| Control plane | API request latency/status aggregates, policy queue age, decision expiry/revocation counts, database pool saturation |
| Broker | connection count, authorized/rejected operation counts, retained-message count/bytes, delivery backlog if exposed safely |

All labels are bounded categories (source class, modality, status code, component), never device identity, topic, message content, URL, path, or principal identifier.

## Review procedure

1. Owner approves the workload window, active sources, retention policy, and maximum local resource budget before measurement.
2. The profiler writes an append-only local report with aggregate metrics, threshold configuration, and redacted exceptions.
3. Dashboard displays trend, headroom, backlog age, and saturation warnings locally only.
4. Before expanding capacity, the owner reviews the report, current free storage, worst-case backlog, p95/p99 latency, and failure/reconnect behavior. Approval is recorded with the configuration change.

## Guardrails

Thresholds are owner-configured and start conservative: warn before storage exhaustion, sustained backlog growth, latency degradation, or resource saturation; stop new optional capture/processing before data corruption or uncontrolled eviction. A warning never silently deletes unexpired data, increases retention, enables cloud routing, changes capture mode, or starts hardware.

Profile data follows the append-only redacted audit policy. It may be deleted/exported only through a future owner-approved data-management flow. No metrics stack, hardware benchmark, camera workload, model workload, or telemetry exporter is enabled by this document.

## Manual acceptance

Verify a report contains only aggregate/local information; a configured saturation/backlog/storage threshold creates a local warning; optional workload is stopped before unapproved eviction; and a capacity expansion remains blocked until owner review records an explicit approval.
