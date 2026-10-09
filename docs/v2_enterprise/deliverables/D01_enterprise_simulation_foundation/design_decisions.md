# Deliverable D01 -- Design Decisions: Enterprise World & Simulation Foundation

## 1. Context & Architectural Motivation

In SCOF V1, synthetic supply chain data generation was handled by procedural toy generators that produced 5 suppliers, 2 warehouses, and a handful of SKUs. While sufficient for early prototype wiring, this setup failed to represent enterprise-grade retail topology, realistic supplier-product sourcing networks, multi-echelon inventory conservation, or financial ledger integrity.

Deliverable D01 in SCOF V2 establishes the authoritative cyber-physical world model and discrete-event simulation foundation. It models a Tier-1 retail enterprise across 30 unified business domains, 96 relational tables, 165 physical foreign key constraints, 49,616 SKUs, and over 4.35 million operational records.

This document formalizes the architectural design decisions governing the design, state boundaries, physical invariants, simulation kernel, and concurrency control for Deliverable D01.

---

## 2. Key Design Decisions

### Decision 1: Tripartite State Architecture & Benchmark Isolation
- **Choice**: Enforce a strict three-layer state isolation model across the enterprise platform ([ADR 002](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_tripartite_state_isolation_for_benchmark_integrity.md)):
  - **Layer 1 (Frozen Ground Truth)**: Immutable physical datasets in [`datasets/`](file:///d:/projects/SCOF_V1/SCOF/datasets/) (`scof_relational.db`, Parquet archives, CSV masters) sealed with cryptographic SHA-256 hashes in [`run_manifest.json`](file:///d:/projects/SCOF_V1/SCOF/run_manifest.json).
  - **Layer 2 (Baseline Operational State)**: Clean Day-0 operational reference state loaded into PostgreSQL and the materialized read-only Neo4j graph.
  - **Layer 3 (Scenario Runtime State)**: Ephemeral copy-on-write execution context tagged with `scenario_id` and `sim_run_id`. All agent deliberations, disruptions, and counterfactual branches exist exclusively within Layer 3.
- **Rationale**: In multi-agent evaluations, executing operational interventions directly against live master data causes catastrophic state contamination across benchmark runs. Layer 3 copy-on-write guarantees 100% experiment reproducibility and prevents evaluation drift in D10.
- **Enforcement**: No simulation run or agent action may issue `UPDATE` or `DELETE` statements against Layer 1 or Layer 2 tables.

### Decision 2: Dual Storage Topology (SQLite Harness & PostgreSQL Target)
- **Choice**: Maintain strict schema and behavioral parity between the local SQLite development harness ([`datasets/scof_relational.db`](file:///d:/projects/SCOF_V1/SCOF/datasets/scof_relational.db)) and enterprise PostgreSQL 16 ([ADR 001](file:///d:/projects/SCOF_V1/SCOF/docs/adr/001_enterprise_knowledge_fabric_over_monolithic_generator.md)).
- **Rationale**: Enterprise PostgreSQL provides high-concurrency transactional guarantees, standard SQL extensions, and network accessibility. However, local developer productivity, unit testing, and continuous integration require a zero-setup, zero-daemon file-backed database that executes in milliseconds without external network or Docker overhead.
- **Implementation**: The schema DDL in [`scripts/schema_ddl.sql`](file:///d:/projects/SCOF_V1/SCOF/scripts/schema_ddl.sql) enforces cross-compatible SQL dialect rules, while [`scripts/load_postgresql_data.py`](file:///d:/projects/SCOF_V1/SCOF/scripts/load_postgresql_data.py) migrates SQLite tables to PostgreSQL using high-throughput batching.

### Decision 3: Event-Stepped Simulation Kernel over Fixed-Tick Daemons
- **Choice**: Implement an event-stepped Discrete Event Simulation (DES) kernel rather than a fixed-interval time-stepped daemon ([ADR 010](file:///d:/projects/SCOF_V1/SCOF/docs/adr/010_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)).
- **Rationale**: In fixed-interval simulations (e.g. 1-second or 1-minute ticks), the CPU wastes substantial compute cycles evaluating empty intervals when no state changes occur. Conversely, during supply chain disruptions, thousands of cascades may occur in a single instant, causing tick starvation.
- **Implementation**: The kernel maintains a priority queue of future discrete events ($t_{\text{event}}$, $\text{event\_type}$, $\text{payload}$). The simulation clock jumps directly to the timestamp of the next scheduled event, deterministically executing event state transitions without idle spinning.

### Decision 4: Deterministic Physical and Financial Invariant Enforcement
- **Choice**: Encode hard physical laws and financial ledger reconciliation as non-negotiable operational invariants ([ADR 008](file:///d:/projects/SCOF_V1/SCOF/docs/adr/008_operational_digital_twin_substrate_layer.md)):
  - **Conservation of Inventory & Mass**: Physical stock levels cannot drop below zero. Stock receipts must equal shipped quantities minus transit damage and spoilage.
  - **Lead-Time Physical Causality**: A shipment cannot arrive prior to dispatch time plus physical lane transit time ($t_{\text{arrival}} \ge t_{\text{dispatch}} + \tau_{\text{lane}}$).
  - **Physical Capacity Bounds**: Warehouse throughput and shelf-facing capacities are rigid physical boundaries. Temperature excursions trigger deterministic spoilage write-offs.
  - **Double-Entry Equilibrium**: Every simulated operational movement, damage write-off, or freight surge generates balancing debit and credit general ledger entries.
- **Rationale**: Cognitive AI agents tend to propose hallucinated operational fixes (such as instant teleportation of inventory or phantom stock creation) unless bound by rigid physical invariants enforced at the substrate layer.

### Decision 5: Minimalist Bounded Worker Concurrency Control
- **Choice**: Control concurrent simulation tasks and agent deliberation using a 4-tier Priority Queue (P0-P3) backed by a bounded worker thread pool ([ADR 011](file:///d:/projects/SCOF_V1/SCOF/docs/adr/011_minimalist_bounded_worker_concurrency.md)).
- **Rationale**: Unbounded concurrency in multi-agent simulations leads to thread thrashing, database connection pool exhaustion, and non-deterministic event orderings.
- **Priority Tiers**:
  - `P0 (Kernel Events)`: Physical simulation event transitions and clock advancement.
  - `P1 (State Telemetry)`: Real-time metric aggregation and invariant validation monitors.
  - `P2 (Agent Deliberation)`: LangGraph agent cognitive cycles and scenario branching.
  - `P3 (Batch Telemetry & Logs)`: Asynchronous audit logging and disk flushing.
- **Dispatching**: Strict FIFO ordering is maintained within each priority tier to preserve causal determinism.

### Decision 6: 30-Domain Unified Enterprise Relational Schema
- **Choice**: Model supply chain operations across 30 unified business domains with 96 normalized relational tables and 165 physical foreign key links, rather than a flattened key-value or document store.
- **Rationale**: Industrial retail enterprise operations require clear separation between legal corporate entities, merchandise hierarchies, multi-echelon facilities, procurement contracts, logistics fleets, inventory buffers, and general ledger accounts. Relational normalization guarantees referential integrity and eliminates update anomalies.

### Decision 7: Multi-Run Coexistence via Composite Foreign Keys
- **Choice**: Enforce composite run tracking using `sim_run_id` and `scenario_id` foreign keys on all operational log, trajectory, and event tables.
- **Rationale**: Truncating tables between simulation runs prevents historical comparison and comparative benchmarking in Deliverable D10. Keying operational records to `sim_run_id` allows multiple baseline runs and disruption experiments to coexist safely within the relational database.

### Decision 8: Deterministic Cryptographic Provenance Manifest
- **Choice**: Require the simulation pipeline to emit an immutable `run_manifest.json` recording SHA-256 hashes of all schema DDLs, generator code modules, input configuration files, and output table datasets.
- **Rationale**: Verifiable scientific reproducibility requires cryptographic proof that a given benchmark score was produced by an exact, unmodified codebase and dataset snapshot.

### Decision 9: Six-Gate Operational Validation Architecture
- **Choice**: Establish six automated validation gates that must execute and pass with zero defects before datasets can be promoted:
  1. *Gate 1 (Referential Closure)*: 100% of the 165 physical foreign keys checked for zero orphan rows.
  2. *Gate 2 (Inventory Conservation)*: Verification that zero negative inventory balances exist across all stock positions.
  3. *Gate 3 (Double-Entry Financial Equilibrium)*: Exact equality between total debits and total credits across general ledger entries ($0.00 imbalance).
  4. *Gate 4 (Three-Way Match Audit)*: Verification that matched purchase order lines, goods receipts, and vendor invoices reconcile within bounded tolerances.
  5. *Gate 5 (Demand Conservation)*: Zero mass-balance or latent-demand violations across all SKU-store pairings.
  6. *Gate 6 (Relational-Graph Parity)*: 100% reconciliation between relational master entities and Neo4j materialized graph nodes/edges.
