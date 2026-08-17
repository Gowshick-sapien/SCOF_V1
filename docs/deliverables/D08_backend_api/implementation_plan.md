# Deliverable D08 Implementation Plan -- Backend API & Real-Time Gateway

## Goal Description
Deliverable D08 establishes the unified API gateway for the SCOF platform. It exposes everything built in D01 through D07 as a coherent, frontend-consumable service layer. It provides REST endpoints for triggering scenarios, fetching dashboard states, and retrieving historical decision logs, while utilizing Kafka and WebSockets to decouple long-running orchestration execution and push real-time updates directly to the frontend.

It accomplishes three primary requirements from the SRS:
- **FR-8.1**: A FastAPI REST service on port `8000` exposing synchronous and asynchronous endpoints (scenarios, what-if, dashboard, decisions, evaluation).
- **FR-8.2**: A resilient Kafka Event Bus topology decoupling disruption injections from D05 execution, implementing idempotency and execution vs. notification separation.
- **FR-8.3**: A WebSocket Real-Time Gateway pushing live UI updates (`dashboard/state`, `decisions/live`, `agents/activity`) driven strictly by the Kafka notification pipeline.

## Proposed Changes

### 1. D05 Coordinator Modifications
#### [MODIFY] [orchestrator.py](../../../services/coordinator/src/orchestrator.py)
- Add a new `orchestrate_full()` method returning an `OrchestrationResult` (containing both the `ClaimBundle` and the final `DecisionRecord`).
- Implement best-effort Kafka agent activity publishing to `scof.agents.activity` natively within the `dispatch_parallel` graph node.
#### [MODIFY] [main.py](../../../services/coordinator/src/main.py)
- Expose the new `POST /orchestrate/full` endpoint alongside the existing endpoints.
- Add robust Kafka producer lifecycle management to the FastAPI lifespan context.
#### [NEW] [orchestration_result.py](../../../shared/scof_shared/schemas/orchestration_result.py)
- Create the shared schema envelope returning both the initial claim bundle and the final resolved decision record.

### 2. Backend API Service Foundation
#### [NEW] [main.py](../../../services/api/src/main.py)
- Initialize the primary FastAPI app encompassing all routers, the error handler middleware, and CORS settings (`http://localhost:3000`).
- Implement async lifespan management for Redis, Kafka, and PostgreSQL resource pooling.
#### [NEW] [config.py](../../../services/api/src/config.py)
- Define standard environment variables (Kafka brokers, Redis host, Observability/Coordinator upstream URLs, TTL properties).
#### [NEW] [error_handler.py](../../../services/api/src/middleware/error_handler.py)
- A global exception handler middleware that natively generates and propagates `X-Request-ID` and `X-Trace-ID` correlation context to every downstream microservice request.

### 3. Kafka Event Bus Integration
#### [NEW] [bus.py](../../../services/api/src/events/bus.py)
- Implements a robust `EventBus` wrapper for `aiokafka`.
- Features logical Execution Consumer and Notification Consumer topologies sharing a single consumer group (`scof-api-gateway`).
- Enforces strict event idempotency checking via Redis `processed_events:{id}` keys.
- Implements resilient retry policies and explicit routing to a `scof.dlq` dead-letter queue for poison messages.
#### [NEW] [handlers.py](../../../services/api/src/events/handlers.py)
- Maps topics (e.g. `scof.disruptions.triggered`, `scof.decisions.completed`, `scof.orchestration.failed`) to the upstream HTTP coordination pipelines and downstream WebSocket broadcasters.

### 4. WebSocket Real-Time Channels
#### [NEW] [manager.py](../../../services/api/src/websocket/manager.py)
- A thread-safe `ConnectionManager` routing connected UI clients to logical `dashboard/state`, `decisions/live`, and `agents/activity` channels.
#### [NEW] [channels.py](../../../services/api/src/websocket/channels.py)
- The FastAPI websocket router exposing the realtime streaming endpoints.

### 5. REST API Routers
#### [NEW] [scenarios.py](../../../services/api/src/routers/scenarios.py)
- Exposes `POST /scenarios/trigger`, `POST /scenarios/replay`, and core metadata retrieval endpoints.
#### [NEW] [whatif.py](../../../services/api/src/routers/whatif.py)
- Endpoints to asynchronously execute and poll what-if simulation overrides.
#### [NEW] [dashboard.py](../../../services/api/src/routers/dashboard.py)
- `GET /dashboard/state` for aggregating cacheable supply chain entity counts and states.
#### [NEW] [decisions.py](../../../services/api/src/routers/decisions.py)
- Endpoints for full trace logic, meeting logs, and confidence arrays (delegating directly to D07 Observability).
#### [NEW] [evaluation.py](../../../services/api/src/routers/evaluation.py), [chat.py](../../../services/api/src/routers/chat.py), [profile.py](../../../services/api/src/routers/profile.py)
- Foundational supporting API routes for Domain Profile retrieval and baseline metrics.

### 6. Infrastructure & Deployment
#### [MODIFY] [docker-compose.yml](../../../docker-compose.yml)
- Register the newly constructed `api` service.
- Implement strict startup execution dependencies utilizing `kafka-setup`—ensuring all topics (like `scof.disruptions.triggered`) are instantiated with proper partition alignment and 7-day retention rules before any API/Coordinator microservices are permitted to boot.

## Verification Plan

### Automated Tests
- Verification of the replay endpoint ensuring `original_event_id` is maintained across newly generated `event_id` execution structures.
- Unit testing across the newly formulated components ensuring idempotency boundaries properly deduplicate WebSocket events.

### Manual Verification
- Testing WebSocket push notifications directly utilizing the `dashboard/state` endpoint to confirm Kafka seamlessly streams integrated state snapshots automatically upon orchestration completions.
- End-to-end verification triggering the `POST /scenarios/trigger` async event flow via Swagger UI and observing the eventual background persistence.
