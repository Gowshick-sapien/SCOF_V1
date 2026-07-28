# Deliverable D2 — Knowledge & Data Layer

## 🎯 Objective
Give agents somewhere to read from and write to, independent of the agents themselves (Neo4j Graph & Postgres pgvector store).

---

## 📋 Requirements Summary (from SRS)
- **FR-2.1**: Neo4j graph schema for supplier, product, warehouse, route nodes & relationships.
- **FR-2.2**: pgvector schema in Postgres for decision records, evidence snippets, and embeddings.
- **FR-2.3**: Idempotent, re-runnable ETL scripts loading synthetic data into Neo4j and Postgres (`data_bindings.yaml`).

---

## 🏁 Standalone Acceptance Criteria
Cypher queries (e.g. shortest path between supplier & warehouse) and pgvector similarity queries return sane results with no agent code present.
