# Deliverable D08 (V2): Enterprise API Gateway & Streaming Event Bus

## 1. Overview & Objectives

Deliverable D08 upgrades the basic synchronous FastAPI endpoints of V1 into an enterprise-grade **API Gateway and Streaming Event Bus**. It provides the communication backbone that decouples disruption producers, multi-agent orchestration kernels, the cognitive twin simulation substrate, and downstream user interfaces.

---

## 2. Architecture & Communication Channels

```
                  ┌─────────────────────────────────────────┐
                  │          EXTERNAL PRODUCERS             │
                  │  (IoT Sensors, ERP Webhooks, Scenarios) │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       FASTAPI ENTERPRISE GATEWAY        │
                  │       (REST Endpoints + Auth + CORS)     │
                  └─────────────┬───────────────────────────┘
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
        ┌─────────────────────┐   ┌─────────────────────┐
        │ STREAMING EVENT BUS │   │ WEBSOCKET BROADCAST │
        │  (Kafka / Redis)    │   │  (Tauri UI Feed)    │
        └──────────┬──────────┘   └─────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   LANGGRAPH KERNEL  │
        │    & TWIN SERVICE   │
        └─────────────────────┘
```

### 2.1 REST API Endpoint Catalog
* **Scenario Management:**
  * `POST /api/v2/scenarios/run` - Initiates a deterministic simulation run.
  * `GET /api/v2/scenarios/{scenario_id}/status` - Queries execution state and metrics.
* **Disruption Ingestion:**
  * `POST /api/v2/disruptions/inject` - Injects physical perturbations (asset failure, supplier blowout, route closure).
* **Deliberation & Consensus:**
  * `GET /api/v2/deliberations/{run_id}/trace` - Retrieves the 8-stage deliberation log.
  * `POST /api/v2/deliberations/{run_id}/escalate/resolve` - Submits human approval for Tier-3 escalations.
* **Knowledge & Twin State:**
  * `GET /api/v2/twin/inventory` - Queries real-time stock levels across 21 facilities.
  * `GET /api/v2/twin/graph/subgraph` - Retrieves bounded topological subgraphs.

### 2.2 Full-Duplex WebSocket Channel
* **Route:** `/ws/v2/deliberation/{sim_run_id}`
* **Payloads:** Streams incremental LLM deliberation tokens, agent critique cards, consensus resolution events, and simulation clock ticks with $< 50\text{ ms}$ latency.

---

## 3. Streaming Event Bus Topics

The event-driven backbone isolates services across four canonical topics:
1. `scof.disruptions.inbound`: Unprocessed telemetry alerts and scenario triggers.
2. `scof.deliberation.transcript`: Agent-to-agent proposals, challenges, and votes.
3. `scof.consensus.committed`: Resolved actions emitted by the CD²F engine.
4. `scof.twin.state_deltas`: State modifications committed to Layer 3 simulation storage.

---

## 4. Acceptance Criteria & Verification Evidence

1. **API Latency Gate:** Non-LLM control endpoints respond in $\le 50\text{ ms}$ (p99).
2. **Streaming Throughput Gate:** Event bus handles up to 2,500 messages/sec with zero message drop.
3. **WebSocket Responsiveness Gate:** Deliberation token updates pushed to clients within $\le 35\text{ ms}$ of generation.
4. **Schema Enforcement Gate:** 100% of payloads validated via strict Pydantic v2 schemas; malformed requests rejected with detailed 422 Unprocessable Entity responses.
