# Bounded MCP Tool Specifications (V2)

## 1. Overview & Security Invariant

To enforce the sub-second ($< 500\text{ ms}$) decision SLA and protect server memory across the 3.73M-node Neo4j property graph and 96 relational tables, specialist agents are **strictly prohibited from executing raw SQL or unconstrained Cypher queries** ([ADR ADR 005 (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005b_amendment_materialized_graph_projection_and_bounded_queries.md)).

All agent interactions with the enterprise environment occur through **Model Context Protocol (MCP)** tools. Furthermore, rather than statically mounting dozens of tools into every prompt, tools are dynamically bound per task via the [Dynamic Capability Registry](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md) ([ADR ADR 012 (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/012b_amendment_dynamic_capability_registry_over_static_mcp.md)), limiting prompt context to 3-5 bounded tools.

---

## 2. Classification by Operational Class

Tools are strictly partitioned into three operational classes ([ADR ADR 013](file:///d:/projects/SCOF_V1/SCOF/docs/adr/013_tri_zone_query_routing_and_deeper_resolver.md)):

### 2.1 Class A: Direct Read-Only Enterprise Facts (D2 Fabric)
Direct lookups against PostgreSQL (system of record) and bounded Neo4j traversals:
* **`mcp_get_inventory_position`**:
  * *Parameters:* `facility_id: string`, `sku_id: string`.
  * *Returns:* `quantity_on_hand`, `quantity_allocated`, `quantity_available`, `reorder_point`.
* **`mcp_get_supplier_profile`**:
  * *Parameters:* `supplier_id: string`.
  * *Returns:* Supplier profile, commercial contracts, payment terms, and vendor tier.
* **`mcp_get_upstream_supply_path`**:
  * *Parameters:* `sku_id: string`, `facility_id: string`, `max_depth: int = 3` (hard cap: 3).
  * *Returns:* Ordered graph path `(:Store) <-[:SERVICED_BY]- (:DC) <-[:SUPPLIED_BY]- (:Supplier)`.
* **`mcp_get_affected_downstream_facilities`**:
  * *Parameters:* `disrupted_facility_id: string`, `max_hops: int = 2` (hard cap: 2).
  * *Returns:* List of retail stores serviced by the affected warehouse.
* **`mcp_find_alternate_carrier_routes`**:
  * *Parameters:* `origin_facility_id: string`, `destination_facility_id: string`, `max_transit_days: int = 5`.
  * *Returns:* Candidate transport lanes, assigned carriers, and standard freight rates.

### 2.2 Class B: Derived Operational Metrics & Analytics (Analytic Services)
Statistical computations and ML inferences:
* **`mcp_get_supplier_reliability_score`**:
  * *Parameters:* `supplier_id: string`.
  * *Returns:* 90-day OTIF compliance rate, quality defect percentage, and risk score.
* **`mcp_evaluate_demand_shock`**:
  * *Parameters:* `event_id: string`, `zone_id: string`, `week_id: int`.
  * *Returns:* Effective category lift multipliers and regional event weight multipliers.
* **`mcp_get_carrier_transit_variance`**:
  * *Parameters:* `carrier_id: string`, `lane_id: string`.
  * *Returns:* Mean transit days, variance, and standard deviation over last 180 days.

### 2.3 Class C: Scenario Simulation & Counterfactuals (Twin Substrate)
Stateful simulation and counterfactual intervention evaluation:
* **`mcp_simulate_asset_disruption`**:
  * *Parameters:* `scenario_id: string`, `asset_id: string`, `downtime_hours: float` ($1.0 \le t \le 168.0$).
  * *Returns:* Capacity reduction %, perishable spoilage units, write-off cost, revenue loss.
* **`mcp_evaluate_counterfactual_intervention`**:
  * *Parameters:* `scenario_id: string`, `branch_name: string`, `actions: list[object]`.
  * *Returns:* Comparative delta matrix (fill-rate preservation, net cost, invariant status).
* **`mcp_get_deterministic_evidence_pack`**:
  * *Parameters:* `scenario_id: string`, `claim_id: string`.
  * *Returns:* Verifiable state snapshots with cryptographic SHA-256 provenance hashes.

---

## 3. Implementation References

* Formal Data Contract: [`capability_registry_spec.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/capability_registry_spec.md)
* Architecture Specification: [Dynamic Capability Registry Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md)
* Twin API Contract: [`twin_service_api_spec.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/twin_service_api_spec.md)

