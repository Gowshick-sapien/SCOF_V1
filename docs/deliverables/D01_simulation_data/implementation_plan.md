# Deliverable D1 Implementation Plan — Simulation Environment & Synthetic Data Foundation

## Goal Description
Deliverable D1 builds a self-contained, profile-driven synthetic supply chain simulation environment and containerized infrastructure before any AI agents or backend services are implemented. It implements:
1. Docker Compose setup for PostgreSQL (+ pgvector), Neo4j, Redis, and Kafka.
2. PostgreSQL DDL schema (`01_init_schema.sql`) modeling topology entities, supplier-product sourcing links, polymorphic routes, historical inventory logs, orders, shipments, disruption events, and simulation/scenario metadata — with `run_id` foreign keys on all operational tables enabling multi-run dataset coexistence.
3. A profile-driven Python simulation service (`services/simulation/`) that reads entity topologies (`topology.yaml`) and disruption parameters (`disruptions.yaml`) from `profiles/mvp-electronics/`, validates topology integrity, computes SHA-256 `profile_hash`, executes 8 sequential generator phases, logs execution statistics, writes `generation_manifest.json`, and populates PostgreSQL.
4. An automated health verification script (`scripts/verify_d1.py`) callable via `make verify-d1`.

---

## Prerequisites Check

> [!NOTE]
> - **Prerequisite Deliverables**: None. Deliverable D1 is the foundation step.
> - **Domain Profile**: [`profiles/mvp-electronics/`](../../../profiles/mvp-electronics/) is complete and ready to be loaded by D1 scripts.
> - **Repository Structure**: Monorepo scaffolding, `.env.example`, `pyproject.toml`, `Makefile`, and `docs/deliverables/D01_simulation_data/` documentation are established.

---

## User Review Required & Final Architectural Refinements Incorporated

> [!IMPORTANT]
> **Key Refinements Incorporated for D1**:
> 1. **Multi-Run Coexistence (`run_id` FK)**: Added `run_id` foreign key to `inventory_levels`, `purchase_orders`, `order_items`, `shipments`, and `disruption_events`. Multiple simulation runs (e.g. Run 17 vs Run 24) can coexist in PostgreSQL without table truncations.
> 2. **Cryptographic Profile Hashing (`profile_hash`)**: Computes SHA-256 hash of profile YAML files and records it in `simulation_runs.profile_hash` to guarantee exact experiment reproducibility.
> 3. **Generation Statistics & Manifest**: Records entity/order/shipment/inventory row counts and execution time in `simulation_runs` and exports `generation_manifest.json`.
> 4. **Canonical Entity ID Strategy**: Standardizes prefix conventions (`mfg-01`, `sup-01`, `prod-101`, `wh-01`, `dc-01`, `route-sup01-wh01`, `run-20260728-001`, `scen-01`, `po-00001`, `ship-00001`, `disrupt-00001`).
> 5. **Audit Columns**: Standardized `created_at` and `updated_at` timestamps across all tables.
> 6. **Single Source `HISTORY_DAYS`**: Centralized in `config.py` sourced from `.env` (default `180`).
> 7. **8 Structured Generator Phases**: Executed sequentially in `main.py`: Load -> Validate -> Register Run/Hash -> Master Entities -> Transactions -> Disruptions -> Persist & Manifest -> Verify.
> 8. **Automated Health Script (`scripts/verify_d1.py`)**: Checks container health, `vector` extension installation, `supplier_products` integrity, polymorphic route types, `run_id` foreign keys, and non-zero table counts (`make verify-d1`).

---

## Open Questions

> [!NOTE]
> None. All 10 architectural refinements are fully specified and ready for implementation.

---

## Proposed Changes

### Infrastructure (`infrastructure/`)

#### [NEW] [docker-compose.yml](../../../docker-compose.yml)
- Docker Compose configuration mounting `./infrastructure/database/postgres/01_init_schema.sql` into Postgres initialization, exposing ports 5432 (Postgres), 7474/7687 (Neo4j), 6379 (Redis), and 9092 (Kafka).

#### [NEW] [01_init_schema.sql](../../../infrastructure/database/postgres/01_init_schema.sql)
- PostgreSQL DDL script creating `scof` schema, `vector` extension, and tables: `simulation_runs` (with `profile_hash` & stats), `scenarios`, `manufacturers`, `products`, `suppliers`, `supplier_products`, `warehouses`, `distribution_centers`, `routes` (polymorphic), `inventory_levels` (run-keyed), `purchase_orders` (run-keyed), `order_items`, `shipments` (run-keyed), `disruption_events` (run-keyed), with audit columns and indexes.

---

### Shared Library (`shared/`)

#### [NEW] [pyproject.toml](../../../shared/pyproject.toml)
- Package specification for `scof-shared` library.

