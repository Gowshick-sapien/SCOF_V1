# Deliverable D8 — Backend API & Real-Time Layer

##  Objective
Expose pipeline capabilities (D1–D7) via FastAPI REST endpoints, WebSockets for live state updates, and Kafka for event-driven simulation decoupling.

---

##  Requirements Summary (from SRS)
- **FR-8.1**: FastAPI REST service for scenario triggers, what-if runs, dashboard state, meeting log, trace replay, and profile metadata.
- **FR-8.2**: Kafka/RabbitMQ event bus connecting simulation events to agent pipelines.
- **FR-8.3**: WebSocket layer pushing real-time supply chain state and decision notifications.
