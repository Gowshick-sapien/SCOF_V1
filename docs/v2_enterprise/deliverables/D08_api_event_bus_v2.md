# Deliverable D08 (V2): Enterprise API Gateway & Streaming Event Bus

## 1. Overview & Objectives

Deliverable D08 upgrades the basic synchronous FastAPI endpoints of V1 into an enterprise-grade **API Gateway and Streaming Event Bus**. It provides the communication backbone that decouples disruption producers, multi-agent orchestration kernels, the cognitive twin simulation substrate, and downstream user interfaces ([ADR 002](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_apache_kafka_event_streaming.md)).

---

## 2. Architecture & Three-Channel Ingress

Disruptions and events enter the enterprise backbone across three distinct channels:

```text
                  ┌─────────────────────────────────────────────────────────┐
                  │                    INGRESS CHANNELS                     │
                  │  Channel A: Automated IoT / Maintenance ERP Webhooks    │
                  │  Channel B: Human Operations Escalation (D09 Console)   │
                  │  Channel C: Injected Benchmark Scenarios (D10 Harness)  │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                                               ▼
                  ┌─────────────────────────────────────────────────────────┐
                  │               FASTAPI ENTERPRISE GATEWAY                │
                  │       (REST Endpoints + Auth + CORS + Rate Limiter)     │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                               ┌───────────────┴───────────────┐
                               ▼                               ▼
                  ┌────────────────────────┐      ┌─────────────────────────┐
                  │  STREAMING EVENT BUS   │      │   WEBSOCKET BROADCAST   │
                  │   (Kafka / Redis 7)    │      │    (Tauri v2 UI Feed)   │
                  └────────────┬───────────┘      └─────────────────────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │    LANGGRAPH KERNEL    │
                  │    & TWIN SERVICE      │
                  └────────────────────────┘
```

---

## 3. REST API Endpoint Catalog

### 3.1 Digital Twin Service Endpoints (V2 Specification)
* **`POST /api/v2/twin/scenarios`** - Initializes an isolated Layer 3 execution sandbox.
* **`POST /api/v2/twin/scenarios/{id}/fork`** - Forks an active scenario into a counterfactual branch.
* **`POST /api/v2/twin/scenarios/{id}/simulate`** - Runs event-stepped forward propagation across specified horizon.
* **`POST /api/v2/twin/scenarios/{id}/advance`** - Advances discrete simulation clock by $k$ steps.
* **`POST /api/v2/twin/scenarios/{id}/counterfactual`** - Evaluates candidate interventions and returns state deltas.
* **`POST /api/v2/twin/scenarios/{id}/actions`** - Commits CD²F-approved interventions to Layer 3 state.
* **`GET /api/v2/twin/scenarios/{id}/evidence/{claim_id}`** - Retrieves verifiable evidence pack with SHA-256 digests.

### 3.2 Dynamic Capability Registry Endpoints
* **`POST /api/v2/capabilities/register`** - Registers a new service provider Capability Card.
* **`POST /api/v2/capabilities/match`** - Resolves semantic intent against registered capabilities and synthesizes bounded MCP tools.

### 3.3 Deliberation & Consensus Endpoints
* **`POST /api/v2/deliberations/run`** - Initiates a multi-agent deliberation cycle over an ingested disruption.
* **`GET /api/v2/deliberations/{run_id}/trace`** - Retrieves the 8-stage verbatim reasoning trace.
* **`POST /api/v2/deliberations/{run_id}/escalate/resolve`** - Submits human approval for Tier-3 escalations.

### 3.4 Full-Duplex WebSocket Broadcast
* **Route:** `/ws/v2/deliberation/{sim_run_id}`
* **Payloads:** Streams incremental LLM deliberation tokens, agent critique cards, consensus resolution events, and simulation clock ticks with $< 50\text{ ms}$ latency.

---

## 4. Streaming Event Bus Topics

The event-driven backbone isolates services across four canonical topics:
1. `scof.disruptions.inbound`: Unprocessed telemetry alerts, maintenance webhooks, and scenario triggers.
2. `scof.deliberation.transcript`: Agent-to-agent proposals, challenges, and votes.
3. `scof.consensus.committed`: Resolved actions emitted by the CD²F engine.
4. `scof.twin.state_deltas`: State modifications committed to Layer 3 simulation storage.

---

## 5. Acceptance Criteria & Verification Evidence

1. **API Latency Gate:** Non-LLM control endpoints respond in $\le 50\text{ ms}$ (p99).
2. **Streaming Throughput Gate:** Event bus handles up to 2,500 messages/sec with zero message drop.
3. **WebSocket Responsiveness Gate:** Deliberation token updates pushed to clients within $\le 35\text{ ms}$ of generation.
4. **Schema Enforcement Gate:** 100% of payloads validated via strict Pydantic v2 schemas; malformed requests rejected with detailed 422 Unprocessable Entity responses.
