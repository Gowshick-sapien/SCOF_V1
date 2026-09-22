# ADR 018: Cognitive Twin Service Layer as Programmatic Simulation and Audit Substrate

* **Status**: Accepted
* **Date**: 2026-09-22
* **Deciders**: SCOF Core Architecture Team
* **Consulted**: Systems Architects, Simulation Engineers
* **Informed**: Engineering Organization

---

## 1. Context and Problem Statement

To prevent autonomous LLM agents from hallucinating physical capacities, unviable freight speeds, or impossible inventory movements, agents must query an authoritative ground-truth environment. 

However, allowing agents to execute raw SQL against 96 relational tables or raw Cypher against 3.73M graph nodes forces agents to act as low-level database parsers, increasing prompt token consumption and latency. Furthermore, calculating multi-echelon physics (e.g., perishable goods temperature decay curves, capacity reduction percentages, write-off accounting, and three-way matching) requires dedicated algorithmic logic that cannot be reliably performed by language models alone.

---

## 2. Decision Drivers

* **Agent Grounding:** Provide specialist agents with deterministic, mathematically verified facts.
* **Physics & Accounting Invariants:** Programmatically enforce conservation of inventory, perishable spoilage curves, contract lead times, and double-entry general ledger balance.
* **Reusable Service Substrate:** Expose a single unified service layer consumable by LLM agents (via MCP), human operators (via Desktop Console REST APIs), and benchmark harnesses.

---

## 3. Considered Options

* **Option 1 (Direct Agent SQL/Cypher Access):** Let agents query the database and graph directly and perform calculations in prompt memory.
* **Option 2 (Dispersed Helper Scripts):** Scatter one-off calculation scripts across each agent microservice directory.
* **Option 3 (Unified Cognitive Twin Service Layer):** Implement a dedicated service layer (`services/twin_service.py`) exposing standardized, contractual operational and simulation APIs.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3: Unified Cognitive Twin Service Layer**

### Rationale:
`services/twin_service.py` acts as the programmatic bridge between the enterprise data fabric and the downstream consumers. It encapsulates:

1. **Stateful Scenario & Lifecycle Tracking:**
   * `create_scenario()`: Registers discrete perturbation experiments.
   * `start_simulation_run()` & `complete_simulation_run()`: Tracks lifecycle execution and timestamps.
   * `record_validation_result()`: Persists validation gate outcomes.
2. **The Five Contractual Cognitive Twin Operations:**
   * `get_farm_to_store_lineage(sku_id, store_id)`: Traces upstream multi-tier sourcing, transport lanes, and shelf facing.
   * `evaluate_demand_shock(event_id, zone_id, week_id)`: Applies localized multipliers and category elasticities.
   * `simulate_disruption(asset_id, downtime_hours)`: Quantifies capacity drops, perishable spoilage, and financial exposure.
   * `audit_three_way_match(po_id)`: Reconciles PO, Goods Receipt, and Supplier Invoice lines.
   * `get_financial_ledger_summary(fiscal_period_id)`: Audits double-entry general ledger equilibrium.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Completely shields agents from low-level schema complexities and database connection pooling.
* Centralizes physical, financial, and mathematical rules in a single, thoroughly testable Python class.
* Provides identical results whether invoked by an autonomous agent, a human operator in the Tauri console, or an automated benchmark test.

### Negative Consequences / Trade-offs:
* All cross-domain simulation operations must be maintained and versioned within `twin_service.py`.

---

## 6. Implementation & Compliance Notes

* **Service Implementation:** Located at `services/twin_service.py`.
* **Database Connection:** Connects to `datasets/scof_relational.db` with automated table creation for lifecycle entities.
* **Unit Test Suite:** Validated by `tests/test_twin_service.py` (5/5 tests passing in $< 0.5\text{s}$).
* **Documentation Guide:** Detailed in `docs/v2_enterprise/research/understanding_cognitive_twin_service.md`.
