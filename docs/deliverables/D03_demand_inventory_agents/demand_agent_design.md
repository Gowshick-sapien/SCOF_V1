# Deliverable D3 -- Demand Agent Design

## 1. Context & Purpose
The Demand Forecast Agent predicts future product demand by analyzing historical purchase order volumes and order item quantities from D1's synthetic data. It ensembles an XGBoost gradient-boosted model with a lightweight statistical decomposition model (trend + seasonality), producing a structured claim with a point forecast, prediction interval, confidence score, reasoning, and traceable evidence. The agent operates as a standalone FastAPI service callable without the Coordinator existing.

---

## 2. Agent Identity

| Property | Value |
| --- | --- |
| **Agent ID** | `demand-agent` |
| **Service Port** | 8011 |
| **Profile Source** | `agents.yaml` -> `demand-agent` block |
| **Confidence Floor** | 0.60 (from profile; used for `low_confidence` flag only, never clamping) |
| **Protocol** | A2A/1.0 (Agent Card at `/.well-known/agent.json`) |
| **A2A Tags** | `["forecasting", "demand", "time-series"]` |
| **Supported Contexts** | `["demand_spike", "supplier_delay"]` |
| **Dependencies** | `["postgres"]` |

---

## 3. Pipeline Architecture

The agent follows a clean four-stage pipeline. Each stage has a single responsibility.

```
ScenarioContext (input)
        |
        v
  DemandDataAccess        -- Fetches raw data from PostgreSQL
        |                     Returns data + query_hash for evidence traceability
        v
  DemandFeatureBuilder    -- Transforms raw data into model-ready features
        |                     Day-of-week, rolling averages, lags, disruption severity
        v
  DemandEnsemble          -- Runs XGBoost + Statistical inference models
        |                     Returns EnsembleResult (point forecast, interval, agreement)
        v
  ClaimBuilder            -- Constructs StructuredClaim
                              Sets low_confidence flag if confidence < floor
                              Never modifies the confidence value itself
```

---

## 4. Data Sources

All data is read from PostgreSQL tables populated by D1 (Simulation Environment).

### 4.1 Historical Demand
- **Tables**: `scof.purchase_orders` joined with `scof.order_items`
- **Query**: Aggregates order item quantities by product ID and order date for a given `run_id`
- **Output**: Time-series DataFrame with columns `[date, product_id, total_quantity]`
- **Traceability**: Each query generates a SHA-256 `query_hash` stored in `EvidenceItem.query_hash`

### 4.2 Active Disruptions
- **Table**: `scof.disruption_events`
- **Query**: Fetches disruption events for the scenario's `run_id` and `scenario_id` where `target_entity_type = 'product'` or `disruption_type = 'demand_spike'`
- **Output**: List of disruption dicts with `disruption_type`, `severity`, `start_date`, `end_date`, `target_entity_id`

### 4.3 Product Metadata
- **Table**: `scof.products`
- **Query**: Fetches product names and SKUs for context in claim reasoning
- **Output**: List of product dicts

---

## 5. Feature Engineering (`DemandFeatureBuilder`)

Feature engineering is separated from the agent into a dedicated `DemandFeatureBuilder` class.

### 5.1 Training Features
Constructed from the historical demand DataFrame:

| Feature | Description | Window |
| --- | --- | --- |
| `day_of_week` | Integer 0-6 (Monday=0) | -- |
| `month` | Integer 1-12 | -- |
| `quarter` | Integer 1-4 | -- |
| `rolling_avg_7d` | Rolling mean of `total_quantity` | 7 days |
| `rolling_avg_14d` | Rolling mean of `total_quantity` | 14 days |
| `rolling_avg_30d` | Rolling mean of `total_quantity` | 30 days |
| `rolling_std_7d` | Rolling standard deviation | 7 days |
| `trend_slope` | Linear regression slope over trailing window | 30 days |
| `lag_1` | `total_quantity` at t-1 | -- |
| `lag_7` | `total_quantity` at t-7 | -- |
| `lag_14` | `total_quantity` at t-14 | -- |
| `disruption_active` | Binary: 1 if a disruption overlaps this date | -- |
| `disruption_severity` | Integer severity (1-5) if active, else 0 | -- |

