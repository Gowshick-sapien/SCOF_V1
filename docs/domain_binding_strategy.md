# SCOF — Domain Binding Strategy

**Making SCOF Deployable Across Any Supply Chain Context Without Rebuilding**

---

## The Problem

SCOF is designed to be a **general-purpose multi-agent decision platform for supply chains** — but a supply chain is never general. Every deployment needs a concrete context: specific entities (how many suppliers, what products, which routes), specific disruption types that matter, specific agents whose domain expertise is relevant, and specific evaluation criteria that define "good."

The system cannot be built in a vacuum. It needs a **particular scope** to reason about. But it also shouldn't need to be **re-engineered** every time that scope changes.

This creates a tension:

| Need | Constraint |
|---|---|
| The platform should be reusable | But every supply chain is structurally different |
| Agents should be domain-agnostic | But their reasoning requires domain-specific data, thresholds, and relationships |
| CD²F should work universally | But escalation thresholds, confidence baselines, and impact scales are context-dependent |
| The dashboard should be consistent | But what's visualized depends on what entities and risks exist |

The question is: **how does SCOF bind to a specific supply chain environment without becoming inseparable from it?**

---

## Proposed Solution: Domain Profiles

Instead of hardcoding the supply chain context into the system, SCOF should treat its operating environment as a **configurable, declarative input** — a **Domain Profile**.

A Domain Profile is a single configuration artifact that captures everything SCOF needs to know about the supply chain it's operating in — without touching the platform's core code.

### What a Domain Profile Defines

```
┌───────────────────────────────────────────────────────────────┐
│                        DOMAIN PROFILE                         │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1. TOPOLOGY                                             │  │
│  │     What entities exist and how they connect              │  │
│  │     (suppliers, products, warehouses, routes, DCs)        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  2. AGENT ROSTER                                         │  │
│  │     Which agents are active and how they're configured    │  │
│  │     (models, thresholds, MCP tool bindings)               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  3. DISRUPTION CATALOG                                   │  │
│  │     What disruption types are relevant to this context    │  │
│  │     (parameters, severity scales, propagation rules)      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  4. CONSENSUS TUNING                                     │  │
│  │     CD²F thresholds and escalation rules for this domain  │  │
│  │     (confidence floors, impact scales, fast-path criteria)│  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  5. DATA BINDINGS                                        │  │
│  │     Where the data lives and how it maps to the platform  │  │
│  │     (DB schemas, MCP server configs, ETL mappings)        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  6. EVALUATION CRITERIA                                  │  │
│  │     What "good" means for this particular environment     │  │
│  │     (metrics, baselines, scenario sets)                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  7. DASHBOARD CONFIGURATION                              │  │
│  │     Which views are active and what labels/scales they    │  │
│  │     use (map coordinates, heatmap dimensions, entity      │  │
│  │     display names)                                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### The Core Idea

SCOF becomes a **profile-driven platform**:

```
SCOF Platform (unchanged)  +  Domain Profile (per deployment)  =  Running System
```

The platform provides the engine — agent orchestration, CD²F consensus, observability, API, dashboard shell. The profile provides the context — what to reason about, how aggressively to escalate, what thresholds matter.

---

## Profile Schema Design

### 1. Topology Definition

Instead of hardcoding "1 manufacturer, 5 suppliers, 2 warehouses," the topology is declared:

```yaml
# profile/topology.yaml

profile_name: "acme-electronics-southeast-asia"
profile_version: "1.0"

entities:
  manufacturers:
    - id: mfg-001
      name: "ACME Electronics - Shenzhen"
      location: { lat: 22.5431, lon: 114.0579 }
      products:
        - id: prod-001
          name: "Wireless Earbuds (Model X)"
          sku: "WEB-X-2026"
        - id: prod-002
          name: "Smart Speaker (Model S)"
          sku: "SS-S-2026"
        - id: prod-003
          name: "Bluetooth Module (BT-5.3)"
          sku: "BTM-53-2026"

  suppliers:
    - id: sup-001
      name: "ChipTech Semiconductors"
      location: { lat: 24.1477, lon: 120.6736 }
      reliability_profile: "high"       # high | medium | low | volatile
      supplies: [prod-001, prod-002]
      lead_time_days: { mean: 14, std_dev: 3 }
    - id: sup-002
      name: "BatteryMax Ltd"
      location: { lat: 37.5665, lon: 126.9780 }
      reliability_profile: "medium"
      supplies: [prod-001, prod-003]
      lead_time_days: { mean: 21, std_dev: 7 }
    # ... more suppliers

  warehouses:
    - id: wh-001
      name: "Hong Kong Regional Hub"
      location: { lat: 22.3193, lon: 114.1694 }
      capacity_units: 50000
      safety_stock_policy: "dynamic"    # static | dynamic
    - id: wh-002
      name: "Singapore Distribution Center"
      location: { lat: 1.3521, lon: 103.8198 }
      capacity_units: 30000
      safety_stock_policy: "static"

  distribution_centers:
    - id: dc-001
      name: "Sydney Last-Mile DC"
      location: { lat: -33.8688, lon: 151.2093 }

  routes:
    - id: route-001
      from: sup-001
      to: wh-001
      mode: "sea_freight"               # sea_freight | air_freight | road | rail
      transit_days: { mean: 5, std_dev: 1 }
      cost_per_unit: 2.30
    - id: route-002
      from: sup-001
      to: wh-001
      mode: "air_freight"
      transit_days: { mean: 1, std_dev: 0.2 }
      cost_per_unit: 12.50
    # ... alternative routes create the multi-route network
