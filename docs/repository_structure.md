# **SCOF — Repository Structure**

## **Complete Project Layout Before Implementation**

**Document Version:** 1.0 **Status:** Draft **Prepared for:** SCOF MVP Development (Docker-Simulation Phase)

**Source Documents:** SCOF Architecture, SRS, Implementation Plan, Domain Binding Strategy

---

## **1\. Design Principles**

| Principle | How It Shapes the Repo |
| ----- | ----- |
| **Monorepo** | All services, agents, frontend, infrastructure, docs, and profiles live in one repository. Simplifies cross-service refactoring, shared contracts, and Docker Compose orchestration. |
| **Service-per-directory** | Each deployable unit (API, agent, frontend) gets its own top-level directory with its own Dockerfile, dependency file, and tests. |
| **Deliverable traceability** | Every deliverable (D1–D11) has a dedicated docs folder linking requirements, design decisions, and acceptance evidence. |
| **Profile-driven** | Domain Profiles are a first-class directory at the repo root — not buried inside a service. |
| **Shared contracts** | Common schemas (Structured Claim, Agent Card, event formats) live in a shared library, imported by all Python services. |
| **Infrastructure as code** | Docker Compose files, database init scripts, and environment configs are versioned alongside application code. |

---

## **2\. Complete Repository Tree**

