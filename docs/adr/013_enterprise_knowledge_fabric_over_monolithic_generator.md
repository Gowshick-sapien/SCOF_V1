# ADR 013: Enterprise Knowledge Fabric over Monolithic Synthetic Generator

* **Status**: Accepted (Supersedes V1 D01/D02 Toy Generator Scope)

---

## 1. Context and Problem Statement

In SCOF V1, Deliverables D1 and D2 relied on a monolithic procedural generator designed to synthesize an isolated toy supply chain (1 manufacturer, 5 suppliers, 2 warehouses, 1 distribution center, and 3–5 products). While sufficient for initial LangGraph and CD²F algorithmic prototyping, this toy dataset lacks the enterprise realism, multi-echelon depth, cross-domain foreign key constraints, and commercial complexities required for an industrial-grade Cognitive Twin.

Furthermore, procedural on-the-fly generation coupled generator code to runtime execution, making it difficult to establish cryptographic provenance, repeatable data lineage, and multi-tier network relationships.

---

## 2. Decision Drivers

* **Enterprise Realism:** Need for realistic multi-echelon supply chain topologies, assortment policies, pricing histories, and transaction ledgers.
* **Referential Integrity:** Enforce strict foreign-key topologies (165 physical FKs across 96 tables) mirroring enterprise ERP systems.
* **Topological Scale:** Support rich graph traversals over tens of thousands of SKUs and multi-tiered supplier-carrier relationships.
* **Deterministic Provenance:** Shift from dynamic random procedural generation to immutable, frozen, cryptographically verified datasets.

---

## 3. Considered Options

* **Option 1 (Retain V1 Monolithic Generator):** Continue expanding procedural Python scripts to dynamically generate larger synthetic populations at container startup.
* **Option 2 (Pre-Generated Scaled Single-Domain Tables):** Generate large CSV files for inventory and orders without a unified enterprise ontology or cross-domain relational integrity.
* **Option 3 (Unified 30-Domain Enterprise Knowledge Fabric):** Construct an authoritative 30-business-domain relational database and materialized property graph governed by an 8-tier Directed Acyclic Graph (DAG), persisted to Parquet/SQLite/Neo4j with complete relational and graph parity.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3: Unified 30-Domain Enterprise Knowledge Fabric**

### Rationale:
Option 3 replaces the toy procedural generator with the **SCOF Retail Enterprise Reference World**:
* **Enterprise Scale:** 49,616 SKUs, 200 suppliers, 25 carriers, 21 facilities (5 DCs, 16 stores), 35 transport lanes, 15,000 purchase orders, 18,000 shipments, 65,000 invoices/payments, 50,000 sales transactions, and 18M demand rows.
* **Authoritative Provenance:** Governed by an 8-tier generation DAG (`SCOF_Physical_Generation_DAG.yaml`) compiled into `generation_manifest.json` and cryptographically tracked via `run_manifest.json`.
* **Verified Parity:** Validated across 5 architectural gates (100% referential integrity, zero dangling foreign keys, 51 frozen core Neo4j constraints).

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Establishes a true industrial foundation capable of supporting realistic demand shock, spoilage, and rerouting experiments.
* Eliminates dynamic startup generation latency; services bind immediately to persisted, high-performance Parquet and SQLite/PostgreSQL stores.
* Enables cross-functional deliberation across inventory, transport, procurement, commerce, and finance.

### Negative Consequences / Trade-offs:
* Dataset footprint increases (approx. 585 MB SQLite database, 2 GB weekly demand history).
* Requires rigorous runtime state isolation to prevent simulation runs from corrupting the baseline dataset (addressed in ADR 015).

---

## 6. Implementation & Compliance Notes

* **Persisted Data:** Located in `datasets/` (`scof_relational.db`, Parquet files, Neo4j CSV dumps).
* **Generation DAG:** Governed by `docs/v2_enterprise/dataset/SCOF_Physical_Generation_DAG.yaml` and `generators/`.
* **Validation Reports:** Documented in `docs/v2_enterprise/dataset/SCOF_Validation_Report.md`.
