# Deliverable D4 -- Transportation Agent Architecture & Design Document

## 1. Executive Overview

The **Transportation Agent** (`transport-agent`) is a specialist AI microservice responsible for estimating transit delays, evaluating route network risks, and generating optimal rerouting options when logistics disruptions occur. It runs as a standalone FastAPI service on port `8014` and returns standardized `StructuredClaim` responses to downstream coordinator services.

---

## 2. Component Architecture & Data Flow

```
[ Neo4j Route Network ] ----> TransportDataAccess <---- [ PostgreSQL Shipment History ]
                                    |
                                    v
                         TransportFeatureBuilder
                                    |
                                    v
          [ Ensemble (GradientBoosting 60% + RuleScorer 40%) ]
                                    |
                                    v
[ ConfidenceCalculator ] -------> ClaimBuilder -------> StructuredClaim (HTTP / JSON)
```

1. **`TransportDataAccess`**: Queries Neo4j for route network topology, origin-destination paths, and alternate routes using shortest path and route details queries. Queries PostgreSQL for historical shipment records and transit delay distributions. Generates SHA-256 `query_hash` for evidence traceability.
2. **`TransportFeatureBuilder`**: Transforms route network and shipment history data into feature vectors:
   - On-time arrival rate (`on_time_arrival_rate`)
   - Average delay in days (`avg_delay_days`)
   - Maximum delay in days (`max_delay_days`)
   - Route distance in kilometers (`route_distance_km`)
   - Standard transit days (`standard_transit_days`)
   - Alternative route count (`alt_route_count` from Neo4j)
   - Active disruption severity (`disruption_severity`)
3. **`TransportEnsemble`**: Weighted combination of:
   - **GradientBoostingRegressor** (60% weight): ML regression model predicting transit delay magnitude in days.
   - **RouteScorerInference** (40% weight): Rule-based delay estimation engine using statistical parameter thresholds captured during initialization.
4. **Deterministic Route Ranking Criteria**: Rerouting recommendations evaluate alternative paths using a weighted multi-criteria formula:
   $$\text{Route Score} = 0.50 \cdot (1 - \hat{D}) + 0.25 \cdot (1 - \hat{K}) + 0.15 \cdot R_{\text{ontime}} + 0.10 \cdot \left(\frac{1}{H}\right)$$
   where $\hat{D}$ is normalized predicted delay, $\hat{K}$ is normalized route distance, $R_{\text{ontime}}$ is historical on-time arrival rate, and $H$ is path hop count.
5. **ConfidenceCalculator**: Composite 40/30/30 score measuring ensemble agreement, prediction interval width (from residual calibration), and historical validation error.
6. **ClaimBuilder**: Assembles the Pydantic `StructuredClaim` without clamping raw confidence scores.

---

## 3. Protocol & Metadata Endpoints

- **Health Check**: `GET /health` returns JSON containing `agent_id`, `profile_loaded`, `db_connected`, `neo4j_connected`, `model_loaded`, `model_version`, and `uptime_seconds`.
- **A2A Agent Card**: `GET /.well-known/agent.json` returns self-describing Agent Card metadata:
  ```json
  {
    "agent_id": "transport-agent",
    "name": "Transportation Agent",
    "version": "1.0.0",
    "capabilities": ["delay_prediction", "route_risk_assessment", "rerouting_recommendation"],
    "tags": ["transportation", "logistics", "routing"],
    "supported_contexts": ["transport_failure", "adverse_weather", "baseline_assessment"],
    "dependencies": ["postgres", "neo4j"],
    "input_schema": {"context": "ScenarioContext"},
    "output_schema": "StructuredClaim",
    "protocol": "A2A/1.0",
    "endpoint": "http://localhost:8014"
  }
  ```
- **MCP Tool Declarations**:
  - `query_route_network`
  - `estimate_delay`
  - `query_alternative_routes`
  - `read_transport_disruptions`

---

## 4. Example Claim Output

```json
{
  "agent_id": "transport-agent",
  "scenario_id": "scen-electronics-01",
  "recommendation": "Reroute Shenzhen-to-Hong Kong shipments via East Asia Secondary Route (rt-03) using air freight.",
  "reasoning": "Primary sea route rt-01 experiences a predicted delay of 4.5 days due to active transport_failure disruption (severity 3). Alternate air route rt-03 adds $1.20/unit cost but reduces transit delay to 0.5 days.",
  "confidence": 0.824,
  "low_confidence": false,
  "priority": "HIGH",
  "impact": "Reduces total transit delay from 4.5 days to 0.5 days, preventing warehouse stockout breach.",
  "evidence": [
    {
      "type": "graph_query",
      "source": "Neo4j: (Route {id: 'rt-01'})-[:DELIVERS_TO]->(Warehouse)",
      "summary": "Shortest path and alternate route query returned 2 viable alternative routes for origin mfg-01 to wh-01.",
      "reference_id": "route_network:rt-01",
      "query_hash": "d4e5f6a1..."
    },
    {
      "type": "historical_data",
      "source": "PostgreSQL: shipments & routes",
      "summary": "Historical shipment analysis over 60 records. Primary route historical delay avg: 0.8 days.",
      "reference_id": "shipment_history:rt-01",
      "query_hash": "e5f6a1b2..."
    },
    {
      "type": "model_output",
      "source": "TransportEnsemble (GradientBoosting + RouteScorer)",
      "summary": "Predicted delay on primary route rt-01: 4.5 days (+/- 0.8). Agreement score: 0.90.",
      "reference_id": "delay_ensemble:scen-electronics-01"
    }
  ]
}
```
