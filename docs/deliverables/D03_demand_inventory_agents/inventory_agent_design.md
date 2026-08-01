# Deliverable D3 -- Inventory Agent Design

## 1. Context & Purpose
The Inventory Agent monitors warehouse stock levels, safety stock thresholds, reorder points, and inbound shipment status to predict stockout and overstock risks. It ensembles an XGBoost model (trained on inventory depletion features) with a statistical decomposition model (trend + seasonality on stock levels), producing a structured claim with days-to-stockout projections, reorder recommendations, confidence scores, reasoning, and traceable evidence. The agent operates as a standalone FastAPI service callable without the Coordinator existing.

---

## 2. Agent Identity

| Property | Value |
| --- | --- |
| **Agent ID** | `inventory-agent` |
| **Service Port** | 8012 |
| **Profile Source** | `agents.yaml` -> `inventory-agent` block |
| **Confidence Floor** | 0.65 (from profile; used for `low_confidence` flag only, never clamping) |
| **Protocol** | A2A/1.0 (Agent Card at `/.well-known/agent.json`) |
| **A2A Tags** | `["inventory", "stockout", "safety-stock", "reorder"]` |
| **Supported Contexts** | `["supplier_delay", "demand_spike", "transport_failure"]` |
| **Dependencies** | `["postgres"]` |

---

## 3. Pipeline Architecture

The agent follows the same clean four-stage pipeline as the Demand Agent.

```
ScenarioContext (input)
        |
        v
  InventoryDataAccess     -- Fetches stock levels, shipments, disruptions, capacity
        |                     Returns data + query_hash for evidence traceability
        v
  InventoryFeatureBuilder -- Transforms raw data into risk-assessment features
        |                     Depletion rate, days-of-supply, safety stock proximity
        v
  InventoryEnsemble       -- Runs XGBoost + Statistical inference models
        |                     Returns EnsembleResult (stock projection, interval, agreement)
        v
  ClaimBuilder            -- Constructs StructuredClaim
                              Sets low_confidence flag if confidence < floor
                              Never modifies the confidence value itself
```

---

## 4. Data Sources

All data is read from PostgreSQL tables populated by D1 (Simulation Environment).

### 4.1 Daily Inventory Levels
- **Table**: `scof.inventory_levels`
- **Query**: Fetches daily `stock_on_hand`, `safety_stock_threshold`, `reorder_point`, `units_in_transit` by `warehouse_id` and `product_id` for a given `run_id`
- **Output**: Time-series DataFrame with columns `[date, warehouse_id, product_id, stock_on_hand, safety_stock_threshold, reorder_point, units_in_transit]`
- **Traceability**: Each query generates a SHA-256 `query_hash` stored in `EvidenceItem.query_hash`

### 4.2 Inbound Shipments
- **Table**: `scof.shipments` joined with `scof.purchase_orders`
- **Query**: Fetches shipments with `status IN ('IN_TRANSIT', 'PENDING')` destined for the queried warehouses, including `estimated_arrival`, `actual_arrival`, and associated `order_items`
- **Output**: List of shipment dicts with arrival dates, quantities, and status

### 4.3 Supplier Disruptions
- **Table**: `scof.disruption_events`
- **Query**: Fetches disruption events where `target_entity_type = 'supplier'` or `disruption_type IN ('supplier_delay', 'transport_failure')` for the scenario's `run_id` and `scenario_id`
- **Purpose**: If a supplier is disrupted, in-transit units from that supplier are at risk and replenishment lead times increase

### 4.4 Warehouse Capacity
- **Table**: `scof.warehouses`
- **Query**: Fetches `capacity_units` for the queried warehouses
- **Purpose**: Capacity utilization analysis for overstock detection

---

## 5. Feature Engineering (`InventoryFeatureBuilder`)

Feature engineering is separated from the agent into a dedicated `InventoryFeatureBuilder` class.

### 5.1 Features

