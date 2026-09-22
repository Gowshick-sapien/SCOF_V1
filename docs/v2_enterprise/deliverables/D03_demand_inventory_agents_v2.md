# Deliverable D03 (V2): Enterprise Demand & Inventory Specialists

## 1. Overview & Objectives

Deliverable D03 upgrades the preliminary single-model predictors of V1 into two enterprise-grade cognitive specialist agents:
1. **The Demand Sensing & Forecasting Agent (`demand-agent`)**: Responsible for continuous demand sensing, promotional lift analysis, and qualitative shock interpretation across 49,616 SKUs and 16 stores.
2. **The Multi-Echelon Inventory Agent (`inventory-agent`)**: Responsible for optimal stock replenishment, buffer allocation across 5 Regional Distribution Centers (DCs) and 16 retail stores, and perishable asset risk management.

Both agents operate as autonomous specialists under the LangGraph orchestration kernel (D05), interfacing with the Enterprise Knowledge Fabric (D02) via bounded MCP tools.

---

## 2. Demand Sensing Specialist (`demand-agent`)

### 2.1 Multi-Model Forecasting Architecture
To handle both regular baseline demand and severe exogenous shocks, the Demand Agent employs a hybrid architecture:
* **Statistical / ML Core:** Quantitative baseline forecasting utilizing gradient-boosted regressors (LightGBM/XGBoost) trained on historical `pos_sales` and `daily_demand` streams.
* **Contextual Shock Reasoner (LLM):** Qualitative reasoning over sudden exogenous disruptions (e.g., severe weather anomalies, unannounced competitor closures, or local festival surges from the 554-event registry).
* **Cross-Elasticity Analysis:** Evaluating category-level product substitutions when a primary SKU encounters an operational stockout.

### 2.2 Domain Inputs & Bounded MCP Tool Permissions
The Demand Agent queries specific slices of the Knowledge Fabric:
* `get_pos_sales_trend(store_id, sku_id, lookback_days)`
* `get_promotional_calendar(zone_id, start_date, end_date)`
* `get_category_assortment_tree(category_id, max_depth=3)` (Neo4j projection)

---

## 3. Multi-Echelon Inventory Specialist (`inventory-agent`)

### 3.1 Multi-Echelon Replenishment Logic
The Inventory Agent governs stock flows across the two physical echelons of the SCOF Retail Enterprise Reference World:
$$\text{Supplier} \xrightarrow{\text{Lanes}} \text{Regional DC (5)} \xrightarrow{\text{Lanes}} \text{Retail Store (16)}$$

* **Dynamic Safety Stock ($SS$):** Evaluated continuously per SKU-facility pair:
  $$SS = Z_\alpha \times \sqrt{L \times \sigma_D^2 + D^2 \times \sigma_L^2}$$
  Where $Z_\alpha$ is the service level factor, $L$ is lead time, $\sigma_D$ is demand variance, and $\sigma_L$ is supplier lead-time jitter.
* **Perishable Asset Risk Management:** Direct integration with asset telemetry (`AST-xxxx`). When a cold-storage unit experiences compressor degradation, the Inventory Agent immediately prioritizes cross-dock transfers to prevent spoilage write-offs.
* **Holding Cost vs. Stockout Trade-off:** Optimizes total landed cost, balancing capital tie-up against SLA non-compliance penalties.

### 3.2 Domain Inputs & Bounded MCP Tool Permissions
* `get_facility_inventory(facility_id, sku_id)`
* `get_asset_operational_status(facility_id, asset_type)`
* `get_in_transit_shipments(destination_facility_id)`

---

## 4. Collaborative Deliberation & Structured Claims

During an operational disruption, the two agents interact via structured claims:
1. **Demand Proposal:** The Demand Agent detects a demand surge or drop and emits a structured claim $C_{demand}$ specifying expected unit requirements over a 14-day horizon.
2. **Inventory Counter-Evaluation:** The Inventory Agent consumes $C_{demand}$, verifies available buffer stocks at the regional DC and store, and evaluates whether local stocks suffice or whether an expedited stock transfer order (STO) is required.
3. **Consensus Hand-off:** If store capacity or lead times constrain fulfillment, the Inventory Agent issues a formal counter-claim with recommended rationing rules.

---

## 5. Acceptance Criteria & Verification Evidence

1. **Forecast Quality Gate:** Baseline demand predictions achieve Weighted Absolute Percentage Error ($\text{WAPE}) \le 12\%$ on stable categories.
2. **Shock Responsiveness Gate:** Qualitative event signals (festival lift or weather anomaly) trigger claim updates within $\le 850\text{ ms}$.
3. **Multi-Echelon Safety Gate:** Zero store-level stockouts for critical Class-A SKUs under nominal supplier lead times.
4. **Contract Compliance Gate:** All agent outputs strictly conform to [`structured_claim_contract.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/structured_claim_contract.md).