### 5.2 Inference Features
For the forecast horizon (default 14 days), features are constructed by extrapolating the trailing training features forward. Disruption features are set based on whether a disruption's `[start_date, end_date]` overlaps the forecast window.

---

## 6. ML Models

### 6.1 XGBoost Demand Model

**Training** (`DemandXGBoostTrainer`):
- Objective: `reg:squarederror` for point forecast; `reg:quantile` with `alpha=0.05` and `alpha=0.95` for prediction intervals
- Hyperparameters:
  - `n_estimators`: 200
  - `max_depth`: 6
  - `learning_rate`: 0.1
  - `reg_alpha`: 0.1
  - `reg_lambda`: 1.0
  - `random_state`: `XGBOOST_SEED` (42)
- Output: `ModelArtifact` containing serialized model bytes, metadata, training metrics
- Storage: `models/demand/v<version>/xgboost_model.pkl`

**Inference** (`DemandXGBoostInference`):
- Initialized from `ModelArtifact` only (never from raw training data)
- `predict(X) -> np.ndarray`: Point forecasts
- `predict_interval(X, alpha=0.1) -> PredictionInterval`: Lower/upper bounds from quantile models

### 6.2 Statistical Decomposition Model

**Training** (`DemandStatisticalTrainer`):
- Decomposes the demand time-series into:
  - **Trend**: Linear regression on time index
  - **Seasonality**: Day-of-week seasonal dummies (7 coefficients)
  - **Residual**: Observed - trend - seasonal
- Stores trend coefficients, seasonal coefficients, and residual standard deviation as the artifact
- Serves as the "Prophet-style" baseline without the heavy fbprophet C++ dependency

**Inference** (`DemandStatisticalInference`):
- `predict(horizon) -> np.ndarray`: Extrapolates trend + seasonal component
- `predict_interval(horizon, alpha=0.1) -> PredictionInterval`: `forecast +/- z * residual_std`

### 6.3 Ensemble (`DemandEnsemble`)
- Subclasses `BaseEnsemble` from `shared/scof_shared/ml/`
- Registers both models via `register_model()`
- Weights from profile `agents.yaml` (default: `{"xgboost": 0.6, "statistical": 0.4}`)
- Combined forecast: weighted average of point forecasts
- Combined interval: weighted combination of individual intervals
- Agreement score: `1.0 - (|xgboost_forecast - statistical_forecast| / mean_forecast)`, clamped to [0, 1]

---

## 7. Confidence Calibration

Confidence is computed via the shared `ConfidenceCalculator` using a composite formula:

```
confidence = 0.4 * agreement_score
           + 0.3 * (1.0 - interval_width / max_interval_width)
           + 0.3 * (1.0 - clamp(historical_error, 0, 1))
```

| Component | Weight | Source |
| --- | --- | --- |
| Ensemble agreement | 40% | How closely XGBoost and Statistical forecasts align |
| Prediction interval width | 30% | Narrower interval = more confident (normalized by max observed width) |
| Historical validation error | 30% | MAPE on a holdout split of the training data (lower error = more confident) |

The resulting `ConfidenceScore` dataclass exposes each component separately for evidence and reasoning generation.

**Confidence is never clamped or inflated.** If the computed confidence falls below `confidence_floor` (0.60), the `ClaimBuilder` sets `low_confidence=True` on the `StructuredClaim`. The Coordinator (D5) decides whether to ignore or flag the recommendation.

---

## 8. MCP Tool Declarations

Tool declarations are metadata descriptors consumed by the Agent Card. Full MCP protocol wiring occurs in D5.

