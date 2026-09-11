# ADR 003: Vector Database Selection — pgvector vs. Dedicated Vector DBs (Pinecone, Weaviate, Qdrant)

---

## 1. Context and Problem Statement

SCOF requires long-term semantic memory to support Retrieval-Augmented Generation (RAG) and historical case-based reasoning. When a disruption occurs, the system must search through past disruption records, agent debate transcripts, and mitigation outcomes to surface similar historical cases and their realized efficacy.

This requires generating 384-dimensional dense vector embeddings (using `sentence-transformers/all-MiniLM-L6-v2`) and performing cosine similarity indexing at sub-second query latency. The critical architectural decision was whether to deploy a dedicated vector database (such as Pinecone, Weaviate, or Qdrant) or to utilize the `pgvector` extension inside the primary PostgreSQL relational database.

---

## 2. Decision Drivers

* **Transactional ACID Consistency**: Relational decision records (`scof.decision_records`) and their corresponding vector embeddings (`scof.embeddings`) must be inserted atomically in a single transaction.
* **Operational Simplicity**: Avoid managing and monitoring separate database containers, network ports, and sync daemons.
* **Hybrid Relational-Vector Queries**: Ability to filter semantic searches by structured metadata (e.g. `disruption_category = 'SUPPLIER_DELAY'` AND `severity >= 0.70` ORDER BY cosine distance).
* **Local, Air-Gapped Feasibility**: Zero external SaaS dependencies; fully functional in a localized Docker Compose environment.

---

## 3. Considered Options

* **Option 1: Pinecone / SaaS Vector DBs**: Hosted cloud vector database.
* **Option 2: Qdrant / Weaviate**: Standalone open-source specialized vector database container.
* **Option 3: PostgreSQL with pgvector**: Open-source vector similarity extension running inside PostgreSQL 16.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — PostgreSQL with pgvector**

### Rationale:
1. **Elimination of Dual-Write Inconsistency**:
   * Storing structured decision metadata in PostgreSQL while pushing embeddings to an external vector DB introduces the dual-write problem: if the vector database insert fails or lags, the systems drift out of sync, requiring distributed two-phase commits or background reconciliation workers.
   * `pgvector` allows an insert into `scof.decision_records` and `scof.embeddings` within a single atomic PostgreSQL transaction block.
2. **Native SQL Filtering & Joins**:
   * Operators frequently need to query: *"Find historical mitigations for key component shortages where the realized fill rate was above 90%."* In PostgreSQL, this is a single SQL query joining `decision_records` and `embeddings` with standard `WHERE` clauses and `<=>` cosine distance operators.
3. **Container Consolidation**:
   * Running `pgvector/pgvector:pg16` satisfies both relational storage (D7 observability, D1 simulation tables) and vector storage (D2 knowledge layer) in a single well-understood container.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Atomic ACID transactions across relational metadata and vector embeddings.
* Simplified backup and disaster recovery using standard `pg_dump`.
* Fast approximate nearest neighbor indexing via HNSW (`CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`).
* Zero cloud subscription costs or external network dependencies.

### Negative Consequences / Trade-offs:
* Extremely large vector scale ($> 100\text{M}$ vectors) requires careful PostgreSQL memory tuning (`shared_buffers`, `maintenance_work_mem`), though far exceeding the MVP requirements.

---

## 6. Implementation & Compliance Notes

* Schema definition in [infrastructure/database/postgres/02_init_vector_schema.sql](file:///d:/projects/SCOF_V1/SCOF/infrastructure/database/postgres/02_init_vector_schema.sql).
* Embedding generation and storage in `services/observability/src/db.py`.
* Cosine similarity RAG query endpoint in `services/api/src/routers/chat.py`.
* Verified via `python scripts/verify_full_loop.py` (Stage 7).

---

## 7. Related Decisions & Artifacts

* [ADR 007: Hybrid Knowledge Layer Architecture](./007_hybrid_knowledge_layer_neo4j_postgres.md)
* [D2 Knowledge Layer Documentation](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D02_knowledge_layer/README.md)
