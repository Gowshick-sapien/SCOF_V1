# Scratch script to generate and test the enhanced Section 11, 12, 13
sec_text = """## 11. Agent Cognitive Runtime: Hybrid ML + LLM

Specialist agents are domain observers and bounded cognitive reasoners, combining deterministic analytical machine learning models with bounded LLM qualitative reasoning and evidence synthesis.

### Architectural Core Principle: LLM != Predictive Model

The LLM is the cognitive reasoner, not the numerical calculator. The LLM must NEVER calculate, extrapolate, or invent numerical values (such as demand quantities, safety stock levels, transportation transit times, or financial net present values) that specialized models perform deterministically.

```
+=============================================================================+
|                    HYBRID AGENT COGNITIVE RUNTIME                           |
+=============================================================================+
|                                                                             |
|  [DETERMINISTIC ANALYTICAL PIPELINE]    [BOUNDED COGNITIVE REASONER]        |
|  - Quantitative ML (XGBoost, Prophet)   - Qualitative Evidence Synthesis    |
|  - Foundation Models (Chronos, TimesFM) - Cross-Domain Conflict Detection   |
|  - Deterministic Optimization Solvers   - Precedent Analogy Interpretation  |
|  - Domain Rules & Conservation Laws     - Structured Claim Formulation      |
|                                                                             |
|  OUTPUT: Quantitative Facts             OUTPUT: Epistemic Reasoning         |
|          (ValueWithProvenance,                  (EpistemicType-tagged,      |
|           source=MODEL_PREDICTION)               source=LLM_INTERPRETATION) |
|                                                                             |
|  +--------------+     +----------------+     +--------------+               |
|  | Analytical   |---->| Context Fusion |---->| Bounded LLM  |               |
|  | Capabilities |     | (Facts + RAG)  |     | Reasoner     |               |
|  +--------------+     +----------------+     +--------------+               |
|         ^                     ^                     |                       |
|         |                     |                     v                       |
|  Pre-Computation       Channel 1 & 2        Targeted Tool Invocations       |
|  (Deterministic)       Retrieval Stores     (Bounded: Max 3 Iterations)     |
|                                                     |                       |
|                                                     v                       |
|                                              +--------------+               |
|                                              | AgentProposal|               |
|                                              | (Claim+Action|               |
|                                              +--------------+               |
+=============================================================================+
```

### Bounded Reasoning Constraints

| Constraint | Value | Architectural Rationale |
| :--- | :--- | :--- |
| Max Tool Call Iterations | 3 (hard ceiling) | Prevents tool-call recursion explosion |
| Max Reasoning Steps | 5 | Restricts cognitive path length; prevents unpredictable loops |
| Hard Timeout per Chain | 80% of SLA budget | Preserves 20% SLA budget for schema validation and event dispatch |
| Output Schema Validation | Strict (Pydantic v2) | Instantly rejects non-conforming or malformed output |
| Deterministic Fallback | ML-Only / Rule Engine | If LLM times out or errors, agent falls back to pure analytical proposal |
| Temperature | 0.1 | Minimizes stochastic variance; optimizes for reproducible reasoning |

### Critical Rule: LLMs Do Not Calculate

```
OBSERVED_VALUE     --> comes from PostgreSQL read          (Level 1)
COMPUTED_VALUE     --> comes from deterministic formula    (Level 2)
PREDICTED_VALUE    --> comes from registered ML capability (Level 3)
SIMULATED_VALUE    --> comes from Twin projection          (Level 4)
LLM_INTERPRETATION --> interprets the above values         (Level 6)
```

The LLM interprets, synthesizes, and explains. It does NOT produce authoritative numerical values. If the only source for a critical number is LLM reasoning, the evidence quality assessment reduces the claim's authority and CD2F applies an uncertainty penalty.

### Dynamic Capability Contracts for Analytical Models

Specialist agents do NOT hard-code direct model library invocations (e.g., `import xgboost; xgboost.predict(...)`). Instead, all quantitative models are exposed as registered capability contracts managed by the Dynamic Capability Registry.

```python
class AnalyticalCapabilityContract(BaseModel):
    \"\"\"Contract defining a governed analytical model capability.\"\"\"
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    capability_name: str
    domain: str
    description: str
    input_parameters: dict[str, Any]
    output_schema: str
    timeout_ms: int = 500
    is_deterministic: bool = True
    model_version: str
    underlying_framework: Literal["XGBOOST", "PROPHET", "CHRONOS", "SOLVER", "STATISTICAL"]

class ForecastEnsembleOutput(BaseModel):
    \"\"\"Ensemble forecast output delivered to Context Fusion.\"\"\"
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    sku_id: str
    location_id: str
    horizon_days: int
    point_forecast: float
    p10_forecast: float
    p50_forecast: float
    p90_forecast: float
    component_models: dict[str, float]
    model_agreement: float
    computed_at: datetime
    execution_time_ms: float
```

### Execution Sequencing: Deterministic Pre-Computation vs Targeted Tool Invocations

To ensure high performance and prevent 3B-class local LLMs from failing on routine tool-routing decisions, agent reasoning executes in two disciplined phases:

1. **Deterministic Pre-Computation (Phase 1):** Before prompt construction, the specialist runtime deterministically runs its standard domain analytical pipeline (e.g., Demand Agent executes the forecast ensemble; Inventory Agent executes stockout projections). These results are tagged with provenance and injected directly into Context Fusion.
2. **Targeted Tool Invocation (Phase 2):** During LLM reasoning, the agent may invoke targeted MCP enterprise data tools (e.g., `get_supplier_delivery_history(supplier_id)`) or specialized scenario tools up to a strict maximum of 3 iterations.

### Structured Agent Reasoning Protocol (SARP)

Rather than relying on unconstrained, stochastic Chain-of-Thought prompting, all specialist reasoning adheres to the formal five-stage **Structured Agent Reasoning Protocol (SARP)**:

1. **OBSERVE:** Ingest the active trigger event, assigned task scope, and operational entity IDs.
2. **RETRIEVE:** Pull authoritative current facts (Channel 1) via MCP and relevant historical precedents (Channel 2) via pgvector.
3. **ANALYZE:** Ingest pre-computed analytical ensemble results; compute metric variances and delta against baselines.
4. **VERIFY / CROSS-CHECK:** Screen for contradictions against the Evidence Hierarchy, verify hard physical constraints, and detect cross-domain conflicts.
5. **RECOMMEND:** Synthesize evidence into a strictly validated `AgentProposal` containing a `StructuredClaim` and compliant `CandidateAction` intents.

### Formal Prompt Engineering Layer and Evidence Hierarchy

Every specialist agent receives a strictly structured System Prompt Contract:

```
+-----------------------------------------------------------------------------+
|                     SYSTEM PROMPT CONTRACT ARCHITECTURE                     |
+-----------------------------------------------------------------------------+
| 1. ROLE & IDENTITY: Defined specialist role within enterprise fabric.        |
| 2. MISSION: Objective, target KPIs, and domain boundaries.                  |
| 3. DOMAIN OWNERSHIP: Explicit list of owned actions and excluded domains.   |
| 4. DATA AUTHORITY: Current facts must originate from approved MCP tools.    |
| 5. ANALYTICAL AUTHORITY: Quantitative values from models cannot be altered. |
| 6. MEMORY RULES: Historical precedent is advisory; cannot override facts.   |
| 7. REASONING PROTOCOL: Enforces OBSERVE -> RETRIEVE -> ANALYZE ->           |
|                        VERIFY -> RECOMMEND.                                 |
| 8. OUTPUT CONTRACT: Output must strictly conform to AgentProposal schema.   |
+-----------------------------------------------------------------------------+
```

#### Strict Evidence Hierarchy Inside the Prompt

When evaluating context and resolving conflicting signals, agents must adhere to the immutable Evidence Precedence Hierarchy:

1. **Hard Enterprise Constraints & Physical Limits (Level 1 - Absolute):** Warehouse storage capacities, transport vehicle volume limits, regulatory trade bans. Cannot be violated under any condition.
2. **Authoritative Current Operational Facts (Level 2 - High Authority):** Real-time inventory positions, active purchase orders, confirmed shipments from PostgreSQL and Neo4j via MCP.
3. **Registered Analytical Model Ensemble Outputs (Level 3 - Quantitative Authority):** Forecasts, reliability scores, lead time distributions from verified ML models.
4. **Historical Precedents and Episodic RAG (Level 4 - Advisory Context):** Historical incident post-mortems and past seasonal patterns from pgvector. Advisory only; NEVER overrides current facts.
5. **LLM Qualitative Interpretation (Level 5 - Bounded Heuristic):** Synthesis, justification, and hypothesis formulation. Lowest authority; penalized if unbacked by Level 1-3 evidence.

### Dual-Mode Specialist Operation: Proactive Monitoring vs Reactive Deliberation

Specialist agents operate continuously across two operational modes:

```
                    SPECIALIST AGENT DUAL-MODE LIFECYCLE
                                      |
                +---------------------+---------------------+
                |                                           |
         PROACTIVE PATH                              REACTIVE PATH
      (Domain Monitoring)                        (Deliberation Session)
                |                                           |
        Continuous Telemetry                        Triggered by Coordinator
        & Scheduled Checks                          via A2A Fan-Out
                |                                           |
        Evaluate Metric vs                          Receive Deliberation Item
        TriggerThreshold                            & Snapshot Coordinate
                |                                           |
        Threshold Breached?                         Execute SARP Protocol
        +-------+-------+                           (Observe->Retrieve->Analyze
        | YES           | NO                         ->Verify->Recommend)
        v               v                                   |
   Emit DomainSignal  Continue Monitoring           Emit AgentProposal
   & IssueProposal                                  to Deliberation Table
        |                                                   |
   Post to Coordinator                              Await Deliberation
   for Session Triage                               Readiness Gate
```

#### Operational Taxonomy of Decision Artifacts

- **Domain Signal:** Raw operational observation from telemetry indicating variance (e.g., demand spike of +31%).
- **Issue Proposal:** Evaluated trigger candidate where variance exceeds `TriggerThreshold`, warranting cross-domain deliberation.
- **Deliberation Item:** Validated issue accepted by Coordinator and bound to a DecisionSnapshot within the Deliberation Table.
- **Execution Outcome:** Monitored result after an authorized action is executed by the adapter.
- **Resolution Status:** Operational determination of whether the originating metric has normalized within SLA.

```python
class TriggerThreshold(BaseModel):
    \"\"\"Domain metric monitoring boundary for proactive signal detection.\"\"\"
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    metric_name: str
    domain: str
    warning_threshold: float
    critical_threshold: float
    evaluation_window_minutes: int
    min_consecutive_breaches: int = 2

class DomainSignal(BaseModel):
    \"\"\"Telemetry observation detected by proactive monitoring.\"\"\"
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    signal_id: str
    domain: str
    metric_name: str
    observed_value: float
    baseline_value: float
    variance_pct: float
    severity: Literal["INFO", "WARNING", "CRITICAL"]
    detected_at: datetime

class IssueProposal(BaseModel):
    \"\"\"Proactively raised issue submitted to Coordinator for session triage.\"\"\"
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    issue_id: str
    originating_agent_id: str
    domain: str
    primary_signal: DomainSignal
    impacted_entities: list[str]
    proposed_scope: list[str]
    created_at: datetime
```

---

## 12. LLM Strategy

The architecture freezes the INTERFACE, not the model. Model selection is runtime configuration, with an initial baseline operational in D3/D4 and empirical validation executed in D10.

### Baseline Runtime Model: Local Ollama + Qwen 2.5 3B

For initial development and testing (D3 through D9), specialist agents deploy against a local **Ollama** service container hosting **Qwen 2.5 3B**:
- **Deployment:** Dedicated container `scof-llm` running on the internal private Docker network.
- **Persistence:** Models cached in dedicated Docker volume `ollama_models`.
- **Inference Mode:** Fast, memoryless local inference; zero cross-call state leakage.
- **Decoupled Architecture:** Agent code interacts strictly with the `ReasoningService` protocol, ensuring zero vendor lock-in. Swapping to vLLM, TGI, or cloud inference requires changing environment configuration, not agent logic.

```python
class ReasoningService(Protocol):
    \"\"\"Abstract interface for LLM reasoning. Model selection is runtime config.\"\"\"
    
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

### Model Selection Principle: D3/D4 Baseline vs D10 Empirical Selection

- **D3/D4 Implementation:** Initial LLM (Ollama + Qwen 2.5 3B) and registered analytical capabilities are operational in D3/D4 to establish cognitive agent behavior from day one.
- **D10 Validation:** D10 empirically benchmarks alternative models (e.g., Mistral 7B, Llama 3 8B, Qwen 2.5 7B, proprietary APIs), prompt templates, and quantization profiles (Q4_K_M vs Q8_0 vs FP16) to select the production configuration.

### Model Selection Evaluation Criteria (D10 Formal Benchmark)

| Criterion | Measurement Protocol | Acceptance Threshold |
| :--- | :--- | :--- |
| Structured Output Reliability | % of outputs that parse strictly into Pydantic schema without retry | >= 98.0% |
| Tool-Call Precision | % of tool calls generated with strictly valid, schema-compliant arguments | >= 95.0% |
| Numerical Discipline | Rate of unauthorized numerical calculation or hallucinated metrics | 0.0% (strict zero tolerance) |
| Evidence Grounding | % of claims with verified provenance links to provided context | >= 95.0% |
| Inference Latency | p50, p95, p99 latency per reasoning pass under concurrent session load | p50 < 400ms, p95 < 900ms |
| Reasoning Reproducibility | Output semantic consistency variance across identical prompts at T=0.1 | Jaccard agreement >= 0.90 |

---

## 13. Memory Architecture

LangChain built-in conversation memories (`ConversationBufferMemory`, `ConversationSummaryMemory`) are strictly forbidden. Memory is SCOF-native, divided across two explicit information channels:

### Two-Channel Memory Model

1. **Channel 1: Current Operational State (System of Record)**
   - Authoritative facts from PostgreSQL, Neo4j, and Redis accessed strictly via bounded MCP tools.
   - Current state is NEVER retrieved via vector embedding similarity / RAG.
2. **Channel 2: Historical Precedents & Episodic Memory (Agentic RAG)**
   - Curated historical disruption post-mortems, resolution outcomes, and edge-case precedents stored in PostgreSQL + pgvector.
   - Retrieved via MCP-governed semantic search and tagged as advisory evidence.

| Memory Need | Source | Forbidden Pattern |
| :--- | :--- | :--- |
| Current decision session context | Deliberation Table (PostgreSQL + Redis) | NOT ConversationBufferMemory |
| Historical decision precedents | pgvector semantic embeddings (D9 archival) | NOT ConversationSummaryMemory |
| Workflow checkpoint / resume | LangGraph checkpoint store (PostgreSQL) | NOT In-memory process dictionary |
| Authoritative enterprise facts | PostgreSQL D2 System of Record | NOT Vector similarity search |
| Topology context | Neo4j bounded graph traversals | NOT LLM hallucinated connections |
| Real-time operational telemetry | Redis ephemeral cache | NOT Stale embedding vectors |
| Agent evaluation history | D10 structured evaluation store | NOT Unstructured chat logs |

LangChain is a consumer and runtime orchestrator of these memories, not the owner. In case of any conflict between historical RAG precedent and current operational state, current state strictly prevails under the Evidence Hierarchy.
"""

with open("scratch/test_sec.md", "w", encoding="utf-8") as f:
    f.write(sec_text)
print("Section 11, 12, 13 generated successfully in scratch/test_sec.md!")