```

**What this enables:** The synthetic data generator (D1), the Neo4j graph (D2), and the dashboard map (D9) all derive their structure from this single source of truth. Change the topology file, and the entire system reshapes.

### 2. Agent Roster

```yaml
# profile/agents.yaml

active_agents:
  - agent_type: "demand"
    id: "demand-agent-v1"
    config:
      model_ensemble:
        - type: "xgboost"
          hyperparams: { n_estimators: 200, max_depth: 6 }
        - type: "prophet"
          hyperparams: { seasonality_mode: "multiplicative" }
        - type: "foundation_model"
          model_id: "chronos-2-base"
      data_sources:
        - mcp_server: "sales-data-server"
          tools: ["read_historical_sales", "read_promotions", "read_seasonality"]
      claim_config:
        confidence_floor: 0.60          # below this, flag as low-confidence
        historical_accuracy_window: 30  # rolling days for accuracy tracking

  - agent_type: "inventory"
    id: "inventory-agent-v1"
    config:
      model_ensemble:
        - type: "xgboost"
        - type: "foundation_model"
          model_id: "chronos-2-base"
      data_sources:
        - mcp_server: "inventory-data-server"
          tools: ["read_stock_levels", "read_reorder_points", "read_safety_stock"]
      claim_config:
        confidence_floor: 0.65
        historical_accuracy_window: 30

  - agent_type: "supplier"
    id: "supplier-agent-v1"
    config:
      data_sources:
        - mcp_server: "graph-data-server"
          tools: ["query_supplier_graph", "read_delivery_history", "find_alternates"]
      claim_config:
        confidence_floor: 0.55
        historical_accuracy_window: 60

  - agent_type: "transportation"
    id: "transport-agent-v1"
    config:
      data_sources:
        - mcp_server: "logistics-data-server"
          tools: ["read_shipment_status", "query_route_network", "estimate_delay"]
      claim_config:
        confidence_floor: 0.50
        historical_accuracy_window: 45

# Post-MVP agents — uncomment to activate (no code changes needed)
# - agent_type: "risk"
#   id: "risk-agent-v1"
#   config:
#     model: "gnn-risk-scorer"
#     data_sources:
#       - mcp_server: "graph-data-server"
#         tools: ["query_supplier_graph", "compute_node_risk", "identify_critical_paths"]
```

**What this enables:** Adding a new agent to SCOF means adding a block to this file and deploying the agent container. The Coordinator discovers it via A2A — no orchestration code changes. Removing an agent means commenting it out.

### 3. Disruption Catalog

```yaml
# profile/disruptions.yaml