#### [NEW] [loader.py](../../../shared/scof_shared/profile/loader.py)
- Domain Profile YAML loader, Pydantic validator, and SHA-256 `profile_hash` computer.

#### [NEW] [validators.py](../../../shared/scof_shared/profile/validators.py)
- Integrity validator checking for duplicate entity IDs, missing entity references, and invalid route links.

---

### Simulation Service (`services/simulation/`)

#### [NEW] [pyproject.toml](../../../services/simulation/pyproject.toml)
- Dependency manifest: `faker`, `numpy`, `pandas`, `psycopg[binary]`, `pydantic`, `scof-shared`.

#### [NEW] [Dockerfile](../../../services/simulation/Dockerfile)
- Lightweight `python:3.11-slim` container build definition.

#### [NEW] [config.py](../../../services/simulation/src/config.py)
- Centralized configuration management for environment variables, database URLs, random seed, `HISTORY_DAYS`, and profile paths.

#### [NEW] [constants.py](../../../services/simulation/src/constants.py)
- Canonical ID prefixes, status enumerations (`OrderStatus`, `ShipmentStatus`, `DisruptionStatus`), and transport mode constants.

#### [NEW] [entity_generator.py](../../../services/simulation/src/entity_generator.py)
- Reads `topology.yaml` to instantiate manufacturers, products, suppliers, `supplier_products` sourcing links, warehouses, distribution centers, and polymorphic routes using canonical ID prefixes.

#### [NEW] [order_generator.py](../../../services/simulation/src/order_generator.py)
- Generates historical daily purchase orders, item lines, shipments, and inventory stock histories keyed by `run_id`.

#### [NEW] [disruption_generator.py](../../../services/simulation/src/disruption_generator.py)
- Reads `disruptions.yaml` model to produce parameterized disruption events linked to `run_id` and scenario metadata.

#### [NEW] [db_writer.py](../../../services/simulation/src/db_writer.py)
- Batch-inserts generated run metadata, scenarios, entities, inventory logs, orders, shipments, and disruption data into PostgreSQL using `psycopg3` transaction blocks.

#### [NEW] [main.py](../../../services/simulation/src/main.py)
- CLI entry point executing 8 sequential pipeline phases, exporting `generation_manifest.json`, and running automated health checks.

---

### Scripts & Verification (`scripts/`)

#### [NEW] [verify_d1.py](../../../scripts/verify_d1.py)
- Health check script checking container status, `vector` extension installation, table row counts, `run_id` foreign key integrity, `supplier_products` integrity, polymorphic route types, and scenario references.

---

### Tests (`services/simulation/tests/`)

#### [NEW] [test_profile_loader.py](../../../services/simulation/tests/test_profile_loader.py)
- Unit tests verifying profile validation rules, hash computation, and error catching for invalid YAML topologies.

#### [NEW] [test_entity_generator.py](../../../services/simulation/tests/test_entity_generator.py)
- Unit tests verifying profile entity parsing, `supplier_products` sourcing mapping, canonical ID prefixes, and polymorphic route formatting.

#### [NEW] [test_disruption_generator.py](../../../services/simulation/tests/test_disruption_generator.py)
- Unit tests verifying disruption event generation from profile definitions.

#### [NEW] [test_db_writer.py](../../../services/simulation/tests/test_db_writer.py)
- Integration test checking batch insert SQL execution and `run_id` FK integrity against Postgres.

#### [NEW] [test_end_to_end.py](../../../services/simulation/tests/test_end_to_end.py)
- End-to-end integration test verifying full generation pipeline, multi-run coexistence, table row counts, and relational foreign key integrity.

---

## Verification Plan

### Automated Tests
1. **Unit & Integration Test Suite**:
   ```bash
   pytest services/simulation/tests/
   ```
2. **Data Generation Pipeline Execution**:
   ```bash
   python -m services.simulation.src.main
   ```
3. **Automated Health Verification Script**:
   ```bash
   make verify-d1
   ```
   or
   ```bash
   python scripts/verify_d1.py
   ```

### Manual Verification
1. **Container & Extension Health**:
   ```bash
   docker compose up -d
   docker compose ps
   ```
2. **Direct SQL Query Verification**:
   Query Postgres directly to verify table counts, `run_id` isolation, and relational integrity:
   ```sql
   SELECT extname FROM pg_extension WHERE extname = 'vector';
   SELECT run_id, profile_name, profile_hash, execution_time_ms FROM scof.simulation_runs;
   SELECT count(*) FROM scof.supplier_products;
   SELECT count(*) FROM scof.routes WHERE origin_type = 'supplier' AND destination_type = 'warehouse';
   SELECT run_id, count(*) FROM scof.inventory_levels GROUP BY run_id;
   SELECT run_id, count(*) FROM scof.disruption_events GROUP BY run_id;
   ```
