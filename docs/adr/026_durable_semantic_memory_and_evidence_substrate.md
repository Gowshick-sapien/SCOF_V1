# ADR 026: Durable Semantic-Memory and Evidence Substrate

* **Status**: Accepted (Amends ADR 003 and ADR 007)

---

## 1. Context and Problem Statement

In Deliverable D02 of the SCOF enterprise architecture, the knowledge layer must provide autonomous specialist agents (D03/D04), orchestration (D05), consensus (D06), and explainability (D07) with access to historical operational intelligence.

The enterprise substrate consists of:
1. **Relational System of Record (PostgreSQL):** 96 tables, 165 physical foreign keys, 4.36M transactional rows, and 18M+ simulation observations.
2. **Materialized Property Graph (Neo4j):** 3,728,199 nodes, 2,104,514 relationships, and 59 schema constraints.

Early proposals suggested vectorizing the entire relational database or providing flat, unversioned vector storage. This posed severe architectural risks:
* **Vector Pollution & Token Inefficiency:** Vectorizing structured rows (SKUs, PO lines, ledger journals) duplicates indexed data, inflates latency, and destroys relational referential integrity.
* **Identity Drift & Multi-Run Collisions:** Deriving document identity solely from content hash causes cross-scenario or multi-run collisions when distinct execution runs observe identical textual descriptions.
* **Model Revision Drift:** Changing embedding models or model versions corrupts vector space comparisons when stored vectors lack immutable model revision identities.
* **Concurrency Race Conditions:** Non-atomic document and embedding creation risks creating orphaned semantic documents.

---

## 2. Decision Drivers

* **Three-Substrate Knowledge Fabric:** Rigorous separation between relational operational truth ("What is true?"), topological graph structure ("How are things connected?"), and semantic memory ("What previous knowledge or evidence is similar?").
* **Non-Vectorization Invariant:** Strict restriction of vector embeddings to high-entropy contextual artifacts (scenarios, evidence claims, decision rationales, consensus explanations, capability cards).
* **Deterministic Identity & Provenance:** Stable document identity incorporating run and scenario provenance, decoupled from content hashing.
* **Model Immutability & Frozen Embedding Space:** Dedicated 384-dimensional cosine space with immutable model identifiers (`name@version`).
* **Safe Service Encapsulation:** Downstream agents interact exclusively through a typed service abstraction (`SemanticMemoryStore`), never issuing raw SQL or manipulating low-level vectors.

---

## 3. Considered Options

* **Option 1: Vectorize Relational Tables:** Convert tabular rows into text embeddings in a generic vector database. (Rejected: Violates single source of truth, destroys relational constraints, creates massive token bloat).
* **Option 2: Flat V1 Embeddings Table:** Single unversioned table storing content and vectors with HNSW indexing. (Rejected: Lacks model versioning, conflates document identity with content, prone to race conditions and orphan documents).
* **Option 3: Durable Multi-Tier Semantic Memory Substrate:** Three-tier schema separating model registry, semantic document identity/provenance, and versioned embeddings, accessed via `SemanticMemoryStore` with exact cosine search. (Accepted).

---

## 4. Decision Outcome

SCOF adopts **Option 3: Durable Multi-Tier Semantic Memory Substrate** as the authoritative semantic layer for Deliverable D02:

### 4.1 Data Architecture
1. **System of Record Precedence:** PostgreSQL is the sole authoritative transactional System of Record. SQLite serves strictly as a local development and smoke-test harness.
2. **Three-Tier Schema:**
   * `scof.embedding_model`: Stores registered embedding models with immutable identities (`model_id` formatted as `model_name@version`). Frozen to 384 dimensions and cosine distance for D02.
   * `scof.semantic_document`: Stores canonical semantic artifacts with stable composite identity (`SD-{type[:3]}-{hash[:12]}`) incorporating `run_id`, `scenario_id`, `source_entity_type`, `source_entity_id`, and `agent_id`.
   * `scof.semantic_embedding`: Stores `vector(384)` embeddings with `embedding_version`, `is_current` boolean flag, and `content_hash`.
3. **Canonical Text Normalization:** Text is normalized via Unicode NFC, newline canonicalization, and whitespace collapsing before SHA-256 hashing.
4. **Transactional Atomic Writes:** Document and embedding insertion execute within a single transaction with row-level locking (`FOR UPDATE`) to prevent concurrent version rollover races.
5. **Exact Search Baseline:** Exact nearest-neighbor cosine search (`<=>`) is the verified D02 baseline. Approximate index construction (HNSW) is deferred to future scale testing.

---

## 5. Architectural Invariants

* **Invariant 1 (Provenance Verification):** 100% of operational semantic documents must resolve to existing records in the relational database (`supplier_profile`, `facility`, `purchase_order`, `scenario`).
* **Invariant 2 (Strict Encapsulation):** Specialist agents (D03/D04) and orchestration kernels (D05) access semantic memory strictly via [SemanticMemoryStore](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py). Direct SQL and psycopg imports in agent code are prohibited.
* **Invariant 3 (Dimension Freeze):** Deliverable D02 supports exactly 384-dimensional embeddings. Model changes require identical dimensional projection or an explicit database schema migration.

---

## 6. Implementation References

* Schema DDL: [02_init_vector_schema.sql](file:///d:/projects/SCOF_V1/SCOF/infrastructure/database/postgres/02_init_vector_schema.sql)
* Configuration: [embedding.yaml](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/config/embedding.yaml)
* Service Implementation: [semantic_memory_store.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py)
* Verification Suite: [verify_pgvector_d2.py](file:///d:/projects/SCOF_V1/SCOF/scripts/verify_pgvector_d2.py)
* Test Suite: [test_semantic_memory.py](file:///d:/projects/SCOF_V1/SCOF/tests/test_semantic_memory.py)
