# SCOF V2 Architecture Shift: D3-D10 Critical Review & Transformation Plan

## Document Purpose

This document provides an ultra-detailed critical analysis of the seven architectural concerns raised for the SCOF V2 Decision Engine transformation (D3 through D10). Each section contains: a diagnosis of the current V1 state, a gap analysis, a proposed V2 architecture, implementation specifics, and explicit rationale for every design decision.

> [!IMPORTANT]
> This is not a surface-level plan. Every recommendation below is traced back to specific files, schemas, and subsystem boundaries already established in the SCOF codebase. Nothing is proposed in isolation from the existing system.

---

## Table of Contents

1. [ONE: Agent Roster Redefinition](#one-agent-roster-redefinition)
2. [TWO: Agentic RAG Pipeline Integration](#two-agentic-rag-pipeline-integration)
3. [THREE: LangChain + LangGraph Dual-Framework Architecture](#three-langchain--langgraph-dual-framework-architecture)
4. [FOUR: True AI Agents -- Local LLM Strategy](#four-true-ai-agents----local-llm-strategy)
5. [FIVE: MCP & A2A Protocol Enhancement](#five-mcp--a2a-protocol-enhancement)
6. [SIX: Kafka Elevation to Core Decision Backbone](#six-kafka-elevation-to-core-decision-backbone)
7. [SEVEN: Inter-Agent Communication Protocol](#seven-inter-agent-communication-protocol)
8. [EIGHT: The Deliberation Table -- Centralized Cognitive Boardroom](#eight-the-deliberation-table----centralized-cognitive-boardroom-architecture)
9. [Cross-Cutting: Integration with D1/D2 Knowledge Layers & Twin Service](#cross-cutting)
10. [Unified V2 Architecture Diagram](#unified-v2-architecture-diagram)
11. [Implementation Sequencing](#implementation-sequencing)
12. [NINE: RAG Pipeline Architectural Correction](#nine-rag-pipeline-architectural-correction----agent-internal-retrieval-model)

---

## ONE: Agent Roster Redefinition

### 1.1 Current State Diagnosis

The V1 agent roster consists of exactly 4 specialist agents:

| Agent | Location | ML Stack | Cognitive Capability |
| :--- | :--- | :--- | :--- |
| `demand-agent` | [agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/src/agent.py) | XGBoost + Statistical ensemble | Rule-based threshold logic; no LLM reasoning |
| `inventory-agent` | [services/agents/inventory/](file:///d:/projects/SCOF_V1/SCOF/services/agents/inventory) | XGBoost ensemble | Safety stock formulas; no autonomous reasoning |
| `supplier-agent` | [agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/agent.py) | GradientBoosting + RuleScorer | Graph queries + deterministic ranking; no LLM |
| `transport-agent` | [services/agents/transportation/](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation) | Delay prediction model | Route queries; no LLM reasoning |

The architecture evolution doc ([scof_v2_architecture_evolution.md L96-104](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/scof_v2_architecture_evolution.md#L96-L104)) explicitly states: *"the core multi-agent federation remains focused on 4 primary operational specialists"* and *"This architectural principle is locked now to prevent scope creep."*

### 1.2 Gap Analysis: Why 4 Agents Cannot Serve V2

The SCOF Retail Enterprise Reference World spans **30 business domains** across 96 tables. The current 4-agent roster was designed for a toy MVP (1 manufacturer, 5 suppliers, 2 warehouses). At enterprise scale, critical operational domains are completely unrepresented:

| Unrepresented Domain Cluster | Impact if Missing |
| :--- | :--- |
| **Financial Operations** (Invoices, Payments, Ledger, Fiscal Periods) | Cannot evaluate cost trade-offs, cash flow impact of procurement decisions, or financial exposure thresholds that gate CD2F Tier-3 escalation |
| **Commercial & Procurement** (Contracts, Price Tiers, MOQ, Payment Terms) | Supplier Agent partially covers this, but contract compliance, penalty enforcement, and price break optimization deserve dedicated governance |
| **Quality & Compliance** (Inspection results, Shelf-life/Perishability, Asset Conditions) | Inventory Agent has a surface reference to asset telemetry, but quality quarantine, recall propagation, and regulatory compliance are absent |
| **Strategic Planning** (Promotions, Events, Seasonality, Regional Calendar) | Demand Agent partially handles this, but promotional lift analysis, cannibalization effects, and cross-category planning need deeper treatment |
| **Risk & Resilience** (Geopolitical, Weather, Commodity Volatility) | Completely absent; [D11](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D11_post_mvp_extensions_v2.md#L13-L16) mentions it as a "post-MVP extension" |

### 1.3 Proposed V2 Agent Roster: 6 Specialists + 1 Coordinator

The fundamental principle remains: **30 domains != 30 agents**. We consolidate the enterprise surface into 6 specialist agents plus a Coordinator, where each specialist governs a logical operational cluster consuming multiple data domains.

```
+=============================================================================+
|                        V2 AGENT ROSTER (6 + 1)                              |
+=============================================================================+
|                                                                             |
|  [COORDINATOR]  Meta-Orchestrator (LangGraph State Machine)                 |
|       |                                                                     |
|       +-- [1] DEMAND & COMMERCE AGENT                                       |
|       |      Domains: Commerce, POS Sales, Promotions, Calendar Events,     |
|       |               Weather, Demand Forecasting, Pricing/Elasticity       |
|       |      Consumes: daily_demand, pos_sales, promotions, events,         |
|       |                weather, pricing tables                              |
|       |                                                                     |
|       +-- [2] INVENTORY & ASSET MANAGEMENT AGENT                           |
|       |      Domains: Inventory Positions, Replenishment, Assortments,      |
|       |               Physical Assets (AST-xxxx), Shelf Life,               |
|       |               Goods Receipts, Storage Conditions                    |
|       |      Consumes: inventory_positions, assortments, assets,            |
|       |                goods_receipts, replenishment_policies               |
|       |                                                                     |
|       +-- [3] PROCUREMENT & SUPPLIER AGENT                                 |
|       |      Domains: Supplier Profiles, Commercial Contracts,              |
|       |               Purchase Orders, Three-Way Match, MOQ, Price Tiers,   |
|       |               Vendor Performance Index, Alternate Sourcing          |
|       |      Consumes: suppliers, contracts, purchase_orders, invoices,     |
|       |                three_way_match, supplier_performance               |
|       |                                                                     |
|       +-- [4] LOGISTICS & TRANSPORTATION AGENT                             |
|       |      Domains: Transport Lanes, Shipments, Carriers, Fleet Assets,   |
|       |               Route Optimization, Freight Modes, Corridor Status   |
|       |      Consumes: transport_lanes, shipments, carriers,               |
|       |                fleet_assets, corridor_disruptions                   |
|       |                                                                     |
|       +-- [5] FINANCIAL OPERATIONS AGENT                                   |
|       |      Domains: Invoices, Payments, Ledger Entries, Fiscal Periods,   |
|       |               Budget Allocations, Cash Flow, Penalty Enforcement   |
|       |      Consumes: invoices, payments, ledger_entries, fiscal_periods, |
|       |                budget_allocations                                   |
|       |                                                                     |
|       +-- [6] RISK & COMPLIANCE AGENT                                      |
|              Domains: Geopolitical Risk Signals, Weather Severity,          |
|                       Commodity Price Volatility, Quality Inspections,      |
|                       Regulatory Compliance, Supplier Financial Health     |
|              Consumes: weather, geopolitical_signals, quality_inspections, |
|                        commodity_prices, supplier_financial_health         |
|                                                                             |
+=============================================================================+
```

### 1.4 Detailed Agent Responsibility Matrix

#### Agent 1: Demand & Commerce Agent (`demand-commerce-agent`)

**Why merged:** Demand forecasting and commerce/pricing are tightly coupled. Promotional lift, price elasticity, cross-category cannibalization, and event-driven surges all feed directly into demand signals. Separating them would create a tight coupling antipattern where one agent constantly queries the other.

**Core Tasks:**
- Multi-horizon demand forecasting (7-day, 14-day, 28-day) across 49,616 SKUs
- Promotional lift and cannibalization analysis across 554 regional events
- Price elasticity sensitivity modeling
- External shock interpretation (weather anomalies, competitor actions)
- Seasonal pattern detection and event calendar alignment
- Cross-category substitution demand estimation during stockouts

**MCP Tools:**
- `get_pos_sales_trend(store_id, sku_id, lookback_days)`
- `get_promotional_calendar(zone_id, start_date, end_date)`
- `get_category_assortment_tree(category_id, max_depth=3)`
- `get_price_elasticity_coefficients(sku_id, store_id)`
- `get_event_calendar_impacts(region_id, date_range)`

---

#### Agent 2: Inventory & Asset Management Agent (`inventory-asset-agent`)

**Why merged:** Physical assets (cold-chain units, conveyors, sorting hubs) directly determine inventory viability. A compressor failure in a cold-storage DC immediately threatens perishable inventory. Separating asset health from inventory optimization creates a dangerous information silo.

**Core Tasks:**
- Multi-echelon safety stock optimization (DC-to-Store two-tier network)
- Perishable asset risk management and shelf-life enforcement
- Cold-chain monitoring and cross-dock transfer prioritization
- Storage condition compliance (temperature, humidity, hazmat segregation)
- Goods receipt validation and quality quarantine management
- Replenishment policy optimization (ROP, ROQ, EOQ)

**MCP Tools:**
- `get_facility_inventory(facility_id, sku_id)`
- `get_asset_operational_status(facility_id, asset_type)`
- `get_in_transit_shipments(destination_facility_id)`
- `get_shelf_life_risk_report(facility_id, category_id)`
- `get_storage_condition_alerts(facility_id)`

---

#### Agent 3: Procurement & Supplier Agent (`procurement-supplier-agent`)

**Why enhanced from V1:** The V1 Supplier Agent handles reliability scoring and alternate sourcing, but completely ignores the commercial dimension -- contracts, price tiers, MOQ constraints, three-way match validation, and penalty enforcement. In an enterprise with 200 suppliers and 225 contracts, procurement governance is mission-critical.

**Core Tasks:**
- Vendor Performance Index (VPI) calculation and tracking
- Dynamic split-allocation across qualified secondary vendors
- Contract SLA compliance monitoring and penalty calculation
- Three-way match validation (PO vs. Goods Receipt vs. Invoice)
- MOQ adherence enforcement during emergency split orders
- Supplier financial health early warning
- Automatic escalation when contractual SLA breaches exceed threshold

**MCP Tools:**
- `get_supplier_scorecard(supplier_id, lookback_months)`
- `get_contract_terms(supplier_id, product_id)`
- `get_supplier_lead_time_distribution(supplier_id, category_id)`
- `validate_three_way_match(po_id)`
- `get_supplier_financial_health_indicator(supplier_id)`

---

#### Agent 4: Logistics & Transportation Agent (`logistics-transport-agent`)

**Why retained as-is (scope only):** Transport operations form a well-bounded domain. The V1 Transport Agent's scope was reasonable but its implementation was non-cognitive. The scope remains; the engine transforms.

**Core Tasks:**
- Dynamic carrier selection based on lane volume, equipment type, and emissions
- Graph-based multi-hop rerouting under corridor disruptions
- Demurrage and dock congestion mitigation
- Multi-modal freight optimization (sea, road, air, rail)
- Freight cost vs. transit time Pareto optimization
- Carbon footprint assessment per route choice

**MCP Tools:**
- `find_alternate_carrier_routes(origin_id, destination_id, max_transit_days)`
- `get_lane_congestion_status(lane_id)`
- `get_carrier_capacity_allowance(carrier_id, date)`
- `get_freight_cost_comparison(origin_id, dest_id, modes=["road", "air"])`

---

#### Agent 5: Financial Operations Agent (`finance-ops-agent`) -- NEW

**Why new:** The CD2F Consensus Engine gates Tier-3 escalation on `financial_exposure > $100,000` ([D06 L57](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D06_cd2f_consensus_v2.md#L57)). The `NetBenefit` calculation in CD2F requires cross-domain cost impact data. Currently, no agent provides this. Financial reasoning is structurally absent from the deliberation pipeline, which means every financial threshold in CD2F is evaluated without domain expertise.

**Core Tasks:**
- Real-time financial exposure calculation for proposed interventions
- Cash flow impact modeling for expedited procurement and air freight
- Invoice-payment reconciliation anomaly detection
- Budget allocation compliance checking (per-department, per-quarter)
- Penalty enforcement cost modeling (SLA breach penalties, demurrage charges)
- Landed cost optimization (procurement cost + freight + duties + handling)

**MCP Tools:**
- `get_financial_exposure(action_type, parameters)`
- `get_budget_allocation_status(department_id, fiscal_period_id)`
- `get_payment_aging_report(supplier_id)`
- `get_landed_cost_estimate(po_id, route_option)`
- `get_ledger_summary(fiscal_period_id)`

---

#### Agent 6: Risk & Compliance Agent (`risk-compliance-agent`) -- NEW

**Why new:** D11 ([D11 L13-16](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D11_post_mvp_extensions_v2.md#L13-L16)) already identifies this as a post-MVP extension. Promoting it to V2 core is justified because:
1. The enterprise has 200 suppliers with varying geopolitical exposure
2. Weather data (554 regional events) is already in the dataset but no agent proactively reasons about it
3. Quality/compliance failures can cascade rapidly through the supply chain

**Core Tasks:**
- Proactive macro-risk sensing (geopolitical, weather, commodity volatility)
- Supplier financial default risk monitoring
- Quality inspection result analysis and recall propagation modeling
- Regulatory compliance verification (food safety, hazmat, cold-chain)
- ESG/sustainability constraint injection into decision scoring
- Early-warning vulnerability penalties for CD2F arbitration

**MCP Tools:**
- `get_geopolitical_risk_index(region_id)`
- `get_weather_severity_forecast(region_id, horizon_days)`
- `get_commodity_price_trend(commodity_id, lookback_days)`
- `get_quality_inspection_results(supplier_id, product_id)`
- `get_compliance_status(facility_id, regulation_type)`

---

### 1.5 Coordinator Responsibilities -- Clear Definition

The Coordinator is NOT an agent that produces claims. It is the **meta-orchestrator** that manages the deliberation lifecycle.

| Coordinator Responsibility | Description |
| :--- | :--- |
| **Agent Discovery & Health** | Queries A2A registry, monitors health status, excludes UNHEALTHY agents from deliberation |
| **Disruption Classification & Routing** | Classifies incoming disruptions and determines which agents to activate (not all 6 for every event) |
| **Context Framing** | Scopes affected entities (SKUs, facilities, corridors) via Knowledge Fabric queries |
| **Capability Resolution** | Invokes Dynamic Capability Registry to bind relevant MCP tools to each activated agent |
| **Parallel Fan-Out/Fan-In** | Dispatches analysis tasks concurrently with bounded SLA (850ms per agent) |
| **Cross-Examination Moderation** | Routes critiques between agents during Phase 3 |
| **Consensus Hand-Off** | Collates claims + critiques and submits to CD2F |
| **Execution Commitment** | Applies approved decision to Twin Layer 3 |
| **Audit Emission** | Emits immutable deliberation transcript to D07 observability |

**What the Coordinator does NOT do:**
- It does not produce its own claims or recommendations
- It does not score or weight agent proposals (CD2F does that)
- It does not modify baseline state (Layer 1 or Layer 2)
- It does not directly query databases (agents do that via MCP)

---

## TWO: Agentic RAG Pipeline Integration

### 2.1 Current State Diagnosis

The V1/V2 architecture already contains the raw materials for RAG:
- **pgvector** stores 384-dimensional embeddings in PostgreSQL ([D07 L40-41](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D07_observability_explainability_v2.md#L40-L41))
- **Semantic Precedent Memory** allows `find_historical_precedents(disruption_embedding, top_k=3, min_similarity=0.80)` via MCP
- **Neo4j** provides topological context via bounded graph traversals

However, these are currently passive retrieval endpoints. No component actively orchestrates a retrieval-augmented reasoning loop. Agents query data, run ML models, and emit claims -- there is no "retrieve relevant context, reason over it, then decide" loop.

### 2.2 The Agentic RAG Architecture

The Agentic RAG pipeline wraps around the entire Decision Engine as an **active reasoning substrate**. It is not a standalone service; it is a pattern embedded into every agent's cognitive loop and the coordinator's context-framing phase.

```
+=============================================================================+
|                       AGENTIC RAG PIPELINE                                  |
|                    (Surrounds the Decision Engine)                          |
+=============================================================================+
|                                                                             |
|  +-----------+     +---------------+     +------------+     +----------+   |
|  | RETRIEVER |---->| RE-RANKER &   |---->| CONTEXT    |---->| REASONER |   |
|  | LAYER     |     | RELEVANCE     |     | ASSEMBLER  |     | (LLM)    |   |
|  +-----------+     | FILTER        |     +------------+     +----------+   |
|       |            +---------------+           |                  |        |
|       |                                        |                  |        |
|  +----+-----+                           +------+------+     +----+----+   |
|  | Sources: |                           | Structured  |     | Claim   |   |
|  | 1. pgvector (Semantic Memory)   |    | Prompt with |     | Output  |   |
|  | 2. Neo4j (Topological Context)  |    | Retrieved   |     |         |   |
|  | 3. PostgreSQL (Factual State)   |    | Evidence    |     |         |   |
|  | 4. Redis (Real-time Cache)      |    +-------------+     +---------+   |
|  +----------+                                                              |
+=============================================================================+
```

### 2.3 RAG Integration Points Across the Decision Engine

#### Phase 1: Coordinator Context Framing (Ingestion & Routing)
**RAG Action:** When a disruption is ingested, the Coordinator:
1. **Retrieves** historical precedents from pgvector: *"Have we seen a similar disruption before? What did we decide? What was the outcome?"*
2. **Retrieves** topological blast radius from Neo4j: *"Which facilities, SKUs, and contracts are affected by this specific disruption?"*
3. **Assembles** a structured context package containing: disruption details + historical precedent summaries + affected entity graph + current state snapshot
4. This assembled context is distributed to all activated agents as their initial knowledge base

#### Phase 2: Agent Proposal Generation
**RAG Action:** Each specialist agent, before generating its claim:
1. **Retrieves** domain-specific historical decisions from pgvector: *"What did I (this agent) recommend in similar situations? How accurate was I?"*
2. **Retrieves** relevant factual state from PostgreSQL via MCP tools
3. **Retrieves** structural dependencies from Neo4j via bounded traversals
4. **Assembles** a domain-specific context window combining: retrieved precedents + real-time data + ML model outputs
5. **Reasons** over this assembled context using the local LLM to generate its StructuredClaimV2

#### Phase 3: Cross-Examination
**RAG Action:** When agents critique peer claims:
1. **Retrieves** counter-evidence: *"Has the proposed action ever failed in similar conditions?"*
2. **Retrieves** cross-domain constraint data: *"Does the proposed route have capacity? Is the proposed supplier financially stable?"*

#### Phase 4: CD2F Consensus
**RAG Action:** The consensus engine:
1. **Retrieves** historical accuracy data for each agent ($R_i$ factor) from pgvector
2. **Retrieves** precedent resolution patterns: *"In similar conflict scenarios, which resolution strategy yielded better outcomes?"*

#### Phase 5: Post-Decision Archival (Closing the Loop)
**RAG Action:** After execution:
1. The resolved incident, its claims, the consensus decision, and the outcome metrics are **embedded** (via `all-MiniLM-L6-v2`) and **stored** in pgvector
2. This closes the RAG feedback loop, ensuring future retrievals benefit from this decision

### 2.4 Implementation Architecture: RAG Service Layer

Rather than embedding RAG logic in every service, we create a shared **RAG Service Layer** within `scof_shared`:

```python
# scof_shared/rag/retriever.py
class SCOFRetriever:
    """Unified retrieval interface across all SCOF knowledge sources."""
    
    def __init__(self, pg_pool, neo4j_client, pgvector_client, redis_client):
        self.pg = pg_pool
        self.neo4j = neo4j_client
        self.pgvector = pgvector_client
        self.redis = redis_client
    
    async def retrieve_precedents(self, query_embedding, top_k=5, min_similarity=0.75):
        """Semantic search over historical decisions in pgvector."""
        ...
    
    async def retrieve_topological_context(self, entity_id, entity_type, max_hops=2):
        """Bounded graph traversal for structural dependencies."""
        ...
    
    async def retrieve_factual_state(self, entity_ids, state_type):
        """Current operational state from PostgreSQL."""
        ...
    
    async def retrieve_real_time_signals(self, signal_keys):
        """Ephemeral real-time data from Redis."""
        ...
    
    async def assemble_context(self, disruption_event, agent_domain=None):
        """Full context assembly combining all retrieval sources."""
        precedents = await self.retrieve_precedents(...)
        topology = await self.retrieve_topological_context(...)
        state = await self.retrieve_factual_state(...)
        signals = await self.retrieve_real_time_signals(...)
        return AssembledContext(precedents, topology, state, signals)
```

---

## THREE: LangChain + LangGraph Dual-Framework Architecture

### 3.1 Current State Diagnosis

The V1 system uses **LangGraph only**, with a thin wrapper:
- [orchestrator.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/orchestrator.py) imports `from langgraph.graph import END, START, StateGraph`
- The graph has 6 nodes: `initialize_context -> discover_agents -> dispatch_parallel -> finalize_bundle -> run_consensus -> persist_decision`
- There is **zero LangChain** anywhere in the codebase
- Agents are called via raw HTTP POST to `/analyze` endpoints; there is no LLM chain, no prompt template, no memory, no tool-calling via LangChain

### 3.2 The Dual-Framework Design Principle

Your intuition is correct. The two frameworks serve fundamentally different purposes:

| Framework | Architectural Role | Scope |
| :--- | :--- | :--- |
| **LangGraph** | **Workflow Orchestration** -- manages the macro-level deliberation state machine, parallel fan-out/fan-in, conditional routing, cycle management, and the end-to-end orchestration graph | The Coordinator and the overall D3-D10 pipeline |
| **LangChain** | **Agent-Level Cognitive Engine** -- manages individual agent reasoning: prompt templates, tool calling, memory/context management, LLM chain composition, output parsing, and structured output generation | Inside each specialist agent |

```
+=============================================================================+
|                     LANGGRAPH ORCHESTRATION LAYER                           |
|                  (Workflow State Machine -- D05 Kernel)                     |
|                                                                             |
|  Manages: State transitions, parallel dispatch, cycle limits,              |
|           conditional routing, checkpoint/replay, audit emission           |
|                                                                             |
|  +---------+   +----------+   +-----------+   +---------+   +----------+  |
|  |Ingestion|-->|Fan-Out   |-->|Cross-Exam |-->|Consensus|-->|Execution |  |
|  |& Route  |   |Dispatch  |   |& Critique |   |Hand-Off |   |& Commit  |  |
|  +---------+   +----------+   +-----------+   +---------+   +----------+  |
|                     |                                                       |
|                     | Invokes N agents concurrently                         |
|                     v                                                       |
|  +==========================================================================|
|  |                  LANGCHAIN AGENT REASONING LAYER                        ||
|  |              (Per-Agent Cognitive Chain -- D03/D04)                      ||
|  |                                                                         ||
|  |  Manages: Prompt templates, tool invocation chains, memory/context,    ||
|  |           structured output parsing, RAG retrieval integration         ||
|  |                                                                         ||
|  |  Each Agent Runs:                                                       ||
|  |  [RetrievalChain] --> [ReasoningChain] --> [ToolCallingChain]          ||
|  |       --> [StructuredOutputParser] --> StructuredClaimV2                ||
|  |                                                                         ||
|  +==========================================================================|
+=============================================================================+
```

### 3.3 LangChain Components Per Agent

Each specialist agent internally uses a LangChain-based reasoning chain:

```python
# Inside each agent (e.g., demand-commerce-agent)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSequence
from langchain.tools import Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.llms import Ollama  # or equivalent

class DemandCommerceAgent(BaseAgent):
    def __init__(self, ...):
        # LLM backbone (local -- see Section FOUR)
        self.llm = self._init_llm()
        
        # RAG retriever for context assembly
        self.retriever = SCOFRetriever(...)
        
        # MCP tools wrapped as LangChain Tools
        self.tools = self._bind_mcp_tools_as_langchain_tools()
        
        # Prompt template with domain specialization
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", DEMAND_SYSTEM_PROMPT),
            ("human", "{disruption_context}\n\n{retrieved_precedents}\n\n{current_state}"),
        ])
        
        # Structured output parser
        self.output_parser = PydanticOutputParser(pydantic_object=StructuredClaimV2)
        
        # Agent executor with tool calling
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools)
    
    async def analyze(self, context: ScenarioContext) -> StructuredClaimV2:
        # 1. RAG: Retrieve relevant context
        assembled_ctx = await self.retriever.assemble_context(
            disruption_event=context.disruption_event,
            agent_domain="demand_commerce"
        )
        
        # 2. ML: Run traditional forecasting models
        ml_forecast = self.ensemble.predict(...)
        
        # 3. LLM: Reason over assembled context + ML output
        result = await self.executor.ainvoke({
            "disruption_context": context.to_prompt(),
            "retrieved_precedents": assembled_ctx.format_precedents(),
            "current_state": assembled_ctx.format_state(),
            "ml_forecast": ml_forecast.to_summary(),
        })
        
        # 4. Parse structured output
        claim = self.output_parser.parse(result["output"])
        return claim
```

### 3.4 LangGraph Orchestration Enhancements

The current LangGraph graph in [orchestrator.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/orchestrator.py) needs significant enhancement:

**Current graph (V1):** Linear pipeline, no cycles, no cross-examination, no conditional routing
```
START -> initialize -> discover -> dispatch -> finalize -> consensus -> persist -> END
```

**Target graph (V2):** Cyclical deliberation with conditional routing, cross-examination rounds, and escalation branching
```
START -> ingest_and_route -> capability_bind -> parallel_fan_out
    -> fan_in_collate -> cross_examination
    -> [CONDITIONAL: consensus_ready?]
        -> YES: consensus_arbitration
            -> [CONDITIONAL: tier?]
                -> TIER_1: twin_sandbox_commit -> persist_and_archive -> END
                -> TIER_2: extended_deliberation -> consensus_arbitration (cycle)
                -> TIER_3: hitl_escalation -> await_human -> twin_sandbox_commit -> END
        -> NO (cycle < 3): parallel_fan_out (re-deliberate)
        -> NO (cycle >= 3): forced_heuristic_arbitration -> END
```

### 3.5 Memory Management via LangChain

LangChain provides the memory substrate that individual agents need:

| Memory Type | Purpose | Implementation |
| :--- | :--- | :--- |
| **Conversational Buffer Memory** | Maintains the current deliberation context within a single scenario run | `ConversationBufferMemory` scoped to `scenario_id + sim_run_id` |
| **Summary Memory** | Compresses historical deliberation transcripts for efficient context window usage | `ConversationSummaryMemory` fed from D07 observability traces |
| **Vector Store Memory** | Long-term semantic memory across runs (pgvector-backed) | `VectorStoreRetrieverMemory` backed by the pgvector Semantic Projection |

---

## FOUR: True AI Agents -- Local LLM Strategy

### 4.1 Current State Diagnosis

The current agents are **not AI agents at all**. Examining [demand/agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/src/agent.py):
- The `analyze()` method runs XGBoost ensemble prediction
- Confidence scores come from numerical agreement between models
- Recommendations are generated via `if/else` threshold logic (lines 121-130)
- There is zero LLM invocation anywhere
- There is zero autonomous reasoning, zero natural language understanding, zero tool-calling autonomy

### 4.2 LLM Selection: Critical Analysis

| Option | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| **Ollama (llama.cpp backend)** | Easy to deploy, wide model support, REST API | Stateless by default (no built-in memory), no native tool-calling for many models | Viable with LangChain memory layer |
| **vLLM** | High-throughput inference, PagedAttention, OpenAI-compatible API | Heavier resource requirements, more complex deployment | Better for production scale |
| **llama-cpp-python** | Direct Python bindings, low overhead | Limited tooling ecosystem, manual everything | Too raw for our needs |
| **LocalAI** | OpenAI-compatible API, drop-in replacement | Fewer optimization features than vLLM | Good fallback |
| **Hugging Face TGI** | Production-grade, enterprise support | Heavier infra requirements | Good for cloud deployment |

### 4.3 Recommended Strategy: Ollama + LangChain Memory + Tool Calling

**Why Ollama is viable despite being "memoryless":**

Ollama itself being stateless is not a problem because memory is handled at the **application layer**, not the inference layer. LangChain provides:
1. `ConversationBufferMemory` -- maintains the current deliberation context
2. `VectorStoreRetrieverMemory` -- long-term semantic recall via pgvector
3. `ConversationSummaryMemory` -- compressed historical context

The LLM inference engine (Ollama) only needs to process a single prompt containing the assembled context. It does not need to "remember" previous conversations because the memory layer reconstructs relevant context for every invocation.

### 4.4 Model Selection Per Agent Role

Not every agent needs the same model. The principle: **use the smallest model that can do the job.**

| Agent | Recommended Model | Rationale |
| :--- | :--- | :--- |
| **Demand & Commerce** | `llama3.1:8b` or `mistral:7b` | Needs numerical reasoning + natural language interpretation of events/promotions |
| **Inventory & Asset** | `llama3.1:8b` | Primarily constraint satisfaction + risk assessment; moderate reasoning |
| **Procurement & Supplier** | `llama3.1:8b` | Contract compliance requires structured reasoning over multi-clause terms |
| **Logistics & Transport** | `mistral:7b` | Route optimization is primarily algorithmic; LLM handles edge cases and natural language |
| **Financial Operations** | `llama3.1:8b` | Financial reasoning requires arithmetic accuracy; 8B models handle this well |
| **Risk & Compliance** | `llama3.1:8b` or `phi3:medium` | Needs world knowledge for geopolitical reasoning; larger context window preferred |
| **Coordinator** | `llama3.1:8b` | Needs meta-reasoning about which agents to activate and how to frame context |

### 4.5 Hybrid Architecture: ML Models + LLM Reasoning

The transformation is NOT "replace XGBoost with LLM." It is "keep XGBoost for what it does well, add LLM for what XGBoost cannot do."

```
+=====================================================================+
|                    HYBRID AGENT ARCHITECTURE                        |
+=====================================================================+
|                                                                     |
|  [TRADITIONAL ML PIPELINE]         [LLM REASONING PIPELINE]        |
|  - XGBoost / LightGBM              - Qualitative shock reasoning   |
|  - Prophet / Chronos-2              - Cross-domain constraint eval  |
|  - GradientBoosting Classifiers     - Natural language evidence     |
|  - Deterministic Rule Engines       - Contrastive explanation gen   |
|  - Safety stock formulas            - Historical precedent reasoning|
|                                     - Tool-calling autonomy         |
|  OUTPUT: Quantitative forecasts     OUTPUT: Qualitative reasoning   |
|          Reliability scores                  Structured arguments   |
|          Confidence intervals                Evidence narratives    |
|                                                                     |
|  +-------+     +--------+     +---------+     +------------------+ |
|  |  ML   |---->| FUSION |---->| LLM     |---->| StructuredClaim  | |
|  | Output|     | LAYER  |     | Reasoner|     | V2 Output        | |
|  +-------+     +--------+     +---------+     +------------------+ |
|                                                                     |
+=====================================================================+
```

### 4.6 Deployment Architecture

```yaml
# docker-compose.yml addition
services:
  ollama:
    image: ollama/ollama:latest
    container_name: scof-ollama
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1  # GPU if available; CPU fallback
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 5
```

Each agent connects via LangChain's Ollama integration:
```python
from langchain_community.llms import Ollama

llm = Ollama(
    model="llama3.1:8b",
    base_url="http://ollama:11434",
    temperature=0.1,  # Low temperature for deterministic reasoning
    num_ctx=4096,      # Context window
)
```

---

## FIVE: MCP & A2A Protocol Enhancement

### 5.1 Current State Diagnosis

#### A2A Current Issues:

1. **Agent Cards are static and cosmetic:** The [AgentCard schema](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/schemas/agent_card.py) stores `capabilities`, `supported_contexts`, `input_schema`, `output_schema`, and `endpoint` -- but these are just metadata strings. The card does not describe tool capabilities, resource requirements, or SLA guarantees.

2. **Discovery is simple HTTP GET:** [a2a_client.py L45](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/a2a_client.py#L45) queries `/.well-known/agent.json`. There is no heartbeat, no capability negotiation, no task delegation protocol.

3. **No task lifecycle management:** The A2A protocol sends a context via POST and receives a claim. There is no `task_id`, no status polling, no streaming, no cancellation.

#### MCP Current Issues:

1. **MCP is just a REST wrapper:** [mcp_server.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/mcp_server.py) exposes `/mcp/tools/list` and `/mcp/tools/call` as simple FastAPI routes. This is a custom REST API wearing an MCP hat, not an actual MCP implementation.

2. **No JSON-RPC 2.0:** The real MCP specification uses JSON-RPC 2.0 over stdio or SSE. Our implementation uses plain REST with custom request/response models.

3. **No dynamic tool mounting:** Tools are statically registered at startup. The Dynamic Capability Registry concept ([ADR 012b](file:///d:/projects/SCOF_V1/SCOF/docs/adr/012b_amendment_dynamic_capability_registry_over_static_mcp.md)) exists in documentation only.

### 5.2 A2A Enhancement Plan

#### 5.2.1 Agent Card V2 Specification

```python
class AgentCardV2(BaseModel):
    """Enhanced A2A Agent Card conforming to Google A2A spec."""
    
    # Identity
    agent_id: str
    name: str
    description: str
    version: str
    
    # Capabilities (structured, not just string tags)
    capabilities: list[CapabilityDeclaration]
    
    # Input/Output schemas (actual JSON Schema, not string references)
    input_schema: dict  # JSON Schema for accepted input
    output_schema: dict  # JSON Schema for produced output
    
    # Task management
    supported_task_types: list[str]  # ["analyze", "critique", "explain"]
    max_concurrent_tasks: int = 1
    
    # SLA declarations
    sla: AgentSLA
    
    # Communication
    protocol: str = "A2A/2.0"
    endpoint: str
    streaming_endpoint: Optional[str] = None  # For SSE streaming
    
    # Health
    health_endpoint: str  # /health for liveness probing

class CapabilityDeclaration(BaseModel):
    capability_id: str
    description: str
    domain_tags: list[str]
    supported_disruption_types: list[str]
    required_mcp_tools: list[str]  # Tools this capability needs

class AgentSLA(BaseModel):
    max_response_time_ms: int = 850
    reliability_target: float = 0.95
    resource_requirements: ResourceSpec
```

#### 5.2.2 Task Lifecycle Protocol

```
POST /a2a/tasks/create     -- Create a new task (returns task_id)
GET  /a2a/tasks/{id}       -- Poll task status
POST /a2a/tasks/{id}/cancel -- Cancel a running task
GET  /a2a/tasks/{id}/stream -- SSE stream for real-time updates
POST /a2a/tasks/{id}/input  -- Send additional input mid-task
```

#### 5.2.3 Agent Discovery Enhancement

```python
class A2ARegistryV2:
    """Enhanced registry with heartbeat monitoring and capability indexing."""
    
    async def register(self, card: AgentCardV2, endpoint: str):
        """Register with capability indexing."""
        ...
    
    async def heartbeat(self, agent_id: str, health: HealthReport):
        """Periodic health reporting (every 10s)."""
        ...
    
    def find_by_disruption_type(self, disruption_type: str) -> list[AgentCardV2]:
        """Find agents whose capabilities match the disruption type."""
        ...
    
    def find_by_required_tools(self, required_tools: list[str]) -> list[AgentCardV2]:
        """Find agents that possess specific MCP tool bindings."""
        ...
```

### 5.3 MCP Enhancement Plan

#### 5.3.1 Proper JSON-RPC 2.0 Implementation

Replace the current REST-based MCP with a proper JSON-RPC 2.0 implementation:

```python
# scof_shared/protocols/mcp_server_v2.py
class MCPServerV2:
    """JSON-RPC 2.0 MCP server with SSE transport."""
    
    def __init__(self):
        self.tools: dict[str, MCPTool] = {}
        self.resources: dict[str, MCPResource] = {}
    
    async def handle_jsonrpc(self, request: JSONRPCRequest) -> JSONRPCResponse:
        match request.method:
            case "tools/list":
                return self._list_tools()
            case "tools/call":
                return await self._call_tool(request.params)
            case "resources/list":
                return self._list_resources()
            case "resources/read":
                return await self._read_resource(request.params)
            case "prompts/list":
                return self._list_prompts()
            case _:
                raise MethodNotFoundError(request.method)
```

#### 5.3.2 Dynamic Capability Registry Implementation

The [Dynamic Capability Registry spec](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md) must be implemented:

```python
class DynamicCapabilityRegistry:
    """Mounts only the 3-5 most relevant tools per agent per deliberation."""
    
    async def register_capability(self, card: CapabilityCard):
        """Service providers register declarative Capability Cards."""
        ...
    
    async def resolve_and_bind(
        self, disruption_event: dict, agent_domain: str
    ) -> list[BoundMCPTool]:
        """
        Semantic matching: resolve which tools are relevant
        for this specific disruption in this agent's domain.
        Returns 3-5 bounded tools to inject into the agent's prompt.
        """
        ...
```

---

## SIX: Kafka Elevation to Core Decision Backbone

### 6.1 Current State Diagnosis

Kafka in V1 is severely underutilized. The [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml) creates 6 topics:

| Topic | Purpose | Usage Level |
| :--- | :--- | :--- |
| `scof.disruptions.triggered` | Disruption event ingestion | Light -- only API gateway publishes |
| `scof.whatif.requested` | What-if simulation requests | Minimal |
| `scof.decisions.completed` | Completed decisions | Light -- coordinator publishes |
| `scof.orchestration.failed` | Failed orchestration events | Error logging only |
| `scof.agents.activity` | Agent status updates | Best-effort telemetry |
| `scof.dlq` | Dead letter queue | Error handling |

Kafka is positioned at the **lowest API layer** (D8), used primarily for decoupling the API gateway from the coordinator. It is not part of the agent communication, deliberation flow, or consensus pipeline.

### 6.2 Kafka's Role in V2: Event Backbone for the Decision Engine

Kafka must become the **central nervous system** connecting agents, the coordinator, CD2F, the Twin, and the observability layer.

### 6.3 V2 Topic Architecture

```
+=============================================================================+
|                     KAFKA V2 TOPIC ARCHITECTURE                            |
+=============================================================================+
|                                                                             |
|  TIER 1: INGRESS & DISRUPTION LIFECYCLE                                    |
|  +-----------------------------------------------------------------+       |
|  | scof.disruptions.inbound        | Raw disruption events         |       |
|  | scof.disruptions.classified     | Router-classified events      |       |
|  | scof.disruptions.scoped         | Context-scoped events         |       |
|  +-----------------------------------------------------------------+       |
|                                                                             |
|  TIER 2: AGENT DELIBERATION & COMMUNICATION                               |
|  +-----------------------------------------------------------------+       |
|  | scof.agents.claims.proposed     | Agent initial claim proposals |       |
|  | scof.agents.critiques.emitted   | Cross-examination critiques   |       |
|  | scof.agents.claims.revised      | Revised claims post-critique  |       |
|  | scof.agents.tools.invoked       | MCP tool call audit trail     |       |
|  | scof.agents.rag.retrieved       | RAG retrieval audit trail     |       |
|  +-----------------------------------------------------------------+       |
|                                                                             |
|  TIER 3: CONSENSUS & DECISION                                              |
|  +-----------------------------------------------------------------+       |
|  | scof.consensus.submitted        | Claim bundles to CD2F         |       |
|  | scof.consensus.resolved         | CD2F decision outcomes        |       |
|  | scof.consensus.escalated        | HITL escalation events        |       |
|  +-----------------------------------------------------------------+       |
|                                                                             |
|  TIER 4: EXECUTION & STATE                                                 |
|  +-----------------------------------------------------------------+       |
|  | scof.twin.actions.committed     | Twin sandbox mutations        |       |
|  | scof.twin.state.deltas          | State change notifications    |       |
|  | scof.execution.erp.dispatched   | ERP actuation events          |       |
|  +-----------------------------------------------------------------+       |
|                                                                             |
|  TIER 5: OBSERVABILITY & AUDIT                                             |
|  +-----------------------------------------------------------------+       |
|  | scof.observability.traces       | Full 8-stage reasoning traces |       |
|  | scof.observability.metrics      | Performance telemetry         |       |
|  | scof.agents.activity            | Agent health & status         |       |
|  | scof.dlq                        | Dead letter queue             |       |
|  +-----------------------------------------------------------------+       |
+=============================================================================+
```

### 6.4 Kafka as Agent Communication Backbone

Currently, agent communication is synchronous HTTP POST via the A2A client. This creates tight coupling and fails under load. In V2, Kafka serves as the asynchronous communication layer:

```
Coordinator                                              Agents
    |                                                       |
    |-- [Publish to scof.agents.claims.proposed] ---------> |
    |   (Fan-out: all 6 agents receive disruption context)  |
    |                                                       |
    |<-- [Consume from scof.agents.claims.proposed] ------- |
    |   (Each agent publishes its StructuredClaimV2)        |
    |                                                       |
    |-- [Publish to scof.agents.critiques.emitted] -------> |
    |   (Cross-examination: agents receive peer claims)     |
    |                                                       |
    |<-- [Consume from scof.agents.critiques.emitted] ----- |
    |   (Agents publish critique responses)                 |
    |                                                       |
    |-- [Publish to scof.consensus.submitted] ------------> CD2F
    |                                                       |
    |<-- [Consume from scof.consensus.resolved] ----------- CD2F
```

### 6.5 Benefits of Kafka Elevation

1. **Decoupled Agent Execution:** Agents do not need to be available at the exact moment of dispatch; messages are durably queued
2. **Replay & Debug:** Every deliberation message is persisted in Kafka with configurable retention, enabling full replay
3. **Audit Trail:** Topic `scof.agents.tools.invoked` provides a complete record of every MCP tool call made during a deliberation
4. **Horizontal Scaling:** Multiple agent instances can consume from the same topic via consumer groups
5. **Cross-Examination Broadcasting:** Phase 3 cross-examination becomes a natural pub/sub pattern

---

## SEVEN: Inter-Agent Communication Protocol

### 7.1 Current State: No True Inter-Agent Communication

In V1, agents do not communicate with each other at all. The coordinator dispatches HTTP requests to each agent independently, collects responses, and bundles them. Agents are completely unaware of each other's existence, claims, or reasoning.

### 7.2 V2 Communication Model: Structured Deliberation Protocol

Inter-agent communication in SCOF V2 follows a **structured deliberation protocol** with three message types:

#### Message Type 1: Claim Proposal

```python
class ClaimProposal(BaseModel):
    """Agent's initial recommendation for a disruption scenario."""
    claim_id: str
    agent_id: str
    scenario_id: str
    sim_run_id: str
    cycle_index: int  # Which deliberation round
    
    # The proposal
    proposed_action: ActionSpec
    confidence: float  # [0.0, 1.0]
    
    # Supporting evidence
    evidence_pack: list[EvidenceItem]
    ml_model_outputs: dict[str, Any]  # Quantitative backing
    retrieved_precedents: list[PrecedentReference]  # RAG context
    
    # Impact assessment
    cost_impact_usd: float
    service_level_delta: float
    lead_time_delta_days: float
    
    # Cross-domain dependencies
    requires_from: list[CrossDomainDependency]  # "I need transport to confirm lane is open"
    affects_domains: list[str]  # Domains my action impacts
```

#### Message Type 2: Critique

```python
class AgentCritique(BaseModel):
    """Agent's challenge to a peer's claim."""
    critique_id: str
    critiquing_agent_id: str
    target_claim_id: str
    target_agent_id: str
    
    critique_type: Literal[
        "CONSTRAINT_VIOLATION",    # "Your plan violates warehouse capacity"
        "INFORMATION_CONFLICT",    # "My data contradicts your assumption"
        "COST_UNDERESTIMATE",      # "You did not account for demurrage charges"
        "DEPENDENCY_UNRESOLVED",   # "The route you assume is available is closed"
        "RISK_UNDERASSESSED",      # "Supplier financial health is deteriorating"
    ]
    
    evidence: list[EvidenceItem]
    suggested_revision: Optional[ActionSpec]  # Alternative if critique invalidates original
    severity: Literal["BLOCKING", "ADVISORY"]  # BLOCKING prevents consensus; ADVISORY is informational
```

#### Message Type 3: Revised Claim

```python
class RevisedClaim(ClaimProposal):
    """Updated claim after incorporating peer critiques."""
    original_claim_id: str
    revisions_applied: list[str]  # Which critique IDs were addressed
    critiques_rejected: list[CritiqueRejection]  # Which critiques were rejected and why
    confidence_delta: float  # How confidence changed after revision
```

### 7.3 Communication Flow (Per Deliberation Cycle)

```
+=============================================================================+
|                    DELIBERATION COMMUNICATION FLOW                          |
+=============================================================================+
|                                                                             |
|  Phase 2: PARALLEL PROPOSAL GENERATION                                     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ All 6 agents receive DisruptionContext via Kafka topic              │   |
|  │ Each agent independently:                                           │   |
|  │   1. Retrieves context (RAG)                                       │   |
|  │   2. Runs ML models                                                │   |
|  │   3. Reasons via LLM                                               │   |
|  │   4. Publishes ClaimProposal to scof.agents.claims.proposed        │   |
|  │ Timeout: 850ms per agent                                           │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
|  Phase 3: CROSS-EXAMINATION                                                |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Coordinator distributes all N claims to all N agents               │   |
|  │ Each agent reviews peer claims and:                                │   |
|  │   1. Checks for cross-domain constraint violations                 │   |
|  │   2. Identifies information conflicts with own data                │   |
|  │   3. Evaluates cost/risk impacts on own domain                     │   |
|  │   4. Publishes AgentCritique to scof.agents.critiques.emitted      │   |
|  │ Timeout: 500ms per agent                                           │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
|  Phase 3b: REVISION (Optional, if BLOCKING critiques exist)                |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Agents whose claims received BLOCKING critiques:                   │   |
|  │   1. Evaluate the critique evidence                                │   |
|  │   2. Either revise their claim or reject the critique with evidence│   |
|  │   3. Publish RevisedClaim to scof.agents.claims.revised            │   |
|  │ Timeout: 500ms per revision                                        │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
|  Phase 4: CONSENSUS HAND-OFF                                               |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Coordinator collates:                                               │   |
|  │   - All final claims (revised or original)                         │   |
|  │   - All critiques (addressed and unaddressed)                      │   |
|  │   - Complete deliberation transcript                               │   |
|  │ Publishes ClaimBundle to scof.consensus.submitted                  │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
+=============================================================================+
```

### 7.4 Communication Basis: What Determines Who Talks to Whom

Not every agent needs to communicate with every other agent for every disruption. The communication topology is **disruption-driven**:

| Disruption Type | Primary Agents | Secondary Agents | Communication Pairs |
| :--- | :--- | :--- | :--- |
| **Supplier Delay** | Procurement, Logistics | Inventory, Finance | Procurement <-> Logistics (route feasibility), Procurement <-> Finance (cost exposure) |
| **Demand Surge** | Demand, Inventory | Procurement, Logistics | Demand <-> Inventory (stock sufficiency), Inventory <-> Procurement (emergency order) |
| **Route Closure** | Logistics, Procurement | Inventory, Demand | Logistics <-> Procurement (alternate source), Logistics <-> Inventory (delivery ETA impact) |
| **Asset Failure** | Inventory, Logistics | Risk, Finance | Inventory <-> Logistics (cross-dock transfer), Inventory <-> Risk (cascade assessment) |
| **Financial Exposure** | Finance, Procurement | Risk, All | Finance <-> Procurement (budget compliance), Finance <-> Risk (default assessment) |
| **Quality Failure** | Risk, Inventory | Procurement, Demand | Risk <-> Inventory (quarantine scope), Risk <-> Procurement (supplier penalty) |

---

## EIGHT: The Deliberation Table -- Centralized Cognitive Boardroom Architecture

> [!IMPORTANT]
> This section supersedes and replaces the communication flow described in Section 7.3 and 7.4 above. The message schemas (ClaimProposal, AgentCritique, RevisedClaim) from Section 7.2 remain valid as the data contracts used within this new architecture. The key architectural shift: **No agent ever communicates with another agent directly. Every interaction passes through the Deliberation Table, mediated by the Coordinator.**

### 8.1 Core Principle: Why No Direct Agent-to-Agent Communication

The original SCOF architectural invariant states it plainly: agents are autonomous domain specialists, not free-roaming conversationalists. If Agent A could directly invoke Agent B, we introduce:

1. **Uncontrolled dependency chains:** Agent A calls Agent B, which needs data from Agent C, creating cascading synchronous call graphs that become impossible to debug, audit, or timeout.
2. **Loss of auditability:** The Coordinator's role as the single orchestration authority means every state transition is observable. Direct agent communication creates invisible side channels.
3. **Priority inversion:** If Agent A directly pushes work onto Agent B, there is no central authority ensuring Agent B is not already serving a higher-priority task from the Coordinator.
4. **Consensus contamination:** Agents that communicate directly before consensus may unknowingly bias each other's independent assessments, undermining the mathematical independence assumption in CD2F's composite weighting formula ($W_i = w_i \times c_i \times R_i$).

The Deliberation Table preserves agent independence while enabling structured multi-party collaboration.

### 8.2 The Deliberation Table: Conceptual Model

Think of it as a physical boardroom conference table. The table is the single shared workspace. Every participant (agent, human operator, system trigger) places items on the table. Every participant can observe what is on the table. But no participant whispers to another -- every utterance goes through the table and is visible to the room (mediated by the Coordinator as the chairperson).

```
+=============================================================================+
|                                                                             |
|                    THE DELIBERATION TABLE                                   |
|              (Centralized Cognitive Boardroom)                              |
|                                                                             |
|  +-----------------------------------------------------------------------+  |
|  |                                                                       |  |
|  |   ITEM #1          ITEM #2          ITEM #3          ITEM #4         |  |
|  |   [Disruption]     [Agent Claim]    [Agent Critique]  [Human Query]   |  |
|  |   Posted by:       Posted by:       Posted by:        Posted by:      |  |
|  |   System/D01       Demand Agent     Inventory Agent   D09 Console     |  |
|  |   Status:          Status:          Status:           Status:         |  |
|  |   SCOPED           RESOLVED         PENDING_REVIEW    AWAITING_WORK   |  |
|  |   Priority: P0     Priority: P2     Priority: P2      Priority: P1   |  |
|  |                                                                       |  |
|  +-----------------------------------------------------------------------+  |
|                              |                                              |
|                     [COORDINATOR]                                            |
|                   Chairperson / Mediator                                    |
|                   - Manages table items                                     |
|                   - Routes tasks to agents                                  |
|                   - Enforces priority ordering                              |
|                   - Collects verdicts                                       |
|                   - Hands off to CD2F                                       |
|                                                                             |
|  +--------+  +--------+  +--------+  +--------+  +--------+  +--------+   |
|  |Demand &|  |Invent. |  |Procure.|  |Logist. |  |Finance |  |Risk &  |   |
|  |Commerce|  |& Asset |  |& Suppl.|  |& Trans.|  |Ops     |  |Compli. |   |
|  +--------+  +--------+  +--------+  +--------+  +--------+  +--------+   |
|                                                                             |
|  Agents observe the table. They respond ONLY when the Coordinator          |
|  assigns them a table item. They NEVER address each other directly.        |
|                                                                             |
+=============================================================================+
```

### 8.3 The Deliberation Table Data Structure

The Deliberation Table is not an abstract metaphor -- it is a concrete, persistent data structure. It lives in PostgreSQL (consistent with the System of Record principle from D2) with a hot cache in Redis for sub-millisecond reads during active deliberation sessions.

```python
class DeliberationTableItem(BaseModel):
    """A single item placed on the Deliberation Table."""

    # Identity
    item_id: str                         # Unique identifier (e.g., "DTI-20260926-00042")
    session_id: str                      # Groups items within a single deliberation session
    scenario_id: str                     # Links to the simulation scenario context
    sim_run_id: str                      # Links to the simulation run

    # Origin
    posted_by: str                       # Agent ID, "coordinator", "human:operator_id", or "system"
    posted_at: datetime                  # Timestamp of posting
    origin_type: Literal[
        "DISRUPTION_TRIGGER",            # System or scenario-injected disruption event
        "AGENT_CLAIM",                   # Specialist agent's structured recommendation
        "AGENT_CRITIQUE",                # Agent's challenge to a peer claim
        "AGENT_REVISED_CLAIM",           # Revised claim after addressing critiques
        "AGENT_QUERY",                   # Agent needs cross-domain information
        "HUMAN_QUERY",                   # Human operator poses a question
        "HUMAN_DIRECTIVE",               # Human operator issues a command/override
        "COORDINATOR_DIRECTIVE",         # Coordinator issues a procedural instruction
        "INFORMATION_RESPONSE",          # Response to a query (from any source)
    ]

    # Content
    payload: dict                        # The actual content (ClaimProposal, AgentCritique,
                                         # RevisedClaim, query text, directive, etc.)
    payload_schema: str                  # Schema identifier for payload validation

    # Priority & Scheduling
    priority: Literal["P0", "P1", "P2", "P3"]
    urgency_score: float                 # [0.0, 1.0] -- fine-grained ordering within a priority tier

    # Lifecycle
    status: Literal[
        "POSTED",                        # Just placed on the table
        "SCOPED",                        # Coordinator has classified and scoped it
        "ASSIGNED",                      # Routed to specific agent(s) for action
        "IN_PROGRESS",                   # Assigned agent(s) actively working
        "VERDICT_POSTED",                # Agent(s) have posted their response
        "RESOLVED",                      # Item fully resolved (all verdicts collected)
        "WITHDRAWN",                     # Poster withdrew the item
        "EXPIRED",                       # SLA timeout exceeded without resolution
    ]

    # Domain Routing (populated by Coordinator during SCOPED phase)
    domain_affinity_scores: dict[str, float]   # Agent ID -> probability score [0.0, 1.0]
    assigned_agents: list[str]                  # Agent IDs that must respond
    optional_agents: list[str]                  # Agent IDs that may respond if relevant

    # Responses (populated as agents post verdicts)
    verdicts: list[DeliberationVerdict]         # Collected agent responses
    
    # SLA
    deadline: datetime                          # Hard deadline for resolution
    sla_budget_ms: int                          # Maximum wall-clock time allowed


class DeliberationVerdict(BaseModel):
    """An agent's response to a Deliberation Table item."""
    
    verdict_id: str
    item_id: str                         # Which table item this responds to
    agent_id: str                        # Which agent posted this verdict
    posted_at: datetime
    
    verdict_type: Literal[
        "CLAIM",                         # Full structured claim proposal
        "CRITIQUE",                      # Critique of another agent's claim
        "INFORMATION",                   # Factual data response to a query
        "ENDORSEMENT",                   # Agent agrees with a peer's claim
        "ABSTENTION",                    # Agent declares item outside its domain
        "REVISED_CLAIM",                 # Revised claim after critique
    ]
    
    payload: dict                        # The verdict content
    confidence: float                    # Agent's confidence in this verdict
    processing_time_ms: float            # How long the agent took to produce this
```

### 8.4 The Deliberation Session Lifecycle

A complete deliberation session (handling one disruption or query from start to consensus) follows this lifecycle:

```
+=============================================================================+
|               DELIBERATION SESSION LIFECYCLE                                |
+=============================================================================+
|                                                                             |
|  PHASE 0: ITEM ARRIVAL                                                     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ A new item arrives on the Deliberation Table:                       │   |
|  │   - Disruption event from D01/Kafka/IoT sensors                    │   |
|  │   - Human query from D09 Desktop Console                          │   |
|  │   - Agent-generated query during its own analysis                  │   |
|  │                                                                     │   |
|  │ The item is posted with status = POSTED                            │   |
|  │ The item is immediately published to Kafka topic:                  │   |
|  │   scof.deliberation.table.items                                    │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|                              v                                              |
|  PHASE 1: COORDINATOR SCOPING & DOMAIN ROUTING                            |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ The Coordinator (and ONLY the Coordinator) picks up POSTED items.  │   |
|  │                                                                     │   |
|  │ Step 1: CLASSIFY the item                                          │   |
|  │   - What type is it? (disruption, query, claim, critique)          │   |
|  │   - What priority? (P0/P1/P2/P3 -- see Section 8.5)              │   |
|  │                                                                     │   |
|  │ Step 2: COMPUTE DOMAIN AFFINITY SCORES                            │   |
|  │   (Probabilistic routing -- see Section 8.6)                      │   |
|  │   For each agent, compute P(item belongs to agent's domain)       │   |
|  │   Using: semantic embedding similarity + keyword matching          │   |
|  │          + disruption-type-to-domain static mapping               │   |
|  │   Example: Supplier delay disruption ->                            │   |
|  │     procurement_supplier: 0.92                                     │   |
|  │     logistics_transport:  0.78                                     │   |
|  │     inventory_asset:      0.65                                     │   |
|  │     finance_ops:          0.54                                     │   |
|  │     demand_commerce:      0.31                                     │   |
|  │     risk_compliance:      0.48                                     │   |
|  │                                                                     │   |
|  │ Step 3: ASSIGN AGENTS based on threshold                          │   |
|  │   - Score >= 0.60: ASSIGNED (must respond)                        │   |
|  │   - 0.40 <= Score < 0.60: OPTIONAL (may respond if relevant)     │   |
|  │   - Score < 0.40: NOT ASSIGNED (agent is not notified)            │   |
|  │                                                                     │   |
|  │ Step 4: Set DEADLINE based on priority                            │   |
|  │   P0: 500ms | P1: 850ms | P2: 1200ms | P3: 5000ms               │   |
|  │                                                                     │   |
|  │ Status transitions: POSTED -> SCOPED -> ASSIGNED                  │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|                              v                                              |
|  PHASE 2: AGENT PROCESSING                                                 |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Each ASSIGNED agent receives notification (via Kafka consumer):    │   |
|  │   "Table item DTI-xxxx has been assigned to you."                 │   |
|  │                                                                     │   |
|  │ Agent actions:                                                     │   |
|  │   1. Checks its internal task queue (see Section 8.7)             │   |
|  │   2. Enqueues the table item according to local priority          │   |
|  │   3. When scheduled: retrieves context (RAG), runs ML models,     │   |
|  │      reasons via LLM, produces a verdict                         │   |
|  │   4. Posts verdict back to the Deliberation Table                 │   |
|  │                                                                     │   |
|  │ OPTIONAL agents:                                                   │   |
|  │   - Receive the notification but may post ABSTENTION if they      │   |
|  │     determine the item is not within their actionable scope       │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|                              v                                              |
|  PHASE 3: VERDICT COLLECTION & CROSS-EXAMINATION                          |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ As verdicts arrive, the Coordinator:                                │   |
|  │   1. Validates each verdict against the expected schema            │   |
|  │   2. Posts ALL received claims back to the table as new items     │   |
|  │      with origin_type = AGENT_CLAIM                               │   |
|  │   3. Computes domain affinity for each claim (who should review?) │   |
|  │   4. Assigns cross-examination tasks to relevant agents           │   |
|  │      (e.g., "Logistics Agent, review this claim from Procurement  │   |
|  │       that proposes rerouting via air freight")                    │   |
|  │   5. Collects critique verdicts                                    │   |
|  │                                                                     │   |
|  │ If BLOCKING critiques exist:                                       │   |
|  │   6. Posts revision requests to the critiqued agents              │   |
|  │   7. Collects revised claims                                       │   |
|  │                                                                     │   |
|  │ Timeout enforcement: if an agent misses deadline, Coordinator     │   |
|  │ proceeds with available verdicts (fail-open with audit log)       │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|                              v                                              |
|  PHASE 4: CONSENSUS HAND-OFF                                              |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Once all verdicts are collected (or deadline expires):             │   |
|  │   1. Coordinator assembles the complete deliberation transcript   │   |
|  │      from all table items in this session                         │   |
|  │   2. Packages claims + critiques + verdicts into ClaimBundle      │   |
|  │   3. Submits to CD2F Consensus Engine                             │   |
|  │   4. CD2F resolves -> Tier 1/2/3                                  │   |
|  │   5. Decision applied to Twin Layer 3 (or HITL escalation)       │   |
|  │   6. Session marked RESOLVED                                      │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
+=============================================================================+
```

### 8.5 Priority Classification for Table Items

The priority system reuses the existing [4-Tier Priority Queue](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md) already established for Twin Service concurrency. We extend it to govern the Deliberation Table itself:

| Priority | Source | Examples | Deadline |
| :--- | :--- | :--- | :--- |
| **P0: Emergency** | System telemetry, critical asset failure, cold-chain breach | Cold-storage compressor failure at DC-003; Critical supplier declares force majeure | 500ms |
| **P1: Human-Escalated / HITL** | D09 Desktop Console operator, human override, CD2F Tier-3 escalation | Operations Director queries impact of rerouting decision; Human rejects proposed action and demands alternatives | 850ms |
| **P2: Agent Deliberation** | Specialist agents during routine disruption handling | Demand Agent posts forecast claim; Inventory Agent critiques procurement volume proposal | 1200ms |
| **P3: Background / Analytical** | D10 benchmark harness, long-horizon risk scanning, batch analytics | Risk Agent scans geopolitical exposure for all 200 suppliers; Background precedent indexing | 5000ms |

**Critical rule: Human-escalated items receive P1 priority unless the Coordinator's classification determines the query is generic/informational (e.g., "What is the address of DC-002?"), in which case it is downgraded to P2 and routed directly to D2 Knowledge Fabric via the Tri-Zone Fast-Path router without occupying agent capacity.**

The Coordinator classifies human queries using the same [Tri-Zone Cognitive Query Routing](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md) confidence scoring:
- Confidence >= 0.85 on Class A (direct fact lookup) -> Fast-Path to D2, no agent involvement, priority irrelevant
- Confidence >= 0.85 on Class B/C or ambiguous -> P1 priority, full agent deliberation
- Confidence < 0.50 -> Zone 3 Fallback: request clarification from the human before assigning priority

### 8.6 Probabilistic Domain Affinity Scoring: Who Gets the Task?

This is the answer to "who tells the agent whether or not the query belongs to their domain?" The answer: **the Coordinator computes probabilistic domain affinity scores and makes the assignment decision.** Agents do not poll the table. Agents do not self-select. The Coordinator assigns.

This directly reuses the probabilistic approach from the Knowledge Layer's Tri-Zone Cognitive Router and the Dynamic Capability Registry's semantic matching.

#### 8.6.1 The Domain Affinity Computation Pipeline

```
+=============================================================================+
|              COORDINATOR: DOMAIN AFFINITY SCORING PIPELINE                 |
+=============================================================================+
|                                                                             |
|  INPUT: Deliberation Table Item (disruption event, query, claim, etc.)     |
|                                                                             |
|  STEP 1: STATIC DISRUPTION-TYPE MAPPING (Fast-Path)                       |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Pre-computed lookup table based on disruption taxonomy:             │   |
|  │                                                                     │   |
|  │ disruption_type: "supplier_delay"                                  │   |
|  │   procurement_supplier: 0.95  (primary domain)                    │   |
|  │   logistics_transport:  0.70  (freight implications)              │   |
|  │   inventory_asset:      0.60  (stock buffer impact)               │   |
|  │   finance_ops:          0.50  (cost exposure)                     │   |
|  │   demand_commerce:      0.25  (minimal direct impact)             │   |
|  │   risk_compliance:      0.45  (supplier health context)           │   |
|  │                                                                     │   |
|  │ disruption_type: "demand_surge"                                    │   |
|  │   demand_commerce:      0.95  (primary domain)                    │   |
|  │   inventory_asset:      0.85  (stock sufficiency)                 │   |
|  │   procurement_supplier: 0.55  (emergency order needed?)           │   |
|  │   logistics_transport:  0.50  (capacity to deliver?)              │   |
|  │   finance_ops:          0.40  (budget impact)                     │   |
|  │   risk_compliance:      0.20  (minimal)                           │   |
|  │                                                                     │   |
|  │ ... (defined for all disruption types in the catalog)             │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  For disruption events with a known type, the static map provides          |
|  the base scores. If confidence in the static map >= 0.85, use it          |
|  directly (Fast-Path, < 5ms).                                              |
|                              |                                              |
|  STEP 2: SEMANTIC SIMILARITY ENRICHMENT (if needed)                        |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ For free-text queries, human questions, or novel disruption types  │   |
|  │ not in the static map:                                             │   |
|  │                                                                     │   |
|  │ 1. Embed the item's payload text using all-MiniLM-L6-v2           │   |
|  │ 2. Compare against each agent's domain description embedding      │   |
|  │    (pre-computed and cached in Redis)                              │   |
|  │ 3. Cosine similarity produces the affinity score per agent        │   |
|  │                                                                     │   |
|  │ This reuses the exact same pgvector infrastructure from D2        │   |
|  │ and the same embedding model from D07's semantic archival.        │   |
|  │ No new system is introduced.                                       │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  STEP 3: CAPABILITY REGISTRY CROSS-REFERENCE                              |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ If the item involves specific MCP tool requirements (e.g., the    │   |
|  │ query mentions "contract terms" or "freight cost"), the Dynamic    │   |
|  │ Capability Registry is consulted to identify which agents have    │   |
|  │ the bound tools to actually fulfill the request.                  │   |
|  │                                                                     │   |
|  │ This adjusts affinity scores:                                      │   |
|  │   - Agent has required tool: score boosted by +0.15               │   |
|  │   - Agent lacks required tool: score capped at 0.40 maximum      │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  STEP 4: THRESHOLD APPLICATION & ASSIGNMENT                                |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Final affinity scores:                                              │   |
|  │   >= 0.60  ->  ASSIGNED (agent MUST respond within deadline)      │   |
|  │   0.40-0.59 -> OPTIONAL (agent MAY respond; abstention allowed)   │   |
|  │   < 0.40   ->  NOT NOTIFIED (agent is not involved)               │   |
|  │                                                                     │   |
|  │ Minimum: At least 1 agent must be ASSIGNED.                       │   |
|  │ If no agent scores >= 0.60, the highest-scoring agent is force-   │   |
|  │ assigned regardless of threshold (prevents orphaned items).       │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
|  OUTPUT: domain_affinity_scores, assigned_agents, optional_agents          |
|                                                                             |
+=============================================================================+
```

#### 8.6.2 Why the Coordinator Does This (Not the Agents)

The user's instinct is exactly right: agents should not dedicate cognitive capacity to continuously polling the table and self-assessing relevance. The reasons are:

1. **Resource efficiency:** Each agent's LLM inference capacity is precious (bounded by Ollama throughput). Wasting it on "is this my job?" classification for every table item is pure overhead.
2. **Consistency:** The Coordinator uses a single, deterministic scoring pipeline. If each agent self-assessed, six different LLM instances would produce six different relevance judgments with potential inconsistency.
3. **Speed:** The static disruption-type mapping resolves in < 5ms. Semantic enrichment adds < 50ms. An agent using its LLM to assess relevance would take 200-500ms per item.
4. **Existing infrastructure:** The Coordinator already runs the [Tri-Zone Cognitive Router](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md) and the [Dynamic Capability Registry](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md). Domain affinity scoring is a natural extension of what it already does.

### 8.7 Agent-Internal Task Queue: Handling Concurrency Within an Agent

This addresses the critical question: "What if Agent B is already working on something when a new task arrives?"

Each agent maintains a **local priority queue** mirroring the structure of the system-level 4-Tier Priority Queue from the [Minimalist Concurrency Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md). This is not a new system -- it is the same proven pattern applied at the agent level.

```
+=============================================================================+
|                   AGENT-INTERNAL TASK QUEUE                                |
|           (Per-Agent Instance -- Same Pattern as Twin Worker Pool)          |
+=============================================================================+
|                                                                             |
|  INCOMING TABLE ASSIGNMENTS                                                |
|  (Coordinator pushes via Kafka: scof.deliberation.agent.{agent_id})       |
|                              |                                              |
|                              v                                              |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │                    AGENT-LOCAL PRIORITY QUEUE                       │   |
|  │                                                                     │   |
|  │  [P0 Queue]  [ Emergency cold-chain failure assessment ]           │   |
|  │  [P1 Queue]  [ Human-escalated query about supplier health ]      │   |
|  │  [P2 Queue]  [ Routine disruption claim generation ] [ Critique ] │   |
|  │  [P3 Queue]  [ Background risk scan for supplier portfolio ]      │   |
|  │                                                                     │   |
|  │  Rules:                                                             │   |
|  │  1. Strict priority dispatch: P0 before P1 before P2 before P3   │   |
|  │  2. FIFO within each tier                                          │   |
|  │  3. Maximum queue depth: 8 items (reject with OVERLOADED status   │   |
|  │     if exceeded -- Coordinator reassigns to backup or extends     │   |
|  │     deadline)                                                       │   |
|  │  4. Preemption: P0 items can preempt an in-progress P2/P3 task   │   |
|  │     (agent checkpoints current work and switches)                 │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|                              v                                              |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │                    AGENT WORKER THREAD(S)                           │   |
|  │                                                                     │   |
|  │  Default: 1 active worker per agent (sequential processing)       │   |
|  │  Configurable: up to 2 workers for high-throughput agents         │   |
|  │                                                                     │   |
|  │  Worker pulls highest-priority task from queue:                    │   |
|  │    1. Retrieves context from RAG pipeline                         │   |
|  │    2. Runs ML models if applicable                                │   |
|  │    3. Reasons via LLM (LangChain chain)                          │   |
|  │    4. Produces verdict                                             │   |
|  │    5. Posts verdict to Deliberation Table                         │   |
|  │    6. Signals Coordinator: "verdict ready for DTI-xxxx"          │   |
|  │    7. Pulls next task from queue                                   │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
+=============================================================================+
```

#### 8.7.1 What Happens When an Agent is Busy

| Scenario | Agent Behavior | Coordinator Response |
| :--- | :--- | :--- |
| Agent has capacity (queue depth < 8) | Accepts task, enqueues at appropriate priority level | None needed |
| Agent is busy but queue has room | Accepts task, enqueues; processes after current task completes | Coordinator monitors deadline; if deadline risk detected, may extend or reassign |
| Agent queue is full (depth = 8) | Responds with `OVERLOADED` status | Coordinator either: (a) extends deadline for lower-priority items, (b) reassigns to the next-highest-affinity agent, or (c) for P0/P1 items, forces preemption of the agent's lowest-priority in-progress task |
| Agent is unhealthy (health_status = UNHEALTHY in A2A registry) | Not assigned by Coordinator in the first place | Coordinator excludes unhealthy agents from affinity scoring. If the only qualified agent is unhealthy, Coordinator falls back to heuristic-based deterministic rules (no LLM needed) |

### 8.8 Multi-Item Concurrency: When Multiple Items Arrive Simultaneously

This addresses: "Say there are multiple agents posting a query or something at the same time. How is the system scheduled?"

The Deliberation Table handles simultaneous arrivals using the same principles:

#### 8.8.1 At the Table Level (Coordinator's Responsibility)

```
Multiple items arrive simultaneously:
  DTI-001: Supplier delay disruption (system trigger)        -> P0
  DTI-002: Demand Agent query about promotional calendar     -> P2
  DTI-003: Human operator asks "what is our exposure?"       -> P1
  DTI-004: Risk Agent posts early-warning on commodity price -> P2

Coordinator processing order (strict priority, FIFO within tier):
  1. DTI-001 (P0 -- emergency)           -> Scope, compute affinity, assign agents
  2. DTI-003 (P1 -- human-escalated)     -> First: Tri-Zone classify.
                                             If Class A fact lookup -> fast-path to D2
                                             If Class B/C -> scope, compute affinity, assign
  3. DTI-002 (P2 -- agent deliberation)  -> Scope, compute affinity, assign
  4. DTI-004 (P2 -- agent deliberation)  -> Scope, compute affinity, assign
     (DTI-002 before DTI-004 because FIFO within P2)
```

#### 8.8.2 At the Agent Level (Agent's Internal Queue)

When an agent receives multiple assignments from the Coordinator within a short window:

```
Procurement Agent receives simultaneously:
  Assignment 1: DTI-001 (P0 -- supplier delay, affinity 0.92)
  Assignment 2: DTI-003 (P1 -- human query about exposure, affinity 0.71)
  Assignment 3: DTI-002 (P2 -- demand agent's promo calendar query, affinity 0.42)

Agent's internal queue after enqueuing:
  [P0] Assignment 1 (DTI-001) -- processed first
  [P1] Assignment 2 (DTI-003) -- processed second
  [P2] Assignment 3 (DTI-002) -- processed third (this was OPTIONAL anyway,
                                  agent may ABSTAIN if too busy)
```

### 8.9 Cross-Examination Through the Table (The Debate Room in Action)

Here is how the "debate" works concretely through the Deliberation Table. No agent talks to another. Every exchange goes through the table, mediated by the Coordinator.

**Example: Supplier SUP-0042 declares force majeure**

```
TIME  | TABLE ITEM                              | ACTION
------+-----------------------------------------+-------------------------------------------
T+0   | DTI-001: Disruption trigger             | System posts supplier force majeure event.
      |   posted_by: system                     | Status: POSTED
      |   priority: P0                          |
      |   status: POSTED                        |
------+-----------------------------------------+-------------------------------------------
T+5ms | DTI-001 scoped and assigned             | Coordinator computes affinity:
      |   assigned: [procurement, logistics,    |   procurement: 0.95, logistics: 0.78,
      |              inventory]                 |   inventory: 0.65, finance: 0.54
      |   optional: [finance]                   |   (finance is OPTIONAL at 0.54)
      |   status: ASSIGNED                      |   risk: 0.48 (not notified)
------+-----------------------------------------+-------------------------------------------
T+600 | DTI-002: Procurement verdict            | Procurement Agent posts its claim:
ms    |   posted_by: procurement_supplier       |   "Reroute to SUP-0089, lead time +3 days,
      |   origin_type: AGENT_CLAIM              |    MOQ satisfied, cost +$12,400"
      |   priority: P2                          |
      |   status: POSTED                        |
------+-----------------------------------------+-------------------------------------------
T+700 | DTI-003: Logistics verdict              | Logistics Agent posts its claim:
ms    |   posted_by: logistics_transport        |   "Alternate carrier available on Lane-17,
      |   origin_type: AGENT_CLAIM              |    reefer capacity confirmed, transit +2 days"
      |   priority: P2                          |
------+-----------------------------------------+-------------------------------------------
T+800 | DTI-004: Inventory verdict              | Inventory Agent posts its claim:
ms    |   posted_by: inventory_asset            |   "Current buffer at DC-003 covers 4 days.
      |   origin_type: AGENT_CLAIM              |    Expedited cross-dock from DC-001 possible."
      |   priority: P2                          |
------+-----------------------------------------+-------------------------------------------
T+810 | Coordinator initiates cross-examination | Coordinator takes all 3 claims (DTI-002,
ms    |                                         | DTI-003, DTI-004) and posts them back to
      |                                         | the table as cross-examination items.
------+-----------------------------------------+-------------------------------------------
T+815 | DTI-005: Cross-exam request for         | Coordinator asks Logistics:
ms    |   Logistics to review Procurement claim |   "Procurement proposes rerouting to
      |   posted_by: coordinator                |    SUP-0089. Is the alternate origin
      |   origin_type: COORDINATOR_DIRECTIVE    |    serviceable by your carrier network?"
      |   assigned: [logistics_transport]       |
------+-----------------------------------------+-------------------------------------------
T+820 | DTI-006: Cross-exam request for         | Coordinator asks Finance (OPTIONAL earlier,
ms    |   Finance to assess cost impact         |   now explicitly asked):
      |   posted_by: coordinator                |   "Procurement proposes +$12,400 expedited
      |   assigned: [finance_ops]               |    sourcing. Does this fit Q3 budget?"
------+-----------------------------------------+-------------------------------------------
T+1100| DTI-007: Logistics critique             | Logistics responds to DTI-005:
ms    |   posted_by: logistics_transport        |   "Lane-17 to SUP-0089 origin has capacity
      |   origin_type: AGENT_CRITIQUE           |    but only for DRY VAN, not REEFER.
      |   verdict_type: CRITIQUE                |    Product requires reefer. BLOCKING."
      |   severity: BLOCKING                    |
------+-----------------------------------------+-------------------------------------------
T+1200| DTI-008: Finance response               | Finance responds to DTI-006:
ms    |   posted_by: finance_ops                |   "Q3 emergency procurement budget has
      |   origin_type: INFORMATION_RESPONSE     |    $45,000 remaining. $12,400 is within
      |   verdict_type: INFORMATION             |    budget. No constraint violation."
------+-----------------------------------------+-------------------------------------------
T+1210| DTI-009: Coordinator requests revision  | Coordinator sees BLOCKING critique on
ms    |   posted_by: coordinator                | Procurement's claim. Posts revision
      |   origin_type: COORDINATOR_DIRECTIVE    | request to Procurement:
      |   assigned: [procurement_supplier]      |   "Your proposal is blocked: Lane-17
      |                                         |    lacks reefer. Revise with reefer-
      |                                         |    capable alternative."
------+-----------------------------------------+-------------------------------------------
T+1600| DTI-010: Procurement revised claim      | Procurement revises:
ms    |   posted_by: procurement_supplier       |   "Updated: Reroute to SUP-0112 (reefer
      |   origin_type: AGENT_REVISED_CLAIM      |    capable), lead time +5 days,
      |   status: POSTED                        |    cost +$18,200"
------+-----------------------------------------+-------------------------------------------
T+1700| Coordinator collects all verdicts       | All assigned agents have responded.
ms    | Assembles ClaimBundle:                  | Claims: DTI-002(revised->DTI-010),
      |   - 3 original claims                   |          DTI-003, DTI-004
      |   - 1 BLOCKING critique (DTI-007)      | Critiques: DTI-007
      |   - 1 revised claim (DTI-010)          | Info: DTI-008
      |   - 1 info response (DTI-008)          |
      |                                         | Submits to CD2F for consensus.
------+-----------------------------------------+-------------------------------------------
T+1850| CD2F resolves: TIER_1 (Automated)      | Weighted consensus score = 0.82
ms    | Selected action: Revised procurement   | Applied to Twin Layer 3.
      |   (SUP-0112 reroute with reefer)       | Session marked RESOLVED.
------+-----------------------------------------+-------------------------------------------
```

### 8.10 Implementation: Reusing Existing Systems

> [!TIP]
> Per the directive: "Lets try to make use of the existing systems to its fullest and efficiency." The Deliberation Table introduces zero new infrastructure. It is built entirely on existing SCOF components.

| Deliberation Table Component | Existing System Reused | What It Provides |
| :--- | :--- | :--- |
| **Table storage (persistent)** | **PostgreSQL** (D2 System of Record) | New `deliberation_items` and `deliberation_verdicts` tables in the existing observability schema. Same DB, same connection pool. |
| **Table hot cache (real-time)** | **Redis** (already in docker-compose.yml, port 6379) | Active session items cached as Redis hashes with TTL. Sub-millisecond reads during active deliberation. Already provisioned. |
| **Item notification / pub-sub** | **Kafka** (already elevated in Section SIX) | New topic `scof.deliberation.table.items` in the existing Kafka cluster. Agents subscribe to `scof.deliberation.agent.{agent_id}` for their assignments. Already provisioned. |
| **Domain affinity: static mapping** | **Domain Profile** (`disruptions.yaml` in profiles/) | The disruption catalog already maps disruption types to domain tags. We extend it with affinity scores per agent. Same YAML, same loader. |
| **Domain affinity: semantic matching** | **pgvector** (D2 Semantic Memory Projection) + `all-MiniLM-L6-v2` | Same embedding model, same vector index already used by D07 Semantic Precedent Memory. We pre-compute agent domain description embeddings and store them alongside existing embeddings. |
| **Domain affinity: capability matching** | **Dynamic Capability Registry** (Section FIVE) | The registry already maps capabilities to agents. We query it to verify tool availability. Already designed. |
| **Priority queue (system-level)** | **4-Tier Priority Queue** (already specified in [04_minimalist_concurrency](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md)) | Same P0/P1/P2/P3 tiers, same FIFO within tier, same bounded concurrency model. Applied at the table level and mirrored inside each agent. |
| **Query classification** | **Tri-Zone Cognitive Router** (already specified in [02_cognitive_query_routing](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md)) | For human queries: classifies whether it needs agent deliberation or can be fast-pathed to D2 directly. Already designed with confidence scoring. |
| **Agent health monitoring** | **A2A Registry** (existing [a2a_registry.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/a2a_registry.py)) | Health status (HEALTHY/DEGRADED/UNHEALTHY) already tracked per agent. Coordinator checks this before assignment. Already implemented. |
| **Observability / audit trail** | **D07 Observability Framework** | Every table item and verdict is an audit record. The 8-Stage Reasoning Trace already captures deliberation transcripts. Deliberation Table items become the authoritative source for Stages 3-5. |

### 8.11 PostgreSQL Schema for the Deliberation Table

```sql
-- Extends the existing observability schema (03_observability_schema.sql)

CREATE TABLE IF NOT EXISTS deliberation_sessions (
    session_id       VARCHAR(64) PRIMARY KEY,
    scenario_id      VARCHAR(64) NOT NULL,
    sim_run_id       VARCHAR(64),
    initiated_by     VARCHAR(64) NOT NULL,       -- "system", "human:op-001", agent_id
    initiated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status           VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    resolved_at      TIMESTAMPTZ,
    consensus_id     VARCHAR(64),                 -- FK to CD2F decision if resolved
    total_items      INTEGER DEFAULT 0,
    total_verdicts   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS deliberation_items (
    item_id                VARCHAR(64) PRIMARY KEY,
    session_id             VARCHAR(64) NOT NULL REFERENCES deliberation_sessions(session_id),
    scenario_id            VARCHAR(64) NOT NULL,
    sim_run_id             VARCHAR(64),
    posted_by              VARCHAR(64) NOT NULL,
    posted_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    origin_type            VARCHAR(32) NOT NULL,
    payload                JSONB NOT NULL,
    payload_schema         VARCHAR(64),
    priority               VARCHAR(4) NOT NULL DEFAULT 'P2',
    urgency_score          REAL DEFAULT 0.5,
    status                 VARCHAR(32) NOT NULL DEFAULT 'POSTED',
    domain_affinity_scores JSONB,                 -- {"agent_id": score, ...}
    assigned_agents        TEXT[],                -- Array of assigned agent IDs
    optional_agents        TEXT[],                -- Array of optional agent IDs
    deadline               TIMESTAMPTZ,
    sla_budget_ms          INTEGER,
    resolved_at            TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS deliberation_verdicts (
    verdict_id       VARCHAR(64) PRIMARY KEY,
    item_id          VARCHAR(64) NOT NULL REFERENCES deliberation_items(item_id),
    session_id       VARCHAR(64) NOT NULL REFERENCES deliberation_sessions(session_id),
    agent_id         VARCHAR(64) NOT NULL,
    posted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verdict_type     VARCHAR(32) NOT NULL,
    payload          JSONB NOT NULL,
    confidence       REAL,
    processing_ms    REAL
);

-- Indexes for real-time queries during active deliberation
CREATE INDEX idx_delib_items_session_status ON deliberation_items(session_id, status);
CREATE INDEX idx_delib_items_priority ON deliberation_items(priority, posted_at);
CREATE INDEX idx_delib_verdicts_item ON deliberation_verdicts(item_id);
CREATE INDEX idx_delib_verdicts_agent ON deliberation_verdicts(agent_id, posted_at);
```

### 8.12 Kafka Topics for Deliberation Table

Two new topics added to the existing Kafka topic architecture (Section SIX):

```
TIER 2 (AGENT DELIBERATION & COMMUNICATION) -- additions:

scof.deliberation.table.items          -- All table item events (posted, scoped, 
                                          assigned, resolved). The master feed.
                                          Partitioned by session_id.

scof.deliberation.agent.{agent_id}     -- Per-agent assignment channel.
                                          Each agent subscribes to its own topic.
                                          Coordinator publishes assignments here.
                                          Partitioned by item priority.
```

These fit naturally into the existing Kafka cluster provisioned in [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml). No new Kafka infrastructure is required.

### 8.13 Agent-Generated Queries on the Table

An important scenario: during its own analysis, an agent discovers it needs information from another domain. Under the "no direct communication" rule, it cannot call the other agent. Instead:

```
Inventory Agent is analyzing stock buffer for SKU-8841 at DC-003.
It discovers the primary supplier (SUP-0042) has a disruption flag.
It needs to know: "What is the contract penalty if we emergency-order from SUP-0089?"

WRONG (V1 anti-pattern): Inventory Agent calls Procurement Agent directly.

RIGHT (V2 Deliberation Table):
1. Inventory Agent posts a table item:
     origin_type: AGENT_QUERY
     payload: {
       "query": "What is the contractual penalty and MOQ for emergency 
                 orders from SUP-0089 for product category DAIRY?",
       "requesting_agent": "inventory_asset",
       "context_item_id": "DTI-001"  -- links to the parent disruption
     }
     priority: P2

2. Coordinator picks it up, computes affinity:
     procurement_supplier: 0.92 (contract terms are their domain)
     finance_ops: 0.55 (penalty enforcement is partially theirs)
   Assigns to: procurement_supplier (ASSIGNED), finance_ops (OPTIONAL)

3. Procurement Agent produces verdict:
     verdict_type: INFORMATION
     payload: {
       "contract_id": "CTR-0089-DAIRY",
       "moq": 500,
       "penalty_per_unit_below_moq": 2.40,
       "emergency_lead_time_days": 7
     }

4. Verdict is posted to the table. Inventory Agent retrieves it and 
   incorporates it into its ongoing claim generation.
```

This pattern ensures:
- Full auditability (the query and response are table items)
- No hidden inter-agent channels
- The Coordinator can prioritize the query appropriately
- Other agents (like Finance) can optionally contribute

### 8.14 Relationship Between Sections SEVEN and EIGHT

> [!NOTE]
> Section SEVEN (Inter-Agent Communication Protocol) defined the message schemas (ClaimProposal, AgentCritique, RevisedClaim) and the disruption-driven communication topology. These remain valid. Section EIGHT defines **where and how** these messages are exchanged: through the Deliberation Table, mediated by the Coordinator. The schemas from Section 7.2 become the `payload` content within `DeliberationTableItem` and `DeliberationVerdict` objects.

| Section SEVEN Concept | Section EIGHT Realization |
| :--- | :--- |
| ClaimProposal message type | Verdict with `verdict_type = "CLAIM"`, payload = ClaimProposal |
| AgentCritique message type | Verdict with `verdict_type = "CRITIQUE"`, payload = AgentCritique |
| RevisedClaim message type | Verdict with `verdict_type = "REVISED_CLAIM"`, payload = RevisedClaim |
| "Communication topology table" (7.4) | Replaced by probabilistic domain affinity scores. The Coordinator dynamically computes which agents are relevant per-item, rather than relying on a static disruption-to-agent mapping |
| "Agents receive disruption via Kafka" (7.3) | Agents receive assignments via `scof.deliberation.agent.{agent_id}` Kafka topic, not directly from the disruption stream |
| Phase 3 cross-examination | Cross-examination items posted to the table by the Coordinator; agents respond with critique verdicts |

### 8.15 Updated Implementation Sequencing (Additions)

The following tasks are inserted into the existing implementation phases:

**Phase 1 (Foundation, Weeks 1-3) -- additions:**
- Design and create `deliberation_sessions`, `deliberation_items`, `deliberation_verdicts` PostgreSQL tables
- Create Kafka topics: `scof.deliberation.table.items`, `scof.deliberation.agent.{agent_id}` (6 topics)
- Implement Redis hot cache layer for active session items

**Phase 2 (Agent Transformation, Weeks 4-6) -- additions:**
- Implement agent-internal priority queue in `scof_shared/agent_base/task_queue.py`
- Add overload detection and `OVERLOADED` response handling to each agent
- Implement preemption logic for P0 items

**Phase 3 (Orchestration Overhaul, Weeks 7-8) -- additions:**
- Implement `DeliberationTableManager` in the Coordinator service
- Implement domain affinity scoring pipeline (static map + semantic enrichment + capability cross-reference)
- Implement the full session lifecycle (POSTED -> SCOPED -> ASSIGNED -> VERDICT_POSTED -> RESOLVED)
- Integrate Tri-Zone Router for human query classification before table posting

**Phase 4 (Consensus & Integration, Weeks 9-10) -- additions:**
- Wire CD2F to consume from the Deliberation Table's assembled claim bundles
- Update D07 observability to source 8-Stage Reasoning Trace data from table items
- Update D09 Desktop Console to display the live Deliberation Table state in the War Room view

---

## Cross-Cutting: Integration with D1/D2 Knowledge Layers & Twin Service {#cross-cutting}

### Twin Service Integration

The [twin_service.py](file:///d:/projects/SCOF_V1/SCOF/services/twin_service.py) provides the operational simulation substrate. All architectural changes above must respect the Twin's boundaries as defined in [06_subsystem_boundaries](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/06_subsystem_boundaries_and_orchestration_contracts.md):

1. **RAG retrieval** queries the Twin for counterfactual scenario state (Layer 3 projections)
2. **Agent claims** that propose physical interventions are validated by the Twin's invariant enforcement
3. **Kafka topics** `scof.twin.actions.committed` and `scof.twin.state.deltas` provide the Twin's event output
4. **The 5-Tier State Hierarchy** ([ADR 017](file:///d:/projects/SCOF_V1/SCOF/docs/adr/017_five_tier_state_hierarchy_and_actuation_boundaries.md)) is respected: agents produce Tier 4 recommendations, CD2F produces Tier 5 decisions, Twin applies to Tier 3

### D2 Knowledge Fabric Integration

The RAG pipeline relies heavily on D2:
- **PostgreSQL** (System of Record) provides factual state for all agent queries
- **Neo4j** (Topological Projection) provides structural context for graph-aware reasoning
- **pgvector** (Semantic Memory) provides historical precedent retrieval

### Tri-Zone Cognitive Query Routing

The [Tri-Zone Router](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md) governs how RAG queries are classified:
- **Zone 1 (Fast-Path):** Direct factual lookups (PostgreSQL/Neo4j) -- < 10ms
- **Zone 2 (Ambiguous-Path):** Semantic searches requiring disambiguation (pgvector + Deeper Resolver) -- < 50ms  
- **Zone 3 (Fallback):** Unresolvable queries requiring human clarification

---

## Unified V2 Architecture Diagram {#unified-v2-architecture-diagram}

```
+=============================================================================+
|                          SCOF V2 DECISION ENGINE                           |
|                    (D3 through D10 Unified Architecture)                   |
+=============================================================================+
|                                                                             |
|  +--[D09: DESKTOP CONSOLE]----------------------------------------------+  |
|  | Tauri v2 | WebSocket Feed | HITL Escalation Modal | What-If Lab      |  |
|  +----------------------------------------------------------------------|  |
|       |                    ^                                                |
|       | REST/WS            | Push Events                                   |
|       v                    |                                                |
|  +--[D08: API GATEWAY & EVENT BUS]--------------------------------------+  |
|  | FastAPI | WebSocket Broadcast | Kafka Event Backbone (20+ topics)     |  |
|  +----------------------------------------------------------------------|  |
|       |                    ^                    ^                           |
|       v                    |                    |                           |
|  +--[D07: OBSERVABILITY]--+  +--[D10: EVALUATION]-+                       |
|  | 8-Stage Trace | pgvector  | | Benchmark Suite    |                      |
|  | Contrastive   | Semantic  | | 20 Scenarios       |                      |
|  | Explanations  | Archival  | | RQ1-RQ4 Analysis   |                      |
|  +-------------------+------+ +--------------------+                       |
|                       ^                                                     |
|                       |                                                     |
|  +=================================================================+       |
|  |              LANGGRAPH ORCHESTRATION KERNEL (D05)               |       |
|  |                                                                 |       |
|  |  [Ingest] -> [Route] -> [Bind Tools] -> [Fan-Out] ->          |       |
|  |  -> [Fan-In] -> [Cross-Exam] -> [Consensus] -> [Execute]      |       |
|  |                                                                 |       |
|  |  State Machine | Cycle Management | Timeout Guards             |       |
|  |  LangGraph StateGraph with conditional branching                |       |
|  +=================================================================+       |
|       |              |              |              |              |        |
|       v              v              v              v              v        |
|  +=================================================================+       |
|  |          LANGCHAIN AGENT REASONING LAYER (D03/D04)             |       |
|  |                                                                 |       |
|  | +----------+ +----------+ +----------+ +----------+           |       |
|  | |Demand &  | |Inventory | |Procure-  | |Logistics |           |       |
|  | |Commerce  | |& Asset   | |ment &    | |& Trans-  |           |       |
|  | |Agent     | |Agent     | |Supplier  | |port Agent|           |       |
|  | +----------+ +----------+ +----------+ +----------+           |       |
|  |                                                                 |       |
|  | +----------+ +----------+                                      |       |
|  | |Financial | |Risk &    |    Each Agent:                       |       |
|  | |Operations| |Compliance|    - LangChain ReAct Chain           |       |
|  | |Agent     | |Agent     |    - Ollama LLM (local)              |       |
|  | +----------+ +----------+    - ML Models (XGBoost/Prophet)     |       |
|  |                              - RAG Retriever                    |       |
|  |                              - MCP Tool Calling                 |       |
|  +=================================================================+       |
|       |              |              |              |                        |
|       v              v              v              v                        |
|  +=================================================================+       |
|  |              AGENTIC RAG PIPELINE (Cross-Cutting)              |       |
|  |                                                                 |       |
|  |  Retriever -> Re-Ranker -> Context Assembler -> LLM Prompt     |       |
|  |  Sources: pgvector | Neo4j | PostgreSQL | Redis                 |       |
|  +=================================================================+       |
|       |              |              |              |                        |
|       v              v              v              v                        |
|  +=================================================================+       |
|  |     CD2F CONSENSUS ENGINE (D06) + TWIN SERVICE (Substrate)     |       |
|  |                                                                 |       |
|  |  Multi-factor weighting | Greedy bias detection                |       |
|  |  Tri-tier escalation | Twin sandbox validation                 |       |
|  +=================================================================+       |
|       |                                                                     |
|       v                                                                     |
|  +=================================================================+       |
|  |     D01 + D02: ENTERPRISE DATA FABRIC (Frozen + Baseline)      |       |
|  |                                                                 |       |
|  |  PostgreSQL | Neo4j (3.73M nodes) | pgvector | Redis           |       |
|  |  96 tables | 30 domains | 49,616 SKUs | Immutable Layer 1      |       |
|  +=================================================================+       |
|                                                                             |
+=============================================================================+
```

---

## Implementation Sequencing {#implementation-sequencing}

> [!IMPORTANT]
> These changes are deeply interdependent. The sequencing below minimizes rework by establishing foundations before dependent layers.

### Phase 1: Foundation (Weeks 1-3)
1. **Deploy Ollama infrastructure** (Docker service, model pulling, health checks)
2. **Implement LangChain agent reasoning layer** in `scof_shared/` (prompt templates, output parsers, memory management)
3. **Implement RAG Service Layer** in `scof_shared/rag/` (retriever, re-ranker, context assembler)
4. **Enhance Kafka topic architecture** (create V2 topics, configure retention, partition strategy)

### Phase 2: Agent Transformation (Weeks 4-6)
5. **Refactor existing 4 agents** to hybrid ML+LLM architecture using LangChain
6. **Build Financial Operations Agent** (new)
7. **Build Risk & Compliance Agent** (new)
8. **Implement V2 Agent Card schema** and update A2A registry
9. **Implement MCP V2** with JSON-RPC 2.0 and Dynamic Capability Registry

### Phase 3: Orchestration Overhaul (Weeks 7-8)
10. **Redesign LangGraph state machine** with cyclical deliberation, cross-examination, and conditional routing
11. **Implement structured deliberation protocol** (ClaimProposal, AgentCritique, RevisedClaim)
12. **Integrate Kafka as agent communication backbone** (replace synchronous HTTP with pub/sub)
13. **Update Coordinator** with disruption-driven agent activation logic

### Phase 4: Consensus & Integration (Weeks 9-10)
14. **Enhance CD2F** to handle 6-agent claim bundles with cross-domain externality penalties
15. **Integrate RAG into CD2F** for precedent-aware arbitration
16. **Update Twin Service** integration contracts
17. **Update D07 observability** for enhanced 8-stage traces with RAG audit trail
18. **Update D08 API Gateway** for V2 endpoints and expanded Kafka consumers

### Phase 5: Validation (Weeks 11-12)
19. **Update D10 benchmark suite** for 6-agent evaluation
20. **Execute full scenario suite** across all 4 disruption classes
21. **Performance tuning** (LLM inference latency, Kafka throughput, RAG retrieval speed)
22. **Update D09 Desktop Console** for 6-agent War Room view

---

> [!NOTE]
> This document is a living specification. Each phase above will generate its own detailed implementation tickets. The architecture described here supersedes the D3-D10 sections of [scof_v2_architecture_evolution.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/scof_v2_architecture_evolution.md) for the decision engine components while preserving all D1/D2 and Twin Service contracts established in the prior phases.

---

## NINE: RAG Pipeline Architectural Correction -- Agent-Internal Retrieval Model

> [!IMPORTANT]
> This section is an architectural correction and refinement of Section TWO (Agentic RAG Pipeline). It does not delete or replace Section TWO -- the RAG pipeline concepts, retrieval sources, integration points, and feedback loop described there remain valid. This section corrects a **visual/structural ambiguity** in the unified architecture diagram and provides the definitive placement of RAG within the system.

### 9.1 The Problem: Diagram vs. Prose Contradiction

Your observation identifies a genuine architectural ambiguity. Let me lay out the problem precisely.

**What the unified architecture diagram (Section 10) shows:**

```
  LANGCHAIN AGENT REASONING LAYER (D03/D04)
  +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
  |Agent 1 |  |Agent 2 |  |Agent 3 |  |Agent 4 |  |Agent 5 |  |Agent 6 |
  +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
       |              |              |              |
       v              v              v              v
  +=================================================================+
  |              AGENTIC RAG PIPELINE (Cross-Cutting)              |
  |  Retriever -> Re-Ranker -> Context Assembler -> LLM Prompt     |
  |  Sources: pgvector | Neo4j | PostgreSQL | Redis                 |
  +=================================================================+
       |              |              |              |
       v              v              v              v
  +=================================================================+
  |     CD2F CONSENSUS ENGINE (D06) + TWIN SERVICE (Substrate)     |
  +=================================================================+
```

This diagram **visually implies** that:
1. RAG sits as a standalone layer *below* the agents
2. Agents produce output, which flows *downward* into RAG
3. RAG is a passive intermediary between agents and CD2F/Twin
4. RAG does not have direct access to the knowledge sources -- it only sees what agents hand it

**This implication is WRONG.** And your instinct caught it.

**What the prose in Section 2.3 and the code in Section 3.3 actually describe:**

Looking at Section 2.3 (Phase 2: Agent Proposal Generation):
> *"Each specialist agent, before generating its claim: (1) Retrieves domain-specific historical decisions from pgvector, (2) Retrieves relevant factual state from PostgreSQL via MCP tools, (3) Retrieves structural dependencies from Neo4j via bounded traversals, (4) Assembles a domain-specific context window..."*

Looking at the code in Section 3.3:
```python
class DemandCommerceAgent(BaseAgent):
    def __init__(self, ...):
        # RAG retriever for context assembly
        self.retriever = SCOFRetriever(...)  # <-- RAG is INSIDE the agent
    
    async def analyze(self, context):
        # 1. RAG: Retrieve relevant context
        assembled_ctx = await self.retriever.assemble_context(...)  # <-- Agent calls RAG directly
```

The prose and code clearly describe RAG as **internal to each agent**, with direct access to PostgreSQL, Neo4j, pgvector, and Redis. But the diagram contradicts this by placing RAG as a separate horizontal layer below the agents.

### 9.2 Critical Assessment: Your Idea is Correct

Your idea -- pushing the RAG pipeline into the agents layer internally, letting each agent use its own RAG pipeline -- is not just viable, it is the **only correct architecture**. Here is the critical reasoning:

#### 9.2.1 Why RAG as a Separate External Layer Does Not Work

If RAG were a standalone service sitting below the agents:

| Problem | Explanation |
| :--- | :--- |
| **Context blindness** | A separate RAG layer would not know which domain lens to apply. "Retrieve context about SUP-0042" means completely different things to the Procurement Agent (contract terms, reliability score, alternate vendors) vs. the Finance Agent (outstanding invoices, payment history, financial health). A domain-agnostic retriever would return a generic soup of results. |
| **Latency overhead** | Every agent would need a round-trip to an external RAG service, adding network latency. With 6 agents retrieving concurrently within an 850ms SLA, external calls are budget-critical. |
| **Loss of retrieval precision** | Domain-specific re-ranking requires domain knowledge. The Procurement Agent knows that "reliability" means OTIF compliance, not demand forecast accuracy. A centralized re-ranker cannot hold 6 different domain interpretations simultaneously. |
| **Bottleneck risk** | A centralized RAG service becomes a single point of contention when all 6 agents retrieve simultaneously during Phase 2 fan-out. |
| **No agent autonomy** | The entire point of V2 is making agents autonomous. An agent that cannot independently access knowledge is not autonomous -- it is a puppet that asks someone else to think for it. |

#### 9.2.2 Why RAG Internal to Each Agent is the Right Architecture

| Benefit | Explanation |
| :--- | :--- |
| **Domain-scoped retrieval** | Each agent retrieves through its own domain lens. The Demand Agent's retriever prioritizes demand patterns, promotional impacts, and seasonal precedents. The Procurement Agent's retriever prioritizes contract SLAs, vendor reliability scores, and alternate supplier graphs. Same knowledge sources, different retrieval strategies. |
| **Direct knowledge access** | Each agent holds connection handles to PostgreSQL, Neo4j, pgvector, and Redis. No intermediary. Retrieval is a direct function call, not a network hop. |
| **Agent-specific re-ranking** | Each agent applies its own relevance scoring to retrieved results. The Finance Agent scores precedents by financial impact magnitude. The Risk Agent scores by severity and propagation velocity. |
| **Parallel retrieval** | 6 agents retrieving simultaneously from the shared knowledge fabric is natural. PostgreSQL and Neo4j are designed for concurrent reads. pgvector vector similarity search is embarrassingly parallel. |
| **Consistent with LangChain** | LangChain's agent architecture natively supports this: the `retriever` is a component *inside* the agent chain, not an external service the agent calls. |

### 9.3 The Corrected Architecture: Agent-Internal RAG

Each agent contains its own `SCOFRetriever` instance, initialized at startup with connection handles to all four knowledge sources. The retriever is a **component of the agent**, not a service the agent calls.

```
+=============================================================================+
|                  CORRECTED: AGENT-INTERNAL RAG ARCHITECTURE                |
+=============================================================================+
|                                                                             |
|  Each of the 6 specialist agents contains:                                 |
|                                                                             |
|  +---------------------------------------------------------------------+   |
|  |                 SPECIALIST AGENT (e.g., Procurement)                 |   |
|  |                                                                     |   |
|  |  +--------------------------+    +-----------------------------+    |   |
|  |  | DOMAIN-SCOPED RAG        |    | ML MODEL PIPELINE           |    |   |
|  |  | RETRIEVER INSTANCE       |    |                             |    |   |
|  |  |                          |    | - XGBoost / LightGBM        |    |   |
|  |  | Connected directly to:   |    | - GradientBoosting          |    |   |
|  |  |  - PostgreSQL (factual)  |    | - Prophet / Statistical     |    |   |
|  |  |  - Neo4j (topological)   |    | - Rule-based scorers        |    |   |
|  |  |  - pgvector (semantic)   |    +-----------------------------+    |   |
|  |  |  - Redis (real-time)     |         |                             |   |
|  |  |                          |         | ML outputs                  |   |
|  |  | Domain-specific:         |         |                             |   |
|  |  |  - Retrieval queries     |         v                             |   |
|  |  |  - Re-ranking weights    |    +-----------------------------+    |   |
|  |  |  - Relevance filters     |    | CONTEXT FUSION LAYER        |    |   |
|  |  |  - Precedent matching    |    |                             |    |   |
|  |  +-----------+--------------+    | Combines:                   |    |   |
|  |              |                   |  - RAG retrieved context     |    |   |
|  |              | Retrieved context |  - ML model outputs          |    |   |
|  |              +------------------>|  - Disruption scenario data  |    |   |
|  |                                  |  - Coordinator's base context|    |   |
|  |                                  +-------------+---------------+    |   |
|  |                                                |                    |   |
|  |                                                v                    |   |
|  |                                  +-----------------------------+    |   |
|  |                                  | LLM REASONING ENGINE        |    |   |
|  |                                  | (Ollama via LangChain)       |    |   |
|  |                                  |                             |    |   |
|  |                                  | Prompt = System + Fused Ctx |    |   |
|  |                                  | -> Structured Claim Output  |    |   |
|  |                                  +-----------------------------+    |   |
|  |                                                                     |   |
|  +---------------------------------------------------------------------+   |
|                                                                             |
|  All 6 agents share the same underlying databases but each has its own     |
|  retriever instance with domain-specific configuration.                    |
|                                                                             |
|  +--[PostgreSQL]--+  +--[Neo4j]--+  +--[pgvector]--+  +--[Redis]--+      |
|  | 96 tables      |  | 3.73M    |  | 384-dim      |  | Hot cache |      |
|  | D2 SoR         |  | nodes    |  | embeddings   |  | Ephemeral |      |
|  | Read-only for  |  | Topology |  | Semantic     |  | signals   |      |
|  | agents (L1/L2) |  | graph    |  | precedents   |  |           |      |
|  +----------------+  +----------+  +--------------+  +-----------+      |
|                                                                             |
+=============================================================================+
```

### 9.4 How the Agent-Internal RAG Actually Works: Detailed Per-Agent Flow

Let me walk through exactly what happens inside a single agent when it processes a Deliberation Table assignment. This is the corrected version of the generic flow described in Section 2.3.

**Example: Procurement & Supplier Agent receives DTI-001 (Supplier SUP-0042 force majeure)**

```
+=============================================================================+
|  PROCUREMENT AGENT: INTERNAL RAG-AUGMENTED REASONING FLOW                  |
+=============================================================================+
|                                                                             |
|  INPUT: Deliberation Table assignment (DTI-001, priority P0)               |
|  Context from Coordinator: disruption_type=supplier_delay,                 |
|    target_entity=SUP-0042, severity=5, affected_products=[prod-101..109]   |
|                                                                             |
|  STEP 1: DOMAIN-SCOPED RAG RETRIEVAL                        [< 100ms]     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │                                                                     │   |
|  │  1a. SEMANTIC PRECEDENT RETRIEVAL (pgvector)                       │   |
|  │      Query: Embed("supplier force majeure, severity 5,             │   |
|  │             agricultural products, multi-product disruption")      │   |
|  │      Filter: agent_id = "procurement_supplier"                     │   |
|  │              (only MY past decisions, not all agents')             │   |
|  │      Top-K: 3, min_similarity: 0.75                               │   |
|  │                                                                     │   |
|  │      Result: 3 historical precedents:                              │   |
|  │        P1: "2026-03-14: SUP-0088 force majeure. Rerouted to       │   |
|  │             SUP-0112. Lead time +5 days. Outcome: successful,     │   |
|  │             fill rate maintained at 94%."                          │   |
|  │        P2: "2026-01-22: SUP-0055 factory shutdown. Emergency      │   |
|  │             split order across SUP-0031 + SUP-0099. Outcome:      │   |
|  │             partial success, 12% stockout on perishables."        │   |
|  │        P3: "2025-11-08: SUP-0042 same supplier, minor delay.     │   |
|  │             No reroute needed. Outcome: buffer absorbed."         │   |
|  │                                                                     │   |
|  │  1b. TOPOLOGICAL CONTEXT RETRIEVAL (Neo4j)                        │   |
|  │      Query: "MATCH (s:Supplier {id:'SUP-0042'})-[:SUPPLIES]->     │   |
|  │              (p:Product)<-[:SUPPLIES]-(alt:Supplier)               │   |
|  │              WHERE alt.id <> 'SUP-0042'                           │   |
|  │              RETURN alt, p LIMIT 20"                              │   |
|  │      Max hops: 2                                                   │   |
|  │                                                                     │   |
|  │      Result: 4 alternate suppliers for affected products:          │   |
|  │        ALT-1: SUP-0089 (3 products, lead time 5d, reefer: NO)    │   |
|  │        ALT-2: SUP-0112 (6 products, lead time 7d, reefer: YES)   │   |
|  │        ALT-3: SUP-0031 (2 products, lead time 3d, reefer: YES)   │   |
|  │        ALT-4: SUP-0177 (4 products, lead time 10d, reefer: YES)  │   |
|  │                                                                     │   |
|  │  1c. FACTUAL STATE RETRIEVAL (PostgreSQL via MCP tools)           │   |
|  │      Tool call: get_contract_terms("SUP-0042", "prod-101")       │   |
|  │        -> MOQ: 200 units, penalty: $2.40/unit below MOQ          │   |
|  │      Tool call: get_supplier_scorecard("SUP-0042", 6)            │   |
|  │        -> OTIF: 91%, avg lead time: 6.2 days, defect rate: 1.3% │   |
|  │      Tool call: get_supplier_scorecard("SUP-0112", 6)            │   |
|  │        -> OTIF: 88%, avg lead time: 7.8 days, defect rate: 2.1% │   |
|  │                                                                     │   |
|  │  1d. REAL-TIME SIGNAL CHECK (Redis)                               │   |
|  │      Key: "disruption:SUP-0042:status"                            │   |
|  │        -> severity: 5, estimated_resolution: "2026-10-10"         │   |
|  │      Key: "capacity:SUP-0112:available"                           │   |
|  │        -> available_capacity: 850 units/week                      │   |
|  │                                                                     │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  STEP 2: ML MODEL INFERENCE                                  [< 50ms]     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │  Run GradientBoosting + RuleScorer ensemble on delivery features   │   |
|  │  for SUP-0042 and alternates.                                      │   |
|  │                                                                     │   |
|  │  Result:                                                            │   |
|  │    SUP-0042 reliability score: 0.22 (severely degraded)           │   |
|  │    SUP-0112 reliability score: 0.84                                │   |
|  │    SUP-0031 reliability score: 0.79                                │   |
|  │    Ensemble agreement: 0.91                                        │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  STEP 3: CONTEXT FUSION                                       [< 5ms]     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │  Assemble all retrieved context into a structured prompt:          │   |
|  │                                                                     │   |
|  │  SYSTEM: "You are the Procurement & Supplier specialist agent     │   |
|  │  for SCOF. Your domain: vendor reliability, contract compliance,  │   |
|  │  alternate sourcing, three-way match. Produce a StructuredClaim." │   |
|  │                                                                     │   |
|  │  CONTEXT:                                                           │   |
|  │  [DISRUPTION] Supplier SUP-0042 force majeure, severity 5...      │   |
|  │  [PRECEDENT 1] 2026-03-14: Similar event, rerouted to SUP-0112..│   |
|  │  [PRECEDENT 2] 2026-01-22: Split order approach, partial success.│   |
|  │  [PRECEDENT 3] 2025-11-08: Same supplier, minor, buffer absorbed.│   |
|  │  [GRAPH] 4 alternate suppliers identified via Neo4j traversal... │   |
|  │  [CONTRACT] SUP-0042 MOQ=200, penalty=$2.40/unit below MOQ...    │   |
|  │  [SCORECARD] SUP-0042 OTIF=91%, SUP-0112 OTIF=88%...            │   |
|  │  [ML OUTPUT] SUP-0042 reliability=0.22, SUP-0112=0.84...        │   |
|  │  [REAL-TIME] SUP-0112 capacity=850 units/week available...       │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  STEP 4: LLM REASONING                                       [< 500ms]    |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │  LLM (llama3.1:8b via Ollama) reasons over the fused context:     │   |
|  │                                                                     │   |
|  │  "Based on precedent P1, rerouting to SUP-0112 was successful    │   |
|  │   in a similar scenario. SUP-0112 has reefer capability (unlike  │   |
|  │   SUP-0089 which P1's precedent did not consider). ML reliability │   |
|  │   score confirms SUP-0112 is viable (0.84). Available capacity   │   |
|  │   (850 units/week) exceeds our typical order volume (~600/week). │   |
|  │   Contract terms allow emergency orders above MOQ threshold.     │   |
|  │   However, lead time increases by 1.6 days on average.           │   |
|  │                                                                     │   |
|  │   Recommendation: Reroute to SUP-0112 with reefer transport.     │   |
|  │   Confidence: 0.86 (high agreement, strong precedent support).   │   |
|  │   Risk: Lead time increase may stress store buffer windows."     │   |
|  │                                                                     │   |
|  │  -> Structured output parsed into StructuredClaimV2              │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|  STEP 5: POST TO DELIBERATION TABLE                           [< 10ms]    |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │  Verdict posted with:                                               │   |
|  │    verdict_type: CLAIM                                              │   |
|  │    confidence: 0.86                                                 │   |
|  │    evidence: [precedent_refs, graph_query_hash, ml_output_hash,   │   |
|  │              contract_lookup_hash, redis_signal_hash]              │   |
|  │    processing_time_ms: 665                                          │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
|  Total agent processing time: ~665ms (within 850ms P0 budget)             |
|                                                                             |
+=============================================================================+
```

### 9.5 Domain-Specific RAG Retriever Configuration Per Agent

The `SCOFRetriever` class from Section 2.4 remains the shared implementation in `scof_shared/rag/retriever.py`. What differs per agent is the **configuration** -- each agent instantiates the retriever with domain-specific parameters.

```python
# scof_shared/rag/retriever.py (unchanged from Section 2.4)
class SCOFRetriever:
    """Unified retrieval interface across all SCOF knowledge sources."""
    
    def __init__(
        self,
        pg_pool,
        neo4j_client,
        pgvector_client,
        redis_client,
        domain_config: DomainRetrievalConfig,  # <-- This is what varies per agent
    ):
        self.pg = pg_pool
        self.neo4j = neo4j_client
        self.pgvector = pgvector_client
        self.redis = redis_client
        self.config = domain_config


class DomainRetrievalConfig(BaseModel):
    """Per-agent configuration controlling HOW retrieval works for this domain."""
    
    # Semantic retrieval configuration
    agent_id: str                        # Filter precedents to this agent's history
    domain_tags: list[str]               # Domain tags for filtering (e.g., ["procurement", "supplier"])
    precedent_top_k: int = 5             # How many precedents to retrieve
    precedent_min_similarity: float = 0.70  # Minimum cosine similarity threshold
    
    # Topological retrieval configuration
    primary_node_types: list[str]        # Which Neo4j node types to prioritize
                                         # e.g., ["Supplier", "Contract", "Product"] for Procurement
    max_graph_hops: int = 2              # Bounded traversal depth
    graph_query_templates: list[str]     # Domain-specific Cypher query templates
    
    # Factual state retrieval configuration
    primary_tables: list[str]            # Which PostgreSQL tables to query
                                         # e.g., ["purchase_orders", "contracts", "suppliers"]
    secondary_tables: list[str]          # Additional context tables
    
    # Real-time signal configuration
    redis_key_patterns: list[str]        # Which Redis keys to check
                                         # e.g., ["disruption:*", "capacity:*"]
    
    # Re-ranking weights
    precedent_weight: float = 0.30       # How much to weight semantic precedents
    topological_weight: float = 0.25     # How much to weight graph context
    factual_weight: float = 0.30         # How much to weight current state
    realtime_weight: float = 0.15        # How much to weight ephemeral signals
```

#### 9.5.1 Agent-Specific Retrieval Configurations

| Agent | `primary_node_types` (Neo4j) | `primary_tables` (PostgreSQL) | `redis_key_patterns` | Re-ranking Priority |
| :--- | :--- | :--- | :--- | :--- |
| **Demand & Commerce** | `["Product", "Store", "Event", "Promotion"]` | `["daily_demand", "pos_sales", "promotions", "events"]` | `["demand:*", "promo:*", "weather:*"]` | Factual (0.35) > Precedent (0.30) > Topological (0.20) > Real-time (0.15) |
| **Inventory & Asset** | `["Facility", "Product", "Asset", "StorageUnit"]` | `["inventory_positions", "assets", "goods_receipts", "replenishment_policies"]` | `["inventory:*", "asset:*", "cold_chain:*"]` | Factual (0.35) > Real-time (0.25) > Topological (0.25) > Precedent (0.15) |
| **Procurement & Supplier** | `["Supplier", "Contract", "Product", "PurchaseOrder"]` | `["suppliers", "contracts", "purchase_orders", "three_way_match"]` | `["disruption:*", "capacity:*"]` | Topological (0.30) > Factual (0.30) > Precedent (0.25) > Real-time (0.15) |
| **Logistics & Transport** | `["TransportLane", "Carrier", "Facility", "Route"]` | `["transport_lanes", "shipments", "carriers", "fleet_assets"]` | `["lane_status:*", "carrier:*", "congestion:*"]` | Topological (0.35) > Real-time (0.25) > Factual (0.25) > Precedent (0.15) |
| **Financial Operations** | `["Invoice", "Payment", "FiscalPeriod", "Budget"]` | `["invoices", "payments", "ledger_entries", "fiscal_periods"]` | `["budget:*", "cashflow:*"]` | Factual (0.40) > Precedent (0.25) > Topological (0.20) > Real-time (0.15) |
| **Risk & Compliance** | `["Supplier", "Region", "Regulation", "Inspection"]` | `["quality_inspections", "weather", "geopolitical_signals"]` | `["risk:*", "weather:*", "compliance:*"]` | Real-time (0.35) > Topological (0.25) > Precedent (0.25) > Factual (0.15) |

Note the re-ranking weight differences: the Risk Agent heavily weights real-time signals (because risk is about emerging threats), while the Finance Agent heavily weights factual state (because financial analysis is about verifiable numbers). The Logistics Agent heavily weights topological context (because routing is a graph problem). These differences are why a centralized RAG layer would produce inferior results -- it cannot hold six different relevance models simultaneously.

### 9.6 Two-Tier RAG: Coordinator Pre-Retrieval + Agent Deep Retrieval

The corrected architecture does not eliminate the Coordinator's role in RAG. Instead, it creates a **two-tier retrieval model**:

```
+=============================================================================+
|                    TWO-TIER RAG RETRIEVAL MODEL                            |
+=============================================================================+
|                                                                             |
|  TIER 1: COORDINATOR PRE-RETRIEVAL (Broad, Shallow)         [Phase 1]     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ When a disruption arrives, the Coordinator performs:                │   |
|  │                                                                     │   |
|  │ 1. BLAST RADIUS SCAN (Neo4j, max_hops=1)                          │   |
|  │    "Which entities are directly affected?"                         │   |
|  │    -> affected_products, affected_facilities, affected_contracts   │   |
|  │                                                                     │   |
|  │ 2. HIGH-LEVEL PRECEDENT SCAN (pgvector, top_k=2, no agent filter) │   |
|  │    "Have we ever seen this type of disruption?"                    │   |
|  │    -> 2 most similar historical disruptions (any agent's history)  │   |
|  │                                                                     │   |
|  │ 3. CURRENT STATE SNAPSHOT (PostgreSQL, summary-level)              │   |
|  │    "What is the current inventory/order/shipment status for        │   |
|  │     affected entities?"                                            │   |
|  │    -> summary metrics (not full records)                           │   |
|  │                                                                     │   |
|  │ PURPOSE: Builds the BASE CONTEXT PACKAGE that all agents receive  │   |
|  │ with their Deliberation Table assignment. Agents do not start      │   |
|  │ from zero -- they start from a shared understanding of what is     │   |
|  │ happening.                                                         │   |
|  │                                                                     │   |
|  │ CHARACTERISTICS:                                                    │   |
|  │   - Broad: covers all domains at surface level                    │   |
|  │   - Shallow: max_hops=1, top_k=2, summary metrics only           │   |
|  │   - Fast: < 50ms total (no LLM, pure DB queries)                  │   |
|  │   - Domain-agnostic: not tailored to any specific agent           │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                              |                                              |
|                              | Base Context Package                         |
|                              v                                              |
|  TIER 2: AGENT DEEP RETRIEVAL (Narrow, Deep)                 [Phase 2]     |
|  ┌──────────────────────────────────────────────────────────────────────┐   |
|  │ Each agent, upon receiving the assignment + base context:          │   |
|  │                                                                     │   |
|  │ 1. DOMAIN-FILTERED PRECEDENT SEARCH (pgvector, top_k=5,           │   |
|  │    agent_id=self, domain_tags=self.config.domain_tags)            │   |
|  │    "What did I specifically recommend in similar situations?       │   |
|  │     How accurate was I?"                                           │   |
|  │                                                                     │   |
|  │ 2. DEEP GRAPH TRAVERSAL (Neo4j, max_hops=2,                      │   |
|  │    node_types=self.config.primary_node_types)                     │   |
|  │    "What are the structural dependencies in my domain?"            │   |
|  │    e.g., Procurement: supplier -> product -> alternate supplier   │   |
|  │    e.g., Logistics: facility -> transport_lane -> carrier -> route│   |
|  │                                                                     │   |
|  │ 3. DETAILED FACTUAL STATE (PostgreSQL via MCP tools)              │   |
|  │    Full record retrieval from domain-specific tables               │   |
|  │    e.g., Procurement: contract terms, MOQ, price tiers            │   |
|  │    e.g., Inventory: exact stock levels, shelf life dates          │   |
|  │                                                                     │   |
|  │ 4. EPHEMERAL SIGNAL CHECK (Redis)                                  │   |
|  │    e.g., Procurement: live supplier capacity, disruption status    │   |
|  │    e.g., Logistics: real-time lane congestion, carrier ETA        │   |
|  │                                                                     │   |
|  │ PURPOSE: Builds DOMAIN-SPECIFIC DEEP CONTEXT for LLM reasoning   │   |
|  │                                                                     │   |
|  │ CHARACTERISTICS:                                                    │   |
|  │   - Narrow: only this agent's domain                              │   |
|  │   - Deep: max_hops=2, top_k=5, full record details               │   |
|  │   - Domain-expert: re-ranked by domain-specific weights           │   |
|  │   - < 100ms total (parallel queries to all 4 sources)            │   |
|  └──────────────────────────────────────────────────────────────────────┘   |
|                                                                             |
+=============================================================================+
```

### 9.7 What Happens to the "AGENTIC RAG PIPELINE" Box in the Diagram

The separate "AGENTIC RAG PIPELINE (Cross-Cutting)" box in the unified diagram is **absorbed into the Agent Reasoning Layer**. It is not deleted -- it is internalized. The corrected diagram placement:

```
+=============================================================================+
|  CORRECTED UNIFIED ARCHITECTURE DIAGRAM (RAG section only)                 |
+=============================================================================+
|                                                                             |
|  +=================================================================+       |
|  |              LANGGRAPH ORCHESTRATION KERNEL (D05)               |       |
|  |              + Coordinator Tier-1 RAG Pre-Retrieval             |       |
|  |                                                                 |       |
|  |  [Ingest] -> [RAG: Blast Radius + Precedent Scan] ->           |       |
|  |  -> [Route] -> [Bind Tools] -> [Fan-Out] ->                    |       |
|  |  -> [Fan-In] -> [Cross-Exam] -> [Consensus] -> [Execute]      |       |
|  +=================================================================+       |
|       |              |              |              |              |        |
|       v              v              v              v              v        |
|  +=================================================================+       |
|  |          LANGCHAIN AGENT REASONING LAYER (D03/D04)             |       |
|  |          + Agent-Internal Tier-2 RAG Deep Retrieval            |       |
|  |                                                                 |       |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  | | Agent 1           | | Agent 2           | | Agent 3           |      |
|  | | +-RAG Retriever-+ | | +-RAG Retriever-+ | | +-RAG Retriever-+ |      |
|  | | | pgvector      | | | | pgvector      | | | | pgvector      | |      |
|  | | | Neo4j         | | | | Neo4j         | | | | Neo4j         | |      |
|  | | | PostgreSQL    | | | | PostgreSQL    | | | | PostgreSQL    | |      |
|  | | | Redis         | | | | Redis         | | | | Redis         | |      |
|  | | +--domain cfg---+ | | +--domain cfg---+ | | +--domain cfg---+ |      |
|  | | +-ML Pipeline---+ | | +-ML Pipeline---+ | | +-ML Pipeline---+ |      |
|  | | +-LLM Reasoner--+ | | +-LLM Reasoner--+ | | +-LLM Reasoner--+ |      |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  |                                                                 |       |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  | | Agent 4           | | Agent 5           | | Agent 6           |      |
|  | | (same structure)  | | (same structure)  | | (same structure)  |      |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  |                                                                 |       |
|  +=================================================================+       |
|       |                                                                     |
|       | Agents read directly from knowledge sources (read-only, L1/L2)     |
|       |                                                                     |
|       v                                                                     |
|  +=================================================================+       |
|  |     CD2F CONSENSUS ENGINE (D06) + TWIN SERVICE (Substrate)     |       |
|  +=================================================================+       |
|       |                                                                     |
|       v                                                                     |
|  +=================================================================+       |
|  |     D01 + D02: ENTERPRISE DATA FABRIC (Frozen + Baseline)      |       |
|  |     PostgreSQL | Neo4j | pgvector | Redis                       |       |
|  +=================================================================+       |
|                                                                             |
|  NOTE: The arrows from Agents to D01+D02 are READ-ONLY connections.       |
|  Agents never write to Layer 1 or Layer 2. They read factual state,        |
|  topological context, semantic precedents, and real-time signals           |
|  directly via their internal RAG retriever instances.                       |
|                                                                             |
+=============================================================================+
```

### 9.8 Why This Does Not Violate the Subsystem Boundary Rules

A legitimate concern: does giving agents direct read access to PostgreSQL, Neo4j, pgvector, and Redis violate the [Subsystem Boundaries](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/06_subsystem_boundaries_and_orchestration_contracts.md)?

No. The boundaries state:

1. **"No Out-of-Band State Mutation"** -- Agents read only. They never write to Layer 1 or Layer 2 databases. All proposals must pass through CD2F.
2. **"Twin does NOT own enterprise data truth"** -- PostgreSQL owns historical and Day-0 books. Neo4j owns baseline topology. Agents reading from these sources is exactly the designed access pattern.
3. **MCP tools already provide this access** -- The existing V1 agents already query PostgreSQL via their `DataAccess` classes (see [demand/data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/src/data_access.py), [supplier/data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/data_access.py)). The RAG retriever formalizes and extends this existing pattern.

The only thing agents cannot do is **write** to these databases or **mutate** state. Reading is their fundamental right as data consumers.

### 9.9 RAG in Cross-Examination (Phase 3 Correction)

Section 2.3 Phase 3 described cross-examination RAG as a separate pipeline action. In the corrected architecture, cross-examination retrieval is performed by the reviewing agent using its own retriever:

```
CROSS-EXAMINATION RAG FLOW:

1. Coordinator posts Procurement's claim to the table and assigns 
   Logistics to cross-examine.

2. Logistics Agent receives the assignment. Inside its internal RAG:
   a. Retrieves from its domain perspective:
      - Neo4j: "Does the route from SUP-0089 origin to our DCs have 
        reefer-capable lanes?" -> Discovers Lane-17 is DRY VAN only
      - PostgreSQL: "What carrier has reefer capacity on alternate routes?"
        -> Finds CR-0012 has reefer but only on Lane-22
      - pgvector: "Have we ever critiqued a similar non-reefer routing 
        proposal?" -> Finds precedent where non-reefer caused $40K spoilage
   
   b. LLM reasons over this retrieved context:
      "Procurement's proposal fails on reefer requirement. Historical 
       precedent shows $40K spoilage loss when reefer was not enforced. 
       BLOCKING critique with evidence."
   
   c. Posts BLOCKING critique verdict to Deliberation Table.
```

Each agent uses its own RAG retriever during cross-examination -- retrieving evidence from its own domain's perspective to validate or challenge peer claims. No centralized RAG layer could provide the domain-specific counter-evidence that makes cross-examination meaningful.

### 9.10 RAG in CD2F Consensus (Phase 4)

The CD2F consensus engine also performs lightweight retrieval, but its retrieval is structurally different from agent-level RAG:

```
CD2F CONSENSUS RAG:

Purpose: Not to generate claims, but to inform SCORING of claims.

1. Retrieve agent reliability factors (R_i):
   - pgvector: "How accurate was each agent in similar historical scenarios?"
   - This is a statistical lookup, not a semantic reasoning task.

2. Retrieve precedent resolution strategies:
   - pgvector: "In past scenarios with similar conflict patterns 
     (e.g., Procurement vs. Logistics disagreement on reefer), 
     which resolution produced better outcomes?"
   - This informs whether CD2F should weight one domain's critique 
     more heavily.

CD2F does NOT use a full SCOFRetriever instance. It uses a lightweight
PrecedentLookup component that queries pgvector directly for 
statistical/historical data. This is a read-only analytical query,
not a cognitive reasoning chain.
```

### 9.11 Updated Implementation Sequencing (RAG-Specific)

**Phase 1 (Foundation, Weeks 1-3) -- corrections:**
- Item 3 changes from "Implement RAG Service Layer in `scof_shared/rag/`" to:
  - Implement `SCOFRetriever` class in `scof_shared/rag/retriever.py` (shared code, domain-configurable)
  - Implement `DomainRetrievalConfig` schema in `scof_shared/rag/config.py`
  - Pre-compute and store 6 agent domain description embeddings in pgvector
  - Define domain-specific retrieval configurations for all 6 agents in `profiles/mvp-electronics/agents/{agent_id}/rag_config.yaml`

**Phase 2 (Agent Transformation, Weeks 4-6) -- corrections:**
- Each agent refactoring task now explicitly includes:
  - Initialize `SCOFRetriever` instance within agent `__init__` with domain-specific `DomainRetrievalConfig`
  - Wire retriever into the LangChain agent chain as the first step before ML inference
  - Implement context fusion layer that combines RAG output + ML output into unified LLM prompt

**Phase 3 (Orchestration Overhaul, Weeks 7-8) -- corrections:**
- Implement Coordinator Tier-1 Pre-Retrieval (broad, shallow RAG during ingestion/routing)
- Wire base context package into Deliberation Table assignment payloads
- Ensure Coordinator's pre-retrieval does NOT use agent-level deep retrieval (separation of concerns)

### 9.12 Relationship to Section TWO

This section does not invalidate Section TWO. It provides a structural correction:

| Section TWO Concept | Section NINE Correction |
| :--- | :--- |
| "RAG wraps around the entire Decision Engine as an active reasoning substrate" | Corrected: RAG is **internal to each agent** and also operates at the Coordinator level. It does not "wrap around" -- it is embedded within. |
| "SCOFRetriever" shared class | Retained: Same class, but now explicitly instantiated per-agent with domain-specific `DomainRetrievalConfig`. |
| Phase 1-5 integration points | Retained: All five phases are still valid. The correction is that Phases 2-3 are executed by agent-internal retrievers, not a separate pipeline layer. |
| "Rather than embedding RAG logic in every service" (Section 2.4) | Corrected: The **code** is shared (one `SCOFRetriever` class). The **instances** are per-agent. The **configuration** is domain-specific. This is the standard pattern: shared library, per-consumer instantiation. |
| Architecture diagram placement | Corrected: "AGENTIC RAG PIPELINE" box is absorbed into the "LANGCHAIN AGENT REASONING LAYER" box. RAG is a component of each agent, not a separate layer. |

