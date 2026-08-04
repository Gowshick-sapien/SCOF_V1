# Deliverable D4 Implementation Plan -- Reliability Agent Slice: Supplier + Transportation

## Goal Description

Deliverable D4 builds the two **network/reliability-focused specialist agents** as standalone, independently testable FastAPI services conforming to the universal Structured Claim contract. Unlike D3's time-series forecasting agents, D4 agents are **graph-centric** -- they query Neo4j for supplier relationships, route networks, and alternate paths, combined with PostgreSQL delivery history data to produce reliability scores, failure predictions, delay estimates, and rerouting options.

D4 delivers:

1. **Supplier Intelligence Agent** (`services/agents/supplier/`) -- a reliability scoring and supplier failure prediction service that queries the Neo4j supplier graph and PostgreSQL delivery history to assess vendor risk, compute reliability scores, and recommend supply chain mitigations.
2. **Transportation Agent** (`services/agents/transportation/`) -- a delay prediction and rerouting recommendation service that queries the Neo4j route network and PostgreSQL shipment history to estimate transit delays and propose alternative routing options.
3. **Profile Extensions** -- Both agents read configuration (confidence floor, port, MCP tools) from `agents.yaml`. D4 adds `mcp_tools` and optional agent-specific configuration to the existing supplier-agent and transport-agent entries.
4. **Model Artifact Storage** -- Versioned model artifact directories at `models/supplier/` and `models/transportation/`.
5. **Verification Script** (`scripts/verify_d4.py`) -- callable via `make verify-d4`, deterministic via explicit random seeds, validates both agents against D1 synthetic disruption scenarios.

---

## Prerequisites Check

> [!NOTE]
> - **Prerequisite Deliverables**: D1 (Simulation Environment) and D2 (Knowledge & Data Layer) are complete. PostgreSQL contains synthetic `suppliers`, `supplier_products`, `purchase_orders`, `shipments`, `routes`, and `disruption_events` tables. Neo4j contains the supply chain graph with Supplier, Product, Warehouse, Route nodes and relationships.
> - **D3 Shared Infrastructure**: `shared/scof_shared/schemas/` (StructuredClaim, EvidenceItem, AgentCard, ScenarioContext), `shared/scof_shared/ml/` (BaseEnsemble, ConfidenceCalculator, BaseTrainer, BaseInferenceModel), and `shared/scof_shared/agent_base/` (BaseAgent, ClaimBuilder) are operational and tested.
> - **Neo4j Graph Client**: `shared/scof_shared/knowledge/graph_client.py` (Neo4jGraphClient) provides `get_upstream_supplier_lineage()`, `get_alternate_suppliers()`, `get_shortest_path()`, `get_route_details()`, and generic `execute_read()` -- all required by D4 agents.
> - **Domain Profile**: [profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml) already contains skeleton entries for `supplier-agent` (port 8013, confidence_floor 0.55) and `transport-agent` (port 8014, confidence_floor 0.50).
> - **Infrastructure**: Docker Compose services (Postgres, Neo4j, Redis, Kafka) are running and healthy.

---

## User Review Required

