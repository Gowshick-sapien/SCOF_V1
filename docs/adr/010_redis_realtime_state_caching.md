# ADR 010: Real-Time State Caching & WebSockets — Redis vs. Direct PostgreSQL Polling

* **Status**: Accepted
* **Date**: 2026-08-16
* **Deciders**: SCOF Core Architecture Team, Real-Time Systems Leads
* **Consulted**: Backend Engineers, Desktop Console Developers
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

The SCOF Desktop Operations Console requires continuous real-time updates:
* Live KPI metric cards (Supply Chain Reliability, Stock Coverage, Disruption Risk).
* Live multi-agent activity indicators (whether agents are idle, investigating, or debating).
* Real-time operational alert broadcasts when disruptions are triggered.

If the desktop application polls PostgreSQL relational tables every second (or hundreds of concurrent desktop instances execute `SELECT` queries against `scof.decision_records` and simulation tables), the transactional database suffers connection pool exhaustion, elevated query latencies, and CPU contention with active decision-writing workloads.

---

## 2. Decision Drivers

* **Sub-Millisecond Read Latency**: Rapid retrieval of cached dashboard snapshots ($< 2\text{ ms}$).
* **Database Isolation**: Shielding PostgreSQL from high-frequency UI read polling.
* **WebSocket Channel State Management**: Fast pub/sub fan-out to active WebSocket clients (`/dashboard/state`, `/agents/activity`).
* **TTL-Based Ephemeral Expiration**: Automatic cache invalidation without writing complex cron cleanup routines.

---

## 3. Considered Options

* **Option 1: Direct PostgreSQL Polling**: Frontend clients query FastAPI, which executes SQL queries against PostgreSQL.
* **Option 2: In-Memory Python Process Cache**: Storing state dictionaries inside FastAPI process memory.
* **Option 3: Redis 7 In-Memory Key-Value Store & Pub/Sub**.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Redis 7 In-Memory Store**

### Rationale:
1. **Sub-Millisecond Ephemeral Caching**:
   * Dashboard state is aggregated and cached under `dashboard:state` with a 5-second Time-To-Live (TTL):
     ```python
     await redis_client.setex("dashboard:state", 5, json.dumps(mock_state))
     ```
   * Repeated incoming desktop queries are served directly from RAM in $< 1\text{ ms}$ without hitting disk.
2. **WebSocket Client Coordination**:
   * As agents perform investigations, they publish presence events to Redis channels. The API gateway consumes these channels and streams updates to desktop WebSockets (`ws://localhost:8000/dashboard/state`), enabling the live activity dots and event logs on the desktop console.
3. **In-Memory Cache vs. Process Memory**:
   * Using Redis ensures that state is shared seamlessly across multiple Uvicorn worker processes, which is impossible with in-process Python memory.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Zero query load on PostgreSQL for high-frequency dashboard telemetry.
* Instant UI responsiveness and smooth WebSocket streaming on the Desktop Operations Console.
* Clean handling of transient session data and rate limits.

### Negative Consequences / Trade-offs:
* Requires running a lightweight Redis container (`scof-redis:6379`) in Docker Compose (~15MB RAM footprint).

---

## 6. Implementation & Compliance Notes

* Redis container definition in [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml) (`redis:7-alpine`).
* Dashboard router in [services/api/src/routers/dashboard.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/dashboard.py).
* WebSocket broadcaster in [services/api/src/websocket/channels.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/websocket/channels.py).

---

## 7. Related Decisions & Artifacts

* [ADR 002: Message Streaming Bus Selection (Kafka)](./002_apache_kafka_event_streaming.md)
* [ADR 008: Desktop Operations Console Architecture](./008_tauri_v2_desktop_operations_console.md)
