# Deliverable D08: Backend API & Real-Time Gateway

## Goal Description

Deliverable D08 establishes the **unified API gateway** for the SCOF platform. It exposes everything built in D01 through D07 as a coherent, frontend-consumable service layer.

Per SRS FR-8.1 through FR-8.3 and the architecture document (Section 4.6):

1. A **FastAPI REST service** on port `8000` provides endpoints to trigger disruption scenarios, run what-if simulations, fetch dashboard state, retrieve decision meeting logs / confidence views / replay traces, query evaluation benchmarks, support AI Chat over operational data, and expose active Domain Profile metadata.
2. A **Kafka event bus** decouples D01 disruption event injection from D05 agent orchestration, enabling event replay, fan-out to multiple consumers, and a clean boundary between simulation and intelligence layers.
3. A **WebSocket layer** pushes live supply chain state, decision notifications, and agent activity updates to connected frontend clients in real time.

The API service itself contains **zero domain logic** -- it is a thin orchestration and routing layer that delegates to the Coordinator (port `8010`), Consensus Engine (port `8020`), Observability Backend (port `8030`), and database services.

## Actual D05 Pipeline Contract

D08's role in the pipeline:

```
D08 (trigger via Kafka)
  |
  v
D05 Coordinator (internally: agents -> D06 consensus -> D07 persistence)
  |
  v
D08 receives OrchestrationResult (both ClaimBundle + DecisionRecord)
  |
  v
D08 publishes to Kafka scof.decisions.completed
  |
  v
D08 Kafka notification consumer broadcasts via WebSocket
D08 reads historical results from D07 Observability (meeting log, confidence, trace)
```

## Detailed Documentation

Please refer to the following documents for detailed architectural design:
- [API Design](./api_design.md)
- [Event Bus Design](./event_bus_design.md)
- [WebSocket Design](./websocket_design.md)
