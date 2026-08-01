# Deliverable D3 -- Forecasting Agent Slice: Demand + Inventory

## Overview & Purpose
Deliverable D3 builds the first two specialist AI agents as standalone, independently testable FastAPI services conforming to the universal Structured Claim contract. These agents are the data-heaviest in the system -- they consume time-series inventory levels, purchase orders, and sales history from PostgreSQL (D1) and graph-based supply chain topology from Neo4j (D2) to produce demand forecasts and inventory risk assessments. Each agent uses an XGBoost + statistical decomposition ensemble, publishes an A2A Agent Card, and declares MCP tool bindings for downstream protocol wiring in D5.

---

## Requirements Summary (from SRS)
- **FR-3.1**: Implement a Demand Agent using an XGBoost/Prophet baseline ensembled with a time-series foundation model, exposed as an MCP-tool-connected service. Model configuration and MCP tool bindings read from the profile's `agents.yaml`.
- **FR-3.2**: Implement an Inventory Agent using the same ensembling approach, reasoning over D1/D2 inventory data, configured via `agents.yaml`.
- **FR-3.3**: Each agent returns a structured claim (recommendation, reasoning, confidence, priority, impact, evidence with traceable reference IDs) as defined in the Structured Claim Contract, independent of other agents.

---

## Prerequisites & Dependencies
- **Prerequisite Deliverables**: D1 (Simulation Environment & Synthetic Data Foundation) and D2 (Knowledge & Data Layer) are complete. PostgreSQL contains synthetic `inventory_levels`, `purchase_orders`, `order_items`, `shipments`, and `disruption_events` tables. Neo4j contains the supply chain graph with Supplier, Product, Warehouse, Route nodes and relationships.
- **Required System Tools**: Docker (v24+), Python 3.11+, PostgreSQL 16+ (with pgvector), Neo4j 5+.
- **Required Domain Profile Files**:
  - [`profiles/mvp-electronics/topology.yaml`](../../../profiles/mvp-electronics/topology.yaml)
  - [`profiles/mvp-electronics/disruptions.yaml`](../../../profiles/mvp-electronics/disruptions.yaml)
  - [`profiles/mvp-electronics/agents.yaml`](../../../profiles/mvp-electronics/agents.yaml)

---

## Document Set in this Directory
1. **[`README.md`](./README.md)** (this document): Overview, requirements, prerequisites, document map, and acceptance criteria.
2. **[`implementation_plan.md`](./implementation_plan.md)**: Detailed technical implementation plan, proposed file changes, and verification strategy for Deliverable D3.
3. **[`demand_agent_design.md`](./demand_agent_design.md)**: Demand Agent architecture -- data sources, feature engineering pipeline, ensemble strategy, confidence calibration, MCP tool declarations, and example claim output.
4. **[`inventory_agent_design.md`](./inventory_agent_design.md)**: Inventory Agent architecture -- stock-level analysis, depletion rate computation, safety stock breach detection, ensemble strategy, MCP tool declarations, and example claim output.
5. **[`model_evaluation.md`](./model_evaluation.md)**: Forecast accuracy metrics framework against D1 ground truth -- MAE, MAPE, prediction interval coverage, stockout detection precision/recall, confidence calibration analysis.
6. **[`acceptance_evidence.md`](./acceptance_evidence.md)**: Evidence log template for D3 acceptance criteria -- health checks, Agent Card validation, Structured Claim compliance, forecast plausibility, disruption response, and determinism tests.

---

## Module Structure

```
shared/
    scof_shared/
        schemas/
            structured_claim.py        # StructuredClaim (with reasoning, low_confidence flag)
            evidence.py                 # EvidenceItem (with reference_id, query_hash)
            agent_card.py               # AgentCard (with version, tags, supported_contexts)
            scenario_context.py         # ScenarioContext (common agent input contract)

        ml/
            types.py                    # ForecastResult, PredictionInterval, EnsembleResult
            confidence.py               # ConfidenceCalculator (40/30/30 composite formula)
            ensemble.py                 # BaseEnsemble (pluggable model registration)
            base_model.py               # BaseTrainer / BaseInferenceModel / ModelArtifact
            feature_scaler.py           # FeatureScaler (serializable scaling)

        agent_base/
            base_agent.py               # BaseAgent abstract class
            claim_builder.py            # ClaimBuilder (never modifies confidence)

        profile/
            agents_config.py            # AgentConfigModel, AgentsRosterModel loader

services/
    agents/
        demand/
            Dockerfile
            pyproject.toml
            src/
                config.py               # Agent ID, DB params, random seeds, forecast horizon
                main.py                 # FastAPI app: /analyze, /health, /.well-known/agent.json
                agent.py                # DemandAgent orchestrating the pipeline
                data_access.py          # DemandDataAccess (SQL queries with query_hash)
                features.py             # DemandFeatureBuilder (rolling averages, lags, disruption)
                mcp/
                    tools.py            # MCP tool declarations (read_historical_demand, etc.)
                models/
                    xgboost_model.py    # DemandXGBoostTrainer / DemandXGBoostInference
                    statistical_model.py # DemandStatisticalTrainer / DemandStatisticalInference
                    ensemble.py         # DemandEnsemble(BaseEnsemble)
            tests/
                test_agent.py
                test_ensemble.py
                test_features.py
                test_data_access.py

        inventory/
            Dockerfile
            pyproject.toml
            src/
                config.py
                main.py
                agent.py                # InventoryAgent orchestrating the pipeline
                data_access.py          # InventoryDataAccess
                features.py             # InventoryFeatureBuilder (depletion, days-of-supply)
                mcp/
                    tools.py            # MCP tool declarations (read_stock_levels, etc.)
                models/
                    xgboost_model.py    # InventoryXGBoostTrainer / InventoryXGBoostInference
                    statistical_model.py
                    ensemble.py         # InventoryEnsemble(BaseEnsemble)
            tests/
                test_agent.py
                test_ensemble.py
                test_features.py

models/
    demand/                             # Versioned trained model artifacts
    inventory/                          # Versioned trained model artifacts

scripts/
    verify_d3.py                        # Health, Agent Card, claim compliance, determinism checks
```

---

## Standalone Acceptance Criteria ("Definition of Done")
1. Both agent containers (`scof-demand-agent` on port 8011, `scof-inventory-agent` on port 8012) start successfully and return a rich health response confirming `profile_loaded`, `db_connected`, `model_loaded`, `model_version`, and `uptime_seconds`.
2. Each agent's `GET /.well-known/agent.json` returns a valid `AgentCard` with `version`, `tags`, `supported_contexts`, and `dependencies` fields.
3. Calling `POST /analyze` on each agent with a synthetic `ScenarioContext` (using the latest D1 simulation run) returns a valid `StructuredClaim` with all required fields: `recommendation`, `reasoning`, `confidence`, `priority`, `impact`, and `evidence[]` with traceable `reference_id` values.
4. Confidence values are within [0.0, 1.0] and are never clamped to `confidence_floor`. If confidence falls below the floor, `low_confidence=True` is set.
5. Demand Agent forecasts are plausible against D1 ground truth (MAE < 50% of actual mean on synthetic data).
6. Inventory Agent detects elevated stockout risk when a `supplier_delay` disruption is active, with reasoning referencing the disruption.
7. Calling each agent twice with the same scenario and random seeds produces identical structured claims (deterministic output).
8. Running `python scripts/verify_d3.py` or `make verify-d3` passes 100% of automated verification checks.
9. Running `pytest services/agents/demand/tests/ services/agents/inventory/tests/` passes 100%.
