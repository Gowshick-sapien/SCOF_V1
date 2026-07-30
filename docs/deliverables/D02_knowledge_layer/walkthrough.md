# Deliverable D2 Walkthrough — Knowledge & Data Layer

## Summary of Accomplishments
Deliverable D2 builds the persistent Knowledge and Data Layer for SCOF before any specialist AI agents or coordinator services are implemented. It provides a structured graph and vector environment to query operational topology, multi-echelon supply chain relationships, and historical decision context. D2 delivers:

1. **Neo4j Graph Store Schema DDL (`infrastructure/database/neo4j/01_init_graph_schema.cypher`)**:
   - Schema migration tracking via `:SchemaVersion {id: 'schema_v2', version: '2.0.0'}`.
   - Unique constraints on `:Manufacturer(id)`, `:Supplier(id)`, `:Product(id)`, `:Warehouse(id)`, `:DistributionCenter(id)`, and `:Route(id)`.
   - Comprehensive performance indexes on all node primary keys, `:Supplier(reliability_profile)`, and `:Route(mode)`.

2. **PostgreSQL pgvector Schema DDL (`infrastructure/database/postgres/02_init_vector_schema.sql`)**:
   - Schema versioning table `scof.schema_version` (v2.0.0).
   - Expanded decision records table `scof.decision_records` storing `decision_type`, `recommendation`, `confidence`, `priority`, `impact_summary`, `created_by`, `simulation_tick`, `outcome`, and `status`.
   - Evidence snippets table `scof.evidence_snippets` linked to decision records.
   - Vector embeddings table `scof.embeddings` tracking embedding metadata (`embedding_model`, `embedding_version`, `embedding_dimension`) with an HNSW cosine similarity index (`idx_embeddings_hnsw`).

3. **Shared Knowledge Access Library (`shared/scof_shared/knowledge/`)**:
   - `Neo4jGraphClient` providing connection pooling, exponential retries, shortest path query helper, upstream supplier lineage, alternate supplier discovery, and route details.
   - `PgVectorClient` providing metadata-aware vector similarity search (`ORDER BY embedding <=> query_vector LIMIT K`), decision/evidence retrieval, and batch insertion.

4. **Modular Python ETL Service (`services/etl/src/`)**:
   - Modular architecture decoupled into Extract (`extract.py`), Transform (`transform.py`), Cypher Graph Loading (`load_graph.py`), Vector Store Loading (`load_vector.py`), Standalone Embedding Service (`embedding_service.py`), and Pipeline Orchestrator (`pipeline.py`).
   - Supports `--mode full` and `--mode incremental` execution flags.
   - High-performance Cypher `UNWIND ... MERGE ...` batch statements with explicit relationship edge properties (`lead_time_days`, `unit_cost`, `minimum_order_qty`, `is_preferred`, `contract_id`, `transit_days`, `risk_score`, `cost_delta_pct`).
   - High-performance Postgres `executemany()` vector batch operations.
   - Standalone `EmbeddingService` with deterministic seed hashing for reproducible vector testing.

5. **Health & Domain Invariant Verification Suite (`scripts/verify_d2.py` & `services/etl/tests/`)**:
   - `scripts/verify_d2.py` verifying database connectivity, Neo4j graph constraints/indexes, node/edge counts, domain invariants (every product has ≥1 supplier, every warehouse stores ≥1 product, every route connects valid facilities), Cypher traversals, pgvector table populated status, metadata-aware vector search, and ETL idempotency.
   - Unit and integration test suite (`test_extract_transform.py`, `test_graph_loader.py`, `test_vector_loader.py`, `test_embedding_service.py`, `test_end_to_end_etl.py`).

---

## Verification & Test Results

### 1. Pytest Suite Execution
Executed `pytest` across all ETL and shared knowledge package test suites:

```bash
python -m pytest services/etl/tests/
```

**Output**:
```
============================= test session starts =============================
platform win32 -- Python 3.12.2, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\SCOF
configfile: pyproject.toml
collected 7 items

services\etl\tests\test_embedding_service.py ..                          [ 28%]
services\etl\tests\test_end_to_end_etl.py .                              [ 42%]
services\etl\tests\test_extract_transform.py ..                          [ 71%]
services\etl\tests\test_graph_loader.py .                                [ 85%]
services\etl\tests\test_vector_loader.py .                               [100%]

============================== 7 passed in 1.90s ==============================
```