disruption_types:
  - type: "supplier_delay"
    description: "A supplier fails to deliver on time"
    parameters:
      severity: { scale: [1, 2, 3, 4, 5], default: 3 }
      duration_days: { min: 1, max: 90, default: 7 }
      affected_entity_type: "supplier"
    propagation:
      downstream: ["inventory_shortage", "production_delay"]
    triggers_agents: ["supplier", "inventory"]

  - type: "transport_failure"
    description: "A transport route becomes unavailable or severely delayed"
    parameters:
      severity: { scale: [1, 2, 3, 4, 5], default: 3 }
      duration_days: { min: 1, max: 30, default: 5 }
      affected_entity_type: "route"
    propagation:
      downstream: ["delivery_delay", "inventory_shortage"]
    triggers_agents: ["transportation", "inventory", "demand"]

  - type: "demand_spike"
    description: "Unexpected surge in demand for one or more products"
    parameters:
      magnitude_multiplier: { min: 1.2, max: 5.0, default: 2.0 }
      duration_days: { min: 1, max: 60, default: 14 }
      affected_entity_type: "product"
    propagation:
      downstream: ["inventory_shortage", "supplier_strain"]
    triggers_agents: ["demand", "inventory", "supplier"]

  - type: "adverse_weather"
    description: "Weather event affecting transport routes or supplier regions"
    parameters:
      severity: { scale: [1, 2, 3, 4, 5], default: 3 }
      duration_days: { min: 1, max: 14, default: 3 }
      affected_entity_type: "route"
    propagation:
      downstream: ["transport_failure", "supplier_delay"]
    triggers_agents: ["transportation", "supplier"]

  # Domain-specific disruptions can be added here:
  # - type: "regulatory_hold"
  # - type: "quality_recall"
  # - type: "port_congestion"
  # - type: "currency_fluctuation"
```

**What this enables:** A pharmaceutical supply chain profile might include `cold_chain_breach` and `regulatory_hold` as disruption types. An automotive profile might include `just_in_time_failure` and `parts_shortage`. The disruption engine doesn't care — it reads from the catalog.

### 4. Consensus Tuning

```yaml
# profile/consensus.yaml

cd2f_config:
  arbitration:
    weighting_method: "confidence_x_historical_accuracy"
    accuracy_window_days: 30
    minimum_claims_for_consensus: 2     # at least N agents must contribute

  escalation:
    fast_path:
      conditions:
        min_confidence: 0.85
        max_impact: "low"
        single_agent_sufficient: true
      description: "Single high-confidence, low-impact agent resolves directly"

    slow_path:
      conditions:
        min_confidence: 0.50
        max_impact: "high"
        requires_full_discussion: true
      description: "Full CD²F multi-agent discussion and arbitration"

    human_escalation:
      conditions:
        consensus_stability_below: 0.40
        impact_above: "critical"
      description: "Surface to human operator with full reasoning trail"

  impact_scale:
    levels: ["negligible", "low", "medium", "high", "critical"]
    thresholds:
      negligible: { cost_impact_usd: 0, service_level_drop_pct: 0 }
      low: { cost_impact_usd: 5000, service_level_drop_pct: 2 }
      medium: { cost_impact_usd: 25000, service_level_drop_pct: 5 }
      high: { cost_impact_usd: 100000, service_level_drop_pct: 10 }
      critical: { cost_impact_usd: 500000, service_level_drop_pct: 25 }

  calibration:
    check_frequency: "every_100_decisions"
    kappa_threshold: 0.70               # below this, flag calibration drift
    hand_labeled_scenario_set: "scenarios/calibration_set.json"
```

**What this enables:** A high-stakes pharmaceutical deployment might set much lower confidence floors and escalate to humans more aggressively. A high-volume FMCG deployment might widen the fast-path to keep latency low. The consensus engine reads these thresholds at runtime — no code changes.

### 5. Evaluation Criteria

```yaml
# profile/evaluation.yaml

metrics:
  decision_quality:
    - decision_accuracy
    - consensus_quality
    - agent_agreement_rate
    - judge_calibration_kappa

  prediction_quality:
    - forecast_accuracy_per_agent
    - forecast_calibration           # for probabilistic outputs

  operational_impact:
    - response_time_seconds
    - fast_path_pct
    - slow_path_pct
    - human_escalation_pct
    - risk_reduction_pct
    - inventory_cost_delta
    - fill_rate

baselines:
  - name: "single_agent"
    description: "Best-performing single agent makes the decision alone"
  - name: "naive_majority_voting"
    description: "Simple majority vote across agent recommendations"

