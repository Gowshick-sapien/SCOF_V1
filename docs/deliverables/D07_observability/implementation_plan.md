# Deliverable D7 Implementation Plan -- Observability & Explainability Backend

## Goal Description
Deliverable D7 provides the Observability and Explainability Backend for SCOF. It makes every agent turn and consensus decision inspectable and replayable. D7 acts as the system of record for all decisions made by the CD²F engine, persisting the full reasoning trails, meeting logs, and judge calibration metrics so they can be queried by the Frontend (D9) via the Backend API (D8). 

It accomplishes three primary requirements from the SRS:
- **FR-7.1**: LangSmith tracing integration across the D5 orchestration graph.
- **FR-7.2**: Full reasoning trail persistence in Postgres/pgvector supporting replay.
- **FR-7.3**: Judge calibration metrics logging and temporal querying.

## Proposed Changes

### 1. Database Infrastructure (Reusing D2 Architecture)
#### [NEW] [02_observability_schema.sql](../../../infrastructure/database/postgres/02_observability_schema.sql)
- Versioned, idempotent raw SQL script that updates `scof.schema_version` and extends the Postgres database established in D2. 
- **Migration Execution**: This script is executed as a versioned migration against the existing `scof` database (e.g., via `make migrate`). The Docker initialization mounting is strictly for clean-environment bootstraps.
  - **Extend `scof.decision_records`**: Add columns for full provenance tracking (`consensus_bundle_id`, `source_bundle_id`, `trace_id`), `wcs`, `escalation_tier`, `decision_method`, and a `JSONB` column to store the complete `reasoning_trail` and `meeting_log_entries`. Enforce `decision_id` as `PRIMARY KEY` (UNIQUE constraint) to guarantee idempotency.
  - **Foreign Key Constraints**: Ensure `scenario_id` has a real relational link referencing `scof.scenarios(scenario_id)`.
  - **Calibration Metrics**: Add `scof.calibration_metrics` table to store temporal records of the CD²F judge calibration runs. Persists the complete `CalibrationReport` as a structured `JSONB` payload (to preserve exact match rates, confusion matrices, and warnings), alongside indexed headline metrics (`recommendation_kappa`, `escalation_tier_kappa`, `timestamp`).

### 2. Reliable Decision Persistence & Orchestrator Integration
#### [MODIFY] [orchestrator.py](../../../services/coordinator/src/orchestrator.py)
- Modify the Coordinator (D5) to post the generated `DecisionRecord` synchronously to the D7 service with a bounded timeout.
- **Persistence Failure Contract**: D7 is the system of record. If D7 persistence fails, D5 will perform bounded retries (using `decision_id` as an idempotency key). If all retries fail, D5 will explicitly bubble up a persistence failure error rather than silently returning a "successful" decision that was lost from the audit trail.

### 3. LangSmith Tracing Implementation (FR-7.1)
#### [NEW] [tracing.py](../../../shared/scof_shared/observability/tracing.py)
- Provides standard LangSmith initialization utilities and callbacks for the LangGraph orchestrator.
#### [MODIFY] [orchestrator.py](../../../services/coordinator/src/orchestrator.py)
- Explicitly configure LangSmith tracing on the compiled LangGraph execution.
- Ensure strict propagation of the correlation lineage (tags) throughout the execution hierarchy: `trace_id`, `scenario_id`, `bundle_id`, `profile_version`, `agent_id`, and `decision_id`.
- Ensure nodes within the graph are tagged appropriately for granular span analysis.

### 4. Observability Microservice
#### [NEW] [models.py](../../../services/observability/src/models.py)
- Pydantic models mapping to the database schemas for HTTP request/response validation.

#### [NEW] [decision_repo.py](../../../services/observability/src/decision_repo.py)
- Provides async CRUD operations for saving `DecisionRecord` objects to Postgres (idempotently) and retrieving them by `decision_id` or `scenario_id`.
- The persistence contract explicitly preserves the D6 provenance chain: `DecisionRecord` → `ConsensusBundle` → `ClaimBundle` → `scenario/profile`.
- Implements semantic similarity search over the `final_recommendation` using D2's existing embedding architecture (384-dimensional `scof.embeddings`).

#### [NEW] [embedding_client.py](../../../services/observability/src/embedding_client.py)
- Reuses the existing D2 standalone embedding service and metadata-aware vector client (`all-MiniLM-L6-v2`, 384 dimensions) to generate embeddings for semantic search, rather than inventing embedding generation locally.

#### [NEW] [calibration_repo.py](../../../services/observability/src/calibration_repo.py)
- Provides async CRUD operations for inserting and retrieving historical judge calibration metrics, reading from and writing to the `JSONB` representation of the `CalibrationReport`.

#### [NEW] [main.py](../../../services/observability/src/main.py)
- A FastAPI microservice (port `8030`) exposing the repository functions over HTTP:
  - `POST /decisions` - Ingest a new DecisionRecord (Idempotent).
  - `GET /decisions/{decision_id}` - Fetch decision provenance and reasoning trail for replay.
  - `GET /scenarios/{scenario_id}/decisions` - Fetch all decisions for a given scenario.
  - `GET /decisions/search` - Semantic search for similar past decisions (utilizing D2 embedding pipeline).
  - `POST /calibration` - Ingest complete calibration report.
  - `GET /calibration/history` - Retrieve calibration scores over time.

#### [NEW] [Dockerfile](../../../services/observability/Dockerfile)
- Standard lightweight Python 3.11/3.12 Dockerfile to run the FastAPI service.

#### [MODIFY] [docker-compose.yml](../../../docker-compose.yml)
- Mount the new `02_observability_schema.sql` into the `postgres` container initialization folder.
- Add the `observability-backend` service running on port `8030`.

### 5. Verification
#### [NEW] [verify_d7.py](../../../scripts/verify_d7.py)
- Automated verification script.
#### [MODIFY] [Makefile](../../../Makefile)
- Add `verify-d7` target.

## Verification Plan

### Automated Tests
- `python scripts/verify_d7.py` will execute the crucial acceptance test: **Verify Correlation Lineage**.
  - It will trace one real D5 → D6 execution, producing a traceable D7 record.
  - It will assert that the lineage is perfectly intact: `scenario_id` → `trace_id` → `bundle_id` → `consensus_bundle_id` → `decision_id` → LangSmith trace/run.
  - It will query the D7 persisted record and verify that the reasoning trail matches the D6 output exactly (preserving provenance).
  - It will insert complete calibration metrics (`JSONB`) and retrieve them.
  - It will perform an end-to-end vector search on a mock recommendation string to ensure the integration with D2's embedding pipeline and pgvector index functions correctly.
