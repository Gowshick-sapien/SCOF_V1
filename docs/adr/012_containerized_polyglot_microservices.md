# ADR 012: Service Fleet Packaging — Polyglot Containerized Microservices vs. Monolithic Deployment

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: SCOF Core Architecture Team, DevOps Leads
* **Consulted**: Backend Developers, QA Engineers
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

The SCOF platform comprises diverse subsystems with distinct operational responsibilities and library ecosystems:
* **Coordination**: LangGraph, A2A discovery client, state transitions (`:8010`).
* **Consensus Arbitration**: Pure vectorized NumPy/scikit-learn matrix calculations (`:8020`).
* **Observability & Embeddings**: SQLAlchemy, PostgreSQL connection pools, sentence-transformers (`:8030`).
* **Evaluation & Benchmarking**: Batch dataset loaders, comparative baseline runners (`:8040`).
* **Specialist Agents**: MCP tool servers, agent cards, domain reasoning (`:8011`–`:8014`).
* **API Gateway & Streaming**: FastAPI, WebSocket channel managers, Kafka consumer loops (`:8000`).

Attempting to run all of these systems in a single monolithic Python process causes dependency conflicts, makes graceful restarts impossible without dropping active WebSockets, and prevents isolated failure containment. Conversely, deploying a complex Kubernetes cluster introduces excessive infrastructure friction for local development and edge deployments.

---

## 2. Decision Drivers

* **Process & Fault Isolation**: An out-of-memory or dependency crash in one agent must not crash the API gateway or consensus engine.
* **Independent Scalability**: High-throughput components (e.g. API gateway) must be scalable independently from compute-heavy components (e.g. evaluation runner).
* **Local Simplicity**: The entire platform must spin up with a single deterministic command (`docker compose up -d`).
* **Health Probing & Resiliency**: Automated health check probes on every microservice container.

---

## 3. Considered Options

* **Option 1: Monolithic Single-Process Python Application**: Single large FastAPI server running background task threads.
* **Option 2: Kubernetes (K8s) Cluster**: Production cloud cluster with Helm charts.
* **Option 3: Containerized Microservices Fleet via Docker Compose**: Dedicated container per service with localized Dockerfiles and standardized health check probes.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Containerized Microservices Fleet via Docker Compose**

### Rationale:
1. **Clear Port & Responsibility Boundaries**:
   * Unified Gateway: `scof-api:8000`
   * Coordinator: `scof-coordinator:8010`
   * Consensus: `scof-consensus:8020`
   * Observability: `scof-observability:8030`
   * Evaluation: `scof-evaluation:8040`
   * Specialist Agents: `scof-agent-demand:8011`, `inventory:8012`, `supplier:8013`, `transport:8014`
2. **Localized Dockerfiles**:
   * Each microservice maintains its own `Dockerfile` in `services/<service>/Dockerfile`, allowing fine-grained caching of Python dependencies without invalidating unrelated services during builds.
3. **Automated Health Probes**:
   * Standardized `GET /health` endpoints configured in `docker-compose.yml` allow automated startup orchestration (`depends_on: condition: service_started`).

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Zero Python dependency collision across microservices.
* Single-command deployment: `docker compose up -d`.
* Predictable, isolated failure domains: individual agents can be updated or restarted in isolation.

### Negative Consequences / Trade-offs:
* Higher cumulative memory consumption (~1.8 GB RAM across all containers) compared to a single monolithic Python process.

---

## 6. Implementation & Compliance Notes

* Microservice service definitions in [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml).
* Health probe endpoints in each service (e.g. `services/api/src/main.py`, `services/consensus/src/main.py`).
* Verified via `python scripts/verify_full_loop.py` (Stage 1: Health audit of all 8 microservices).

---

## 7. Related Decisions & Artifacts

* [ADR 001: Orchestration Kernel Selection](./001_langgraph_orchestration_kernel.md)
* [ADR 008: Desktop Operations Console Architecture](./008_tauri_v2_desktop_operations_console.md)
* [D8 Backend API Documentation](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D08_backend_api/README.md)