evaluation_scenarios: "scenarios/evaluation_set.json"
```

---

## How Each SCOF Layer Becomes Profile-Driven

| Layer | Currently (hardcoded) | With Domain Profiles |
|---|---|---|
| **D1 — Simulation** | Generator hardcodes 5 suppliers, 2 warehouses, etc. | Generator reads `topology.yaml` and produces entities matching the profile |
| **D2 — Knowledge Layer** | Neo4j/pgvector schemas assume fixed entity types | ETL scripts read `topology.yaml` to build the graph; schema is parameterized |
| **D3/D4 — Agents** | Agents are built with fixed model configs and data sources | Each agent reads its block from `agents.yaml` for model selection, thresholds, and MCP tool bindings |
| **D5 — Orchestration** | LangGraph wires exactly 4 agents + Coordinator | Coordinator reads `agents.yaml` at startup and discovers active agents via A2A — graph nodes are dynamic |
| **D6 — CD²F** | Escalation thresholds and impact scales are constants | Engine reads `consensus.yaml` for all thresholds, scales, and calibration settings |
| **D7 — Observability** | Trace schemas assume fixed agent set | Traces are keyed by agent ID from the profile — any number of agents, any names |
| **D8 — API** | Endpoints assume fixed entity and disruption types | API reads the profile to validate scenario triggers and parameterize responses |
| **D9 — Dashboard** | Map coordinates, entity names, view layouts are fixed | Dashboard reads a dashboard config block for entity display names, map bounds, heatmap dimensions |
| **D10 — Evaluation** | Metrics and baselines are hardcoded | Evaluation harness reads `evaluation.yaml` for metrics, baselines, and scenario sets |

---

## Deployment Patterns

Domain Profiles enable three deployment patterns, each progressively more flexible:

### Pattern 1: Single-Profile Deployment

The simplest model. One SCOF instance, one Domain Profile. This is what the MVP already is — just with the profile externalized rather than hardcoded.

```
┌─────────────────────────────┐
│       SCOF Platform         │
│                             │
│  ┌───────────────────────┐  │
│  │  Domain Profile:      │  │
│  │  "acme-electronics"   │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

**When to use:** Single organization, single supply chain scope, MVP.

### Pattern 2: Multi-Profile Switchable

One SCOF instance can load different profiles. Useful for organizations with multiple supply chain contexts (e.g., different product lines, different regions).

```
┌─────────────────────────────────────────────┐
│              SCOF Platform                   │
│                                             │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Profile A:   │  │ Profile B:           │ │
│  │ "electronics │  │ "pharma-cold-chain"  │ │
│  │  -southeast" │  │                      │ │
│  └──────────────┘  └──────────────────────┘ │
│                                             │
│  Active Profile: [A] ← switchable at        │
│                        startup or runtime    │
└─────────────────────────────────────────────┘
```

**When to use:** Same organization, multiple supply chain contexts, shared infrastructure.

### Pattern 3: Multi-Tenant

Multiple SCOF instances, each with its own profile, sharing core platform containers but isolated data stores. This is the path toward SCOF-as-a-service.

