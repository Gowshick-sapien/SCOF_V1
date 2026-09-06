# SCOF — Supply Chain Cognitive Orchestration Framework

**Powered by CD²F (Consensus-Driven Collaborative Decision Framework)**

SCOF is a profile-driven, multi-agent cognitive platform that monitors, predicts, and recommends mitigation decisions for complex enterprise supply chain disruptions.

---

## MVP Status: COMPLETED & OFFICIALLY ACCEPTED

The **SCOF Minimum Viable Product (MVP)**, encompassing Deliverables **D1 through D10**, is officially completed, empirically validated, and fully accepted. Deliverable D11 serves as the Post-MVP architectural roadmap for future research extensions.

* **Final MVP Acceptance Report**: [docs/deliverables/D10_integration_evaluation/results_report.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/results_report.md)
* **Master Acceptance Evidence**: [docs/deliverables/D10_integration_evaluation/acceptance_evidence.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/acceptance_evidence.md#sub-deliverable-d105-research-questions-synthesis--final-mvp-acceptance-report)

---

## Deliverable Tracking (`docs/deliverables/`)

Documentation, implementation plans, and acceptance evidence for each deliverable:

| Deliverable | Description | Status | Documentation Folder |
| :--- | :--- | :--- | :--- |
| **D1** | Simulation Environment & Synthetic Data Foundation | **Completed** | [`docs/deliverables/D01_simulation_data/`](./docs/deliverables/D01_simulation_data/README.md) |
| **D2** | Knowledge & Data Layer (Neo4j Graph + pgvector) | **Completed** | [`docs/deliverables/D02_knowledge_layer/`](./docs/deliverables/D02_knowledge_layer/README.md) |
| **D3** | Demand & Inventory Agents | **Completed** | [`docs/deliverables/D03_demand_inventory_agents/`](./docs/deliverables/D03_demand_inventory_agents/README.md) |
| **D4** | Supplier & Transport Agents | **Completed** | [`docs/deliverables/D04_supplier_transport_agents/`](./docs/deliverables/D04_supplier_transport_agents/README.md) |
| **D5** | Agent Orchestration & Protocols (LangGraph, MCP, A2A) | **Completed** | [`docs/deliverables/D05_orchestration/`](./docs/deliverables/D05_orchestration/README.md) |
| **D6** | CD²F Consensus Engine | **Completed** | [`docs/deliverables/D06_consensus_engine/`](./docs/deliverables/D06_consensus_engine/README.md) |
| **D7** | Observability & Explainability Backend | **Completed** | [`docs/deliverables/D07_observability/`](./docs/deliverables/D07_observability/README.md) |
| **D8** | Backend API & Real-Time Layer (FastAPI, WebSockets, Kafka) | **Completed** | [`docs/deliverables/D08_backend_api/`](./docs/deliverables/D08_backend_api/README.md) |
| **D9** | SCOF Desktop Operations Console (Tauri v2 + React 19 + Apple HIG) | **Completed** | [`docs/deliverables/D09_desktop_operations_console/`](./docs/deliverables/D09_desktop_operations_console/README.md) |
| **D10** | End-to-End Integration & Evaluation Harness | **Completed (MVP Complete)** | [`docs/deliverables/D10_integration_evaluation/`](./docs/deliverables/D10_integration_evaluation/README.md) |
| **D11** | Post-MVP Extension Points (Architecture Roadmap) | **Post-MVP Roadmap (Non-MVP)** | [`docs/deliverables/D11_post_mvp_extensions/`](./docs/deliverables/D11_post_mvp_extensions/README.md) |

---

## Core MVP Empirical Findings (Research Questions RQ1–RQ4)

The evaluation harness rigorously validated the CD²F engine against comparative baselines across 20 canonical disruption scenarios:

* **RQ1 (Decision Quality vs. Baselines)**: CD²F eliminates single-agent cognitive bias. In stress tests where a single agent asserted flawed confidence ($c=0.99$) on an aggressive action (`Cancel Backorders`), CD²F synthesized corroborating domain evidence to select the optimal mitigation (`Fulfill from Hub A`), yielding **+27.5% net stockout risk reduction** and **+7.7% fill rate delta**.
* **RQ2 (Consensus Robustness vs. Naive Majority)**: While Naive Majority Voting deadlocked in **60.0%** of calibration scenarios requiring arbitrary alphabetical tie-breaking, CD²F's continuous multi-factor weights ($W_i = w_i \cdot c_i$) achieved **0.0% tie-breaker rate (TBR)**.
* **RQ3 (Operator Transparency & Trust)**: All decisions produce an immutable 8-stage reasoning trail and verbatim meeting log persisted to PostgreSQL `scof.decision_records` and pgvector `scof.embeddings` (384-dimension vectors). Calibrated risk-tier escalation gating achieved Cohen's Kappa $\kappa = 0.894$ against expert ground truth.
* **RQ4 (Real-Time Latency & SLA Viability)**: Fast-Path autonomous mitigations resolve with a median latency of **330.0 – 335.0 ms** and P90 of **485.0 ms**, fully compliant with the $< 500\text{ ms}$ SLA. 60.0% of disruptions resolve autonomously, while 40.0% safely escalate to Slow-Path simulation or Human-in-the-Loop review.

---

## Documentation Index

All core project documentation has been organized into the [`docs/`](./docs/) directory:

- [Ideation & Vision](./docs/ideation.md)
- [Software Requirements Specification (SRS)](./docs/srs.md)
- [System Architecture](./docs/architecture.md)
- [Implementation Plan](./docs/implementation_plan.md)
- [Domain Binding Strategy](./docs/domain_binding_strategy.md)
- [Repository Structure & Layout](./docs/repository_structure.md)
- [D10 Final Results Report](./docs/deliverables/D10_integration_evaluation/results_report.md)
- [D10 Acceptance Evidence](./docs/deliverables/D10_integration_evaluation/acceptance_evidence.md)

---

## Domain Profiles (`profiles/`)

SCOF is domain-agnostic and relies on declarative Domain Profiles for supply chain context:
- Active Profile: [`profiles/mvp-electronics/`](./profiles/mvp-electronics/)

---

## Quickstart & Verification

1. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

2. Start background infrastructure (PostgreSQL, Redis, Kafka, Neo4j, Microservices):
   ```bash
   docker compose up -d
   ```

3. Run End-to-End Autonomous Pipeline Full Loop Verification:
   ```bash
   python scripts/verify_full_loop.py
   ```

4. Run Evaluation Test Suite (40 / 40 Tests):
   ```bash
   python -m pytest services/evaluation/tests/ -v
   ```

5. Launch Desktop Operations Console:
   ```bash
   cd desktop
   npm run tauri dev
   ```
