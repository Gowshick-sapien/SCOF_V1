# Deliverable D03 -- Cognitive Agent Runtime & Vertical Slice

## Overview & Purpose

Deliverable D03 establishes the foundational **Cognitive Agent Runtime** for the Supply Chain Cognitive Orchestration Framework (SCOF) V2 Enterprise platform, serving as **Phase 1** of the frozen decision fabric implementation sequence defined in [`final_decision_engine_draft.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/decision_engine_architecture_fabric/final_decision_engine_draft.md) (specifically Sections 64, 67 through 73).

D03 transforms the legacy, script-based predictors of V1 into an industrial-grade, hybrid cognitive agent runtime that couples deterministic analytical machine learning models with bounded Large Language Model (LLM) qualitative reasoning and evidence synthesis.

The governing architectural principle of D03 is that **D03 implements the cognitive runtime of an individual specialist agent, not the entire cognitive decision fabric**. The agent runtime is designed to be independently executable, auditable, and testable, exposing stable, frozen contracts for the multi-agent federation, evidence fabric, and counterfactual arbitration layers that subsequent deliverables will assemble around it.

Rather than relying on unconstrained chat prompts, monolithic scripts, or ad-hoc wrappers, D03 enforces:
1. **The Core Invariant (`LLM != Predictive Model`):** Machine learning models deterministically compute numbers; LLMs synthesize qualitative context, evaluate cross-domain trade-offs, and formulate structured hypotheses.
2. **The LangChain vs LangGraph Hard Boundary:** LangChain strictly governs intra-agent cognition; LangGraph strictly governs inter-agent macro-orchestration.
3. **A Decoupled Provider Hierarchy:** LLMs are swappable runtime providers behind the `ReasoningService` protocol, with a local Docker-hosted Ollama container running Qwen 2.5 3B as the baseline.
4. **The Canonical Eight-Stage Reasoning Protocol (SARP-8):** Every specialist reasons through an immutable `RECEIVE -> SCOPE -> RETRIEVE -> ANALYZE -> CHECK -> PROPOSE -> VALIDATE -> EMIT` state machine.
5. **The Structured Six-Layer Prompt Stack:** Contexts are deterministically constructed from an immutable Global Constitution, Domain Contract, Task Contract, Evidence Context, Analytical Results, and Output Contract, with strict external security validation.
6. **The Vertical Research Slice:** Validates the single-agent runtime architecture on the Procurement & Supplier Specialist across a bounded research pipeline:
   $$\text{One Agent} \longrightarrow \text{One Action Intent} \longrightarrow \text{Simulation Test Double} \longrightarrow \text{CD2F Test Double} \longrightarrow \text{Statistical Evaluation}$$
   evaluating whether the hybrid cognitive runtime achieves statistically significant joint improvement across co-primary objectives over the static rule-based heuristic baseline ($B_0$).

---

## Canonical Deliverable Boundaries & Integration Matrix

To prevent architectural scope creep and protect implementation velocity, Deliverable D03 maintains strict boundaries with upstream foundations and downstream deliverables. D03 delivers a fully testable single-agent runtime with stable integration contracts; it does not reimplement D04 through D10 to pass its own acceptance tests.

### Deliverable Responsibility & Ownership Matrix

| Deliverable | Canonical Responsibility | What D03 Owns (In Scope) | What D03 Must NOT Absorb (Out of Scope) |
| :--- | :--- | :--- | :--- |
| **D01** | Enterprise World & Simulation Foundation | Consumes relational System of Record (SoR) and 96 enterprise tables | Dataset generation, historical ground-truth creation, core simulation physics |
| **D02** | Enterprise Knowledge & Data Fabric | Consumes PostgreSQL 16 transactional facts, Neo4j topology, and pgvector embeddings | Database clustering, graph projection pipelines, enterprise-wide ETL sync |
| **D03** | Cognitive Agent Runtime & Vertical Slice | Single-agent runtime lifecycle, SARP-8 engine, prompt stack, provider abstraction, local fallback, single Procurement vertical slice | Multi-agent federation, inter-agent consensus, shared retrieval platform, platform-wide event backbone, execution authorization |
| **D04** | Specialist Federation & Agent Cards | Conforms to canonical `DomainOwnershipPolicy` schemas and exposes `AgentProposal` contracts | Full six-specialist rollout, federation lifecycle management, cross-specialist discovery, enterprise agent cards |
| **D05** | Agentic Retrieval & Evidence Fabric | Consumes typed client contracts and local routing adapters for Path A and Path B | Shared retrieval microservice, global RAG query planning, multi-source ingestion engines |
| **D06** | Cognitive Orchestration & Deliberation | Exposes `reason(task)` interface for Coordinator dispatch | LangGraph macro-orchestrator, Deliberation Table, multi-agent fan-out/fan-in, cross-examination rounds, session readiness gates |
| **D07** | CD2F Arbitration & Counterfactual Decision | Emits sealed `ActionIntent` envelopes within `AgentProposal` | Production Candidate Normalization, production Digital Twin execution, CD2F arbitration, execution policy authorization |
| **D08** | Event & Runtime Backbone | Emits local audit events via standard logging/event interfaces | Kafka cluster infrastructure, transactional outbox pattern, platform-wide event bus, API gateway |
| **D09** | Observability, Explainability & Desktop Console | Emits structured trace spans, correlation IDs, and diagnostic logs | Platform-wide trace aggregation, OpenTelemetry collector, desktop operator console, human-in-the-loop UI |
| **D10** | Evaluation & Benchmark Suite | Executes single vertical slice $B_0$ benchmark test harness | Full B0-B7 ablation ladder, multi-scenario enterprise benchmark, empirical model selection, cross-dataset statistical conclusions |

### Canonical Contract Ownership

All foundational schemas governing agent interaction—including `TaskContract`, `AgentProposal`, `ActionIntent`, `StructuredClaim`, `DomainOwnershipPolicy`, `ActionRegistry`, `ValueWithProvenance`, and `SnapshotCoordinate`—are canonically defined and versioned in the shared architecture contract repository. Deliverable D03 strictly imports and conforms to these canonical contracts. D03 implements local validation engines, policy bindings, and test harnesses, but does not fork or maintain competing schema definitions.

### Downstream Component Classification in D03 Vertical Research Slice

In the vertical research slice, components outside D03's core ownership are explicitly classified into three operational categories:
1. **Existing Upstream Dependencies:** Real PostgreSQL tables, Neo4j projections, and SQLite datasets from D01 and D02.
2. **Minimal Test Doubles & Adapters:** Lightweight test harnesses (`minimal_twin_adapter`, `minimal_cd2f_evaluator`, `b0_baseline_heuristic`) built exclusively to exercise the end-to-end slice loop without pulling production D07 machinery into D03.
3. **Integration-Only Contracts:** Strongly typed Pydantic contracts (`TaskContract`, `AgentProposal`, `ActionIntent`, `StructuredClaim`) that D03 seals and emits to downstream orchestrators without participating in downstream state transitions.

---

## Scope Completeness Matrix

The following matrix audits the nineteen core functional areas of Deliverable D03 to ensure full architectural clarity:

| Scope Area | Specification Status | Architectural Invariant & D03 Implementation Contract |
| :--- | :--- | :--- |
| **Cognitive Runtime & SARP-8** | Specification Frozen | Canonical 8-stage state machine (`RECEIVE -> SCOPE -> RETRIEVE -> ANALYZE -> CHECK -> PROPOSE -> VALIDATE -> EMIT`) with fail-closed transitions. |
| **ReasoningService & Provider** | Specification Frozen | Decoupled `LLMProvider` abstraction, supporting local Docker Ollama baseline (Qwen 2.5 3B), with timeout, cancellation, and error mapping. |
| **AgentProposal Output Model** | Specification Frozen | 4-tier validation (syntactic, semantic, authorization, evidence) ensuring 100% containment of invalid proposals. Output is an `ActionIntent`, not an admitted candidate. |
| **Provenance-Aware Numerical Authority** | Specification Frozen | Structural numerical provenance: all numbers encapsulate `ValueWithProvenance` with multi-dimensional validation (authenticity, entity, unit, temporal scope, safe AST derivation grammar). Zero ungrounded numbers. |
| **Dual-Path Information Architecture** | Specification Frozen | Mechanically routed: Path A (operational facts) strictly supersedes Path B (advisory precedents). RAG never acts as transactional truth. |
| **Analytical Model Integration** | Specification Frozen | Exposes required ML models (XGBoost lead-time, supplier disruption risk) through typed `AnalyticalCapabilityContract` interfaces. |
| **MCP Tool Access & Bounding** | Specification Frozen | Bounded execution: max 3 dynamic tool calls per task during reasoning; analytics pre-computed in Stage 4; strict allowlists, read-only tools, and timeout precedence (`min` of task budget, call limit, and cumulative tool budget). |
| **Domain Ownership & ActionRegistry** | Specification Frozen | Local fail-closed enforcement of canonical `DomainOwnershipPolicy`: unknown action types and out-of-scope entities trigger rejection. |
| **Prompt Engineering Stack** | Specification Frozen | Deterministic 6-layer prompt stack with strict precedence, context budgeting (<1,000 tokens), and external security validation. |
| **Deterministic Fallback Engine** | Specification Frozen | Automated fail-safe emitting degraded proposals (`DEGRADED_PROPOSED`) or safe abstentions (`ABSTAINED`) within 50 ms of activation. |
| **CPU Deployment & Sizing** | Specification Frozen | Sized for pinned 8-core CPU reference host (~2.68 GB host RAM planning estimate; empirical peak container RSS <= 3.5 GB); `OLLAMA_NUM_PARALLEL=1` for single-agent D03 slice; realistic TTFT profile. |
| **Agent-Local Observability** | Specification Frozen | Emits structured JSON audit events capturing stage timings, tool invocations, token counts, fault codes, model digest, prompt hash, and correlation IDs. |
| **Snapshot & Temporal Consistency** | Specification Frozen | Binds all evidence and outputs to `SnapshotCoordinate`; separates logical epoch from ISO-8601 wall-clock timestamp; validates Neo4j transaction compatibility against PostgreSQL snapshot; rejects post-snapshot data. |
| **Epistemic Memory Architecture** | Specification Frozen | Consumes advisory episodic memory via pgvector; strictly forbidden from overriding current System of Record facts. |
| **Testing & Formal Verification** | Specification Frozen | Comprehensive testing suite: unit, property-based, fault-injection, versioned adversarial prompt injection corpus containment, and paired-seed statistical benchmark. |
| **Security & Trust Boundaries** | Specification Frozen | Zero embedded secrets, parameterized queries, bounded outputs, sealed proposals (`intent_hash`), and complete isolation of reasoning from physical actuation. |
| **Packaging & Lifecycle** | Specification Frozen | Pinned container image (`ollama/ollama:0.4.1`), configuration validation on boot, capability-aware readiness (`FULL_READY`, `DEGRADED_READY`, `NOT_READY`), graceful shutdown, and smoke test. |
| **Vertical Research Slice** | Specification Frozen | End-to-end slice for Procurement Agent responding to supplier insolvency, evaluating $B_0$ outperformance across paired seeds ($N >= 30$) under prespecified Wilcoxon signed-rank protocol. |
| **Acceptance Evidence** | Specification Frozen | Traceable test evidence and empirical benchmark logs published across three distinct acceptance layers (Runtime Correctness, Operational Readiness, Research Release). |

---

## Architectural Topology & Component Structure

### Hybrid Specialist Cognitive Runtime

```
+=============================================================================+
|                    HYBRID AGENT COGNITIVE RUNTIME                           |
+=============================================================================+
|                                                                             |
|  [DETERMINISTIC ANALYTICAL PIPELINE]    [BOUNDED COGNITIVE REASONER]        |
|  - Quantitative ML (XGBoost)            - Qualitative Evidence Synthesis    |
|  - Pre-computed in Stage 4 (ANALYZE)    - Cross-Domain Conflict Detection   |
|  - Safe AST Mathematical Derivations    - Precedent Analogy Interpretation  |
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
|  Pre-Computation       Channel 1 & 2        Dynamic Tool Invocations        |
|  (Stage 4 ANALYZE)     Retrieval Stores     (Bounded: Max 3 Calls)          |
|                                                     |                       |
|                                                     v                       |
|                                              +--------------+               |
|                                              | AgentProposal|               |
|                                              | (Claim+Action|               |
|                                              +--------------+               |
+=============================================================================+
```

### Architectural Boundary: LangChain vs LangGraph

```
+=============================================================================+
|             ARCHITECTURAL BOUNDARY: COGNITION VS ORCHESTRATION              |
+=============================================================================+
|                                                                             |
|  INTRA-AGENT COGNITIVE RUNTIME (LangChain)                                  |
|  Location: Contained strictly INSIDE each specialist agent process          |
|  +-----------------------------------------------------------------------+  |
|  | - Six-Layer Prompt Stack assembly and template hydration              |  |
|  | - Bounded tool definitions and controlled invocation (max 3 calls)    |  |
|  | - Semantic memory retriever integration (pgvector historical search)  |  |
|  | - ReasoningService abstraction and provider invocation (Qwen 2.5 3B)  |  |
|  | - Pydantic v2 structured output enforcement and schema validation     |  |
|  | - Conversion of MCP tool execution results into LLM context tokens    |  |
|  +-----------------------------------------------------------------------+  |
|                                                                             |
|  -------------------------------- HARD BOUNDARY --------------------------  |
|                                                                             |
|  INTER-AGENT MACRO ORCHESTRATION (LangGraph)                                |
|  Location: Positioned strictly ABOVE the specialist agents in Coordinator   |
|  +------------------------------------------------------------------------+ |
|  | - Domain blast-radius evaluation and specialist task delegation        | |
|  | - Parallel fan-out dispatch (zero cross-agent communication leakage)   | |
|  | - Deliberation Table fan-in assembly and conflict detection            | |
|  | - Cross-examination iteration control (strictly bounded to <= 2 rounds)| |
|  | - Deliberation readiness gating before candidate evaluation            | |
|  | - Macro state transitions and common snapshot epoch tracking           | |
|  | - SLA budget tracking, timeout enforcement, and cancellation handling  | |
|  | - Downstream pipeline handoff (Candidate Normalizer, Twin, CD2F)       | |
|  +------------------------------------------------------------------------+ |
+=============================================================================+
```

### Decoupled Model Provider Topology & Provider Contract

```
ReasoningService (Abstract Protocol Interface)
      │
      ├── OllamaProvider (Local Docker Baseline: Qwen 2.5 3B)
      │      └── Qwen 2.5 3B (q4_k_m, pinned container image & digest)
      │
      ├── VLLMProvider (High-Throughput Self-Hosted Production Candidate)
      │      └── Open-Weights Models (Mistral 7B, Llama 3 8B, Qwen 2.5 7B)
      │
      └── CloudProvider (Enterprise Redundant Fallback Candidate)
             └── Governed Enterprise Endpoints (Anthropic Claude, Google Gemini)
```

#### Minimum LLMProvider Interface Contract
Every provider implementation must conform to the abstract `LLMProvider` protocol:
1. **Structured Output Enforcement:** Guaranteed emission of JSON conforming strictly to a supplied Pydantic schema (via guided decoding or grammar-constrained sampling).
2. **Cancellation Propagation:** Asynchronous request cancellation cleanly propagating `asyncio.CancelledError` and terminating remote inference.
3. **Deadline Management:** Explicit execution timeout parameter (`timeout_seconds`) bounding total HTTP and generation duration.
4. **Error Mapping:** Normalized mapping of transport, HTTP, connection, and timeout errors into typed exception codes (`PROVIDER_TIMEOUT`, `PROVIDER_UNAVAILABLE`, `SCHEMA_CONFORMANCE_ERROR`).
5. **Token Accounting:** Return of verified token counts (`prompt_tokens`, `completion_tokens`, `total_tokens`) with each completion.
6. **Model Governance Metadata:** Exposure of immutable provider metadata (`model_id`, `model_digest`, `provider_type`).
7. **Health Probe:** Responsive `ping()` / readiness probe returning latency and connectivity status.

For Deliverable D03, `OllamaProvider` is the sole required provider implementation. Alternative providers are defined as prospective adapters for later deliverables.

### Containerized Inference Infrastructure & Hardware Execution Profile (CPU vs GPU)

In full accordance with [`final_decision_engine_draft.md` Section 72](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/decision_engine_architecture_fabric/final_decision_engine_draft.md#72-containerized-inference-concurrency-architecture-and-cpu-hardware-deployment-profile), Deliverable D03 operates against a centralized Ollama container instance (`scof-ollama`) deployed on the private Docker bridge network (`scof-network`):

#### 1. Hardware Sizing & Memory Footprint (RAM Analysis)
- **Model Quantization Baseline:** Qwen 2.5 3B quantized at 4-bit medium precision (`q4_k_m`), parameter count $3.09 \times 10^9$.
- **Model Weights in System RAM:** $\approx 1.93\text{ GB RAM}$ (loaded once and shared read-only across context slots).
- **Grouped-Query Attention (GQA) Key-Value Cache Allocation:**
  $$\text{Memory}_{\text{slot}}(S) = 2 \times 36\text{ layers} \times 2\text{ KV heads} \times 128\text{ head dim} \times S \times 2\text{ bytes} = 36,864 \times S\text{ bytes}$$
  - At $S = 2,048$ tokens: $\approx 75.5\text{ MB RAM}$ per slot.
  - At $S = 4,096$ tokens: $\approx 151.0\text{ MB RAM}$ per slot.
- **Workload Host RAM Planning Estimate:**
  $$\text{Total Host RAM} = 1.93\text{ GB (Weights)} + 0.15\text{ GB (KV Cache)} + 0.60\text{ GB (Runtime/OS)} \approx \mathbf{2.68\text{ GB RAM}}$$
- **Empirical Acceptance Envelope:** The $2.68\text{ GB}$ figure is an analytical workload planning estimate. For formal acceptance on the reference host, the container memory footprint is bounded by an empirical acceptance envelope: **peak container RSS $\le 3.5\text{ GB}$** during active single-stream inference under the standard evaluation workload.

#### 2. D03 Concurrency & CPU Latency Profile
Because Deliverable D03 activates exclusively **one** cognitive specialist (Procurement & Supplier Agent) in an isolated vertical slice:
- Effective runtime concurrency equals **1**.
- The Ollama deployment is configured with `OLLAMA_NUM_PARALLEL=1` and `OLLAMA_NUM_THREADS=8` to focus all CPU execution threads on single-stream prompt processing and token generation, completely eliminating inter-agent scheduling contention and redundant KV cache memory allocation.
- Single-stream generation throughput reaches $\sim 25\text{--}38\text{ tokens/s}$ on modern CPUs supporting AVX2/AVX-512.
- **Warm Time to First Token (TTFT):** $\approx 1.2\text{--}1.8\text{ seconds}$ on reference 8-core CPU ($< 150\text{ ms}$ on reference GPU).
- **Proposal Generation (350 tokens):** $\approx 9.0\text{--}14.0\text{ seconds}$ on reference 8-core CPU ($< 400\text{ ms}$ on reference GPU).
- **End-to-End Reasoning Cycle:** $\approx 11.0\text{--}15.0\text{ seconds}$, fully satisfying P3 operational planning thresholds and enabling local developer validation without requiring dedicated GPU hardware.

#### 3. Canonical Docker Compose Inference Service Specification
```yaml
version: "3.8"
services:
  scof-ollama:
    image: ollama/ollama:0.4.1
    container_name: scof-ollama
    restart: unless-stopped
    networks:
      - scof-network
    ports:
      - "11434:11434"
    volumes:
      - scof-ollama-models:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=1
      - OLLAMA_NUM_THREADS=8
      - OLLAMA_MAX_QUEUE=512
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_FLASH_ATTENTION=1
    deploy:
      resources:
        limits:
          cpus: "8.0"
          memory: 6144M
        reservations:
          cpus: "4.0"
          memory: 4096M

networks:
  scof-network:
    name: scof-network
    driver: bridge

volumes:
  scof-ollama-models:
    name: scof-ollama-models
```

---

## Core Protocols & Behavioral Contracts

### 1. Canonical Eight-Stage Agent Reasoning Protocol (SARP-8)

Every specialist agent in D03 executes through the standardized eight-stage reasoning lifecycle frozen in [`final_decision_engine_draft.md` Section 71](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/decision_engine_architecture_fabric/final_decision_engine_draft.md#71-canonical-eight-stage-agent-reasoning-protocol-sarp-8-contract):

$$\text{RECEIVE} \longrightarrow \text{SCOPE} \longrightarrow \text{RETRIEVE} \longrightarrow \text{ANALYZE} \longrightarrow \text{CHECK} \longrightarrow \text{PROPOSE} \longrightarrow \text{VALIDATE} \longrightarrow \text{EMIT}$$

```
+=============================================================================+
|             CANONICAL EIGHT-STAGE REASONING PROTOCOL (SARP-8)               |
+=============================================================================+
|                                                                             |
|   1. RECEIVE   --> Ingest TaskContract, Snapshot Coordinate, Idempotency    |
|         │                                                                   |
|         v                                                                   |
|   2. SCOPE     --> Determine Domain Ownership, Permitted Claims & Actions   |
|         │                                                                   |
|         v                                                                   |
|   3. RETRIEVE  --> Pull Path A Facts (MCP) and Path B Precedents (pgvector)|
|         │                                                                   |
|         v                                                                   |
|   4. ANALYZE   --> Run Pre-Computed ML Models (Deterministic Analytics)     |
|         │                                                                   |
|         v                                                                   |
|   5. CHECK     --> Validate Sufficiency, Freshness, & Resolve Contradictions|
|         │                                                                   |
|         v                                                                   |
|   6. PROPOSE   --> Synthesize Action Intents & Dynamic Tool Invocations     |
|         │                                                                   |
|         v                                                                   |
|   7. VALIDATE  --> Verify ActionRegistry & Structural Numerical Lineage     |
|         │                                                                   |
|         v                                                                   |
|   8. EMIT      --> Deliver Sealed Proposal (intent_hash) & Telemetry        |
|                                                                             |
+=============================================================================+
```

#### Detailed Stage Execution Contracts

| Stage | Input Schema | Permitted Operations | Output Schema | Preconditions & Postconditions | Failure Codes | Trace Events |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. RECEIVE** | `TaskContract` | Validate task metadata, check snapshot coordinate, enforce idempotency index | `ValidatedTaskContext` | **Pre:** Active task dispatch.<br>**Post:** Correlation ID bound, SLA timer started, idempotency verified. | `INVALID_TASK_CONTRACT`, `SNAPSHOT_VERSION_INCOMPATIBLE` | `task_received`, `sla_timer_started` |
| **2. SCOPE** | `ValidatedTaskContext`, `DomainOwnershipPolicy` | Filter target entity IDs against domain ownership, resolve permitted claim/action types | `ScopedAgentContext` | **Pre:** Validated task context.<br>**Post:** Explicit entity & action boundaries locked. | `UNAUTHORIZED_ENTITY_SCOPE`, `EMPTY_OWNERSHIP_SCOPE` | `domain_scoped`, `authority_locked` |
| **3. RETRIEVE** | `ScopedAgentContext` | Pull Path A operational facts and Path B precedents via governed client adapters | `RetrievedEvidenceBundle` | **Pre:** Scoped entity boundaries.<br>**Post:** Evidence items assigned provenance IDs and validated against event horizon. | `PATH_A_RETRIEVAL_FAILED`, `RETRIEVAL_TIMEOUT` | `path_a_retrieved`, `path_b_retrieved` |
| **4. ANALYZE** | `RetrievedEvidenceBundle`, registered models | Execute registered analytical ML models (XGBoost lead-time); generate projections | `AnalyticalResultsBundle` | **Pre:** Level 1-2 evidence available.<br>**Post:** Quantitative metrics carrying provenance generated. | `ANALYTICAL_MODEL_FAILED`, `OOD_PREDICTION_ERROR` | `ml_model_executed`, `projections_generated` |
| **5. CHECK** | `RetrievedEvidenceBundle`, `AnalyticalResultsBundle` | Enforce evidence hierarchy (Path A > Path B), detect stale data, evaluate operational conflicts | `VerifiedContextBundle` | **Pre:** Analytics and evidence complete.<br>**Post:** Zero unresolved Level 1-2 operational contradictions. | `CRITICAL_EVIDENCE_MISSING`, `CONTRADICTION_UNRESOLVED`| `evidence_checked`, `freshness_verified` |
| **6. PROPOSE** | `VerifiedContextBundle`, Prompt Stack | Hydrate 6-Layer Prompt Stack; invoke `ReasoningService`; execute bounded tool calls (<= 3) | `RawAgentProposal` | **Pre:** Verified context bundle sealed.<br>**Post:** Pydantic JSON proposal parsed. | `PROVIDER_TIMEOUT`, `JSON_PARSE_ERROR`, `TOOL_BUDGET_EXCEEDED` | `prompt_assembled`, `llm_invoked`, `raw_proposal_received` |
| **7. VALIDATE** | `RawAgentProposal`, canonical `ActionRegistry` | Perform 4-tier validation: syntax, semantic, authorization, and multi-dimensional numerical provenance | `ValidatedAgentProposal` | **Pre:** Parsed raw proposal.<br>**Post:** 100% containment of unauthorized actions and ungrounded parameters. | `SCHEMA_VALIDATION_FAILED`, `UNAUTHORIZED_ACTION_TYPE`, `PROVENANCE_VALIDATION_FAILED` | `proposal_validated`, `provenance_verified` |
| **8. EMIT** | `ValidatedAgentProposal` | Seal output proposal (SHA-256 `intent_hash`); update idempotency cache; dispatch to caller | `AgentProposal` | **Pre:** Validated proposal.<br>**Post:** Final immutable sealed proposal emitted. | `EMISSION_FAILED` | `proposal_emitted`, `cycle_completed` |

#### Operational Contradiction Resolution (Stage 5 CHECK)
The requirement for "zero unresolved operational contradictions" is bounded by explicit severity classes:
1. **Blocking Contradictions (Fail-Closed Abstention):** Direct factual contradictions among Level 1-2 authoritative operational data sources (e.g., conflicting inventory counts between transactional tables, or mutually exclusive facility statuses) represent state corruption. The runtime flags `CONTRADICTION_UNRESOLVED` and immediately halts execution with status `ABSTAINED`.
2. **Advisory Differences (Automatic Hierarchy Resolution):** Disagreements between Level 2 current operational facts and Level 4 historical episodic precedents do not block execution. The evidence hierarchy mechanically resolves the conflict: Level 2 operational facts deterministically supersede Level 4 precedents.
3. **Noncritical Uncertainty Representation:** Analytical model variances or noncritical parameter ranges are represented via `confidence_score` and `uncertainty_factors` within `StructuredClaim` and do not force safe abstention.

#### Fail-Closed State Machine Invariants
1. **Monotonic Progression:** Stages must execute in exact serial order. Stage skipping, reverse transitions, and unbounded loops are strictly blocked in code.
2. **Terminal Exception Handling:** Any unhandled exception or unresolvable invariant violation immediately triggers a terminal state transition to `FAILED` or `ABSTAINED` with machine-readable diagnostic error codes.
3. **No Phantom Proposals:** A failed run must never emit a partial, unchecked, or unvalidated `AgentProposal`.

---

### 2. Six-Layer Architectural Prompt Stack & External Security Enforcement

Monolithic prompts are replaced with an immutable six-layer stack assembled deterministically by the runtime, enforcing strict token budgeting (<1,000 tokens for assembled task context on CPU):

```
+=============================================================================+
|                      STRUCTURED 6-LAYER PROMPT STACK                        |
+=============================================================================+
|  Layer 1: GLOBAL CONSTITUTION (Immutable System Governance)                 |
|  - Enterprise rules, zero hallucination mandate, authoritative evidence     |
|    hierarchy, strict tool boundaries, uncertainty representation rules.     |
+-----------------------------------------------------------------------------+
|  Layer 2: DOMAIN CONTRACT (Specialist Identity & Authority)                 |
|  - Specialist identity, domain boundary, owned claim types, permitted      |
|    action types, parameter authority, explicit non-responsibilities.        |
+-----------------------------------------------------------------------------+
|  Layer 3: TASK CONTRACT (Session & Context Coordinate)                      |
|  - Session coordinate, snapshot coordinate, active trigger event, assigned  |
|    entities, blast-radius scope, SLA timeout budget.                        |
+-----------------------------------------------------------------------------+
|  Layer 4: EVIDENCE CONTEXT (Dual-Path Operational Information)              |
|  - Authoritative facts (Path A via PostgreSQL/Neo4j), real-time telemetry  |
|    (Redis), retrieved historical precedents (Path B via pgvector).          |
+-----------------------------------------------------------------------------+
|  Layer 5: ANALYTICAL RESULTS (Quantitative Model Projections)               |
|  - Pre-computed ML forecast ensembles, reliability scores, lead times,     |
|    deterministic constraint bounds, solver baseline solutions.              |
+-----------------------------------------------------------------------------+
|  Layer 6: OUTPUT CONTRACT (Machine-Enforceable Target Schema)               |
|  - Strict Pydantic v2 JSON schema requiring StructuredClaim,              |
|    ActionIntent parameters, uncertainty assessments, and evidence links.    |
+=============================================================================+
```

#### External Security & Context Budget Invariants
- **Prompt Order Precedence:** Layer 1 (Constitution) strictly overrides all subsequent layers.
- **External Security Enforcement:** Prompts are a reasoning aid, NOT a security boundary. Hard authorization constraints (claim allowlists, action allowlists, entity scopes) are enforced by external Python validators outside the LLM.
- **Untrusted Content Isolation:** Text retrieved from Path B (pgvector) or dynamic tool execution outputs is enclosed in isolated `<untrusted_retrieved_evidence>` XML tags.
- **Budget Compression & Preservation of Invariants:** In CPU environments, raw transaction rows are summarized by Phase 1 ML pipelines into scalar projections (`p10`, `p50`, `p90`) to maintain prompt length below 1,000 tokens. If critical evidence cannot fit, the agent compresses with lineage or safely abstains; hard constraints are never silently discarded.

---

### 3. Strict 5-Tier Evidence Hierarchy & Structural Numerical Lineage

When resolving conflicting signals in agent reasoning, the following hierarchy strictly governs:

```text
Level 1: Hard Enterprise Constraints & Physical Limits (Absolute)
         Warehouse storage capacities, transport vehicle volume limits, regulatory bans.
         Cannot be violated under any condition.
  │
  ▼
Level 2: Authoritative Current Operational Facts (High Authority)
         Real-time inventory counts, confirmed purchase orders, active shipments
         originating from PostgreSQL and Neo4j via MCP tools (Path A).
  │
  ▼
Level 3: Registered Analytical Model Ensemble Outputs (Quantitative Authority)
         Forecasts, lead time distributions, reliability metrics from registered ML models.
  │
  ▼
Level 4: Historical Precedents and Episodic RAG (Advisory Context)
         Historical post-mortems and past disruption resolutions from pgvector (Path B).
         Advisory only; strictly forbidden from overriding Level 2 facts.
  │
  ▼
Level 5: LLM Qualitative Interpretation (Bounded Heuristic)
         Synthesis, cross-domain trade-off reasoning, and hypothesis formulation.
         Carries ZERO numerical authority.
```

#### Structural Numerical Provenance Contract
Naive string and ungrounded float matching are strictly prohibited. To guarantee numerical integrity, every decision-relevant quantitative field emitted in `StructuredClaim` and `ActionIntent` must be encapsulated as a `ValueWithProvenance`:

```python
from typing import Literal
from pydantic import BaseModel, Field

class ValueWithProvenance(BaseModel):
    value: float
    unit: str                                   # Validated against canonical physical unit ontology
    entity_id: str                              # Validated against target entity scope
    temporal_scope: str                         # Validated against task temporal scope
    source_class: Literal[
        "OPERATIONAL_FACT",                     # Level 2: PostgreSQL / Neo4j via Path A
        "ANALYTICAL_PREDICTION",                 # Level 3: Registered ML Model (XGBoost)
        "DETERMINISTIC_DERIVATION",              # Verified formula computed from Level 1-3 inputs
        "LLM_QUALITATIVE_ESTIMATE"               # Flagged qualitative estimate (never authoritative)
    ]
    provenance_reference: str                   # Database PK, model run ID, or formula ID
    snapshot_epoch: int                         # Bound to task logical snapshot epoch
    is_authoritative: bool = False              # COMPUTED by trusted runtime validator, never by LLM
    derivation_formula: str | None = None       # e.g., "shortage = po_qty - reorder_point"
    derivation_inputs: list[str] = Field(default_factory=list)  # Provenance IDs of input operands
```

#### Comprehensive Trusted Validation Protocol
The runtime validator verifies the complete validity of numeric parameters through multi-dimensional verification:
1. **Source Authenticity:** The `provenance_reference` is checked against active Level 1-3 evidence records (PostgreSQL primary keys, Neo4j entity identifiers, or registered capability execution IDs). Unreferenced IDs are rejected.
2. **Entity Identity:** The `entity_id` is validated against the task target entity scope. A provenance reference pointing to an unrelated supplier or facility is rejected as an entity mismatch.
3. **Physical Unit Consistency:** The declared `unit` must match the canonical ontology for the parameter (e.g., `USD`, `EA`, `DAYS`, `HOURS`) and must be dimensionally consistent across derivation formulas.
4. **Temporal Scope & Snapshot Alignment:** The declared `snapshot_epoch` must match the active task snapshot coordinate.
5. **Safe Expression Grammar for Derivations:** Declared mathematical formulas (`derivation_formula`) are parsed and evaluated using a closed, safe Abstract Syntax Tree (AST) grammar restricted to basic arithmetic operators (`+`, `-`, `*`, `/`) and a closed whitelist of registered functions (`min`, `max`, `abs`, `sum`). Arbitrary executable code, `eval()`, `exec()`, lambda expressions, and module imports are strictly prohibited and rejected.
6. **Derived Authority Invariant:** `is_authoritative` is an unalterable derived result computed exclusively by trusted runtime validation logic. If any validation dimension fails, or if `source_class == "LLM_QUALITATIVE_ESTIMATE"`, `is_authoritative` evaluates to `False`. Authoritative action parameters strictly require `is_authoritative == True`; qualitative estimates are barred from populating action intent execution parameters.

---

### 4. Dual-Path Information Architecture & Information Router

```
+=============================================================================+
|             DUAL-PATH INFORMATION TOPOLOGY & OWNERSHIP BOUNDARIES           |
+=============================================================================+
|                                                                             |
|  PATH A: AUTHORITATIVE OPERATIONAL INFORMATION (System of Record)           |
|  LLM ──> MCP Tool ──> Governed Service ──> PostgreSQL / Neo4j / Models      |
|  +-----------------------------------------------------------------------+  |
|  | - Current inventory positions and warehouse stock levels               |  |
|  | - Current shipments, lane transit telemetry, and arrival estimates   |  |
|  | - Active purchase orders, customer sales orders, and backlog queues    |  |
|  | - Real-time supplier operational status, facility uptime, and halts   |  |
|  | - Network topology, bill-of-materials, and route graph state          |  |
|  | - Registered analytical model ensemble outputs                        |  |
|  +-----------------------------------------------------------------------+  |
|  Authority: ABSOLUTE GROUND TRUTH for Current Enterprise State              |
|                                                                             |
|  -------------------------------- HARD BOUNDARY --------------------------  |
|                                                                             |
|  PATH B: SEMANTIC MEMORY (Experiential Precedent Context)                   |
|  LLM ──> Retriever Tool ──> pgvector ──> Historical Evidence / Precedents  |
|  +-----------------------------------------------------------------------+  |
|  | - Prior deliberation session records and resolved decision artifacts  |  |
|  | - Historical disruption incident logs, root-cause analyses, and notes |  |
|  | - Post-mortem incident playbooks and operational response lessons     |  |
|  | - Previous mitigation outcomes and counterfactual effectiveness data   |  |
|  | - Analogous historical edge cases and disruption scenarios             |  |
|  +-----------------------------------------------------------------------+  |
|  Authority: ADVISORY ONLY (Informs Hypotheses, Never Overrides Ground Truth)|
+=============================================================================+
```

**Mechanical Path Routing Enforcement:**
1. Operational entity queries (`INVENTORY_POSITION`, `PURCHASE_ORDER`, `SUPPLIER_STATUS`) are routed exclusively to Path A. The `InformationPathRouter` mechanically rejects queries for current operational state directed to Path B.
2. In the event of contradiction between Path A and Path B, Path A deterministically overrides Path B.
3. For Deliverable D03, until the shared D05 retrieval microservice is online, Path A and Path B are accessed through thin, versioned client adapters backed by existing D01/D02 databases without constructing a parallel retrieval platform.

---

### 5. Comprehensive Tool Execution Governance & Workflow Budgeting

To ensure the prescribed reasoning workflow is achievable within resource limits:

1. **Definition of Tool Invocation:** A "tool call" is defined strictly as **one agent-visible invocation during the cognitive loop (Stages 3/6)**, NOT an internal database query.
2. **Exclusion of Pre-Computed Analytics:** Analytical model execution in Stage 4 (ANALYZE) is deterministic pre-computation executed before prompt assembly; it does NOT consume the dynamic LLM tool budget.
3. **Dynamic Tool Cap:** The specialist runtime is allocated a maximum of **3 dynamic tool invocations** during Stage 6 (PROPOSE) for targeted ad-hoc context retrieval (e.g. checking alternative supplier capacity).
4. **Latency Budget Precedence & Timeout Formula:** To prevent tool execution from exceeding task deadlines, each dynamic tool call timeout is governed by strict precedence:
   $$\text{call\_timeout} = \min(\text{remaining\_task\_budget},\; 3.0\text{ s},\; \text{remaining\_cumulative\_tool\_budget})$$
   where the cumulative dynamic tool execution budget is capped at $7.0\text{ s}$. For example, if only $1.5\text{ s}$ remains in the cumulative tool budget, the next call timeout is strictly $1.5\text{ s}$, not $3.0\text{ s}$.
5. **Context Contribution Limits:** Tool return payloads are truncated to a maximum of $1,500$ characters / $\approx 350$ tokens.
6. **Strictly Read-Only (Zero Mutations):** All tools available to the specialist during the reasoning loop are strictly classified as `READ_ONLY`. Mutating tools (e.g., `CREATE_PURCHASE_ORDER`) are barred from D03; physical actuation belongs exclusively to downstream execution services following authorization.
7. **Active Cancellation Verification:** If the task deadline expires or an upstream cancellation signal is received, active tool execution threads and sockets are actively aborted, and the cancellation handler verifies that in-flight operations have terminated immediately.

---

### 6. Deterministic Fallback Engine & Terminal Outcome Taxonomy

The fallback engine guarantees system safety and resilience without forcing reckless proposals:

#### Four Terminal Outcomes

| Terminal Status | Trigger Condition | Emitted Artifact | Authority & Governance |
| :--- | :--- | :--- | :--- |
| **`PROPOSED`** | LLM completes within timeout; passes 4-tier validation | Fully validated `AgentProposal` | Normal authority; candidate evaluated downstream |
| **`DEGRADED_PROPOSED`** | Provider timeout ($> 10\text{ s}$), container 503, syntax retry exhaustion; Level 1-3 facts valid | Schema-compliant `DeterministicFallbackProposal` | `is_degraded = True`; restricted confidence; explicit fault codes (`PROVIDER_TIMEOUT`, `OLLAMA_UNAVAILABLE`) |
| **`ABSTAINED`** | Critical operational evidence missing, unresolvable Level 1-2 contradiction, stale snapshot | Structured abstention report | Safe non-mitigation outcome; triggers upstream escalation without ungrounded actions |
| **`FAILED`** | Unhandled internal exception, unrecoverable state corruption | Terminal fault diagnostic record | Zero proposal emitted; execution aborted fail-closed |

#### Fallback Execution Contract
- **Activation Latency:** The fallback engine emits a schema-compliant proposal within $\le 50\text{ ms}$ of fallback activation (warm in-process logic), excluding time spent waiting for the provider timeout.
- **Rule-Based Synthesis:** Emits baseline rule actions (contractually pre-approved backup supplier allocation) based purely on Level 1-3 analytical outputs.
- **No Hallucinated Fallbacks:** Fallback must never invent missing values. If required input data is absent, the engine emits `ABSTAINED`.

---

### 7. Snapshot Consistency Data Contract (`SnapshotCoordinate`)

To eliminate ambiguity between logical state sequences and physical event horizons, `SnapshotCoordinate` explicitly disentangles logical epochs from wall-clock timestamps:

```python
from datetime import datetime
from pydantic import BaseModel

class SnapshotCoordinate(BaseModel):
    snapshot_epoch: int                         # Monotonically increasing logical epoch / sequence coordinate
    snapshot_timestamp_utc: datetime            # Typed ISO-8601 wall-clock timestamp bounding event horizon
    scenario_id: str
    sor_transaction_id: str                     # PostgreSQL transaction identifier / LSN coordinate
    neo4j_applied_sor_tx_id: str                # Neo4j projection's applied PostgreSQL source transaction ID
    neo4j_projection_version: str               # Neo4j graph projection catalog version
    max_allowable_projection_lag_ms: int = 5000 # Secondary operational telemetry threshold
```

#### Snapshot Consistency Verification Rules:
1. **Cross-Store Transactional Compatibility:** Before Stage 3 execution, the runtime verifies that the Neo4j graph projection is transactionally compatible with the PostgreSQL System of Record snapshot. Compatibility is established if `neo4j_applied_sor_tx_id == sor_transaction_id` or if the projection's recorded source transaction horizon encompasses the required state. If compatibility cannot be verified, the runtime flags `SNAPSHOT_VERSION_INCOMPATIBLE` and safely aborts/abstains. Projection lag in milliseconds is tracked as secondary telemetry, not primary proof of consistency.
2. **Analytical Alignment:** Analytical model executions in Stage 4 declare their input snapshot epoch. If computed against an older logical epoch, they are rejected as stale.
3. **Rejection of Post-Snapshot Evidence:** Any evidence bearing an event timestamp greater than `snapshot_timestamp_utc` is rejected by `ContextFusion` (strict wall-clock to wall-clock comparison).
4. **State Invalidation Reporting:** If a critical operational change occurs during execution, D03 reports `SNAPSHOT_INVALIDATED`; session-wide restart orchestration is owned by D06.

---

### 8. Security, Runtime Hardening & Trust Boundaries

1. **Zero Embedded Secrets:** All database credentials and container URLs are injected via environment variables; none exist in source code, prompts, or images.
2. **Parameterized Data Access:** All MCP tool clients utilize parameterized SQL and Cypher queries.
3. **Proposal Intent vs Physical Actuation Separation:** The runtime produces exclusively *action intents* within an `AgentProposal`. Under no circumstance does the D03 agent possess execution authorization to trigger physical supply chain mutations.
4. **Adversarial Test Corpus Containment:** The runtime is verified against a versioned indirect prompt injection test suite (`tests/fixtures/prompt_injection_v1.json`). Runtime security invariants (action allowlists, parameter ranges, read-only tools) are enforced externally by Python validators regardless of model compliance, guaranteeing 100% containment of the defined test corpus.
5. **Proposal Envelope Sealing:** A "sealed" `ActionIntent` envelope is defined as immutable typed serialization (frozen Pydantic model) accompanied by a deterministic SHA-256 payload digest (`intent_hash = sha256(canonical_json(action_intent))`). This establishes tamper-evident downstream lineage without implying cryptographic PKI digital signatures (which are managed downstream in D07/D08).
6. **Task Idempotency Contract:** The runtime maintains an in-memory idempotency cache keyed by `(task_id, snapshot_epoch)`. Re-delivering an identical task returns the identical cached `AgentProposal` with matching `intent_hash` without re-running LLM inference or re-invoking tools.

---

### 9. Agent-Local Observability, Diagnostics & Audit Events

Each specialist execution emits structured, audit-grade JSON telemetry events to standard logging channels for downstream ingestion by D09:

```json
{
  "event_type": "sarp_stage_completed",
  "task_id": "task-proc-2026-10-10-001",
  "session_id": "sess-disrupt-884",
  "agent_id": "procurement_supplier_agent",
  "snapshot_coordinate": {
    "snapshot_epoch": 1042,
    "snapshot_timestamp_utc": "2026-10-10T14:30:00Z",
    "scenario_id": "scenario-insolvency-s101"
  },
  "stage": "VALIDATE",
  "duration_ms": 42.5,
  "dynamic_tool_calls_count": 1,
  "token_usage": {
    "prompt_tokens": 842,
    "completion_tokens": 312,
    "total_tokens": 1154
  },
  "terminal_status": "PROPOSED",
  "intent_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "model_governance": {
    "model_id": "qwen2.5:3b-instruct-q4_K_M",
    "model_digest": "sha256:d8b2...pinned_digest",
    "prompt_template_hash": "a1f9e2...",
    "capability_versions": {
      "supplier_lead_time_model": "v1.2.0"
    }
  },
  "fault_code": null,
  "is_fallback": false
}
```

- **Replay Diagnostics vs LLM Determinism:** Diagnostic logs record complete logical inputs: snapshot coordinate, evidence IDs, prompt hash, analytical capability versions, random seed, and tool execution traces. While this guarantees 100% deterministic reconstruction of the logical context, local LLM token sampling across CPU thread pools can exhibit minor non-determinism; diagnostics capture full telemetry to explain non-determinism without overpromising bitwise-identical completion strings.
- **Redaction Rules:** Sensitive financial margins and supplier proprietary contract terms are redacted by default.

---

### 10. Service Lifecycle, Startup Checks & Capability-Aware Readiness

1. **Configuration Validation:** Validates all environment variables, paths, and policy YAML files on boot. Missing settings halt startup immediately.
2. **Capability-Aware Readiness Reporting:**
   - `/health/live`: Reports HTTP 200 if agent process is responsive.
   - `/health/ready`: Reports status according to functional capability:
     - `FULL_READY` (HTTP 200): All data sources (PostgreSQL SoR, Neo4j graph) and the Ollama model provider are reachable. Normal cognitive inference is active.
     - `DEGRADED_READY` (HTTP 200): Mandatory data sources (PostgreSQL, Neo4j) are connected and the deterministic fallback engine is operational, but Ollama is unreachable. The service is ready to execute in safe fallback mode.
     - `NOT_READY` (HTTP 503): Any mandatory data source (PostgreSQL SoR or Neo4j) is unreachable, configuration is invalid, or the state machine is corrupted. Because fallback cannot operate safely without Level 1-2 operational facts, the service is strictly NOT ready.
3. **Graceful Shutdown:** Intercepts `SIGTERM`/`SIGINT`, draining active requests within a 5-second grace period before closing connections.
4. **Container Smoke Test:** Validates that the container boots, passes health checks, and processes a synthetic test task within 20 seconds.

---

## The Vertical Research Slice

Deliverable D03 implements an end-to-end **Vertical Research Slice** centered on the **Procurement & Supplier Specialist Agent** (`procurement_supplier_agent`) responding to a critical primary supplier insolvency disruption.

### Vertical Slice Architecture & Pipeline

```
[Disruption Ingest]
Primary Supplier Insolvency Shocks (Supplier S-101 Halted)
         │
         v
[D03: Procurement & Supplier Agent]
Executes SARP-8 Protocol (LangChain Runtime + Qwen 2.5 3B)
Pre-Computes ML Lead Times + Queries Path A Facts + Path B Precedents
Emits StructuredClaim + ActionIntent (Split Sourcing / Expedited PO)
         │
         v
[Candidate Normalization (Test Double)]
Validates ActionRegistry schema, bounds parameters, computes intent_hash
         │
         v
[Digital Twin Simulation (Minimal Adapter)]
Simulates 14-day supply disruption under Action Intent
Simulates 14-day supply disruption under Baseline Heuristic B0
         │
         v
[CD2F Objective Evaluation (Minimal Evaluator)]
Computes multi-objective impact vector: Total Cost, Stockout Severity
         │
         v
[Research Gate Verification (Gate 3.8)]
Evaluates joint outperformance: Delta C >= 5.0% and Delta S >= 10.0%
(Prespecified Wilcoxon signed-rank test, Holm-Bonferroni adjusted p < 0.05)
```

### Research Protocol vs Engineering Acceptance

The vertical slice evaluates the central empirical research hypothesis of D03:
> A hybrid cognitive agent combining deterministic analytical predictions with bounded LLM qualitative reasoning generates actionable mitigation proposals that achieve statistically significant joint outperformance across co-primary supply chain objectives relative to the static rule-based heuristic baseline ($B_0$).

#### Protocol Rigor & Predeclared Analysis Plan
- **Scenario:** S-101 Primary Supplier Insolvency Shock (14-day supply disruption scenario).
- **Experimental Unit & Sample Sizing:** Paired Monte Carlo simulation seed ($s \in S$). The initial benchmark uses **$N = 30$ paired seeds as a power-sized pilot and reference benchmark batch**. (If pilot variance requires greater statistical power for definitive publication, $N$ is expanded based on formal power calculation).
- **Baseline Heuristic $B_0$:** Deterministic static rule: reorder upon stockout at fixed reorder point with primary supplier; if halted, wait 7 days then attempt standard PO.
- **Co-Primary Outcomes (Lower is Better):**
  1. *Total Landed Disruption Cost ($C$, in USD):* Cumulative cost of goods, expedited freight, and delay penalties.
  2. *Stockout Severity ($S$, in Units):* Cumulative unfulfilled customer order units across the 14-day horizon.
- **Sign Convention:** Defined consistently as Cost Reduction ($\Delta C = C(B_0) - C(c) > 0$) and Stockout Reduction ($\Delta S = S(B_0) - S(c) > 0$).
- **Prespecified Statistical Test:** Pre-declared Wilcoxon signed-rank test on paired differences (with exact or bootstrap 95% confidence intervals and paired Hodges-Lehmann median difference effect sizes). Holm-Bonferroni correction is applied across the co-primary outcomes at $\alpha = 0.05$. (The Shapiro-Wilk test is reported strictly as an exploratory diagnostic test for normality, not as a data-dependent branch in the primary analysis).
- **Minimum Meaningful Effect Sizes:** $\Delta C \ge 5.0\%$ cost reduction and $\Delta S \ge 10.0\%$ stockout reduction.
- **Handling of Experimental Anomalies:**
  - *Ties & Zero Differences:* Ranked using standard Pratt / Wilcoxon average rank procedures.
  - *Provider Crashes & Fallback Invocations:* Runs that trigger fallback are evaluated under their resulting fallback proposal.
  - *Safe Abstentions (`ABSTAINED`):* Treated as non-improving safety outcomes in the primary effectiveness evaluation and reported transparently in a separate safety/abstention rate metric.
  - *Missing / Incomplete Runs:* Censored with documented failure codes; silent imputation is strictly prohibited.
- **Conceptual Precision Regarding Pareto Dominance:** Statistically significant joint improvement on both co-primary outcomes ($\Delta C \ge 5.0\%$, $\Delta S \ge 10.0\%$, adjusted $p < 0.05$) demonstrates empirical superiority across the distribution. It is not labeled "strict Pareto dominance" unless every individual seed satisfies $C(c) \le C(B_0)$ and $S(c) \le S(B_0)$ with at least one strict inequality; seed-level Pareto dominance is reported as an empirical sample percentage.
- **Strict Layer Separation:** Gate 3.8 is an empirical research release milestone. It does not substitute for deterministic engineering correctness (Gates 3.1 through 3.7 and 3.9 through 3.14).

---

## Package and Codebase Organization

The D03 codebase is organized into modular packages under `agents/` and `tests/`:

```text
agents/
    runtime/
        __init__.py
        agent_runtime.py               # Core SpecialistCognitiveRuntime container
        sarp_engine.py                 # SARP-8 state machine and execution protocol
        fallback_engine.py             # Deterministic ML/rules fallback engine
        context_fusion.py              # Context assembler fusing Facts, Analytics, and RAG
    prompt/
        __init__.py
        prompt_stack.py                # StructuredPromptStack container & assembler
        global_constitution.py         # Layer 1: Invariants & Evidence Hierarchy
        domain_contract.py             # Layer 2: Domain ownership & authority rules
        task_contract.py               # Layer 3: Session & snapshot context
        evidence_context.py            # Layer 4: Path A facts & Path B precedents
        analytical_results.py          # Layer 5: Pre-computed ML forecast payloads
        output_contract.py             # Layer 6: Pydantic v2 JSON schema definitions
    providers/
        __init__.py
        base_provider.py               # LLMProvider abstract base class
        ollama_provider.py             # Local Ollama Qwen 2.5 3B implementation
        reasoning_service.py           # High-level ReasoningService protocol
    capabilities/
        __init__.py
        capability_contract.py         # AnalyticalCapabilityContract schema
        capability_registry.py         # In-memory registry of analytical models
        supplier_lead_time_model.py    # Required ML lead-time model (XGBoost)
        supplier_risk_model.py         # Required supplier disruption risk model
    retrieval/
        __init__.py
        path_router.py                 # InformationPathRouter (Path A vs Path B enforcement)
        mcp_fact_client.py             # Path A: MCP operational data adapter
        pgvector_precedent_client.py   # Path B: pgvector semantic memory adapter
    specialists/
        procurement_supplier/
            __init__.py
            agent.py                   # Procurement & Supplier Agent implementation
            domain_policy.yaml         # Machine-enforceable DomainOwnershipPolicy binding
            tools.py                   # Bounded dynamic tools (max 3 calls)
    vertical_slice/
        __init__.py
        slice_orchestrator.py          # End-to-end slice test runner
        minimal_twin_adapter.py        # 14-day discrete simulation test double
        minimal_cd2f_evaluator.py      # Two-objective impact evaluation test double
        b0_baseline_heuristic.py       # Static rule-based benchmark comparator

tests/
    unit/
        test_sarp_engine.py            # 8-stage transition and fail-closed tests
        test_prompt_stack.py           # 6-layer prompt stack assembly and budgeting
        test_ollama_provider.py        # Ollama connection and schema enforcement tests
        test_capability_contracts.py   # AnalyticalCapabilityContract registry tests
        test_path_router.py            # Path A vs Path B invariant violation tests
        test_numerical_discipline.py   # Structural numerical provenance & AST grammar tests
        test_tool_governor.py          # Bounded tool execution, timeout precedence tests
    integration/
        test_procurement_agent_sarp.py # End-to-end procurement agent reasoning test
        test_deterministic_fallback.py# Fallback trigger and analytical execution test
        test_cancellation.py           # Task cancellation propagation and thread verification
        test_security_isolation.py     # Versioned prompt injection corpus containment tests
    evaluation/
        test_vertical_slice_b0.py      # Statistical evaluation of slice vs B0 heuristic
    fixtures/
        prompt_injection_v1.json       # Versioned adversarial injection test fixtures
```

---

## Standalone Acceptance Criteria ("Definition of Done")

To consider Deliverable D03 complete, the implementation must satisfy fourteen normative verification gates.
- **Gates 3.1 through 3.8:** Canonical Architecture Verification Gates defined in [`final_decision_engine_draft.md` Section 73](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/decision_engine_architecture_fabric/final_decision_engine_draft.md#73-deliverable-d03-formal-verification-gates-and-acceptance-criteria-definition-of-done).
- **Gates 3.9 through 3.14:** D03-Specific Normative Extensions establishing runtime engineering completeness, security isolation, replay diagnostics, and container lifecycle readiness.

```
                              +---------------------------------------+
                              |      D03 Phase 1 Verification Loop    |
                              +-------------------+-------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                      |                                      |
     +-----v-----+                          +-----v-----+                          +-----v-----+
     | Gate 3.1  |                          | Gate 3.2  |                          | Gate 3.3  |
     |  Schema   |                          | Numerical |                          |   Tool    |
     |>= 98.0%   |                          | Lineage   |                          | Budget Min|
     +-----+-----+                          +-----+-----+                          +-----+-----+
           |                                      |                                      |
           +--------------------------------------+--------------------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                      |                                      |
     +-----v-----+                          +-----v-----+                          +-----v-----+
     | Gate 3.4  |                          | Gate 3.5  |                          | Gate 3.6  |
     |  SARP-8   |                          | Dual-Path |                          | Fallback  |
     |Fail-Closed|                          | Routing   |                          | <= 50 ms  |
     +-----+-----+                          +-----+-----+                          +-----+-----+
           |                                      |                                      |
           +--------------------------------------+--------------------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                      |                                      |
     +-----v-----+                          +-----v-----+                          +-----v-----+
     | Gate 3.7  |                          | Gate 3.8  |                          | Gate 3.9  |
     | Benchmark |                          |  B0 Beat  |                          | Contract  |
     | Reference |                          | p < 0.05  |                          | Integrity |
     +-----+-----+                          +-----+-----+                          +-----+-----+
           |                                      |                                      |
           +--------------------------------------+--------------------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                   |                  |                   |                  |
     +-----v-----+       +-----v-----+      +-----v-----+       +-----v-----+      +-----v-----+
     | Gate 3.10 |       | Gate 3.11 |      | Gate 3.12 |       | Gate 3.13 |      | Gate 3.14 |
     | Snapshot  |       |   Fault   |      | Security  |       | Replay    |      | Capability|
     | Integrity |       |Containment|      | Isolation |       |Diagnostics|      | Readiness |
     +-----------+       +-----------+      +-----------+       +-----------+      +-----------+
```

### Canonical Section 73 Verification Gates (Gates 3.1 -- 3.8)

#### Gate 3.1: Schema Conformance Rate (>= 98.0%) & 100% Containment
- **Requirement:** Evaluated across a benchmark suite of $N = 100$ consecutive synthetic and historical supply chain disruption tasks.
- **Disaggregated Metrics Reporting:**
  1. *LLM First-Pass Schema Validity:* $\ge 98.0\%$ first-pass schema validation without retry across 100 tasks.
  2. *Post-Retry Validity:* Bounded retry (maximum 1 attempt) resolving remaining initial formatting errors.
  3. *Fallback Invocation Rate:* Explicit tracking of tasks routed to fallback upon retry exhaustion.
  4. *Accepted-Output Containment Invariant:* **100% containment** of invalid outputs (0.0% unvalidated or malformed proposals escape runtime validation). Tasks failing validation after bounded retry must be intercepted and routed to the deterministic fallback engine or emitted as safe abstentions. (Abstentions are counted toward safety containment, not LLM schema parse success).

#### Gate 3.2: Structural Numerical Lineage & Hallucination Elimination
- **Requirement:** 100% of numeric quantities appearing in `StructuredClaim` and `ActionIntent` parameters must encapsulate a verified `ValueWithProvenance` struct linking them to Level 1-3 operational evidence or registered analytical models.
- **Pass Threshold:** Exactly 0.0% ungrounded, fabricated, or hallucinated numeric values across the test suite.
- **Multi-Dimensional Validation:**
  1. `provenance_reference` verified against trusted PostgreSQL SoR primary keys or model execution records.
  2. Target entity and physical unit validated against canonical ontologies.
  3. Temporal scope verified within `snapshot_timestamp_utc`.
  4. Mathematical derivations evaluated using a closed, safe AST arithmetic grammar (zero arbitrary code execution).
  5. `is_authoritative` is an unalterable derived validator output; qualitative estimates (`LLM_QUALITATIVE_ESTIMATE`) are barred from action parameters.

#### Gate 3.3: Comprehensive Tool Bounding (<= 3 Dynamic Calls & Budget Precedence)
- **Requirement:** Bounded dynamic tool execution during Stage 6 (PROPOSE). Dynamic agent-visible tool invocations are strictly capped at $\le 3$ calls per task lifecycle.
- **Pass Threshold:**
  1. No execution sequence exceeds 3 dynamic tool invocations.
  2. Pre-computed ML analytics (Stage 4) execute deterministically and do not count against the dynamic tool cap.
  3. Timeout precedence strictly enforced: $\text{call\_timeout} = \min(\text{remaining\_task\_budget},\; 3.0\text{ s},\; \text{remaining\_cumulative\_tool\_budget})$.
  4. Cumulative tool execution capped at $7.0\text{ s}$; individual tool payloads truncated to $\le 350$ tokens.
  5. 100% of available tools verified as read-only.
  6. In-flight operations cancelled and verified stopped upon deadline expiration.

#### Gate 3.4: SARP-8 State Machine Integrity
- **Requirement:** Formal verification of monotonic progression across all eight stages:
  `RECEIVE -> SCOPE -> RETRIEVE -> ANALYZE -> CHECK -> PROPOSE -> VALIDATE -> EMIT`.
- **Pass Threshold:** 100% compliance across all unit and property-based tests. Stage skipping, reverse transitions, and execution loops are architecturally blocked. Any invariant violation immediately aborts execution via a fail-closed exception.

#### Gate 3.5: Dual-Path Information Routing Enforcement
- **Requirement:** Complete mechanical separation of Authoritative Operational Facts (Path A) from Advisory Precedents (Path B).
- **Pass Threshold:**
  1. 100% of operational entity queries (`INVENTORY_POSITION`, `PURCHASE_ORDER`, `SUPPLIER_STATUS`) are routed to Path A; operational queries directed to Path B are rejected by `InformationPathRouter`.
  2. In every synthetic contradiction injection scenario where historical precedent conflicts with current PostgreSQL operational state, Path A strictly supersedes Path B.

#### Gate 3.6: Deterministic Fallback Execution & Safe Abstention
- **Requirement:** Resilient fault handling on provider disruption. If Ollama inference exceeds timeout ($> 10.0\text{ s}$), crashes, or emits malformed output, the runtime invokes the deterministic fallback pipeline.
- **Pass Threshold:**
  1. Emits a valid, schema-compliant `DeterministicFallbackProposal` within $\le 50\text{ ms}$ of fallback activation (warm in-process logic) when Level 1-3 facts are available.
  2. Safely emits `ABSTAINED` when critical operational facts are missing or unresolvable, preventing the generation of ungrounded proposals.
  3. Emitted proposals carry `is_degraded = True` and explicit fault codes.

#### Gate 3.7: Measured Latency on Pinned Reference Hardware
- **Reference Hardware Specification:**
  - CPU: AMD EPYC 7763 or Intel Xeon Platinum 8375C (8 vCPUs pinned), AVX2/AVX-512 enabled, 16 GB RAM.
  - OS: Ubuntu 22.04 LTS (Kernel 5.15+), Docker Engine 24.0+.
  - Container Limits: `cpus: "8.0"`, `memory: 6144M`.
  - Pinned Image & Model: `ollama/ollama:0.4.1`, model `qwen2.5:3b-instruct-q4_K_M` (verified SHA-256 digest).
  - Ollama Configuration: `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_NUM_THREADS=8`.
  - Standardized Workload: Assembled context fixed to $850 \pm 50$ tokens, target completion fixed to 350 tokens.
- **Qualification vs Tail Benchmark Classification:**
  - *Engineering Smoke Benchmark ($N = 30$ warm runs):* Used for initial engineering qualification and operational sanity.
  - *Statistically Reliable Tail-Latency Benchmark ($N \ge 100$ runs):* Required for formal publication of $p95$ and $p99$ tail bounds with empirical confidence intervals.
- **Normative Pass Thresholds (Reference CPU Host):**
  - Warm Time to First Token (TTFT): $p50 < 1,500\text{ ms}$, $p95 < 2,000\text{ ms}$ on reference CPU ($p50 < 150\text{ ms}$ on reference GPU).
  - Proposal Generation (350 tokens): $p50 < 11.0\text{ s}$, $p95 < 14.0\text{ s}$ ($< 15.0\text{ s}$ ceiling) on reference CPU ($< 1.5\text{ s}$ on reference GPU).
  - End-to-End Deliberation Cycle: $p50 < 13.0\text{ s}$, $p95 < 16.0\text{ s}$ on reference CPU ($< 2.0\text{ s}$ on reference GPU).

#### Gate 3.8: Vertical Slice B0 Baseline Outperformance (Research Release Milestone)
- **Requirement:** In the frozen S-101 supplier insolvency scenario, the hybrid cognitive agent's synthesized action must achieve statistically significant joint improvement across co-primary outcomes relative to the static heuristic baseline $B_0$.
- **Pass Threshold:** Statistically significant reduction in Total Landed Disruption Cost ($\Delta C \ge 5.0\%$) and Stockout Severity ($\Delta S \ge 10.0\%$) at significance level $p < 0.05$ (Holm-Bonferroni adjusted across co-primary outcomes) evaluated under a pre-declared Wilcoxon signed-rank test across a minimum pilot batch of $N = 30$ paired simulation seeds.
- **Reporting Requirements:** Full publication of paired effect sizes (Hodges-Lehmann median differences), 95% confidence intervals, tie counts, safe abstention rates, and fallback occurrences.

---

### D03-Specific Normative Extensions (Gates 3.9 -- 3.14)

#### Gate 3.9: Contract and Authorization Integrity
- **Requirement:** All emitted proposals must strictly comply with the canonical `DomainOwnershipPolicy` and `ActionRegistry`.
- **Pass Threshold:** 100% compliance. Proposing unauthorized action types, out-of-scope entity IDs, or unowned claims results in immediate validation rejection.

#### Gate 3.10: Snapshot and Temporal Provenance Integrity
- **Requirement:** All evidence, analytical models, and outputs must be strictly bound to the task's `SnapshotCoordinate`.
- **Pass Threshold:** 100% compliance. Transactional compatibility between PostgreSQL and Neo4j is established via transaction identifiers (`sor_transaction_id` vs `neo4j_applied_sor_tx_id`); incompatible snapshots trigger rejection. Evidence bearing timestamps greater than `snapshot_timestamp_utc` is discarded. Output proposals accurately reference the input snapshot coordinate.

#### Gate 3.11: Fault Containment, Deadline Propagation, and Cancellation
- **Requirement:** End-to-end task deadline budgets are propagated through provider calls, tools, retries, and fallback. Upstream task cancellation signals must cleanly terminate all active subroutines.
- **Pass Threshold:** Zero orphaned background threads, socket leaks, or unhandled asyncio exceptions upon cancellation. Verified immediate termination of in-flight operations.

#### Gate 3.12: Security Isolation & Adversarial Corpus Containment
- **Requirement:** Adversarial text embedded within retrieved evidence or tool outputs must not alter agent instructions, override domain policies, or trigger unauthorized actions.
- **Pass Threshold:** 100% containment across the versioned indirect prompt injection test suite (`tests/fixtures/prompt_injection_v1.json`). Zero state mutations against the baseline System of Record. External Python validation prevents unauthorized actions regardless of model output.

#### Gate 3.13: Logical Replay Diagnostics
- **Requirement:** Every execution run must emit sufficient structured metadata to reconstruct logical execution: snapshot coordinate, evidence IDs, model digest, prompt template hash, capability versions, random seeds, and tool references.
- **Pass Threshold:** 100% of execution runs produce replay-capable diagnostic logs with sensitive fields appropriately redacted. Trace metadata provides sufficient diagnostic detail to explain minor local token variations.

#### Gate 3.14: Standalone Lifecycle & Capability-Aware Readiness Verification
- **Requirement:** The agent runtime service must validate configuration on boot, report accurate readiness/liveness status by capability, and pass a standalone container smoke test.
- **Pass Threshold:** Pinned container image (`ollama/ollama:0.4.1`) with verified model digest; readiness correctly reports `FULL_READY`, `DEGRADED_READY`, or `NOT_READY` according to component health; smoke test executes end-to-end synthetic task successfully within 20 seconds.

---

## Definition of Done (Three-Layer Acceptance Checklist)

Deliverable D03 acceptance is structured across three distinct evaluation layers. Passing Layers 1 and 2 establishes that D03 is an implemented, safe, and independently testable cognitive runtime. Layer 3 determines whether the empirical research hypothesis is supported. Favorable research outcomes do not substitute for engineering correctness, and empirical success is never claimed before running the frozen experiment.

### Layer 1 -- Mandatory Runtime Correctness (Engineering Safety)
- [ ] 1. **Contract Conformance:** All canonical runtime contracts (`TaskContract`, `AgentProposal`, `ActionIntent`, `StructuredClaim`, `DomainOwnershipPolicy`, `ActionRegistry`) are imported from canonical definitions and validated via Pydantic v2.
- [ ] 2. **SARP-8 State Machine:** Monotonic progression verified across all 8 stages; stage skipping and reverse loops blocked; fail-closed transitions on errors.
- [ ] 3. **Validation & Containment:** 100% containment verified: zero malformed, unauthorized, or out-of-scope proposals escape runtime validation as accepted outputs.
- [ ] 4. **Structural Numerical Lineage:** All numerical values encapsulated as `ValueWithProvenance`; multi-dimensional validation enforced (authenticity, entity, unit, temporal scope); derivations evaluated via safe AST arithmetic grammar; `is_authoritative` computed by validator.
- [ ] 5. **Evidence Hierarchy & Snapshot Integrity:** Path A strictly supersedes Path B; blocking Level 1-2 contradictions trigger safe abstention; `SnapshotCoordinate` separates logical epoch from ISO-8601 timestamps; cross-store transactional compatibility verified.
- [ ] 6. **Tool Bounding & Cancellation:** Dynamic tool calls strictly capped at <= 3; timeout precedence enforced (`min` of task budget, call limit, and cumulative tool budget); read-only tools enforced; active cancellation terminates in-flight operations.
- [ ] 7. **Deterministic Fallback Engine:** Emits schema-compliant proposals within <= 50 ms upon simulated provider disruption; safely emits `ABSTAINED` on missing data; zero ungrounded fallbacks.
- [ ] 8. **Security & State Isolation:** Zero embedded secrets; parameterized queries; 100% containment against versioned prompt injection corpus; zero physical actuation authority.

### Layer 2 -- Operational Readiness (Packaging & Diagnostics)
- [ ] 9. **Pinned Container & Sizing:** Pinned container image (`ollama/ollama:0.4.1`) and verified model digest (`qwen2.5:3b-instruct-q4_K_M`); `OLLAMA_NUM_PARALLEL=1` and `OLLAMA_NUM_THREADS=8` configured for single-agent slice; empirical peak container RSS <= 3.5 GB on reference host.
- [ ] 10. **Lifecycle & Capability Readiness:** Configuration validated on boot; `/health/ready` accurately reports `FULL_READY`, `DEGRADED_READY`, and `NOT_READY`; graceful shutdown handles `SIGTERM`/`SIGINT`.
- [ ] 11. **Diagnostics & Replay Manifest:** Structured JSON audit telemetry emitted for all stages; logical replay metadata (snapshot, template hash, capability versions, random seed, intent_hash) recorded.
- [ ] 12. **Vertical Slice End-to-End Execution:** The Procurement & Supplier Agent vertical slice executes end-to-end using documented simulation and CD2F test doubles.

### Layer 3 -- Research Release (Empirical Evaluation)
- [ ] 13. **Frozen Baseline Comparator:** Static heuristic baseline comparator $B_0$ frozen and executed on identical paired Monte Carlo seeds.
- [ ] 14. **Predeclared Statistical Protocol:** Wilcoxon signed-rank test on paired differences with Holm-Bonferroni correction at $\alpha = 0.05$ across minimum pilot batch ($N = 30$ paired seeds).
- [ ] 15. **Transparent Outcome Reporting:** Complete reporting of co-primary effect sizes ($\Delta C \ge 5.0\%$, $\Delta S \ge 10.0\%$), 95% confidence intervals, tie counts, safe abstention rates, fallback occurrences, and empirical seed-level Pareto dominance percentages.
