# Deliverable D01 -- Enterprise World & Simulation Foundation

## Overview & Purpose

Deliverable D01 establishes the authoritative cyber-physical world model and discrete-event simulation foundation for the Supply Chain Cognitive Orchestration Framework (SCOF) V2 Enterprise platform. Replacing the procedural toy generator of V1 (which generated 5 suppliers and 2 warehouses), D01 establishes an industrial-scale reference world modeling a Tier-1 retail enterprise network across 30 unified business domains, 96 relational tables, 165 physical foreign keys, and 49,616 SKUs.

D01 guarantees that all downstream multi-agent deliberations (D03, D04), LangGraph orchestration loops (D05), CD2F consensus arbitration (D06), and empirical benchmarks (D10) reason over an authoritative, physically grounded, and cryptographically verifiable world model.

---

## Requirements Summary

- **ER-1.1 (30 Unified Business Domains)**: Synthesize and model complete enterprise lifecycle operations across 30 domains, including Corporate Structure, Merchandise Hierarchy, Sourcing, Procurement, Inventory, Network Logistics, Commerce, General Ledger Accounting, and Exogenous Disruptions.
- **ER-1.2 (Relational Referential Closure)**: Enforce 100% referential integrity across 96 relational tables and 165 physical foreign key constraints, with exact parity between PostgreSQL 16 and the local SQLite development harness (`datasets/scof_relational.db`).
- **ER-1.3 (Physical & Causal Invariant Enforcement)**: Enforce non-negotiable physical laws: conservation of mass and inventory, lead-time causality, warehouse throughput and cold-chain thermal capacity bounds, and balanced double-entry financial ledger accounting.
- **ER-1.4 (Tripartite State Isolation)**: Strictly implement the tripartite state isolation model ([ADR 002](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_tripartite_state_isolation_for_benchmark_integrity.md)), guaranteeing that simulation runs (Layer 3) execute in isolated sandboxes without contaminating the frozen reference baseline (Layer 1) or operational state (Layer 2).
- **ER-1.5 (Deterministic Provenance & Run Manifest)**: Record cryptographic SHA-256 hashes of all schema definitions, generator source files, and output tables in `run_manifest.json` with unique `run_id` tracking for 100% replayability.
- **ER-1.6 (Directed Generation DAG)**: Structure dataset creation into a 6-phase directed acyclic graph (DAG) respecting entity topological dependency orders.

---

## Prerequisites & Dependencies

- **Prerequisite Deliverables**: None. Deliverable D01 establishes the foundational world model for SCOF V2.
- **Required System Tools**: Python 3.11+, SQLite 3.40+, DuckDB 0.9+, PostgreSQL 16+ (optional for live staging).
- **Authoritative Datasets & Schemas**:
  - Relational Database Harness: [`datasets/scof_relational.db`](file:///d:/projects/SCOF_V1/SCOF/datasets/scof_relational.db)
  - Unified Schema DDL: [`scripts/schema_ddl.sql`](file:///d:/projects/SCOF_V1/SCOF/scripts/schema_ddl.sql)
  - Run Provenance Manifest: [`run_manifest.json`](file:///d:/projects/SCOF_V1/SCOF/run_manifest.json)
  - Operational Validation Audit: [`datasets/operational_validation_results.json`](file:///d:/projects/SCOF_V1/SCOF/datasets/operational_validation_results.json)

---

## Document Set in this Directory

1. **[`README.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/README.md)** (this document): Overview, requirements, prerequisites, document map, and acceptance criteria.
2. **[`implementation_plan.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/implementation_plan.md)**: Detailed technical implementation plan across the 6 generator phases, module layout, and verification strategy.
3. **[`design_decisions.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/design_decisions.md)**: Architectural design decisions covering tripartite state isolation, physical invariants, event-stepped simulation kernel, and bounded worker concurrency.
4. **[`schema_design.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/schema_design.md)**: Enterprise relational schema architecture across 30 domains, 96 tables, 165 physical foreign keys, audit columns, and indexing strategy.
5. **[`data_dictionary.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/data_dictionary.md)**: Complete field-by-field reference guide for the 96 enterprise tables and entity relationships.
6. **[`acceptance_evidence.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/acceptance_evidence.md)**: Empirical verification evidence, validation logs, table row counts, and audit certificates.
7. **[`walkthrough.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation/walkthrough.md)**: Complete step-by-step walkthrough for running the generation DAG, inspecting manifests, and executing automated validation suites.

---

## Module Structure

```text
generators/
    foundations/
        foundations_generator.py        # Calendar, fiscal periods, geography, currencies
    enterprise_core/
        enterprise_core_generator.py    # Legal entities, operating units, facilities, parties
    product/
        product_generator.py            # Merchandise hierarchy, 49.6K SKUs, UOM, pricing
    inventory/
        inventory_generator.py          # Multi-echelon stock levels, lots, serials, storage bins
    logistics/
        logistics_generator.py          # Transport lanes, carriers, freight rates, vehicles
    orders/
        orders_generator.py             # Purchase orders, lines, goods receipts, sales orders
    financial_ledger/
        financial_ledger_generator.py   # General ledger, chart of accounts, journal entries
    disruptions/
        disruptions_generator.py        # Exogenous shocks: weather, delays, asset downtime
    simulation_engine/
        simulation_kernel.py            # Event-stepped DES clock, queue manager, state masks
        physical_invariants.py          # Mass conservation, causality, capacity validators
    run_generation.py                   # Master DAG orchestrator and provenance sealer

datasets/
    scof_relational.db                  # Authoritative 96-table SQLite development database
    operational_validation_results.json # 6-Gate formal certification report
    relational_ingestion_audit.json     # 4.36M row ingestion audit log

scripts/
    schema_ddl.sql                      # Master PostgreSQL/SQLite relational schema DDL
    validate_enterprise_architecture.py # Automated 6-gate architectural validator
    load_postgresql_data.py             # Topological relational ingestion engine
```

---

## Standalone Acceptance Criteria ("Definition of Done")

1. **Schema & Referential Closure**: Master schema DDL generates all 96 tables and 165 foreign key links with zero syntax errors, verified on both SQLite and PostgreSQL 16.
2. **Deterministic Scale Target**: Generation DAG produces >= 4,000,000 relational rows and 49,616 SKUs with 100% deterministic reproducibility when seeded with `seed = 42`.
3. **Gate 1 (Referential Closure)**: 100% of foreign key references resolve cleanly to valid primary keys with 0 orphaned records across all 96 tables.
4. **Gate 2 (Inventory Conservation)**: Zero negative inventory balances exist across all facilities, and spoiled/expired stock is correctly written off.
5. **Gate 3 (Financial Equilibrium)**: 100% of journal entries satisfy double-entry accounting equilibrium: sum(Debits) = sum(Credits) across all fiscal periods.
6. **Gate 4 (Three-Way Match Audit)**: Purchase orders, goods receipts, and supplier invoices reconcile cleanly with zero phantom receipts.
7. **Gate 5 (Demand Conservation)**: Sales line quantities do not exceed observed store-level customer traffic or safety-stock constraints.
8. **Cryptographic Sealing**: Execution completes with `run_manifest.json` containing SHA-256 hashes of all generated tables and pipeline outputs.