```
SCOF/

 .github/                                    # CI/CD and GitHub configuration
    workflows/
       ci.yml                              # Lint + test on every PR
       build.yml                           # Docker build verification
       evaluation.yml                      # D10 benchmark run (manual trigger)
    ISSUE_TEMPLATE/
       bug_report.md
       feature_request.md
       deliverable_task.md                 # Template tied to D1–D11 tracking
    PULL_REQUEST_TEMPLATE.md

 docs/                                       # All project documentation
    ideation.md                             # FINAL_SCOF_Ideation.md (moved here)
    srs.md                                  # SCOF SRS (moved here)
    architecture.md                         # SCOF Architecture (moved here)
    implementation_plan.md                  # Implementation Plan (moved here)
    domain_binding_strategy.md              # Domain Binding Strategy (moved here)
    repository_structure.md                 # This document (moved here)
   
    deliverables/                           # Per-deliverable documentation
       D01_simulation_data/
          README.md                       # D1 overview, objectives, acceptance criteria
          implementation_plan.md          # D1 implementation plan
          design_decisions.md             # Generator architecture, data model choices
          schema_design.md                # PostgreSQL schema definitions
          data_dictionary.md              # Entity fields, types, constraints
          acceptance_evidence.md          # Test results proving "done"
          walkthrough.md                  # D1 walkthrough
      
       D02_knowledge_layer/
          README.md                       # D2 overview, objectives, acceptance criteria
          neo4j_schema.md                 # Graph schema: nodes, relationships, properties
          pgvector_schema.md              # Vector store tables, embedding strategy
          etl_design.md                   # ETL pipeline design and idempotency approach
          acceptance_evidence.md          # Test results proving "done"
          walkthrough.md   
      
       D03_demand_inventory_agents/
          README.md                       # D3 overview, objectives, acceptance criteria
          demand_agent_design.md          # Model selection, ensemble strategy, MCP tools
          inventory_agent_design.md       # Model selection, ensemble strategy, MCP tools
          model_evaluation.md             # Forecast accuracy against D1 ground truth
          acceptance_evidence.md          # Test results proving "done"
          walkthrough.md                  # D3 walkthrough
      
       D04_supplier_transport_agents/
          README.md                       # D4 overview, objectives, acceptance criteria
          supplier_agent_design.md        # Reliability scoring, Neo4j queries, MCP tools
          transport_agent_design.md       # Delay prediction, rerouting logic, MCP tools
          model_evaluation.md             # Prediction accuracy against D1 disruptions
          acceptance_evidence.md
      
       D05_orchestration/
          README.md                       # D5 overview, objectives, acceptance criteria
          langgraph_design.md             # State graph topology, node definitions
          mcp_server_design.md            # MCP server specifications per agent
          a2a_protocol_design.md          # Agent Card schema, discovery mechanism
          acceptance_evidence.md
      
       D06_consensus_engine/
          README.md                       # D6 overview, objectives, acceptance criteria
          cd2f_algorithm_design.md        # Arbitration pipeline, weighting, escalation
          calibration_design.md           # Judge calibration, Cohen's kappa methodology
          baseline_design.md              # Single-agent and naive voting baselines
          fixture_test_cases.md           # Hand-worked expected outputs
          acceptance_evidence.md
      
       D07_observability/
          README.md                       # D7 overview, objectives, acceptance criteria
          tracing_design.md               # LangSmith/Langfuse integration approach
          trace_schema.md                 # Decision trace storage schema
          acceptance_evidence.md
      
       D08_backend_api/
          README.md                       # D8 overview, objectives, acceptance criteria
          api_design.md                   # Endpoint specifications, request/response schemas
          event_bus_design.md             # Kafka/RabbitMQ topic design
          websocket_design.md             # Channel specifications, payload formats
          acceptance_evidence.md
      
       D09_desktop_operations_console/
          README.md                       # D9 overview, objectives, acceptance criteria
          implementation_plan.md          # D9 implementation plan
          component_design.md             # React component hierarchy, view specifications
          ui_ux_design.md                 # Wireframes, interaction patterns
          desktop_integration.md          # Tauri native features: tray, notifications, window
          type_contract.md                # OpenAPI codegen strategy, WebSocket type definitions
          acceptance_evidence.md
      
       D10_integration_evaluation/
          README.md                       # D10 overview, objectives, acceptance criteria
          evaluation_harness_design.md    # Metrics computation, benchmark methodology
          benchmark_results.md            # CD²F vs. baselines results (filled post-run)
          rq_mapping.md                   # Results mapped to RQ1–RQ4
          acceptance_evidence.md
      
       D11_post_mvp_extensions/
           README.md                       # D11 overview, extension points summary
           risk_agent_interface.md          # Where Risk Agent plugs in
           finance_sustainability_weather.md # Where these agents attach
           cross_org_handoff.md             # Cross-organization A2A extension
           digital_twin_interface.md        # Digital Twin replay extension
           new_profile_deployment.md        # How a new Domain Profile deploys
   
    research/                               # Research-specific documentation
       research_questions.md               # RQ1–RQ4 definitions and methodology
       literature_review.md                # Related work, positioning
       paper_draft/                        # Academic paper workspace
           .gitkeep
   
    adr/                                    # Architecture Decision Records
        001_langgraph_over_crewai.md        # Why LangGraph was chosen
        002_kafka_vs_rabbitmq.md            # Message broker selection
        003_pgvector_over_dedicated_vectordb.md
        template.md                         # ADR template

 profiles/                                   # Domain Profiles (profile-driven config)
    mvp-electronics/                        # MVP Domain Profile
        profile.yaml                        # Top-level metadata (name, version, description)
        topology.yaml                       # Entities: manufacturers, suppliers, warehouses, DCs, routes
        agents.yaml                         # Active agents: model configs, MCP bindings, thresholds
        disruptions.yaml                    # Disruption catalog: types, parameters, propagation
        consensus.yaml                      # CD²F: escalation thresholds, impact scales, calibration
        data_bindings.yaml                  # MCP server configs, DB connection mappings
        evaluation.yaml                     # Metrics, baselines, scenario set references
        dashboard.yaml                      # View configuration, map bounds, entity labels
        scenarios/
            calibration_set.json            # Hand-labeled scenarios for judge calibration
            evaluation_set.json             # Scenarios for benchmark evaluation

 shared/                                     # Shared Python library (imported by all services)
    pyproject.toml                          # Package definition for `scof-shared`
    README.md
    scof_shared/
        __init__.py
        schemas/                            # Pydantic models for cross-service contracts
           __init__.py
           structured_claim.py             # StructuredClaim: recommendation, confidence, priority, impact, evidence
           agent_card.py                   # A2A Agent Card schema
           disruption_event.py             # Disruption event schema (from D1 generator → Kafka → D5)
           decision_record.py              # Final decision + reasoning trail + escalation tier
           meeting_log.py                  # AI Meeting Log entry schema
           evaluation_metrics.py           # Benchmark result schemas
        protocols/                          # Protocol helpers
           __init__.py
           mcp_client.py                   # MCP client base class / utilities
           a2a_client.py                   # A2A discovery and delegation client
           a2a_server.py                   # A2A Agent Card publishing server mixin
        profile/                            # Domain Profile loader
           __init__.py
           loader.py                       # Load and validate profile YAML files
           topology.py                     # Typed topology config model
           agents_config.py                # Typed agent roster config model
           disruptions_config.py           # Typed disruption catalog config model
           consensus_config.py             # Typed consensus tuning config model
           dashboard_config.py             # Typed dashboard config model
        database/                           # Shared DB connection utilities
           __init__.py
           postgres.py                     # PostgreSQL / pgvector connection factory
           neo4j.py                        # Neo4j driver factory
           redis.py                        # Redis connection factory
        messaging/                          # Shared message broker utilities
           __init__.py
           producer.py                     # Kafka/RabbitMQ producer abstraction
           consumer.py                     # Kafka/RabbitMQ consumer abstraction
        observability/                      # Shared tracing utilities
            __init__.py
            tracing.py                      # LangSmith/Langfuse trace setup helpers

 services/                                   # All deployable backend services
   
    simulation/                             # D1 — Simulation Environment & Synthetic Data
       Dockerfile
       pyproject.toml                      # Dependencies: faker, numpy, pandas, psycopg, etc.
       README.md
       src/
          __init__.py
          main.py                         # CLI entry point: generate data, inject disruptions
          entity_generator.py             # Reads topology.yaml → generates manufacturers, suppliers, etc.
          order_generator.py              # Generates order/inventory/shipment histories
          disruption_generator.py         # Reads disruptions.yaml → produces parameterized events
          db_writer.py                    # Writes generated data to PostgreSQL
       tests/
           __init__.py
           test_entity_generator.py
           test_disruption_generator.py
           test_db_writer.py
   
    etl/                                    # D2 — Knowledge & Data Layer ETL
       Dockerfile
       pyproject.toml                      # Dependencies: neo4j, psycopg, pgvector, pyyaml
       README.md
       src/
          __init__.py
          main.py                         # CLI entry point: run ETL pipeline
          neo4j_loader.py                 # Reads topology.yaml → builds Neo4j graph
          pgvector_seeder.py              # Seeds pgvector tables with initial embeddings
          validators.py                   # Post-ETL validation queries
       tests/
           __init__.py
           test_neo4j_loader.py
           test_pgvector_seeder.py
   
    agents/                                 # D3 + D4 — All specialist agents
      
       demand/                             # D3 — Demand Forecast Agent
          Dockerfile
          pyproject.toml                  # Dependencies: xgboost, prophet, chronos, fastapi, langgraph
          README.md
          src/
             __init__.py
             main.py                     # FastAPI app + A2A Agent Card endpoint
             agent.py                    # Core agent logic: observe → predict → claim
             models/
                __init__.py
                xgboost_model.py        # XGBoost demand forecast model
                prophet_model.py        # Prophet demand forecast model
                foundation_model.py     # Chronos-2 time-series foundation model
                ensemble.py             # Ensemble combiner (weighted average / stacking)
             mcp/
                __init__.py
                tools.py                # MCP tool definitions: read_sales, read_promotions, etc.
             claim_builder.py            # Constructs StructuredClaim from model output
          tests/
              __init__.py
              test_agent.py
              test_ensemble.py
              test_claim_builder.py
      
       inventory/                          # D3 — Inventory Agent
          Dockerfile
          pyproject.toml
          README.md
          src/
             __init__.py
             main.py
             agent.py
             models/
                __init__.py
                xgboost_model.py
                foundation_model.py
                ensemble.py
             mcp/
                __init__.py
                tools.py                # MCP tools: read_stock_levels, read_reorder_points, etc.
             claim_builder.py
          tests/
              __init__.py
              test_agent.py
              test_ensemble.py
      
       supplier/                           # D4 — Supplier Intelligence Agent
          Dockerfile
          pyproject.toml
          README.md
          src/
             __init__.py
             main.py
             agent.py
             models/
                __init__.py
                reliability_scorer.py   # Supplier reliability scoring model
             mcp/
                __init__.py
                tools.py                # MCP tools: query_supplier_graph, read_delivery_history, etc.
             claim_builder.py
          tests/
              __init__.py
              test_agent.py
              test_reliability_scorer.py
      
       transportation/                     # D4 — Transportation Agent
           Dockerfile
           pyproject.toml
           README.md
           src/
              __init__.py
              main.py
              agent.py
              models/
                 __init__.py
                 delay_predictor.py      # Delay prediction and rerouting model
              mcp/
                 __init__.py
                 tools.py                # MCP tools: query_route_network, estimate_delay, etc.
              claim_builder.py
           tests/
               __init__.py
               test_agent.py
               test_delay_predictor.py
   
    coordinator/                            # D5 — Coordinator Agent (Orchestration)
       Dockerfile
       pyproject.toml                      # Dependencies: langgraph, langsmith/langfuse, fastapi
       README.md
       src/
          __init__.py
          main.py                         # FastAPI app + orchestration entry point
          orchestrator.py                 # LangGraph state graph definition
          agent_discovery.py              # A2A agent discovery: reads agents.yaml + queries Agent Cards
          claim_collector.py              # Collects structured claims from all discovered agents
          state.py                        # LangGraph state definition (TypedDict / Pydantic)
       tests/
           __init__.py
           test_orchestrator.py
           test_agent_discovery.py
           test_claim_collector.py
   
    consensus/                              # D6 — CD²F Consensus Engine
       Dockerfile
       pyproject.toml                      # Dependencies: numpy, scipy, scikit-learn
       README.md
       src/
          __init__.py
          main.py                         # FastAPI app (or callable library)
          arbitration.py                  # Core: confidence-weighted voting pipeline
          escalation.py                   # Tiering logic: fast path / slow path / human
          calibration.py                  # Judge calibration: Cohen's kappa computation
          baselines/
             __init__.py
             single_agent.py             # Single-agent baseline
             naive_majority.py           # Naive majority voting baseline
          reasoning_trail.py              # Constructs reasoning trail + meeting log entries
       fixtures/                           # Test fixture data (mock claims for validation)
          agreement_case.json
          disagreement_case.json
          conflicting_evidence_case.json
       tests/
           __init__.py
           test_arbitration.py
           test_escalation.py
           test_calibration.py
           test_baselines.py
   
    observability/                          # D7 — Observability & Explainability Backend
       Dockerfile
       pyproject.toml                      # Dependencies: langsmith/langfuse, psycopg, pgvector
       README.md
       src/
          __init__.py
          main.py
          trace_persister.py              # Persists full decision traces to PostgreSQL/pgvector
          trace_retriever.py              # Retrieves traces for replay / API consumption
          calibration_logger.py           # Logs judge calibration metrics over time
          langsmith_integration.py        # LangSmith/Langfuse wiring into LangGraph
       tests/
           __init__.py
           test_trace_persister.py
           test_trace_retriever.py
   
    api/                                    # D8 — Backend API & Real-Time Layer
       Dockerfile
       pyproject.toml                      # Dependencies: fastapi, uvicorn, websockets, kafka-python/pika
       README.md
       src/
          __init__.py
          main.py                         # FastAPI application factory
          config.py                       # Settings, profile path, env vars
          routers/
             __init__.py
             scenarios.py                # POST /scenarios/trigger
             whatif.py                   # POST /whatif/run, GET /whatif/{id}/result
             dashboard.py                # GET /dashboard/state
             decisions.py                # GET /decisions/{id}/log, /confidence, /trace
             evaluation.py               # GET /evaluation/benchmark
             chat.py                     # POST /chat/query (AI Chat)
             profile.py                  # GET /profile/active
          websocket/
             __init__.py
             manager.py                  # WebSocket connection manager
             channels.py                 # Channel definitions: dashboard/state, decisions/live, agents/activity
          events/
             __init__.py
             bus.py                      # Kafka/RabbitMQ event bus abstraction
             handlers.py                 # Event handlers: disruption → agent pipeline
             topics.py                   # Topic/queue definitions
          middleware/
              __init__.py
              error_handler.py            # Global error handling middleware
       tests/
           __init__.py
           test_scenarios.py
           test_whatif.py
           test_decisions.py
           test_websocket.py
   
    evaluation/                             # D10 — Evaluation Harness
        Dockerfile
        pyproject.toml                      # Dependencies: numpy, pandas, scikit-learn, matplotlib
        README.md
        src/
           __init__.py
           main.py                         # CLI entry point: run benchmarks
           harness.py                      # Orchestrates: scenario run → collect metrics → compare
           metrics/
              __init__.py
              decision_quality.py         # Decision accuracy, consensus quality, agreement rate
              prediction_quality.py       # Per-model forecast accuracy, calibration
              operational_impact.py       # Response time, risk reduction, inventory cost, fill rate
              calibration.py              # Judge calibration kappa over time
           benchmarks/
              __init__.py
              cd2f_benchmark.py           # Full CD²F benchmark run
              single_agent_benchmark.py   # Single-agent baseline benchmark
              majority_voting_benchmark.py # Naive majority voting benchmark
           reporting/
               __init__.py
               report_generator.py         # Generates markdown/HTML results report
               rq_mapper.py                # Maps results to RQ1–RQ4
        results/                            # Benchmark results output directory
           .gitkeep
        tests/
            __init__.py
            test_harness.py

 desktop/                                    # D09 — SCOF Desktop Operations Console
    src-tauri/                              # Tauri native layer (Rust, kept thin)
       Cargo.toml
       tauri.conf.json                     # Window config, app metadata, permissions
       icons/                              # Application icons (all platforms)
       src/
          main.rs                         # Tauri entry point
          tray.rs                         # System tray setup and menu
          notifications.rs                # Desktop notification dispatch
          window.rs                       # Window state persistence
    src/                                    # React + TypeScript UI
       main.tsx                            # React entry point
       App.tsx                             # Root layout
       App.module.css                      # Root layout styles
       index.css                           # Design system tokens (CSS custom properties)
       api/                                # D08 communication layer
          client.ts                       # REST client
          client.test.ts
          websocket.ts                    # WebSocket connection manager
          websocket.test.ts
          generated/
             types.ts                    # TypeScript types from Pydantic schemas
          ws-types.ts                     # WebSocket event payload types
       stores/                             # Zustand state management
          connectionStore.ts              # D08 connection state
          connectionStore.test.ts
          dashboardStore.ts               # Dashboard operational state
          decisionStore.ts                # Decision list and detail cache
          agentStore.ts                   # Agent activity and status
          scenarioStore.ts                # Scenario library and active scenario state
       hooks/                              # Custom React hooks
          useDashboardState.ts
          useDecisions.ts
          useAgentActivity.ts
          useWebSocket.ts
          useProfile.ts
          usePolling.ts
       views/                              # Top-level view components
          Operations/
          Scenarios/
          DecisionCenter/
          AgentCommand/
          WhatIfLab/
          ReasoningTrace/
          Evaluation/
          Settings/
       components/                         # Reusable UI components
          layout/
          cards/
          charts/
          map/
          meeting-log/
          chat/
       utils/                              # Utility functions
          formatters.ts
          constants.ts
    package.json                            # Dependencies: react, zustand, recharts, d3, leaflet, etc.
    tsconfig.json
    vite.config.ts                          # Vite bundler configuration (Tauri default)
    index.html                              # HTML entry point (Vite)
    .eslintrc.cjs

 infrastructure/                             # Docker, database init, and deployment configs
   
    docker/                                 # Dockerfiles that aren't service-specific
       docker-compose.yml                  # Full Docker Compose: all services + infra
   
    docker-compose.yml                      # Root-level symlink or primary compose file
    docker-compose.override.yml             # Dev overrides (hot-reload, debug ports)
   
    database/                               # Database initialization scripts
       postgres/
          01_init_schema.sql              # Core PostgreSQL schema (orders, inventory, suppliers, shipments)
          02_pgvector_schema.sql          # pgvector tables (decision_records, evidence_snippets, embeddings)
          03_seed_data.sql                # Optional seed data (run after ETL for testing)
       neo4j/
          constraints.cypher              # Neo4j constraints and indexes
       redis/
           redis.conf                      # Redis configuration
   
    kafka/                                  # Kafka configuration
       topics.sh                           # Script to create Kafka topics
       kafka.properties                    # Broker configuration overrides
   
    nginx/                                  # Reverse proxy (optional, for production)
        nginx.conf

 scripts/                                    # Developer and operational scripts
    setup.sh                                # One-command dev environment setup (Linux/Mac)
    setup.ps1                               # One-command dev environment setup (Windows)
    generate_data.sh                        # Run D1 synthetic data generation
    run_etl.sh                              # Run D2 ETL pipeline
    run_evaluation.sh                       # Run D10 evaluation harness
    lint.sh                                 # Run all linters (ruff, eslint, mypy)
    test_all.sh                             # Run all tests across services
    clean.sh                                # Clean generated data, containers, volumes

 .env.example                                # Environment variable template
 .env                                        # Local environment variables (gitignored)
 .gitignore                                  # Comprehensive gitignore
 .pre-commit-config.yaml                     # Pre-commit hooks (ruff, black, eslint, prettier)
 pyproject.toml                              # Root-level Python config (workspace / monorepo tooling)
 Makefile                                    # Convenience targets: make up, make test, make generate, etc.
 LICENSE
 README.md                                   # Project overview, quickstart, architecture summary
```

