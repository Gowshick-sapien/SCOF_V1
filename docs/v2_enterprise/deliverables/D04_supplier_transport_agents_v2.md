# Deliverable D04 (V2): Enterprise Supplier & Transport Specialists

## 1. Overview & Objectives

Deliverable D04 elevates the preliminary heuristic delay checkers of V1 into two enterprise-scale structural network specialists:
1. **The Supplier Collaboration Agent (`supplier-agent`)**: Governs relationships, procurement allocations, and SLA monitoring across 200 suppliers and 225 commercial contracts.
2. **The Transportation Logistics Agent (`transport-agent`)**: Governs freight dispatch, carrier allocation, and dynamic corridor rerouting across 25 carriers and 35 primary transport corridors.

Both agents operate on the Enterprise Knowledge Fabric (D02), utilizing graph traversals over the 3.73M-node topology to resolve complex upstream and midstream supply chain bottlenecks.

---

## 2. Supplier Collaboration Specialist (`supplier-agent`)

### 2.1 Performance Analytics & Multi-Sourcing Optimization
The Supplier Agent continuously evaluates vendor health and enforces contractual integrity:
* **Vendor Performance Index (VPI):** Composite metric tracking historical On-Time In-Full ($\text{OTIF}$), quality inspection pass rates, and invoice pricing accuracy across 15,000 purchase orders.
* **Dynamic Split-Allocation:** When a Tier-1 supplier flags a production disruption or lead-time blowout ($+\Delta t$), the agent splits orders with secondary qualified vendors in the catalog while respecting Minimum Order Quantities (MOQ) and tiered price breaks.
* **Contract Penalty Enforcement:** Calculates contractual SLA breach penalties to inform financial exposure calculations.

### 2.2 Domain Inputs & Bounded MCP Tool Permissions
* `get_supplier_scorecard(supplier_id, lookback_months)`
* `get_contract_terms(supplier_id, product_id)`
* `get_supplier_lead_time_distribution(supplier_id, category_id)`

---

## 3. Transportation Logistics Specialist (`transport-agent`)

### 3.1 Freight Optimization & Corridor Disruption Rerouting
The Transport Agent manages the physical movement of freight between 200 suppliers, 5 Regional DCs, and 16 retail stores:
* **Dynamic Carrier Selection:** Selects carriers among the 25 contracted providers based on committed lane volume, equipment type (dry van vs. reefer), and carbon efficiency ratings.
* **Graph-Based Rerouting:** When a transport corridor experiences physical closure (e.g., weather impassability or infrastructure failure), the agent queries the Neo4j materialized graph projection to compute optimal multi-hop detour paths satisfying:
  $$\min \sum_{(u, v) \in \text{Path}} \text{Cost}(u, v) \quad \text{subject to } \text{TransitTime}(\text{Path}) \le T_{max}$$
* **Demurrage & Backlog Mitigation:** Re-allocates dock appointment slots to prevent terminal congestion.

### 3.2 Domain Inputs & Bounded MCP Tool Permissions
* `find_alternate_carrier_routes(origin_id, destination_id, max_transit_days=5)` (Neo4j projection)
* `get_lane_congestion_status(lane_id)`
* `get_carrier_capacity_allowance(carrier_id, date)`

---

## 4. Upstream-Midstream Collaborative Protocol

When an upstream disruption occurs (e.g., Supplier `SUP-0042` declares force majeure):
1. **Supplier Claim ($C_{supplier}$):** The Supplier Agent calculates volume shortfalls and emits a claim recommending an alternate vendor (`SUP-0089`) with an updated ship date.
2. **Transportation Feasibility Check ($C_{transport}$):** The Transport Agent inspects whether the alternate origin has active carrier contracts, sufficient reefer capacity, and viable transit lanes within the SLA window.
3. **Harmonized Action Plan:** If viable, the Transport Agent seconds the claim; if unviable, it proposes an alternative transshipment hub.

---

## 5. Acceptance Criteria & Verification Evidence

1. **Vendor Resilience Gate:** Automated dual-sourcing rebalances order shortfalls within $\le 1.2\text{ s}$ of supplier disruption injection.
2. **Graph Traversal Gate:** Bounded alternate route queries over the 3.73M-node Neo4j graph return viable paths in $< 50\text{ ms}$ (ADR ADR 005 (Amendment)).
3. **Contract Adherence Gate:** 100% of generated purchase claims honor minimum order quantities and supplier payment terms.
4. **Contract Compliance Gate:** All outputs conform to [`structured_claim_contract.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/structured_claim_contract.md).
