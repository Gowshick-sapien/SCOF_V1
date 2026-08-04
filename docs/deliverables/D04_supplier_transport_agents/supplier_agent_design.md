# Deliverable D4 -- Supplier Intelligence Agent Architecture & Design Document

## 1. Executive Overview

The **Supplier Intelligence Agent** (`supplier-agent`) is a specialist AI microservice responsible for scoring vendor reliability, predicting supplier failures, and recommending alternate supply options when disruptions occur. It runs as a standalone FastAPI service on port `8013` and returns standardized `StructuredClaim` responses to downstream coordinator services.

---

## 2. Component Architecture & Data Flow

```
[ Neo4j Graph ] ------> SupplierDataAccess <------ [ PostgreSQL Delivery History ]
                             |
                             v
                   SupplierFeatureBuilder
                             |
                             v
          [ Ensemble (GradientBoosting 60% + RuleScorer 40%) ]
                             |
                             v
[ ConfidenceCalculator ] --> ClaimBuilder --> StructuredClaim (HTTP / JSON)
```

1. **`SupplierDataAccess`**: Queries Neo4j for supplier lineage, product-supplier relationships, and alternate suppliers. Queries PostgreSQL for historical purchase orders and shipment delivery metrics. Generates SHA-256 `query_hash` for evidence traceability.
2. **`SupplierFeatureBuilder`**: Constructs feature matrix from combined graph and tabular data:
   - On-time delivery rate (`on_time_delivery_rate`)
   - Average delay in days (`avg_delay_days`)
   - Maximum delay in days (`max_delay_days`)
   - Order fulfillment rate (`order_fulfillment_rate`)
   - Alternate supplier count (`alternate_supplier_count` from Neo4j)
   - Supply chain hop count (`supply_chain_hop_count` from Neo4j shortest path)
   - Lead time reliability standard deviation (`lead_time_reliability`)
   - Active disruption severity (`disruption_severity`)
3. **`SupplierEnsemble`**: Weighted combination of:
   - **GradientBoostingClassifier** (60% weight): ML classification model predicting supplier reliability score based on historical performance.
   - **RuleScorerInference** (40% weight): Rule-based scoring engine using statistical parameter thresholds captured during initialization.
4. **Deterministic Alternate Supplier Ranking**: Reroutes and alternate vendor selections use a weighted multi-criteria formula:
   $$\text{Rank Score} = 0.40 \cdot S_{\text{rel}} + 0.30 \cdot (1 - \hat{L}) + 0.20 \cdot (1 - \hat{C}) + 0.10 \cdot \left(\frac{1}{H}\right)$$
   where $S_{\text{rel}}$ is supplier reliability, $\hat{L}$ is normalized lead time, $\hat{C}$ is normalized unit cost, and $H$ is supply chain hop count.
5. **ConfidenceCalculator**: Composite 40/30/30 score measuring ensemble agreement, prediction interval width (from residual calibration), and historical validation error.
6. **ClaimBuilder**: Assembles the Pydantic `StructuredClaim` without clamping raw confidence scores.

---

## 3. Protocol & Metadata Endpoints

- **Health Check**: `GET /health` returns JSON containing `agent_id`, `profile_loaded`, `db_connected`, `neo4j_connected`, `model_loaded`, `model_version`, and `uptime_seconds`.
- **A2A Agent Card**: `GET /.well-known/agent.json` returns self-describing Agent Card metadata:
  ```json
  {
    "agent_id": "supplier-agent",
    "name": "Supplier Intelligence Agent",
    "version": "1.0.0",
    "capabilities": ["supplier_reliability_scoring", "failure_prediction", "alternate_supplier_recommendation"],
    "tags": ["supplier", "reliability", "graph"],
    "supported_contexts": ["supplier_delay", "baseline_assessment"],
    "dependencies": ["postgres", "neo4j"],
    "input_schema": {"context": "ScenarioContext"},
    "output_schema": "StructuredClaim",
    "protocol": "A2A/1.0",
    "endpoint": "http://localhost:8013"
  }
  ```
- **MCP Tool Declarations**:
  - `query_supplier_graph`
  - `read_delivery_history`
  - `query_alternate_suppliers`
  - `read_supplier_disruptions`

---

## 4. Example Claim Output

```json
{
  "agent_id": "supplier-agent",
  "scenario_id": "scen-electronics-01",
  "recommendation": "Shift 60% order volume from MicroBattery Global (sup-02) to alternate supplier Semico Components (sup-01).",
  "reasoning": "Primary supplier MicroBattery Global (sup-02) reliability score dropped to 0.42 due to an active supplier delay disruption (severity 4). Alternate supplier Semico Components (sup-01) exhibits 0.94 reliability with 7-day lead time.",
  "confidence": 0.865,
  "low_confidence": false,
  "priority": "HIGH",
  "impact": "Prevented downstream assembly line shutdown by securing alternate battery cell supply within 48 hours.",
  "evidence": [
    {
      "type": "graph_query",
      "source": "Neo4j: (Supplier {id: 'sup-02'})-[:SUPPLIES]->(Product)",
      "summary": "Upstream lineage graph query returned 2 alternate suppliers for product prod-101.",
      "reference_id": "supplier_graph:sup-02",
      "query_hash": "b2c3d4e5..."
    },
    {
      "type": "historical_data",
      "source": "PostgreSQL: purchase_orders & shipments",
      "summary": "Historical delivery sample of 45 orders for sup-02. On-time delivery rate: 58.2%, avg delay: 4.2 days.",
      "reference_id": "delivery_history:sup-02",
      "query_hash": "c3d4e5f6..."
    },
    {
      "type": "model_output",
      "source": "SupplierEnsemble (GradientBoosting + RuleScorer)",
      "summary": "Ensemble reliability score: 0.42 for sup-02 vs 0.94 for alternate sup-01. Agreement score: 0.92.",
      "reference_id": "reliability_ensemble:scen-electronics-01"
    }
  ]
}
```