---

## Step-by-Step Execution & Manual Testing Guide

> [!NOTE]
> On Windows (CMD / PowerShell) without GNU `make` installed, use direct `python` commands shown under each step.

### Step 1: Start Infrastructure & Verify Health
Start the database and messaging infrastructure containers in detached mode:
```bash
docker compose up -d
```

Verify that PostgreSQL, Neo4j, Redis, and Kafka containers are running and healthy:
```bash
docker compose ps
```
Confirm PostgreSQL (port 5432) and Neo4j (7474/7687) containers are online.

### Step 2: Initialize Database Schemas & Versioning
Apply PostgreSQL vector schema DDL and versioning:
```cmd
:: Windows CMD / PowerShell:
type infrastructure\database\postgres\02_init_vector_schema.sql | docker exec -i scof-postgres psql -U scof -d scof

:: Linux / Bash:
docker exec -i scof-postgres psql -U scof -d scof < infrastructure/database/postgres/02_init_vector_schema.sql
```

Apply Neo4j graph schema constraints, indexes, and versioning:
```cmd
:: Windows CMD / PowerShell:
type infrastructure\database\neo4j\01_init_graph_schema.cypher | docker exec -i scof-neo4j cypher-shell -u neo4j -p changeme

:: Linux / Bash:
docker exec -i scof-neo4j cypher-shell -u neo4j -p changeme < infrastructure/database/neo4j/01_init_graph_schema.cypher
```

### Step 3: Run the Modular ETL Pipeline
Execute the 5-step Python ETL pipeline in `--mode full` or `--mode incremental`:
```cmd
:: Full ingestion mode:
python -m services.etl.src.main --mode full

:: Incremental update mode:
python -m services.etl.src.main --mode incremental
```

### Step 4: Run Automated Verification & Domain Invariant Checks
Execute the automated health and domain invariant verification script:
```cmd
:: On Windows CMD / PowerShell:
python scripts/verify_d2.py

:: On Linux / macOS / Git Bash:
make verify-d2
```

---

## Direct Database & Cypher Exploration Strategy

### 1. Neo4j Cypher Direct Queries
Connect to Neo4j Browser at `http://localhost:7474` (or via `cypher-shell`) and run:

```cypher
// Check node counts and schema version
MATCH (v:SchemaVersion) RETURN v.version;
MATCH (n) RETURN labels(n)[0] AS Label, count(*) AS Count;

// Inspect SUPPLIES edge properties
MATCH (s:Supplier)-[r:SUPPLIES]->(p:Product)
RETURN s.name AS Supplier, p.name AS Product, r.unit_cost AS UnitCost, r.lead_time_days AS LeadTime, r.is_preferred AS IsPreferred;

// Execute shortest path query
MATCH p=shortestPath((s:Supplier {id: 'sup-01'})-[*..6]-(w:Warehouse {id: 'wh-01'}))
RETURN p;
```

### 2. PostgreSQL Vector Direct Queries
Run direct SQL queries against the `scof` database by opening an interactive `psql` session in **CMD / PowerShell**:

```cmd
docker exec -it scof-postgres psql -U scof -d scof
```

Once inside the `scof=#` prompt, paste and execute SQL queries:

**Exit psql prompt**: Type `\q` and press Enter.

```sql
-- Check schema version
SELECT * FROM scof.schema_version;

-- Check decision records with expanded metadata
SELECT id, decision_type, recommendation, confidence, priority, created_by, outcome FROM scof.decision_records;

-- Check embeddings model metadata
SELECT id, entity_type, entity_id, embedding_model, embedding_version, embedding_dimension FROM scof.embeddings LIMIT 5;

-- Execute vector similarity search
SELECT id, entity_type, content_text, embedding_model, 1 - (embedding <=> '[0.01, 0.02, ...]'::vector) AS similarity_score
FROM scof.embeddings
WHERE entity_type = 'decision'
  AND embedding_model = 'all-MiniLM-L6-v2'
ORDER BY embedding <=> '[0.01, 0.02, ...]'::vector
LIMIT 3;
```
