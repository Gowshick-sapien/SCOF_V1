# Decision Persistence Design

## Objective
Establish a reliable, idempotent, and semantically searchable system of record for decisions produced by the CD²F engine, ensuring that no decision is silently lost and every decision retains its complete provenance.

## 1. Reusing the D2 Knowledge Layer
To prevent schema divergence and redundant infrastructure, D7 explicitly reuses the `scof` database established in D2.
- **Vectors**: Instead of introducing a new embedding specification (e.g., `vector(1536)`), D7 reuses the `scof.embeddings` standard (384-dimensional `all-MiniLM-L6-v2`) for semantic search of decision recommendations.
- **Migrations**: `02_observability_schema.sql` extends the existing `scof.decision_records` table and updates `scof.schema_version`, rather than acting as a standalone bootstrap.

## 2. Provenance Chain
The persistence contract guarantees that the lineage of a decision is fully reconstructible. The schema mandates:
- `DecisionRecord` → `ConsensusBundle` (`consensus_bundle_id`) → `ClaimBundle` (`source_bundle_id`)
- **Foreign Keys**: `scenario_id` must maintain a strict relational link to `scof.scenarios(scenario_id)`.

## 3. The Failure Contract (Synchronous Bounded Persistence)
The system of record cannot rely on fire-and-forget delivery.
- **Delivery**: The Orchestrator (D5) synchronously POSTs the decision to D7.
- **Idempotency**: D7 enforces `decision_id` as a `PRIMARY KEY`. Retries from D5 will not create duplicate history.
- **Failure**: If D7 is unavailable after bounded retries, D5 will explicitly fail the orchestration flow. It will *not* return a "successful" decision that was lost from the audit trail.
