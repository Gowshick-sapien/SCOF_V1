# Deliverable D3 Implementation Plan -- Forecasting Agent Slice: Demand + Inventory

## Goal Description

Deliverable D3 builds the first two specialist AI agents as **standalone, independently testable services** that conform to the universal Structured Claim contract. These agents are the data-heaviest in the system -- they consume time-series inventory levels, purchase orders, and sales history from PostgreSQL (D1) and graph-based supply chain topology from Neo4j (D2) to produce demand forecasts and inventory risk assessments.

D3 delivers:

1. **Shared Agent Contracts** (`shared/scof_shared/schemas/`) -- Pydantic models for `StructuredClaim` (with `reasoning` field), `EvidenceItem` (with `reference_id` traceability), `AgentCard` (future-proofed with `version`, `tags`, `supported_contexts`), and `ScenarioContext`.
2. **Shared ML Library** (`shared/scof_shared/ml/`) -- Reusable ML components (`BaseEnsemble`, `PredictionInterval`, `ForecastResult`, `ConfidenceCalculator`, `FeatureScaler`) shared across D3 and D4 agents, eliminating code duplication.
3. **Demand Forecast Agent** (`services/agents/demand/`) -- an ensemble forecasting service combining XGBoost with a statistical baseline, exposed as a FastAPI service with MCP tool declarations. Clean pipeline: DataAccess -> FeatureBuilder -> InferenceModel -> ClaimBuilder.
4. **Inventory Agent** (`services/agents/inventory/`) -- a safety-stock and stockout risk assessment service using the same ensembling pattern. Same clean pipeline architecture.
5. **Profile-Driven Agent Configuration** -- Both agents read their `confidence_floor`, port, ensemble weights, and identity from the profile's `agents.yaml` at startup.
6. **Model Artifact Storage** -- Versioned trained model artifacts stored in `models/demand/` and `models/inventory/`.
7. **Verification Script** (`scripts/verify_d3.py`) -- callable via `make verify-d3`, deterministic via explicit random seeds, validates both agents against D1 synthetic scenarios.

---

## Prerequisites Check

