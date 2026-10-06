# SCOF V2 Cognitive Decision Fabric -- Canonical Architecture Plan

## Document Purpose

This document is the authoritative specification for the SCOF V2 Cognitive Decision Fabric architecture spanning deliverables D3 through D10. Every schema, contract, invariant, pipeline, state machine, and architecture diagram herein represents the definitive, implementation-ready contract.

---

## Table of Contents

### Part I: Architectural Foundation
1. [Ten Architectural Invariants](#1-ten-architectural-invariants)
2. [Canonical D3-D10 Deliverable Map](#2-canonical-d3-d10-deliverable-map)
3. [Six Cognitive Stages](#3-six-cognitive-stages)
4. [High-Level Architecture Diagram](#4-high-level-architecture-diagram)

### Part II: Canonical Registries and Vocabularies
5. [ClaimType Registry](#5-claimtype-registry)
6. [EvidenceClass Registry](#6-evidenceclass-registry)
7. [Unified ActionRegistry](#7-unified-actionregistry)
8. [Registry Startup Validation](#8-registry-startup-validation)

### Part III: Agent Layer (D3/D4)
9. [Agent Roster: Six Specialists + Coordinator](#9-agent-roster-six-specialists--coordinator)
10. [Agent Ownership Contracts (DomainOwnershipPolicy)](#10-agent-ownership-contracts)
11. [Agent Cognitive Runtime: Hybrid ML + LLM](#11-agent-cognitive-runtime)
12. [LLM Strategy: ReasoningService Abstraction](#12-llm-strategy)
13. [Memory Architecture: SCOF-Native Model](#13-memory-architecture)

### Part IV: Evidence and Retrieval Layer (D5)
14. [Evidence Architecture: Provenance, Authority, Epistemic Boundaries](#14-evidence-architecture)
15. [Agentic RAG: Two-Tier MCP-Governed Retrieval](#15-agentic-rag)
16. [Two-Class Retrieval Model](#16-two-class-retrieval-model)

### Part V: Orchestration and Deliberation Layer (D6)
17. [LangGraph Orchestration Kernel](#17-langgraph-orchestration-kernel)
18. [Coordinator Service Decomposition](#18-coordinator-service-decomposition)
19. [Deliberation Table: Event-Sourced Cognitive Workspace](#19-deliberation-table)
20. [Domain Affinity Routing](#20-domain-affinity-routing)
21. [Cross-Examination Governance](#21-cross-examination-governance)
22. [Evidence Sufficiency Gate](#22-evidence-sufficiency-gate)
23. [Priority and SLA: Two-Dimensional Model](#23-priority-and-sla)
24. [Decision Snapshot and Temporal Consistency](#24-decision-snapshot)
25. [Session State Machine](#25-session-state-machine)

### Part VI: Decision Object Model
26. [Agent Output: StructuredClaim and CandidateAction](#26-agent-output-model)
27. [ActionIntent / ActionImpact Separation](#27-actionintent-actionimpact-separation)
28. [Three-Tier Impact Evaluation Model](#28-three-tier-impact-evaluation)
29. [Candidate Normalization and Budget Selection Pipeline](#29-candidate-normalization-pipeline)

### Part VII: Counterfactual Evaluation and Arbitration (D7)
30. [Digital Twin: Counterfactual Evaluator](#30-digital-twin)
31. [Twin Simulation Materiality and Requirement Classification](#31-twin-simulation-materiality)
32. [CD2F Evidence-Based Arbitration Engine](#32-cd2f-arbitration-engine)
33. [Direction-Aware Objective Normalization](#33-objective-normalization)
34. [Pareto Analysis and Confidence Labels](#34-pareto-analysis)
35. [Execution Authorization (ExecutionPolicyService)](#35-execution-authorization)
36. [State Revalidation Before Execution](#36-state-revalidation)

### Part VIII: Event and Runtime Backbone (D8)
37. [State Authority Map](#37-state-authority-map)
38. [Transactional Outbox Pattern](#38-transactional-outbox)
39. [SCOFEvent Contract](#39-scofevent-contract)
40. [Kafka Topic Architecture](#40-kafka-topic-architecture)
41. [Consumer Idempotency](#41-consumer-idempotency)

### Part IX: Decision Policy Layer
42. [DecisionPolicy Schema](#42-decision-policy)
43. [Policy Precedence Hierarchy](#43-policy-precedence)
44. [Policy and Profile Integrity](#44-policy-integrity)

### Part X: Agent Reliability and Governance
45. [R_i Agent Reliability Factor](#45-r_i-reliability)
46. [R_i Lifecycle Governance](#46-r_i-lifecycle)
47. [Contradiction Taxonomy](#47-contradiction-taxonomy)
48. [Failure Taxonomy and Response Map](#48-failure-taxonomy)
49. [Cancellation Propagation](#49-cancellation-propagation)

### Part XI: Observability, Explainability, and Decision Record (D9)
50. [Decision Record](#50-decision-record)
51. [Outcome Observation Schema](#51-outcome-observation)
52. [Replay Manifest](#52-replay-manifest)
53. [MCP Capability Versioning and Side-Effect Classification](#53-capability-versioning)

### Part XII: Evaluation and Benchmark (D10)
54. [B0-B7 Ablation Ladder](#54-ablation-ladder)
55. [Statistical Evaluation Protocol](#55-statistical-protocol)
56. [Evaluation Metrics and Targets](#56-evaluation-metrics)

### Part XIII: Execution Boundary and Cross-Cutting Concerns
57. [Execution Boundary Matrix](#57-execution-boundary)
58. [Mechanism Responsibility Matrix](#58-mechanism-responsibility)
59. [Redis Governance](#59-redis-governance)
60. [Priority-Aware Admission Control](#60-admission-control)
61. [Concurrent Session Interference Detection](#61-concurrent-sessions)

### Part XIV: Architecture Diagrams
62. [Detailed Unified Architecture Diagram](#62-unified-architecture-diagram)
63. [Corrected LangGraph State Machine](#63-langgraph-state-machine)

### Part XV: Implementation
64. [Evaluation-Gated Implementation Sequencing](#64-implementation-sequencing)
65. [Contract Freeze Declaration](#65-contract-freeze-declaration)
66. [Improvement and Future Enhancement Backlog](#66-improvement-backlog)

---

# PART I: ARCHITECTURAL FOUNDATION

---

## 1. Ten Architectural Invariants

These ten invariants are the non-negotiable foundational properties of the D3-D10 architecture. Every design decision, implementation contract, runtime mechanism, and evaluation criterion must strictly satisfy them.

### Invariant 1: Source Authority

```
PostgreSQL:
    Authoritative operational facts (System of Record).

Neo4j:
    Authoritative representation of the current materialized
    topology projection, subject to projection freshness/version.
    Derived from PostgreSQL via batch/streaming sync.

No operational fact may be made authoritative solely
because it exists in Neo4j. If PostgreSQL and Neo4j
disagree on an operational fact, PostgreSQL wins.
```

### Invariant 2: Cognitive Workspace Boundary

```
The Deliberation Table stores decision artifacts
(claims, critiques, verdicts, directives).
It NEVER stores or replicates enterprise operational truth.

DeliberationEvents are authoritative for the historical
cognitive session state.

PostgreSQL operational tables remain authoritative for
enterprise operational state.

These are separate authority domains. "Events are the
source of truth" applies ONLY to the deliberation event
stream, not globally.
```

### Invariant 3: Evidence Sufficiency

```
Agent response != sufficient evidence.
Evidence sufficiency is a multi-dimensional assessment of:
coverage, freshness, authority, consistency, critical-fact presence,
and tiered criticality (HARD_CRITICAL / DEGRADED_CRITICAL /
IMPORTANT / SUPPLEMENTARY).

Criticality != average evidence quality.
Every HARD_CRITICAL fact must INDIVIDUALLY be:
    present, authoritative, fresh enough (>= min_hard_critical_freshness),
    and non-contradicted.
Aggregate (average) freshness is a supplementary quality signal
and can NEVER compensate for a failing critical fact.
```

### Invariant 4: Candidate Discipline

```
No unbounded candidate or simulation expansion.
Candidate budget and simulation budget are explicit, configurable limits.
Budget enforcement (Step 10) is a HEURISTIC (UCB-based), not a safety proof.

Every candidate that enters the Digital Twin -- atomic OR synthesized
composite -- must have passed: schema, registry, ownership, entity,
impact, hard constraints, deduplication, and budget selection.
Synthesized composite candidates must re-enter the validation pipeline
before budget allocation. This is enforced mechanically by the
CandidateAdmissionSeal (Section 29).
```

### Invariant 5: Counterfactual Isolation

```
The Digital Twin can mutate ONLY isolated Layer-3 scenario state.
It cannot modify Layer-1 (historical fact) or Layer-2 (baseline operational state).
Every simulation is bound to a reproducible manifest.
```

### Invariant 6: Decision Authority Hierarchy

```
LLM: proposes, interprets, explains (non-authoritative for numbers).
ImpactEvaluationService: computes impact from authoritative data (three tiers).
CD2F: evaluates Pareto dominance directly on multi-objective normalized
      VECTORS U(c), then applies policy-weighted scalar utility and
      uncertainty penalties ONLY to resolve multi-candidate frontiers.
      CD2F SELECTS the winning candidate; it NEVER authorizes execution.
ExecutionPolicyService: gates execution (separate from decision approval).
Execution Adapter: acts (with policy-gated authorization).
```

### Invariant 7: Policy Authority

```
The organization's Decision Policy defines:
objectives, constraints, autonomy, escalation, and risk tolerance.
LLMs, agents, and CD2F do NOT define what "good" means.
Policy comes from the domain profile, not from inference.
Policy precedence: Safety > Enterprise Hard > Profile Policy > Soft > Agent Preference.
```

### Invariant 8: State Freshness

```
Every decision is bound to a declared world-state snapshot
using a common snapshot_epoch coordinate.
All agents in a session reason over the same observation boundary.

Post-snapshot evidence is REJECTED from the decision state.
If critical state changes are detected after the snapshot:
    - The snapshot is advanced and ALL agents restart (no partial restart)
    - Maximum advancement count is enforced to prevent infinite loops

Post-snapshot evidence may be QUARANTINED as auxiliary information
for HITL review, but it MUST NOT influence automated scoring,
evidence sufficiency assessment, or CD2F arbitration.
```

### Invariant 9: Execution Safety

```
Decision approval (CD2F Tier-1) != physical execution.
Decision approval and execution authorization are SEPARATE gates.
The execution gate is controlled by organizational policy, not by CD2F confidence.
State revalidation occurs between ExecutionPolicy approval and execution.
```

### Invariant 10: Replayability

```
Every decision is reconstructable from:
state snapshot + evidence + model versions + policy version +
candidate actions + simulations + events + random seeds.

Replay fidelity is bounded and explicitly classified:
TRACE / LOGICAL / MODEL / EXACT_SYSTEM.
EXACT_SYSTEM requires explicit confirmation that all dependencies
are captured. Overclaiming replay fidelity is prohibited.
```

---

## 2. Canonical D3-D10 Deliverable Map

This table is FROZEN. Every reference in every document, diagram, heading, table, and code comment must use exactly this mapping.

| D | Name | Responsibility | Phase |
| :--- | :--- | :--- | :--- |
| **D1** | Enterprise World and Simulation Foundation | Frozen | Complete |
| **D2** | Enterprise Knowledge and Data Fabric | Frozen | Complete |
| **D3** | Cognitive Agent Runtime | Single-agent bounded reasoning, ReasoningService, ML+LLM hybrid, vertical research slice | Phase 1 |
| **D4** | Specialist Federation and Agent Cards | 6-agent expansion, Agent Card V2, DomainOwnershipPolicy, A2A lifecycle | Phase 2 |
| **D5** | Agentic Retrieval and Evidence Fabric | SCOFRetriever, MCP-governed retrieval, evidence provenance, two-tier RAG | Phase 3 |
| **D6** | Cognitive Orchestration and Deliberation | LangGraph state machine, Deliberation Table, domain affinity routing, cross-examination, evidence sufficiency gate | Phase 4 |
| **D7** | CD2F Arbitration and Counterfactual Decision | CD2F objective function, Twin counterfactual evaluation, candidate normalization, DecisionSnapshot, DecisionPolicy | Phase 5 |
| **D8** | Event and Runtime Backbone | Kafka topic architecture, transactional outbox, SCOFEvent contract, consumer idempotency, API Gateway | Phase 6 |
| **D9** | Observability, Explainability and Desktop Console | Decision trace, evidence visualization, trade-off explanation, Tauri v2 HITL console, DecisionRecord archival | Phase 7 |
| **D10** | Evaluation and Benchmark | Benchmark suite, ablation baseline ladder, R_i calibration, SLA validation, anti-overfitting measures, RQ1-RQ4 | Phase 8 |

---

## 3. Six Cognitive Stages

The D3-D10 architecture is organized around six cognitive stages (KNOW, UNDERSTAND, DELIBERATE, EXPLORE, DECIDE, EXPLAIN). This mental model governs runtime flow and state machine transitions (with DELIBERATE strictly preceding EXPLORE).

```
+-----------------------------------------------------------------------------+
|                    STAGE 1: KNOW (Evidence Acquisition)                     |
|           PostgreSQL System of Record + Neo4j Topology + pgvector           |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                 STAGE 2: UNDERSTAND (Specialist Reasoning)                  |
|               6 Autonomous Domain Specialists (Hybrid ML + LLM)             |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                  STAGE 3: DELIBERATE (Cognitive Workspace)                  |
|                 Deliberation Table + Targeted Cross-Critique                |
+-----------------------------------------------------------------------------+
                                       |
                                       v
                        /-----------------------------\
                       <   EVIDENCE SUFFICIENCY GATE   >
                        \-----------------------------/
                                       |
                 +---------------------+---------------------+
                 | INSUFFICIENT                              | SUFFICIENT
                 v                                           v
+---------------------------------+         +---------------------------------+
|        HITL ESCALATION          |         |    STAGE 4: EXPLORE (Twin)      |
|    (Human Incident Review)      |         | Isolated Scenario Simulation    |
+---------------------------------+         +---------------------------------+
                                                             |
                                           /----------------------------------\
                                          <   Simulation Violates Expectation? >
                                           \----------------------------------/
                                                             |
                                        +--------------------+--------------------+
                                        | YES (First Time)                        | NO
                                        v                                         v
                         +-----------------------------+            +-----------------------------+
                         |  TARGETED RE-DELIBERATION   |            |       STAGE 5: DECIDE       |
                         |   (Max 1 Bounded Cycle)     |            |    CD2F Vector Arbitration  |
                         +-----------------------------+            +-----------------------------+
                                        |                                         |
                                        +--------------------+--------------------+
                                                             |
                                                             v
                                              +-----------------------------+
                                              |      STAGE 6: EXPLAIN       |
                                              |    D9 Observability Trace   |
                                              +-----------------------------+
```

| Stage | Component | Core Question |
| :--- | :--- | :--- |
| **KNOW** | D1/D2 + Agentic RAG | What facts, context, and precedents are relevant? |
| **UNDERSTAND** | Specialist Agents (ML + LLM) | What does each domain expert conclude from the evidence? |
| **DELIBERATE** | Coordinator + Deliberation Table + Cross-Examination | Where do experts agree and disagree? Can conflicts be resolved? |
| **EXPLORE** | Digital Twin (counterfactual sandbox) | What happens if we take each proposed action? |
| **DECIDE** | CD2F (with DecisionPolicy) | Which candidate action is best justified by evidence, constraints, policy, and simulated outcomes? |
| **EXPLAIN** | D9 Observability | Complete provenance chain from trigger to outcome. |

### DELIBERATE-EXPLORE Interaction Loop

The primary flow is: DELIBERATE -> EXPLORE -> DECIDE. An optional feedback loop exists:

```
+-----------------------------------------------------------------------------+
|              EXPLORE: Digital Twin Counterfactual Simulation Branch         |
+-----------------------------------------------------------------------------+
                                       |
                                       v
                     /-----------------------------------\
                    <   Twin Outcome Exceeds Surprise     >
                    <   or Severe Deviation Threshold?    >
                     \-----------------------------------/
                                       |
                 +---------------------+---------------------+
                 | NO                                        | YES (First Occurrence)
                 v                                           v
+---------------------------------+         +---------------------------------+
|       PROCEED TO DECIDE         |         |    TARGETED RE-DELIBERATION     |
|   Forward to CD2F Arbitration   |         | Coordinator Posts Shock Findings|
+---------------------------------+         | Agents Revise Domain Proposals  |
                                            +---------------------------------+
                                                             |
                                                             v
                                            +---------------------------------+
                                            |   CANDIDATE RE-NORMALIZATION    |
                                            |  11-Step Revalidation Pipeline  |
                                            +---------------------------------+
                                                             |
                                                             v
                                            +---------------------------------+
                                            |       TWIN RE-SIMULATION        |
                                            |   (Strictly Max 1 Re-Sim Pass)  |
                                            +---------------------------------+
                                                             |
                                                             v
                                            +---------------------------------+
                                            |       PROCEED TO DECIDE         |
                                            |   Forward to CD2F Arbitration   |
                                            +---------------------------------+
```

**Bound:** This EXPLORE -> DELIBERATE loop executes at most once. If the second simulation still produces unexpected results, the system proceeds to CD2F with available evidence and flags elevated uncertainty.

---

## 4. High-Level Architecture Diagram

```
+===================================================================================================+
|                                SCOF V2 COGNITIVE DECISION FABRIC                                  |
|                             (Canonical Architecture Reference D3-D10)                             |
+===================================================================================================+
|                                                                                                   |
|  +---------------------------------------------------------------------------------------------+  |
|  | D9: OBSERVABILITY, EXPLAINABILITY AND HUMAN-IN-THE-LOOP CONSOLE                             |  |
|  | - Tauri v2 Desktop GUI        - End-to-End Decision Trace Log     - What-If Scenario Lab    |  |
|  | - Evidence Graph Viewer       - Multi-Objective Frontier Radar    - DecisionRecord Archival |  |
|  | - HITL Escalation Inbox       - Criticality Sensitivity Report    - Replay Engine (Bounded) |  |
|  +---------------------------------------------------------------------------------------------+  |
|         |                                            ^                                            |
|         | User Directives / Approvals                | Real-Time Session & Audit Streams          |
|         v                                            |                                            |
|  +---------------------------------------------------------------------------------------------+  |
|  | D8: EVENT AND RUNTIME BACKBONE                                                              |  |
|  | - FastAPI REST & WebSocket Gateways              - Transactional Outbox Relay               |  |
|  | - Kafka Message Transport (Partitioned by Session) - Idempotent Consumer State Machines     |  |  
|  | - SCOFEvent Strict Schema Envelope               - DB-Level Session State Transition Locks  |  |
|  +---------------------------------------------------------------------------------------------+  |
|         |                                            ^                      ^                     |
|         | Policy Directives                          | Deliberation Events  | Evaluation Feeds    |
|         v                                            |                      |                     |
|  +-------------------------------------+             |       +---------------------------------+  |
|  | DECISION POLICY LAYER (FROM PROFILE)|             |       | D10: EVALUATION AND BENCHMARKS  |  |
|  | - Objective Metric Definitions      |             |       | - B0 to B7 Ablation Ladder      |  |
|  | - Direction-Aware Normalization     |             |       | - Non-Parametric Permutation    |  |
|  | - 6-Level Precedence Hierarchy      |             |       | - ECE / Brier Reliability Tests |  |
|  | - Anti-Tamper Content Hash Excl.    |             |       | - Anti-Overfitting Scenario Set |  |
|  +-------------------------------------+             |       +---------------------------------+  |
|         | Configured Objectives & Gates              |                      ^                     |
|         v                                            |                      | Traces & Metrics    |
|  +=============================================================================================+  |
|  | D6: LANGGRAPH MACRO-ORCHESTRATION KERNEL (COORDINATOR META-FRAMEWORK)                       |  |
|  |                                                                                             |  |
|  |   [Disruption Trigger Ingest]                                                               |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [1. Allocate Atomic DecisionSnapshot Epoch] ---> World-State Consistency Coordinate       |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [2. Tier-1 RAG Pre-Retrieval] -------------> Broad & Shallow Context Package              |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [3. Capability Binding & Affinity Routing] -> Resolve Dynamic MCP Tools & Agent Roster    |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [4. Parallel Specialist Fan-Out] ----------> Zero Cross-Agent Visibility (Independent)    |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [5. Deliberation Table Fan-In] ------------> Collate Observations, Claims & Proposals     |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [6. Targeted Cross-Examination] -----------> Conflict-Directed Critiques (Max 2 Rounds)   |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [7. EVIDENCE SUFFICIENCY GATE] ------------> Individual HARD_CRITICAL Freshness/Authority |  |
|  |             |                                  (Fail -> Mandatory HITL Escalation)          |  |
|  |             v                                                                               |  |
|  |   [8. Candidate Extraction & Normalization] -> Schema, Entity, T1 Baseline & T2 Predictive  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [9. Controlled Combination Synthesis] -----> Non-Conflicting Cross-Domain Pairs           |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [10. MANDATORY REVALIDATION PASS] ---------> Composites Validated on Schema, Entities,    |  |
|  |             |                                  Hard Constraints, Joint Impact & Dedup       |  |
|  |             v                                                                               |  |
|  |   [11. Candidate Budget Selection] ----------> UCB Heuristic + Baseline & Domain Coverage   |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [12. Digital Twin Materiality Check] ------> Required / Recommended / Advisory Gate       |  |
|  |             |                                                                               |  |
|  |             +==========================+==================================+                 |  |
|  |                                        |                                  |                 |  |
|  |                                [Simulatable]                    [Non-Simulatable]           |  |
|  |                                        |                                  |                 |  |
|  |                                        v                                  |                 |  |
|  |                          [13. Digital Twin Simulation]                    |                 |  |
|  |                          (Counterfactual Tier-3 Impact)                   |                 |  |
|  |                                        |                                  |                 |  |
|  |                                        v                                  v                 |  |
|  |             +=============================================================+                 |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [14. CD2F VECTOR PARETO ARBITRATION] ------> Multi-Objective Vector Frontier P on U(c)    |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [15. Frontier Policy Resolution] ----------> Scalar Utility J_final = J - lambda*Uncert   |  |
|  |             |                                  (Singleton / Policy Resolved / Ambiguity)    |  |
|  |             v                                                                               |  |
|  |   [16. Return DecisionResult] ---------------> CD2F Selects (Does NOT Authorize Execution)  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [17. ExecutionPolicyService Gate] ---------> Autonomous Threshold & Role Permission Check |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [18. Pre-Execution State Revalidation] ----> Detect Epoch Drift & Invalidation            |  |
|  |             |                                                                               |  |
|  |             +------------+-------------------------------+-------------------+              |  |
|  |                          |                               |                   |              |  |
|  |                    [State Valid]                 [Material Drift]      [Policy Gate]        |  |
|  |                          |                               |                   |              |  |
|  |                          v                               v                   v              |  |
|  |                  [Execute Adapter]               [Trigger Replan]    [HITL Escalation]      |  |
|  +=============================================================================================+  |
|         | Tool Invocations       ^ Agent Proposals          ^ Simulation Results|                 |
|         v via Governed MCP       | & Cross-Critiques        | & Validation Envs | State Checks    |
|  +----------------------------------------------------+   +-------------------+ |                 |
|  | D3/D4: LANGCHAIN SPECIALIST REASONING AGENT ROSTER |   | D7: DIGITAL TWIN  | |                 |
|  | [1] Demand & Commerce Agent                        |   | (COUNTERFACTUAL   | |                 |
|  | [2] Inventory & Asset Management Agent             |   |  EVALUATION)      | |                 |
|  | [3] Procurement & Supplier Agent                   |   | - Scenario Layer 3| |                 |
|  | [4] Logistics & Transport Agent                    |   |   State Mutation  | |                 |
|  | [5] Financial & Enterprise Value Agent             |   | - Reproducible    | |                 |
|  | [6] Risk & Resilience Agent                        |   |   Manifest Replay | |                 |
|  | Each Specialist Runs:                              |   | - Multi-Horizon   | |                 |
|  | - Hybrid Domain ML Models + Bounded LLM Reasoning  |   |   Rollout [7..28d]| |                 |
|  | - Tier-2 Deep RAG (MCP Governed + Hot-Path Cache)  |   +-------------------+ |                 |
|  | - Strict DomainOwnershipPolicy & ActionIntent Only |             ^           |                 |
|  +----------------------------------------------------+             |           |                 |
|         | Read Artifacts              ^ Append Events               | Manifests | Projections     |
|         v & Materialized Views        | (Session Partitioned)       |           v                 |
|  +---------------------------------------------------------------------------------------------+  |
|  | DELIBERATION TABLE (EVENT-SOURCED COGNITIVE WORKSPACE)                                      |  |
|  | - Authoritative Cognitive Events: PostgreSQL deliberation_events (Append-Only, Immutable)   |  |
|  | - Materialized Session Projections: Redis session:{id}:{epoch}:{seq} (Snapshot-Keyed)       |  |
|  | - Single-Writer Sequence Allocation & DB Constraint: UNIQUE(session_id, sequence_number)    |  |
|  +---------------------------------------------------------------------------------------------+  |
|         | Reads & Graph Traversals                                  | Write Events / Sync         |
|         v                                                           v                             |
|  +---------------------------------------------------------------------------------------------+  |
|  | D1 + D2: ENTERPRISE DATA FABRIC (SYSTEM OF RECORD)                                          |  |
|  | - PostgreSQL: Authoritative operational facts (96 core relational tables, transactional)    |  |
|  | - Neo4j: Current materialized topology projection (3.73M nodes, version-stamped)            |  |
|  | - pgvector: Semantic memory & historical decision precedent index (384-dimensional)         |  |
|  | - Redis: Ephemeral real-time telemetry cache (governed, fail-closed on critical queries)    |  |
|  | - Atomic Snapshot Epoch Coordinator: Common temporal coordinate for all session reasoning   |  |
|  +---------------------------------------------------------------------------------------------+  |
|                                                                                                   |
+===================================================================================================+
```

---

# PART II: CANONICAL REGISTRIES AND VOCABULARIES

---

## 5. ClaimType Registry

The single source of truth for all valid claim types in the system. Every `owned_claim_type`, `consumes_from` reference, and `forbidden_claim_type` in agent contracts MUST reference an entry in this registry.

```python
class ClaimTypeRegistry:
    """Canonical registry of all valid claim types.
    Enforced at system startup.
    Naming convention: {domain}_{assessment_type}"""
    
    # ---- Procurement & Supplier Domain ----
    SUPPLIER_OPERATIONAL_ASSESSMENT = "supplier_operational_assessment"
    PROCUREMENT_COST_ANALYSIS = "procurement_cost_analysis"
    ALTERNATE_SOURCING_FEASIBILITY = "alternate_sourcing_feasibility"
    SUPPLIER_CAPACITY_ASSESSMENT = "supplier_capacity_assessment"
    
    # ---- Risk & Resilience Domain ----
    SUPPLIER_FINANCIAL_DISTRESS = "supplier_financial_distress"
    SYSTEMIC_RISK_ASSESSMENT = "systemic_risk_assessment"
    CASCADE_FAILURE_ANALYSIS = "cascade_failure_analysis"
    REGULATORY_COMPLIANCE_STATUS = "regulatory_compliance_status"
    CORRIDOR_RISK_ASSESSMENT = "corridor_risk_assessment"
    GEOPOLITICAL_RISK_ASSESSMENT = "geopolitical_risk_assessment"
    SUPPLIER_CONCENTRATION_RISK = "supplier_concentration_risk"
    NETWORK_FRAGILITY_ASSESSMENT = "network_fragility_assessment"
    
    # ---- Demand & Commerce Domain ----
    DEMAND_ASSESSMENT = "demand_assessment"
    COMMERCIAL_IMPACT_ANALYSIS = "commercial_impact_analysis"
    PRICING_RECOMMENDATION = "pricing_recommendation"
    REVENUE_IMPACT_ASSESSMENT = "revenue_impact_assessment"
    PROMOTIONAL_IMPACT_ANALYSIS = "promotional_impact_analysis"
    
    # ---- Inventory & Asset Management Domain ----
    INVENTORY_VIABILITY_ASSESSMENT = "inventory_viability_assessment"
    REPLENISHMENT_ANALYSIS = "replenishment_analysis"
    ASSET_CONDITION_REPORT = "asset_condition_report"
    INVENTORY_CONCENTRATION_ASSESSMENT = "inventory_concentration_assessment"
    INVENTORY_POSITION_ASSESSMENT = "inventory_position_assessment"
    
    # ---- Logistics & Transport Domain ----
    TRANSPORT_FEASIBILITY = "transport_feasibility"
    ROUTE_OPTIMIZATION_ANALYSIS = "route_optimization_analysis"
    CARBON_IMPACT_ASSESSMENT = "carbon_impact_assessment"
    ROUTE_VULNERABILITY_ASSESSMENT = "route_vulnerability_assessment"
    TRANSPORT_COST_ASSESSMENT = "transport_cost_assessment"
    CARRIER_CAPACITY_ASSESSMENT = "carrier_capacity_assessment"
    
    # ---- Financial & Enterprise Value Domain ----
    ECONOMIC_CONSEQUENCE_ASSESSMENT = "economic_consequence_assessment"
    COST_IMPACT_ANALYSIS = "cost_impact_analysis"
    WORKING_CAPITAL_PROJECTION = "working_capital_projection"
    MARGIN_IMPACT_ANALYSIS = "margin_impact_analysis"
    PENALTY_EXPOSURE_ASSESSMENT = "penalty_exposure_assessment"
```

---

## 6. EvidenceClass Registry

Orthogonal to ClaimTypeRegistry. Classifies evidence by its epistemic nature, not by what it asserts.

```python
class EvidenceClass(str, Enum):
    """Canonical classification of evidence by epistemic nature.
    Orthogonal to ClaimTypeRegistry.
    Used in: critical-fact profiles, evidence sufficiency, quality scoring."""
    
    CURRENT_STATE = "current_state"
    """Direct observation of current entity state.
    Freshness sensitivity: HIGH."""
    
    TOPOLOGICAL = "topological"
    """Supply chain network structure.
    Freshness sensitivity: MODERATE."""
    
    FORECAST = "forecast"
    """Predictive model output.
    Freshness sensitivity: VARIABLE."""
    
    HISTORICAL = "historical"
    """Past decisions or outcomes.
    Freshness sensitivity: LOW."""
    
    REGULATORY = "regulatory"
    """Regulatory requirements or contract terms.
    Freshness sensitivity: MODERATE."""
    
    FINANCIAL = "financial"
    """Financial data or economic models.
    Freshness sensitivity: MODERATE."""
```

### Relationship between ClaimType and EvidenceClass

```
ClaimTypeRegistry:
    WHAT the agent asserts (proposition domain)
    Example: supplier_operational_assessment
    Used in: agent ownership contracts, cross-examination targeting

EvidenceClass:
    WHAT KIND of knowledge supports the assertion
    Example: current_state
    Used in: critical-fact profiles, evidence quality assessment

A single claim may be supported by evidence from multiple classes.
A single evidence class may support multiple claim types.
```

---

## 7. Unified ActionRegistry

The single source of truth for ALL action-related metadata.

### 7.1 Registry Contract: Exact Schema-Configuration Parity

The Pydantic schema and the YAML configuration are ONE unified contract. There is no second interpretation or runtime ambiguity.

```
RULE 1: Every field declared in ActionRegistryEntry is strictly REQUIRED.
        No field has a default value.
RULE 2: The YAML mapping key IS the action_type identifier.
        The loader injects it; an "action_type" key inside the body
        is rejected as a duplicate declaration.
RULE 3: Conditional fields (twin_handler_id, execution_capability_id)
        are nullable but NOT optional: the key MUST be present in YAML,
        and its value MUST be explicitly written as null when not applicable.
RULE 4: Unknown keys are strictly forbidden (extra="forbid").
RULE 5: Any schema violation, missing key, or validation failure aborts system startup.
```

### 7.2 Field Requirement Matrix

| Field | Key Required | Nullable | Validation Constraint |
| :--- | :---: | :---: | :--- |
| `action_type` | Mapping Key | No | Unique snake_case string, injected by loader |
| `display_name` | Yes | No | Non-empty human-readable label |
| `description` | Yes | No | Non-empty operational description |
| `primary_domain` | Yes | No | One of 6 domain names or `universal` |
| `primary_owner_agent` | Yes | No | Valid agent_id or `coordinator`; must be in `permitted_proposers` |
| `permitted_proposers` | Yes | No | Non-empty list of agent_ids or `coordinator` |
| `parameter_authority` | Yes | No | Must be in `permitted_proposers`, or `COMPONENT_DELEGATED` for `composite_action` |
| `intent_schema_class` | Yes | No | Resolves to a registered Pydantic ActionIntent subclass |
| `impact_evaluation_tier` | Yes | No | `BASELINE_ONLY` or `BASELINE_AND_PREDICTIVE` |
| `simulatable` | Yes | No | Boolean |
| `twin_handler_id` | Yes | Yes | Non-null string IFF `simulatable == True`; explicit `null` otherwise |
| `execution_capability_id` | Yes | Yes | Non-null string IFF `advisory_only == False`; explicit `null` otherwise |
| `advisory_only` | Yes | No | Boolean |

### 7.3 ActionRegistryEntry Schema

```python
COMPONENT_DELEGATED = "COMPONENT_DELEGATED"
"""Reserved parameter_authority sentinel. Legal ONLY for composite_action.
Indicates that each constituent action intent within the composite bundle
remains governed by its own respective parameter authority."""


class ActionRegistryEntry(BaseModel):
    """Single canonical definition of an action type.
    ALL action-related metadata lives here.
    Strict validation: Every field is explicitly REQUIRED; no defaults; extra fields forbidden."""
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    # Identity
    action_type: str                       # Injected from YAML mapping key
    display_name: str
    description: str
    
    # Domain Classification
    primary_domain: str
    
    # Ownership and Authority
    primary_owner_agent: str
    permitted_proposers: list[str]
    parameter_authority: str
    
    # Typed Intent Schema Binding
    intent_schema_class: str
    
    # Impact Evaluation Tier
    impact_evaluation_tier: Literal[
        "BASELINE_ONLY",
        "BASELINE_AND_PREDICTIVE",
    ]
    
    # Digital Twin Simulation Binding
    simulatable: bool
    twin_handler_id: Optional[str]         # Required key; explicit null if simulatable=False
    
    # Execution Capability Binding
    execution_capability_id: Optional[str] # Required key; explicit null if advisory_only=True
    advisory_only: bool
    
    @property
    def composable(self) -> bool:
        """Derived property. An action may participate in a composite_action
        only if it is executable, simulatable, and is neither do_nothing
        nor already a composite action."""
        return (
            not self.advisory_only
            and self.simulatable
            and self.action_type not in ("do_nothing", "composite_action")
        )
    
    def validate(self) -> list[str]:
        errors = []
        at = self.action_type
        
        if not self.display_name.strip():
            errors.append(f"{at}: display_name cannot be empty")
        if not self.description.strip():
            errors.append(f"{at}: description cannot be empty")
        if not self.permitted_proposers:
            errors.append(f"{at}: permitted_proposers cannot be empty")
        if self.primary_owner_agent not in self.permitted_proposers:
            errors.append(f"{at}: primary_owner_agent '{self.primary_owner_agent}' must be in permitted_proposers")
            
        if self.parameter_authority == COMPONENT_DELEGATED:
            if at != "composite_action":
                errors.append(f"{at}: COMPONENT_DELEGATED is reserved solely for 'composite_action'")
        elif self.parameter_authority not in self.permitted_proposers:
            errors.append(f"{at}: parameter_authority '{self.parameter_authority}' must be in permitted_proposers")
            
        if self.advisory_only and self.execution_capability_id is not None:
            errors.append(f"{at}: advisory_only=True requires execution_capability_id=null")
        if not self.advisory_only and self.execution_capability_id is None:
            errors.append(f"{at}: advisory_only=False requires valid execution_capability_id string")
        if self.simulatable and self.twin_handler_id is None:
            errors.append(f"{at}: simulatable=True requires valid twin_handler_id string")
        if not self.simulatable and self.twin_handler_id is not None:
            errors.append(f"{at}: simulatable=False requires twin_handler_id=null")
            
        if at == "composite_action":
            if self.intent_schema_class != "CompositeActionIntent":
                errors.append(f"{at}: intent_schema_class must be 'CompositeActionIntent'")
            if self.permitted_proposers != ["coordinator"]:
                errors.append(f"{at}: permitted_proposers must be ['coordinator']")
            if self.parameter_authority != COMPONENT_DELEGATED:
                errors.append(f"{at}: parameter_authority must be '{COMPONENT_DELEGATED}'")
                
        return errors


class ActionRegistry:
    """Singleton registry. Loaded and validated at startup."""
    
    _entries: dict[str, ActionRegistryEntry] = {}
    
    @classmethod
    def register(cls, entry: ActionRegistryEntry) -> None:
        if entry.action_type in cls._entries:
            raise ValueError(f"Duplicate action_type registration: {entry.action_type}")
        cls._entries[entry.action_type] = entry
    
    @classmethod
    def get(cls, action_type: str) -> ActionRegistryEntry:
        if action_type not in cls._entries:
            raise KeyError(f"Action '{action_type}' not registered in ActionRegistry")
        return cls._entries[action_type]
    
    @classmethod
    def get_all_action_types(cls) -> set[str]:
        return set(cls._entries.keys())
    
    @classmethod
    def validate_all(cls) -> list[str]:
        errors = []
        for entry in cls._entries.values():
            errors.extend(entry.validate())
        return errors
```

### 7.4 Canonical Action Definitions (Exhaustive YAML)

Every action declares all 12 body fields explicitly. Conditional fields write explicit `null` when not applicable. The closed registry contains exactly 18 actions across all enterprise operational domains.

```yaml
actions:
  # ---- Logistics & Transport Domain ----
  reroute_shipment:
    display_name: "Reroute Shipment"
    description: "Move an in-transit or scheduled shipment onto an alternate route or corridor."
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    parameter_authority: logistics_transport
    intent_schema_class: RerouteShipmentIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.logistics.reroute_shipment.v1
    execution_capability_id: exec.logistics.reroute_shipment.v1
    advisory_only: false

  expedite_shipment:
    display_name: "Expedite Shipment"
    description: "Upgrade the freight service level of an active shipment to shorten transit duration."
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    parameter_authority: logistics_transport
    intent_schema_class: ExpediteShipmentIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.logistics.expedite_shipment.v1
    execution_capability_id: exec.logistics.expedite_shipment.v1
    advisory_only: false

  change_freight_mode:
    display_name: "Change Freight Mode"
    description: "Switch transportation mode for a lane or order (e.g. ocean to air, road to intermodal)."
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    parameter_authority: logistics_transport
    intent_schema_class: ChangeFreightModeIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.logistics.change_freight_mode.v1
    execution_capability_id: exec.logistics.change_freight_mode.v1
    advisory_only: false

  # ---- Procurement & Supplier Domain ----
  switch_supplier:
    display_name: "Switch Supplier"
    description: "Re-source open purchase demand to a qualified secondary or alternate supplier."
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: SwitchSupplierIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.procurement.switch_supplier.v1
    execution_capability_id: exec.procurement.switch_supplier.v1
    advisory_only: false

  increase_purchase_order:
    display_name: "Increase Purchase Order"
    description: "Increase line quantity on an existing purchase order within vendor capacity."
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: IncreasePurchaseOrderIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.procurement.increase_purchase_order.v1
    execution_capability_id: exec.procurement.increase_purchase_order.v1
    advisory_only: false

  cancel_purchase_order:
    display_name: "Cancel Purchase Order"
    description: "Cancel an unfulfilled purchase order or PO line to curtail inventory inflow."
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: CancelPurchaseOrderIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.procurement.cancel_purchase_order.v1
    execution_capability_id: exec.procurement.cancel_purchase_order.v1
    advisory_only: false

  expedite_purchase_order:
    display_name: "Expedite Purchase Order"
    description: "Renegotiate delivery date with supplier to bring forward ship date."
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: ExpeditePurchaseOrderIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.procurement.expedite_purchase_order.v1
    execution_capability_id: exec.procurement.expedite_purchase_order.v1
    advisory_only: false

  # ---- Inventory & Asset Management Domain ----
  reallocate_inventory:
    display_name: "Reallocate Inventory"
    description: "Transfer available stock between nodes in the distribution network."
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset]
    parameter_authority: inventory_asset
    intent_schema_class: ReallocateInventoryIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.inventory.reallocate_inventory.v1
    execution_capability_id: exec.inventory.reallocate_inventory.v1
    advisory_only: false

  adjust_safety_stock:
    display_name: "Adjust Safety Stock"
    description: "Recalibrate safety stock target days of supply for a SKU at a stocking location."
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset, demand_commerce]
    parameter_authority: inventory_asset
    intent_schema_class: AdjustSafetyStockIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.inventory.adjust_safety_stock.v1
    execution_capability_id: exec.inventory.adjust_safety_stock.v1
    advisory_only: false

  quarantine_inventory:
    display_name: "Quarantine Inventory"
    description: "Temporarily freeze suspect inventory lots to prevent allocation or shipment."
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset, risk_resilience]
    parameter_authority: inventory_asset
    intent_schema_class: QuarantineInventoryIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.inventory.quarantine_inventory.v1
    execution_capability_id: exec.inventory.quarantine_inventory.v1
    advisory_only: false

  # ---- Demand & Commerce Domain ----
  promotion_adjustment:
    display_name: "Promotion Adjustment"
    description: "Throttle, postpone, or cancel a planned promotional campaign to dampen demand."
    primary_domain: demand_commerce
    primary_owner_agent: demand_commerce
    permitted_proposers: [demand_commerce]
    parameter_authority: demand_commerce
    intent_schema_class: PromotionAdjustmentIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.demand.promotion_adjustment.v1
    execution_capability_id: exec.demand.promotion_adjustment.v1
    advisory_only: false

  demand_signal_override:
    display_name: "Demand Signal Override"
    description: "Apply an expert correction to baseline statistical demand forecast."
    primary_domain: demand_commerce
    primary_owner_agent: demand_commerce
    permitted_proposers: [demand_commerce]
    parameter_authority: demand_commerce
    intent_schema_class: DemandSignalOverrideIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.demand.demand_signal_override.v1
    execution_capability_id: exec.demand.demand_signal_override.v1
    advisory_only: false

  # ---- Risk & Resilience Domain ----
  risk_mitigation_recommendation:
    display_name: "Risk Mitigation Recommendation"
    description: "Advisory mitigation guidance regarding supplier fragility, compliance, or disruption."
    primary_domain: risk_resilience
    primary_owner_agent: risk_resilience
    permitted_proposers: [risk_resilience]
    parameter_authority: risk_resilience
    intent_schema_class: RiskMitigationRecommendationIntent
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    twin_handler_id: null
    execution_capability_id: null
    advisory_only: true

  compliance_hold:
    display_name: "Compliance Hold"
    description: "Enforce a regulatory or sanctions block on physical movement or purchase orders."
    primary_domain: risk_resilience
    primary_owner_agent: risk_resilience
    permitted_proposers: [risk_resilience]
    parameter_authority: risk_resilience
    intent_schema_class: ComplianceHoldIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.risk.compliance_hold.v1
    execution_capability_id: exec.risk.compliance_hold.v1
    advisory_only: false

  # ---- Financial & Enterprise Value Domain ----
  financial_impact_flag:
    display_name: "Financial Impact Flag"
    description: "Advisory flag highlighting severe working capital, margin, or penalty exposure."
    primary_domain: financial_enterprise
    primary_owner_agent: financial_enterprise
    permitted_proposers: [financial_enterprise]
    parameter_authority: financial_enterprise
    intent_schema_class: FinancialImpactFlagIntent
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    twin_handler_id: null
    execution_capability_id: null
    advisory_only: true

  budget_escalation:
    display_name: "Budget Escalation"
    description: "Advisory escalation requesting executive spend approval beyond autonomous limits."
    primary_domain: financial_enterprise
    primary_owner_agent: financial_enterprise
    permitted_proposers: [financial_enterprise]
    parameter_authority: financial_enterprise
    intent_schema_class: BudgetEscalationIntent
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    twin_handler_id: null
    execution_capability_id: null
    advisory_only: true

  # ---- Universal Actions ----
  do_nothing:
    display_name: "Do Nothing (Baseline)"
    description: "Mandatory counterfactual baseline candidate: observe natural disruption trajectory."
    primary_domain: universal
    primary_owner_agent: coordinator
    permitted_proposers: [coordinator]
    parameter_authority: coordinator
    intent_schema_class: DoNothingIntent
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: true
    twin_handler_id: twin.universal.baseline_passthrough.v1
    execution_capability_id: exec.universal.noop.v1
    advisory_only: false

  composite_action:
    display_name: "Composite Action Bundle"
    description: >-
      Mechanical bundle of 2..N individually validated, agent-proposed atomic
      intents of different action types. Introduces no new parameters.
      Synthesized only by CandidateService (Section 29, Step 8) and always
      revalidated (Section 29, Step 9) before budget selection.
    primary_domain: universal
    primary_owner_agent: coordinator
    permitted_proposers: [coordinator]
    parameter_authority: COMPONENT_DELEGATED
    intent_schema_class: CompositeActionIntent
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: twin.universal.composite_joint.v1
    execution_capability_id: exec.universal.composite_dispatch.v1
    advisory_only: false
```

### 7.5 Strict Registry Loader

The loader validates structure before instantiating Pydantic objects, guaranteeing that missing keys, unknown fields, or redundant definitions are caught immediately at startup.

```python
REQUIRED_BODY_KEYS: frozenset[str] = frozenset(
    ActionRegistryEntry.model_fields.keys() - {"action_type"}
)   # Exactly 12 keys


def load_action_registry(path: Path) -> list[str]:
    """Load and validate canonical actions YAML. Returns error list.
    System startup MUST abort if the returned list is non-empty."""
    
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))["actions"]
    errors: list[str] = []
    
    for action_type, body in raw.items():
        keys = set(body.keys())
        
        if "action_type" in keys:
            errors.append(f"{action_type}: 'action_type' must not appear in body (Rule 2)")
            continue
            
        missing = REQUIRED_BODY_KEYS - keys
        unknown = keys - REQUIRED_BODY_KEYS
        
        if missing:
            errors.append(f"{action_type}: missing required fields {sorted(missing)} (Rule 1/3)")
        if unknown:
            errors.append(f"{action_type}: unknown fields detected {sorted(unknown)} (Rule 4)")
        if missing or unknown:
            continue
            
        try:
            entry = ActionRegistryEntry(action_type=action_type, **body)
            ActionRegistry.register(entry)
        except (ValidationError, ValueError) as exc:
            errors.append(f"{action_type}: {exc}")
            
    errors.extend(ActionRegistry.validate_all())
    return errors
```

---

## 8. Registry Startup Validation

All three registries (ClaimTypeRegistry, EvidenceClass, ActionRegistry) are cross-validated against agent contracts, Twin handlers, and execution capabilities at system startup. If any validation check returns errors, startup is unconditionally blocked.

```python
def validate_claim_registry(agent_cards: list[AgentCard]) -> list[str]:
    """Validates all agent contracts reference registered claim types
    and valid source agents. Nonexistent source agents produce explicit errors."""
    
    registered = set(vars(ClaimTypeRegistry).values())
    agent_map = {card.agent_id: card for card in agent_cards}
    errors = []
    
    for card in agent_cards:
        policy = card.ownership_policy
        
        for claim in policy.owned_claim_types:
            if claim not in registered:
                errors.append(f"{card.agent_id}: owned_claim '{claim}' not in ClaimTypeRegistry")
        
        for source_agent, claims in policy.consumes_from.items():
            if source_agent not in agent_map:
                errors.append(f"{card.agent_id}: references nonexistent agent '{source_agent}'")
                continue
            
            source_card = agent_map[source_agent]
            for claim in claims:
                if claim not in registered:
                    errors.append(f"{card.agent_id}: consumes unregistered '{claim}'")
                if claim not in source_card.ownership_policy.owned_claim_types:
                    errors.append(f"{card.agent_id}: '{source_agent}' does not own '{claim}'")
        
        for claim in policy.forbidden_claim_types:
            if claim not in registered:
                errors.append(f"{card.agent_id}: forbidden_claim '{claim}' not in registry")
        
        for action in policy.forbidden_action_types:
            if action not in ActionRegistry.get_all_action_types():
                errors.append(f"{card.agent_id}: forbidden_action '{action}' not in ActionRegistry")
    
    return errors


def validate_action_registry_completeness(
    registry: ActionRegistry,
    agent_cards: list[AgentCard],
    twin_handlers: dict[str, TwinHandler],
    execution_capabilities: dict[str, ExecutionCapability]
) -> list[str]:
    """Full cross-registry integrity check at startup.
    Every action reference must resolve; composite_action must satisfy invariants."""
    
    errors = registry.validate_all()
    agent_ids = {card.agent_id for card in agent_cards}
    
    for entry in registry._entries.values():
        if entry.simulatable and entry.twin_handler_id not in twin_handlers:
            errors.append(f"{entry.action_type}: twin_handler '{entry.twin_handler_id}' not found in TwinHandlerRegistry")
        if entry.execution_capability_id and entry.execution_capability_id not in execution_capabilities:
            errors.append(f"{entry.action_type}: execution_capability '{entry.execution_capability_id}' not found in CapabilityRegistry")
        if entry.primary_owner_agent not in agent_ids and entry.primary_owner_agent != "coordinator":
            errors.append(f"{entry.action_type}: owner agent '{entry.primary_owner_agent}' not found")
        for proposer in entry.permitted_proposers:
            if proposer not in agent_ids and proposer != "coordinator":
                errors.append(f"{entry.action_type}: permitted proposer '{proposer}' not found")
        if entry.parameter_authority != COMPONENT_DELEGATED and entry.parameter_authority not in agent_ids and entry.parameter_authority != "coordinator":
            errors.append(f"{entry.action_type}: parameter_authority '{entry.parameter_authority}' not found")
            
    return errors
```

---

# PART III: AGENT LAYER (D3/D4)

---

## 9. Agent Roster: Six Specialists + Coordinator

The enterprise surface is consolidated into 6 specialist agents plus a Coordinator. Each specialist governs a logical operational cluster consuming multiple data domains with non-overlapping primary ownership.

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
|       |      Core Question: What demand/commercial effect is occurring?     |
|       |      Domains: Commerce, POS Sales, Promotions, Calendar Events,     |
|       |               Weather, Demand Forecasting, Pricing/Elasticity       |
|       |                                                                     |
|       +-- [2] INVENTORY & ASSET MANAGEMENT AGENT                            |
|       |      Core Question: Can the network physically hold, preserve,      |
|       |        and stage the required inventory?                            |
|       |      Domains: Inventory Positions, Replenishment, Assortments,      |
|       |               Physical Assets, Shelf Life, Goods Receipts,          |
|       |               Storage Conditions                                    |
|       |                                                                     |
|       +-- [3] PROCUREMENT & SUPPLIER AGENT                                  |
|       |      Core Question: Can the supply network provide what is needed?  |
|       |      Domains: Supplier Performance, Contracts, Purchase Orders,     |
|       |               MOQ, Price Tiers, Three-Way Match, Vendor             |
|       |               Qualification, Alternate Sourcing                     |
|       |      DOES NOT own: supplier financial distress assessment           |
|       |                                                                     |
|       +-- [4] LOGISTICS & TRANSPORT AGENT                                   |
|       |      Core Question: Can we move it?                                 |
|       |      Domains: Transport Lanes, Shipments, Carriers, Fleet Assets,   |
|       |               Route Optimization, Freight Modes, Corridor Status    |
|       |                                                                     |
|       +-- [5] FINANCIAL & ENTERPRISE VALUE AGENT                            |
|       |      Core Question: What is the economic consequence of this        |
|       |        decision?                                                    |
|       |      Purpose: Economic consequence modeling, NOT accounting         |
|       |      Outputs: Landed cost, working capital, cash impact,            |
|       |               margin impact, penalty exposure, expedite cost        |
|       |                                                                     |
|       +-- [6] RISK & RESILIENCE AGENT                                       |
|              Core Question: What systemic downside, constraint violation,   |
|                or cascading failure could this decision introduce?          |
|              Domains: External threats, Supplier concentration risk,        |
|                       Supplier financial distress, Geopolitical exposure,   |
|                       Quality failure propagation, Regulatory constraints,  |
|                       Network fragility, Cascade modeling                   |
|                                                                             |
+=============================================================================+
```

### Agent Design Rationale

| Agent | Why This Boundary |
| :--- | :--- |
| **Demand & Commerce** | Demand forecasting and commerce/pricing are tightly coupled. Promotional lift, price elasticity, cross-category cannibalization, and event-driven surges all feed directly into demand signals. |
| **Inventory & Asset** | Physical assets (cold-chain units, conveyors) directly determine inventory viability. A compressor failure in a cold-storage DC immediately threatens perishable inventory. |
| **Procurement & Supplier** | The V1 Supplier Agent ignores the commercial dimension -- contracts, price tiers, MOQ constraints, three-way match validation, and penalty enforcement. Enterprise scale demands dedicated procurement governance. |
| **Logistics & Transport** | Transport operations form a well-bounded domain. Scope retained from V1; engine transforms from rule-based to cognitive. |
| **Financial & Enterprise Value** | CD2F gates decisions on financial exposure thresholds. The NetBenefit calculation requires cross-domain cost impact data. Financial reasoning is structurally absent without this agent. |
| **Risk & Resilience** | 200 suppliers with varying geopolitical exposure, 554 regional weather events in the dataset, and quality/compliance failures that cascade rapidly through the supply chain. |

### Ownership Collision Resolution

| Domain | Procurement Owns | Risk Owns |
| :--- | :--- | :--- |
| Supplier Performance | OTIF, lead time, defect rate, capacity | -- |
| Supplier Commercial | Contracts, MOQ, price tiers, payment terms | -- |
| Supplier Financial Health | -- (consumes Risk's output) | Financial distress, credit risk, bankruptcy probability |
| Supplier Concentration | -- | Systemic single-supplier risk |
| Geopolitical Exposure | -- | Per-supplier/per-region geopolitical risk score |
| Quality/Compliance | -- | Inspection results, regulatory violations, recall propagation |

### Coordinator Responsibilities and Strict Role Discipline

The Coordinator is the meta-orchestrator implemented as a LangGraph state machine. It is STRICTLY NOT an agent. It possesses zero epistemic authority and must never be permitted to drift into a "seventh specialist".

```
COORDINATOR STRICT CODE-LEVEL PROHIBITIONS:
1. NEVER generates or asserts domain claims or beliefs.
2. NEVER generates recommendations, domain evaluations, or qualitative opinions.
3. NEVER proposes domain candidate actions. It instantiates the baseline
   'do_nothing' action and executes the mechanical combination synthesis subroutine
   (Section 29, Step 8), but creates zero novel domain action intents.
4. NEVER evaluates trade-offs or ranks candidates using internal heuristics.
5. NEVER communicates directly with human operators during deliberation
   (all interactions route through the Deliberation Table and D9).
```

| Responsibility | Description |
| :--- | :--- |
| **Deliberation Table Management** | Creates sessions, posts items, allocates sequence numbers, manages lifecycle |
| **Domain Affinity Routing** | Computes probabilistic affinity scores, assigns specialist agents |
| **Tier-1 RAG Pre-Retrieval** | Broad, shallow context retrieval for base context package (< 50ms) |
| **Capability Resolution** | Invokes Dynamic Capability Registry to bind tools per agent per task |
| **Cross-Examination Mediation** | Routes targeted critiques between conflicting agents via the table |
| **Evidence Sufficiency Gating** | Enforces tiered evidence checks (individual hard-critical validation) before simulation |
| **Candidate Pipeline Governance** | Runs normalization, dedup, synthesis subroutine, revalidation, and budget |
| **Twin Simulation Dispatch** | Validates CandidateAdmissionSeal, dispatches manifests to Digital Twin |
| **Arbitration Submission** | Assembles verified candidate package and submits to CD2F pure computation |
| **Snapshot Epoch Allocation** | Atomically allocates common snapshot epochs across all session actors |
| **Audit Emission** | Emits complete deliberation transcript to Kafka outbox and D9 |

---

## 10. Agent Ownership Contracts

Every agent's Agent Card V2 includes a machine-enforceable DomainOwnershipPolicy. Validated at startup against the ClaimTypeRegistry and ActionRegistry.

```python
class DomainOwnershipPolicy(BaseModel):
    """Machine-enforceable ownership boundaries for each agent.
    Validated by the Coordinator before posting proposals."""
    
    owned_entity_types: list[str]
    owned_metric_types: list[str]
    owned_claim_types: list[str]       # Must be in ClaimTypeRegistry
    
    permitted_action_types: list[str]  # Must be in ActionRegistry
    
    consumes_from: dict[str, list[str]]  # {agent_id: [claim_types]}
    
    forbidden_claim_types: list[str]
    forbidden_action_types: list[str]
```

### Enforcement Mechanism

```
Agent produces AgentProposal
    |
    v
Coordinator validates against DomainOwnershipPolicy:
    
    For each claim in proposal.claim:
        If claim.claim_type in agent.ownership.forbidden_claim_types:
            -> REJECT proposal with AGENT_OWNERSHIP_VIOLATION
            -> Request revised output from agent
    
    For each action in proposal.candidate_actions:
        If action.action_type not in agent.ownership.permitted_action_types:
            -> REJECT action (remove from proposal)
            -> Log ownership boundary violation
    
    If proposal passes validation:
        -> Post to Deliberation Table
```

Per-agent ownership contract definitions specify the strict bindings between each specialist, their owned claim types, permitted candidate actions, and consumed evidence classes as governed by the ClaimTypeRegistry (Section 5) and ActionRegistry (Section 7).

---

## 11. Agent Cognitive Runtime: Hybrid ML + LLM

Each agent runs a bounded reasoning chain combining traditional ML pipelines with LLM reasoning.

```
+=============================================================================+
|                    HYBRID AGENT COGNITIVE RUNTIME                           |
+=============================================================================+
|                                                                             |
|  [TRADITIONAL ML PIPELINE]           [BOUNDED LLM REASONING]                |
|  - XGBoost / LightGBM                - Qualitative evidence synthesis       |
|  - Prophet / Statistical              - Cross-domain constraint reasoning   |
|  - GradientBoosting                   - Historical precedent interpretation |
|  - Deterministic Rule Engines         - Natural language explanation        |
|  - Domain-specific formulas           - Tool-calling (bounded)              |
|                                                                             |
|  OUTPUT: Quantitative values          OUTPUT: Qualitative reasoning         |
|          (ValueWithProvenance,                 (EpistemicType-tagged,       |
|           source=MODEL_PREDICTION)              source=LLM_INTERPRETATION)  |
|                                                                             |
|  +-------+     +--------+     +--------+     +------------------+           |
|  |  ML   |---->| CONTEXT|---->|BOUNDED |---->| AgentProposal    |           |
|  | Output|     | FUSION |     |REASONER|     | (Claim + Actions)|           |
|  +-------+     +--------+     +--------+     +------------------+           |
|       ^             ^              |                                        |
|       |             |              | Max iterations: 3                      |
|       |        RAG context         | Max tool calls: 5                      |
|       |        + Base ctx          | Hard timeout: 80% of SLA budget        |
|       |                            | Schema validation on every output      |
|       |                            | Deterministic fallback if LLM fails    |
|  Domain ML models                                                           |
+=============================================================================+
```

### Bounded Reasoning Constraints

| Constraint | Value | Rationale |
| :--- | :--- | :--- |
| Max tool call iterations | 3 (configurable) | Prevents tool-call explosion |
| Max reasoning steps | 5 | Prevents unpredictable loops |
| Hard timeout per chain | 80% of SLA budget | Leaves 20% for output parsing + posting |
| Schema validation | Every output | Rejects malformed claims immediately |
| Deterministic fallback | ML-only output with reduced confidence | If LLM fails, agent still produces valid output |
| Temperature | 0.1 | Low temperature for deterministic reasoning |

### Critical Rule: LLMs Do Not Calculate

```
OBSERVED_VALUE   --> comes from PostgreSQL read      (Level 1)
COMPUTED_VALUE   --> comes from deterministic formula  (Level 2)
PREDICTED_VALUE  --> comes from ML model output        (Level 3)
SIMULATED_VALUE  --> comes from Twin projection        (Level 4)
LLM_INTERPRETATION --> interprets the above values     (Level 6)
```

The LLM interprets, synthesizes, and explains. It does NOT produce authoritative numerical values. If the only source for a critical number is LLM reasoning, the evidence quality assessment reduces the claim's authority and CD2F applies an uncertainty penalty.

---

## 12. LLM Strategy

The architecture freezes the INTERFACE, not the model. Model selection is deferred to D10 evaluation.

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

Ollama is the recommended MVP deployment (Docker service, CPU/GPU fallback). But agent code interacts with `ReasoningService`, not Ollama directly. Swapping to vLLM, TGI, or a cloud API requires changing config, not code.

### Model Selection Criteria (D10 Evaluates)

| Criterion | Measurement |
| :--- | :--- |
| Structured-output reliability | % of outputs that parse correctly into schema |
| Tool-call reliability | % of tool calls with valid parameters |
| Numerical reasoning | Error rate on domain-specific calculations |
| Hallucination rate | % of claims not supported by provided evidence |
| Latency | p50, p95, p99 inference time |
| Context length | Maximum effective context window |
| Reproducibility | Variance across identical prompts |

---

## 13. Memory Architecture

LangChain conversation memories are NOT used. Memory is SCOF-native.

| Memory Need | Source | NOT |
| :--- | :--- | :--- |
| Current decision session context | Deliberation Table (PostgreSQL + Redis) | NOT ConversationBufferMemory |
| Historical decision precedents | pgvector semantic embeddings (D9 archival) | NOT ConversationSummaryMemory |
| Workflow checkpoint/resume | LangGraph checkpoint store | -- |
| Enterprise facts | PostgreSQL D2 System of Record | -- |
| Topology context | Neo4j bounded graph traversals | -- |
| Real-time signals | Redis ephemeral cache | -- |
| Agent evaluation history | D10 structured evaluation store | NOT pgvector similarity |

LangChain is a consumer/orchestrator of these memories, not the owner.

---

# PART IV: EVIDENCE AND RETRIEVAL LAYER (D5)

---

## 14. Evidence Architecture

### Evidence Item Schema

Every piece of evidence carries a full provenance chain:

```python
class EvidenceItem(BaseModel):
    """An atomic unit of evidence used in reasoning."""
    
    evidence_id: str
    source_type: Literal[
        "postgresql", "neo4j", "pgvector", "redis",
        "ml_model", "twin_simulation", "llm",
    ]
    source_ref: str
    retrieved_at: datetime
    data_as_of: datetime
    query_hash: str
    authority: EvidenceAuthority
    freshness_score: float
```

### Proposition-Specific Evidence Authority

Authority depends on WHAT is being claimed. The global linear hierarchy from the initial plan is replaced with a claim-type-dependent authority model.

```
CURRENT-STATE CLAIM ("Inventory at DC-003 is 500 units"):
    1. PostgreSQL (System of Record) -- AUTHORITATIVE
    2. Neo4j projection (check projection_version)
    3. Redis cache (check cache_version)
    4. LLM interpretation -- NON-AUTHORITATIVE
    Conflict resolution: PostgreSQL wins. Always.

TOPOLOGICAL CLAIM ("DC-003 supplies stores S-101, S-102"):
    1. Neo4j projection -- AUTHORITATIVE (this IS its purpose)
    2. PostgreSQL source tables (reference)
    3. LLM interpretation -- NON-AUTHORITATIVE
    Conflict resolution: Neo4j wins for topology.

FORECAST CLAIM ("Demand will increase 35% next quarter"):
    1. Validated ML model (with known accuracy metrics)
    2. Historical precedent (pgvector match with confirmed outcome)
    3. LLM estimation -- NON-AUTHORITATIVE
    Conflict resolution: ML model wins if calibration_score > 0.60.

COUNTERFACTUAL CLAIM ("If we reroute, inventory at T+7 will be 380"):
    1. Twin simulation -- AUTHORITATIVE (this IS its purpose)
    2. Deterministic calculation (cost formulas)
    3. Heuristic estimate
    4. LLM speculation -- NON-AUTHORITATIVE
    Conflict resolution: Twin simulation wins.

COMPUTED-DERIVATION CLAIM ("$128,421 landed cost"):
    1. Deterministic formula from Level-1 inputs -- AUTHORITATIVE
    2. ML approximation
    3. LLM arithmetic -- NON-AUTHORITATIVE
    Conflict resolution: Deterministic formula wins.
```

### Value With Provenance

All numerical values in agent outputs carry their source:

```python
class ValueWithProvenance(BaseModel):
    value: float
    source: EvidenceAuthority
    source_ref: str
    timestamp: datetime
    computation: Optional[str]  # For COMPUTED_DERIVATION: the formula used
```

### Epistemic Boundaries

```python
class EpistemicType(str, Enum):
    OBSERVATION = "OBSERVATION"
    PREDICTION = "PREDICTION"
    CONSTRAINT = "CONSTRAINT"
    RISK_ASSESSMENT = "RISK"
    RECOMMENDATION = "RECOMMENDATION"
    COUNTERFACTUAL = "COUNTERFACTUAL"
```

---

## 15. Agentic RAG: Two-Tier MCP-Governed Retrieval

```
+=============================================================================+
|                    TWO-TIER RAG RETRIEVAL MODEL                             |
+=============================================================================+
|                                                                             |
|  TIER 1: COORDINATOR PRE-RETRIEVAL (Broad, Shallow)                         |
|  +-----------------------------------------------------------------+        |
|  | Blast radius scan (Neo4j, max_hops=1)                           |        |
|  | High-level precedent scan (pgvector, top_k=2, no agent filter)  |        |
|  | Current state snapshot (PostgreSQL, summary metrics only)       |        |
|  | Output: Base Context Package sent with every agent assignment   |        |
|  | SLA: < 50ms total (no LLM, pure DB queries via MCP)             |        |
|  +-----------------------------------------------------------------+        |
|                              |                                              |
|                              v                                              |
|  TIER 2: AGENT DEEP RETRIEVAL (Narrow, Deep, Domain-Specific)               |
|  +-----------------------------------------------------------------+        |
|  | Domain-filtered precedent search (pgvector via MCP, top_k=5)    |        |
|  | Deep graph traversal (Neo4j via MCP, max_hops=2)                |        |
|  | Detailed factual state (PostgreSQL via MCP tools)               |        |
|  | Ephemeral signal check (Redis, DIRECT access)                   |        |
|  | Domain-specific re-ranking weights applied                      |        |
|  | Output: Domain-Specific Deep Context for LLM reasoning          |        |
|  | SLA: < 100ms total (parallel queries)                           |        |
|  +-----------------------------------------------------------------+        |
+=============================================================================+
```

### Domain-Specific Re-Ranking Weights

| Agent | Re-ranking Priority |
| :--- | :--- |
| Demand & Commerce | Factual (0.35) > Precedent (0.30) > Topological (0.20) > Real-time (0.15) |
| Inventory & Asset | Factual (0.35) > Real-time (0.25) > Topological (0.25) > Precedent (0.15) |
| Procurement & Supplier | Topological (0.30) > Factual (0.30) > Precedent (0.25) > Real-time (0.15) |
| Logistics & Transport | Topological (0.35) > Real-time (0.25) > Factual (0.25) > Precedent (0.15) |
| Financial & Enterprise Value | Factual (0.40) > Precedent (0.25) > Topological (0.20) > Real-time (0.15) |
| Risk & Resilience | Real-time (0.35) > Topological (0.25) > Precedent (0.25) > Factual (0.15) |

### MCP-Governed Retrieval Architecture

```
             AGENT
               |
    Domain Retrieval Policy (agent-internal strategy)
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

**Why MCP-governed:** Every retrieval is a traceable MCP tool invocation. Dynamic Capability Registry controls per-agent retrieval capabilities. Connection pool management is centralized.

**Why Redis is exempt:** Sub-millisecond key-value reads. MCP JSON-RPC overhead exceeds the lookup itself. Audited via application-level logging.

---

## 16. Two-Class Retrieval Model

```
CLASS 1: CONTROLLED SYNCHRONOUS RETRIEVAL (MCP-governed)
    - Full JSON-RPC round-trip to MCP server
    - Audit-traced via MCP tool invocation log
    - Used for: initial queries, complex joins, graph traversals
    - Latency budget: < 20ms per call

CLASS 2: LOCAL HOT-PATH RETRIEVAL (in-process read-through cache)
    - First retrieval: MCP call (audit-traced, result cached)
    - Subsequent retrievals of same entity: in-process cache hit
    - Cache scope: single agent reasoning chain within single session
    - Cache key: (session_id, agent_id, entity_type, entity_id)
    - Cache eviction: automatic at end of agent reasoning chain
    - NOT a long-lived cache, NOT cross-session
```

---

# PART V: ORCHESTRATION AND DELIBERATION LAYER (D6)

---

## 17. LangGraph Orchestration Kernel

**LangGraph** = macro workflow orchestration (state machine, cycles, branching)
**LangChain** = agent-level cognitive components (prompts, tools, output parsing)

```
+-----------------------------------------------------------------------------------------------+
|                        LANGGRAPH MACRO-ORCHESTRATION STATE MACHINE                            |
+-----------------------------------------------------------------------------------------------+
                                                |
                                                v
                                     [  ingest_and_route  ]
                                                |
                                                v
                                 [  create_decision_snapshot  ]
                                 (Allocate Snapshot Epoch)
                                                |
                                                v
                                   [  tier1_rag_preretrieval  ]
                                 (Broad & Shallow Base Package)
                                                |
                                                v
                                      [  capability_bind  ]
                                 (Resolve Dynamic MCP Tools)
                                                |
                                                v
                                    [  parallel_fan_out  ]
                                 (Independent Agent Reasoning)
                                                |
                                                v
                                     [  fan_in_collate  ]
                                 (Assemble Deliberation Table)
                                                |
                                                v
                                    [  cross_examination  ]
                                 (Targeted Conflict Critiques)
                                                |
                                                v
                                   /-------------------------\
                                  <   blocking_critiques?     >
                                   \-------------------------/
                                                |
                       +------------------------+------------------------+
                       | YES (Max 2 Rounds)                              | NO
                       v                                                 v
             [  revision_round  ]                          [  evidence_sufficiency_gate  ]
                       |                                   (Individual HARD_CRITICAL Check)
                       v                                                 |
             [  fan_in_revised  ]                                        v
                       |                                       /-------------------\
                       +-------------------------------------><   sufficiency tier?   >
                                                               \-------------------/
                                                                         |
                      +----------------------------------+---------------+----------------------------------+
                      | INSUFFICIENT                     | MARGINALLY_SUFFICIENT                            | SUFFICIENT
                      v                                  v                                                  v
            [  hitl_escalation  ]              [  flag_degraded_scope  ]                        [  candidate_extraction  ]
                      |                                  |                                                  |
                      v                                  +--------------------------------------------------+
                 ((  END  ))                                                                |
                                                                                            v
                                                                             [  candidate_normalization  ]
                                                                             (Schema, Entity, T1 & T2 Impact,
                                                                              Hard Constraints, Dedup, Prune)
                                                                                            |
                                                                                            v
                                                                             [  combination_synthesis  ]
                                                                             (Generate Non-Conflicting Composites)
                                                                                            |
                                                                                            v
                                                                             [  revalidate_composites  ]
                                                                             (Re-check Schema, Entities, Constraints,
                                                                              Joint Impact, Dedup for Composites)
                                                                                            |
                                                                                            v
                                                                             [  candidate_budget_select  ]
                                                                             (UCB Heuristic + Baseline & Domains)
                                                                                            |
                                                                                            v
                                                                             [  stamp_admission_seals  ]
                                                                             (Seal: Must Pass All Gates for Twin)
                                                                                            |
                                                                                            v
                                                                               /-------------------------\
                                                                              <   twin_simulation_req?    >
                                                                               \-------------------------/
                                                                                            |
                                              +---------------------------------------------+------------------------------------+
                                              | REQUIRED / RECOMMENDED                                                           | ADVISORY / NOT NEEDED
                                              v                                                                                  |
                                     [  twin_dispatch  ]                                                                         |
                                              |                                                                                  |
                                              v                                                                                  |
                                      [  twin_collect  ]                                                                         |
                                              |                                                                                  |
                                              v                                                                                  |
                                   /---------------------\                                                                       |
                                  <  unexpected_outcome?  >                                                                      |
                                   \---------------------/                                                                       |
                                              |                                                                                  |
                             +----------------+----------------+                                                                 |
                             | YES (First Time)                | NO / Re-sim Done                                                |
                             v                                 v                                                                 |
               [  targeted_re_deliberation  ]                  +------------------------------------------------+                |
                             |                                                                                  |                |
                             v                                                                                  v                v
                 [  re_normalize_candidates  ]                                                      [  cd2f_vector_pareto_calc  ]
                             |                                                                      (Dominance on Metric Vector U(c))
                             v                                                                                  |
                    [  re_simulate_twin  ]                                                                      v
                             |                                                                      [  cd2f_frontier_resolution  ]
                             +--------------------------------------------------------------------> (Apply Policy Weights & Uncertainty)
                                                                                                                |
                                                                                                                v
                                                                                                    [  return_decision_result  ]
                                                                                                    (CD2F Pure Computation Complete)
                                                                                                                |
                                                                                                                v
                                                                                                      /-------------------\
                                                                                                     <   resolution tier?  >
                                                                                                      \-------------------/
                                                                                                                |
                        +----------------------------------+------------------------------------+---------------+-----------------------------------+
                        | SINGLETON / POLICY_WEIGHT        | TIER_2 (Extended Deliberation)     | GENUINE_PARETO_AMBIGUITY          | NO_FEASIBLE_ACTION
                        v                                  v                                    v                                   v
             [  execution_policy_check  ]        [  parallel_fan_out  ]                       [  hitl_tradeoff_summary  ]         [  hitl_escalation  ]
                        |                        (Cycle, Max 1)                                         |                                   |
                        v                                                                               v                                   v
             [  state_revalidation  ]                                                              ((  AWAIT_HUMAN  ))                 ((  END  ))
              (Detect Epoch Drift)                                                                      |
                        |                                                                               v
                        v                                                                      [  archive_record  ]
                 /--------------\                                                                       |
                <   state valid? >                                                                      v
                 \--------------/                                                                  ((  END  ))
                        |
            +-----------+-----------+
            | VALID                 | STALE / MATERIAL DRIFT
            v                       v
    [  execute_adapter  ]   [  trigger_replan  ]
            |                       |
            v                       v
    [  archive_record  ]   [  advance_snapshot  ]
            |                       |
            v                       v
       ((  END  ))          [  parallel_fan_out  ]
```

---

## 18. Coordinator Service Decomposition

The Coordinator remains a single logical component but its internals are decomposed into independently testable services.

```
Coordinator (LangGraph State Machine)
    |
    +-- RoutingService
    |     Input:  disruption event, agent cards
    |     Output: domain affinity scores, agent assignments
    |
    +-- DeliberationService
    |     Input:  session requests, agent verdicts
    |     Output: session lifecycle events, item management
    |
    +-- EvidenceSufficiencyService
    |     Input:  agent proposals, evidence items, policy
    |     Output: EvidenceSufficiencyAssessment
    |
    +-- CandidateService
    |     Input:  agent proposals
    |     Output: normalized candidate set
    |
    +-- SimulationDispatchService
    |     Input:  candidate set, DecisionSnapshot
    |     Output: SimulationManifests, dispatched to Twin
    |
    +-- AuditService
    |     Input:  all deliberation events
    |     Output: complete decision trace
    |
    +-- ExecutionPolicyService
          Input:  ApprovedDecision, ExecutionPolicy, context
          Output: ExecutionAuthorization
```

---

## 19. Deliberation Table: Event-Sourced Cognitive Workspace

### Core Rules

1. **No agent communicates with another agent directly.** Every interaction passes through the table, mediated by the Coordinator.
2. **The table is a decision-workspace, NOT a source of enterprise truth.** It stores decision artifacts (claims, critiques, verdicts). It does NOT replicate operational state.
3. **The Coordinator is chairperson.** Agents observe the table. They respond ONLY when assigned.

### Event Sourcing

```
EVENTS are the source of truth (immutable, append-only).
VIEWS are derived state (materialized projections for fast reads).
```

### Deliberation Event Schema

```python
class DeliberationEvent(BaseModel):
    """Immutable event. Stored in PostgreSQL (append-only).
    Distributed via Kafka (outbox). Materialized in Redis."""
    
    event_id: str
    session_id: str
    sequence_number: int           # Monotonically increasing within session
    
    event_type: Literal[
        "SESSION_STARTED", "SNAPSHOT_BOUND", "ITEM_POSTED", "ITEM_SCOPED",
        "AGENTS_ASSIGNED", "PROPOSAL_SUBMITTED", "CRITIQUE_SUBMITTED",
        "REVISION_SUBMITTED", "ENDORSEMENT_SUBMITTED",
        "EVIDENCE_GATE_EVALUATED", "CANDIDATE_EXTRACTED",
        "CANDIDATE_NORMALIZED", "SIMULATION_DISPATCHED",
        "SIMULATION_COMPLETED", "RE_DELIBERATION_TRIGGERED",
        "CD2F_SUBMITTED", "DECISION_RESOLVED", "EXECUTION_AUTHORIZED",
        "EXECUTION_COMPLETED", "SESSION_CLOSED", "SESSION_CANCELLED",
        "SESSION_EXPIRED",
    ]
    
    actor: str
    payload: dict
    timestamp: datetime
    causation_id: str
    correlation_id: str
```

### Event Sequence Allocation

The Coordinator is the ONLY component that allocates `sequence_number` values. Single-writer guarantee prevents sequence conflicts. Database-level enforcement provides a safety net:

```sql
ALTER TABLE deliberation_events
    ADD CONSTRAINT uq_session_sequence UNIQUE (session_id, sequence_number);
ALTER TABLE deliberation_events
    ADD CONSTRAINT chk_sequence_positive CHECK (sequence_number > 0);
```

### Storage

```
PostgreSQL: deliberation_events (append-only, immutable, partitioned by session_id)
    --> Authority for replay and audit

Kafka: scof.deliberation.events (via outbox)
    Key: session_id (ordering within session)
    --> Transport and distribution

Redis: session:{session_id}:view (materialized projection)
    --> Fast reads for active sessions
    Cache key: {session_id}:{snapshot_epoch}:{sequence_number}
```

---

## 20. Domain Affinity Routing

```
STEP 1: HARD CAPABILITY ELIGIBILITY       [< 1ms]
    Can the agent answer this at all?
    If agent lacks required MCP tools -> cap score at 0.30 maximum

STEP 2: STATIC DISRUPTION-TYPE MAPPING    [< 5ms]
    Known disruption-to-domain lookup table
    If confidence >= 0.85 -> use directly (Fast-Path)

STEP 3: ENTITY/CONTEXT RELEVANCE          [< 5ms]
    Does the item reference entities in this agent's domain?

STEP 4: SEMANTIC SIMILARITY               [< 50ms, if needed]
    Only used for free-text queries or novel disruption types

STEP 5: LOAD/AVAILABILITY                 [< 1ms]
    Degraded agents get score penalty

STEP 6: THRESHOLD APPLICATION             [< 1ms]
    >= assigned_threshold (default 0.60) -> ASSIGNED
    >= optional_threshold (default 0.40) -> OPTIONAL
    < optional_threshold                  -> NOT NOTIFIED
```

---

## 21. Cross-Examination Governance

### Two-Phase Independence Protocol

```
PHASE 2: INITIAL INDEPENDENT ASSESSMENT
    
    Each agent receives:
        + Base context package (Coordinator's Tier-1 RAG)
        + Their own deep retrieval results (Tier-2 RAG)
        + The disruption event description
        + DecisionSnapshot binding
    
    Each agent does NOT receive:
        - Other agents' claims
        - Other agents' evidence
        - Other agents' candidate actions
        - Other agents' confidence scores
    
    Purpose: Ensure INDEPENDENT initial assessment.

PHASE 3: TARGETED CROSS-EXAMINATION
    
    Each agent receives ONLY:
        - The specific claims from specific agents that conflict with
          or affect this agent's domain
        - NOT the full set of all claims
        - NOT other agents' confidence scores (prevents anchoring)
    
    Purpose: Structured conflict resolution without conformity bias.
```

### Termination Policy

```yaml
deliberation:
  max_cross_exam_rounds: 2
  max_critiques_per_agent: 3
  max_total_critiques_per_session: 18

  termination_conditions:
    - no_blocking_critiques
    - max_rounds_reached
    - candidate_set_unchanged
    - evidence_convergence
    - deadline_imminent
```

---

## 22. Evidence Sufficiency Gate

Multi-dimensional assessment with tiered criticality.

### Tiered Criticality Model

```python
class CriticalityTier(str, Enum):
    HARD_CRITICAL = "HARD_CRITICAL"
    """Absolute decision blocker if missing or stale."""
    
    DEGRADED_CRITICAL = "DEGRADED_CRITICAL"
    """Decision proceeds but with elevated uncertainty and reduced autonomy."""
    
    IMPORTANT = "IMPORTANT"
    """Affects decision quality but does not block."""
    
    SUPPLEMENTARY = "SUPPLEMENTARY"
    """Adds context but is not decision-critical."""
```

### Verdict Logic (Strict Precedence & Individual Critical Gate)

Critical evidence receives an **individual gate**. Aggregate freshness is only a supplementary quality signal and can never compensate for a stale or missing hard-critical fact.

```
INDIVIDUAL HARD-CRITICAL EVIDENCE CHECK:
    For every evidence item e requiring HARD_CRITICAL tier:
        assert e.present == True                          # Fact must be observed
        assert e.authority in AUTHORITATIVE_LEVELS        # Must come from authoritative source
        assert e.freshness >= policy.min_hard_critical_freshness  # Must satisfy freshness individually
        assert e.contradiction_status == "UNCONTRADICTED" # Cannot be contested by conflicting data

    hard_critical_all_met = (
        hard_critical_present == hard_critical_required
        AND all(e.freshness >= policy.min_hard_critical_freshness for e in hard_critical_items)
        AND all(e.authority in AUTHORITATIVE_LEVELS for e in hard_critical_items)
        AND not any(e.has_blocking_contradiction for e in hard_critical_items)
    )

INDIVIDUAL DEGRADED-CRITICAL EVIDENCE CHECK:
    degraded_critical_all_met = (
        degraded_critical_present == degraded_critical_required
        AND all(e.freshness >= policy.min_degraded_critical_freshness for e in degraded_critical_items)
    )

VERDICT PRECEDENCE RULES:

SUFFICIENT:
    hard_critical_all_met == True                      # ALL hard-critical pass individually
    AND degraded_critical_all_met == True              # ALL degraded-critical pass individually
    AND domain_coverage.coverage_score >= policy.min_domain_coverage
    AND evidence_quality.avg_evidence_freshness >= policy.min_evidence_freshness  # Supplementary aggregate
    AND consistency.contradiction_severity != "BLOCKING"
    AND evidence_quality.model_validity_score >= 0.50
    
    -> Full autonomous decision execution permitted (subject to ExecutionPolicy).

MARGINALLY_SUFFICIENT:
    hard_critical_all_met == True                      # HARD-CRITICAL MUST STILL PASS INDIVIDUALLY
    AND degraded_critical_present >= degraded_critical_required
    AND (
        degraded_critical_all_met == False             # Stale degraded-critical data accepted with penalty
        OR domain_coverage.coverage_score >= 0.60
    )
    AND consistency.contradiction_severity != "BLOCKING"
    
    -> Autonomy strictly capped at Tier-2. HITL notification issued. CD2F applies uncertainty penalty.

INSUFFICIENT:
    hard_critical_all_met == False                     # ANY single hard-critical item failing
    OR hard_critical_present < hard_critical_required  # ANY hard-critical fact missing
    OR consistency.contradiction_severity == "BLOCKING"# Unresolved data contradiction
    
    -> NO autonomous decision. Exploration and CD2F blocked. Mandatory HITL escalation.
```

**Non-Negotiable Semantic Invariant:**
The principle that `criticality != average evidence quality` is an absolute system invariant. Even if 99 supplementary evidence items have freshness `1.0`, a single HARD_CRITICAL fact with freshness `0.05` forces the verdict to `INSUFFICIENT`.

---

## 23. Priority and SLA: Two-Dimensional Model

### Business Priority

| Priority | Description | Operational Examples |
| :--- | :--- | :--- |
| **P0: Critical** | System emergency, safety risk, severe regulatory hazard | Cold-chain temperature breach, Tier-1 sole supplier shutdown |
| **P1: High** | Human operator escalation, active network disruption | Expedited ship request, CD2F Tier-3 trade-off escalation |
| **P2: Normal** | Routine multi-agent deliberation cycle | Standard replenishment rebalance, minor lead-time variance |
| **P3: Background** | Asynchronous analytics, network fragility scanning | Weekly supplier risk recalibration, demand curve drift scan |

### Execution SLA

| SLA Level | Description | Target Latency | Architectural Scope |
| :--- | :--- | :--- | :--- |
| **S0: Real-time** | Deterministic safety rules, zero LLM calls | < 100ms | Rule engine only, immediate fail-safe trigger |
| **S1: Interactive** | Interactive human console operator query | < 2s | Targeted Tier-1 context + fast deterministic path |
| **S2: Operational** | Standard multi-agent cognitive deliberation | < 5s per agent | Full hybrid ML + bounded LLM reasoning cycle |
| **S3: Analytical** | Batch, deep counterfactuals, background jobs | < 30s | Multi-horizon Digital Twin simulation rollout |

SLA values represent benchmark targets tested in D10. They are monitored via Kafka outbox timestamps.

### P0 Dual-Path Architecture and Strict Fast-Path Discipline

When a P0 critical event is ingested, the system branches immediately into dual pathways:

```
P0 Critical Event Ingested
         |
         +---------------------------------------+
         |                                       |
         v                                       v
+-------------------------------+   +------------------------------------------+
| FAST DETERMINISTIC PATH (S0)  |   | FULL COGNITIVE DELIBERATION PATH (S2)    |
| Latency: < 100ms (Zero LLM)   |   | Full 6-Stage Deliberation Pipeline       |
| Role: DETECT, PROTECT,        |   | Role: Comprehensive Multi-Objective      |
|       FREEZE, ESCALATE        |   |       Optimization & Root-Cause Resolute |
| Scope: Protective Rule Only   |   | Scope: Evaluates full trade-off set      |
+-------------------------------+   +------------------------------------------+
```

**Strict Fast-Path Behavioral Bounds:**
The Fast Deterministic Path is **strictly a safety and containment mechanism**, NOT an autonomous optimization engine. It is explicitly prohibited from competing with CD2F.
1. Permitted fast-path actions are strictly confined to the closed protective vocabulary:
   - **DETECT:** Register physical boundary breach or sensor anomaly.
   - **PROTECT:** Enforce immediate containment (e.g. `quarantine_inventory`, `compliance_hold`).
   - **FREEZE:** Suspend pending dispatches on affected lanes or purchase orders.
   - **ESCALATE:** Alert human incident commander and dispatch P0 deliberation session.
2. The Fast Path NEVER executes multi-objective optimization, route re-planning, or commercial re-sourcing. Those decisions require cross-domain trade-off analysis and remain the sole authority of CD2F.

---

## 24. Decision Snapshot and Temporal Consistency

All agents in a decision session reason over the same world-state. Consistency is enforced via a common `snapshot_epoch` coordinate, not via heterogeneous LSN arithmetic.

```python
class DataProjectionStatus(BaseModel):
    projection_name: str
    projection_epoch: int
    last_materialized_at: datetime
    native_position: Optional[str]   # For monitoring only, NOT for consistency math

class DecisionSnapshot(BaseModel):
    snapshot_epoch: int              # Monotonically increasing, atomically allocated
    
    trigger_event_id: str
    trigger_event_timestamp: datetime
    observation_cutoff: datetime
    
    projections: list[DataProjectionStatus]
    consistency_class: Literal[
        "FULLY_CONSISTENT",
        "ACCEPTABLE_LAG",
        "STALE_PROJECTION",
    ]
    
    max_fact_age_minutes: int
    max_model_age_hours: int
    max_precedent_age_days: int
```

### Freshness Computation

Freshness is ALWAYS relative to the decision's observation boundary. WALL_CLOCK is removed. Post-snapshot evidence raises an error.

```python
def compute_fact_freshness(data_as_of: datetime, snapshot: DecisionSnapshot) -> float:
    if data_as_of > snapshot.observation_cutoff:
        raise PostSnapshotEvidenceError(
            "Post-snapshot evidence must be rejected by upstream validator"
        )
    
    fact_age = snapshot.observation_cutoff - data_as_of
    max_age = timedelta(minutes=snapshot.max_fact_age_minutes)
    
    if fact_age == timedelta(0):
        return 1.0
    if fact_age >= max_age:
        return 0.0
    return 1.0 - (fact_age / max_age)
```

### Snapshot Advancement Policy

Partial agent restart is PROHIBITED. If snapshot advancement is needed, ALL agents re-reason from the new snapshot.

```yaml
snapshot_advancement:
  max_snapshot_advancements: 3
  advancement_guard_window_seconds: 30
  advancement_escalation: HITL
```

---

## 25. Session State Machine

```
+-----------------------------------------------------------------------------+
|                      SESSION STATE TRANSITION TOPOLOGY                      |
+-----------------------------------------------------------------------------+

                  [Session Initialized via Ingest Trigger]
                                     |
                                     v
                          +--------------------+
                          |      CREATED       |
                          +--------------------+
                                     |
                      +--------------+--------------+
                      |                             |
                      | (Snapshot Allocated)        | (Trigger Rejected / Aborted)
                      v                             v
           +--------------------+        +--------------------+
           |       ACTIVE       |        |     CANCELLED      |
           +--------------------+        +--------------------+
                      |                   (Terminal Absorbing)
           +----------+----------+
           |                     |
           | (Normal Completion) | (SLA Hard Timeout Breach)
           v                     v
   +--------------------+ +--------------------+
   |       CLOSED       | |      EXPIRED       |
   +--------------------+ +--------------------+
   (Terminal Absorbing)   (Terminal Absorbing)
```

```python
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "CREATED":   {"ACTIVE", "CANCELLED"},
    "ACTIVE":    {"CLOSED", "CANCELLED", "EXPIRED"},
    "CLOSED":    set(),    # Absorbing state
    "CANCELLED": set(),    # Absorbing state
    "EXPIRED":   set(),    # Absorbing state
}

TERMINAL_STATES = {"CLOSED", "CANCELLED", "EXPIRED"}
```

State transitions and event insertion MUST occur in a single database transaction with `FOR UPDATE` lock on the session row.

---

# PART VI: DECISION OBJECT MODEL

---

## 26. Agent Output Model

```python
class StructuredClaim(BaseModel):
    """What the agent BELIEVES, with evidence."""
    observations: list[ClaimElement]
    predictions: list[ClaimElement]
    risks: list[ClaimElement]
    constraints: list[ClaimElement]

class CandidateAction(BaseModel):
    """What the agent PROPOSES to do.
    action_type is DERIVED from intent to prevent inconsistency."""
    
    action_id: str
    intent: ActionIntent              # Agent-provided: WHAT to do
    impact: Optional[ActionImpactEnvelope]  # System-computed: WHAT it costs
    impact_computed: bool = False
    supporting_claims: list[str]
    evidence: list[EvidenceItem]
    proposer_agent_id: str
    
    @property
    def action_type(self) -> str:
        return self.intent.action_type
```

---

## 27. ActionIntent / ActionImpact Separation

ActionIntent schemas contain **decision parameters**: identifiers, modes, and decision quantities. They do NOT contain **impact estimates**: cost deltas, lead time deltas, service level projections. Impact estimates are computed by the ImpactEvaluationService and the Digital Twin.

```
DECISION PARAMETERS (permitted in ActionIntent):
    quantity: 500
    target_days_of_supply: 14.0
    new_supplier_id: "SUP-042"
    freight_mode: "air"

IMPACT ESTIMATES (PROHIBITED in ActionIntent):
    incremental_cost_usd: 12400
    new_lead_time_days: 8.5
    service_level_improvement: 0.03
```

---

## 28. Three-Tier Impact Evaluation Model

```
TIER 1: BASELINE IMPACT (Authoritative Facts)
    Source: PostgreSQL, rate tables, contract terms
    Nature: Deterministic derivation
    Confidence: HIGH
    Used for: Hard constraint pre-check, dominance pruning (SAFE)

TIER 2: PREDICTIVE IMPACT ESTIMATE (Model-Based)
    Source: Validated domain models
    Nature: Statistical prediction with quantified uncertainty
    Confidence: MEDIUM
    Used for: UCB candidate budgeting, pre-Twin scoring (NOT for dominance pruning)

TIER 3: COUNTERFACTUAL IMPACT (Twin Simulation)
    Source: Digital Twin simulation
    Nature: Counterfactual projection
    Confidence: VARIABLE
    Used for: Final CD2F arbitration, Pareto frontier computation
```

```python
class ActionImpactEnvelope(BaseModel):
    action_id: str
    baseline: BaselineImpact
    predictive: Optional[PredictiveImpactEstimate]
    simulation: Optional[SimulationResult]
    baseline_computed: bool = False
    predictive_computed: bool = False
    simulation_computed: bool = False
```

---

## 29. Candidate Normalization and Budget Selection Pipeline

Candidate actions cannot bypass safety or impact safeguards through late-stage synthesis. Combination synthesis is positioned as a controlled candidate-generation subroutine at Step 8, immediately followed by Step 9: Mandatory Revalidation of Synthesized Candidates. Only candidates that successfully pass all 11 stages and receive a signed `CandidateAdmissionSeal` are eligible for Digital Twin simulation or CD2F arbitration.

### Canonical 11-Step Pipeline Specification

```
STEP 1: CANDIDATE EXTRACTION
    Collect atomic candidate actions from all revised specialist proposals on the Deliberation Table.
    Every candidate action must be bound to the session's active snapshot_epoch.

STEP 2: SCHEMA AND PARAMETER AUTHORITY VALIDATION
    Validate intent against the strictly typed ActionIntent schema registered for action_type.
    Verify action_type exists in the closed ActionRegistry.
    Verify proposing agent is enumerated in permitted_proposers.
    Verify all intent fields conform to parameter_authority (reject any impact estimates).

STEP 3: ENTITY EXISTENCE VALIDATION
    Verify all referenced entity IDs (SKUs, facilities, carriers, POs, lanes) exist in PostgreSQL
    as of the active snapshot_epoch. Reject phantom, deleted, or future entity references.

STEP 4: THREE-TIER IMPACT EVALUATION (PRE-SIMULATION)
    Compute Tier 1 BaselineImpact (from authoritative database facts, rate cards, inventory tables).
    Compute Tier 2 PredictiveImpactEstimate (from validated, calibrated domain models with uncertainty).
    LLM estimates are strictly prohibited from entering impact computation.

STEP 5: HARD-CONSTRAINT PRE-CHECK
    Eliminate candidates violating hard physical, regulatory, or policy constraints.
    Evaluated strictly against Tier 1 BaselineImpact values.
    If a candidate violates a hard constraint, it is immediately pruned with an audit record.

STEP 6: DEDUPLICATION
    Identify and merge semantically identical candidate actions proposed by different agents.
    Retain highest-reliability proposer provenance and merge corroborating evidence lists.

STEP 7: DOMINANCE PRUNING (SAFE BASELINE ONLY)
    A candidate c_b is pruned as dominated by c_a ONLY if:
        - Both candidates have complete Tier 1 BaselineImpact data.
        - c_a is strictly superior to c_b across ALL Tier 1 dimensions.
        - The dominance margin exceeds policy.dominance_safety_margin.
    Tier 2 PredictiveImpactEstimate is NEVER used for dominance pruning.

STEP 8: COMBINATION SYNTHESIS (CROSS-DOMAIN COMPOSITES)
    If multiple non-conflicting actions across complementary domains address the disruption:
    Synthesize candidate combinations typed strictly as `composite_action` (governed in ActionRegistry).
    Component actions must be drawn exclusively from candidates surviving Steps 1-7.
    Reject combinations with conflicting parameters (e.g., conflicting expedite vs cancel on same PO).

STEP 9: REVALIDATION OF SYNTHESIZED COMPOSITE CANDIDATES
    Synthesized composites CANNOT bypass pipeline validation. Every composite MUST pass:
    - 9A. Composite Schema Validation: Validate CompositeActionIntent and component list bounds.
    - 9B. Component Parameter Authority: Verify each component respects its domain authority.
    - 9C. Joint Entity Validation: Verify all referenced entities across all components exist at snapshot_epoch.
    - 9D. Joint Hard-Constraint Pre-Check: Verify combined physical and operational constraints
          (e.g., aggregate warehouse receiving capacity, total fleet vehicle limit).
    - 9E. Joint Impact Evaluation: Calculate combined Tier 1 BaselineImpact and joint Tier 2 PredictiveImpact.
    - 9F. Deduplication & Coherence Check: Eliminate duplicate combinations or cross-component mutual exclusions.

STEP 10: CANDIDATE BUDGET SELECTION (HEURISTIC)
    Rank all validated candidates (atomic and synthesized) using the UCB heuristic:
        UCB(c) = weighted_score(Tier 1 + Tier 2) + alpha * uncertainty(c)
    Coverage and Safety Invariants:
        - MANDATORY inclusion of Do-Nothing Baseline (c_0).
        - MANDATORY inclusion of at least one top candidate per participating domain.
        - Maximum admitted candidates: K_max = max_simulation_branches + 1 (baseline).

STEP 11: CANDIDATE ADMISSION SEAL CERTIFICATION
    Every candidate admitted to Digital Twin simulation or CD2F arbitration is stamped with
    a cryptographically verifiable CandidateAdmissionSeal.
    The Digital Twin simulation dispatcher and CD2F arbitration engine MUST reject any candidate
    lacking a valid CandidateAdmissionSeal.
```

### Candidate Admission Seal Contract

```python
class CandidateAdmissionStatus(str, Enum):
    ADMITTED_ATOMIC = "ADMITTED_ATOMIC"
    ADMITTED_COMPOSITE = "ADMITTED_COMPOSITE"
    REJECTED_SCHEMA = "REJECTED_SCHEMA"
    REJECTED_ENTITY = "REJECTED_ENTITY"
    REJECTED_HARD_CONSTRAINT = "REJECTED_HARD_CONSTRAINT"
    REJECTED_DOMINATED = "REJECTED_DOMINATED"
    REJECTED_BUDGET = "REJECTED_BUDGET"
    REJECTED_COMPOSITE_VALIDATION = "REJECTED_COMPOSITE_VALIDATION"

class CandidateAdmissionSeal(BaseModel):
    """Cryptographic seal proving a candidate action successfully passed all normalization gates."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    seal_id: str
    action_id: str
    session_id: str
    snapshot_epoch: int
    pipeline_version: str = "v2.0"
    admission_status: CandidateAdmissionStatus
    
    # Validation gates passed verification
    schema_validated: bool
    entity_validated: bool
    hard_constraints_passed: bool
    baseline_impact_computed: bool
    composite_revalidated: bool
    budget_selected: bool
    
    sealed_at: datetime
    seal_signature: str    # HMAC-SHA256 signature of (action_id + session_id + snapshot_epoch + status)

class CompositeActionIntent(ActionIntent):
    """Strict schema for cross-domain composite actions synthesized in Step 8."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    action_type: Literal["composite_action"] = "composite_action"
    composite_name: str
    component_action_ids: list[str]
    component_intents: list[ActionIntent]
    execution_coordination_mode: Literal["PARALLEL", "SEQUENTIAL_STRICT", "SEQUENTIAL_BEST_EFFORT"] = "PARALLEL"
    max_component_count: int = Field(default=4, le=6)

class CandidatePipelineService:
    """Orchestrates candidate extraction, validation, synthesis, revalidation, and admission sealing."""
    
    def __init__(self, action_registry: ActionRegistry, policy: DecisionPolicy):
        self.registry = action_registry
        self.policy = policy
    
    def validate_atomic_candidate(self, candidate: CandidateAction, snapshot_epoch: int) -> bool:
        """Executes Steps 2, 3, 4, 5 on atomic proposals."""
        entry = self.registry.get_entry(candidate.action_type)
        if candidate.proposer_agent_id not in entry.permitted_proposers:
            return False
        # Entity existence check against PostgreSQL at snapshot_epoch
        if not self._verify_entities_exist(candidate.intent, snapshot_epoch):
            return False
        # Hard constraint pre-check on Tier-1 baseline
        if not self._check_hard_constraints(candidate):
            return False
        return True
    
    def revalidate_composite_candidate(self, composite: CandidateAction, snapshot_epoch: int) -> bool:
        """Executes Step 9: Mandatory revalidation for synthesized composite candidates."""
        if composite.action_type != "composite_action":
            return False
        if not isinstance(composite.intent, CompositeActionIntent):
            return False
        
        intent: CompositeActionIntent = composite.intent
        if len(intent.component_intents) < 2 or len(intent.component_intents) > intent.max_component_count:
            return False
            
        # 9A & 9B: Verify each component adheres to ActionRegistry and parameter authority
        for sub_intent in intent.component_intents:
            entry = self.registry.get_entry(sub_intent.action_type)
            if not self._verify_parameter_authority(sub_intent, entry.parameter_authority):
                return False
                
        # 9C: Joint entity existence check at snapshot_epoch
        for sub_intent in intent.component_intents:
            if not self._verify_entities_exist(sub_intent, snapshot_epoch):
                return False
                
        # 9D: Joint hard-constraint check
        if not self._check_joint_hard_constraints(composite):
            return False
            
        # 9E: Joint Tier 1 baseline computation and joint Tier 2 predictive impact
        if not self._compute_joint_impact(composite):
            return False
            
        return True

    def stamp_admission_seal(self, candidate: CandidateAction, session_id: str, snapshot_epoch: int) -> CandidateAdmissionSeal:
        """Generates the cryptographically signed admission seal for compliant candidates."""
        is_composite = (candidate.action_type == "composite_action")
        status = CandidateAdmissionStatus.ADMITTED_COMPOSITE if is_composite else CandidateAdmissionStatus.ADMITTED_ATOMIC
        
        raw_token = f"{candidate.action_id}:{session_id}:{snapshot_epoch}:{status.value}"
        signature = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        
        return CandidateAdmissionSeal(
            seal_id=f"SEAL-{uuid4().hex[:12].upper()}",
            action_id=candidate.action_id,
            session_id=session_id,
            snapshot_epoch=snapshot_epoch,
            pipeline_version="v2.0",
            admission_status=status,
            schema_validated=True,
            entity_validated=True,
            hard_constraints_passed=True,
            baseline_impact_computed=True,
            composite_revalidated=is_composite,
            budget_selected=True,
            sealed_at=datetime.now(timezone.utc),
            seal_signature=signature
        )
```

---

# PART VII: COUNTERFACTUAL EVALUATION AND ARBITRATION (D7)

---

## 30. Digital Twin: Counterfactual Evaluator

Position: BEFORE CD2F (evaluates candidates, outcomes inform arbitration).

```python
class SimulationManifest(BaseModel):
    """Complete specification for a reproducible Twin simulation."""
    simulation_id: str
    session_id: str
    candidate_action_id: str
    baseline_snapshot_id: str
    scenario_id: str
    time_horizons: list[int]          # [7, 14, 28] days
    action_set_hash: str
    twin_model_version: str
    random_seed: int
    input_state_hash: str
```

### Twin State Authority Rule

```
AUTHORITATIVE:
    - Within the scope of THIS simulation ONLY
    - For counterfactual claims about THIS candidate action

NOT AUTHORITATIVE:
    - For enterprise operational state (Layer 1 / Layer 2)
    - For any other simulation branch
```

---

## 31. Twin Simulation Materiality and Requirement Classification

Single canonical definition of Twin simulation requirement thresholds.

```python
class SimulationMaterialityThresholds(BaseModel):
    # REQUIRED thresholds (ANY triggers REQUIRED)
    required_financial_exposure_usd: float = 200000.0
    required_cascade_potential: float = 0.70
    required_novelty_score: float = 0.80
    required_regulatory_relevance: bool = True
    
    # RECOMMENDED thresholds (ANY triggers RECOMMENDED)
    recommended_financial_exposure_usd: float = 10000.0
    recommended_service_impact: float = 0.15
    recommended_risk_exposure: float = 0.50
```

Classification: REQUIRED / RECOMMENDED / ADVISORY. If Twin is REQUIRED and times out, HITL escalation is mandatory (no autonomous CD2F).

---

## 32. CD2F Evidence-Based Arbitration Engine

CD2F is a **pure computation engine** that takes: (candidates + evidence + simulation results + policy) and produces: (selected action + justification + trade-off summary).

### What CD2F Does NOT Do

- Does NOT use LLM reasoning to select the winning candidate
- Does NOT generate new candidate actions
- Does NOT retrieve data
- Does NOT call the Twin
- Does NOT define what "good" means (policy defines it)
- Does NOT authorize execution (ExecutionPolicyService authorizes)

### Formal Mathematical Arbitration Process

Pareto dominance operates directly on the **multi-objective normalized metric vector** $U(c)$, preserving trade-off geometry across all dimensions. Policy scalar weighting and uncertainty penalties are applied **only to resolve non-dominated candidates on the Pareto frontier**.

```
STAGE 1: FEASIBILITY FILTER
    For each candidate c in AdmittedCandidates:
        Verify hard physical, regulatory, and policy constraints against Tier 1 baseline and Tier 3 simulation.
        If hard constraints are violated:
            Prune candidate c with explicit InfeasibilityReason.
    FeasibleSet = { c in AdmittedCandidates | c satisfies all hard constraints }
    
    If FeasibleSet is empty:
        Emit CD2F_NO_FEASIBLE_ACTION.
        Generate InfeasibilityDiagnosticReport (documenting violated constraints for each candidate).
        Halt autonomous selection -> Mandatory HITL Escalation.

STAGE 2: OBJECTIVE METRIC VECTOR EVALUATION
    For each candidate c in FeasibleSet:
        For each metric m in policy.objective_metrics:
            raw_val = extract_metric_value(c, m)
            u_m(c) = m.normalize(raw_val)   # Direction-aware: [-1.0, +1.0], where +1.0 is optimal
        Construct Objective Metric Vector:
            U(c) = [ u_1(c), u_2(c), ..., u_M(c) ] in [-1.0, 1.0]^M
    (Trade-off dimensionality is fully preserved. Collapsing into a scalar score at this stage is strictly forbidden).

STAGE 3: POINT-ESTIMATE PARETO FRONTIER COMPUTATION
    Compute the non-dominated Pareto frontier P subset of FeasibleSet based on objective vectors U(c):
    For candidates c_a, c_b in FeasibleSet:
        c_a dominates c_b (c_a >_P c_b) if and only if:
            (for all m in {1..M}: u_m(c_a) >= u_m(c_b)) AND (exists m in {1..M}: u_m(c_a) > u_m(c_b))
    
    The Pareto Frontier is defined as:
        P = { c in FeasibleSet | not exists c' in FeasibleSet such that c' >_P c }
    
    Cardinality Evaluation of Pareto Frontier P:
    
    Case A: |P| == 1 (Singleton Frontier)
        The frontier contains exactly one universally non-dominated candidate.
        Selected Action = only member c* in P.
        Frontier Classification = SINGLETON_PARETO_FRONTIER.
        Confidence Score = 1.0 - lambda * uncertainty(c*).
        Proceed directly to Stage 5.
    
    Case B: |P| > 1 (Multiple Pareto Candidates)
        Multiple candidates exhibit genuine dimensional trade-offs (no candidate dominates all others).
        Proceed to Stage 4 to resolve the frontier using policy weights and uncertainty penalties.

STAGE 4: FRONTIER RESOLUTION VIA POLICY UTILITY AND UNCERTAINTY
    Policy weights and uncertainty penalties are applied ONLY to rank candidates within frontier P:
    (Dominated candidates outside P are strictly excluded from scalar evaluation).
    
    For each candidate c in P:
        Calculate Policy Scalar Utility:
            J_policy(c) = SUM_{m=1..M} (w_m * u_m(c)) - soft_constraint_penalties(c)
            where w_m = policy.weights[m] and SUM(w_m) = 1.0.
        
        Apply Robust Uncertainty Penalty:
            J_final(c) = J_policy(c) - lambda * sigma_total(c)
            where:
                lambda = policy.uncertainty_aversion_factor (>= 0.0)
                sigma_total(c) = composite_uncertainty(c.tier1_variance, c.tier2_ci, c.tier3_variance, R_i_discount)
    
    Sort candidates in P by J_final(c) descending: [c_(1), c_(2), ..., c_(|P|)]
    Utility Delta: Delta_J = J_final(c_(1)) - J_final(c_(2))
    
    If Delta_J >= policy.tie_threshold_epsilon:
        Selected Action = c_(1).
        Frontier Classification = POLICY_WEIGHT_RESOLVED.
        Resolution Mechanism: Policy weights unambiguously differentiate the optimal trade-off.
        Proceed to Stage 5.
    Else:
        Selected Action = c_(1) (tentative recommendation).
        Frontier Classification = GENUINE_PARETO_AMBIGUITY.
        Resolution Mechanism: Candidates are materially tied within epsilon margin.
        Construct Trade-off Matrix comparing all members of P across individual dimensions u_m(c).
        Halt autonomous pipeline -> Mandatory HITL Escalation.

STAGE 5: RETURN DECISION RESULT
    Package DecisionResult containing:
        - decision_id, session_id, snapshot_epoch
        - selected_action (CandidateAction)
        - frontier_classification (SINGLETON_PARETO_FRONTIER / POLICY_WEIGHT_RESOLVED / GENUINE_PARETO_AMBIGUITY)
        - pareto_frontier_candidates (List of candidate IDs and objective vectors U(c))
        - evaluated_candidates (full audit trace of all candidates, feasibility status, U(c), J_final)
        - justification (machine-generated trade-off explanation and dominant metric drivers)
        - decision_confidence (derived from Delta_J, sigma_total, and agent reliability R_i)
    
    ARCHITECTURAL BOUNDARY ENFORCEMENT:
        CD2F SELECTS the winning candidate; it NEVER authorizes physical execution.
        Return DecisionResult to LangGraph Orchestrator.
        LangGraph dispatches DecisionResult to ExecutionPolicyService (Section 35) for independent authorization.
```

---

## 33. Direction-Aware Objective Normalization

```python
class ObjectiveMetricDefinition(BaseModel):
    name: str
    direction: Literal["MINIMIZE", "MAXIMIZE"]
    reference_scale: float
    weight: float
    saturation_policy: Literal["CLIP", "LOG_COMPRESS"] = "CLIP"
    
    def normalize(self, raw_value: float) -> float:
        """Direction-aware normalization.
        Output: [-1, +1]. Positive = GOOD. Negative = BAD.
        
        For MINIMIZE: negative raw = reduction (GOOD) -> positive normalized
        For MAXIMIZE: positive raw = improvement (GOOD) -> positive normalized"""
        
        normalized = raw_value / self.reference_scale
        
        if self.saturation_policy == "CLIP":
            normalized = max(-1.0, min(1.0, normalized))
        elif self.saturation_policy == "LOG_COMPRESS":
            sign = 1.0 if normalized >= 0 else -1.0
            normalized = sign * min(1.0, math.log1p(abs(normalized)))
        
        if self.direction == "MINIMIZE":
            return -normalized     # Flip: reduction is good
        else:
            return normalized      # Keep: improvement is good
```

---

## 34. Pareto Analysis and Confidence Labels

Pareto analysis in CD2F evaluates multi-dimensional trade-offs strictly in the vector space $U(c) = [u_1(c), u_2(c), \dots, u_M(c)]$, preserving trade-off geometry prior to any scalar ranking.

### Pareto Frontier Mathematical Definitions

1. **Vector Dominance:** For two feasible candidates $c_a, c_b \in \mathcal{F}$, candidate $c_a$ dominates candidate $c_b$ ($c_a \succ_P c_b$) if and only if:
   $$\forall m \in \{1, \dots, M\}: u_m(c_a) \ge u_m(c_b) \quad \land \quad \exists m \in \{1, \dots, M\}: u_m(c_a) > u_m(c_b)$$

2. **Pareto Frontier Set ($P$):** The non-dominated subset of feasible candidates:
   $$P = \{ c \in \mathcal{F} \mid \nexists c' \in \mathcal{F} \text{ such that } c' \succ_P c \}$$

3. **Frontier Resolution:** Scalar weighting is applied exclusively to candidates within $P$:
   $$J_{\text{policy}}(c) = \sum_{m=1}^M w_m u_m(c) - \text{penalties}(c)$$
   $$J_{\text{final}}(c) = J_{\text{policy}}(c) - \lambda \cdot \sigma_{\text{total}}(c)$$
   $$\Delta_J = J_{\text{final}}(c_{(1)}) - J_{\text{final}}(c_{(2)})$$

### Canonical Classification Labels

```
SINGLETON_PARETO_FRONTIER:
    The Pareto frontier P contains exactly one member (|P| = 1).
    Candidate c* is universally non-dominated across all evaluated dimensions.
    Selected unconditionally without requiring policy weighting. Highest decision confidence.

POLICY_WEIGHT_RESOLVED:
    The Pareto frontier contains multiple candidates (|P| > 1), but policy-weighted utility
    with uncertainty penalty clearly distinguishes a superior trade-off:
    Delta_J = J_final(c_(1)) - J_final(c_(2)) >= policy.tie_threshold_epsilon.
    The top candidate c_(1) is selected autonomously.

GENUINE_PARETO_AMBIGUITY:
    The Pareto frontier contains multiple candidates (|P| > 1), and the top candidates are
    materially tied within the policy indifference margin:
    Delta_J = J_final(c_(1)) - J_final(c_(2)) < policy.tie_threshold_epsilon.
    No objective basis exists to select autonomously without imposing arbitrary preferences.
    Halt autonomous execution; generate Trade-off Matrix comparing frontier members; escalate to HITL.

CD2F_NO_FEASIBLE_ACTION:
    All proposed candidates violate one or more hard physical, regulatory, or policy constraints (|F| = 0).
    Autonomous pipeline halts; diagnostic report generated; mandatory HITL escalation.
```

### Python Pareto Arbitration Implementation

```python
class ParetoFrontierClassification(str, Enum):
    SINGLETON_PARETO_FRONTIER = "SINGLETON_PARETO_FRONTIER"
    POLICY_WEIGHT_RESOLVED = "POLICY_WEIGHT_RESOLVED"
    GENUINE_PARETO_AMBIGUITY = "GENUINE_PARETO_AMBIGUITY"
    CD2F_NO_FEASIBLE_ACTION = "CD2F_NO_FEASIBLE_ACTION"

class ParetoCandidateVector(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    action_id: str
    objective_vector: dict[str, float]       # Normalized [-1.0, 1.0] per metric
    uncertainty: float                       # Total composite uncertainty
    is_dominated: bool = False
    dominated_by_action_id: Optional[str] = None
    policy_utility: Optional[float] = None
    final_score: Optional[float] = None

class ParetoArbitrationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    classification: ParetoFrontierClassification
    selected_action_id: Optional[str]
    frontier_action_ids: list[str]
    candidate_vectors: dict[str, ParetoCandidateVector]
    utility_delta: Optional[float] = None
    tradeoff_summary: str
    requires_hitl: bool

class ParetoArbitrationEngine:
    """Computes Pareto dominance on metric vectors and resolves frontier members via policy utility."""
    
    @staticmethod
    def compute_dominance(candidates: list[ParetoCandidateVector], metric_names: list[str]) -> list[ParetoCandidateVector]:
        """Calculates point-estimate vector Pareto dominance."""
        updated = [c.model_copy() for c in candidates]
        n = len(updated)
        
        for i in range(n):
            for j in range(n):
                if i == j or updated[i].is_dominated:
                    continue
                # Check if updated[j] dominates updated[i]
                u_i = updated[i].objective_vector
                u_j = updated[j].objective_vector
                
                j_weakly_better = all(u_j[m] >= u_i[m] for m in metric_names)
                j_strictly_better = any(u_j[m] > u_i[m] for m in metric_names)
                
                if j_weakly_better and j_strictly_better:
                    updated[i] = updated[i].model_copy(update={
                        "is_dominated": True,
                        "dominated_by_action_id": updated[j].action_id
                    })
                    break
        return updated

    @classmethod
    def arbitrate(
        cls,
        feasible_candidates: list[ParetoCandidateVector],
        metric_definitions: dict[str, ObjectiveMetricDefinition],
        weights: dict[str, float],
        uncertainty_aversion: float,
        tie_threshold_epsilon: float = 0.02
    ) -> ParetoArbitrationResult:
        if not feasible_candidates:
            return ParetoArbitrationResult(
                classification=ParetoFrontierClassification.CD2F_NO_FEASIBLE_ACTION,
                selected_action_id=None,
                frontier_action_ids=[],
                candidate_vectors={},
                tradeoff_summary="All candidates violate hard constraints. Feasible set is empty.",
                requires_hitl=True
            )
            
        metric_names = list(weights.keys())
        evaluated = cls.compute_dominance(feasible_candidates, metric_names)
        frontier = [c for c in evaluated if not c.is_dominated]
        vectors_by_id = {c.action_id: c for c in evaluated}
        
        # Case 1: Singleton Frontier
        if len(frontier) == 1:
            winner = frontier[0]
            return ParetoArbitrationResult(
                classification=ParetoFrontierClassification.SINGLETON_PARETO_FRONTIER,
                selected_action_id=winner.action_id,
                frontier_action_ids=[winner.action_id],
                candidate_vectors=vectors_by_id,
                utility_delta=None,
                tradeoff_summary=f"Candidate {winner.action_id} universally dominates all alternatives.",
                requires_hitl=False
            )
            
        # Case 2: Multi-candidate Frontier -> Apply Policy Utility & Uncertainty Penalty
        scored_frontier: list[tuple[float, ParetoCandidateVector]] = []
        for c in frontier:
            j_pol = sum(weights[m] * c.objective_vector[m] for m in metric_names)
            j_fin = j_pol - (uncertainty_aversion * c.uncertainty)
            
            updated_c = c.model_copy(update={"policy_utility": j_pol, "final_score": j_fin})
            vectors_by_id[c.action_id] = updated_c
            scored_frontier.append((j_fin, updated_c))
            
        scored_frontier.sort(key=lambda x: x[0], reverse=True)
        top_score, top_candidate = scored_frontier[0]
        runner_up_score, _ = scored_frontier[1]
        delta_j = top_score - runner_up_score
        
        frontier_ids = [c.action_id for _, c in scored_frontier]
        
        if delta_j >= tie_threshold_epsilon:
            return ParetoArbitrationResult(
                classification=ParetoFrontierClassification.POLICY_WEIGHT_RESOLVED,
                selected_action_id=top_candidate.action_id,
                frontier_action_ids=frontier_ids,
                candidate_vectors=vectors_by_id,
                utility_delta=delta_j,
                tradeoff_summary=(
                    f"Frontier resolved by policy weighting: {top_candidate.action_id} exceeds "
                    f"runner-up by delta={delta_j:.4f} (threshold={tie_threshold_epsilon:.4f})."
                ),
                requires_hitl=False
            )
        else:
            return ParetoArbitrationResult(
                classification=ParetoFrontierClassification.GENUINE_PARETO_AMBIGUITY,
                selected_action_id=top_candidate.action_id,  # Tentative recommendation
                frontier_action_ids=frontier_ids,
                candidate_vectors=vectors_by_id,
                utility_delta=delta_j,
                tradeoff_summary=(
                    f"Genuine Pareto ambiguity on frontier: top candidate {top_candidate.action_id} "
                    f"and runner-up differ by only delta={delta_j:.4f} < {tie_threshold_epsilon:.4f}. Escalating to HITL."
                ),
                requires_hitl=True
            )
```

---

## 35. Execution Authorization

```python
class ExecutionPolicyService:
    """SEPARATE from CD2F. Applies organizational execution policy."""
    
    def authorize(self, decision, policy, context) -> ExecutionAuthorization:
        if context in ("simulation", "benchmark"):
            return ExecutionAuthorization(authorization="SIMULATION_ONLY")
        
        if decision.selected_action.action_type in policy.hitl_required_action_types:
            return ExecutionAuthorization(authorization="HITL_REQUIRED")
        
        if decision.cost_impact > policy.max_autonomous_cost_usd:
            return ExecutionAuthorization(authorization="HITL_REQUIRED")
        
        return ExecutionAuthorization(authorization="AUTO_EXECUTE")
```

---

## 36. State Revalidation Before Execution

Runs AFTER ExecutionPolicy approval, BEFORE execution adapter. Detects stale authorizations via epoch comparison.

```python
class StateRevalidation(BaseModel):
    decision_id: str
    approved_snapshot_epoch: int
    current_snapshot_epoch: int
    epoch_drift: int
    critical_entity_changes: list[EntityChange]
    revalidation_result: Literal["VALID", "DEGRADED", "STALE"]
    execution_authorization: Literal["PROCEED", "PROCEED_WITH_FLAG", "REPLAN", "ESCALATE"]
```

---

# PART VIII: EVENT AND RUNTIME BACKBONE (D8)

---

## 37. State Authority Map

```
+===================================================================================================+
|                                     STATE AUTHORITY TOPOLOGY                                      |
+===================+=====================+=========================+===============================+
| Storage Layer     | Authority Class     | Managed Data Scopes     | Consistency & Failover Policy |
+===================+=====================+=========================+===============================+
| PostgreSQL        | AUTHORITATIVE SoR   | Enterprise Facts (D1/D2)| ACID single source of truth   |
|                   |                     | Deliberation Events     | Append-only immutable log     |
|                   |                     | Agent Metrics (R_i)     | Evaluated historical scores   |
|                   |                     | Transactional Outbox    | Guaranteed event relay intent |
+-------------------+---------------------+-------------------------+-------------------------------+
| Neo4j             | DERIVED TOPOLOGY    | Network Graph Projection| Synchronized from PostgreSQL  |
|                   |                     | Multi-echelon Nodes     | Stale lag checked via epoch   |
+-------------------+---------------------+-------------------------+-------------------------------+
| pgvector          | SEMANTIC INDEX      | Precedent Memory Embeds | Cosine similarity memory      |
| (in PostgreSQL)   |                     | Decision Records Vectors| Read-only precedent guidance  |
+-------------------+---------------------+-------------------------+-------------------------------+
| Kafka             | TRANSPORT BACKBONE  | Event Log Bus           | At-least-once outbox delivery |
|                   |                     | Session Partitioning    | Strictly non-authoritative    |
+-------------------+---------------------+-------------------------+-------------------------------+
| Redis             | EPHEMERAL CACHE     | Deliberation Projections| Fail-closed on HARD_CRITICAL  |
|                   |                     | Hot Telemetry Cache     | Strictly non-authoritative    |
+===================+=====================+=========================+===============================+
```

---

## 38. Transactional Outbox Pattern

```
+-----------------------------------------------------------------------------+
|                          COGNITIVE AGENT / SERVICE                          |
|       Generates DeliberationEvent, StructuredClaim, or DecisionArtifact     |
+-----------------------------------------------------------------------------+
                                       |
                                       | [1. Synchronous Single DB Transaction]
                                       v
+-----------------------------------------------------------------------------+
|                    POSTGRESQL ACID TRANSACTION BOUNDARY                     |
|                                                                             |
|  BEGIN TRANSACTION;                                                         |
|    INSERT INTO deliberation_events (...) VALUES (...);  -- Authoritative    |
|    INSERT INTO scof_outbox (event_id, payload, ...)     -- Durable Intent   |
|  COMMIT;                                                                    |
+-----------------------------------------------------------------------------+
                                       |
                                       | [2. Asynchronous Polling / CDC Relay]
                                       v
+-----------------------------------------------------------------------------+
|                             OUTBOX RELAY WORKER                             |
|          Debezium CDC / Polling Daemon (Guarantees At-Least-Once)           |
+-----------------------------------------------------------------------------+
                                       |
                                       | [3. Publish Event Partitioned by session_id]
                                       v
+-----------------------------------------------------------------------------+
|                        KAFKA DISTRIBUTED EVENT LOG                          |
|        Ordered Partitions: scof.deliberation.events.v1 (Key: session_id)    |
+-----------------------------------------------------------------------------+
                                       |
                                       | [4. Idempotent Consumption]
                                       v
+-----------------------------------------------------------------------------+
|                         IDEMPOTENT KAFKA CONSUMER                           |
|      Checks: aggregate_version == current + 1 (Discards Duplicates)         |
+-----------------------------------------------------------------------------+
                                       |
                                       | [5. Materialize In-Memory Projection]
                                       v
+-----------------------------------------------------------------------------+
|                       REDIS SESSION VIEW CACHE STORE                        |
|       Key: session:{session_id}:{snapshot_epoch}:{sequence_number}          |
+-----------------------------------------------------------------------------+
```

**Guarantee:** PostgreSQL is always consistent. If PostgreSQL commits a state change, the corresponding event intent is also durably persisted in `scof_outbox`. Kafka provides at-least-once distribution via the outbox relay. Consumers achieve effective exactly-once state transitions through idempotent processing with aggregate version checks.

---

## 39. SCOFEvent Contract

```python
class SCOFEvent(BaseModel):
    """Base contract for ALL events in the SCOF event backbone."""
    event_id: str
    aggregate_type: str
    aggregate_id: str
    aggregate_version: int
    event_type: str
    causation_id: str
    correlation_id: str
    producer_id: str
    schema_version: str
    payload: dict
    timestamp: datetime
```

---

## 40. Kafka Topic Architecture

All events enter Kafka strictly via the Transactional Outbox relay. Ordering is guaranteed per decision session by partitioning on `session_id`.

### Canonical Topic Registry

| Topic Name | Purpose | Partition Key | Retention Policy | Consumers |
| :--- | :--- | :--- | :--- | :--- |
| `scof.decision.triggers.v1` | External disruptions & operational alerts | `entity_id` / `session_id` | 30 days (compacted) | Orchestrator, Ingestion Engine |
| `scof.deliberation.events.v1` | Agent claims, critiques, and coordinator events | `session_id` | 90 days (delete) | Redis Projection, Audit, Desktop Console |
| `scof.simulation.requests.v1` | Dispatches from Candidate Pipeline to Digital Twin | `simulation_id` | 7 days (delete) | Digital Twin Worker Pool |
| `scof.simulation.results.v1` | Completed simulation manifests & metrics | `simulation_id` | 90 days (delete) | Coordinator, CD2F Engine, Archival |
| `scof.decisions.published.v1` | Formally arbitrated DecisionResult objects | `session_id` | 365 days (compacted) | ExecutionPolicyService, HITL Hub |
| `scof.execution.commands.v1` | Authorized commands sent to ERP/TMS/WMS adapters | `execution_id` | 365 days (compacted) | Execution Adapters (ERP/TMS/WMS) |
| `scof.telemetry.metrics.v1` | Agent calibration, ECE, SLA latency, R_i signals | `agent_id` | 30 days (delete) | Evaluation Framework (D10) |

---

## 41. Consumer Idempotency

```
Before applying any event:
    current_version = get_aggregate_version(event.aggregate_id)
    
    If event.aggregate_version <= current_version:
        -> Duplicate event. Discard. Log.
    
    If event.aggregate_version > current_version + 1:
        -> Out-of-order event. Queue for re-ordering.
    
    If event.aggregate_version == current_version + 1:
        -> Apply event. Update aggregate version.
```

---

# PART IX: DECISION POLICY LAYER

---

## 42. DecisionPolicy Schema

All organizational decision-making policy in one schema. Loaded from profile YAML, never generated by agents or LLMs.

```python
class DecisionPolicy(BaseModel):
    profile_id: str
    version: str
    
    objective: DecisionObjective
    evidence_policy: EvidencePolicy
    deliberation_policy: DeliberationPolicy
    simulation_policy: SimulationPolicy
    routing_policy: RoutingPolicy
    reliability_policy: ReliabilityGovernancePolicy
    execution_policy: ExecutionPolicy
    priority_sla_policy: PrioritySLAPolicy
    
    integrity: PolicyIntegrity
```

---

## 43. Policy Precedence Hierarchy

```
1. SAFETY / REGULATORY CONSTRAINTS       (non-negotiable)
2. ENTERPRISE HARD CONSTRAINTS           (from DecisionPolicy.hard_constraints)
3. PROFILE-SPECIFIC POLICIES             (from DecisionPolicy)
4. ORGANIZATIONAL NORMS                  (from execution_policy)
5. SOFT OBJECTIVES                       (from DecisionPolicy.soft_constraints)
6. AGENT PREFERENCES                     (lowest authority)
```

---

## 44. Policy and Profile Integrity

```python
class PolicyIntegrity(BaseModel):
    policy_content_hash: str
    profile_content_hash: str
    computed_at: datetime
    hash_algorithm: str = "sha256"
    
    EXCLUDED_FROM_HASH: ClassVar[set[str]] = {
        "policy_content_hash", "profile_content_hash",
        "computed_at", "hash_algorithm",
    }
```

The integrity metadata itself is EXCLUDED from hash computation to avoid self-reference. Hashing uses deterministic JSON serialization with `sort_keys=True`.

---

# PART X: AGENT RELIABILITY AND GOVERNANCE

---

## 45. R_i Agent Reliability Factor

R_i is computed from structured evaluation metrics, not pgvector semantic similarity.

```python
class ReliabilityScore(BaseModel):
    agent_id: str
    disruption_type: str
    model_version: str
    decision_class: str
    
    accuracy: float
    calibration: float
    constraint_violation_rate: float
    outcome_quality: float
    
    composite_r_i: float
    confidence_interval: tuple[float, float]
    
    sample_size: int
    is_cold_start: bool
    clamped: bool
```

### Agent Influence Status

```python
class AgentInfluenceStatus(str, Enum):
    FULL = "FULL"               # R_i > threshold, full sample size
    REDUCED = "REDUCED"         # R_i below threshold or small sample
    ADVISORY = "ADVISORY"       # Below minimum but not excluded
```

---

## 46. R_i Lifecycle Governance

```python
class ReliabilityGovernancePolicy(BaseModel):
    evaluation_window_days: int = 90
    minimum_sample_size: int = 10
    cold_start_prior: float = 0.50
    decay_half_life_days: int = 30
    
    stratify_by: list[str] = [
        "disruption_type", "decision_class", "model_version",
    ]
    
    min_r_i: float = 0.20      # Floor: no agent fully excluded
    max_r_i: float = 0.95      # Ceiling: no agent dominates
    
    compute_confidence_interval: bool = True
    update_frequency: str = "per_session"
    batch_recalibration_cron: str = "weekly"
```

---

## 47. Contradiction Taxonomy

```python
class ConflictRecord(BaseModel):
    conflict_type: Literal[
        "DATA_CONTRADICTION",
        "MODEL_DISAGREEMENT",
        "POLICY_CONFLICT",
        "ACTION_CONFLICT",
        "TEMPORAL_DISAGREEMENT",
    ]
    
    severity: Literal["MINOR", "MAJOR", "BLOCKING"]
    
    resolution_method: Optional[Literal[
        "AUTHORITY_HIERARCHY",
        "FRESHNESS_WINS",
        "SNAPSHOT_ENFORCED",
        "CROSS_REFERENCE",
        "UNRESOLVABLE",
    ]]
```

---

## 48. Failure Taxonomy and Response Map

| Failure | Response | Escalation |
| :--- | :--- | :--- |
| AGENT_TIMEOUT | Use deterministic ML-only fallback | If critical domain, flag in sufficiency |
| AGENT_SCHEMA_FAILURE | Retry once with corrected prompt; then fallback | Log for prompt review |
| AGENT_OWNERSHIP_VIOLATION | Reject proposal, request revision | Log for policy review |
| EVIDENCE_INSUFFICIENT | HITL escalation (Tier-3) | Do not proceed to Twin or CD2F |
| TWIN_TIMEOUT | Proceed to CD2F without simulation; if REQUIRED, HITL | CD2F applies higher uncertainty |
| TWIN_INVARIANT_VIOLATION | Eliminate the violating candidate | Log for debugging |
| CD2F_NO_FEASIBLE_ACTION | HITL escalation | Human must provide alternative |
| CD2F_PARETO_AMBIGUITY | HITL with trade-off summary | Human selects from Pareto set |
| STATE_CHANGED | Revalidate decision against new state | If material, replan |
| SESSION_CANCELLED | Propagate cancellation (Section 49) | Archive partial session |

---

## 49. Cancellation Propagation

```
CancellationEvent received
    |-> DecisionSession.status -> "CANCELLED"
    |-> LangGraph: interrupt current workflow
    |-> A2A: cancel all active tasks for session
    |-> MCP: cancel in-flight tool calls (best-effort)
    |-> Twin: cancel simulations, release branches
    |-> Kafka: publish SESSION_CANCELLED (via outbox)
    |-> Redis: update session cache
    |-> Deliberation Table: all items -> WITHDRAWN
    |-> Audit: emit cancellation trace
```

---

# PART XI: OBSERVABILITY, DECISION RECORD, AND REPLAY (D9)

---

## 50. Decision Record

```python
class DecisionRecord(BaseModel):
    """Final, immutable business artifact. Stored permanently."""
    record_id: str
    session_id: str
    trigger: DisruptionEvent
    snapshot: DecisionSnapshot
    policy_version: str
    policy_content_hash: str
    
    agents_consulted: list[str]
    evidence_sufficiency: EvidenceSufficiencyAssessment
    candidate_count_raw: int
    candidate_count_normalized: int
    simulation_count: int
    cross_exam_rounds: int
    total_deliberation_duration_ms: float
    
    selected_action: CandidateAction
    arbitration_result: CD2FArbitrationResult
    execution_authorization: ExecutionAuthorization
    execution_outcome: ExecutionOutcome
    
    replay_manifest_ref: str
    full_event_log_ref: str
    
    human_assessment: Optional[str]
    actual_outcome: Optional[OutcomeObservation]
    outcome_recorded_at: Optional[datetime]
```

---

## 51. Outcome Observation Schema

Structured, not free-form. Used for R_i calibration.

```python
class OutcomeObservation(BaseModel):
    decision_id: str
    observed_at: datetime
    horizon_days: int
    
    actual_service_level: Optional[float]
    actual_cost_usd: Optional[float]
    actual_lead_time_days: Optional[float]
    actual_risk_materialized: Optional[bool]
    
    observation_source: Literal["automated_kpi", "human_assessment", "hybrid"]
    observation_confidence: float
```

---

## 52. Replay Manifest

```python
class DecisionReplayManifest(BaseModel):
    decision_id: str
    session_id: str
    enterprise_snapshot: DecisionSnapshot
    
    agent_model_versions: dict[str, str]
    llm_model_id: str
    llm_model_version: str
    twin_model_version: str
    
    profile_version: str
    policy_version: str
    random_seeds: dict[str, int]
    
    replay_type: Literal["TRACE", "LOGICAL", "MODEL", "EXACT_SYSTEM"]
    exact_system_available: bool
    exact_system_blockers: list[str]
    
    tool_invocation_log_ref: Optional[str]
```

Replay fidelity is bounded and explicitly classified. `EXACT_SYSTEM` requires explicit confirmation that all dependencies are captured.

---

## 53. MCP Capability Versioning and Side-Effect Classification

```python
class CapabilityCard(BaseModel):
    capability_id: str
    version: str
    schema: dict
    
    side_effect_class: Literal[
        "READ_ONLY",
        "SCENARIO_MUTATION",
        "EXTERNAL_SIDE_EFFECT",
    ]
    
    authorization_scope: Literal["AGENT", "COORDINATOR", "EXECUTION_ADAPTER"]
    latency_class: Literal["fast", "medium", "slow"]
    cacheable: bool
    cache_ttl_seconds: Optional[int]
    domain_tags: list[str]
```

Runtime enforcement:
- Agents: ONLY `READ_ONLY`
- Twin: `READ_ONLY` and `SCENARIO_MUTATION`
- Execution Adapter: `EXTERNAL_SIDE_EFFECT` (with policy gate)

---

# PART XII: EVALUATION AND BENCHMARK (D10)

---

## 54. B0-B7 Ablation Ladder

| Baseline | Components Added (vs Previous) | What It Tests |
| :--- | :--- | :--- |
| **B0** | Hard-coded if-then-else. No ML, no LLM, no agents, no Twin. | Is any intelligence better than deterministic rules? |
| **B1** | One LLM+ML agent. No specialization. Minimal CD2F. | Does ML+LLM reasoning add value over rules? |
| **B2** | Six independent specialists. No cross-examination. No Twin. | Does domain specialization improve quality? |
| **B3** | B2 + Deliberation Table + cross-examination. NO evidence gate. | Does structured deliberation improve over independent assessment? |
| **B4** | B3 + evidence sufficiency gate actively enforced. No Twin. | Does evidence gating reduce error rate? |
| **B5** | B4 + Twin simulation with simplified scoring. | Does counterfactual simulation add value? |
| **B6** | B5 + full CD2F (direction-aware normalization, proper Pareto, three-tier impact). | Does formal arbitration beat simplified scoring? |
| **B7** | Full system with all governance layers. | Full system with all governance. |

B0 rules MUST be frozen before any system evaluation begins.

---

## 55. Statistical Evaluation Protocol

- Primary test: non-parametric, distribution-light (permutation tests assume exchangeability, not distributional shape)
- Minimum scenarios per test: 30 (floor for V2 MVP; production evaluation should use formal power analysis)
- ECE acceptance threshold: 0.10
- Brier acceptance threshold: 0.15

---

## 56. Evaluation Metrics and Targets

| Metric | Target |
| :--- | :--- |
| Decision Quality Score (vs. B0) | Statistically significant improvement (p < 0.05) |
| Constraint Violation Rate | < 5% of decisions |
| Service Level Preservation | >= 90% |
| Cost Efficiency (vs. hindsight optimal) | Within 15% |
| Human Agreement | >= 75% on blind sample |
| Calibration (confidence vs. outcome) | r >= 0.60 |
| Latency p95 | Within SLA targets |
| Explainability | >= 90% fully traceable |

---

# PART XIII: EXECUTION BOUNDARY AND CROSS-CUTTING CONCERNS

---

## 57. Execution Boundary Matrix

```
+==========================================================================+
|  Component           | ERP Write | Twin Write | DB Write | Deliberation  |
|  --------------------|-----------|------------|----------|---------------|
|  Agent               |    NO     |    NO      |   NO     | Post verdicts |
|  Coordinator         |    NO     |    NO      |   NO*    | Manage items  |
|  CD2F                |    NO     |    NO      |   NO     | Post decision |
|  Twin                |    NO     | SCENARIO   |   NO     | --            |
|  Execution Adapter   |   YES**   |    NO      |   NO     | --            |
|                                                                          |
|  * Coordinator writes ONLY to deliberation_* tables                      |
|  ** Execution Adapter requires HITL or policy authorization              |
|                                                                          |
|  THREE KINDS OF "EXECUTION" (never collapse):                            |
|  1. Simulation execution: Twin (ephemeral scenario state)                |
|  2. Decision execution: CD2F -> approved decision object                 |
|  3. Real-world execution: Execution Adapter -> ERP/TMS/WMS (gated)       |
+==========================================================================+
```

---

## 58. Mechanism Responsibility Matrix

| Mechanism | Responsibility | Does NOT Do |
| :--- | :--- | :--- |
| **LangGraph** | Workflow execution: state machine, branching, cycles, timeouts | Does not store claims, transport events, manage agent contracts |
| **Deliberation Table** | Cognitive workspace/state: items, verdicts, sessions | Does not execute workflows, transport events |
| **A2A** | Agent interoperability/task contract: agent cards, capability, health | Does not store decision artifacts |
| **Kafka** | Durable event transport: notifications, audit trail, replay | Does not store state authoritatively |
| **MCP** | Bounded tool/data access: governed retrieval, audit-traced | Does not store state |
| **CD2F** | Evidence-based arbitration: constraint validation, trade-off evaluation | Does not retrieve data, execute simulations |
| **RAG** | Evidence acquisition: retrieval, re-ranking, context assembly | Does not make decisions |
| **Digital Twin** | Counterfactual evaluation: simulation, invariant enforcement | Does not orchestrate agents, make decisions |

---

## 59. Redis Governance

```python
class GovernedDataAccessRecord(BaseModel):
    """All data access produces this record."""
    access_id: str
    agent_id: str
    session_id: str
    data_source: Literal["postgresql", "neo4j", "pgvector", "redis"]
    access_mechanism: Literal["mcp", "direct"]
    query_hash: str
    timestamp: datetime
    authorized: bool
    audited: bool
```

### Fail-Closed Policy for Critical Evidence

If Redis is unavailable for critical evidence:
- Do NOT fall back to stale cached data
- Treat as evidence gap in the sufficiency assessment
- If the missing data is HARD_CRITICAL, verdict becomes INSUFFICIENT

---

## 60. Priority-Aware Admission Control

```yaml
concurrency:
  twin_workers:
    total: 8
    reserved:
      P0: 2
      P1: 2
    shared:
      P2_P3: 4
    preemption:
      P0_can_preempt: [P1, P2, P3]
      P1_can_preempt: [P2, P3]
      P2_can_preempt: [P3]

  agent_workers:
    total: 12
    reserved:
      P0: 6
    shared:
      P1_P2_P3: 6

  llm_inference:
    max_concurrent_requests: 4
    priority_queue: true
```

---

## 61. Concurrent Session Interference Detection

When a new decision session is created, the Coordinator checks for existing active sessions that share affected entities. If overlap is detected, the new session either waits, or proceeds with an interference flag that reduces its autonomy tier.

---

# PART XIV: ARCHITECTURE DIAGRAMS

---

## 62. Ultra-Detailed Unified Architecture Diagram

```
+===================================================================================================+
|                                SCOF V2 COGNITIVE DECISION FABRIC                                  |
|                 (Ultra-Detailed Unified Architecture Reference -- D3 through D10)                 |
+===================================================================================================+
|                                                                                                   |
|  TEN ARCHITECTURAL INVARIANTS (FROZEN FOUNDATION):                                                |
|  1. Source Authority     2. Cognitive Workspace 3. Evidence Sufficiency 4. Candidate Discipline   |
|  5. Counterfactual Isolate 6. Decision Authority 7. Policy Authority    8. State Freshness        |
|  9. Execution Safety     10. Bounded Replayability                                                |
|                                                                                                   |
|  +--[CANONICAL REGISTRIES (STARTUP VALIDATED SINGLE SOURCE OF TRUTH)]--------------------------+  |
|  | ClaimTypeRegistry (30 Types) | EvidenceClass Registry (6 Classes) | ActionRegistry (18 Acts)|  |
|  | - Every reference cross-validated at boot; strict validation failure aborts system startup  |  |
|  | - Closed-vocabulary composite_action governed with parameter_authority: COMPONENT_DELEGATED |  |
|  +---------------------------------------------------------------------------------------------+  |
|                                                                                                   |
|  +--[D9: OBSERVABILITY, EXPLAINABILITY AND HUMAN CONSOLE]--------------------------------------+  |
|  | Tauri v2 Desktop GUI Console                                                                |  |
|  | - End-to-End Decision Trace Log (Trigger -> Snapshot -> RAG -> Proposals -> Critiques       |  |
|  |   -> Sufficiency -> Normalization -> Composites -> Twin -> Pareto Vector -> Decision)       |  |
|  | - Real-Time Deliberation Visualizer (Redis Session Projection Views)                        |  |
|  | - Multi-Objective Trade-Off Frontier Radar & Sensitivity Breakdown Plots                    |  |
|  | - Human-in-the-Loop Escalation Hub (Trade-off Matrix for GENUINE_PARETO_AMBIGUITY)          |  |
|  | - DecisionRecord Archival Engine & Bounded Replay (TRACE / LOGICAL / MODEL / EXACT_SYSTEM)  |  |
|  +---------------------------------------------------------------------------------------------+  |
|         | User Directives / Approvals                ^ Real-Time Streaming Telemetry / Audits     |
|         v                                            |                                            |
|  +--[D8: EVENT AND RUNTIME BACKBONE]-----------------------------------------------------------+  |
|  | FastAPI Gateway & WebSocket Broadcast                                                       |  |
|  | Transactional Outbox Relay -> Kafka Topic Backbone (Session Partitioned)                    |  |
|  | SCOFEvent Contract (event_id, aggregate_version, causation_id, payload, timestamp)          |  |
|  | Idempotent Consumer Engines (aggregate_version ordering check)                              |  |
|  | DB-Enforced Session State Transitions: CREATED -> ACTIVE -> {CLOSED | CANCELLED | EXPIRED}  |  |
|  | Deliberation Event Store Constraints: UNIQUE(session_id, sequence_number)                   |  |
|  +---------------------------------------------------------------------------------------------+  |
|         | Directives & Events                        ^ State Changes        ^ Metrics & Traces    |
|         v                                            |                      |                     |
|  +--[DECISION POLICY LAYER]----------+               |       +--[D10: EVALUATION BENCHMARK]----+  |
|  | DecisionPolicy Schema             |               |       | B0-B7 Ablation Baseline Ladder  |  |
|  | - Direction-Aware Normalization   |               |       | Non-Parametric Permutation Test |  |
|  | - 6-Level Precedence Hierarchy    |               |       | ECE (<0.10) / Brier (<0.15)     |  |
|  | - Content-Addressable Integrity   |               |       | Anti-Overfitting Scenario Suite |  |
|  |   (Excludes Hash Self-Reference)  |               |       | RQ1-RQ4 Statistical Validation  |  |
|  +-----------------------------------+               |       +---------------------------------+  |
|         | Bound Policy Object                        |                      ^ Evaluation Feeds    |
|         v                                            |                      |                     |
|  +=============================================================================================+  |
|  | D6: LANGGRAPH MACRO-ORCHESTRATION KERNEL (DETERMINISTIC COORDINATOR ENGINE)                 |  |
|  | (Strict Discipline: Coordinator is a deterministic workflow orchestrator, NOT an agent)     |  |
|  |                                                                                             |  |
|  |   [Disruption Trigger Ingestion]                                                            |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [1. Allocate DecisionSnapshot Epoch] --------> Atomic Common Consistency Coordinate       |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [2. Tier-1 RAG Pre-Retrieval] ---------------> Broad & Shallow Context Package            |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [3. Capability Binding & Routing] -----------> Resolve Dynamic MCP Tools & Agent Affinity |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [4. Parallel Specialist Fan-Out] ------------> Zero Cross-Agent Visibility (Independent)  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [5. Fan-In Deliberation Collation] ----------> Assemble Deliberation Table in PostgreSQL  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [6. Targeted Cross-Examination] -------------> Conflict Critiques (Strictly <= 2 Rounds)  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [7. EVIDENCE SUFFICIENCY GATE] --------------> Individual HARD_CRITICAL Freshness/Auth    |  |
|  |             |                                    (Fail -> Mandatory HITL Escalation)        |  |
|  |             v                                                                               |  |
|  |   [8. Candidate Extraction & Atomic Normalization]                                          |  |
|  |       (Steps 1-7: Schema, Entities, T1 Baseline, T2 Predictive, Constraints, Dedup, Prune)  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [9. Combination Synthesis (Step 8)] ---------> Cross-Domain Non-Conflicting Composites    |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [10. COMPOSITE REVALIDATION PASS (Step 9)]                                                |  |
|  |        (Revalidate: Schema, Parameter Authority, Entities, Hard Constraints, Joint Impact)  |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [11. Candidate Budget Selection (Step 10)] --> UCB Heuristic + Baseline & Domain Reserves |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [12. Candidate Admission Sealing (Step 11)] -> Sign Validated Candidates with Seal        |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [13. Digital Twin Materiality Evaluation] ---> REQUIRED / RECOMMENDED / ADVISORY Check    |  |
|  |             |                                                                               |  |
|  |             +==========================+==================================+                 |  |
|  |                                        |                                  |                 |  |
|  |                                [Simulatable]                    [Non-Simulatable]           |  |
|  |                                        |                                  |                 |  |
|  |                                        v                                  |                 |  |
|  |                          [14. Digital Twin Simulation]                    |                 |  |
|  |                          (Counterfactual Tier-3 Impact)                   |                 |  |
|  |                          (Optional 1-Time Re-Deliberation)                |                 |  |
|  |                                        |                                  |                 |  |
|  |                                        v                                  v                 |  |
|  |             +=============================================================+                 |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [15. CD2F VECTOR PARETO ARBITRATION] --------> Multi-Objective Vector Frontier P on U(c)  |  |
|  |             |                                    (Evaluates Dimensional Dominance First)    |  |
|  |             v                                                                               |  |
|  |   [16. Frontier Resolution via Policy & Uncert] -> Resolve P if |P| > 1 via J_final         |  |
|  |             |                                    (SINGLETON / POLICY_RESOLVED / AMBIGUITY)  |  |
|  |             v                                                                               |  |
|  |   [17. Return DecisionResult] -----------------> CD2F Selects; Does NOT Authorize Execution |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [18. ExecutionPolicyService Gate] -----------> Independent Organization Autonomy Gate     |  |
|  |             |                                                                               |  |
|  |             v                                                                               |  |
|  |   [19. State Revalidation Check] --------------> Detect Snapshot Epoch Drift & Stale World  |  |
|  |             |                                                                               |  |
|  |             +------------+-------------------------------+-------------------+              |  |
|  |                          |                               |                   |              |  |
|  |                    [State Valid]                 [Material Drift]      [Policy Gate]        |  |
|  |                          |                               |                   |              |  |
|  |                          v                               v                   v              |  |
|  |                  [Execute Adapter]               [Trigger Replan]    [HITL Escalation]      |  |
|  +=============================================================================================+  |
|         | Tool Invocations       ^ Agent Proposals          ^ Simulation Results|                 |
|         v via Governed MCP       | & Cross-Critiques        | & Validation Envs | State Checks    |
|  +====================================================+   +===================+ |                 |
|  | D3/D4: LANGCHAIN SPECIALIST REASONING AGENT ROSTER |   | D7: DIGITAL TWIN  | |                 |
|  | [1] Demand & Commerce Specialist Agent             |   | (COUNTERFACTUAL   | |                 |
|  | [2] Inventory & Asset Management Specialist Agent  |   |  EVALUATION)      | |                 |
|  | [3] Procurement & Supplier Specialist Agent        |   | - Scenario Layer 3| |                 |
|  | [4] Logistics & Transport Specialist Agent         |   |   State Mutation  | |                 |
|  | [5] Financial & Enterprise Value Specialist Agent  |   | - Reproducible    | |                 |
|  | [6] Risk & Resilience Specialist Agent             |   |   Manifest Replay | |                 |
|  | Each Specialist Runs:                              |   | - Horizon Rollout | |                 |
|  | - Hybrid Domain ML Models + Bounded LLM Reasoning  |   |   [7 to 28 Days]  | |                 |
|  | - Tier-2 Deep RAG (MCP Governed + Hot-Path Cache)  |   | - Enforces Twin   | |                 |
|  | - Strict DomainOwnershipPolicy & ActionIntent Only |   |   Admission Seals | |                 |
|  +====================================================+   +===================+ |                 |
|         | Read Artifacts              ^ Append Events               | Manifests | Projections     |
|         v & Materialized Views        | (Session Partitioned)       |           v                 |
|  +---------------------------------------------------------------------------------------------+  |
|  | DELIBERATION TABLE (EVENT-SOURCED COGNITIVE WORKSPACE)                                      |  |
|  | - Authoritative Cognitive Events: PostgreSQL deliberation_events (Append-Only, Immutable)   |  |
|  | - Materialized Session Projections: Redis session:{id}:{epoch}:{seq} (Snapshot-Keyed)       |  |
|  | - Single-Writer Sequence Allocation & DB Constraint: UNIQUE(session_id, sequence_number)    |  |
|  +---------------------------------------------------------------------------------------------+  |
|         | Reads & Graph Traversals                                  | Write Events / Sync         |
|         v                                                           v                             |
|  +---------------------------------------------------------------------------------------------+  |
|  | D1 + D2: ENTERPRISE DATA FABRIC (SYSTEM OF RECORD)                                          |  |
|  | - PostgreSQL: Authoritative operational facts (96 core relational tables, transactional)    |  |
|  | - Neo4j: Current materialized topology projection (3.73M nodes, version-stamped)            |  |
|  | - pgvector: Semantic memory & historical decision precedent index (384-dimensional)         |  |
|  | - Redis: Ephemeral real-time telemetry cache (governed, fail-closed on critical queries)    |  |
|  | - Atomic Snapshot Epoch Coordinator: Common temporal coordinate for all session reasoning   |  |
|  +---------------------------------------------------------------------------------------------+  |
|                                                                                                   |
|  CROSS-CUTTING RUNTIME INFRASTRUCTURE:                                                            |
|  Kafka  = Event backbone (via Transactional Outbox, at-least-once, idempotent consumers)          |
|  MCP    = Governed tool/capability access (versioned, side-effect classified, audit-logged)       |
|  A2A    = Agent task contracts, capability advertisements, and health monitoring                  |
|  Redis  = Governed operational cache (policy-governed access, fail-closed on critical evidence)   |
|                                                                                                   |
+===================================================================================================+
```

---

## 63. Corrected LangGraph State Machine

See Section 17 for the complete state machine definition with all conditional branches, evidence gate ordering, candidate normalization, Twin simulation, CD2F arbitration, and execution policy check.

---

# PART XV: IMPLEMENTATION

---

## 64. Evaluation-Gated Implementation Sequencing

### Phase 1: Cognitive Agent Runtime + Vertical Research Slice (D3)

**Build:** ReasoningService abstraction, Ollama provider, structured output parsing, bounded tool calling, evidence provenance tracking, deterministic fallback, transform ONE agent (Procurement & Supplier).

**Vertical Slice:** One agent -> one candidate -> one Twin simulation -> one CD2F evaluation -> one evaluation metric.

**Gate:** Can one agent produce valid, structured, evidence-backed proposals? Does the minimal loop outperform B0?

### Phase 2: Specialist Federation (D4)

**Build:** Expand to six agents, Agent Card V2, DomainOwnershipPolicy with enforcement, domain-specific RAG configs, A2A lifecycle.

**Gate:** Do specialist boundaries improve performance over a single generalist (B1 vs B2)?

### Phase 3: Evidence Fabric and Retrieval (D5)

**Build:** SCOFRetriever, MCP-governed retrieval, two-class retrieval model, proposition-specific evidence authority, Neo4j projection freshness, CapabilityCard with versioning.

**Gate:** Does MCP-governed RAG improve factual grounding?

### Phase 4: Cognitive Orchestration and Deliberation (D6)

**Build:** LangGraph V2 state machine, DecisionSnapshot binding, event-sourced Deliberation Table, domain affinity routing, two-phase independence protocol, evidence sufficiency gates, priority/SLA system, Coordinator service decomposition, DecisionPolicy loading, contradiction taxonomy, cancellation propagation.

**Gate:** Does orchestrated deliberation with cross-examination improve over independent agents (B2 vs B3)?

### Phase 5: CD2F + Counterfactual Decision (D7)

**Build:** Candidate normalization and composite revalidation pipeline (11-step with CandidateAdmissionSeal), three-tier impact evaluation, Twin simulation dispatch with SimulationManifest, CD2F formal objective vector evaluation and point-estimate Pareto arbitration, execution authorization separation (ExecutionPolicyService), R_i governance, state revalidation.

**Gate:** Does Twin simulation + evidence-based arbitration beat naive scoring (B3 vs B5 vs B6)? Statistical significance: p < 0.05.

### Phase 6: Event and Runtime Backbone (D8)

**Build:** Transactional outbox, Kafka V2 topics, SCOFEvent contract, consumer idempotency, Redis derived cache, API Gateway V2.

**Gate:** Does Kafka eventing improve auditability without unacceptable latency?

### Phase 7: Observability, Explainability and Desktop Console (D9)

**Build:** Complete decision trace, evidence provenance visualization, trade-off explanation rendering, DecisionRecord, replay capability, failure dashboards, Tauri v2 HITL console.

**Gate:** Is every decision fully traceable? Can decisions be replayed from manifests?

### Phase 8: Final Evaluation (D10)

**Build:** Full benchmark suite, B0-B7 ablation ladder, anti-overfitting measures, R_i validation, SLA validation, statistical significance testing.

**Gate:** Does the complete system satisfy RQ1-RQ4 benchmarks? Does each layer contribute measurable value?

---

## 65. Contract Freeze Declaration

### Frozen (No Further Conceptual Redesign)

- Ten Architectural Invariants
- Six Cognitive Stages (KNOW -> UNDERSTAND -> DELIBERATE -> EXPLORE -> DECIDE -> EXPLAIN)
- Agent Roster (6 + 1)
- Mechanism Responsibility Matrix
- ClaimTypeRegistry (30 types), EvidenceClass (6 classes), ActionRegistry (18 actions unified)
- ActionRegistry Full 12-Field Canonical Specification and closed-vocabulary composite_action
- DomainOwnershipPolicy contracts and parameter_authority rules
- Three-tier impact model (Baseline / Predictive / Counterfactual)
- Tiered criticality model (HARD_CRITICAL / DEGRADED_CRITICAL / IMPORTANT / SUPPLEMENTARY)
- Individual Hard-Critical evidence freshness, authority, presence, and non-contradiction gate
- Common snapshot epoch consistency coordinate
- Full session restart on snapshot advancement (no partial restart)
- Direction-aware signed normalization with saturation policy (CLIP / LOG_COMPRESS)
- Controlled Combination Synthesis and 11-step candidate normalization pipeline with CandidateAdmissionSeal
- Candidate Budget Selection (UCB heuristic, explicitly not a safety proof)
- Unified SimulationMaterialityThresholds
- Proper Vector-First Pareto Arbitration (Pareto dominance computed directly on metric vectors before scalar weighting)
- Event-sourced Deliberation Table (PostgreSQL authoritative, Redis projections)
- Session state machine with DB-enforced transition locks
- Content-addressable policy hashing (excluding integrity self-references)
- State revalidation before execution (approved_snapshot_epoch vs current_snapshot_epoch)
- Corrected B0-B7 ablation ladder (B3 deliberation / B4 evidence gate separation)
- Proposition-specific evidence authority
- Execution authorization separation (CD2F selects; ExecutionPolicyService authorizes)
- DecisionRecord as immutable business artifact
- Replay manifest with bounded fidelity classification (TRACE / LOGICAL / MODEL / EXACT_SYSTEM)

### Tunable (Profile Defaults, Not Frozen Architecture)

- Objective weights per profile
- Evidence freshness thresholds
- Domain affinity routing thresholds
- Cross-examination round limits
- Simulation budget parameters
- R_i governance parameters (window, decay, floor/ceiling)
- SLA target values
- Saturation policy per metric (CLIP or LOG_COMPRESS)
- Snapshot advancement limits
- Revalidation drift thresholds
- Calibration acceptance thresholds (ECE, Brier)
- Minimum sample size floor

---

## 66. Improvement and Future Enhancement Backlog

These items are validated architectural observations. They are NOT required for V2 to demonstrate its central thesis.

### High-Priority (Consider for V2.1)

| # | Item | Description |
| :--- | :--- | :--- |
| I-1 | Coverage-aware budget selection | Mandatory candidate reservations per domain |
| I-2 | Grouped leakage control | Group-aware train/eval splitting |
| I-3 | Action outcome selection bias control | Exposure count for R_i computation |
| I-4 | Retrieval artifact snapshot binding | snapshot_id in retrieval artifacts |
| I-5 | Resource-level concurrent session detection | Resource/capability overlap checks |

### Medium-Priority (Consider for V2.2)

| # | Item | Description |
| :--- | :--- | :--- |
| I-6 | Uncertainty-aware Pareto | Interval/robust Pareto analysis |
| I-7 | R_i causal attribution | Confound-aware outcome quality |
| I-8 | Action-specific Twin horizons | Candidate-level simulation materiality |
| I-9 | ActionRegistryEntry versioning | Cryptographic action definitions |
| I-10 | Replanning refinement | Entity/failure-class-specific exclusion |

### Future Enhancements (Post-V2)

| # | Item | Description |
| :--- | :--- | :--- |
| F-1 | Logarithmic/sigmoid utility | Advanced utility functions |
| F-2 | Bitemporal evidence semantics | valid_time, transaction_time, observed_time |
| F-3 | Rich risk realization model | Severity/monetary loss for outcomes |
| F-4 | Power analysis for sample sizing | Formal power analysis |
| F-5 | Multi-disruption B0 baselines | B0 heuristics per disruption class |
| F-6 | Controlled component ablations | Component ON/OFF studies |
| F-7 | Dynamic governance class | Context-sensitive governance |
| F-8 | Full A2A delegation | Inter-agent task delegation |
| F-9 | Production concurrency | Multi-instance Coordinator |
| F-10 | Bit-exact replay | Container digest, CUDA runtime capture |

---

> This document represents the consolidated, contract-frozen architecture for SCOF V2 D3-D10 implementation. All architectural contracts are frozen and validated. The vocabulary is closed. The mathematical model is fully verified. The state semantics are internally consistent. The evaluation protocol is formalized. The scope is explicitly bounded. The architecture is frozen and ready for D3 implementation.
