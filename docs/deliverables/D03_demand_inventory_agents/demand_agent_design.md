# Deliverable D3 — Demand Agent Architecture & Design Document

## 1. Executive Overview

The **Demand Forecast Agent** (`demand-agent`) is a specialist AI microservice responsible for generating product-level demand forecasts and analyzing the operational impact of demand spikes or order volatility. It is implemented as a standalone FastAPI microservice running on port `8011` and returns standard `StructuredClaim` responses to downstream coordinator services.

---

## 2. Component Architecture & Data Flow

```
[ PostgreSQL (Order Items / Orders) ] ---> DataAccess ---> FeatureBuilder
                                                               |
                                                               v
[ Ensemble (XGBoost 60% + Statistical 40%) ] <-----------------+
                               |
                               v
[ ConfidenceCalculator ] ---> ClaimBuilder ---> StructuredClaim (HTTP / JSON)
```

1. **`DemandDataAccess`**: Queries PostgreSQL for historical daily order item aggregations and active demand disruption events. Generates SHA-256 `query_hash` for evidence traceability.
2. **`DemandFeatureBuilder`**: Transforms raw time-series records into feature vectors:
   - Day of week (0–6)
   - 7-day, 14-day, 30-day rolling averages
   - Lag-1 and Lag-7 demand
   - Disruption severity exogenous features
3. **`DemandEnsemble`**: Weighted combination of:
   - **XGBoost Regressor** (60% weight): Tree-based gradient boosting model.
   - **Statistical Decomposition Model** (40% weight): Linear trend + weekly day-of-week seasonality.
4. **`ConfidenceCalculator`**: Auditable 40/30/30 composite score based on:
   - Ensemble agreement score (40%)
   - Prediction interval width relative score (30%)
   - Historical validation error score (30%)
5. **`ClaimBuilder`**: Assembles the Pydantic `StructuredClaim` object without clamping raw confidence scores.

---

## 3. Protocol & Metadata Endpoints

- **Health Check**: `GET /health` returns JSON containing `agent_id`, `profile_loaded`, `db_connected`, `neo4j_connected`, `model_loaded`, `model_version`, and `uptime_seconds`.
- **A2A Agent Card**: `GET /.well-known/agent.json` returns self-describing Agent Card metadata:
  ```json
  {
    "agent_id": "demand-agent",
    "name": "Demand Forecast Agent",
    "version": "1.0.0",
    "capabilities": ["demand_forecasting", "trend_analysis", "disruption_impact_assessment"],
    "supported_contexts": ["demand_spike", "baseline_forecast"],
    "protocol": "A2A/1.0",
    "endpoint": "http://localhost:8011"
  }
  ```
- **MCP Tool Declarations**:
  - `read_historical_demand`
  - `read_demand_disruptions`
  - `read_product_catalog`

---

## 4. Example Claim Output

```json
{
  "agent_id": "demand-agent",
  "scenario_id": "scen-electronics-01",
  "recommendation": "Increase production and safety stock buffer by 42% for product allocation.",
  "reasoning": "Demand forecast projects a 42.1% surge over trailing baseline. Active demand spike disruption detected. Forecast ensemble agreement is 0.94.",
  "confidence": 0.842,
  "low_confidence": false,
  "priority": "HIGH",
  "impact": "Potential stockout risk if inventory allocations are not increased by 42%.",
  "evidence": [
    {
      "type": "historical_data",
      "source": "PostgreSQL: order_items",
      "summary": "Historical demand sample over 365 records. Recent average: 120.5 units/day.",
      "reference_id": "demand_history:scen-electronics-01",
      "query_hash": "a1b2c3d4..."
    },
    {
      "type": "model_output",
      "source": "DemandEnsemble (XGBoost + Statistical)",
      "summary": "Ensemble point forecast average: 171.2 units/day. Agreement: 0.94.",
      "reference_id": "ensemble_forecast:scen-electronics-01"
    }
  ]
}
```
