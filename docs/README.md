# SCOF Documentation Portal: Two-Track Architecture

## Welcome to the SCOF Technical Documentation

The documentation for the **Supply Chain Cognitive Orchestration Framework (SCOF)** is organized into a **Two-Track Architecture** to provide complete clarity between the proven, working V1 MVP baseline and the active V2 Enterprise Cognitive Twin expansion.

---

## 1. Documentation Tracks Overview

```
docs/
├── adr/                                    # Master Architecture Decision Records (ADR ADR 014 - 018+)
├── v1_mvp/                                # Track 1: Frozen V1 MVP Baseline Specification
└── v2_enterprise/                         # Track 2: Active V2 Enterprise Cognitive Twin Architecture
```

| Documentation Track | Focus & Scope | Key Contents | Primary Audience |
| :--- | :--- | :--- | :--- |
| **[Track 1: V1 MVP Baseline](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/README.md)** | Proof-of-concept multi-agent consensus system over the initial 5-supplier electronics profile. | V1 Architecture, SRS, Ideation, Implementation Plan, and original Deliverables D01 through D11. | Historical reference, baseline benchmarking, and verification of initial 40/40 tests. |
| **[Track 2: V2 Enterprise Cognitive Twin](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/README.md)** | Full-scale industrial digital twin over 30 business domains, 96 tables, 49.6K SKUs, and 3.73M Neo4j nodes. | Enterprise Dataset Architecture, Ontologies, ERDs, V2 Deliverable Blueprints (D01-D11), Contracts, and Research. | Active development, enterprise deployment, simulation studies, and academic research. |
| **[Architecture Decision Records (ADRs)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/README.md)** | Sequentially tracked architectural choices across both V1 (001-012) and V2 (013-018+). | Formal records documenting problem context, evaluated alternatives, decisions, and supersession links. | Systems architects, core contributors, and auditors. |

---

## 2. Quick Links to Key Documents

### Track 1: V1 MVP Baseline
* **[V1 System Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/architecture.md)**
* **[V1 Software Requirements Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/srs.md)**
* **[V1 Ideation & Vision](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/ideation.md)**
* **[V1 Deliverables Index](file:///d:/projects/SCOF_V1/SCOF/docs/v1_mvp/deliverables/D01_simulation_data/README.md)**

### Track 2: V2 Enterprise Cognitive Twin
* **[V2 Architecture Evolution Blueprint](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/scof_v2_architecture_evolution.md)**
* **[Enterprise Dataset Master Architecture Report](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/dataset/SCOF_Enterprise_Dataset_Architecture_and_Implementation_Report.md)**
* **[Dataset Files Big Picture Understanding Guide](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/dataset/SCOF_Dataset_Files_Big_Picture_Understanding_Document.md)**
* **[Enterprise Foundational Ontology](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Foundational_Ontology.md)**
* **[Canonical Enterprise ERD](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Canonical_ERD.md)**
* **[Cognitive Twin Service Guide](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/research/understanding_cognitive_twin_service.md)**

### Repository Organization & Governance
* **[Repository Structure Guide](file:///d:/projects/SCOF_V1/SCOF/docs/repository_structure.md)**
* **[Architecture Decision Records Registry](file:///d:/projects/SCOF_V1/SCOF/docs/adr/README.md)**

---

## 3. Dataset Architecture & Bootstrap Strategy

SCOF implements a **Two-Tiered Hybrid Dataset Strategy** to maintain git repository speed, respect GitHub's 100 MB file limit, and guarantee 100% deterministic reproducibility:

* **Tier 1 (Tracked in Git, < 20 MB):** All generation code, schemas (`schema_ddl.sql`, `neo4j_schema_ddl.cql`), cryptographic SHA-256 manifests (`run_manifest.json`), domain binding profiles, and small foundational seed CSVs.
* **Tier 2 (Materialized Local Projections, Ignored in Git):** Heavy compiled SQLite databases (`datasets/scof_relational.db`, 558 MB), giant uncompressed raw simulation dumps (1.97 GB), and Neo4j bulk CSV export trees (430 MB).

### Setting Up the Dataset

To inspect or compile the local enterprise database, use the bootstrap utility:

```bash
# Check current database and dataset readiness
python scripts/bootstrap_dataset.py --status
# Or via Makefile:
make data-status

# Recompile the 96-table SQLite database from tracked CSVs/Parquets
python scripts/bootstrap_dataset.py --build
# Or via Makefile:
make data-build

# Compress the SQLite database to a 107 MB zip for GitHub Release upload
python scripts/bootstrap_dataset.py --compress
```
