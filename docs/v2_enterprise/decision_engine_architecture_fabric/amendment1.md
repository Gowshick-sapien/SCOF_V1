# SCOF V2 Revised Architecture: D3-D10 Cognitive Decision Fabric

## Document Lineage

- **Predecessor:** [scof_v2_d3_d10_architecture_shift_review.md](file:///C:/Users/Gowshick/.gemini/antigravity-ide/brain/ef0dbb38-699f-44a8-8f41-6efb96240b04/scof_v2_d3_d10_architecture_shift_review.md) (Original Plan, Sections ONE through NINE)
- **Corrections Source:** [review_response_analysis.md](file:///C:/Users/Gowshick/.gemini/antigravity-ide/brain/ef0dbb38-699f-44a8-8f41-6efb96240b04/review_response_analysis.md) (Point-by-point response to external review)
- **Status:** This document is the **architectural baseline** for D3-D10 implementation. It supersedes the original plan on all points where amendments have been applied.
- **What this document does NOT do:** It does not alter anything in the original plan document. That document remains intact as the historical record of the initial architectural design.

> [!IMPORTANT]
> This is NOT a copy of the original plan with patches. It is a clean, ground-up restatement of the complete D3-D10 architecture incorporating all seven amendments validated by the architectural review. Every section is self-contained.

---

## Table of Contents

1. [Conceptual Model: Six Cognitive Stages](#1-conceptual-model-six-cognitive-stages)
2. [Agent Roster: Six Specialists + Coordinator](#2-agent-roster-six-specialists--coordinator)
3. [Mechanism Responsibility Matrix](#3-mechanism-responsibility-matrix)
4. [Evidence Architecture: Provenance, Hierarchy, Epistemic Boundaries](#4-evidence-architecture)
5. [Decision Object Model: Claim vs. Action Separation](#5-decision-object-model)
6. [Agentic RAG: Two-Tier MCP-Governed Retrieval](#6-agentic-rag-two-tier-mcp-governed-retrieval)
7. [Agent Cognitive Runtime: Bounded Reasoning Chain](#7-agent-cognitive-runtime)
8. [Deliberation Table: Core Cognitive Workspace](#8-deliberation-table-core-cognitive-workspace)
9. [Priority & SLA: Two-Dimensional Model](#9-priority--sla-two-dimensional-model)
10. [Fail-Safe Behavior: Evidence Sufficiency Gates](#10-fail-safe-behavior-evidence-sufficiency-gates)
11. [Digital Twin: First-Class Counterfactual Evaluator](#11-digital-twin-first-class-counterfactual-evaluator)
12. [CD2F: Evidence-Based Arbitration Engine](#12-cd2f-evidence-based-arbitration-engine)
13. [State Authority & Consistency: Transactional Outbox](#13-state-authority--consistency)
14. [Kafka: Event Backbone (Not Universal RPC)](#14-kafka-event-backbone)
15. [MCP & A2A Protocol Enhancement](#15-mcp--a2a-protocol-enhancement)
16. [LangChain + LangGraph Architecture](#16-langchain--langgraph-architecture)
17. [LLM Strategy: Interface Abstraction](#17-llm-strategy-interface-abstraction)
18. [Memory Architecture: SCOF-Native Model](#18-memory-architecture-scof-native-model)
19. [Execution Boundary Matrix](#19-execution-boundary-matrix)
20. [Unified Architecture Diagram](#20-unified-architecture-diagram)
21. [Evaluation-Gated Implementation Sequencing](#21-evaluation-gated-implementation-sequencing)

---

## 1. Conceptual Model: Six Cognitive Stages

The D3-D10 architecture is organized around six cognitive stages. This is the mental model that governs every design decision in this document.

```
                   +--------------------------+
                   |       D1 / D2            |
                   | Enterprise Knowledge     |
                   | & Digital World          |
                   +-----------+--------------+
                               |
                        1. KNOW / RETRIEVE
                               |
                               v
                   +--------------------------+
                   |  COGNITIVE DECISION      |
                   |       FABRIC             |
                   |                          |
                   |  Coordinator             |
                   |  Deliberation Table      |
                   |  6 Specialist Agents     |
                   |  Agentic RAG             |
                   |  LangChain / LangGraph   |
                   |  MCP / A2A              |
                   |  Kafka                   |
                   +-----------+--------------+
                               |
                        2. UNDERSTAND
                        3. EXPLORE
                        4. DELIBERATE
                               |
                               v
                   +--------------------------+
                   |     DIGITAL TWIN         |
                   |  Counterfactual Sandbox  |
                   +-----------+--------------+
                               |
                        5. DECIDE
                               |
                               v
                   +--------------------------+
                   |          CD2F            |
                   | Evidence + Constraints   |
                   | + Trade-offs + Outcomes  |
                   +-----------+--------------+
                               |
                        6. EXPLAIN
                               |
                        +------+------+
                        v             v
                      HITL       Scenario State
                                      |
                                 Execution
                                 Boundary
```

| Stage | Component | Core Question |
| :--- | :--- | :--- |
| **KNOW** | D1/D2 + Agentic RAG | What facts, context, and precedents are relevant? |
| **UNDERSTAND** | Specialist Agents (ML + LLM) | What does each domain expert conclude from the evidence? |
| **EXPLORE** | Digital Twin | What happens if we take each proposed action? |
| **DELIBERATE** | Coordinator + Deliberation Table | Where do experts agree and disagree? Can conflicts be resolved? |
| **DECIDE** | CD2F | Which candidate action is best justified by evidence, constraints, and simulated outcomes? |
| **EXPLAIN** | D07 Observability | Complete provenance chain from trigger to outcome. |

---

## 2. Agent Roster: Six Specialists + Coordinator

### 2.1 Final Roster

> [!IMPORTANT]
> **Amendment 1 applied.** Agent boundaries refined per review. Supplier financial health moved from Procurement to Risk. Finance reframed as economic consequence modeling. Risk & Compliance renamed to Risk & Resilience.

```
+=============================================================================+
|                        V2 AGENT ROSTER (6 + 1)                              |
+=============================================================================+
|                                                                             |
|  [COORDINATOR]  Meta-Orchestrator (LangGraph State Machine)                 |
|       |         NOT an agent. Does not produce claims.                      |
|       |         Chairperson of the Deliberation Table.                      |
|       |                                                                     |
|       +-- [1] DEMAND & COMMERCE AGENT                                       |
|       |      Core Question: What demand/commercial effect is occurring?      |
|       |      Domains: Commerce, POS Sales, Promotions, Calendar Events,     |
|       |               Weather, Demand Forecasting, Pricing/Elasticity       |
|       |      Does NOT own: interpretation of all external shocks            |
|       |        (external signals are multi-perspective)                     |
|       |                                                                     |
|       +-- [2] INVENTORY & ASSET MANAGEMENT AGENT                           |
|       |      Core Question: Can the network physically hold, preserve,      |
|       |        and stage the required inventory?                            |
|       |      Domains: Inventory Positions, Replenishment, Assortments,      |
|       |               Physical Assets, Shelf Life, Goods Receipts,          |
|       |               Storage Conditions                                    |
|       |                                                                     |
|       +-- [3] PROCUREMENT & SUPPLIER AGENT                                 |
|       |      Core Question: Can the supply network provide what is needed?  |
|       |      Domains: Supplier Performance, Contracts, Purchase Orders,     |
|       |               MOQ, Price Tiers, Three-Way Match, Vendor             |
|       |               Qualification, Alternate Sourcing                     |
|       |      DOES NOT own: supplier financial distress assessment           |
|       |        (consumes Risk's assessment as input)                        |
|       |                                                                     |
|       +-- [4] LOGISTICS & TRANSPORT AGENT                                   |
|       |      Core Question: Can we move it?                                 |
|       |      Domains: Transport Lanes, Shipments, Carriers, Fleet Assets,   |
|       |               Route Optimization, Freight Modes, Corridor Status   |
|       |      Carbon footprint: computes per-route emissions as DATA,        |
|       |        but CD2F weighs it as a constraint/objective, not Logistics  |
|       |                                                                     |
|       +-- [5] FINANCIAL & ENTERPRISE VALUE AGENT                            |
|       |      Core Question: What is the economic consequence of this        |
|       |        decision?                                                    |
|       |      Purpose: Economic consequence modeling, NOT accounting          |
|       |      Outputs: Landed cost, working capital impact, cash impact,     |
|       |               margin impact, penalty exposure, expedite cost        |
|       |      Accounting/ledger data is evidence it CONSUMES, not its        |
|       |        reason for existing                                          |
|       |                                                                     |
|       +-- [6] RISK & RESILIENCE AGENT                                       |
|              Core Question: What systemic downside, constraint violation,   |
|                or cascading failure could this decision introduce?          |
|              Domains: External threats, Supplier concentration risk,         |
|                       Supplier financial distress, Geopolitical exposure,   |
|                       Quality failure propagation, Regulatory constraints,  |
|                       Network fragility, Cascade modeling, Single points    |
|                       of failure, Recovery time estimation                  |
|              NOT a catch-all for "anything else"                            |
|                                                                             |
+=============================================================================+
```

### 2.2 Ownership Collision Resolution

| Domain | Procurement Owns | Risk Owns |
| :--- | :--- | :--- |
| Supplier Performance | OTIF, lead time, defect rate, capacity | -- |
| Supplier Commercial | Contracts, MOQ, price tiers, payment terms | -- |
| Supplier Financial Health | -- (consumes Risk's output) | Financial distress, credit risk, bankruptcy probability |
| Supplier Concentration | -- | Systemic single-supplier risk |
| Geopolitical Exposure | -- | Per-supplier/per-region geopolitical risk score |
| Quality/Compliance | -- | Inspection results, regulatory violations, recall propagation |

### 2.3 Coordinator Responsibilities

The Coordinator is the meta-orchestrator. It is NOT an agent. It does NOT produce claims, recommendations, or opinions.

| Responsibility | Description |
| :--- | :--- |
| **Deliberation Table Management** | Creates sessions, posts items, manages lifecycle |
| **Domain Affinity Routing** | Computes probabilistic scores, assigns agents |
| **Tier-1 RAG Pre-Retrieval** | Broad, shallow context retrieval for base context package |
| **Capability Resolution** | Invokes Dynamic Capability Registry to bind tools per agent per task |
| **Cross-Examination Mediation** | Routes critiques between agents via the table |
| **Evidence Sufficiency Gating** | Validates that mandatory domains are represented before CD2F |
| **Twin Simulation Dispatch** | Extracts candidate actions, dispatches to Twin for counterfactual evaluation |
| **Consensus Hand-Off** | Assembles decision package and submits to CD2F |
| **Audit Emission** | Emits complete deliberation transcript to D07 |

**What the Coordinator does NOT do:**
- Does NOT produce its own claims or recommendations
- Does NOT score or weight agent proposals (CD2F does that)
- Does NOT modify baseline state (Layer 1 or Layer 2)
- Does NOT directly query databases for analysis (agents do that via RAG/MCP)

---

## 3. Mechanism Responsibility Matrix

> [!IMPORTANT]
> **Amendment from review.** This matrix resolves the A2A / Kafka / LangGraph / Deliberation Table overlap identified by the review.

| Mechanism | Responsibility | Does NOT Do |
| :--- | :--- | :--- |
| **LangGraph** | Workflow execution: state machine, branching, cycles, timeouts, conditional routing | Does not store claims, does not transport events, does not manage agent task contracts |
| **Deliberation Table** | Cognitive workspace/state: items, verdicts, sessions, decision artifacts | Does not execute workflows, does not transport events, does not manage agent lifecycle |
| **A2A** | Agent interoperability/task contract: agent cards, capability declaration, health, task lifecycle | Does not store decision artifacts, does not execute workflows |
| **Kafka** | Durable event transport: notifications, audit trail, replay, distribution | Does not store state authoritatively, does not execute logic |
| **MCP** | Bounded tool/data access: governed retrieval, tool invocation, audit-traced | Does not store state, does not manage workflow |
| **CD2F** | Evidence-based arbitration: constraint validation, trade-off evaluation, escalation | Does not retrieve data, does not execute simulations directly |
| **RAG** | Evidence acquisition: retrieval, re-ranking, context assembly | Does not make decisions, does not store state |
| **Digital Twin** | Counterfactual evaluation: simulation, branching, invariant enforcement | Does not orchestrate agents, does not make decisions |

### 3.1 How They Compose (Example Flow)

```
Disruption arrives via Kafka topic (KAFKA = transport)
    |
Coordinator's LangGraph state machine transitions to "ingest" (LANGGRAPH = workflow)
    |
Coordinator performs Tier-1 RAG pre-retrieval (RAG = evidence acquisition)
    |
Coordinator posts item to Deliberation Table (TABLE = cognitive workspace)
    |
Coordinator computes domain affinity, creates A2A tasks (A2A = task contract)
    |
Agents receive task, invoke MCP tools for deep retrieval (MCP = governed access)
    |
Agents post verdicts to Deliberation Table (TABLE = workspace)
    |
Coordinator dispatches candidate actions to Twin (TWIN = counterfactual)
    |
Twin returns simulated outcomes
    |
Coordinator submits evidence package to CD2F (CD2F = arbitration)
    |
Decision event published to Kafka (KAFKA = transport)
```

---

## 4. Evidence Architecture

> [!IMPORTANT]
> **New section.** Evidence provenance, hierarchy, and epistemic boundaries were identified as critical missing concepts by the review.

### 4.1 Evidence Item Schema

Every piece of evidence in the system carries a full provenance chain:

```python
class EvidenceItem(BaseModel):
    """An atomic unit of evidence used in reasoning."""
    
    evidence_id: str
    source_type: Literal[
        "postgresql",     # Direct fact from System of Record
        "neo4j",          # Topological relationship from graph
        "pgvector",       # Semantic match from embedding store
        "redis",          # Real-time ephemeral signal
        "ml_model",       # Output from ML pipeline
        "twin_simulation",# Output from Digital Twin scenario
        "llm",            # LLM-generated interpretation
    ]
    source_ref: str              # Table name, model name, query hash, etc.
    retrieved_at: datetime       # When this evidence was acquired
    data_as_of: datetime         # When the underlying data was last updated
    query_hash: str              # SHA-256 of the query that produced this evidence
    authority: EvidenceAuthority  # See hierarchy below
    freshness_score: float       # [0.0, 1.0] based on data age relative to decision time
```

### 4.2 Evidence Authority Hierarchy

Not all evidence has equal weight. The hierarchy is strictly enforced:

```
Level 1: AUTHORITATIVE_FACT       -- Direct read from PostgreSQL/Neo4j (SoR)
    Examples: current inventory level, contract MOQ, supplier OTIF score

Level 2: COMPUTED_DERIVATION      -- Deterministic calculation from Level 1 data
    Examples: landed cost computation, safety stock formula output

Level 3: MODEL_PREDICTION         -- ML model output (XGBoost, Prophet, etc.)
    Examples: demand forecast, supplier reliability score, delay probability

Level 4: SIMULATION_OUTCOME       -- Digital Twin projected result
    Examples: simulated fill rate after rerouting, projected inventory at T+7

Level 5: HISTORICAL_PRECEDENT     -- Semantic match from pgvector precedent store
    Examples: "In a similar scenario, we rerouted to SUP-0112 with 94% success"

Level 6: LLM_INTERPRETATION      -- LLM reasoning output (lowest authority)
    Examples: "Based on the evidence, I recommend..."
```

**Critical Rule:** An LLM interpretation (Level 6) must NEVER override an authoritative fact (Level 1). If the LLM says "inventory is sufficient" but PostgreSQL says "inventory = 0 units," the fact wins. Context fusion enforces this by presenting Level 1-5 evidence as immutable inputs to the LLM prompt.

### 4.3 Value With Provenance

All numerical values in agent outputs carry their source:

```python
class ValueWithProvenance(BaseModel):
    """A numerical value with traceable origin."""
    value: float
    source: EvidenceAuthority
    source_ref: str              # Traceable reference
    timestamp: datetime          # When produced
    computation: Optional[str]   # For COMPUTED_DERIVATION: the formula/SQL used
```

### 4.4 Epistemic Boundaries

Every element in an agent's output is tagged with its epistemic type:

```python
class EpistemicType(str, Enum):
    OBSERVATION = "OBSERVATION"       # Verified fact from authoritative source
    PREDICTION = "PREDICTION"         # Model-generated forecast with uncertainty
    CONSTRAINT = "CONSTRAINT"         # Hard limit that cannot be violated
    RISK_ASSESSMENT = "RISK"          # Probabilistic risk evaluation
    RECOMMENDATION = "RECOMMENDATION" # Agent's suggested course of action
    COUNTERFACTUAL = "COUNTERFACTUAL" # "If X happens, then Y follows"
```

---

## 5. Decision Object Model

> [!IMPORTANT]
> **Amendment from review.** Claims are separated from candidate actions. This gives CD2F a cleaner input model.

### 5.1 Agent Output: Structured Proposal

```python
class StructuredClaim(BaseModel):
    """What the agent BELIEVES, with evidence. This is assessment, not action."""
    observations: list[ClaimElement]     # What facts did the agent observe?
    predictions: list[ClaimElement]      # What does the agent forecast?
    risks: list[ClaimElement]            # What risks does the agent identify?
    constraints: list[ClaimElement]      # What hard limits apply?

class ClaimElement(BaseModel):
    claim_type: EpistemicType
    description: str
    value: Optional[ValueWithProvenance]  # Numerical value if applicable
    evidence: list[EvidenceItem]          # Supporting evidence chain
    confidence: float                     # Agent's confidence in this element

class CandidateAction(BaseModel):
    """What the agent PROPOSES to do about its assessment."""
    action_id: str
    action_type: str                     # e.g., "reroute_supplier", "increase_order"
    parameters: dict                     # Action-specific parameters
    expected_impact: ImpactAssessment    # Projected consequences
    supporting_claims: list[str]         # References to ClaimElement IDs above
    evidence: list[EvidenceItem]         # Evidence supporting this action

class ImpactAssessment(BaseModel):
    """Projected consequences of a candidate action. All values have provenance."""
    cost_impact_usd: ValueWithProvenance
    service_level_delta: ValueWithProvenance
    lead_time_delta_days: ValueWithProvenance
    risk_score_delta: ValueWithProvenance
    affected_domains: list[str]          # Which other agents' domains are impacted

class AgentProposal(BaseModel):
    """Complete agent output: assessment + recommendation."""
    proposal_id: str
    agent_id: str
    session_id: str
    
    # Assessment (what the agent believes)
    claim: StructuredClaim
    
    # Recommendations (what the agent proposes)
    candidate_actions: list[CandidateAction]  # May propose multiple options
    recommended_action_id: str                 # Which candidate the agent recommends
    
    # Meta
    overall_confidence: float
    processing_time_ms: float
    evidence_summary: list[EvidenceItem]
```

### 5.2 Decision Session Object

The complete decision lifecycle:

```python
class DecisionSession(BaseModel):
    """The complete record of a single deliberation-to-decision cycle."""
    session_id: str
    trigger: DisruptionEvent
    context_package: ContextPackage        # Coordinator's Tier-1 pre-retrieval output
    
    # Phase 2: Agent proposals
    proposals: list[AgentProposal]
    
    # Phase 3: Cross-examination
    critiques: list[AgentCritique]
    revised_proposals: list[AgentProposal]  # Revised after critique
    
    # Phase 3.5: Candidate extraction
    candidate_actions: list[CandidateAction]  # All candidates from all agents
    
    # Phase 4: Counterfactual evaluation (NEW)
    twin_simulations: list[SimulationResult]  # Twin outcome per candidate
    
    # Phase 5: Arbitration
    evidence_sufficiency: EvidenceSufficiencyAssessment
    arbitration_result: CD2FArbitrationResult
    
    # Phase 6: Execution
    decision: ApprovedDecision
    execution_status: ExecutionStatus
    
    # Observability
    full_transcript: list[DeliberationTableItem]
    total_duration_ms: float
```

---

## 6. Agentic RAG: Two-Tier MCP-Governed Retrieval

> [!IMPORTANT]
> **Amendment 2 applied.** Agents own retrieval STRATEGY but data access goes through MCP-governed capabilities (not direct DB connections). Exception: Redis remains direct for sub-millisecond key-value reads.

### 6.1 Two-Tier Model

```
+=============================================================================+
|                    TWO-TIER RAG RETRIEVAL MODEL                            |
+=============================================================================+
|                                                                             |
|  TIER 1: COORDINATOR PRE-RETRIEVAL (Broad, Shallow)                       |
|  +-----------------------------------------------------------------+       |
|  | Blast radius scan (Neo4j, max_hops=1)                          |       |
|  | High-level precedent scan (pgvector, top_k=2, no agent filter) |       |
|  | Current state snapshot (PostgreSQL, summary metrics only)       |       |
|  | Output: Base Context Package sent with every agent assignment   |       |
|  | SLA: < 50ms total (no LLM, pure DB queries via MCP)            |       |
|  +-----------------------------------------------------------------+       |
|                              |                                              |
|                              v                                              |
|  TIER 2: AGENT DEEP RETRIEVAL (Narrow, Deep, Domain-Specific)             |
|  +-----------------------------------------------------------------+       |
|  | Domain-filtered precedent search (pgvector via MCP, top_k=5)   |       |
|  | Deep graph traversal (Neo4j via MCP, max_hops=2)               |       |
|  | Detailed factual state (PostgreSQL via MCP tools)               |       |
|  | Ephemeral signal check (Redis, DIRECT access)                  |       |
|  | Domain-specific re-ranking weights applied                      |       |
|  | Output: Domain-Specific Deep Context for LLM reasoning          |       |
|  | SLA: < 100ms total (parallel queries)                           |       |
|  +-----------------------------------------------------------------+       |
|                                                                             |
+=============================================================================+
```

### 6.2 MCP-Governed Retrieval Architecture

```
             AGENT
               |
    Domain Retrieval Policy (agent-internal strategy)
    - What to retrieve (domain-specific queries)
    - How to re-rank (domain-specific weights)
    - Which filters to apply (agent_id, domain_tags)
               |
               v
    SCOFRetriever (shared library, domain-configured)
               |
    +----------+-----------+-----------+----------+
    |          |           |           |          |
    v          v           v           v          |
 MCP:       MCP:        MCP:       Direct:       |
 semantic   graph       factual    Redis         |
 retrieval  retrieval   retrieval  key-value     |
    |          |           |           |          |
    v          v           v           v          |
 pgvector   Neo4j      PostgreSQL  Redis         |
```

**Why MCP-governed instead of direct DB access:**
1. Every retrieval is a traceable MCP tool invocation in the audit trail
2. Dynamic Capability Registry controls which retrieval capabilities each agent has
3. Connection pool management is centralized in the MCP server, not distributed across 6 agents
4. Consistent with the subsystem boundary principle: agents access data through governed interfaces

**Why Redis is exempt:**
Redis lookups are sub-millisecond key-value reads. Wrapping them in MCP JSON-RPC adds more overhead than the lookup itself. The agent reads `disruption:SUP-0042:status` directly. This is audited via application-level logging, not MCP.

### 6.3 Domain-Specific Retrieval Configuration

```python
class DomainRetrievalConfig(BaseModel):
    """Per-agent configuration controlling retrieval strategy."""
    
    agent_id: str
    domain_tags: list[str]
    
    # Semantic retrieval
    precedent_top_k: int = 5
    precedent_min_similarity: float = 0.70
    
    # Graph retrieval
    primary_node_types: list[str]
    max_graph_hops: int = 2
    graph_query_templates: list[str]
    
    # Factual retrieval
    primary_tables: list[str]
    
    # Re-ranking weights (domain-specific)
    precedent_weight: float
    topological_weight: float
    factual_weight: float
    realtime_weight: float
```

| Agent | Re-ranking Priority |
| :--- | :--- |
| Demand & Commerce | Factual (0.35) > Precedent (0.30) > Topological (0.20) > Real-time (0.15) |
| Inventory & Asset | Factual (0.35) > Real-time (0.25) > Topological (0.25) > Precedent (0.15) |
| Procurement & Supplier | Topological (0.30) > Factual (0.30) > Precedent (0.25) > Real-time (0.15) |
| Logistics & Transport | Topological (0.35) > Real-time (0.25) > Factual (0.25) > Precedent (0.15) |
| Financial & Enterprise Value | Factual (0.40) > Precedent (0.25) > Topological (0.20) > Real-time (0.15) |
| Risk & Resilience | Real-time (0.35) > Topological (0.25) > Precedent (0.25) > Factual (0.15) |

---

## 7. Agent Cognitive Runtime: Bounded Reasoning Chain

> [!IMPORTANT]
> **Amendment from review.** Agents use bounded reasoning chains, not unrestricted ReAct loops.

### 7.1 Hybrid ML + LLM Architecture

```
+=============================================================================+
|                    HYBRID AGENT COGNITIVE RUNTIME                           |
+=============================================================================+
|                                                                             |
|  [TRADITIONAL ML PIPELINE]           [BOUNDED LLM REASONING]              |
|  - XGBoost / LightGBM                - Qualitative evidence synthesis     |
|  - Prophet / Statistical              - Cross-domain constraint reasoning |
|  - GradientBoosting                   - Historical precedent interpretation|
|  - Deterministic Rule Engines         - Natural language explanation       |
|  - Domain-specific formulas           - Tool-calling (bounded)             |
|                                                                             |
|  OUTPUT: Quantitative values          OUTPUT: Qualitative reasoning        |
|          (ValueWithProvenance,                 (EpistemicType-tagged,      |
|           source=MODEL_PREDICTION)              source=LLM_INTERPRETATION)|
|                                                                             |
|  +-------+     +--------+     +--------+     +------------------+         |
|  |  ML   |---->| CONTEXT|---->|BOUNDED |---->| AgentProposal    |         |
|  | Output|     | FUSION |     |REASONER|     | (Claim + Actions)|         |
|  +-------+     +--------+     +--------+     +------------------+         |
|       ^             ^              |                                       |
|       |             |              | Max iterations: 3                     |
|       |        RAG context         | Max tool calls: 5                     |
|       |        + Base ctx          | Hard timeout: 80% of SLA budget      |
|       |                            | Schema validation on every output    |
|       |                            | Deterministic fallback if LLM fails  |
|  Domain ML models                                                          |
|  (deterministic,                                                           |
|   reproducible)                                                            |
|                                                                             |
+=============================================================================+
```

### 7.2 Bounded Reasoning Constraints

| Constraint | Value | Rationale |
| :--- | :--- | :--- |
| Max tool call iterations | 3 (configurable) | Prevents tool-call explosion |
| Max reasoning steps | 5 | Prevents unpredictable loops |
| Hard timeout per chain | 80% of SLA budget | Leaves 20% for output parsing + posting |
| Schema validation | Every output | Rejects malformed claims immediately |
| Deterministic fallback | ML-only output with reduced confidence | If LLM fails, the agent still produces a valid (if less insightful) output |
| Temperature | 0.1 | Low temperature for deterministic reasoning |

### 7.3 Critical Rule: LLMs Do Not Calculate

```
OBSERVED_VALUE   --> comes from PostgreSQL read      (Level 1)
COMPUTED_VALUE   --> comes from deterministic formula  (Level 2)
PREDICTED_VALUE  --> comes from ML model output        (Level 3)
SIMULATED_VALUE  --> comes from Twin projection        (Level 4)
LLM_INTERPRETATION --> interprets the above values     (Level 6)
```

The LLM interprets, synthesizes, and explains. It does NOT compute `$128,421` or `3.8 days` or `94.3%`. Those come from SQL, formulas, or ML models.

---

## 8. Deliberation Table: Core Cognitive Workspace

The Deliberation Table is the **central working memory of the collective decision process**. It is the strongest architectural idea from the original plan and is promoted to core architecture status.

### 8.1 Core Rules

1. **No agent communicates with another agent directly.** Every interaction passes through the table, mediated by the Coordinator.
2. **The table is a decision-workspace, NOT a source of enterprise truth.** It stores decision artifacts (claims, critiques, verdicts). It does NOT replicate operational state.
3. **The Coordinator is chairperson.** Agents observe the table. They respond ONLY when assigned.

### 8.2 Data Structures

The `DeliberationTableItem`, `DeliberationVerdict`, and `DeliberationSession` schemas from the original plan (Section 8.3, 8.4) remain valid with two corrections:

**Correction 1:** Priority field is now `BusinessPriority` (see Section 9).

**Correction 2:** SLA field is now `ExecutionSLA` (see Section 9).

```python
class DeliberationTableItem(BaseModel):
    item_id: str
    session_id: str
    scenario_id: str
    
    posted_by: str
    posted_at: datetime
    origin_type: Literal[
        "DISRUPTION_TRIGGER", "AGENT_CLAIM", "AGENT_CRITIQUE",
        "AGENT_REVISED_CLAIM", "AGENT_QUERY", "HUMAN_QUERY",
        "HUMAN_DIRECTIVE", "COORDINATOR_DIRECTIVE", "INFORMATION_RESPONSE",
    ]
    
    payload: dict
    payload_schema: str
    
    # Two-dimensional priority (AMENDED)
    business_priority: Literal["P0", "P1", "P2", "P3"]
    execution_sla: Literal["S0", "S1", "S2", "S3"]
    urgency_score: float
    
    status: Literal[
        "POSTED", "SCOPED", "ASSIGNED", "IN_PROGRESS",
        "VERDICT_POSTED", "RESOLVED", "WITHDRAWN", "EXPIRED",
    ]
    
    domain_affinity_scores: dict[str, float]
    assigned_agents: list[str]
    optional_agents: list[str]
    verdicts: list[DeliberationVerdict]
    
    deadline: datetime
```

### 8.3 Domain Affinity Scoring Pipeline (Corrected Order)

> [!IMPORTANT]
> **Amendment from review.** Capability eligibility check comes FIRST, before semantic similarity. Thresholds are configurable, not architectural constants.

```
STEP 1: HARD CAPABILITY ELIGIBILITY       [< 1ms]
    Can the agent answer this at all?
    If agent lacks required MCP tools -> cap score at 0.30 maximum

STEP 2: STATIC DISRUPTION-TYPE MAPPING    [< 5ms]
    Known disruption-to-domain lookup table
    If confidence >= 0.85 -> use directly (Fast-Path)

STEP 3: ENTITY/CONTEXT RELEVANCE          [< 5ms]
    Does the item reference entities in this agent's domain?
    (e.g., mentions "supplier" -> boost Procurement)

STEP 4: SEMANTIC SIMILARITY               [< 50ms, if needed]
    Embed item text, compare against agent domain embeddings
    Only used for free-text queries or novel disruption types

STEP 5: LOAD/AVAILABILITY                 [< 1ms]
    Is the agent healthy? Is its queue full?
    Degraded agents get score penalty

STEP 6: THRESHOLD APPLICATION             [< 1ms]
    Configurable thresholds (D10 calibrates):
    >= assigned_threshold (default 0.60) -> ASSIGNED
    >= optional_threshold (default 0.40) -> OPTIONAL
    < optional_threshold                  -> NOT NOTIFIED
```

Threshold configuration:
```yaml
# profiles/mvp-electronics/routing_config.yaml
routing:
  assigned_threshold: 0.60
  optional_threshold: 0.40
  minimum_assigned_agents: 1
  force_assign_if_none_above_threshold: true
```

---

## 9. Priority & SLA: Two-Dimensional Model

> [!IMPORTANT]
> **Amendment 4 applied.** Business urgency is separated from computational SLA. Timing numbers are benchmark targets, not architectural guarantees.

### 9.1 Business Priority

How urgent is the business decision?

| Priority | Description | Examples |
| :--- | :--- | :--- |
| **P0: Critical** | System emergency, safety, regulatory | Cold-chain breach, critical supplier force majeure |
| **P1: High** | Human-escalated, active disruption | Operator query, CD2F Tier-3 escalation |
| **P2: Normal** | Routine agent deliberation | Standard disruption handling |
| **P3: Background** | Analytics, risk scanning, batch | Periodic supplier risk scan, precedent indexing |

### 9.2 Execution SLA

How fast must the computation complete?

| SLA | Description | Target Latency |
| :--- | :--- | :--- |
| **S0: Real-time** | Deterministic safety rules, no LLM | < 100ms |
| **S1: Interactive** | Human-facing response expected | < 2s |
| **S2: Operational** | Standard deliberation cycle | < 5s per agent |
| **S3: Analytical** | Batch/background processing | < 30s |

### 9.3 Valid Combinations

| Combination | Example |
| :--- | :--- |
| P0 + S0 | Cold-chain breach -> immediate quarantine rule (deterministic, no LLM) |
| P0 + S2 | Critical supplier failure -> full cognitive deliberation (urgent but complex) |
| P1 + S1 | Operator asks "What is the impact of rerouting?" -> quick analytical response |
| P2 + S2 | Routine demand surge -> standard agent deliberation |
| P3 + S3 | Weekly supplier risk scan -> batch analysis |

### 9.4 P0 Dual-Path Architecture

For P0 events, the system provides BOTH immediate safety AND cognitive depth:

```
P0 event arrives
    |
    +---> FAST PATH (S0): Deterministic safety rule
    |     - Pre-defined rule engine (no LLM)
    |     - e.g., cold-chain breach -> quarantine affected inventory
    |     - Executed immediately (< 100ms)
    |     - Applied to Twin Layer 3
    |
    +---> COGNITIVE PATH (S2): Full agent deliberation
          - Standard 6-stage pipeline
          - Produces remediation plan
          - May take 5-15 seconds total
          - Runs in parallel with fast path
```

### 9.5 Timing as Targets, Not Guarantees

> [!WARNING]
> The SLA target values above are **benchmark targets**, not architectural guarantees. D10 benchmarks will calibrate actual achievable latency on the target deployment hardware. The architecture guarantees the MECHANISM (two-dimensional priority, dual-path for P0, bounded agent chains), not specific millisecond numbers.

---

## 10. Fail-Safe Behavior: Evidence Sufficiency Gates

> [!IMPORTANT]
> **Amendment 5 applied.** Universal "fail-open" is replaced with a three-state evidence sufficiency model.

### 10.1 Before CD2F: Evidence Sufficiency Assessment

```
Are all ASSIGNED (mandatory) agents represented?
    |
    +-- YES -> SAFE_TO_PROCEED
    |           Continue to CD2F with full evidence
    |
    +-- NO
         |
         +-- Missing agent was OPTIONAL (affinity < assigned_threshold)?
         |       -> SAFE_TO_PROCEED with penalty
         |          CD2F applies reduced confidence for that domain
         |
         +-- Missing agent was ASSIGNED but produced DETERMINISTIC_FALLBACK?
         |       -> PROCEED_WITH_FALLBACK
         |          Use ML-only output from that agent (no LLM reasoning)
         |          CD2F scores it with reduced weight
         |
         +-- Missing agent was ASSIGNED and produced NO output?
                 -> INSUFFICIENT_EVIDENCE
                    Do NOT proceed to CD2F
                    Escalate to HITL (CD2F Tier-3)
                    Audit: "Decision deferred: critical domain [X] unrepresented"
```

### 10.2 Three States

| State | Condition | Action |
| :--- | :--- | :--- |
| **SAFE_TO_PROCEED** | All mandatory agents responded, or missing agents are optional | Continue to counterfactual evaluation and CD2F |
| **PROCEED_WITH_FALLBACK** | Mandatory agent timed out but its ML pipeline produced a valid deterministic output | Use ML output as claim with reduced confidence; CD2F applies penalty weight |
| **INSUFFICIENT_EVIDENCE** | Critical domain is completely unrepresented (no agent output, no fallback) | Escalate to HITL. Do NOT make automated decision. |

---

## 11. Digital Twin: First-Class Counterfactual Evaluator

> [!IMPORTANT]
> **Amendment 7 applied.** The Twin is elevated from "receives the final decision" to "evaluates candidate actions BEFORE CD2F arbitration."

### 11.1 Position in the Pipeline

```
Original:  Agents -> CD2F -> Twin (apply decision)
Revised:   Agents -> Twin (evaluate candidates) -> CD2F (arbitrate with outcomes)
```

### 11.2 Counterfactual Evaluation Flow

```
PHASE 3.5: CANDIDATE ACTION EXTRACTION & TWIN SIMULATION (NEW)
+-----------------------------------------------------------------------+
| After cross-examination is complete:                                   |
|                                                                        |
| 1. Coordinator extracts ALL candidate actions from all agent proposals |
|    (multiple agents may propose the same type of action with different |
|     parameters; some agents may propose multiple candidates)           |
|                                                                        |
| 2. Coordinator creates Twin simulation requests:                       |
|    - Scenario A: Apply Procurement's recommended action                |
|    - Scenario B: Apply Logistics' recommended action                   |
|    - Scenario C: Apply combined Procurement + Logistics action         |
|    - Scenario D: Apply deterministic fallback (do nothing + buffer)    |
|                                                                        |
| 3. Twin simulates each scenario:                                       |
|    - Advances DES clock by T+7, T+14, T+28 days                       |
|    - Computes projected KPIs: fill rate, inventory turns,              |
|      service level, total cost, lead time                              |
|    - Enforces physical invariants (mass conservation, capacity)        |
|    - Returns SimulationResult per scenario                             |
|                                                                        |
| 4. Coordinator attaches simulation results to the decision package     |
|    submitted to CD2F                                                   |
+-----------------------------------------------------------------------+
```

### 11.3 When Twin Simulation is Triggered

Twin simulation is NOT required for every decision. The Coordinator decides:

| Condition | Twin Simulation? |
| :--- | :--- |
| Multiple competing candidate actions exist | YES -- compare outcomes |
| Single candidate with high confidence and no blocking critiques | NO -- proceed directly to CD2F |
| Financial exposure > configurable threshold | YES -- verify projected cost |
| Candidate involves irreversible action (e.g., air freight commitment) | YES -- verify before committing |
| P3 background analytical task | NO -- not a decision, just an assessment |

### 11.4 Simulation Result Schema

```python
class SimulationResult(BaseModel):
    simulation_id: str
    candidate_action_id: str
    scenario_branch_id: str
    
    # Projected outcomes at T+7, T+14, T+28
    projected_kpis: dict[str, list[KPIProjection]]
    
    # Physical invariant status
    invariant_violations: list[str]  # Empty if all constraints hold
    
    # Comparison metrics
    baseline_delta: dict[str, float]  # KPI change vs. do-nothing baseline
    
    # Confidence in simulation
    simulation_fidelity: float  # Based on data freshness and model coverage
```

---

## 12. CD2F: Evidence-Based Arbitration Engine

> [!IMPORTANT]
> **Amendment 6 applied.** CD2F is redefined from "weighted consensus voting" to "evidence-based arbitration."

### 12.1 What CD2F Asks Now (Revised)

**Old question:** "Which agent has the highest weighted confidence score?"

**New question:** "Which candidate action remains justified after evidence, constraints, conflicts, and simulated consequences are considered?"

### 12.2 CD2F Input Package

```python
class CD2FInputPackage(BaseModel):
    session_id: str
    
    # Candidate actions (extracted from agent proposals)
    candidate_actions: list[CandidateAction]
    
    # Supporting evidence per candidate (with full provenance)
    evidence_per_candidate: dict[str, list[EvidenceItem]]
    
    # Constraint evaluation
    constraint_violations: list[ConstraintViolation]  # Hard limits breached
    
    # Conflict analysis
    conflicts: list[ConflictRecord]  # Where agents disagree
    
    # Twin simulation results (NEW)
    simulation_results: list[SimulationResult]  # Projected outcomes per candidate
    
    # Agent reliability factors
    agent_reliability: dict[str, AgentReliabilityScore]
    
    # Evidence sufficiency assessment
    sufficiency: EvidenceSufficiencyAssessment
```

### 12.3 CD2F Arbitration Process

```
STEP 1: ELIMINATE
    Remove candidates that violate hard constraints
    (e.g., proposed route has no reefer capability for perishable goods)

STEP 2: EVALUATE EVIDENCE QUALITY
    For each remaining candidate:
    - What is the authority level of supporting evidence?
    - How fresh is the evidence?
    - How reliable is the proposing agent historically?
    (R_i computed from STRUCTURED evaluation metrics, not pgvector similarity)

STEP 3: COMPARE SIMULATED OUTCOMES
    For candidates with Twin simulation results:
    - Which produces the best projected KPIs?
    - Which has the fewest invariant violations?
    - Which aligns best with the organization's objective weights?

STEP 4: ANALYZE TRADE-OFFS
    Identify trade-off dimensions:
    - Cost vs. Speed
    - Service Level vs. Risk
    - Short-term vs. Long-term
    Produce explicit trade-off summary

STEP 5: ARBITRATE
    Select the candidate that is best justified by:
    evidence quality + constraint validity + simulated outcomes + trade-off balance

STEP 6: ESCALATION CHECK
    - High confidence + no constraint violations + simulation confirms -> Tier-1 (auto-commit)
    - Moderate confidence or competing candidates close -> Tier-2 (extended deliberation)
    - Low confidence or insufficient evidence or high financial exposure -> Tier-3 (HITL)
```

### 12.4 CD2F Output

```python
class CD2FArbitrationResult(BaseModel):
    decision_id: str
    session_id: str
    
    # Selected action
    selected_action: CandidateAction
    escalation_tier: Literal["TIER_1", "TIER_2", "TIER_3"]
    
    # Justification
    justification: str                    # Why this action over alternatives
    trade_off_summary: str                # What was sacrificed, what was gained
    eliminated_candidates: list[dict]     # Why each rejected candidate was eliminated
    
    # Confidence (based on evidence quality, NOT agent self-assessment)
    arbitration_confidence: float
    confidence_factors: dict[str, float]  # Evidence quality, simulation support, etc.
    
    # Agent reliability update
    agent_scores_used: dict[str, float]   # R_i values used in this arbitration
```

### 12.5 R_i: Agent Reliability Factor (Corrected)

R_i is computed from **structured evaluation metrics**, not pgvector semantic similarity.

```python
class AgentReliabilityScore(BaseModel):
    agent_id: str
    disruption_type: str
    
    # Structured metrics (from D10 evaluation store)
    historical_accuracy: float          # % of past predictions that were correct
    constraint_violation_rate: float    # % of past proposals that violated constraints
    decision_outcome_quality: float     # Post-hoc evaluation of past decisions
    calibration_score: float            # How well stated confidence matches actual outcomes
    
    # Computed composite
    composite_r_i: float               # Weighted combination of above metrics
    sample_size: int                    # How many historical decisions this is based on
```

pgvector helps identify which historical scenarios are comparable. The actual R_i is computed from structured metrics stored in the D10 evaluation store.

---

## 13. State Authority & Consistency

> [!IMPORTANT]
> **Amendment 3 applied.** Transactional outbox pattern adopted for all PostgreSQL-to-Kafka flows.

### 13.1 State Authority Map

```
PostgreSQL
    +-- Enterprise truth (D1/D2 System of Record)
    +-- Deliberation state (sessions, items, verdicts)
    +-- Agent evaluation metrics (R_i data)
    +-- Outbox table (pending Kafka events)

Kafka
    +-- Event backbone (transport, replay, distribution)
    +-- NOT authoritative state

Redis
    +-- Derived cache (populated FROM Kafka consumers)
    +-- Hot deliberation state (mirrors PostgreSQL for active sessions)
    +-- NOT authoritative

Neo4j
    +-- Topology truth (baseline network structure)

pgvector (inside PostgreSQL)
    +-- Semantic memory (embeddings, precedents)
```

### 13.2 Transactional Outbox Pattern

```
                 TRANSACTION
Agent result ----------------------> PostgreSQL
                                         |
                                    [Same transaction]
                                         |
                                    Outbox table INSERT
                                         |
                                         v
                                    Outbox Relay
                                    (polls outbox table)
                                         |
                                         v
                                    Kafka PUBLISH
                                         |
                                         v
                                    Kafka Consumer
                                         |
                                         v
                                    Redis CACHE UPDATE
```

**Guarantee:** PostgreSQL is always consistent. Kafka events are derived. Redis is derived. There is exactly one write path: PostgreSQL first, Kafka second (via outbox), Redis third (via Kafka consumer). No dual writes. No split-brain.

### 13.3 Outbox Table Schema

```sql
CREATE TABLE deliberation_outbox (
    outbox_id       BIGSERIAL PRIMARY KEY,
    aggregate_type  VARCHAR(64) NOT NULL,    -- 'deliberation_item', 'verdict', 'session'
    aggregate_id    VARCHAR(128) NOT NULL,   -- The item/verdict/session ID
    event_type      VARCHAR(128) NOT NULL,   -- 'item.posted', 'verdict.submitted', etc.
    payload         JSONB NOT NULL,          -- The event payload
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMPTZ,             -- NULL until outbox relay publishes to Kafka
    published       BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_outbox_unpublished ON deliberation_outbox (published, created_at)
    WHERE published = FALSE;
```

### 13.4 Deliberation Table Governance Rule

> The Deliberation Table stores decision artifacts (claims, critiques, verdicts, directives). It does NOT store or replicate enterprise operational state. Agents query the Enterprise Data Fabric (D2) for facts via RAG/MCP. They query the Deliberation Table only for decision-session context (e.g., "What did Agent X claim about this scenario?").

---

## 14. Kafka: Event Backbone

Kafka is the **event backbone**, not the universal communication mechanism.

### 14.1 What Goes Through Kafka

```
GOOD (event transport):
    DisruptionOccurred
    ClaimProduced
    CritiqueProduced
    DecisionResolved
    SimulationCompleted
    SessionStarted / SessionClosed
    AgentHealthUpdate
```

### 14.2 What Does NOT Go Through Kafka

```
SYNCHRONOUS / MCP (tool access):
    get_contract_terms()
    get_inventory()
    get_route_capacity()
    get_supplier_scorecard()

A2A (task contracts):
    submit analysis task
    cancel task
    retrieve task result

LANGGRAPH (workflow):
    state transitions
    conditional branching
    timeout management
```

### 14.3 V2 Topic Architecture

The topic architecture from the original plan (Section 6.3) is retained with one correction: all topics receive events via the transactional outbox, not via direct dual writes.

---

## 15. MCP & A2A Protocol Enhancement

The MCP and A2A upgrade plans from the original plan (Sections 5.2, 5.3) are retained in full. Key elements:

- **A2A:** Agent Card V2 with structured capability declarations, task lifecycle protocol (create/poll/cancel/stream), heartbeat-based health monitoring
- **MCP:** JSON-RPC 2.0 implementation, Dynamic Capability Registry with semantic tool matching (3-5 tools bound per agent per deliberation)
- **New role for MCP:** RAG retrieval capabilities are now MCP-governed (see Section 6.2)

---

## 16. LangChain + LangGraph Architecture

The dual-framework split from the original plan (Section 3) is retained:

```
                 LANGGRAPH
             Decision workflow
             (Coordinator level)
                    |
       +------------+------------+
       v            v            v
   Agent A       Agent B      Agent C
       |            |            |
   LangChain    LangChain    LangChain
   (Bounded     (Bounded     (Bounded
    Reasoning)   Reasoning)   Reasoning)
       |            |            |
      LLM          LLM          LLM
```

**LangGraph** = macro workflow orchestration (state machine, cycles, branching)
**LangChain** = agent-level cognitive components (prompts, tools, output parsing)

### 16.1 LangGraph V2 State Machine (Updated)

```
START -> ingest_and_route -> tier1_rag_preretrieval -> capability_bind
    -> parallel_fan_out
    -> fan_in_collate -> cross_examination
    -> [CONDITIONAL: blocking_critiques?]
        -> YES: revision_round -> fan_in_revised
        -> NO: proceed
    -> candidate_extraction
    -> [CONDITIONAL: twin_simulation_needed?]     (NEW)
        -> YES: twin_dispatch -> twin_collect     (NEW)
        -> NO: proceed
    -> evidence_sufficiency_gate                   (NEW)
    -> [CONDITIONAL: sufficient?]
        -> SAFE_TO_PROCEED: cd2f_arbitration
        -> FALLBACK: cd2f_arbitration (with penalty)
        -> INSUFFICIENT: hitl_escalation -> END
    -> [CONDITIONAL: tier?]
        -> TIER_1: execute_and_archive -> END
        -> TIER_2: extended_deliberation -> parallel_fan_out (cycle)
        -> TIER_3: hitl_escalation -> await_human -> execute_and_archive -> END
```

---

## 17. LLM Strategy: Interface Abstraction

> [!IMPORTANT]
> **Amendment from review.** The architecture freezes the INTERFACE, not the model. Model selection is deferred to D10 evaluation.

### 17.1 ReasoningService Abstraction

```python
class ReasoningService(Protocol):
    """Abstract interface for LLM reasoning. Model selection is runtime config."""
    
    async def reason(
        self,
        system_prompt: str,
        context: AssembledContext,
        output_schema: type[BaseModel],
        max_iterations: int = 3,
        temperature: float = 0.1,
    ) -> StructuredOutput:
        ...
    
    async def health_check(self) -> bool:
        ...
```

### 17.2 Model Selection Criteria (D10 Evaluates)

| Criterion | Measurement |
| :--- | :--- |
| Structured-output reliability | % of outputs that parse correctly into schema |
| Tool-call reliability | % of tool calls with valid parameters |
| Numerical reasoning | Error rate on domain-specific calculations |
| Hallucination rate | % of claims not supported by provided evidence |
| Latency | p50, p95, p99 inference time |
| Context length | Maximum effective context window |
| Reproducibility | Variance across identical prompts |

### 17.3 Deployment

Ollama remains the recommended MVP deployment (Docker service, CPU/GPU fallback). But the agent code interacts with `ReasoningService`, not `Ollama` directly. Swapping to vLLM, TGI, or a cloud API requires changing config, not code.

---

## 18. Memory Architecture: SCOF-Native Model

> [!IMPORTANT]
> **Amendment from review.** LangChain conversation memories are removed. Memory is SCOF-native.

| Memory Need | Source | NOT |
| :--- | :--- | :--- |
| Current decision session context | Deliberation Table (PostgreSQL + Redis) | NOT ConversationBufferMemory |
| Historical decision precedents | pgvector semantic embeddings (D07 archival) | NOT ConversationSummaryMemory |
| Workflow checkpoint/resume | LangGraph checkpoint store | -- |
| Enterprise facts | PostgreSQL D2 System of Record | -- |
| Topology context | Neo4j bounded graph traversals | -- |
| Real-time signals | Redis ephemeral cache | -- |
| Agent evaluation history | D10 structured evaluation store | NOT pgvector similarity |

LangChain is a consumer/orchestrator of these memories, not the owner.

---

## 19. Execution Boundary Matrix

```
+=============================================================================+
|                     EXECUTION BOUNDARY MATRIX                              |
+=============================================================================+
|                                                                             |
|  Component           | ERP Write | Twin Write | DB Write | Deliberation   |
|  --------------------|-----------|------------|----------|----------------|
|  Agent               |    NO     |    NO      |   NO     | Post verdicts  |
|  Coordinator         |    NO     |    NO      |   NO*    | Manage items   |
|  CD2F                |    NO     |    NO      |   NO     | Post decision  |
|  Twin                |    NO     | SCENARIO   |   NO     | --             |
|  Execution Adapter   |   YES**   |    NO      |   NO     | --             |
|                                                                             |
|  * Coordinator writes ONLY to deliberation_* tables (decision workspace)   |
|  ** Execution Adapter requires HITL authorization                          |
|                                                                             |
|  THREE KINDS OF "EXECUTION" (never collapse into one concept):             |
|  1. Simulation execution: Twin (ephemeral scenario state)                  |
|  2. Decision execution: CD2F -> approved decision object                   |
|  3. Real-world execution: Execution Adapter -> ERP/TMS/WMS (HITL gated)  |
|                                                                             |
+=============================================================================+
```

---

## 20. Unified Architecture Diagram

```
+=============================================================================+
|                   SCOF V2 COGNITIVE DECISION FABRIC                        |
|              (D3 through D10 -- Revised Architecture)                      |
+=============================================================================+
|                                                                             |
|  +--[D09: DESKTOP CONSOLE]----------------------------------------------+  |
|  | Tauri v2 | WebSocket Feed | HITL Escalation | What-If Lab             |  |
|  +----------------------------------------------------------------------|  |
|       |                    ^                                                |
|       | REST/WS            | Push Events                                   |
|       v                    |                                                |
|  +--[D08: API GATEWAY & EVENT BACKBONE (Kafka)]-------------------------+  |
|  | FastAPI | WebSocket Broadcast | Transactional Outbox -> Kafka Topics  |  |
|  +----------------------------------------------------------------------|  |
|       |                    ^                    ^                           |
|       v                    |                    |                           |
|  +--[D07: OBSERVABILITY]--+  +--[D10: EVALUATION]--+                      |
|  | 8-Stage Trace | pgvector  | | Benchmark Suite     |                     |
|  | Contrastive   | Semantic  | | Evaluation Gates    |                     |
|  | Explanations  | Archival  | | R_i Computation     |                     |
|  +-------------------+------+ +---------------------+                     |
|                       ^                                                     |
|                       |                                                     |
|  +=================================================================+       |
|  |        LANGGRAPH ORCHESTRATION KERNEL (D05/D06)                |       |
|  |        + Coordinator + Tier-1 RAG Pre-Retrieval                |       |
|  |                                                                 |       |
|  |  [Ingest] -> [RAG T1] -> [Route] -> [Bind Tools] ->           |       |
|  |  -> [Fan-Out] -> [Fan-In] -> [Cross-Exam] ->                  |       |
|  |  -> [Extract Candidates] -> [Twin Simulation] ->    (NEW)     |       |
|  |  -> [Evidence Sufficiency Gate] ->               (NEW)        |       |
|  |  -> [CD2F Arbitration] -> [Execute/Escalate]                  |       |
|  +=================================================================+       |
|       |              |              |              |              |        |
|       v              v              v              v              v        |
|  +=================================================================+       |
|  |     LANGCHAIN AGENT REASONING LAYER (D03/D04)                 |       |
|  |     + Agent-Internal Tier-2 RAG (MCP-Governed)                |       |
|  |                                                                 |       |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  | | Demand &          | | Inventory &       | | Procurement &     |      |
|  | | Commerce          | | Asset Mgmt        | | Supplier          |      |
|  | | +-RAG Strategy--+ | | +-RAG Strategy--+ | | +-RAG Strategy--+ |      |
|  | | | MCP: pgvector | | | | MCP: pgvector | | | | MCP: pgvector | |      |
|  | | | MCP: Neo4j    | | | | MCP: Neo4j    | | | | MCP: Neo4j    | |      |
|  | | | MCP: Postgres | | | | MCP: Postgres | | | | MCP: Postgres | |      |
|  | | | Direct: Redis | | | | Direct: Redis | | | | Direct: Redis | |      |
|  | | +-domain cfg----+ | | +-domain cfg----+ | | +-domain cfg----+ |      |
|  | | +-ML Pipeline---+ | | +-ML Pipeline---+ | | +-ML Pipeline---+ |      |
|  | | +-Bounded LLM---+ | | +-Bounded LLM---+ | | +-Bounded LLM---+ |      |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  |                                                                 |       |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  | | Logistics &       | | Financial &       | | Risk &            |      |
|  | | Transport         | | Enterprise Value  | | Resilience        |      |
|  | | (same structure)  | | (same structure)  | | (same structure)  |      |
|  | +-------------------+ +-------------------+ +-------------------+      |
|  |                                                                 |       |
|  +=================================================================+       |
|       |                                                                     |
|       |  MCP-governed reads (audit-traced)                                 |
|       |  + Direct Redis reads (application-logged)                         |
|       |                                                                     |
|  +=================================================================+       |
|  |     DELIBERATION TABLE (Core Cognitive Workspace)              |       |
|  |                                                                 |       |
|  |  PostgreSQL: persistent state (authority)                      |       |
|  |  Redis: hot cache for active sessions                          |       |
|  |  Kafka: event distribution (via outbox)                        |       |
|  +=================================================================+       |
|       |                                                                     |
|       v                                                                     |
|  +=================================================================+       |
|  |     DIGITAL TWIN -- COUNTERFACTUAL EVALUATOR (NEW POSITION)   |       |
|  |                                                                 |       |
|  |  Receives: candidate actions from agent proposals              |       |
|  |  Returns:  projected outcomes per scenario branch              |       |
|  |  Enforces: physical invariants, capacity, mass conservation    |       |
|  |  Position: BEFORE CD2F (not after)                             |       |
|  +=================================================================+       |
|       |                                                                     |
|       v                                                                     |
|  +=================================================================+       |
|  |     CD2F EVIDENCE-BASED ARBITRATION ENGINE                    |       |
|  |                                                                 |       |
|  |  Input:  claims + evidence + constraints + conflicts           |       |
|  |          + simulation results + agent reliability              |       |
|  |  Process: eliminate -> evaluate evidence -> compare outcomes   |       |
|  |           -> analyze trade-offs -> arbitrate -> escalate?      |       |
|  |  Output:  selected action + justification + trade-off summary |       |
|  +=================================================================+       |
|       |                                                                     |
|       v                                                                     |
|  +=================================================================+       |
|  |     D01 + D02: ENTERPRISE DATA FABRIC (Frozen + Baseline)     |       |
|  |                                                                 |       |
|  |  PostgreSQL | Neo4j (3.73M nodes) | pgvector | Redis           |       |
|  |  96 tables | 30 domains | 49,616 SKUs | Immutable Layer 1     |       |
|  +=================================================================+       |
|                                                                             |
|  SURROUNDING INFRASTRUCTURE:                                               |
|  Kafka = event backbone (via outbox)                                       |
|  MCP = bounded tool/data access (audit-traced)                             |
|  A2A = agent task contract + health + capability                           |
|  D07 = complete decision trace from trigger to outcome                     |
|                                                                             |
+=============================================================================+
```

---

## 21. Evaluation-Gated Implementation Sequencing

> [!IMPORTANT]
> **Amendment from review.** Implementation is restructured around vertical slices with evaluation gates, not technology layers.

### Phase 1: Cognitive Agent Runtime (D3)

**Build:**
- ReasoningService abstraction
- Model provider interface (Ollama initial, swappable)
- Structured output parsing with schema validation
- Bounded tool calling (max iterations, timeout)
- Evidence provenance tracking
- Deterministic fallback mechanism
- Transform ONE agent (Procurement & Supplier recommended -- richest domain)

**Evaluation Gate:**
> Can one agent produce valid, structured, evidence-backed proposals with separated claims and candidate actions?

### Phase 2: Specialist Federation (D4)

**Build:**
- Expand to all six agents
- Agent Card V2 with capability declarations
- Domain-specific RAG configurations
- Ownership boundary enforcement (procurement/risk split)
- A2A task lifecycle protocol

**Evaluation Gate:**
> Do specialist boundaries improve task performance over a single generalist agent? Do domain-specific RAG weights improve retrieval precision?

### Phase 3: Evidence Fabric & Retrieval (D5)

**Build:**
- SCOFRetriever with MCP-governed retrieval
- DomainRetrievalConfig per agent
- Coordinator Tier-1 pre-retrieval
- Evidence provenance schema enforcement
- Evidence authority hierarchy in context fusion

**Evaluation Gate:**
> Does RAG improve factual grounding? Does evidence provenance reduce hallucination? Does Tier-1 pre-retrieval reduce agent retrieval latency?

### Phase 4: Cognitive Orchestration & Deliberation (D6)

**Build:**
- LangGraph V2 state machine (cyclical deliberation)
- Deliberation Table (PostgreSQL + Redis + Kafka outbox)
- Domain affinity scoring pipeline (capability-first)
- Cross-examination mediation
- Evidence sufficiency gates
- Two-dimensional priority/SLA system

**Evaluation Gate:**
> Does orchestrated deliberation with cross-examination produce better decisions than independent agents? Does the evidence sufficiency gate prevent bad automated decisions?

### Phase 5: CD2F + Counterfactual Decision (D7)

**Build:**
- Twin simulation dispatch (candidate evaluation)
- CD2F evidence-based arbitration engine
- Constraint validation
- Conflict detection
- Trade-off analysis
- R_i from structured evaluation metrics

**Evaluation Gate:**
> Does Twin simulation + evidence-based arbitration beat the original weighted voting? Do simulated outcomes correlate with actual outcomes?

### Phase 6: Event & Runtime Backbone (D8)

**Build:**
- Transactional outbox implementation
- Kafka V2 topic architecture
- Redis derived cache population
- Consumer groups and idempotency
- API Gateway V2 endpoints

**Evaluation Gate:**
> Does Kafka eventing improve auditability and replay without adding unacceptable latency?

### Phase 7: Observability & Explainability (D9)

**Build:**
- Complete decision trace: trigger -> retrieval -> tool calls -> ML results -> LLM reasoning -> claims -> critiques -> simulations -> CD2F -> decision
- Evidence provenance visualization
- Trade-off explanation rendering
- Decision replay capability

**Evaluation Gate:**
> Is every decision fully traceable from trigger to outcome? Can a human reviewer understand WHY a decision was made?

### Phase 8: Final Evaluation (D10)

**Build:**
- Full benchmark suite across all 4 disruption classes
- 6-agent evaluation (RQ1-RQ4)
- LLM model comparison (on ReasoningService interface)
- Affinity threshold calibration
- R_i accuracy validation
- SLA target validation on actual hardware
- End-to-end decision quality assessment

**Gate:**
> Does the complete system satisfy RQ1-RQ4 benchmarks? Are SLA targets achievable on target hardware?

---

## Summary of Amendments Applied

| Amendment | What Changed | Where in This Document |
| :--- | :--- | :--- |
| **1: Agent Boundaries** | Risk & Compliance -> Risk & Resilience. Financial Operations -> Financial & Enterprise Value. Supplier financial health moved from Procurement to Risk. | Section 2 |
| **2: RAG Governance** | Agent-internal retrieval strategy retained. Data access MCP-governed (except Redis). | Section 6 |
| **3: State Consistency** | Transactional outbox pattern. PostgreSQL = authority. Kafka = transport. Redis = derived. | Section 13 |
| **4: Priority/SLA** | Two-dimensional model. Timing as targets, not guarantees. P0 dual-path. | Section 9 |
| **5: Fail-Safe** | Three-state evidence sufficiency model replaces universal fail-open. | Section 10 |
| **6: CD2F** | Evidence-based arbitration replaces weighted voting. R_i from structured metrics. | Section 12 |
| **7: Digital Twin** | Counterfactual evaluator BEFORE CD2F. Candidate actions simulated, outcomes inform arbitration. | Section 11 |

---

> [!NOTE]
> This document is the architectural baseline for D3-D10 implementation. The original plan document remains unaltered as the historical design record. All implementation work should reference this revised document.
