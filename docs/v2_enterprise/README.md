# SCOF Track 2: V2 Enterprise Cognitive Twin Architecture

## 1. Executive Summary & Vision

The **V2 Enterprise Cognitive Twin** marks the transformation of SCOF from an initial 5-supplier proof-of-concept into an **industrial-grade Cognitive Digital Twin** for complex retail and supply chain ecosystems.

While preserving the core CD²F consensus algorithms, A2A orchestration kernel, and desktop operations console proven in V1, V2 scales the underlying environment to the **SCOF Retail Enterprise Reference World**:
* **Scale:** 30 business domains, 96 relational tables, 165 physical foreign keys, 49,616 SKUs, 200 suppliers, 21 facilities (5 DCs, 16 stores), 35 transport lanes, and 18M demand rows.
* **Graph Topology:** 3,732,388 Neo4j nodes and 2,104,188 edges across 59 schema constraints.
* **Service Substrate:** The [`services/twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/services/twin_service.py) layer provides programmatic APIs for discrete disruption simulation, farm-to-store lineage tracing, three-way match reconciliation, and financial ledger equilibrium.
* **Architectural Blueprint:** Detailed in [`scof_v2_architecture_evolution.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/scof_v2_architecture_evolution.md).

---

## 2. Directory Structure (Track 2)

```
docs/v2_enterprise/
├── README.md                              # This master document
├── scof_v2_architecture_evolution.md      # Detailed V1-to-V2 transformation report
│
├── architecture/                          # Core Subsystem Architecture Specifications
│   ├── README.md                          # Subsystem matrix & interaction flow
│   ├── 01_digital_twin_service_architecture.md
│   ├── 02_cognitive_query_routing_and_resolution_pipeline.md
│   ├── 03_dynamic_capability_registry.md
│   ├── 04_minimalist_concurrency_and_worker_pool.md
│   ├── 05_state_isolation_and_evidence_fabric.md
│   └── 06_subsystem_boundaries_and_orchestration_contracts.md
│
├── dataset/                               # Authoritative Dataset Architecture & Specs
│   ├── SCOF_Enterprise_Dataset_Architecture_and_Implementation_Report.md
│   ├── SCOF_Dataset_Files_Big_Picture_Understanding_Document.md
│   ├── SCOF_Internal_Dataset_Architecture_Specification.md
│   ├── SCOF_Physical_Generation_DAG.md & .yaml
│   ├── SCOF_Validation_Report.md
│   ├── SCOF_Operational_Validation_Report.md
│   └── dataset_schema_report.md
│
├── ontology/                              # Enterprise Ontologies, ERD, & Graph Specs
│   ├── SCOF_Foundational_Ontology.md
│   ├── SCOF_Enterprise_Domain_and_Node_Registry.md
│   ├── SCOF_Enterprise_Relationship_Registry.md
│   ├── SCOF_Entity_Realization_Map.md
│   ├── SCOF_Enterprise_Lifecycle_Flows.md
│   ├── SCOF_Canonical_ERD.md
│   ├── SCOF_Neo4j_Graph_Specification.md
│   └── conceptual_models/
│
├── deliverables/                          # V2 Deliverable Evolution Blueprints (D1–D11)
│   ├── D01_enterprise_simulation_foundation.md
│   ├── D02_knowledge_fabric.md
│   ├── D03_demand_inventory_agents_v2.md
│   ├── D04_supplier_transport_agents_v2.md
│   ├── D05_orchestration_kernel_v2.md
│   ├── D06_cd2f_consensus_v2.md
│   ├── D07_observability_explainability_v2.md
│   ├── D08_api_event_bus_v2.md
│   ├── D09_desktop_console_v2.md
│   ├── D10_benchmarking_evaluation_v2.md
│   └── D11_post_mvp_extensions_v2.md
│
├── contracts/                             # Machine-Readable Interface Contracts
│   ├── twin_service_api_spec.md
│   ├── capability_registry_spec.md
│   ├── structured_claim_contract.md
│   ├── agent_card_spec.md
│   └── bounded_mcp_tools_spec.md
│
└── research/                              # Academic & Research Foundations
    ├── understanding_cognitive_twin_service.md
    ├── research_questions_v2.md
    └── benchmark_methodology.md
```


---

## 3. Key Architectural Pillars of V2

1. **Tripartite State Architecture:**
   * *Layer 1 (Frozen Ground Truth):* Immutable Parquet and CSV files in [`datasets/`](file:///d:/projects/SCOF_V1/SCOF/datasets/).
   * *Layer 2 (Baseline Operational State):* Clean Day-0 operational reference in PostgreSQL and Neo4j.
   * *Layer 3 (Scenario Runtime State):* Isolated, ephemeral copy-on-write contexts preventing cross-scenario contamination in benchmarks.
2. **Materialized Graph Projection with Bounded Query Contracts:**
   * Neo4j is strictly a unidirectional materialized projection from PostgreSQL.
   * Agents interact with the 3.73M-node graph exclusively through parameterized, depth-bounded MCP tools (`max_depth=3`) to guarantee sub-500ms SLAs.
3. **Decoupling Data Ontology from Multi-Agent Roster:**
   * The 30 business domains represent the **data ontology**, not 30 separate agents.
   * Four federated specialist agents (**Demand**, **Inventory**, **Supplier**, **Transportation**) consume multiple domains via MCP tools.
4. **Declarative Domain Binding Profiles:**
   * Domain Profiles bind runtime instances to operational subsets of the enterprise dataset:
     $$\text{Enterprise Dataset} + \text{Domain Binding Profile} = \text{SCOF Runtime World}$$
