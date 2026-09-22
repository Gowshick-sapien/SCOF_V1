# SCOF Track 1: V1 MVP Baseline Specification

## 1. Overview & Purpose

This directory preserves the **original V1 Minimum Viable Product (MVP) documentation and architecture** for the Supply Chain Cognitive Orchestration Framework (SCOF).

The V1 baseline represents the initial proof-of-concept that established:
* **The Core Multi-Agent Hypothesis:** Four specialist agents (Demand, Inventory, Supplier, Transport) coordinated via LangGraph.
* **CD²F Dynamic Consensus Arbitration:** Mathematical weighting ($W_i = w_i \times c_i$) eliminating deadlocks and greedy bias.
* **Dual-Path Autonomous Risk Gating:** Fast-path execution ($< 335\text{ ms}$) vs. slow-path human-in-the-loop escalation.
* **Desktop Operations Console:** Native Tauri v2 + React control room with 7 specialized operator views.
* **Empirical Verification:** 40 / 40 passing unit tests and benchmark evaluation over 20 canonical disruption scenarios.

> [!NOTE]
> All files in this directory are preserved as an immutable historical and baseline reference. For the active multi-domain enterprise expansion (30 business domains, 96 tables, 3.73M Neo4j nodes), see [`docs/v2_enterprise/`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/).

---

## 2. Document Index (Track 1)

| Document | Purpose |
| :--- | :--- |
| **[System Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/architecture.md)** | Technical specification of the 4-agent LangGraph topology, CD²F algorithm, and microservice layout. |
| **[Software Requirements Specification (SRS)](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/srs.md)** | Functional and non-functional requirements governing the V1 MVP. |
| **[Ideation & Theoretical Foundations](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/ideation.md)** | Theoretical rationale for multi-agent collaboration and research questions RQ1–RQ4. |
| **[Implementation Plan](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/implementation_plan.md)** | Original 11-deliverable milestone plan for V1 development. |
| **[Domain Binding Strategy](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/domain_binding_strategy.md)** | V1 concept for declarative Domain Profiles (`mvp-electronics`). |

---

## 3. Original V1 Deliverables (`deliverables/`)

Detailed design decisions, acceptance criteria, and evidence for Deliverables D01 through D11 as implemented in the V1 MVP:

* **[D01: Simulation Data & Profile Generation](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D01_simulation_data/README.md)**
* **[D02: Knowledge Layer (Neo4j, pgvector, ETL)](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D02_knowledge_layer/README.md)**
* **[D03: Demand & Inventory Agents](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D03_demand_inventory_agents/README.md)**
* **[D04: Supplier & Transportation Agents](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D04_supplier_transport_agents/README.md)**
* **[D05: LangGraph Orchestration & A2A Kernel](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D05_orchestration/README.md)**
* **[D06: CD²F Dynamic Consensus Engine](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D06_consensus_engine/README.md)**
* **[D07: Observability & Decision Trace Persistence](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D07_observability/README.md)**
* **[D08: FastAPI Gateway & Event Bus](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D08_backend_api/README.md)**
* **[D09: Desktop Operations Console (Tauri v2)](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D09_desktop_operations_console/README.md)**
* **[D10: Integration & Empirical Evaluation](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D10_integration_evaluation/README.md)**
* **[D11: Post-MVP Extensions Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D11_post_mvp_extensions/README.md)**