> [!IMPORTANT]
> **Key Design Decisions**:
>
> 1. **Model Architecture Difference from D3**: D3 agents use time-series ensembles (XGBoost + Statistical). D4 agents operate on **graph-structured + tabular delivery history data**, not pure time-series. The Supplier Agent uses a **scikit-learn GradientBoostingClassifier** trained on delivery performance features to predict failure probability, combined with a **rule-based reliability scorer** using Neo4j graph topology features. The Transportation Agent uses a **GradientBoostingRegressor** for delay magnitude prediction combined with a **graph-based rerouting engine** that queries Neo4j for alternative paths. Both still produce `EnsembleResult` via the shared `BaseEnsemble` framework for confidence calculation consistency.
>
> 2. **Neo4j as Primary Data Source**: Unlike D3 agents that primarily use PostgreSQL, D4 agents heavily rely on the Neo4j graph for supplier relationships (`get_upstream_supplier_lineage`, `get_alternate_suppliers`) and route network queries (`get_shortest_path`, `get_route_details`). PostgreSQL provides complementary historical delivery/shipment records. The `Neo4jGraphClient` from `shared/scof_shared/knowledge/` is used directly -- same pattern as D3's PostgreSQL data access but for graph queries. **No graph centrality metrics** (PageRank, betweenness, closeness) are used -- the existing `Neo4jGraphClient` API does not expose centrality computation and D2 does not pre-compute it. All graph-derived features use only the existing API: lineage queries, alternate supplier lookups, shortest path, and route details.
>
> 3. **MCP Implementation Scope**: Same as D3 -- D4 declares MCP tool definitions (schema + capability descriptions) for each agent's data access, but full MCP server wiring is completed in D5. In D4, agents call their data sources through the shared knowledge library directly.
>
> 4. **Confidence Calculation**: Both D4 agents reuse the shared `ConfidenceCalculator` (40/30/30 formula) from `shared/scof_shared/ml/confidence.py`. The "ensemble agreement" component measures agreement between the ML model prediction and the rule-based scorer. The "interval width" maps to prediction uncertainty. The "historical error" maps to validation error on the delivery history holdout set.
>
> 5. **Prediction Intervals for GradientBoosting**: Scikit-learn's GradientBoosting models do not natively produce prediction intervals. D4 uses **residual calibration** (same approach as D3's XGBoost models): during `fit()`, compute `residual_std = std(y_true - y_pred)` on training data, then during `predict_interval()`, apply `point_forecast +/- z * residual_std` where `z` is the normal quantile for the requested alpha (e.g., z=1.645 for alpha=0.1). This is identical to the technique in [xgboost_model.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/src/models/xgboost_model.py#L60-L66).
>
> 6. **Fallback Mock Data**: Following the D3 pattern, both D4 data access classes include fallback mock data generation when Neo4j/PostgreSQL connections are unavailable, enabling offline unit testing without running infrastructure. **Graph mock data must simulate realistic topology**: at least 3 suppliers per product (enabling alternate lookups), 2+ routes between origin-destination pairs, at least one supplier with no alternates (disconnected node case), and at least one route cycle (A->B->C->A) to exercise graph traversal robustness.
>
> 7. **Ensemble Weight Tuning**: Default weights (0.6 ML model / 0.4 rule scorer) are read from `agents.yaml` and are sufficient for MVP. Post-MVP, weights can be tuned via cross-validated evaluation against D1 ground truth -- this is noted as a D10 extension point but is not in scope for D4 implementation.

---

## Open Questions

> [!NOTE]
> **ScenarioContext Extension**: The existing `ScenarioContext` schema already includes `disruption_type`, `target_entity_type`, `target_entity_id`, and `severity` fields -- sufficient for D4 agents to receive supplier_delay and transport_failure disruption contexts. No schema changes needed.
>
> **Route Network Topology**: The D4 Transportation Agent queries Neo4j for alternative routes. The existing `Neo4jGraphClient.get_shortest_path()` and `get_route_details()` methods provide the required graph traversal. If the route graph is sparse (few alternate paths), the agent still produces a valid claim with reduced rerouting options and appropriate confidence scoring.

---

## Proposed Changes

### Supplier Agent Service (`services/agents/supplier/`)

The Supplier Intelligence Agent assesses vendor reliability and predicts supplier failures by combining Neo4j graph topology features (supplier relationships, alternate availability, lead time patterns) with PostgreSQL delivery performance history (on-time rate, delay frequency, order fulfillment).

#### [NEW] [pyproject.toml](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/pyproject.toml)
- Package manifest declaring dependencies: `fastapi`, `uvicorn`, `scikit-learn`, `numpy`, `pandas`, `psycopg[binary]`, `neo4j`, `pydantic>=2.0`, `pyyaml`, `scof-shared`.
- Build system: setuptools.
- Pytest configuration with `testpaths = ["tests"]`.

#### [NEW] [Dockerfile](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/Dockerfile)
- Python 3.11-slim based container. Installs `scof-shared` from local path. Exposes port 8013. Entrypoint: `uvicorn src.main:app --host 0.0.0.0 --port 8013`.
- Same COPY and install pattern as `services/agents/demand/Dockerfile`.

#### [NEW] [src/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/__init__.py)
- Package marker.

#### [NEW] [src/config.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/config.py)
- Agent-specific configuration: `AGENT_ID = "supplier-agent"`, `AGENT_NAME = "Supplier Intelligence Agent"`, `DEFAULT_PORT = 8013`.
- Database connection parameters from environment (Postgres + Neo4j).
- Profile path from `SCOF_PROFILE_PATH`.
- Model artifact directory: `MODEL_ARTIFACT_DIR = Path("models/supplier")`.
- Random seeds: `NUMPY_SEED = 42`, `SKLEARN_SEED = 42`, `PYTHON_RANDOM_SEED = 42`.
- Reliability thresholds: `HIGH_RELIABILITY_THRESHOLD = 0.85`, `LOW_RELIABILITY_THRESHOLD = 0.50`.

#### [NEW] [src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/main.py)
- FastAPI application with same endpoint pattern as D3 agents:
  - `POST /analyze` -- accepts `ScenarioContext`, returns `StructuredClaim`.
  - `GET /health` -- rich health endpoint returning `agent_id`, `profile_loaded`, `db_connected`, `neo4j_connected`, `model_loaded`, `model_version`, `uptime_seconds`.
  - `GET /.well-known/agent.json` -- returns A2A `AgentCard`.
- Lifespan context manager initializes `SupplierAgent` with profile path and DB configs.

#### [NEW] [src/agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/agent.py)
- `SupplierAgent(BaseAgent)` class.
- Pipeline architecture (adapted from D3 for graph + tabular data):
  1. **DataAccess** -- fetches supplier delivery history from PostgreSQL + supplier graph topology from Neo4j.
  2. **FeatureBuilder** -- constructs reliability features: on-time delivery rate, average delay days, order fulfillment rate, alternate supplier count, supply chain hop count (from Neo4j shortest path), disruption severity features.
  3. **InferenceModel** (via ensemble) -- produces reliability scores and failure probability predictions.
  4. **ClaimBuilder** -- constructs StructuredClaim with reasoning referencing specific suppliers, reliability scores, and graph-based evidence.
- `analyze(context: ScenarioContext) -> StructuredClaim`:
  - Queries delivery history for the target supplier (or all suppliers if no target).
  - Queries Neo4j for supplier relationships, alternates, and supply chain paths.
  - Builds features, runs ensemble, constructs claim.
  - For `supplier_delay` disruptions: recommends switching to alternate suppliers ranked by a deterministic composite score, cites reliability scores.
  - **Alternate Supplier Ranking**: When recommending alternates, suppliers are ranked by a deterministic composite score: `0.40 * reliability_score + 0.30 * (1.0 - normalized_lead_time) + 0.20 * (1.0 - normalized_unit_cost) + 0.10 * (1.0 / hop_count)`. This prioritizes reliability first, then shorter lead time, then lower cost, then graph proximity. Ranking is deterministic given the same input data.
  - For baseline scenarios: reports overall supplier health assessment.
- `get_agent_card()`: Returns AgentCard with capabilities `["supplier_reliability_scoring", "failure_prediction", "alternate_supplier_recommendation"]`, tags `["supplier", "reliability", "graph"]`, supported_contexts `["supplier_delay", "baseline_assessment"]`.

#### [NEW] [src/data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/data_access.py)
- `SupplierDataAccess` class wrapping both PostgreSQL and Neo4j queries:
  - `get_supplier_delivery_history(run_id, supplier_ids) -> Tuple[pd.DataFrame, str]` -- joins `purchase_orders` with `shipments` for delivery performance metrics. Returns query hash.
  - `get_supplier_disruptions(run_id, scenario_id) -> Tuple[List[dict], str]` -- fetches disruption events targeting suppliers.
  - `get_supplier_graph_data(supplier_id, product_id) -> Tuple[List[dict], str]` -- uses `Neo4jGraphClient.get_upstream_supplier_lineage()` to fetch supplier-product-warehouse relationships.
  - `get_alternate_suppliers(supplier_id, product_id) -> Tuple[List[dict], str]` -- uses `Neo4jGraphClient.get_alternate_suppliers()` to find backup vendor options.
- Each method returns both result and query_hash for evidence traceability.
- **Fallback mock data** for offline testing. Graph mocks simulate: 5 suppliers (matching topology.yaml), 3 products, 2+ alternate suppliers per product, 1 supplier with zero alternates (disconnected node), supplier-to-warehouse paths of varying hop counts. PostgreSQL mocks generate synthetic delivery records with a mix of on-time and delayed deliveries per supplier reliability profile.

#### [NEW] [src/features.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/features.py)
- `SupplierFeatureBuilder` class:
  - `build_features(delivery_df, graph_data, disruptions, alternates) -> Tuple[np.ndarray, np.ndarray, List[str]]`:
    - `on_time_delivery_rate` -- percentage of orders delivered on or before expected date.
    - `avg_delay_days` -- mean delay in days across all deliveries.
    - `max_delay_days` -- worst-case delay observed.
    - `order_fulfillment_rate` -- percentage of orders with status 'DELIVERED' vs total.
    - `alternate_supplier_count` -- number of alternate suppliers available (from `Neo4jGraphClient.get_alternate_suppliers()`).
    - `supply_chain_hop_count` -- number of hops in shortest path from supplier to destination warehouse (from `Neo4jGraphClient.get_shortest_path()`). Proxy for supply chain complexity without requiring centrality computation.
    - `lead_time_reliability` -- actual vs expected lead time consistency (std deviation of `actual_delivery_date - expected_delivery_date`).
    - `disruption_severity` -- exogenous feature if active disruption targets this supplier.
  - Target variable `y`: binary label for "failure" (1 if on-time rate < threshold, 0 otherwise) for classifier training.
  - **No graph centrality features**: all graph-derived features use existing `Neo4jGraphClient` methods (lineage, alternates, shortest path). No PageRank, betweenness, or closeness centrality is computed.

#### [NEW] [src/mcp/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/mcp/__init__.py)
- Package marker.

#### [NEW] [src/mcp/tools.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/mcp/tools.py)
- MCP tool declarations as `MCPToolDescriptor` dataclass descriptors (same pattern as D3):
  - `query_supplier_graph` -- queries Neo4j for supplier-product-warehouse relationships.
  - `read_delivery_history` -- reads historical delivery performance data from PostgreSQL.
  - `query_alternate_suppliers` -- queries Neo4j for alternate supplier options.
  - `read_supplier_disruptions` -- reads disruption events targeting suppliers.

#### [NEW] [src/models/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/__init__.py)
- Package marker.

#### [NEW] [src/models/reliability_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/reliability_scorer.py)
- `ReliabilityScorerTrainer(BaseTrainer)`:
  - `fit(X_train, y_train) -> ModelArtifact` -- trains a scikit-learn `GradientBoostingClassifier` on delivery performance features. Hyperparameters: `n_estimators=100`, `max_depth=4`, `learning_rate=0.1`, `random_state=SKLEARN_SEED`.
  - During `fit()`, computes `residual_std = std(y_true - predict_proba(X_train)[:, 1])` and stores it in `training_metadata["residual_std"]` for interval estimation.
- `ReliabilityScorerInference(BaseInferenceModel)`:
  - `predict(X) -> np.ndarray` -- returns reliability scores (1.0 - failure_probability) for each supplier, using `predict_proba()[:, 1]`.
  - `predict_interval(X, alpha=0.1) -> PredictionInterval` -- **residual calibration method**: `score +/- z * residual_std` where `z` is the normal quantile for the requested alpha (z=1.645 for alpha=0.1), clamped to [0.0, 1.0]. Same technique as D3's XGBoost interval estimation.

#### [NEW] [src/models/rule_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/rule_scorer.py)
- `RuleScorerInitializer(BaseTrainer)`:
  - `fit(X_train, y_train) -> ModelArtifact` -- captures feature statistics (per-feature mean, std, min, max) and stores them as serialized parameters. This is a **statistics-capture step**, not ML training -- the naming uses `BaseTrainer` interface for API consistency with the ensemble framework, but the operation is deterministic aggregation of feature distributions.
- `RuleScorerInference(BaseInferenceModel)`:
  - `predict(X) -> np.ndarray` -- computes rule-based reliability scores:
    - Weighted composite of on-time rate (40%), fulfillment rate (30%), lead time consistency (20%), alternate availability (10%).
  - `predict_interval(X, alpha) -> PredictionInterval` -- `score +/- z * feature_variance` where `feature_variance` is the standard deviation of the weighted composite across the captured training statistics.
- Serves as the "rule-based baseline" counterpart to the ML classifier (same architectural role as `DemandStatisticalModel` in D3). The class is named `RuleScorerInitializer` rather than `RuleScorerTrainer` to clarify that no gradient-based learning occurs -- it captures distributional statistics for threshold-based scoring.

#### [NEW] [src/models/ensemble.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/ensemble.py)
- `SupplierEnsemble(BaseEnsemble)`:
  - Registers `ReliabilityScorerInference` and `RuleScorerInference` as models.
  - Weights from profile `agents.yaml` (default: `{"reliability_scorer": 0.6, "rule_scorer": 0.4}`).
  - Inherits `predict() -> EnsembleResult` from `BaseEnsemble`.

---

### Transportation Agent Service (`services/agents/transportation/`)

The Transportation Agent predicts transit delays and generates rerouting recommendations by combining Neo4j route network topology with PostgreSQL shipment history data.

#### [NEW] [pyproject.toml](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/pyproject.toml)
- Same dependency set as Supplier Agent: `fastapi`, `uvicorn`, `scikit-learn`, `numpy`, `pandas`, `psycopg[binary]`, `neo4j`, `pydantic>=2.0`, `pyyaml`, `scof-shared`.

#### [NEW] [Dockerfile](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/Dockerfile)
- Python 3.11-slim. Exposes port 8014. Entrypoint: `uvicorn src.main:app --host 0.0.0.0 --port 8014`.

#### [NEW] [src/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/__init__.py)
- Package marker.

#### [NEW] [src/config.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/config.py)
- Agent-specific configuration: `AGENT_ID = "transport-agent"`, `AGENT_NAME = "Transportation Agent"`, `DEFAULT_PORT = 8014`.
- Database connections (Postgres + Neo4j), profile path, model artifact directory.
- Random seeds: `NUMPY_SEED = 42`, `SKLEARN_SEED = 42`, `PYTHON_RANDOM_SEED = 42`.
- Delay thresholds: `CRITICAL_DELAY_DAYS = 5`, `WARNING_DELAY_DAYS = 2`.

#### [NEW] [src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/main.py)
- FastAPI application with same endpoint pattern:
  - `POST /analyze`, `GET /health`, `GET /.well-known/agent.json`.

#### [NEW] [src/agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/agent.py)
- `TransportAgent(BaseAgent)` class.
- Pipeline architecture:
  1. **DataAccess** -- fetches shipment history from PostgreSQL + route network from Neo4j.
  2. **FeatureBuilder** -- constructs delay prediction features: historical delay rate per route, average transit time deviation, route distance, transport mode, disruption severity, alternative route count.
  3. **InferenceModel** (via ensemble) -- predicts delay magnitude and identifies rerouting options.
  4. **ClaimBuilder** -- constructs StructuredClaim with reasoning referencing specific routes, predicted delays, and rerouting alternatives.
- `analyze(context: ScenarioContext) -> StructuredClaim`:
  - For `transport_failure` disruptions: queries the affected route, predicts delay magnitude, queries Neo4j for alternative routes, ranks alternatives and recommends rerouting.
  - **Route Ranking Criteria**: When recommending alternative routes, candidates are ranked by a deterministic composite score: `0.50 * (1.0 - normalized_predicted_delay) + 0.25 * (1.0 - normalized_distance_km) + 0.15 * historical_on_time_rate + 0.10 * (1.0 / hop_count)`. This prioritizes lowest predicted delay first, then shortest distance, then historical reliability, then fewest hops. Ranking is deterministic given the same input data.
  - For `adverse_weather` disruptions: same delay analysis and rerouting logic, reasoning references weather-related impact.
  - For baseline: reports route network health assessment.
- `get_agent_card()`: Returns AgentCard with capabilities `["delay_prediction", "route_risk_assessment", "rerouting_recommendation"]`, tags `["transportation", "logistics", "routing"]`, supported_contexts `["transport_failure", "adverse_weather", "baseline_assessment"]`.

#### [NEW] [src/data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/data_access.py)
- `TransportDataAccess` class:
  - `get_shipment_history(run_id, route_ids) -> Tuple[pd.DataFrame, str]` -- joins `shipments` with `routes` for transit performance metrics. Returns query hash.
  - `get_route_disruptions(run_id, scenario_id) -> Tuple[List[dict], str]` -- fetches disruption events targeting routes.
  - `get_route_network(route_id) -> Tuple[List[dict], str]` -- uses `Neo4jGraphClient.get_route_details()`.
  - `get_alternative_routes(origin_id, destination_id) -> Tuple[List[dict], str]` -- queries Neo4j for alternative paths between origin and destination.
- **Fallback mock data** for offline testing. Graph mocks simulate: 4+ routes between origin-destination pairs with varying distances and transit times, at least 1 origin-destination pair with only a single route (no alternates), 1 route cycle (A->B->C->A path) to test graph traversal, and routes with different transport modes (sea, air, land). PostgreSQL mocks generate synthetic shipment records with a mix of on-time and delayed arrivals per route.

#### [NEW] [src/features.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/features.py)
- `TransportFeatureBuilder` class:
  - `build_features(shipment_df, route_data, disruptions, alt_routes) -> Tuple[np.ndarray, np.ndarray, List[str]]`:
    - `on_time_arrival_rate` -- percentage of shipments arriving on or before estimated arrival.
    - `avg_delay_days` -- mean delay across all shipments on this route.
    - `max_delay_days` -- worst-case delay observed.
    - `route_distance_km` -- route distance from graph data.
    - `standard_transit_days` -- expected transit time from route definition.
    - `alt_route_count` -- number of alternative routes available.
    - `disruption_severity` -- exogenous feature if active disruption targets this route.
  - Target variable `y`: actual delay in days (regression target) for delay predictor training.

#### [NEW] [src/mcp/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/mcp/__init__.py)
- Package marker.

#### [NEW] [src/mcp/tools.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/mcp/tools.py)
- MCP tool declarations:
  - `query_route_network` -- queries Neo4j for route topology and details.
  - `estimate_delay` -- reads shipment history for delay estimation.
  - `query_alternative_routes` -- queries Neo4j for alternative routing options.
  - `read_transport_disruptions` -- reads disruption events targeting routes.

#### [NEW] [src/models/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/__init__.py)
- Package marker.

#### [NEW] [src/models/delay_predictor.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/delay_predictor.py)
- `DelayPredictorTrainer(BaseTrainer)`:
  - `fit(X_train, y_train) -> ModelArtifact` -- trains a scikit-learn `GradientBoostingRegressor` on shipment performance features. Hyperparameters: `n_estimators=100`, `max_depth=4`, `learning_rate=0.1`, `random_state=SKLEARN_SEED`.
  - During `fit()`, computes `residual_std = std(y_true - model.predict(X_train))` and stores it in `training_metadata["residual_std"]` for interval estimation.
- `DelayPredictorInference(BaseInferenceModel)`:
  - `predict(X) -> np.ndarray` -- returns predicted delay days (0 = on-time, positive = delayed), clamped to `max(0, prediction)`.
  - `predict_interval(X, alpha=0.1) -> PredictionInterval` -- **residual calibration method**: `prediction +/- z * residual_std` where `z` is the normal quantile for alpha (z=1.645 for alpha=0.1), lower bound clamped to 0. Same technique as D3's XGBoost and the Supplier Agent's reliability scorer.

#### [NEW] [src/models/route_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/route_scorer.py)
- `RouteScorerInitializer(BaseTrainer)`:
  - `fit(X_train, y_train) -> ModelArtifact` -- captures route performance statistics (per-feature mean, std, delay distribution percentiles) and stores as serialized parameters. Same as the Supplier Agent's `RuleScorerInitializer` -- a **statistics-capture step**, not ML training. Uses `BaseTrainer` interface for ensemble framework API consistency.
- `RouteScorerInference(BaseInferenceModel)`:
  - `predict(X) -> np.ndarray` -- rule-based delay estimates:
    - Weighted composite of historical on-time rate (40%), route distance factor (25%), mode reliability indicator (20%), disruption severity impact (15%).
  - `predict_interval(X, alpha) -> PredictionInterval` -- `estimate +/- z * route_delay_std` where `route_delay_std` is the standard deviation of delay observations captured during initialization.

#### [NEW] [src/models/ensemble.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/ensemble.py)
- `TransportEnsemble(BaseEnsemble)`:
  - Registers `DelayPredictorInference` and `RouteScorerInference`.
  - Weights from profile (default: `{"delay_predictor": 0.6, "route_scorer": 0.4}`).

---

### Model Artifact Storage

#### [NEW] models/supplier/.gitkeep
#### [NEW] models/transportation/.gitkeep
- Versioned model artifact directories at the repository root.
- Same pattern as `models/demand/` and `models/inventory/`.

---

### Profile Extension

#### [MODIFY] [agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml)
- Add `mcp_tools` and `ensemble_weights` to the existing `supplier-agent` and `transport-agent` entries:

```yaml
  - id: "supplier-agent"
    name: "Supplier Intelligence Agent"
    port: 8013
    confidence_floor: 0.55
    ensemble_weights:
      reliability_scorer: 0.6
      rule_scorer: 0.4
    mcp_tools:
      - query_supplier_graph
      - read_delivery_history
      - query_alternate_suppliers
      - read_supplier_disruptions

  - id: "transport-agent"
    name: "Transportation Agent"
    port: 8014
    confidence_floor: 0.50
    ensemble_weights:
      delay_predictor: 0.6
      route_scorer: 0.4
    mcp_tools:
      - query_route_network
      - estimate_delay
      - query_alternative_routes
      - read_transport_disruptions
```

---

### Docker Compose Extension

#### [MODIFY] [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml)
- Add `supplier-agent` service:
  - Build context: `.`, Dockerfile: `services/agents/supplier/Dockerfile`
  - Container name: `scof-supplier-agent`
  - Depends on: `postgres` (healthy), `neo4j` (healthy)
  - Environment: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `NEO4J_URI=bolt://neo4j:7687`, `NEO4J_USER`, `NEO4J_PASSWORD`, `SCOF_PROFILE_PATH=/app/profiles/mvp-electronics`, `NUMPY_SEED=42`, `SKLEARN_SEED=42`
  - Volumes: `./profiles:/app/profiles:ro`, `./models/supplier:/app/models:rw`
  - Port: `8013:8013`
- Add `transport-agent` service:
  - Same pattern, port `8014:8014`, container name `scof-transport-agent`, models volume: `./models/transportation:/app/models:rw`

---

### Verification & Tests

#### [NEW] [scripts/verify_d4.py](file:///d:/projects/SCOF_V1/SCOF/scripts/verify_d4.py)
- Comprehensive verification script (mirrors `verify_d3.py` structure):
  1. **Connectivity**: HTTP health check on both agent endpoints (8013, 8014), validate rich health response.
  2. **Agent Card Validation**: Fetch `/.well-known/agent.json` from each agent, validate against `AgentCard` schema.
  3. **Structured Claim Compliance**: Send a `ScenarioContext` with `disruption_type="supplier_delay"` to the Supplier Agent and `disruption_type="transport_failure"` to the Transportation Agent. Validate responses against `StructuredClaim` schema.
  4. **Confidence Integrity**: Assert `0.0 <= claim.confidence <= 1.0`. Verify `low_confidence` flag logic.
  5. **Evidence Traceability**: Assert evidence items have non-empty `reference_id` and valid `source`.
  6. **Disruption Response** (Supplier Agent): Inject a `supplier_delay` disruption targeting `sup-02`, verify reasoning mentions the delay and recommends alternate suppliers.
  7. **Rerouting Response** (Transport Agent): Inject a `transport_failure` disruption, verify reasoning mentions route alternatives.
  8. **Determinism**: Call each agent twice with identical inputs and seeds, verify identical claims.

#### [MODIFY] [Makefile](file:///d:/projects/SCOF_V1/SCOF/Makefile)
- Add target `verify-d4: python scripts/verify_d4.py`.

#### [NEW] [services/agents/supplier/tests/test_supplier_agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_supplier_agent.py)
- Unit tests for `SupplierAgent.analyze()` with mocked data access. Verifies claim structure, reasoning content, confidence computation, evidence traceability.

#### [NEW] [services/agents/supplier/tests/test_reliability_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_reliability_scorer.py)
- Unit tests for `ReliabilityScorerTrainer/Inference`: fit on synthetic delivery data, verify predictions in [0, 1] range, interval validity.

#### [NEW] [services/agents/supplier/tests/test_supplier_features.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_supplier_features.py)
- Unit tests for `SupplierFeatureBuilder`: on-time rate computation, delay aggregation, alternate count integration.

#### [NEW] [services/agents/supplier/tests/test_supplier_data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_supplier_data_access.py)
- Unit tests for `SupplierDataAccess` with fallback mock data. Verifies query_hash generation.

#### [NEW] [services/agents/transportation/tests/test_transport_agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_transport_agent.py)
- Unit tests for `TransportAgent.analyze()`.

#### [NEW] [services/agents/transportation/tests/test_delay_predictor.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_delay_predictor.py)
- Unit tests for `DelayPredictorTrainer/Inference`: fit on synthetic shipment data, delay predictions non-negative, interval validity.

#### [NEW] [services/agents/transportation/tests/test_transport_features.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_transport_features.py)
- Unit tests for `TransportFeatureBuilder`.

#### [NEW] [services/agents/transportation/tests/test_transport_data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_transport_data_access.py)
- Unit tests for `TransportDataAccess` with fallback mock data.

---

### Deliverable Documentation (`docs/deliverables/D04_supplier_transport_agents/`)

#### [MODIFY] [README.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/README.md)
- Updated overview, prerequisites, document map, module structure, and definition of done (matching D3 README structure).

#### [NEW] [implementation_plan.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/implementation_plan.md)
- Copy of this plan to the deliverable documentation directory.

#### [NEW] [supplier_agent_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/supplier_agent_design.md)
- Detailed Supplier Agent design: data sources (Neo4j graph + PostgreSQL delivery history), feature engineering pipeline, ML model (GradientBoostingClassifier), rule-based scorer, ensemble strategy, MCP tool declarations, claim output examples.

#### [NEW] [transport_agent_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/transport_agent_design.md)
- Detailed Transportation Agent design: route network queries, shipment history analysis, delay predictor model, rerouting engine, MCP tool declarations, claim output examples.

#### [NEW] [model_evaluation.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/model_evaluation.md)
- Prediction accuracy metrics against D1 disruption ground truth: supplier failure detection precision/recall, delay prediction MAE, rerouting recommendation validity.

#### [NEW] [acceptance_evidence.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/acceptance_evidence.md)
- Evidence log template for D4 acceptance criteria.

---

## Verification Plan

### Automated Tests

1. **Supplier Agent Unit Tests**:
   ```bash
   pytest services/agents/supplier/tests/ -v
   ```

2. **Transportation Agent Unit Tests**:
   ```bash
   pytest services/agents/transportation/tests/ -v
   ```

3. **D4 Verification Script** (requires running containers):
   ```bash
   make verify-d4
   ```
   or
   ```bash
   python scripts/verify_d4.py
   ```

### Manual Verification

1. **Direct API Invocation**:
   ```bash
   # Rich health checks
   curl http://localhost:8013/health
   curl http://localhost:8014/health

   # Agent Cards
   curl http://localhost:8013/.well-known/agent.json
   curl http://localhost:8014/.well-known/agent.json

   # Supplier Agent analysis (supplier_delay disruption)
   curl -X POST http://localhost:8013/analyze \
     -H "Content-Type: application/json" \
     -d '{"scenario_id": "scen-test-01", "run_id": "run-01", "disruption_type": "supplier_delay", "target_entity_type": "supplier", "target_entity_id": "sup-02", "severity": 4}'

   # Transportation Agent analysis (transport_failure disruption)
   curl -X POST http://localhost:8014/analyze \
     -H "Content-Type: application/json" \
     -d '{"scenario_id": "scen-test-01", "run_id": "run-01", "disruption_type": "transport_failure", "target_entity_type": "route", "target_entity_id": "rt-01", "severity": 3}'
   ```

2. **Structured Claim Inspection**: Verify the returned JSON contains all required fields including `reasoning` (referencing specific suppliers/routes), `low_confidence` flag, and evidence items with `reference_id` (e.g., `"supplier_graph:sup-02"`, `"route_network:rt-01"`).

3. **Disruption Response Test**: Inject a `supplier_delay` disruption targeting `sup-02` (medium reliability profile), verify the Supplier Agent reasoning mentions the delay and recommends alternate suppliers (e.g., `sup-01` or `sup-03`). Inject a `transport_failure` disruption, verify the Transportation Agent reasoning mentions delay prediction and rerouting options.

---

## Summary of New Files

| Component | Files | Purpose |
| --- | --- | --- |
| Supplier Agent | ~14 files | FastAPI service, DataAccess (PG + Neo4j), FeatureBuilder, ReliabilityScorer/RuleScorer, MCP tools, tests |
| Transportation Agent | ~14 files | FastAPI service, DataAccess (PG + Neo4j), FeatureBuilder, DelayPredictor/RouteScorer, MCP tools, tests |
| Model Artifacts | 2 dirs + .gitkeep | models/supplier/, models/transportation/ |
| Profile Extension | 1 modified | agents.yaml with D4 agent config + MCP tools + ensemble weights |
| Infrastructure | 1 modified | docker-compose.yml with D4 agent services |
| Verification | 1 new, 1 modified | verify_d4.py (deterministic), Makefile target |
| Documentation | 6 files (5 new, 1 modified) | README, design docs, evaluation, acceptance evidence |
| **Total** | **~40 files** | |
