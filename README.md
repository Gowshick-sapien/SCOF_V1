# SCOF — Supply Chain Cognitive Orchestration Framework

**Powered by CD²F (Consensus-Driven Collaborative Decision Framework)**

SCOF is a profile-driven, multi-agent cognitive platform that monitors, predicts, and recommends mitigation decisions for supply chain disruptions.

---

## Documentation Index

All core project documentation has been organized into the [`docs/`](./docs/) directory:

- [Ideation & Vision](./docs/ideation.md)
- [Software Requirements Specification (SRS)](./docs/srs.md)
- [System Architecture](./docs/architecture.md)
- [Implementation Plan](./docs/implementation_plan.md)
- [Domain Binding Strategy](./docs/domain_binding_strategy.md)
- [Repository Structure & Layout](./docs/repository_structure.md)

---

## Deliverable Tracking (`docs/deliverables/`)

Documentation, plans, and acceptance evidence for each deliverable stage:

| Deliverable | Description | Status | Documentation Folder |
|---|---|---|---|
| **D1** | Simulation Environment & Synthetic Data Foundation | Completed | [`docs/deliverables/D01_simulation_data/`](./docs/deliverables/D01_simulation_data/README.md) |
| **D2** | Knowledge & Data Layer (Neo4j Graph + pgvector) | Completed | [`docs/deliverables/D02_knowledge_layer/`](./docs/deliverables/D02_knowledge_layer/README.md) |
| **D3** | Demand & Inventory Agents | Completed | [`docs/deliverables/D03_demand_inventory_agents/`](./docs/deliverables/D03_demand_inventory_agents/README.md) |
| **D4** | Supplier & Transport Agents | Completed | [`docs/deliverables/D04_supplier_transport_agents/`](./docs/deliverables/D04_supplier_transport_agents/README.md) |
| **D5** | Agent Orchestration & Protocols (LangGraph, MCP, A2A) | Completed | [`docs/deliverables/D05_orchestration/`](./docs/deliverables/D05_orchestration/README.md) |
| **D6** | CD²F Consensus Engine | Completed | [`docs/deliverables/D06_consensus_engine/`](./docs/deliverables/D06_consensus_engine/README.md) |
| **D7** | Observability & Explainability Backend | Completed | [`docs/deliverables/D07_observability/`](./docs/deliverables/D07_observability/README.md) |
| **D8** | Backend API & Real-Time Layer (FastAPI, WebSockets, Kafka) | Completed | [`docs/deliverables/D08_backend_api/`](./docs/deliverables/D08_backend_api/README.md) |
| **D9** | SCOF Desktop Operations Console (Tauri v2 + React 19 + Apple HIG) | Completed | [`docs/deliverables/D09_desktop_operations_console/`](./docs/deliverables/D09_desktop_operations_console/README.md) |
| **D10** | End-to-End Integration & Evaluation Harness | Pending | [`docs/deliverables/D10_integration_evaluation/`](./docs/deliverables/D10_integration_evaluation/README.md) |
| **D11** | Post-MVP Extension Points | Pending | [`docs/deliverables/D11_post_mvp_extensions/`](./docs/deliverables/D11_post_mvp_extensions/README.md) |

---

## Domain Profiles (`profiles/`)

SCOF is domain-agnostic and relies on declarative Domain Profiles for supply chain context:
- Active Profile: [`profiles/mvp-electronics/`](./profiles/mvp-electronics/)

---

## Quickstart & Execution

1. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

2. Start background infrastructure:
   ```bash
   docker compose up -d
   ```

3. Run D1 Synthetic Simulation Data Generator:
   ```bash
   python -m services.simulation.src.main
   python scripts/verify_d1.py
   ```

4. Run D2 Knowledge & Data Layer Modular ETL Pipeline:
   ```bash
   python -m services.etl.src.main --mode full
   python scripts/verify_d2.py
   ```

5. Run Automated Test Suite:
   ```bash
   python -m pytest services/etl/tests/
   ```