---

## **3\. File-by-File Explanation: Key Configuration Files**

### **3.1 Root Configuration**

| File | Purpose |
| ----- | ----- |
| `pyproject.toml` | Root-level Python configuration. Defines monorepo workspace (if using uv/hatch workspaces), shared linting rules (ruff), and formatting (black). Does **not** define dependencies — each service has its own. |
| `Makefile` | Developer convenience targets: `make up` (docker compose up), `make test` (run all tests), `make generate` (run D1 data gen), `make etl` (run D2 ETL), `make evaluate` (run D10 benchmarks), `make lint`, `make clean`. |
| `.env.example` | Template for environment variables used by Docker Compose and services. |
| `.pre-commit-config.yaml` | Pre-commit hooks: ruff (Python linting), black (Python formatting), eslint + prettier (TypeScript/JS), YAML lint, markdown lint. |
| `.gitignore` | Ignores: `.env`, `__pycache__`, `.venv`, `node_modules`, `*.pyc`, `.next`, `dist/`, `results/`, Docker volumes, model artifacts (`*.pt`, `*.pkl`, `*.joblib`). |

### **3.2 Environment Variables (`.env.example`)**

```env
#  General 
SCOF_PROFILE_PATH=./profiles/mvp-electronics
SCOF_ENV=development                            # development | staging | production

#  PostgreSQL 
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=scof
POSTGRES_USER=scof
POSTGRES_PASSWORD=changeme

#  Neo4j 
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme

#  Redis 
REDIS_HOST=redis
REDIS_PORT=6379

#  Kafka 
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

#  Agent Ports 
COORDINATOR_PORT=8010
DEMAND_AGENT_PORT=8011
INVENTORY_AGENT_PORT=8012
SUPPLIER_AGENT_PORT=8013
TRANSPORT_AGENT_PORT=8014

#  API 
API_PORT=8000
API_HOST=0.0.0.0

#  Frontend 
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

#  Observability 
LANGSMITH_API_KEY=                               # Leave blank to use Langfuse instead
LANGFUSE_HOST=http://langfuse:4000
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

---

## **4\. Dependency Files**

### **4.1 Python Services**

Each Python service uses `pyproject.toml` with its own dependency list. All services depend on the `scof-shared` library via a path reference.

#### **Shared Library (`shared/pyproject.toml`)**

```toml
[project]
name = "scof-shared"
version = "0.1.0"
description = "Shared schemas, protocols, and utilities for SCOF services"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "psycopg[binary]>=3.1",
    "pgvector>=0.3",
    "neo4j>=5.0",
    "redis>=5.0",
    "kafka-python>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### **Per-Service Dependencies**

