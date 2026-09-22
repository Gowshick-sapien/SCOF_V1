# SCOF V2 Deliverables Roadmap (D1 through D11)

## 1. Overview & Evolution Strategy

This directory houses the authoritative **V2 Deliverable Blueprints** for the SCOF Enterprise Cognitive Twin expansion. Each blueprint defines how the original V1 MVP deliverable is upgraded to leverage the 30-domain, 96-table, 3.73M-node enterprise dataset, establishing concrete technical requirements, acceptance criteria, and migration milestones.

---

## 2. Deliverables Evolution Matrix

| Deliverable | V1 MVP Baseline (Track 1) | V2 Enterprise Cognitive Twin (Track 2) | Status | Key Specification |
| :--- | :--- | :--- | :--- | :--- |
| **D01** | Procedural generation of 5 suppliers, 2 warehouses. | **Enterprise World & Simulation Foundation:** 96 tables, SHA-256 provenance, Day-0 baseline, and isolated scenario injection. | **Dataset Frozen; V2 Blueprint Ready** | [`D01_enterprise_simulation_foundation.md`](./D01_enterprise_simulation_foundation.md) |
| **D02** | Basic ETL to PostgreSQL, Neo4j, pgvector. | **Enterprise Knowledge Fabric:** PostgreSQL SoR, Materialized Neo4j Topology with bounded query contracts, pgvector semantic memory. | **Data Materialized; V2 Blueprint Ready** | [`D02_enterprise_knowledge_fabric.md`](./D02_knowledge_fabric.md) |
| **D03** | Simple single-model predictors for demand/inventory. | **Enterprise Demand & Inventory Agents:** Demand Agent (multi-model ensemble + 554 events) and Inventory Agent (multi-echelon stock rules) via MCP. | **V2 Blueprint Ready; Next Phase** | [`D03_demand_inventory_agents_v2.md`](./D03_demand_inventory_agents_v2.md) |
| **D04** | Rule-based delay checks for supplier/transport. | **Enterprise Supplier & Transport Agents:** Supplier Agent (vendor reliability scoring) and Transport Agent (dynamic multi-modal routing) via Neo4j. | **V2 Blueprint Ready; Next Phase** | [`D04_supplier_transport_agents_v2.md`](./D04_supplier_transport_agents_v2.md) |
| **D05** | Sequential LangGraph state machine. | **Orchestration & Protocol Kernel:** Resilient A2A kernel executing parallel agent deliberation with sub-second budgets. | **V1 Running; V2 Blueprint Ready** | [`D05_orchestration_kernel_v2.md`](./D05_orchestration_kernel_v2.md) |
| **D06** | Static confidence-weighted voting. | **CD²F Consensus Engine:** Multi-factor weighting ($W_i = w_i \times c_i$), greedy bias override, and tri-tier escalation gating. | **V1 Running; V2 Blueprint Ready** | [`D06_cd2f_consensus_v2.md`](./D06_cd2f_consensus_v2.md) |
| **D07** | Flat decision logging to PostgreSQL. | **Observability & Explainability:** Verbatim meeting logs, 8-stage reasoning traces, and pgvector precedent retrieval. | **V1 Running; V2 Blueprint Ready** | [`D07_observability_explainability_v2.md`](./D07_observability_explainability_v2.md) |
| **D08** | Basic FastAPI scenario trigger endpoints. | **API Gateway & Kafka Event Bus:** High-throughput event streaming decoupling disruption producers, orchestrators, and consumers. | **V1 Running; V2 Blueprint Ready** | [`D08_api_event_bus_v2.md`](./D08_api_event_bus_v2.md) |
| **D09** | Tauri desktop preview. | **Desktop Operations Console (Tauri v2):** 7 views, What-If Simulation Lab sliders, and zero-latency WebSocket updates. | **V1 Running; V2 Blueprint Ready** | [`D09_desktop_console_v2.md`](./D09_desktop_console_v2.md) |
| **D10** | Basic assertion scripts. | **Scientific Benchmarking & Evaluation:** Rigorous test harness enforcing tripartite state isolation across 20 canonical disruption benchmarks. | **V1 Running; V2 Blueprint Ready** | [`D10_benchmarking_evaluation_v2.md`](./D10_benchmarking_evaluation_v2.md) |
| **D11** | Future work notes. | **Modular Extension Interfaces:** Risk & Resilience Agent, Sustainability/ESG Agent, and external A2A cross-enterprise negotiation. | **V2 Blueprint Ready** | [`D11_post_mvp_extensions_v2.md`](./D11_post_mvp_extensions_v2.md) |

---

## 3. Implementation Phasing Strategy

* **Phase A (Foundations — COMPLETED):** D01 and D02 data layers fully generated, validated across 6 gates, and frozen in `datasets/` with `twin_service.py` operational.
* **Phase B (Specialist Intelligence — NEXT):** Refactoring D03 (Demand/Inventory) and D04 (Supplier/Transport) to bind to the V2 Knowledge Fabric via bounded MCP tools.
* **Phase C (Consensus & Execution):** Validating D05, D06, and D08 against complex enterprise disruption cascades.
* **Phase D (Operations & Scientific Benchmarks):** Deploying D09 Desktop Console against live V2 simulation streams and executing D10 benchmarks with zero state contamination.
