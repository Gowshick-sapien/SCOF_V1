# Deliverable D4 -- Reliability Agent Slice: Supplier + Transportation

## Overview & Purpose

Deliverable D4 builds the two network & reliability-focused specialist AI agents as standalone, independently testable FastAPI microservices conforming to the universal Structured Claim contract. Unlike D3's time-series forecasting agents, D4 agents are graph-centric: they query Neo4j for supplier relationships, route networks, and alternate paths, combined with PostgreSQL delivery and shipment performance history to produce reliability scores, supplier failure predictions, transit delay estimates, and rerouting recommendations.

Each agent uses an ensemble strategy (scikit-learn ML model + rule-based scorer), publishes an A2A Agent Card, and declares MCP tool bindings for downstream protocol wiring in Deliverable D5.

---

## Requirements Summary (from SRS)

- **FR-4.1**: Implement a Supplier Intelligence Agent producing reliability scores and failure predictions from Neo4j graph data and historical delivery data, configured via `agents.yaml`.
- **FR-4.2**: Implement a Transportation Agent producing delay predictions and rerouting-option generation over the route network, configured via `agents.yaml`.
- **FR-4.3**: Both agents shall return a structured claim (recommendation, reasoning, confidence, priority, impact, evidence with traceable reference IDs) conforming to the universal Structured Claim contract, independent of other agents and MCP-connected.

---

## Prerequisites & Dependencies

- **Prerequisite Deliverables**: 
  - [D01_simulation_data](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D01_simulation_data/README.md) -- PostgreSQL contains synthetic `suppliers`, `supplier_products`, `purchase_orders`, `shipments`, `routes`, and `disruption_events` tables.
  - [D02_knowledge_layer](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D02_knowledge_layer/README.md) -- Neo4j contains the supply chain graph with Supplier, Product, Warehouse, Route nodes and relationships.
  - [D03_demand_inventory_agents](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D03_demand_inventory_agents/README.md) -- Shared schemas, ML base classes, and agent base classes operational.
- **Required System Tools**: Docker (v24+), Python 3.11+, PostgreSQL 16+ (with pgvector), Neo4j 5+.
- **Required Domain Profile Files**:
  - [profiles/mvp-electronics/topology.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/topology.yaml)
  - [profiles/mvp-electronics/disruptions.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/disruptions.yaml)
  - [profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml)

---

## Document Set in this Directory

1. [README.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/README.md) (this document): Overview, requirements, prerequisites, document map, and acceptance criteria.
2. [implementation_plan.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/implementation_plan.md): Detailed technical implementation plan, proposed file changes, and verification strategy for Deliverable D4.
3. [supplier_agent_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/supplier_agent_design.md): Supplier Intelligence Agent architecture -- Neo4j lineage queries, GradientBoostingClassifier, rule scorer initializer, alternate supplier ranking algorithm, MCP tool declarations, and sample claims.
4. [transport_agent_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/transport_agent_design.md): Transportation Agent architecture -- route network queries, GradientBoostingRegressor, rerouting engine, route ranking algorithm, MCP tool declarations, and sample claims.
5. [model_evaluation.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/model_evaluation.md): Evaluation metrics framework against D1 synthetic disruptions -- classification precision/recall, delay prediction MAE, prediction interval coverage (PICP), and ranking validity.
6. [acceptance_evidence.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/acceptance_evidence.md): Evidence verification log template for D4 acceptance criteria.
7. [walkthrough.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/walkthrough.md): Post-implementation walkthrough and verification evidence log.

---

## Module Structure

```
services/
    agents/
        supplier/
            Dockerfile
            pyproject.toml
            src/
                config.py               # Port 8013, thresholds, random seeds
                main.py                 # FastAPI app: /analyze, /health, /.well-known/agent.json
                agent.py                # SupplierAgent orchestrating graph + delivery history pipeline
                data_access.py          # SupplierDataAccess (PG queries + Neo4jGraphClient)
                features.py             # SupplierFeatureBuilder (on-time rate, lead time, hop count)
                mcp/
                    tools.py            # MCP tool declarations (query_supplier_graph, etc.)
                models/
                    reliability_scorer.py # GradientBoostingClassifier + residual calibration
                    rule_scorer.py        # RuleScorerInitializer + RuleScorerInference
                    ensemble.py           # SupplierEnsemble(BaseEnsemble)
            tests/
                test_supplier_agent.py
                test_reliability_scorer.py
                test_supplier_features.py
                test_supplier_data_access.py

        transportation/
            Dockerfile
            pyproject.toml
            src/
                config.py               # Port 8014, delay thresholds, random seeds
                main.py                 # FastAPI app: /analyze, /health, /.well-known/agent.json
                agent.py                # TransportAgent orchestrating route network + shipment pipeline
                data_access.py          # TransportDataAccess (PG queries + Neo4jGraphClient)
                features.py             # TransportFeatureBuilder (delay rate, transit dev, alt routes)
                mcp/
                    tools.py            # MCP tool declarations (query_route_network, etc.)
                models/
                    delay_predictor.py    # GradientBoostingRegressor + residual calibration
                    route_scorer.py        # RouteScorerInitializer + RouteScorerInference
                    ensemble.py           # TransportEnsemble(BaseEnsemble)
            tests/
                test_transport_agent.py
                test_delay_predictor.py
                test_transport_features.py
                test_transport_data_access.py

models/
    supplier/                           # Versioned trained model artifacts
    transportation/                     # Versioned trained model artifacts

scripts/
    verify_d4.py                        # Health, Agent Card, claim compliance, determinism checks
```

---

## Standalone Acceptance Criteria ("Definition of Done")

1. Both agent containers (`scof-supplier-agent` on port 8013, `scof-transport-agent` on port 8014) start successfully and return a rich health response confirming `profile_loaded`, `db_connected`, `neo4j_connected`, `model_loaded`, `model_version`, and `uptime_seconds`.
2. Each agent's `GET /.well-known/agent.json` returns a valid `AgentCard` with `version`, `tags`, `supported_contexts`, and `dependencies` fields.
3. Calling `POST /analyze` on each agent with a synthetic `ScenarioContext` returns a valid `StructuredClaim` with required fields: `recommendation`, `reasoning`, `confidence`, `priority`, `impact`, and `evidence[]` with traceable `reference_id` values.
4. Confidence values are within [0.0, 1.0] and are never clamped. If confidence falls below the agent's `confidence_floor`, `low_confidence=True` is set.
5. Supplier Agent identifies elevated vendor failure risk when a `supplier_delay` disruption is active and provides deterministically ranked alternate suppliers.
6. Transportation Agent predicts transit delay magnitude when a `transport_failure` or `adverse_weather` disruption is active and provides deterministically ranked rerouting options.
7. Calling each agent twice with the same scenario and random seeds produces identical structured claims (deterministic output).
8. Running `python scripts/verify_d4.py` passes 100% of automated verification checks.
9. Running `pytest services/agents/supplier/tests/ services/agents/transportation/tests/` passes 100%.
