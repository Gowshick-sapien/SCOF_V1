# Deliverable D01 Implementation Plan -- Enterprise World & Simulation Foundation

## Goal Description

Deliverable D01 constructs the enterprise world model and simulation foundation for SCOF V2. Moving away from isolated procedural generation, D01 establishes an authoritative cyber-physical reference environment spanning 30 unified business domains, 96 relational tables, and 49,616 SKUs.

The implementation is executed as a directed generation pipeline that validates entity dependencies, computes cryptographic hashes, enforces physical invariants, and exports the authoritative local SQLite harness and PostgreSQL ingestion scripts.

---

## Technical Architecture & Phasing Roadmap

The implementation is organized into six sequential generation phases:

```text
Phase 1: Foundations & Geography (Calendar, Countries, Currencies, Fiscal Periods)
   │
   ▼
Phase 2: Master Entities (Legal Entities, Facilities, Merchandise, 49.6K SKUs)
   │
   ▼
Phase 3: Sourcing & Logistics (Suppliers, Transport Lanes, Carriers, Asset Profiles)
   │
   ▼
Phase 4: Operational Transactions (POs, Goods Receipts, Invoices, Sales, Inventory Snapshots)
   │
   ▼
Phase 5: Financial Accounting (GL Accounts, Journal Entries, Balance Audits)
   │
   ▼
Phase 6: Exogenous Disruptions & Sealing (Weather, Transit Shocks, Manifest Hashing)
```

### Phase 1: Foundations & Master Dimensionality
- Define calendar dimensions (Day, Week, Month, Calendar Year, Fiscal Year, Fiscal Quarter, Fiscal Period).
- Model geographic hierarchies (Country, State/Province, District, City, Postal Area, Transport Zone).
- Establish ISO standard currency tables and unit-of-measure conversion matrices.

### Phase 2: Master & Structural Entities
- Model corporate organizational structure (Enterprise Group, Legal Entities, Operating Units).
- Establish physical facilities (Distribution Centers, Regional Warehouses, Retail Stores, Carrier Hubs).
- Build the 4-tier merchandise hierarchy (Department -> Category -> Subcategory -> Product Family).
- Generate 49,616 individual SKU records with physical attributes, packaging types, and storage temperature requirements.

### Phase 3: Sourcing & Network Logistics
- Model supplier organizations, tiered capability ratings, lead-time profiles, and compliance scores.
- Build multi-modal transport lanes (Road, Rail, Air, Ocean) with baseline transit times, cost matrices, and distance calculations.
- Register physical logistics assets (Trucks, Reefers, Chiller Units) with operational capacity limits.

### Phase 4: Operational Transactions & Physical Movement
- Generate purchase order contracts and PO item lines.
- Model multi-echelon inventory positions across DC buffers and retail store backrooms.
- Simulate point-of-sale customer transactions and e-commerce order fulfillment.
- Record goods receipts, cross-docking events, and delivery shipments.

### Phase 5: Financial General Ledger & Three-Way Matching
- Define standard Chart of Accounts (Assets, Liabilities, Equity, Revenue, Expense).
- Generate double-entry journal entries for every goods receipt, inventory write-off, and customer sale.
- Enforce automated three-way matching reconciliation across POs, receipts, and vendor invoices.

### Phase 6: Exogenous Disruptions & Provenance Sealing
- Model structured disruption events (Severe Weather, Port Closures, Supplier Delays, Asset Breakdowns, Demand Surges).
- Bind disruption events to target network entities with severity multipliers and temporal durations.
- Compute SHA-256 digests of all generated CSV/Parquet tables and compile `run_manifest.json`.

---

## Key Refinements Incorporated

1. **Tripartite State Isolation ([ADR 002](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_tripartite_state_isolation_for_benchmark_integrity.md))**:
   - Layer 1: Frozen Reference World (Parquet files and sealed seed data).
   - Layer 2: Baseline Operational Reality (PostgreSQL and SQLite tables).
   - Layer 3: Runtime Scenario Sandboxes (Ephemeral copy-on-write contexts).
2. **Physical & Causal Invariants**:
   - Mass conservation: Inventory cannot go negative; expired stock cannot be sold.
   - Lead-time causality: Shipments cannot arrive prior to transit duration.
   - Capacity bounds: Warehouse throughput cannot exceed physical cubic capacity.
3. **Event-Stepped DES Simulation Kernel ([ADR 010](file:///d:/projects/SCOF_V1/SCOF/docs/adr/010_event_stepped_simulation_kernel_over_fixed_tick_daemon.md))**:
   - Replaces continuous fixed-tick daemons with discrete-event priority queue dispatching, ensuring 100% replayability and sub-second simulation execution.
4. **Minimalist Bounded Worker Concurrency ([ADR 011](file:///d:/projects/SCOF_V1/SCOF/docs/adr/011_minimalist_bounded_worker_concurrency.md))**:
   - 4-tier Priority Queue (P0 System Critical -> P3 Speculative What-If) backed by bounded worker threads.
5. **Dual Database Harness**:
   - High-speed local SQLite database (`scof_relational.db`) for zero-daemon unit testing and development.
   - Production PostgreSQL 16 DDL for staging and deployment.

---

## Verification & Testing Strategy

- **Automated Validation Suite**: Executed via [`scripts/validate_enterprise_architecture.py`](file:///d:/projects/SCOF_V1/SCOF/scripts/validate_enterprise_architecture.py).
- **Relational Ingestion Verification**: Executed via [`scripts/load_postgresql_data.py`](file:///d:/projects/SCOF_V1/SCOF/scripts/load_postgresql_data.py), validating all 96 tables and 165 foreign keys.
- **Twin Service Invariant Suite**: Unit tests in [`tests/test_twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/tests/test_twin_service.py) verifying inventory decay, 3-way match, and financial ledger summaries.