> [!NOTE]
> - **Prerequisite Deliverables**: D1 (Simulation Environment) and D2 (Knowledge & Data Layer) are complete. PostgreSQL contains synthetic `inventory_levels`, `purchase_orders`, `order_items`, `shipments`, and `disruption_events` tables. Neo4j contains the supply chain graph with Supplier, Product, Warehouse, Route nodes and relationships.
> - **Domain Profile**: [`profiles/mvp-electronics/`](file:///d:/SCOF/profiles/mvp-electronics/) is complete with `topology.yaml`, `disruptions.yaml`, and `agents.yaml`.
> - **Shared Library**: `shared/scof_shared/profile/` (ProfileLoader) and `shared/scof_shared/knowledge/` (Neo4jGraphClient, PgVectorClient) are operational.
> - **Infrastructure**: Docker Compose services (Postgres, Neo4j, Redis, Kafka) are running and healthy.

---

## User Review Required

> [!IMPORTANT]
> **Key Design Decisions**:
>
> 1. **ML Model Selection**: The architecture doc specifies "XGBoost/Prophet baseline ensembled with a time-series foundation model (e.g., Chronos-2)." For the MVP, the plan uses **XGBoost + a lightweight statistical decomposition model** (trend + seasonality extraction) as the primary ensemble pair. The reasoning: Chronos-2 requires a PyTorch dependency and significant GPU/memory, which adds container complexity for marginal gain on 365-day synthetic data. The foundation model slot is **architected as a pluggable interface** so Chronos-2 can be swapped in post-MVP without code changes to the ensemble combiner.
>
> 2. **MCP Implementation Scope**: D3 declares MCP tool definitions (schema + capability descriptions) for each agent's data access, but full MCP server wiring is completed in D5 when the Coordinator needs to invoke these tools via protocol. In D3, agents call their data sources through the shared knowledge library directly. MCP tool declarations exist as metadata for D5's Agent Card discovery.
>
> 3. **A2A Agent Card**: Each agent publishes a `/.well-known/agent.json` endpoint (per A2A spec) describing its capabilities. This endpoint is built in D3 but not consumed until D5's Coordinator discovery phase.
>
> 4. **Confidence is never fabricated**: The `ClaimBuilder` reports the model's actual computed confidence. If confidence falls below the agent's `confidence_floor`, the claim is tagged with `low_confidence=True` -- the Coordinator (D5) decides whether to ignore or flag it. Confidence is never clamped or inflated.
>
> 5. **Trainer/InferenceModel separation**: Even though training occurs at startup for the MVP (fitting on synthetic data), the interfaces are separated into `Trainer.fit() -> ModelArtifact` and `InferenceModel.predict(features)`. This keeps D6/D7 clean and prevents inference-time code from depending on training logic.

---

## Resolved Design Questions

> [!NOTE]
> **Ensemble Weights**: Fixed configurable weights, read from `agents.yaml`. Default: `{"xgboost": 0.6, "statistical": 0.4}`. No stacking implementation at this stage.
>
> **Confidence Calibration**: Composite score with the formula:
> - 40% -- ensemble agreement (how closely the two models' forecasts align)
> - 30% -- prediction interval width (narrower = more confident)
> - 30% -- historical validation error (lower error on holdout = more confident)
>
> This formula is implemented in `shared/scof_shared/ml/confidence.py` and is easy to explain and audit.

---

## Proposed Changes

### Shared Contracts (`shared/scof_shared/schemas/`)

This new `schemas/` sub-package establishes the cross-service Pydantic contracts that all agents (D3, D4) and downstream consumers (D5, D6, D7, D8) will import. These are the API boundaries between services.

#### [NEW] [structured_claim.py](file:///d:/SCOF/shared/scof_shared/schemas/structured_claim.py)
- `StructuredClaim` Pydantic model with fields:
  - `agent_id` (str)
  - `scenario_id` (str)
  - `recommendation` (str)
  - `reasoning` (str) -- concise rationale summarizing why this recommendation was made (e.g., "Demand increased 42%. Supplier delay active. Inventory below safety stock. Forecast interval narrow."). Distinct from evidence: reasoning is the agent's interpretation, evidence is the raw backing data.
  - `confidence` (float, 0.0-1.0) -- the model's actual computed confidence, never clamped or inflated
  - `low_confidence` (bool, default False) -- set to True when confidence falls below the agent's `confidence_floor`; the Coordinator decides how to handle this
  - `priority` (Literal["HIGH", "MEDIUM", "LOW"])
  - `impact` (str)
  - `evidence` (List[EvidenceItem])
  - `timestamp` (datetime)
- Validator enforcing confidence range [0.0, 1.0].
- `to_dict()` and `from_dict()` serialization helpers.

#### [NEW] [evidence.py](file:///d:/SCOF/shared/scof_shared/schemas/evidence.py)
- `EvidenceItem` Pydantic model with fields:
  - `type` (Literal["historical_data", "model_output", "graph_query", "external_signal"])
  - `source` (str) -- human-readable source description
  - `summary` (str) -- human-readable evidence description
  - `reference_id` (str) -- machine-traceable identifier (e.g., `"inventory_level:4567"`, `"shipment:882"`, `"graph_path:91"`)
  - `query_hash` (Optional[str]) -- hash of the query that produced this evidence, for reproducibility and audit
- All claims become fully traceable and auditable through `reference_id`.

#### [NEW] [agent_card.py](file:///d:/SCOF/shared/scof_shared/schemas/agent_card.py)
- `AgentCard` Pydantic model (future-proofed per A2A spec):
  - `agent_id` (str)
  - `name` (str)
  - `description` (str)
  - `version` (str) -- agent version string (e.g., "1.0.0")
  - `capabilities` (List[str])
  - `tags` (List[str]) -- classification tags (e.g., ["forecasting", "demand", "time-series"])
  - `supported_contexts` (List[str]) -- disruption types this agent handles (e.g., ["demand_spike", "supplier_delay"])
  - `dependencies` (List[str]) -- other agent IDs or services this agent depends on (e.g., ["neo4j", "postgres"])
  - `input_schema` (dict)
  - `output_schema` (str = "StructuredClaim")
  - `protocol` (str = "A2A/1.0")
  - `endpoint` (str)

#### [NEW] [scenario_context.py](file:///d:/SCOF/shared/scof_shared/schemas/scenario_context.py)
- `ScenarioContext` Pydantic model representing the input to any specialist agent: `scenario_id`, `run_id`, `disruption_id` (optional), `disruption_type` (optional), `target_entity_type` (optional), `target_entity_id` (optional), `severity` (optional int), `start_date` (optional date), `end_date` (optional date), `product_ids` (optional List[str]), `warehouse_ids` (optional List[str]).
- Provides the common request contract that D5's Coordinator will eventually use to invoke agents.

#### [NEW] [\_\_init\_\_.py](file:///d:/SCOF/shared/scof_shared/schemas/__init__.py)
- Re-exports `StructuredClaim`, `EvidenceItem`, `AgentCard`, `ScenarioContext`.

---

### Shared ML Library (`shared/scof_shared/ml/`)

Reusable ML components shared by the Demand Agent, Inventory Agent, and later D4 agents. Eliminates the ~80% code duplication that would otherwise exist between agent services.

#### [NEW] [\_\_init\_\_.py](file:///d:/SCOF/shared/scof_shared/ml/__init__.py)
- Re-exports `BaseEnsemble`, `ForecastResult`, `PredictionInterval`, `ConfidenceCalculator`, `FeatureScaler`, `BaseTrainer`, `BaseInferenceModel`.

#### [NEW] [types.py](file:///d:/SCOF/shared/scof_shared/ml/types.py)
- `PredictionInterval` dataclass: `lower` (np.ndarray), `upper` (np.ndarray), `alpha` (float).
- `ForecastResult` dataclass: `point_forecast` (np.ndarray), `interval` (PredictionInterval), `model_name` (str), `metadata` (dict).
- `EnsembleResult` dataclass: `point_forecast` (np.ndarray), `interval` (PredictionInterval), `agreement_score` (float), `model_contributions` (Dict[str, ForecastResult]).

#### [NEW] [confidence.py](file:///d:/SCOF/shared/scof_shared/ml/confidence.py)
- `ConfidenceCalculator` class implementing the composite confidence formula:
  - `compute(agreement_score: float, interval_width: float, historical_error: float, max_interval_width: float) -> float`
  - Formula: `0.4 * agreement_score + 0.3 * (1.0 - interval_width / max_interval_width) + 0.3 * (1.0 - clamp(historical_error, 0, 1))`
  - Result clamped to [0.0, 1.0].
  - Each component is individually queryable for evidence/reasoning generation.
- `ConfidenceScore` dataclass: `score` (float), `components` (dict with keys `agreement`, `interval`, `historical`).

#### [NEW] [ensemble.py](file:///d:/SCOF/shared/scof_shared/ml/ensemble.py)
- `BaseEnsemble` abstract class:
  - `__init__(weights: Dict[str, float], confidence_calculator: ConfidenceCalculator)`
  - `register_model(name: str, model: BaseInferenceModel)` -- pluggable model registration.
  - `predict(features) -> EnsembleResult` -- weighted average of point forecasts, combined prediction interval, agreement score computation.
  - `compute_agreement(results: Dict[str, ForecastResult]) -> float` -- normalized pairwise forecast distance.
- Concrete agents subclass this and register their specific models.

#### [NEW] [base_model.py](file:///d:/SCOF/shared/scof_shared/ml/base_model.py)
- `BaseTrainer` abstract class:
  - `fit(X_train, y_train, **kwargs) -> ModelArtifact` -- trains and returns a serializable artifact.
  - `save(artifact: ModelArtifact, path: Path)` -- persists to model artifact directory.
  - `load(path: Path) -> ModelArtifact` -- loads from model artifact directory.
- `BaseInferenceModel` abstract class:
  - `__init__(artifact: ModelArtifact)` -- initialized from a trained artifact, never from raw data.
  - `predict(X: np.ndarray) -> np.ndarray` -- point forecasts.
  - `predict_interval(X: np.ndarray, alpha: float = 0.1) -> PredictionInterval` -- prediction intervals.
- `ModelArtifact` dataclass: `model_bytes` (bytes), `model_name` (str), `model_version` (str), `training_metadata` (dict), `created_at` (datetime).
- This separation ensures inference services never import training logic at runtime.

#### [NEW] [feature_scaler.py](file:///d:/SCOF/shared/scof_shared/ml/feature_scaler.py)
- `FeatureScaler` class wrapping standard scaling with serialization:
  - `fit_transform(X) -> np.ndarray`
  - `transform(X) -> np.ndarray`
  - `save(path: Path)` / `load(path: Path)` -- persists scaler parameters alongside model artifacts.

---

### Profile Extension (`shared/scof_shared/profile/`)

#### [NEW] [agents_config.py](file:///d:/SCOF/shared/scof_shared/profile/agents_config.py)
- `AgentConfigModel` Pydantic model: `id` (str), `name` (str), `port` (int), `confidence_floor` (float), `ensemble_weights` (Optional[Dict[str, float]]), `forecast_horizon_days` (Optional[int]), `mcp_tools` (Optional[List[str]]).
- `AgentsRosterModel` Pydantic model: `active_agents` (List[AgentConfigModel]).
- `load_agents_config(profile_path: Path) -> AgentsRosterModel` function reading `agents.yaml`.
- `get_agent_config(roster: AgentsRosterModel, agent_id: str) -> AgentConfigModel` helper.

#### [MODIFY] [loader.py](file:///d:/SCOF/shared/scof_shared/profile/loader.py)
- Add optional `agents_config: Optional[AgentsRosterModel]` field to `DomainProfile`.
- `ProfileLoader.load_profile()` optionally loads `agents.yaml` if present (backward-compatible; D1/D2 callers unaffected).

#### [MODIFY] [\_\_init\_\_.py](file:///d:/SCOF/shared/scof_shared/profile/__init__.py)
- Re-export `AgentConfigModel`, `AgentsRosterModel`, `load_agents_config`.

---

### Shared Agent Base (`shared/scof_shared/agent_base/`)

A thin base layer providing common patterns so both D3 agents (and later D4 agents) do not duplicate boilerplate.

#### [NEW] [\_\_init\_\_.py](file:///d:/SCOF/shared/scof_shared/agent_base/__init__.py)
- Re-exports `BaseAgent`, `ClaimBuilder`.

#### [NEW] [base_agent.py](file:///d:/SCOF/shared/scof_shared/agent_base/base_agent.py)
- Abstract `BaseAgent` class defining the `analyze(context: ScenarioContext) -> StructuredClaim` contract.
- Common lifecycle: load profile agent config by agent_id from `agents.yaml`, initialize data clients (Neo4jGraphClient, PgVectorClient passed via constructor or env), expose `get_agent_card() -> AgentCard`.
- `confidence_floor` property read from profile config -- used only for setting `low_confidence` flag, never for clamping.

#### [NEW] [claim_builder.py](file:///d:/SCOF/shared/scof_shared/agent_base/claim_builder.py)
- `ClaimBuilder` utility class that constructs a `StructuredClaim` from model outputs.
- Methods:
  - `set_recommendation(text)` -- the proposed action
  - `set_reasoning(text)` -- concise rationale (distinct from evidence)
  - `set_confidence(score: float)` -- records the raw computed confidence as-is
  - `add_evidence(type, source, summary, reference_id, query_hash=None)` -- adds traceable evidence
  - `set_priority(priority)` -- urgency level
  - `set_impact(text)` -- consequence description
  - `build(confidence_floor: float) -> StructuredClaim` -- finalizes the claim; sets `low_confidence=True` if `confidence < confidence_floor` but **never modifies the confidence value itself**

---

### Demand Agent Service (`services/agents/demand/`)

#### [NEW] [pyproject.toml](file:///d:/SCOF/services/agents/demand/pyproject.toml)
- Package manifest declaring dependencies: `fastapi`, `uvicorn`, `xgboost`, `scikit-learn`, `numpy`, `pandas`, `psycopg[binary]`, `pydantic>=2.0`, `pyyaml`, `scof-shared`.

#### [NEW] [Dockerfile](file:///d:/SCOF/services/agents/demand/Dockerfile)
- Python 3.11-slim based container. Installs `scof-shared` from local path. Exposes port 8011. Entrypoint: `uvicorn src.main:app --host 0.0.0.0 --port 8011`.

#### [NEW] [src/\_\_init\_\_.py](file:///d:/SCOF/services/agents/demand/src/__init__.py)
- Package marker.

#### [NEW] [src/config.py](file:///d:/SCOF/services/agents/demand/src/config.py)
- Agent-specific configuration: `AGENT_ID = "demand-agent"`, database connection parameters from environment, profile path from `SCOF_PROFILE_PATH`, forecast horizon days.
- **Random seeds**: `NUMPY_SEED = 42`, `XGBOOST_SEED = 42`, `PYTHON_RANDOM_SEED = 42` -- all specified explicitly for deterministic verification.

#### [NEW] [src/main.py](file:///d:/SCOF/services/agents/demand/src/main.py)
- FastAPI application with endpoints:
  - `POST /analyze` -- accepts `ScenarioContext`, returns `StructuredClaim`.
  - `GET /health` -- rich health endpoint returning:
    ```json
    {
      "status": "healthy",
      "agent_id": "demand-agent",
      "profile_loaded": true,
      "db_connected": true,
      "neo4j_connected": true,
      "model_loaded": true,
      "model_version": "1.0.0",
      "uptime_seconds": 3421.5
    }
    ```
  - `GET /.well-known/agent.json` -- returns A2A `AgentCard`.
- Startup event: loads profile, initializes agent, connects to data stores, sets random seeds.

#### [NEW] [src/agent.py](file:///d:/SCOF/services/agents/demand/src/agent.py)
- `DemandAgent(BaseAgent)` class.
- Clean pipeline architecture:
  1. `DataAccess` -- fetches raw data from PostgreSQL
  2. `FeatureBuilder` -- transforms raw data into model-ready features
  3. `InferenceModel` (via ensemble) -- produces forecasts
  4. `ClaimBuilder` -- constructs the StructuredClaim with reasoning and traceable evidence
- `analyze(context: ScenarioContext) -> StructuredClaim` orchestrates this pipeline.
- Startup: calls `Trainer.fit()` on historical data, saves artifact, initializes `InferenceModel` from artifact.

#### [NEW] [src/data_access.py](file:///d:/SCOF/services/agents/demand/src/data_access.py)
- `DemandDataAccess` class wrapping PostgreSQL queries specific to the Demand Agent:
  - `get_historical_demand(run_id, product_ids, start_date, end_date) -> pd.DataFrame` -- aggregates `order_items` joined with `purchase_orders` by date. Returns query hash for evidence traceability.
  - `get_active_disruptions(run_id, scenario_id) -> List[dict]` -- fetches disruption events targeting products.
  - `get_product_metadata(product_ids) -> List[dict]` -- fetches product details.
- Each query method returns both the result and a `query_hash` (SHA-256 of the parameterized SQL) for `EvidenceItem.query_hash`.

#### [NEW] [src/features.py](file:///d:/SCOF/services/agents/demand/src/features.py)
- `DemandFeatureBuilder` class -- separated from agent logic per clean architecture:
  - `build_features(demand_df: pd.DataFrame, disruptions: List[dict]) -> pd.DataFrame` -- constructs:
    - Day-of-week, month, quarter indicators
    - Rolling averages (7d, 14d, 30d)
    - Trend features (linear slope over trailing window)
    - Lag features (t-1, t-7, t-14)
    - Disruption severity as exogenous feature (if active)
  - `build_inference_features(demand_df, disruptions, horizon) -> pd.DataFrame` -- constructs features for forecast horizon.
  - Returns feature names for model interpretability.

#### [NEW] [src/mcp/\_\_init\_\_.py](file:///d:/SCOF/services/agents/demand/src/mcp/__init__.py)
- Package marker.

#### [NEW] [src/mcp/tools.py](file:///d:/SCOF/services/agents/demand/src/mcp/tools.py)
- MCP tool declarations as dataclass descriptors:
  - `read_historical_demand` -- reads demand time-series for a product over a date range.
  - `read_demand_disruptions` -- reads disruption events affecting demand.
  - `read_product_catalog` -- reads product metadata.
- Each tool descriptor includes `name`, `description`, `input_schema`, `output_schema`.
- These declarations are consumed by the Agent Card and will be protocol-wrapped in D5.

#### [NEW] [src/models/\_\_init\_\_.py](file:///d:/SCOF/services/agents/demand/src/models/__init__.py)
- Package marker.

#### [NEW] [src/models/xgboost_model.py](file:///d:/SCOF/services/agents/demand/src/models/xgboost_model.py)
- `DemandXGBoostTrainer(BaseTrainer)`:
  - `fit(X_train, y_train) -> ModelArtifact` -- trains XGBoost regressor, serializes to artifact.
  - Hyperparameters: `n_estimators=200`, `max_depth=6`, `learning_rate=0.1`, `reg_alpha=0.1`, `reg_lambda=1.0`, `random_state=XGBOOST_SEED`.
- `DemandXGBoostInference(BaseInferenceModel)`:
  - `__init__(artifact: ModelArtifact)` -- deserializes model from artifact.
  - `predict(X) -> np.ndarray` -- point forecasts.
  - `predict_interval(X, alpha=0.1) -> PredictionInterval` -- via quantile regression (XGBoost `quantile` objective with alpha/2 and 1-alpha/2).

#### [NEW] [src/models/statistical_model.py](file:///d:/SCOF/services/agents/demand/src/models/statistical_model.py)
- `DemandStatisticalTrainer(BaseTrainer)`:
  - `fit(series: pd.Series) -> ModelArtifact` -- decomposes into trend (linear regression), weekly seasonality (day-of-week dummies), and residual. Serializes parameters.
- `DemandStatisticalInference(BaseInferenceModel)`:
  - `predict(horizon: int) -> np.ndarray` -- extrapolates trend + seasonal component.
  - `predict_interval(horizon, alpha=0.1) -> PredictionInterval` -- intervals from residual distribution.
- Serves as the "Prophet-style" baseline without the heavy fbprophet C++ build dependency.

#### [NEW] [src/models/ensemble.py](file:///d:/SCOF/services/agents/demand/src/models/ensemble.py)
- `DemandEnsemble(BaseEnsemble)`:
  - Registers `DemandXGBoostInference` and `DemandStatisticalInference` as models.
  - Weights read from profile `agents.yaml` (default: `{"xgboost": 0.6, "statistical": 0.4}`).
  - Inherits `predict() -> EnsembleResult` from `BaseEnsemble`.
  - Confidence computed via shared `ConfidenceCalculator`.

---

### Inventory Agent Service (`services/agents/inventory/`)

#### [NEW] [pyproject.toml](file:///d:/SCOF/services/agents/inventory/pyproject.toml)
- Same dependency set as Demand Agent.

#### [NEW] [Dockerfile](file:///d:/SCOF/services/agents/inventory/Dockerfile)
- Python 3.11-slim. Exposes port 8012. Entrypoint: `uvicorn src.main:app --host 0.0.0.0 --port 8012`.

#### [NEW] [src/\_\_init\_\_.py](file:///d:/SCOF/services/agents/inventory/src/__init__.py)
- Package marker.

#### [NEW] [src/config.py](file:///d:/SCOF/services/agents/inventory/src/config.py)
- Agent-specific configuration: `AGENT_ID = "inventory-agent"`, database connections, profile path, stockout risk thresholds.
- **Random seeds**: `NUMPY_SEED = 42`, `XGBOOST_SEED = 42`, `PYTHON_RANDOM_SEED = 42`.

#### [NEW] [src/main.py](file:///d:/SCOF/services/agents/inventory/src/main.py)
- FastAPI application with same endpoint pattern as Demand Agent:
  - `POST /analyze` -- accepts `ScenarioContext`, returns `StructuredClaim`.
  - `GET /health` -- rich health endpoint (same schema as Demand Agent).
  - `GET /.well-known/agent.json` -- returns A2A `AgentCard`.

#### [NEW] [src/agent.py](file:///d:/SCOF/services/agents/inventory/src/agent.py)
- `InventoryAgent(BaseAgent)` class.
- Same clean pipeline: DataAccess -> FeatureBuilder -> InferenceModel -> ClaimBuilder.
- `analyze(context: ScenarioContext) -> StructuredClaim`:
  1. **DataAccess**: Fetches inventory levels, in-transit shipments, disruptions, warehouse capacity.
  2. **FeatureBuilder**: Constructs depletion rate, days-of-supply, safety stock proximity, disruption impact features.
  3. **InferenceModel**: Ensemble forecasts stock levels forward, estimates time-to-stockout.
  4. **ClaimBuilder**: Constructs claim with reasoning (e.g., "Stock depleting at 120 units/day. Safety threshold breached in 5 days. Supplier delay active for sup-02. Reorder recommended."), traceable evidence with reference_ids.

#### [NEW] [src/data_access.py](file:///d:/SCOF/services/agents/inventory/src/data_access.py)
- `InventoryDataAccess` class:
  - `get_inventory_levels(run_id, warehouse_ids, product_ids, start_date, end_date) -> pd.DataFrame` -- returns levels with query hash.
  - `get_inbound_shipments(run_id, warehouse_ids) -> List[dict]` -- in-transit shipments with ETAs.
  - `get_supplier_disruptions(run_id, scenario_id) -> List[dict]` -- disruptions affecting suppliers that feed these warehouses.
  - `get_warehouse_capacity(warehouse_ids) -> List[dict]` -- capacity constraints.

#### [NEW] [src/features.py](file:///d:/SCOF/services/agents/inventory/src/features.py)
- `InventoryFeatureBuilder` class:
  - `build_features(inventory_df, shipments, disruptions) -> pd.DataFrame`:
    - Depletion rate (rolling consumption over 7d, 14d)
    - Days-of-supply projection (stock_on_hand / depletion_rate)
    - Safety stock breach countdown (days until stock_on_hand < safety_stock_threshold)
    - Reorder point proximity (stock_on_hand - reorder_point)
    - Units-in-transit risk factor (if supplier disruption active, in-transit units are at risk)
    - Capacity utilization (stock_on_hand / warehouse_capacity)

#### [NEW] [src/mcp/\_\_init\_\_.py](file:///d:/SCOF/services/agents/inventory/src/mcp/__init__.py)
- Package marker.

#### [NEW] [src/mcp/tools.py](file:///d:/SCOF/services/agents/inventory/src/mcp/tools.py)
- MCP tool declarations:
  - `read_stock_levels` -- reads current and historical inventory levels.
  - `read_reorder_points` -- reads safety stock and reorder thresholds.
  - `read_inbound_shipments` -- reads pending shipment arrivals.
  - `read_inventory_disruptions` -- reads disruptions impacting inventory replenishment.

#### [NEW] [src/models/\_\_init\_\_.py](file:///d:/SCOF/services/agents/inventory/src/models/__init__.py)
- Package marker.

#### [NEW] [src/models/xgboost_model.py](file:///d:/SCOF/services/agents/inventory/src/models/xgboost_model.py)
- `InventoryXGBoostTrainer(BaseTrainer)` / `InventoryXGBoostInference(BaseInferenceModel)` -- same XGBoost pattern as Demand Agent but trained on inventory depletion features.

#### [NEW] [src/models/statistical_model.py](file:///d:/SCOF/services/agents/inventory/src/models/statistical_model.py)
- `InventoryStatisticalTrainer` / `InventoryStatisticalInference` -- trend + seasonality decomposition on stock level time-series.

#### [NEW] [src/models/ensemble.py](file:///d:/SCOF/services/agents/inventory/src/models/ensemble.py)
- `InventoryEnsemble(BaseEnsemble)` -- registers inventory-specific models, weights from config.

---

### Model Artifact Storage

#### [NEW] models/demand/.gitkeep
#### [NEW] models/inventory/.gitkeep
- Versioned model artifact directories at the repository root.
- Each trained model is saved as a versioned artifact (e.g., `models/demand/v1.0.0/model.pkl`, `models/demand/v1.0.0/scaler.pkl`, `models/demand/v1.0.0/metadata.json`).
- `metadata.json` includes: `model_name`, `model_version`, `training_date`, `training_run_id`, `profile_hash`, `random_seeds`, `hyperparameters`, `validation_metrics`.
- `.gitignore` updated to track `.gitkeep` files but ignore `*.pkl` artifacts (artifacts are generated, not committed).

---

### Docker Compose Extension

#### [MODIFY] [docker-compose.yml](file:///d:/SCOF/docker-compose.yml)
- Add `demand-agent` service:
  - Build context: `.`, Dockerfile: `services/agents/demand/Dockerfile`
  - Container name: `scof-demand-agent`
  - Depends on: `postgres` (healthy)
  - Environment: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SCOF_PROFILE_PATH=/app/profiles/mvp-electronics`, `AGENT_ID=demand-agent`, `NUMPY_SEED=42`, `XGBOOST_SEED=42`
  - Volumes: `./profiles:/app/profiles:ro`, `./models/demand:/app/models:rw`
  - Port: `8011:8011`
- Add `inventory-agent` service:
  - Same pattern, port `8012:8012`, `AGENT_ID=inventory-agent`, models volume: `./models/inventory:/app/models:rw`

---

### Profile Extension

#### [MODIFY] [agents.yaml](file:///d:/SCOF/profiles/mvp-electronics/agents.yaml)
- Add model configuration and MCP tool binding metadata to each D3 agent entry:
  ```yaml
  - id: "demand-agent"
    name: "Demand Forecast Agent"
    port: 8011
    confidence_floor: 0.60
    ensemble_weights:
      xgboost: 0.6
      statistical: 0.4
    forecast_horizon_days: 14
    mcp_tools:
      - read_historical_demand
      - read_demand_disruptions
      - read_product_catalog
  ```
- Similar additions for `inventory-agent` with inventory-specific MCP tools and risk thresholds.

---

### Verification & Tests

#### [NEW] [scripts/verify_d3.py](file:///d:/SCOF/scripts/verify_d3.py)
- Comprehensive verification script (all tests use explicit random seeds for determinism):
  1. **Connectivity**: HTTP health check on both agent endpoints, validate rich health response (profile_loaded, db_connected, model_loaded, model_version, uptime).
  2. **Agent Card Validation**: Fetch `/.well-known/agent.json` from each agent, validate against `AgentCard` schema including `version`, `tags`, `supported_contexts`, `dependencies`.
  3. **Structured Claim Compliance**: Send a `ScenarioContext` (using the latest D1 simulation run) to each agent's `/analyze` endpoint, validate the response against `StructuredClaim` schema including `reasoning` field.
  4. **Confidence Integrity**: Assert `0.0 <= claim.confidence <= 1.0`. If confidence < confidence_floor, assert `claim.low_confidence == True`. Verify confidence is never clamped to floor.
  5. **Evidence Traceability**: Assert each evidence item has non-empty `reference_id` and valid `source` and `summary`.
  6. **Forecast Plausibility** (Demand Agent): Compare forecast against D1 ground truth -- forecast should be within a configurable tolerance (e.g., MAE < 50% of actual mean) on the synthetic data.
  7. **Stockout Detection** (Inventory Agent): For a scenario with a known supplier delay disruption, verify the agent detects elevated stockout risk and reasoning mentions the disruption.
  8. **Determinism**: Call each agent twice with the same scenario and identical random seeds, verify identical structured claims (byte-level comparison of serialized output).

#### [MODIFY] [Makefile](file:///d:/SCOF/Makefile)
- Add target `verify-d3: python scripts/verify_d3.py`.

#### [NEW] [services/agents/demand/tests/\_\_init\_\_.py](file:///d:/SCOF/services/agents/demand/tests/__init__.py)
- Package marker.

#### [NEW] [services/agents/demand/tests/test_agent.py](file:///d:/SCOF/services/agents/demand/tests/test_agent.py)
- Unit tests for `DemandAgent.analyze()` with mocked data access returning fixture DataFrames. Verifies claim structure, reasoning content, confidence computation, evidence traceability.

#### [NEW] [services/agents/demand/tests/test_ensemble.py](file:///d:/SCOF/services/agents/demand/tests/test_ensemble.py)
- Unit tests for `DemandEnsemble`: predict with synthetic series, weighted combination correctness, agreement score computation, prediction interval validity.

#### [NEW] [services/agents/demand/tests/test_features.py](file:///d:/SCOF/services/agents/demand/tests/test_features.py)
- Unit tests for `DemandFeatureBuilder`: feature column names, rolling average correctness, disruption feature injection.

#### [NEW] [services/agents/demand/tests/test_data_access.py](file:///d:/SCOF/services/agents/demand/tests/test_data_access.py)
- Integration tests for `DemandDataAccess` queries against a test database (or mocked cursor). Verifies query_hash generation.

#### [NEW] [services/agents/inventory/tests/\_\_init\_\_.py](file:///d:/SCOF/services/agents/inventory/tests/__init__.py)
- Package marker.

#### [NEW] [services/agents/inventory/tests/test_agent.py](file:///d:/SCOF/services/agents/inventory/tests/test_agent.py)
- Unit tests for `InventoryAgent.analyze()` with fixture inventory data. Verifies stockout detection, reorder recommendations, priority assignment, reasoning content.

#### [NEW] [services/agents/inventory/tests/test_ensemble.py](file:///d:/SCOF/services/agents/inventory/tests/test_ensemble.py)
- Unit tests for `InventoryEnsemble`.

#### [NEW] [services/agents/inventory/tests/test_features.py](file:///d:/SCOF/services/agents/inventory/tests/test_features.py)
- Unit tests for `InventoryFeatureBuilder`: depletion rate, days-of-supply, safety stock breach countdown.

---

### Deliverable Documentation (`docs/deliverables/D03_demand_inventory_agents/`)

#### [MODIFY] [README.md](file:///d:/SCOF/docs/deliverables/D03_demand_inventory_agents/README.md)
- Updated overview, prerequisites, document map, module structure, and definition of done.

#### [NEW] [implementation_plan.md](file:///d:/SCOF/docs/deliverables/D03_demand_inventory_agents/implementation_plan.md)
- This document, copied to the deliverable's documentation directory.

#### [NEW] [demand_agent_design.md](file:///d:/SCOF/docs/deliverables/D03_demand_inventory_agents/demand_agent_design.md)
- Detailed Demand Agent design: data sources, feature engineering pipeline (FeatureBuilder), XGBoost hyperparameters, statistical model decomposition approach, ensemble combiner strategy, confidence calibration formula, MCP tool declarations, claim output examples with reasoning and traceable evidence.

#### [NEW] [inventory_agent_design.md](file:///d:/SCOF/docs/deliverables/D03_demand_inventory_agents/inventory_agent_design.md)
- Detailed Inventory Agent design: stock-level analysis, depletion rate computation, days-of-supply projection, safety stock breach detection, disruption impact assessment, ensemble strategy, MCP tool declarations, claim output examples with reasoning and traceable evidence.

#### [NEW] [model_evaluation.md](file:///d:/SCOF/docs/deliverables/D03_demand_inventory_agents/model_evaluation.md)
- Forecast accuracy metrics against D1 ground truth: MAE, MAPE, coverage probability of prediction intervals, stockout detection recall/precision, confidence calibration analysis.

#### [NEW] [acceptance_evidence.md](file:///d:/SCOF/docs/deliverables/D03_demand_inventory_agents/acceptance_evidence.md)
- Evidence log template and test execution outputs for D3 acceptance criteria.

---

## Verification Plan

### Automated Tests

1. **Shared ML Library Tests**:
   ```bash
   pytest shared/ -v
   ```

2. **Demand Agent Unit Tests**:
   ```bash
   pytest services/agents/demand/tests/ -v
   ```

3. **Inventory Agent Unit Tests**:
   ```bash
   pytest services/agents/inventory/tests/ -v
   ```

4. **D3 Verification Script** (requires running containers):
   ```bash
   make verify-d3
   ```
   or
   ```bash
   python scripts/verify_d3.py
   ```

### Manual Verification

1. **Direct API Invocation**:
   ```bash
   # Rich health checks
   curl http://localhost:8011/health
   curl http://localhost:8012/health

   # Agent Cards (with version, tags, supported_contexts)
   curl http://localhost:8011/.well-known/agent.json
   curl http://localhost:8012/.well-known/agent.json

   # Demand Agent analysis
   curl -X POST http://localhost:8011/analyze \
     -H "Content-Type: application/json" \
     -d '{"scenario_id": "<scenario_id>", "run_id": "<run_id>", "product_ids": ["prod-101"]}'

   # Inventory Agent analysis
   curl -X POST http://localhost:8012/analyze \
     -H "Content-Type: application/json" \
     -d '{"scenario_id": "<scenario_id>", "run_id": "<run_id>", "warehouse_ids": ["wh-01"], "product_ids": ["prod-101"]}'
   ```

2. **Structured Claim Inspection**: Verify the returned JSON contains all required fields including `reasoning` (distinct from evidence), `low_confidence` flag (not clamped confidence), and evidence items with `reference_id` and `query_hash`.

3. **Disruption Response Test**: Inject a `demand_spike` disruption event via D1 data, call the Demand Agent, and verify the reasoning mentions the spike. Inject a `supplier_delay` disruption, call the Inventory Agent, and verify reasoning mentions the delay and stockout risk.

---

## Summary of New Files

| Component | Files | Purpose |
| --- | --- | --- |
| Shared Schemas | 5 files | StructuredClaim (with reasoning), EvidenceItem (with reference_id), AgentCard (future-proofed), ScenarioContext |
| Shared ML Library | 6 files | BaseEnsemble, PredictionInterval, ForecastResult, ConfidenceCalculator, FeatureScaler, Trainer/InferenceModel split |
| Profile Extension | 2 files (1 new, 1 modified) | agents.yaml loader, DomainProfile extension |
| Agent Base | 3 files | BaseAgent, ClaimBuilder (no confidence clamping) |
| Demand Agent | 14 files | FastAPI service, DataAccess, FeatureBuilder, Trainer/InferenceModel, MCP tools, tests |
| Inventory Agent | 14 files | FastAPI service, DataAccess, FeatureBuilder, Trainer/InferenceModel, MCP tools, tests |
| Model Artifacts | 2 dirs + .gitkeep | models/demand/, models/inventory/ with versioning |
| Infrastructure | 1 modified | docker-compose.yml with agent services + random seeds |
| Verification | 1 new, 1 modified | verify_d3.py (deterministic), Makefile target |
| Documentation | 5 files | Design docs, evaluation, acceptance evidence |
| **Total** | **~52 files** | |
