# ADR 002: Message Streaming Bus Selection — Apache Kafka vs. RabbitMQ and Redis Pub/Sub

---

## 1. Context and Problem Statement

SCOF is a reactive, event-driven platform where disruption signals (e.g. supplier delay notices, port closures, severe weather warnings) arrive asynchronously and must trigger multi-agent evaluation workflows. Furthermore, downstream systems—including the observability backend, audit logger, and real-time operations console—must consume decision records and agent reasoning events without tight point-to-point coupling.

The message streaming layer must guarantee high throughput, strict ordering of disruption events, event durability, and the capability to replay historical events for what-if counterfactual analysis.

---

## 2. Decision Drivers

* **Durable Event Log**: Disruption events and resulting decisions must be persisted on disk in an immutable log, not lost if consumers are temporarily down.
* **Stream Replayability**: Ability to rewind the event log and replay past disruption sequences for what-if analysis and model evaluation.
* **Decoupled Asynchronous Fan-Out**: Single disruption events must be fanned out independently to multiple consumer groups (Coordinator, Observability, WebSocket Gateway) with independent read offsets.
* **Dead-Letter Queue (DLQ)**: Built-in handling for malformed or failed orchestration payloads.
* **Self-Contained Deployment**: Feasible local containerized execution in Docker Compose without external enterprise cloud dependencies.

---

## 3. Considered Options

* **Option 1: Redis Pub/Sub**: In-memory ephemeral publish/subscribe mechanism.
* **Option 2: RabbitMQ**: Traditional AMQP message broker with exchange-to-queue routing.
* **Option 3: Apache Kafka (KRaft Mode)**: Distributed append-only event streaming platform.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Apache Kafka (KRaft Mode)**

### Rationale:
1. **Append-Only Commit Log vs. Ephemeral Queues**:
   * Redis Pub/Sub is strictly fire-and-forget; if the coordinator or observability service restarts, in-flight events are permanently lost.
   * RabbitMQ deletes messages once acknowledged by a worker, making historical event replay impossible without external archiving.
   * Kafka retains messages on disk according to configurable retention windows (`retention.ms = 604800000`, 7 days).
2. **Replayability for What-If Simulation**:
   * Supply chain operators need to replay past disruption events with altered parameters (e.g. testing higher inventory buffers on an earlier supplier delay). Kafka's offset rewind mechanism natively supports this requirement.
3. **KRaft Mode (No ZooKeeper)**:
   * Modern Apache Kafka (v3.7+) operates using the KRaft consensus algorithm, eliminating the need for an auxiliary Apache ZooKeeper container and dramatically reducing resource overhead in Docker Compose.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Guaranteed message durability and zero data loss during service restarts.
* Multi-consumer group isolation: Observability reads at its own pace without blocking real-time API responses.
* Standardized topic topology: `scof.disruptions.triggered`, `scof.whatif.requested`, `scof.decisions.completed`, `scof.agents.activity`, `scof.dlq`.

### Negative Consequences / Trade-offs:
* Higher initial memory footprint (~350 MB RAM for Kafka broker) compared to lightweight Redis.
* Requires containerized topic initialization scripts at startup (`kafka-setup`).

---

## 6. Implementation & Compliance Notes

* Service configuration in [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml) (`apache/kafka:3.7.0` container on port `9092`).
* Automated topic creation in `scof-kafka-setup` container.
* Topic consumers and producers implemented in [services/api/src/routers/scenarios.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/scenarios.py).

---

## 7. Related Decisions & Artifacts

* [ADR 003: Vector Database Selection](./003_pgvector_for_semantic_memory.md)
* [ADR 010: Real-Time State Caching with Redis](./010_redis_realtime_state_caching.md)
* [Event Bus Design Document](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D08_backend_api/event_bus_design.md)