| Service | Key Dependencies |
| ----- | ----- |
| `services/simulation/` | `faker`, `numpy`, `pandas`, `psycopg[binary]`, `pyyaml`, `scof-shared` |
| `services/etl/` | `neo4j`, `psycopg[binary]`, `pgvector`, `pyyaml`, `scof-shared` |
| `services/agents/demand/` | `fastapi`, `uvicorn`, `xgboost`, `prophet`, `torch`, `chronos`, `langgraph`, `scof-shared` |
| `services/agents/inventory/` | `fastapi`, `uvicorn`, `xgboost`, `torch`, `chronos`, `langgraph`, `scof-shared` |
| `services/agents/supplier/` | `fastapi`, `uvicorn`, `scikit-learn`, `neo4j`, `langgraph`, `scof-shared` |
| `services/agents/transportation/` | `fastapi`, `uvicorn`, `scikit-learn`, `neo4j`, `langgraph`, `scof-shared` |
| `services/coordinator/` | `fastapi`, `uvicorn`, `langgraph`, `langsmith` or `langfuse`, `scof-shared` |
| `services/consensus/` | `fastapi`, `uvicorn`, `numpy`, `scipy`, `scikit-learn`, `scof-shared` |
| `services/observability/` | `langsmith` or `langfuse`, `psycopg[binary]`, `pgvector`, `scof-shared` |
| `services/api/` | `fastapi`, `uvicorn`, `websockets`, `kafka-python`, `scof-shared` |
| `services/evaluation/` | `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `scof-shared` |

### **4.2 Frontend (`frontend/package.json`)**

```json
{
  "name": "scof-dashboard",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "d3": "^7.0.0",
    "recharts": "^2.0.0",
    "leaflet": "^1.9.0",
    "react-leaflet": "^5.0.0",
    "@types/leaflet": "^1.9.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^19.0.0",
    "@types/node": "^22.0.0",
    "tailwindcss": "^4.0.0",
    "postcss": "^8.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.0.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^16.0.0",
    "playwright": "^1.40.0"
  }
}
```

---

## **5\. Docker Compose Configuration**

### **5.1 Primary Compose File (`docker-compose.yml`)**

```yaml
version: "3.9"