```
┌──────────────────────────────────────────────────────────┐
│                   Shared SCOF Platform                    │
│         (Agent images, CD²F engine, dashboard shell)      │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │  Tenant A      │  │  Tenant B      │  │  Tenant C  │ │
│  │  Profile:      │  │  Profile:      │  │  Profile:  │ │
│  │  "electronics" │  │  "pharma"      │  │  "auto"    │ │
│  │  Own data      │  │  Own data      │  │  Own data  │ │
│  │  stores        │  │  stores        │  │  stores    │ │
│  └────────────────┘  └────────────────┘  └────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**When to use:** Platform-as-a-service, multiple organizations, full data isolation.

---

## Building Profile-Aware from Day One

The MVP doesn't need to implement multi-profile or multi-tenant support. But it **should** treat its current hardcoded values as a profile from the start, so that the transition later is a refactor, not a rewrite.

### Minimal MVP Changes

| What to do | Effort | Payoff |
|---|---|---|
| Extract entity counts, supplier configs, and disruption parameters into YAML files instead of Python constants | Low | D1 generator becomes reusable for any topology |
| Have agents read their model config and thresholds from a config file instead of hardcoding | Low | Agent behavior becomes tunable without code changes |
| Store CD²F thresholds (fast-path/slow-path cutoffs, impact scale) in a config file | Low | Consensus engine becomes domain-adaptable |
| Have the Coordinator read active agents from config (even if it still discovers them via A2A) | Low | Adding/removing agents becomes a config change |
| Parameterize the dashboard's map bounds, entity labels, and heatmap scale from a config | Medium | Dashboard works for any geography and entity set |

### What Stays the Same

These parts of SCOF are **already domain-agnostic** and don't need changes:

- The **Structured Claim Contract** — works for any agent type, any domain
- The **A2A protocol** — agents self-describe via Agent Cards regardless of domain
- The **MCP protocol** — tool/data access is already abstracted
- The **LangGraph orchestration** — state graph structure doesn't depend on domain
- The **CD²F arbitration algorithm** — confidence-weighted voting works on any claim bundle
- The **observability layer** — traces are keyed by agent ID and decision ID, not by domain
- The **API structure** — endpoints are parameterized by IDs, not by entity types

---

## Worked Example: Two Profiles, One Platform

To make this concrete, here's how two very different supply chains would look as Domain Profiles on the same SCOF instance:

### Profile A: FMCG Manufacturer (Fast-Moving Consumer Goods)

| Dimension | Configuration |
|---|---|
| **Topology** | 1 manufacturer, 12 products (high SKU count), 8 suppliers (mostly reliable), 4 warehouses, 3 DCs, dense route network |
| **Key Disruptions** | Demand spikes (promotions-driven), supplier delays (raw material shortages), transport delays (port congestion) |
| **Active Agents** | Demand (critical — promotions-heavy), Inventory (high SKU churn), Supplier, Transportation |
| **Consensus Tuning** | Wide fast-path (most decisions are routine restocks), low human-escalation threshold (high volume, low individual impact) |
| **Impact Scale** | "Critical" = $50K+ (lower threshold — margins are thin) |
| **Dashboard Focus** | Inventory heatmap, demand forecast charts, fill rate tracking |

### Profile B: Pharmaceutical Cold-Chain Distributor

| Dimension | Configuration |
|---|---|
| **Topology** | 1 distributor, 3 products (vaccines, biologics, insulin), 4 suppliers (highly regulated), 2 cold-storage warehouses, 1 DC, limited route network (temperature-controlled) |
| **Key Disruptions** | Cold chain breach, regulatory hold, supplier quality failure, transport temperature excursion |
| **Active Agents** | Supplier (regulatory compliance focus), Transportation (temperature monitoring), Inventory (expiry tracking), Demand |
| **Consensus Tuning** | Narrow fast-path (patient safety — most decisions need full discussion), aggressive human-escalation (any quality or temperature issue) |
| **Impact Scale** | "Critical" = any patient safety risk (not purely financial) |
| **Dashboard Focus** | Temperature monitoring map, regulatory compliance status, expiry tracking |

### What's Different Between Them

| Aspect | FMCG Profile | Pharma Profile |
|---|---|---|
| Disruption types | Demand spikes, port congestion | Cold chain breach, regulatory hold |
| Fast-path width | Wide (routine restocks) | Narrow (safety-critical) |
| Human escalation trigger | Rare (high volume, low stakes per unit) | Frequent (patient safety) |
| Impact scale anchor | Financial (cost, margin) | Safety (patient risk, compliance) |
| Agent priority weighting | Demand Agent weighted highest | Supplier Agent (compliance) weighted highest |
| Dashboard emphasis | Fill rate, inventory turnover | Temperature logs, expiry dates |

### What's Identical Between Them

- The SCOF platform code
- The Structured Claim Contract
- The CD²F arbitration algorithm
- The A2A/MCP protocol layer
- The LangGraph orchestration engine
- The observability and trace infrastructure
- The API endpoint structure
- The dashboard component library (different components are *activated*, but the same components exist)

---

## Profile Directory Structure

A complete Domain Profile lives in a single directory:

```
profiles/
└── acme-electronics-southeast-asia/
    ├── profile.yaml              # Top-level metadata (name, version, description)
    ├── topology.yaml             # Entities and relationships
    ├── agents.yaml               # Active agents and their configurations
    ├── disruptions.yaml          # Disruption catalog
    ├── consensus.yaml            # CD²F thresholds and escalation rules
    ├── evaluation.yaml           # Metrics, baselines, scenario sets
    ├── dashboard.yaml            # View configuration, map bounds, labels
    ├── data_bindings.yaml        # MCP server configs, DB connection mappings
    └── scenarios/
        ├── calibration_set.json  # Hand-labeled scenarios for judge calibration
        └── evaluation_set.json   # Scenarios for benchmark evaluation
```

Deploying SCOF to a new supply chain context means **writing a new profile directory** — not modifying platform code.

---

## Summary

| Question | Answer |
|---|---|
| Can SCOF be a general-purpose platform? | Yes — the engine (orchestration, consensus, observability, API, dashboard) is domain-agnostic. |
| Does it need a specific context to run? | Yes — it needs entities, disruption types, thresholds, and evaluation criteria. |
| How is that context provided? | Through a **Domain Profile** — a declarative configuration artifact, not hardcoded values. |
| Does the MVP need multi-profile support? | No — but it should treat its current scope as a profile (externalized config, not constants), so multi-profile is a refactor later, not a rewrite. |
| What changes when deploying to a new supply chain? | Only the profile directory. Platform code stays the same. |
| What stays the same across all deployments? | The Structured Claim Contract, A2A/MCP protocols, CD²F algorithm, LangGraph orchestration, observability layer, API structure, dashboard component library. |