| Tool Name | Description | Input | Output |
| --- | --- | --- | --- |
| `read_historical_demand` | Read demand time-series for a product over a date range | `{run_id, product_ids, start_date, end_date}` | `DataFrame[date, product_id, total_quantity]` |
| `read_demand_disruptions` | Read disruption events affecting demand or products | `{run_id, scenario_id}` | `List[DisruptionEvent]` |
| `read_product_catalog` | Read product metadata (name, SKU, manufacturer) | `{product_ids}` | `List[ProductInfo]` |

---

## 9. Random Seeds

All random number generation is explicitly seeded for deterministic, reproducible verification:

| Seed | Value | Controls |
| --- | --- | --- |
| `NUMPY_SEED` | 42 | NumPy random state (feature engineering, statistical model) |
| `XGBOOST_SEED` | 42 | XGBoost `random_state` parameter |
| `PYTHON_RANDOM_SEED` | 42 | Python `random` module (any stdlib random usage) |

Seeds are set at agent startup before any model training or inference.

---

## 10. Health Endpoint

`GET /health` returns a rich status object:

```json
{
  "status": "healthy",
  "agent_id": "demand-agent",
  "profile_loaded": true,
  "db_connected": true,
  "neo4j_connected": false,
  "model_loaded": true,
  "model_version": "1.0.0",
  "uptime_seconds": 3421.5
}
```

The Demand Agent does not require Neo4j (it reads from PostgreSQL only), so `neo4j_connected` will be `false` and is not a health failure.

---

## 11. Example Structured Claim Output

```json
{
  "agent_id": "demand-agent",
  "scenario_id": "scenario-001",
  "recommendation": "Increase procurement for prod-101 (Smart IoT Controller) by 35% over the next 14 days to meet projected demand surge.",
  "reasoning": "Demand increased 42% over trailing 14-day window. demand_spike disruption active (severity 4) for prod-101. Ensemble agreement high (0.91). Forecast interval narrow. Historical validation error low (MAPE 8.2%).",
  "confidence": 0.87,
  "low_confidence": false,
  "priority": "HIGH",
  "impact": "Projected demand of 4,200 units over 14 days vs. current run-rate of 3,100 units. Shortfall of ~1,100 units if procurement unchanged.",
  "evidence": [
    {
      "type": "historical_data",
      "source": "scof.purchase_orders + scof.order_items",
      "summary": "14-day trailing demand for prod-101: avg 221 units/day, up from 155 units/day 30 days prior.",
      "reference_id": "order_items:prod-101:2026-07-15:2026-07-29",
      "query_hash": "a3f8c2e1b9d04567..."
    },
    {
      "type": "model_output",
      "source": "DemandEnsemble (XGBoost 0.6, Statistical 0.4)",
      "summary": "14-day point forecast: 4,200 units. 90% prediction interval: [3,800, 4,600]. Agreement score: 0.91.",
      "reference_id": "ensemble:demand:v1.0.0:scenario-001",
      "query_hash": null
    },
    {
      "type": "historical_data",
      "source": "scof.disruption_events",
      "summary": "Active disruption: demand_spike (severity 4) targeting prod-101, started 2026-07-20, ends 2026-08-03.",
      "reference_id": "disruption_event:dis-evt-007",
      "query_hash": "b7e4f1a2c3d89012..."
    }
  ],
  "timestamp": "2026-08-01T16:00:00Z"
}
```

---

## 12. Maps to Source Documents
- **SRS**: Section 3.3 (FR-3.1, FR-3.3), Section 3.4 (Structured Claim Contract)
- **Architecture**: Section 4.2 (Specialist Agent Layer), Section 4.2.1 (Structured Claim Contract), Section 4.2.2 (Agent Specifications -- Demand Agent row)
- **Ideation**: Section 10.4 (Demand Forecast Agent), Section 13.1 (Structured Agent Claims)
- **Implementation Plan**: D3 deliverable definition