services:
  #  Infrastructure 
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./infrastructure/database/postgres:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      retries: 5

  neo4j:
    image: neo4j:5
    ports: ["7474:7474", "7687:7687"]
    environment:
      NEO4J_AUTH: ${NEO4J_USER}/${NEO4J_PASSWORD}
    volumes:
      - neo4jdata:/data
      - ./infrastructure/database/neo4j:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD", "neo4j", "status"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redisdata:/data
      - ./infrastructure/database/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
    command: redis-server /usr/local/etc/redis/redis.conf

  kafka:
    image: confluentinc/cp-kafka:7.7.0
    ports: ["9092:9092"]
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      CLUSTER_ID: "scof-cluster-001"
    volumes:
      - kafkadata:/var/lib/kafka/data

  #  Agents (D3 + D4) 
  demand-agent:
    build: ./services/agents/demand
    ports: ["${DEMAND_AGENT_PORT}:8000"]
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro
    depends_on:
      postgres: { condition: service_healthy }

  inventory-agent:
    build: ./services/agents/inventory
    ports: ["${INVENTORY_AGENT_PORT}:8000"]
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro
    depends_on:
      postgres: { condition: service_healthy }

  supplier-agent:
    build: ./services/agents/supplier
    ports: ["${SUPPLIER_AGENT_PORT}:8000"]
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro
    depends_on:
      neo4j: { condition: service_healthy }

  transport-agent:
    build: ./services/agents/transportation
    ports: ["${TRANSPORT_AGENT_PORT}:8000"]
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro
    depends_on:
      neo4j: { condition: service_healthy }

  #  Coordinator (D5) 
  coordinator:
    build: ./services/coordinator
    ports: ["${COORDINATOR_PORT}:8000"]
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro
    depends_on:
      - demand-agent
      - inventory-agent
      - supplier-agent
      - transport-agent
      - kafka

  #  Consensus Engine (D6) 
  consensus:
    build: ./services/consensus
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro

  #  API (D8) 
  api:
    build: ./services/api
    ports: ["${API_PORT}:8000"]
    environment:
      SCOF_PROFILE_PATH: /profiles
    volumes:
      - ./profiles:/profiles:ro
    depends_on:
      - coordinator
      - consensus
      - postgres
      - redis
      - kafka

  #  Frontend (D9) 
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://api:8000
      NEXT_PUBLIC_WS_URL: ws://api:8000
    depends_on:
      - api

