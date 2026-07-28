# Deliverable D1 — Design Decisions

## 1. Context & Motivation
SCOF requires synthetic supply chain data to simulate operational conditions, test predictive agent algorithms (D3/D4), and validate consensus decision-making (D6) without depending on proprietary enterprise ERP data. The synthetic generator must be reproducible, profile-driven, and capable of generating both baseline normal operations and injectable disruption events.

---

## 2. Key Design Decisions

### Decision 1: Multi-Run Dataset Coexistence via `run_id` Foreign Keys
- **Choice**: All operational tables (`inventory_levels`, `purchase_orders`, `order_items`, `shipments`, `disruption_events`) are foreign-keyed to `simulation_runs.run_id`.
- **Rationale**: Truncating tables before every simulation run destroys historical datasets and makes multi-run benchmarking (comparing Run A vs Run B in D10) impossible. Keying by `run_id` permits multiple independent simulation runs to coexist safely within PostgreSQL.

### Decision 2: Profile Hashing (`profile_hash`) for Exact Reproducibility
- **Choice**: Compute a SHA-256 hash of all profile files (`topology.yaml` + `disruptions.yaml`) during pipeline execution and store it in `simulation_runs.profile_hash`.
- **Rationale**: If a user edits a YAML file without incrementing `profile_version`, the datasets generated will differ. The SHA-256 hash guarantees cryptographic proof of exact profile state during benchmark execution.

### Decision 3: Profile-Driven Generation vs. Hardcoded Generators
- **Choice**: The data generator will read entity topologies (`topology.yaml`) and disruption parameters (`disruptions.yaml`) directly from the active Domain Profile at runtime.
- **Rationale**: Reading from `profiles/mvp-electronics/` ensures that switching to a new supply chain profile requires zero code changes in the simulation generator.
- **Implementation**: The `services/simulation/src/entity_generator.py` module uses `scof-shared.profile.loader` and `validators.py` to parse and validate profile YAML files into typed Pydantic models before executing generation logic.

### Decision 4: Canonical Entity Identifier Convention
- **Choice**: Enforce explicit prefix conventions for canonical IDs across master and operational tables:
  - Manufacturer: `mfg-01`
  - Supplier: `sup-01`
  - Warehouse: `wh-01`
  - Distribution Center: `dc-01`
  - Product: `prod-101`
  - Route: `route-sup01-wh01`
  - Run: `run-20260728-001`
  - Scenario: `scen-01`
  - Purchase Order: `po-00001`
  - Shipment: `ship-00001`
  - Disruption Event: `disrupt-00001`
- **Rationale**: Standardized prefix conventions allow Neo4j ETL (D2), Kafka events (D5), and frontend UI (D9) to parse entity types from IDs unambiguously.

### Decision 5: Polymorphic Route Modeling
- **Choice**: Store routes using `origin_type`, `origin_id`, `destination_type`, `destination_id` rather than raw IDs alone.
- **Rationale**: Origin can be supplier, warehouse, or manufacturer; destination can be warehouse or distribution center. Storing explicit types simplifies graph node/edge creation during D2 Neo4j ETL pipelines.

### Decision 6: Supplier-Product Sourcing Junction Table (`supplier_products`)
- **Choice**: Explicitly model multi-sourcing relationships using a `supplier_products` junction table with fields for `is_preferred_supplier`, `unit_cost`, `minimum_order_qty`, and `lead_time_override_days`.
- **Rationale**: Single-sourcing products directly to a manufacturer prevents agents from reasoning over supplier diversification, cost-vs-delay trade-offs, and alternate vendor selection during disruptions.

### Decision 7: Centralized Configuration and Enumerations
- **Choice**: Use `services/simulation/src/config.py` for environment settings (with `HISTORY_DAYS` as single source of truth) and `services/simulation/src/constants.py` for status and transport mode enumerations.
- **Rationale**: Prevents magic strings, duplicate constants, and scattered `os.getenv` calls across generators.

### Decision 8: Structured Generator Execution Phases
- **Choice**: Structure simulation execution into explicit sequential pipeline phases:
  - `Phase 1`: Load Profile
  - `Phase 2`: Validate Topology
  - `Phase 3`: Register Simulation Run & Profile Hash
  - `Phase 4`: Generate & Persist Master Data
  - `Phase 5`: Generate & Persist Transactions
  - `Phase 6`: Generate & Persist Disruptions
  - `Phase 7`: Export Generation Manifest (`generation_manifest.json`)
  - `Phase 8`: Execute Automated Verification Check
- **Rationale**: Clear pipeline phase separation simplifies debugging, error recovery, and performance tracking.

### Decision 9: Data Generation Manifest Output (`generation_manifest.json`)
- **Choice**: Produce a `generation_manifest.json` file in `services/simulation/` after execution containing run ID, seed, profile metadata, SHA-256 hash, execution time, and row counts.
- **Rationale**: Provides an immediate machine-readable summary of simulation output for automated CI checks and developer inspection.

### Decision 10: Automated Health Verification Script
- **Choice**: Provide `scripts/verify_d1.py` and `make verify-d1` to verify container health, PostgreSQL `pgvector` extension installation, `supplier_products` integrity, polymorphic routes, `run_id` foreign keys, and non-zero counts automatically.
