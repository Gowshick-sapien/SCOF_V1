# SCOF — Supply Chain Cognitive Orchestration Framework

**Powered by CD²F (Consensus-Driven Collaborative Decision Framework)**

SCOF is a profile-driven, multi-agent cognitive platform that monitors, predicts, and recommends mitigation decisions for supply chain disruptions.

---

## 📚 Documentation Index

All core project documentation has been organized into the [`docs/`](./docs/) directory:

- 📘 [Ideation & Vision](./docs/ideation.md)
- 📋 [Software Requirements Specification (SRS)](./docs/srs.md)
- 🏗️ [System Architecture](./docs/architecture.md)
- 🗺️ [Implementation Plan (Docker-Simulation MVP)](./docs/implementation_plan.md)
- 🧩 [Domain Binding Strategy](./docs/domain_binding_strategy.md)
- 📁 [Repository Structure & Layout](./docs/repository_structure.md)

---

## 📁 Deliverable Tracking (`docs/deliverables/`)

Documentation, plans, and acceptance evidence for each deliverable stage:

| Deliverable | Description | Documentation Folder |
|---|---|---|
| **D1** | Simulation Environment & Synthetic Data | [`docs/deliverables/D01_simulation_data/`](./docs/deliverables/D01_simulation_data/README.md) |
| **D2** | Knowledge & Data Layer (Neo4j + pgvector) | [`docs/deliverables/D02_knowledge_layer/`](./docs/deliverables/D02_knowledge_layer/README.md) |
| **D3** | Demand & Inventory Agents | [`docs/deliverables/D03_demand_inventory_agents/`](./docs/deliverables/D03_demand_inventory_agents/README.md) |
| **D4** | Supplier & Transport Agents | [`docs/deliverables/D04_supplier_transport_agents/`](./docs/deliverables/D04_supplier_transport_agents/README.md) |
| **D5** | Agent Orchestration & Protocols (LangGraph, MCP, A2A) | [`docs/deliverables/D05_orchestration/`](./docs/deliverables/D05_orchestration/README.md) |
| **D6** | CD²F Consensus Engine | [`docs/deliverables/D06_consensus_engine/`](./docs/deliverables/D06_consensus_engine/README.md) |
| **D7** | Observability & Explainability Backend | [`docs/deliverables/D07_observability/`](./docs/deliverables/D07_observability/README.md) |
| **D8** | Backend API & Real-Time Layer (FastAPI, WebSockets, Kafka) | [`docs/deliverables/D08_backend_api/`](./docs/deliverables/D08_backend_api/README.md) |
| **D9** | Frontend Dashboard (Next.js, Leaflet, Recharts) | [`docs/deliverables/D09_frontend_dashboard/`](./docs/deliverables/D09_frontend_dashboard/README.md) |
| **D10** | End-to-End Integration & Evaluation Harness (MVP Complete) | [`docs/deliverables/D10_integration_evaluation/`](./docs/deliverables/D10_integration_evaluation/README.md) |
| **D11** | Post-MVP Extension Points (Interface Stubs) | [`docs/deliverables/D11_post_mvp_extensions/`](./docs/deliverables/D11_post_mvp_extensions/README.md) |

---

## ⚙️ Domain Profiles (`profiles/`)

SCOF is domain-agnostic and relies on declarative Domain Profiles for supply chain context:
- 🔌 Active Profile: [`profiles/mvp-electronics/`](./profiles/mvp-electronics/)

---

## 🚀 Quickstart

1. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
2. Start background infrastructure:
   ```bash
   docker compose up -d
   ```