volumes:
  pgdata:
  neo4jdata:
  redisdata:
  kafkadata:
```

### **5.2 Dev Override (`docker-compose.override.yml`)**

```yaml
version: "3.9"

services:
  api:
    volumes:
      - ./services/api/src:/app/src     # Hot-reload source
    command: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    volumes:
      - ./frontend/src:/app/src         # Hot-reload source
    command: npm run dev
```

---

## **6\. Makefile Targets**

```makefile
.PHONY: up down test lint generate etl evaluate clean

up:                                    ## Start all services
	docker compose up -d

down:                                  ## Stop all services
	docker compose down

build:                                 ## Build all Docker images
	docker compose build

generate:                              ## Run D1 synthetic data generation
	docker compose run --rm simulation python -m src.main

etl:                                   ## Run D2 ETL pipeline
	docker compose run --rm etl python -m src.main

test:                                  ## Run all tests
	@echo "=== Shared ===" && cd shared && python -m pytest
	@echo "=== Simulation ===" && cd services/simulation && python -m pytest
	@echo "=== ETL ===" && cd services/etl && python -m pytest
	@echo "=== Demand Agent ===" && cd services/agents/demand && python -m pytest
	@echo "=== Inventory Agent ===" && cd services/agents/inventory && python -m pytest
	@echo "=== Supplier Agent ===" && cd services/agents/supplier && python -m pytest
	@echo "=== Transport Agent ===" && cd services/agents/transportation && python -m pytest
	@echo "=== Coordinator ===" && cd services/coordinator && python -m pytest
	@echo "=== Consensus ===" && cd services/consensus && python -m pytest
	@echo "=== Observability ===" && cd services/observability && python -m pytest
	@echo "=== API ===" && cd services/api && python -m pytest
	@echo "=== Evaluation ===" && cd services/evaluation && python -m pytest
	@echo "=== Frontend ===" && cd frontend && npm test

