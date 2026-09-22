# Bounded MCP Tool Specifications (V2)

## 1. Overview & Security Invariant

To enforce the sub-second ($< 500\text{ ms}$) decision SLA and protect server memory across the 3.73M-node Neo4j property graph and 96 relational tables, specialist agents are **strictly prohibited from executing raw SQL or unconstrained Cypher queries** (ADR 014).

All agent interactions with the enterprise environment occur through **Model Context Protocol (MCP)** tools. Each tool enforces strict input validation, parameter boundaries, and depth constraints.

---

## 2. Standardized Tool Registry

### 2.1 Twin Service Simulation & Lineage Tools
* **`mcp_simulate_asset_disruption`**:
  * *Parameters:* `asset_id: string`, `downtime_hours: float` (bounded: $1.0 \le t \le 168.0$).
  * *Returns:* Capacity reduction %, perishable spoilage units, write-off cost, revenue loss.
* **`mcp_get_farm_to_store_lineage`**:
  * *Parameters:* `sku_id: string`, `store_id: string`.
  * *Returns:* Upstream supplier tier, preferred contract terms, primary DC, transport lane, and shelf facing.
* **`mcp_evaluate_demand_shock`**:
  * *Parameters:* `event_id: string`, `zone_id: string`, `week_id: int`.
  * *Returns:* Effective category lift multipliers and regional event weight multipliers.

### 2.2 Knowledge Fabric Bounded Graph Traversal Tools
* **`mcp_get_upstream_supply_path`**:
  * *Parameters:* `sku_id: string`, `facility_id: string`, `max_depth: int = 3` (hard cap: 3).
  * *Returns:* Ordered graph path `(:Store) <-[:SERVICED_BY]- (:Warehouse) <-[:SUPPLIED_BY]- (:Supplier)`.
* **`mcp_get_affected_downstream_facilities`**:
  * *Parameters:* `disrupted_facility_id: string`, `max_hops: int = 2` (hard cap: 2).
  * *Returns:* List of retail stores serviced by the affected warehouse.
* **`mcp_find_alternate_carrier_routes`**:
  * *Parameters:* `origin_facility_id: string`, `destination_facility_id: string`, `max_transit_days: int = 5`.
  * *Returns:* Candidate transport lanes, assigned carriers, and standard freight rates.

### 2.3 Relational System of Record Query Tools
* **`mcp_get_inventory_position`**:
  * *Parameters:* `facility_id: string`, `sku_id: string`.
  * *Returns:* `quantity_on_hand`, `quantity_allocated`, `quantity_available`, `reorder_point`.
* **`mcp_get_supplier_reliability_score`**:
  * *Parameters:* `supplier_id: string`.
  * *Returns:* Historical on-time delivery rate, quality compliance score, and vendor tier.
