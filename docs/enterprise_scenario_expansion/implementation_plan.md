# Implementation Plan: Enterprise South Indian Supply Chain Scenario Expansion (25 Scenarios)

## 1. Executive Summary & Core Concept

### 1.1 Context & Motivation
Following the transition of the SCOF (Supply Chain Cognitive Orchestration Framework) platform to the **Enterprise South Indian Electronics Manufacturing Topology** (18 nodes, 48 routes, 3 products), the operational scenario portfolio was initially seeded with 5 foundational scenarios (`scen-01` through `scen-05`). 

While these baseline scenarios validated the core autonomous loop and agent-to-agent (A2A) discovery, real-world electronics manufacturing in peninsular India entails a diverse spectrum of systemic failure modes. To test the full capability of the multi-agent cognitive fleet, the platform requires an expanded portfolio of **25 distinct, production-grade operational scenarios** (5 existing + 20 new scenarios) that comprehensively cover upstream semiconductor cleanroom halts, regional demand spikes, interstate highway blockades, facility AS/RS crane malfunctions, customs bonded FTWZ clearance holds, multimodal seaport siltation, and catastrophic cyclonic weather events.

### 1.2 Core Objectives
This implementation plan establishes the engineering roadmap to integrate the 20 new scenarios into the SCOF microservice architecture:
1. **Catalog Expansion (S1)**: Author the comprehensive operational reference book (`scenario_description_book.md`) establishing failure mechanics, multi-agent conflict dynamics, winning consensus actions, and performance targets for all 25 scenarios.
2. **Simulation & Database Seeding (S2)**: Update `services/simulation/src/disruption_generator.py` to synthetically generate scenarios `scen-01` through `scen-25` with parameterized disruption events seeded directly into PostgreSQL (`scof.scenarios` and `scof.disruption_events`).
3. **What-If Predictive Engine Expansion (S3)**: Extend the counterfactual simulation engine in `services/api/src/routers/whatif.py` and `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` to support all 25 base scenarios with dynamic Rupee cost variance calculation.
4. **Desktop Operations Console Integration (S4)**: Update `desktop/src/views/Scenarios/ScenariosView.tsx` with all 25 scenarios, full search/filtering, and seamless execution triggers.
5. **Quality Assurance & Acceptance Gate (S5)**: Validate that all 25 scenarios execute end-to-end within the sub-500ms Fast-Path SLA, maintain CD2F consensus stability >= 0.880, and adhere strictly to zero-emoji constraints.

---

## 2. Deliverables Structure (S1 through S5)

```
[ S1: Master Scenario Description Book ]
                    │
                    ▼
[ S2: Synthetic Generator & Seeding ] ──► [ S3: Counterfactual Engine Update ]
                    │                                     │
                    ├─────────────────────────────────────┤
                    ▼                                     ▼
[ S4: Desktop Operations Console UX ] ◄───────────────────┘
                    │
                    ▼
[ S5: End-to-End Verification, Benchmarking & Acceptance Gate ]
```

### Deliverable S1: Master Scenario Description Book
- **Scope**: Document all 25 operational scenarios with complete domain grounding in South India, conflict tension analysis, and ground-truth consensus actions.
- **Output**: [`scenario_description_book.md`](scenario_description_book.md) fully authored and integrated into documentation index.

### Deliverable S2: Simulation Engine & Disruption Seeding Updates
- **Scope**: Update `services/simulation/src/disruption_generator.py` to generate scenarios `scen-01` to `scen-25` with parameterized disruption specs, severities, and durations. Execute database reseeding script to populate PostgreSQL.
- **Output**: Populated `scof.scenarios` and `scof.disruption_events` tables containing all 25 scenarios.

### Deliverable S3: Counterfactual Simulation Lab Mathematical Matrix Expansion
- **Scope**: Extend `services/api/src/routers/whatif.py` to accept all 25 base scenarios, provide tailored counterfactual consensus actions for all nodes, and return dynamic INR cost variance.
- **Output**: Hot-deployed API gateway returning realistic what-if simulations for any scenario selection.

