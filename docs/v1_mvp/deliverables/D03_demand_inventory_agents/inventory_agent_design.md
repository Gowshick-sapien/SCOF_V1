# Deliverable D3 — Inventory Agent Architecture & Design Document

## 1. Executive Overview

The **Inventory Agent** (`inventory-agent`) is a specialist AI microservice responsible for monitoring warehouse inventory levels, calculating depletion rates, projecting days of supply, and evaluating stockout risks caused by supply chain disruptions (such as supplier delays). It runs on port `8012` as a FastAPI microservice and returns standard `StructuredClaim` payloads.

---

## 2. Component Architecture & Data Flow

```
[ PostgreSQL (Inventory Levels / Disruptions) ] ---> DataAccess ---> FeatureBuilder
                                                                         |
                                                                         v
[ Ensemble (XGBoost 60% + Statistical 40%) ] <---------------------------+
                               |
                               v
[ ConfidenceCalculator ] ---> ClaimBuilder ---> StructuredClaim (HTTP / JSON)
```

1. **`InventoryDataAccess`**: Queries PostgreSQL for inventory levels (`quantity_on_hand`, `reorder_point`, `safety_stock`) and active supplier disruption events.
2. **`InventoryFeatureBuilder`**: Transforms stock data into feature vectors:
   - Current stock level
   - 7-day rolling depletion rate
   - Projected days of supply
   - Safety stock proximity ($stock - safety\_stock$)
   - Reorder point proximity ($stock - reorder\_point$)
   - Disruption severity exogenous features
3. **`InventoryEnsemble`**: Combines XGBoost Regressor (60%) and Statistical Depletion Model (40%) to project 7-day future stock levels.
4. **Stockout Risk Rule Evaluator**:
   - **Critical Stockout Risk** (Days of supply $\le 5$ days or active supplier delay): Recommends expedited reorders & safety stock rerouting; sets priority to `HIGH`.
   - **Reorder Point Breach** (Days of supply $\le 10$ days): Recommends standard replenishment; sets priority to `MEDIUM`.
   - **Healthy Stock**: Recommends maintaining existing parameters; sets priority to `LOW`.

---

## 3. Protocol & Metadata Endpoints

- **Health Check**: `GET /health`
- **A2A Agent Card**: `GET /.well-known/agent.json`
- **MCP Tool Declarations**:
  - `read_stock_levels`
  - `read_reorder_points`
  - `read_inbound_shipments`
  - `read_inventory_disruptions`

---

## 4. Example Claim Output

```json
{
  "agent_id": "inventory-agent",
  "scenario_id": "scen-electronics-01",
  "recommendation": "Issue expedited purchase reorder and reroute safety stock from alternate warehouse.",
  "reasoning": "Stock level depleting at 22.5 units/day. Days of supply (3.5 days) is critical. Active supplier delay disruption detected for target entity sup-01. Projected 7-day stock is 12.0 units. Model agreement: 0.91.",
  "confidence": 0.815,
  "low_confidence": false,
  "priority": "HIGH",
  "impact": "High risk of stockout within 5 days leading to unfulfilled customer demand.",
  "evidence": [
    {
      "type": "historical_data",
      "source": "PostgreSQL: inventory_levels",
      "summary": "Current stock on hand: 78.8 units. Depletion rate: 22.5 units/day (3.5 days of supply).",
      "reference_id": "inventory_level:scen-electronics-01",
      "query_hash": "e5f6g7h8..."
    },
    {
      "type": "model_output",
      "source": "InventoryEnsemble (XGBoost + Statistical)",
      "summary": "Ensemble projected 7-day stock: 12.0 units. Agreement score: 0.91.",
      "reference_id": "inventory_forecast:scen-electronics-01"
    }
  ]
}
```