| Feature | Description | Computation |
| --- | --- | --- |
| `depletion_rate_7d` | Average daily stock consumption over trailing 7 days | `(stock[t-7] - stock[t]) / 7` |
| `depletion_rate_14d` | Average daily stock consumption over trailing 14 days | `(stock[t-14] - stock[t]) / 14` |
| `days_of_supply` | Projected days until stockout at current depletion rate | `stock_on_hand / depletion_rate_7d` |
| `safety_stock_ratio` | Current stock relative to safety threshold | `stock_on_hand / safety_stock_threshold` |
| `reorder_proximity` | Distance from reorder point (negative = below) | `stock_on_hand - reorder_point` |
| `safety_breach_countdown` | Days until stock falls below safety threshold | `(stock_on_hand - safety_stock_threshold) / depletion_rate_7d` |
| `units_in_transit` | Units currently in transit to this warehouse | Direct from `inventory_levels` |
| `transit_risk_factor` | In-transit risk: 1.0 if supplier disruption active, 0.0 otherwise | Binary based on active disruptions |
| `effective_in_transit` | In-transit units adjusted for risk | `units_in_transit * (1.0 - transit_risk_factor)` |
| `capacity_utilization` | Stock as fraction of warehouse capacity | `stock_on_hand / capacity_units` |
| `stock_velocity_trend` | Trend in depletion rate (accelerating/decelerating) | Slope of `depletion_rate_7d` over trailing 14 days |
| `disruption_active` | Binary: 1 if a supplier/transport disruption is active | -- |
| `disruption_severity` | Integer severity (1-5) if active, else 0 | -- |

### 5.2 Risk Assessment Logic
Beyond the ML ensemble, the agent applies deterministic risk rules for high-confidence edge cases:
- **Immediate stockout**: `days_of_supply < 3` and no inbound shipments within 3 days -> priority HIGH
- **Safety stock breach imminent**: `safety_breach_countdown < 5` -> priority HIGH
- **Overstock risk**: `capacity_utilization > 0.90` with inbound shipments arriving -> flag in reasoning

---

## 6. ML Models

### 6.1 XGBoost Inventory Model

**Training** (`InventoryXGBoostTrainer`):
- Objective: `reg:squarederror` for stock level projection; `reg:quantile` for prediction intervals
- Target variable: `stock_on_hand` at t+N (where N = forecast horizon)
- Hyperparameters:
  - `n_estimators`: 200
  - `max_depth`: 6
  - `learning_rate`: 0.1
  - `reg_alpha`: 0.1
  - `reg_lambda`: 1.0
  - `random_state`: `XGBOOST_SEED` (42)
- Output: `ModelArtifact` stored at `models/inventory/v<version>/xgboost_model.pkl`

**Inference** (`InventoryXGBoostInference`):
- Initialized from `ModelArtifact` only
- `predict(X) -> np.ndarray`: Projected stock levels
- `predict_interval(X, alpha=0.1) -> PredictionInterval`: Lower/upper bounds

### 6.2 Statistical Decomposition Model

**Training** (`InventoryStatisticalTrainer`):
- Decomposes the stock level time-series into:
  - **Trend**: Linear regression on time index (captures gradual depletion or accumulation)
  - **Seasonality**: Day-of-week seasonal dummies (captures weekly ordering patterns)
  - **Residual**: Observed - trend - seasonal
- Stores coefficients and residual standard deviation

**Inference** (`InventoryStatisticalInference`):
- `predict(horizon) -> np.ndarray`: Extrapolated stock levels
- `predict_interval(horizon, alpha=0.1) -> PredictionInterval`: From residual distribution

### 6.3 Ensemble (`InventoryEnsemble`)
- Subclasses `BaseEnsemble` from `shared/scof_shared/ml/`
- Weights from profile `agents.yaml` (default: `{"xgboost": 0.6, "statistical": 0.4}`)
- Agreement score computed the same way as Demand Agent

---

## 7. Confidence Calibration

Uses the same shared `ConfidenceCalculator` as the Demand Agent:

```
confidence = 0.4 * agreement_score
           + 0.3 * (1.0 - interval_width / max_interval_width)
           + 0.3 * (1.0 - clamp(historical_error, 0, 1))
```

For the Inventory Agent, `historical_error` is the MAE of stock level predictions on a holdout split, normalized by the mean stock level.

**Confidence is never clamped or inflated.** If computed confidence falls below `confidence_floor` (0.65), `low_confidence=True` is set on the claim.

---

## 8. MCP Tool Declarations

Tool declarations are metadata descriptors consumed by the Agent Card. Full MCP protocol wiring occurs in D5.

| Tool Name | Description | Input | Output |
| --- | --- | --- | --- |
| `read_stock_levels` | Read current and historical inventory levels | `{run_id, warehouse_ids, product_ids, start_date, end_date}` | `DataFrame[date, warehouse_id, product_id, stock_on_hand, ...]` |
| `read_reorder_points` | Read safety stock thresholds and reorder points | `{warehouse_ids, product_ids}` | `List[{warehouse_id, product_id, safety_stock, reorder_point}]` |
| `read_inbound_shipments` | Read pending and in-transit shipment arrivals | `{run_id, warehouse_ids}` | `List[ShipmentInfo]` |
| `read_inventory_disruptions` | Read disruptions impacting suppliers or transport routes | `{run_id, scenario_id}` | `List[DisruptionEvent]` |

