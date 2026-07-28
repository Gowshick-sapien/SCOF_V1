# Deliverable D1 — Simulation Environment & Synthetic Data Foundation

## Overview & Purpose
Deliverable D1 establishes a self-contained, reproducible synthetic supply chain world and Docker infrastructure before any AI agents or API services are deployed. It ensures that SCOF's data layer can generate and store realistic supply chain operations (manufacturers, suppliers, supplier-product sourcing mappings, warehouses, products, orders, inventory logs, polymorphic route shipments, disruption events, and simulation/scenario metadata) driven entirely by the active Domain Profile, with run-keyed isolation permitting multiple datasets to coexist.

---

## Requirements Summary (from SRS)
- **FR-1.1**: Provide a Docker Compose configuration provisioning PostgreSQL (+ pgvector extension), Redis, Kafka, and Neo4j as standalone containers.
- **FR-1.2**: Generate synthetic entities for 1 manufacturer, 3–5 products, 5 suppliers (with varying reliability profiles), supplier-product sourcing links, 2 warehouses, 1 distribution center, and a polymorphic multi-route transport network.
- **FR-1.3**: Provide a disruption event generator supporting: supplier delay, transport failure, demand spike, and adverse weather, each parameterized by severity, duration, and timing, linked to scenario metadata.
- **FR-1.4**: Ensure all generated historical data is queryable directly from PostgreSQL by `run_id`, independent of any agent or API code.
- **FR-1.5**: Read entity definitions, relationship structures, and disruption parameters dynamically from the active Domain Profile (`topology.yaml` and `disruptions.yaml`).

---

## Prerequisites & Dependencies
- **Prerequisite Deliverables**: None (D1 is the foundation deliverable).
- **Required System Tools**: Docker (v24+), Docker Compose (v2.20+), Python 3.11+.
- **Required Domain Profile Files**:
  - [`profiles/mvp-electronics/topology.yaml`](../../../profiles/mvp-electronics/topology.yaml)
  - [`profiles/mvp-electronics/disruptions.yaml`](../../../profiles/mvp-electronics/disruptions.yaml)

---

## Document Set in this Directory
1. **[`README.md`](./README.md)** (this document): Overview, requirements, prerequisites, roadmap, and acceptance criteria.
2. **[`implementation_plan.md`](./implementation_plan.md)**: Detailed step-by-step technical implementation plan and verification strategy for Deliverable D1.
3. **[`design_decisions.md`](./design_decisions.md)**: Architectural design decisions for run-keyed dataset coexistence, SHA-256 profile hashing, canonical ID conventions, supplier sourcing junctions, polymorphic routes, metadata tracking, and verification automation.
4. **[`schema_design.md`](./schema_design.md)**: PostgreSQL relational table schemas, primary/foreign keys, indexes, and constraints.
5. **[`data_dictionary.md`](./data_dictionary.md)**: Complete field-by-field reference guide for all generated database tables.
6. **[`acceptance_evidence.md`](./acceptance_evidence.md)**: Empirical test logs, SQL query results, and verification evidence (populated upon implementation completion).

---

## Module Structure

```
infrastructure/
    docker-compose.yml
    database/
        postgres/
            01_init_schema.sql          # Includes pgvector, run_id FKs, supplier_products, routes, metadata

shared/
    scof_shared/
        profile/
            loader.py                   # Loads profile YAML files
            validators.py               # Validates profile topology integrity

services/
    simulation/
        src/
            config.py                   # Centralized env, seed & HISTORY_DAYS settings
            constants.py                # Status and transport enums
            entity_generator.py         # Generates topology entities & sourcing links
            order_generator.py          # Generates historical orders & inventory
            disruption_generator.py     # Generates scenario disruption events
            db_writer.py                # Batch SQL writer with run_id foreign keys
            main.py                     # 8-Phase execution pipeline CLI entry point

        tests/
            test_profile_loader.py       # Profile validation unit tests
            test_entity_generator.py    # Entity generator unit tests
            test_disruption_generator.py# Disruption generator unit tests
            test_db_writer.py           # Database writer integration tests
            test_end_to_end.py          # End-to-end simulation & FK integrity test

scripts/
    verify_d1.py                        # Health verification script for D1 (docker, tables, pgvector, FKs)
```

---

## Standalone Acceptance Criteria ("Definition of Done")
1. Running `docker compose up -d` successfully spins up healthy PostgreSQL (with `vector` extension), Neo4j, Redis, and Kafka containers.
2. Executing `python -m src.main` within `services/simulation/` reads the active Domain Profile, computes SHA-256 `profile_hash`, populates PostgreSQL with historical operational data keyed by `run_id`, writes `generation_manifest.json`, and records execution statistics.
3. Running `python scripts/verify_d1.py` or `make verify-d1` passes 100% of automated checks:
   - PostgreSQL `vector` extension is installed.
   - `supplier_products` links exist and pass FK integrity.
   - Polymorphic routes have valid origin/destination types.
   - All operational tables (`inventory_levels`, `purchase_orders`, `shipments`, `disruption_events`) reference a valid `run_id`.
   - Multiple simulation runs coexist without truncating existing data.
4. Executing automated test suite `pytest services/simulation/tests/` passes 100%.