### Deliverable S4: Desktop Operations Console & Scenario Launcher UX Modernization
- **Scope**: Update `desktop/src/views/Scenarios/ScenariosView.tsx` and `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` with the complete 25-scenario portfolio, category indicators, search filter, and reactive trigger states.
- **Output**: Clean frontend production build via `npm run build` with full desktop operational accessibility.

### Deliverable S5: End-to-End Test Suite, Observability Traces, and Acceptance Gate
- **Scope**: Execute test scripts verifying that scenarios trigger successfully, dispatch events to Kafka, execute LangGraph agent coordination, and log immutable decision records to PostgreSQL.
- **Output**: Comprehensive verification report confirming all 25 scenarios pass acceptance criteria.

---

## 3. Core File Changes & Technical Specifications

### 3.1 File 1: `services/simulation/src/disruption_generator.py` (Deliverable S2)
**Purpose**: Generates the 25 scenario records and associated disruption shock events.

```python
# Expansion of scenario definitions from 5 to 25 items
scenarios = [
    # Baseline & Core Proofs (scen-01 to scen-05)
    {"scenario_id": f"{Prefix.SCENARIO}01", "name": "Baseline Nominal Operations", ...},
    {"scenario_id": f"{Prefix.SCENARIO}02", "name": "Tier-1 Semiconductor Packaging Delay (SPEL Chennai)", ...},
    {"scenario_id": f"{Prefix.SCENARIO}03", "name": "Automotive Sensor Demand Surge (Oragadam Hub)", ...},
    {"scenario_id": f"{Prefix.SCENARIO}04", "name": "NH48 Arterial Freight Corridor Monsoon Inundation", ...},
    {"scenario_id": f"{Prefix.SCENARIO}05", "name": "Cochin Port Vallarpadam Terminal Cyclonic Stoppage", ...},
    
    # Upstream Supplier Shortages (scen-06 to scen-10)
    {"scenario_id": f"{Prefix.SCENARIO}06", "name": "Discrete Power Fab Cleanroom Outage (CDIL Bengaluru)", ...},
    {"scenario_id": f"{Prefix.SCENARIO}07", "name": "Automotive Telematics SMT Head Failure (Kaynes Mysuru)", ...},
    {"scenario_id": f"{Prefix.SCENARIO}08", "name": "Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur)", ...},
    {"scenario_id": f"{Prefix.SCENARIO}09", "name": "Aerospace Sub-Module Allocation Rationing (Centum Yelahanka)", ...},
    {"scenario_id": f"{Prefix.SCENARIO}10", "name": "High-Density PCB Copper Laminate Stockout (Sahasra Hyderabad)", ...},
    
    # Downstream Demand Shocks (scen-11 to scen-14)
    {"scenario_id": f"{Prefix.SCENARIO}11", "name": "Smart Energy IoT Meter Mandate Demand Surge", ...},
    {"scenario_id": f"{Prefix.SCENARIO}12", "name": "Commercial Fleet EV Powertrain Retrofit Spike", ...},
    {"scenario_id": f"{Prefix.SCENARIO}13", "name": "Quarter-End Automotive OEM Assembly Ramp-Up", ...},
    {"scenario_id": f"{Prefix.SCENARIO}14", "name": "Coastal Municipal Sensor Network Renewal Push", ...},
    
    # Freight & Route Disruptions (scen-15 to scen-18)
    {"scenario_id": f"{Prefix.SCENARIO}15", "name": "Attibele Interstate Border Truck Checkpost Strike", ...},
    {"scenario_id": f"{Prefix.SCENARIO}16", "name": "Palakkad Gap Western Ghats Landslide Corridor Halt", ...},
    {"scenario_id": f"{Prefix.SCENARIO}17", "name": "NH44 Kurnool Bridge Heavy-Axle Weight Embargo", ...},
    {"scenario_id": f"{Prefix.SCENARIO}18", "name": "Chennai Outer Ring Road Heavy Freight Gridlock", ...},
    
    # Warehouse & Facility Shocks (scen-19 to scen-21)
    {"scenario_id": f"{Prefix.SCENARIO}19", "name": "Hosur Buffer Automated AS/RS Crane System Fault", ...},
    {"scenario_id": f"{Prefix.SCENARIO}20", "name": "Sri City FTWZ Regulatory Customs Audit Clearance Hold", ...},
    {"scenario_id": f"{Prefix.SCENARIO}21", "name": "Whitefield Inland Container Depot Rail Rake Deficit", ...},
    
    # Multimodal Seaport & Airport Terminal Shocks (scen-22 to scen-23)
    {"scenario_id": f"{Prefix.SCENARIO}22", "name": "Chennai Port Shallow Channel Silting Berth Congestion", ...},
    {"scenario_id": f"{Prefix.SCENARIO}23", "name": "Shamshabad Aerotropolis Airfreight Cargo Crunch", ...},
    
    # Compound Catastrophes (scen-24 to scen-25)
    {"scenario_id": f"{Prefix.SCENARIO}24", "name": "Cyclone Michaung Coromandel Plain Compound Inundation", ...},
    {"scenario_id": f"{Prefix.SCENARIO}25", "name": "Peninsular Grid Blackout Sourcing Crisis", ...},
]
```

