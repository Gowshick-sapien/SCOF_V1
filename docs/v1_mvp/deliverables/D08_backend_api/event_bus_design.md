# Event Bus Design

## Topic Architecture

| Topic | Key Strategy | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `scof.disruptions.triggered` | `scenario_id` | D08 API (scenarios router) | D08 execution consumer | Decouple scenario trigger from orchestration execution |
| `scof.whatif.requested` | `whatif_id` | D08 API (what-if router) | D08 execution consumer | Unified execution path for what-if simulations |
| `scof.decisions.completed` | `decision_id` | D08 execution consumer (after D05 returns) | D08 notification consumer | Push completed decisions to connected clients |
| `scof.orchestration.failed` | `scenario_id` | D08 execution consumer (on D05 failure) | D08 notification consumer | Push orchestration failure notifications to clients |
| `scof.agents.activity` | `agent_id` | D05 Coordinator (during dispatch) | D08 notification consumer | Push agent lifecycle status to connected clients |

## DLQ Topic

| Topic | Purpose |
|---|---|
| `scof.dlq` | Dead-letter queue for messages that fail processing after all retries or fail deserialization |

**DLQ Event Schemas:**
1. **Processing Failure (Valid Envelope):**
```json
{
  "original_event": { ... },
  "error": "Exception details...",
  "dlq_reason": "MAX_RETRIES_EXCEEDED"
}
```
2. **Deserialization Failure (Invalid Bytes):**
```json
{
  "dlq_reason": "DESERIALIZATION_ERROR",
  "error": "JSONDecodeError...",
  "source_topic": "scof.disruptions.triggered",
  "partition": 0,
  "offset": 123,
  "timestamp": "...",
  "raw_payload_base64": "..."
}
```

## Event Envelope Schema

All Kafka messages -- including those published by D05 -- use a standardized envelope:

```json
{
  "event_id": "evt-a1b2c3d4",
  "event_type": "disruption.triggered",
  "schema_version": "1.0.0",
  "producer": "scof-api",
  "timestamp": "2026-08-14T20:00:00Z",
  "correlation": {
    "trace_id": "tr-...",
    "scenario_id": "sc-...",
    "profile_version": "1.0.0",
    "request_id": "req-..."
  },
  "payload": { ... }
}
```

Every event carries `event_id` (UUID, idempotency key), `schema_version` (for forward compatibility), `producer` (origin service), `timestamp` (UTC), and the full correlation context.

## Replay Event Envelope

Replay events generate a **new `event_id`** and a **new `trace_id`**, while retaining provenance via `original_event_id`:

```json
{
  "event_id": "evt-NEW-UUID",
  "original_event_id": "evt-ORIGINAL-UUID",
  "event_type": "disruption.triggered",
  "schema_version": "1.0.0",
  "producer": "scof-api",
  "timestamp": "2026-08-14T21:00:00Z",
  "correlation": {
    "trace_id": "tr-NEW-TRACE",
    "scenario_id": "sc-...",
    "profile_version": "1.0.0",
    "request_id": "req-..."
  },
  "payload": { ... }
}
```

To support this, D08 persists a copy of the published event payload in Redis (`published_events:{event_id}`) with a 7-day TTL matching Kafka's retention. The `/scenarios/replay` endpoint looks up this original event payload by `event_id`. This ensures replay is always a distinct event that passes idempotency checks, while the `original_event_id` field preserves the provenance chain for auditing.

## Consumer Architecture

The D08 API process runs two logically separated consumer roles within a single Kafka consumer group:

```
D08 API Process
  |
  +-- Execution Consumer (handler dispatch)
  |     scof.disruptions.triggered  -> handle_disruption_triggered
  |     scof.whatif.requested       -> handle_whatif_requested
  |
  +-- Notification Consumer (WebSocket dispatch)
        scof.decisions.completed    -> handle_decision_completed
        scof.orchestration.failed   -> handle_orchestration_failed
        scof.agents.activity        -> handle_agent_activity
```

Both roles share the same `AIOKafkaConsumer` instance and consumer group. Message routing is based on the topic name. The logical separation ensures that future extraction of the execution consumer into a standalone event worker service requires moving handler functions, not restructuring the consumer.

## Consumer Group Configuration

| Parameter | Value | Rationale |
|---|---|---|
| `group_id` | `scof-api-gateway` | Single consumer group for the API service |
| `auto_offset_reset` | `latest` | Only process events published after consumer startup. Historical replay is explicit via `POST /scenarios/replay`. |
| `enable_auto_commit` | `false` | Manual commit after successful processing |
| `max_poll_records` | `10` | Bounded batch size |

## Delivery Semantics

- **At-least-once delivery**: Offsets are committed only after successful processing. Duplicate processing is possible on consumer restart.
- **Idempotency**: All consumers (execution and notification) check the `event_id` against a common Redis set (`processed_events:{event_id}`) before processing. If already seen, the message is acknowledged and skipped. The Redis set entries expire after 24 hours. This guarantees no duplicate WebSocket broadcasts even with at-least-once delivery.
- **Retry policy**: Failed messages are retried up to 3 times with exponential backoff (1s, 2s, 4s). After exhaustion, the message is published to `scof.dlq` with the original event envelope plus error metadata.
- **Poison message handling**: Messages that fail deserialization are immediately sent to `scof.dlq` without retry, using the deserialization failure DLQ schema (with base64 raw payload).

## Notification Flow (No Duplicates)

The following invariant governs all real-time notifications:
> **WebSocket broadcasts are driven exclusively by Kafka notification consumers, never by HTTP handlers or execution consumers directly.**

### Disruption Trigger Flow
```
POST /scenarios/trigger
  |
  v
Publish to Kafka: scof.disruptions.triggered
  |
  v
[Execution Consumer] handle_disruption_triggered
  |  - Call D05 POST /orchestrate/full
  |  - Publish OrchestrationResult summary to Kafka: scof.decisions.completed
  |  - On failure, publish to Kafka: scof.orchestration.failed
  |  - (No WebSocket broadcast here)
  |
  v
[Notification Consumer] handle_decision_completed
  |  - Broadcast decision summary to ws/decisions/live
  |  - Invalidate Redis dashboard cache
  |  - Assemble and broadcast fresh state to ws/dashboard/state
```