lint:                                  ## Run all linters
	ruff check .
	cd frontend && npm run lint

evaluate:                              ## Run D10 evaluation harness
	docker compose run --rm evaluation python -m src.main

clean:                                 ## Clean generated data, volumes, caches
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf frontend/.next
```

---

## **7\. Service-to-Deliverable Mapping**

| Deliverable | Repo Location(s) | Docs Location |
| ----- | ----- | ----- |
| **D1** — Simulation & Synthetic Data | `services/simulation/`, `infrastructure/`, `profiles/` | `docs/deliverables/D01_simulation_data/` |
| **D2** — Knowledge & Data Layer | `services/etl/`, `infrastructure/database/` | `docs/deliverables/D02_knowledge_layer/` |
| **D3** — Demand + Inventory Agents | `services/agents/demand/`, `services/agents/inventory/` | `docs/deliverables/D03_demand_inventory_agents/` |
| **D4** — Supplier + Transport Agents | `services/agents/supplier/`, `services/agents/transportation/` | `docs/deliverables/D04_supplier_transport_agents/` |
| **D5** — Orchestration & Protocol Layer | `services/coordinator/`, `shared/scof_shared/protocols/` | `docs/deliverables/D05_orchestration/` |
| **D6** — CD²F Consensus Engine | `services/consensus/` | `docs/deliverables/D06_consensus_engine/` |
| **D7** — Observability & Explainability | `services/observability/`, `shared/scof_shared/observability/` | `docs/deliverables/D07_observability/` |
| **D8** — Backend API & Real-Time | `services/api/` | `docs/deliverables/D08_backend_api/` |
| **D9** — Frontend Dashboard | `frontend/` | `docs/deliverables/D09_frontend_dashboard/` |
| **D10** — Integration & Evaluation | `services/evaluation/` | `docs/deliverables/D10_integration_evaluation/` |
| **D11** — Post-MVP Extension Points | — (docs only) | `docs/deliverables/D11_post_mvp_extensions/` |
| **Shared Contracts** | `shared/` | Inline in `shared/README.md` |
| **Domain Profiles** | `profiles/` | `docs/domain_binding_strategy.md` |

---

## **8\. Testing Strategy**

| Test Type | Tool | Location | When |
| ----- | ----- | ----- | ----- |
| **Unit tests** (Python) | `pytest` | `services/<service>/tests/` | Every PR (CI) |
| **Unit tests** (Frontend) | `jest` + React Testing Library | `frontend/tests/components/` | Every PR (CI) |
| **Integration tests** | `pytest` + Docker Compose | `services/<service>/tests/` (marked `@pytest.mark.integration`) | Pre-merge |
| **E2E tests** | Playwright | `frontend/tests/e2e/` | Pre-release |
| **Contract tests** | `pytest` + Pydantic validation | `shared/` tests | Every PR |
| **Benchmark tests** | Custom harness (D10) | `services/evaluation/` | Manual trigger |

---

## **9\. Gitignore**

```gitignore
#  Python 
__pycache__/
*.py[cod]
*.pyo
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/

