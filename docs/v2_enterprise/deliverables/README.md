# SCOF V2 Deliverables Roadmap (D1 through D11)

## 1. Overview & Evolution Strategy

This directory houses the authoritative **V2 Deliverable Blueprints** for the SCOF Enterprise Cognitive Twin expansion. Each blueprint defines how the original V1 MVP deliverable is upgraded to leverage the 30-domain, 96-table, 3.73M-node enterprise dataset, establishing concrete technical requirements, acceptance criteria, and migration milestones.

---

## 2. Deliverables Evolution Matrix

| Deliverable | V1 MVP Baseline (Track 1) | V2 Enterprise Cognitive Twin (Track 2) | Status | Key Specification |
| :--- | :--- | :--- | :--- | :--- |
| **D01** | Procedural generation of 5 suppliers, 2 warehouses. | **Enterprise World & Simulation Foundation:** 96 tables, SHA-256 provenance, Day-0 baseline, and isolated scenario injection. | **Dataset Frozen; V2 Suite Complete** | [Full Suite (7 Docs)](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/README.md) / [Blueprint](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation.md) |
| **D02** | Basic ETL to PostgreSQL, Neo4j, pgvector. | **Enterprise Knowledge Fabric:** PostgreSQL SoR, Materialized Neo4j Topology with bounded query contracts, durable pgvector semantic memory substrate. | **Completed & Verified** | [Full Suite (7 Docs)](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/README.md) / [Blueprint](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric.md) |
| **D03** | Simple single-model predictors for demand/inventory. | **Cognitive Agent Runtime & Vertical Slice:** Hybrid ML+LLM runtime, SARP-8 reasoning protocol, 6-layer prompt stack, decoupled Ollama provider, and Procurement & Supplier vertical research slice. | **Specification Frozen; Implementation Ready** | [Full Suite](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D03/README.md) / [Blueprint](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D03_demand_inventory_agents_v2.md) |
| **D04** | Rule-based delay checks for supplier/transport. | **Specialist Federation & Agent Cards:** 6-agent expansion, Agent Card V2, DomainOwnershipPolicy, Dynamic Capability Contracts, A2A lifecycle. | **Phase 2 Pipeline** | [D04_supplier_transport_agents_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D04_supplier_transport_agents_v2.md) |
| **D05** | Sequential LangGraph state machine. | **Agentic Retrieval & Evidence Fabric:** SCOFRetriever, MCP-governed retrieval, evidence provenance, two-tier RAG (operational facts vs historical precedent). | **Phase 3 Pipeline** | [D05_orchestration_kernel_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D05_orchestration_kernel_v2.md) |
| **D06** | Static confidence-weighted voting. | **Cognitive Orchestration & Deliberation:** LangGraph state machine, Deliberation Table, domain affinity routing, cross-examination, evidence sufficiency gate, Deliberation Readiness Gate. | **Phase 4 Pipeline** | [D06_cd2f_consensus_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D06_cd2f_consensus_v2.md) |
| **D07** | Flat decision logging to PostgreSQL. | **CD2F Arbitration & Counterfactual Decision:** CD2F objective function, Twin counterfactual evaluation, candidate normalization, DecisionSnapshot, DecisionPolicy. | **Phase 5 Pipeline** | [D07_observability_explainability_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D07_observability_explainability_v2.md) |
| **D08** | Basic FastAPI scenario trigger endpoints. | **Event & Runtime Backbone:** Kafka topic architecture, transactional outbox, SCOFEvent contract, consumer idempotency, API Gateway. | **Phase 6 Pipeline** | [D08_api_event_bus_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D08_api_event_bus_v2.md) |
| **D09** | Tauri desktop preview. | **Observability, Explainability & Desktop Console:** Decision trace, evidence visualization, trade-off explanation, Tauri v2 HITL console, DecisionRecord archival. | **Phase 7 Pipeline** | [D09_desktop_console_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D09_desktop_console_v2.md) |
| **D10** | Basic assertion scripts. | **Evaluation & Benchmark Suite:** Benchmark suite, ablation baseline ladder, empirical model selection and validation, R_i calibration, SLA validation, RQ1-RQ4. | **Phase 8 Pipeline** | [D10_benchmarking_evaluation_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D10_benchmarking_evaluation_v2.md) |
| **D11** | Future work notes. | **Modular Extension Interfaces:** Risk & Resilience Agent, Sustainability/ESG Agent, and external A2A cross-enterprise negotiation. | **Post-V2 Blueprint** | [D11_post_mvp_extensions_v2.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D11_post_mvp_extensions_v2.md) |

---

## 3. Implementation Phasing Strategy

* **Phase 1 (D03 — CURRENT):** Cognitive Agent Runtime & Vertical Slice (hybrid ML+LLM runtime, SARP-8 state machine, 6-layer prompt stack, decoupled Ollama provider, Procurement & Supplier vertical research slice).
* **Phase 2 (D04):** Specialist Federation & Agent Cards (6-agent expansion, Agent Card V2, DomainOwnershipPolicy, A2A lifecycle).
* **Phase 3 (D05):** Agentic Retrieval & Evidence Fabric (SCOFRetriever, MCP-governed retrieval, two-tier RAG: facts vs precedents).
* **Phase 4 (D06):** Cognitive Orchestration & Deliberation (LangGraph orchestrator, Deliberation Table, cross-examination, readiness gates).
* **Phase 5 (D07):** CD2F Arbitration & Counterfactual Decision (Digital Twin evaluation, CD2F objective function, candidate normalization).
* **Phase 6 (D08):** Event & Runtime Backbone (Kafka topic topology, transactional outbox, consumer idempotency).
* **Phase 7 (D09):** Observability, Explainability & Desktop Console (decision trace, Tauri v2 HITL console, DecisionRecord archival).
* **Phase 8 (D10):** Evaluation & Benchmark Suite (B0-B7 ablation ladder, empirical model selection, statistical validation).