### 3.2 File 2: `services/api/src/routers/whatif.py` (Deliverable S3)
**Purpose**: Extends the counterfactual predictive router to map all 25 scenarios, compute node-specific impacts, and return formatted INR cost variances.

- Update `run_whatif`: Support default scenario binding for all 25 IDs (`scen-01` to `scen-25`).
- Maintain `COUNTERFACTUAL_PROFILES` with authentic actions for all 18 entities.
- Ensure output formatting uses `format_inr` and `+₹` currency prefixes.

### 3.3 File 3: `desktop/src/views/Scenarios/ScenariosView.tsx` (Deliverable S4)
**Purpose**: Presents all 25 scenarios in the Desktop Operations Console with search, filtering, and instant trigger actions.

- Define `DEFAULT_SCENARIOS`: 25 structured items with complete IDs, titles, descriptions, categories, target nodes, and default severities.
- Add category filter tabs: `All`, `Supplier Shortage`, `Demand Volatility`, `Logistics Failure`, `Facility Shock`, `Compound Crisis`.
- Add search filter input to quickly locate scenarios by node ID or keyword.

### 3.4 File 4: `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` (Deliverable S4)
**Purpose**: Expands the Base Scenario dropdown to encompass all 25 scenarios so operators can evaluate counterfactuals against any baseline scenario.

- Update `<select value={baseScenario}>` with 25 `<option>` tags.
- Retain instantaneous local simulation calculation alongside backend API queries.

---

## 4. Impact Analysis

### 4.1 Coordinator & Orchestration Kernel Impact
- **Non-Invasive Execution**: The LangGraph coordinator (`services/coordinator`) operates dynamically on incoming Kafka disruption envelopes (`scof.disruptions.triggered`). Expanding scenarios from 5 to 25 introduces zero coordinator code changes because the orchestration flow is completely data-driven.
- **Trace Context Propagation**: All 25 scenario IDs (`scen-01` through `scen-25`) map cleanly to trace correlation contexts.

### 4.2 Autonomous Specialist Fleet Impact
- **Demand Forecasting Agent (`demand-agent`)**: Evaluates scenarios `scen-03`, `scen-11`, `scen-12`, `scen-13`, `scen-14` using Prophet and XGBoost ensembles, triggering reorder recommendations.
- **Inventory Risk Agent (`inventory-agent`)**: Computes multi-echelon safety stock drawdown across Hosur (`wh-01`), Whitefield (`wh-02`), Oragadam (`wh-03`), and Sri City (`wh-04`).
- **Supplier Intelligence Agent (`supplier-agent`)**: Interrogates Neo4j graph for `[:ALTERNATE_FOR]` edges, calculating composite scores across CDIL, Centum, Syrma, Kaynes, Vinyas, and Sahasra.
- **Transportation Logistics Agent (`transport-agent`)**: Evaluates arterial highway detours along NH44, NH48, NH544, state highways, and intermodal rail connectors.

