# Deliverable D1 — Simulation Environment & Synthetic Data Foundation

## 🎯 Objective
Produce a self-contained, reproducible synthetic supply chain world before any AI touches it, driven by the active Domain Profile.

---

## 📋 Requirements Summary (from SRS)
- **FR-1.1**: Docker Compose infrastructure (Postgres, Redis, Kafka, Neo4j).
- **FR-1.2**: Synthetic entity generator (1 manufacturer, 3–5 products, 5 suppliers, 2 warehouses, 1 DC, multi-route network).
- **FR-1.3**: Parameterized disruption event generator (supplier delay, transport failure, demand spike, adverse weather).
- **FR-1.4**: Generated data queryable directly from Postgres.
- **FR-1.5**: Generator reads entity definitions & disruption parameters from active Domain Profile (`topology.yaml`, `disruptions.yaml`).

---

## 🏁 Standalone Acceptance Criteria
Running `docker compose up`, triggering the generator, and querying Postgres directly returns realistic order/inventory/shipment histories and injectable disruption events, with no agents or APIs involved.

---

## 📁 Folder Contents
- `README.md` — Overview & tracking
- `design_decisions.md` — Generator architecture & data model choices *(to be created during D1 implementation)*
- `schema_design.md` — PostgreSQL table definitions *(to be created during D1 implementation)*
- `data_dictionary.md` — Entity fields, types, and constraints *(to be created during D1 implementation)*
- `acceptance_evidence.md` — Test results & query outputs proving completion *(to be created upon completion)*