#  Node / Frontend 
node_modules/
.next/
out/

#  Environment 
.env
.env.local
.env.*.local

#  Docker 
docker-compose.override.yml

#  IDE 
.vscode/
.idea/
*.swp
*.swo

#  Model Artifacts 
*.pt
*.pth
*.pkl
*.joblib
*.onnx
models/checkpoints/

#  Data & Results 
services/evaluation/results/*.json
services/evaluation/results/*.html
services/evaluation/results/*.csv

#  OS 
.DS_Store
Thumbs.db
```

---

## **10\. Implementation Order Checklist**

This is the order in which directories should be populated with code, matching the deliverable dependency graph:

| Step | What to Build | Directories Involved |
| ----- | ----- | ----- |
| **0** | Repo scaffolding — create all directories, config files, `pyproject.toml`s, `Dockerfile`s, `.gitignore`, `Makefile` | All |
| **1** | MVP Domain Profile | `profiles/mvp-electronics/` |
| **2** | Docker Compose + DB init scripts | `infrastructure/`, root `docker-compose.yml` |
| **3** | Shared library (schemas, profile loader) | `shared/` |
| **4** | D1: Synthetic data generator | `services/simulation/` |
| **5** | D2: ETL pipeline | `services/etl/` |
| **6** | D3: Demand + Inventory agents | `services/agents/demand/`, `services/agents/inventory/` |
| **7** | D4: Supplier + Transport agents | `services/agents/supplier/`, `services/agents/transportation/` |
| **8** | D5: Coordinator + orchestration | `services/coordinator/` |
| **9** | D6: CD²F consensus engine | `services/consensus/` |
| **10** | D7: Observability backend | `services/observability/` |
| **11** | D8: Backend API + real-time layer | `services/api/` |
| **12** | D9: Frontend dashboard | `frontend/` |
| **13** | D10: Evaluation harness + benchmarks | `services/evaluation/` |
| **14** | D11: Extension interface docs | `docs/deliverables/D11_post_mvp_extensions/` |