### 4.3 CD2F Consensus Engine Impact
- **Dynamic Weighting Calibration**: Exercises the CD2F formula $W_i = w_i \cdot c_i \cdot \prod (1 - p_{ij})$ across 25 distinct claim configurations.
- **Escalation Policy Adherence**:
  - `FAST_PATH` (< 500ms): Automated resolution for single-node disruptions with clear dominant claims.
  - `SLOW_PATH`: Deliberation requiring second-round consensus weighting (e.g., `scen-04`, `scen-11`, `scen-16`, `scen-20`).
  - `HUMAN_ESCALATION`: Triggered for compound or critical enterprise-level events (`scen-12`, `scen-24`, `scen-25`).

### 4.4 PostgreSQL Database & Neo4j Knowledge Layer Impact
- **PostgreSQL**: `scof.scenarios` stores 25 rows; `scof.disruption_events` stores 25 corresponding event rows. No schema modifications required.
- **Neo4j**: Unchanged. Existing 18-node topology with 48 routes supports all 25 scenario mappings.

---

## 5. Testing & Observability Suite

### 5.1 Synthetic Generator Unit Tests
Run unit tests verifying that all 25 scenarios are synthetically generated with valid dates, IDs, and severities:
```bash
python -m pytest services/simulation/tests/test_disruption_generator.py -v
```

### 5.2 Database Re-seeding & API Verification
Execute database reseeding and confirm all 25 scenarios are queryable via REST:
```bash
# Seed master scenarios into PostgreSQL
python -c "from services.simulation.src.db_writer import seed_scenarios; seed_scenarios()"

# Verify scenario list via API Gateway
curl -s http://localhost:8000/scenarios | jq '.scenarios | length'
# Expected output: 25
```

### 5.3 Automated Scenario Suite Verification Script
Create and execute `scripts/verify_scenario_suite.py` to trigger every scenario sequentially and verify:
1. Event dispatch into Kafka topic `scof.disruptions.triggered`.
2. Discovery of all 4 specialist agents.
3. CD2F consensus arbitration generation.
4. Decision persistence in `scof.decision_records`.
5. P90 latency under 500ms SLA.

```bash
python scripts/verify_scenario_suite.py
```

### 5.4 Desktop Frontend Compilation Verification
Verify that the React/TypeScript desktop console builds cleanly with zero errors:
```bash
cd desktop
npm run build
```

---

## 6. Evaluation & Acceptance Gate

To achieve formal sign-off for Deliverables S1 through S5, the implementation must satisfy all of the following criteria:

| Gate Criterion | Verification Method | Acceptance Standard |
| :--- | :--- | :--- |
| **G1: Scenario Catalog Completeness** | Database query `SELECT count(*) FROM scof.scenarios;` | Exactly 25 active scenarios seeded |
| **G2: Description Book Integrity** | Audit of `scenario_description_book.md` | Complete specifications for all 25 scenarios |
| **G3: Fast-Path Latency SLA** | Full loop automated benchmark | P50 < 350ms, P90 < 500ms |
| **G4: CD2F Consensus Stability** | Decision ledger inspection | WCS score >= 0.880 across all automated scenarios |
| **G5: Currency Formatting Compliance** | What-If Lab and API inspection | All cost deltas rendered in INR (`+₹...`) |
| **G6: Zero-Emoji Constraint** | Automated regex audit across codebase | Zero emojis across all modified files and markdown docs |
| **G7: Frontend Build Cleanliness** | `npm run build` in `desktop/` | Exit code 0, 0 TypeScript errors |