---

## 9. Random Seeds

| Seed | Value | Controls |
| --- | --- | --- |
| `NUMPY_SEED` | 42 | NumPy random state |
| `XGBOOST_SEED` | 42 | XGBoost `random_state` parameter |
| `PYTHON_RANDOM_SEED` | 42 | Python `random` module |

---

## 10. Health Endpoint

`GET /health` returns:

```json
{
  "status": "healthy",
  "agent_id": "inventory-agent",
  "profile_loaded": true,
  "db_connected": true,
  "neo4j_connected": false,
  "model_loaded": true,
  "model_version": "1.0.0",
  "uptime_seconds": 1842.3
}
```

---

## 11. Example Structured Claim Output

```json
{
  "agent_id": "inventory-agent",
  "scenario_id": "scenario-001",
  "recommendation": "Initiate emergency reorder of 800 units of prod-102 (Industrial Sensor Unit) for wh-01 (East Asia Transit Hub). Projected stockout in 5 days at current depletion rate.",
  "reasoning": "Stock depleting at 120 units/day (7d average). Current stock: 580 units. Safety threshold: 200 units. Safety breach in ~3.2 days. Supplier delay active for sup-02 (severity 3), placing 400 in-transit units at risk. Ensemble agreement moderate (0.78). Recommend alternate supplier sourcing.",
  "confidence": 0.72,
  "low_confidence": false,
  "priority": "HIGH",
  "impact": "Projected stockout of prod-102 at wh-01 within 5 days. Estimated fill-rate drop from 98% to 72% if no action taken. 400 units in-transit from sup-02 at risk due to active supplier delay.",
  "evidence": [
    {
      "type": "historical_data",
      "source": "scof.inventory_levels",
      "summary": "wh-01 / prod-102: stock_on_hand=580, safety_stock=200, reorder_point=350, units_in_transit=400. 7-day depletion rate: 120 units/day.",
      "reference_id": "inventory_level:wh-01:prod-102:2026-07-29",
      "query_hash": "c4d9e2f1a8b73456..."
    },
    {
      "type": "model_output",
      "source": "InventoryEnsemble (XGBoost 0.6, Statistical 0.4)",
      "summary": "5-day stock projection: 0 units (stockout at day 4.8). 90% prediction interval: [-60, 45]. Agreement score: 0.78.",
      "reference_id": "ensemble:inventory:v1.0.0:scenario-001:wh-01:prod-102",
      "query_hash": null
    },
    {
      "type": "historical_data",
      "source": "scof.disruption_events",
      "summary": "Active disruption: supplier_delay (severity 3) targeting sup-02, started 2026-07-25, ends 2026-08-01. In-transit shipment from sup-02 (400 units, ETA 2026-07-31) at risk.",
      "reference_id": "disruption_event:dis-evt-003",
      "query_hash": "e8a1b3c5d7f20946..."
    },
    {
      "type": "historical_data",
      "source": "scof.shipments",
      "summary": "Inbound shipment shp-0042 from sup-02: 400 units of prod-102, status=IN_TRANSIT, ETA=2026-07-31. Route: route-sup02-wh01 (ocean, 12 transit days).",
      "reference_id": "shipment:shp-0042",
      "query_hash": "f2b4d6e8a0c13579..."
    }
  ],
  "timestamp": "2026-08-01T16:00:00Z"
}
```

---

## 12. Stockout vs. Overstock Decision Logic

| Condition | Priority | Recommendation Direction |
| --- | --- | --- |
| `days_of_supply < 3` and no inbound within 3 days | HIGH | Emergency reorder |
| `safety_breach_countdown < 5` | HIGH | Accelerated reorder |
| `reorder_proximity < 0` (below reorder point) | MEDIUM | Standard reorder |
| `days_of_supply > 30` and inbound arriving | LOW | Defer or reduce orders |
| `capacity_utilization > 0.90` with inbound | MEDIUM | Divert shipments or defer |

The agent always includes the quantitative basis (days-of-supply, depletion rate, threshold values) in the `reasoning` field so the Coordinator can weigh this claim against other agents' claims.

---

## 13. Maps to Source Documents
- **SRS**: Section 3.3 (FR-3.2, FR-3.3), Section 3.4 (Structured Claim Contract)
- **Architecture**: Section 4.2 (Specialist Agent Layer), Section 4.2.2 (Agent Specifications -- Inventory Agent row)
- **Ideation**: Section 10.2 (Inventory Agent), Section 13.1 (Structured Agent Claims)
- **Implementation Plan**: D3 deliverable definition
