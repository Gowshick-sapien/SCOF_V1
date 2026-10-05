# SCOF V2 Cognitive Decision Fabric -- Final Architecture Draft

**Document Status:** FINAL DRAFT -- Consolidated Canonical Reference
**Scope:** D3 through D10 (Decision Engine Architecture)
**Predecessors:** Initial Plan, Amendments 1, 2, 3, and 4 (Contract Freeze Pass)
**Date:** 2026-10-05
**Authority:** This document consolidates and supersedes all prior amendment documents. Where amendments contradict each other, the latest correction (Amendment 4) prevails. Where no correction exists, the original definition stands.

---

## Document Purpose

This document is the single authoritative reference for the SCOF V2 Cognitive Decision Fabric architecture spanning deliverables D3 through D10. It consolidates the initial architecture plan and four successive amendment passes into one self-contained specification. Every schema, contract, invariant, pipeline, and diagram herein represents the final canonical form -- all contradictions resolved, all vocabulary unified, all mathematical corrections applied.

This is NOT an abstract overview. Every section contains the implementation-contract-level detail required for engineering execution.

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
62. [Ultra-Detailed Unified Architecture Diagram](#62-unified-architecture-diagram)
63. [Corrected LangGraph State Machine](#63-langgraph-state-machine)

### Part XV: Implementation
64. [Evaluation-Gated Implementation Sequencing](#64-implementation-sequencing)
65. [Contract Freeze Declaration](#65-contract-freeze-declaration)
66. [Improvement and Future Enhancement Backlog](#66-improvement-backlog)

---

# PART I: ARCHITECTURAL FOUNDATION

---

## 1. Ten Architectural Invariants

These ten invariants are the non-negotiable properties of the D3-D10 architecture. Every design decision, implementation choice, and evaluation criterion must be validated against them. Wording refined through Amendments 2, 3, and 4.

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
```

### Invariant 4: Candidate Discipline

```
No unbounded candidate or simulation expansion.
Candidate budget and simulation budget are explicit, configurable limits.
Budget enforcement (Step 8) is a HEURISTIC (UCB-based), not a safety proof.
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
CD2F: arbitrates using a formal objective function with direction-aware normalization.
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

The D3-D10 architecture is organized around six cognitive stages. This is the mental model that governs every design decision. Stage ordering corrected in Amendment 2 (DELIBERATE before EXPLORE).

```
                    KNOW
                      |
                      v
                 UNDERSTAND
                      |
                      v
                 DELIBERATE
                /           \
       revise/critique    candidate actions
                              |
                              v
                    EVIDENCE GATE
                    (must pass before
                     expensive simulation)
                              |
                   insufficient |  sufficient
                       |                |
                      HITL              v
                                    EXPLORE
                                 Digital Twin
                                      |
                        [if unexpected outcome]
                              |            |
                       re-deliberate    proceed
                              |            |
                              +-----+------+
                                    |
                                    v
                                 DECIDE
                                  CD2F
                                    |
                                    v
                                 EXPLAIN
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
EXPLORE (Twin simulation) reveals unexpected outcome
    |
    v
Twin result violates expectation threshold?
    |
    +-- NO:  proceed to DECIDE
    |
    +-- YES: targeted re-deliberation (max 1 iteration)
             |
             v
             Coordinator posts Twin result to Deliberation Table
             Affected agents receive targeted re-assessment request
             Agents revise candidate actions based on simulation insight
             |
             v
             Re-normalize candidates -> Re-simulate -> Proceed to DECIDE
```

**Bound:** This EXPLORE -> DELIBERATE loop executes at most once. If the second simulation still produces unexpected results, the system proceeds to CD2F with available evidence and flags elevated uncertainty.

---

## 4. High-Level Architecture Diagram

```
+=============================================================================+
|                   SCOF V2 COGNITIVE DECISION FABRIC                         |
|                   (D3 through D10 -- Final Draft)                           |
+=============================================================================+
|                                                                             |
|  +--[D9: OBSERVABILITY, EXPLAINABILITY & DESKTOP CONSOLE]----------------+  |
|  | Tauri v2 | Decision Trace | HITL Escalation | What-If Lab             |  |
|  | Evidence Visualization | Trade-off Explanations | DecisionRecord      |  |
|  +-----------------------------------------------------------------------+  |
|       |                    ^                                                |
|  +--[D8: EVENT & RUNTIME BACKBONE (Kafka + Outbox)]---------------------+   |
|  | FastAPI | WebSocket | Transactional Outbox -> Kafka Topics           |   |
|  | SCOFEvent Contract | Consumer Idempotency | Aggregate Versioning     |   |
|  | Session State Machine (DB-enforced transitions)                      |   |
|  +----------------------------------------------------------------------+   |
|       |                    ^                    ^                           |
|  +--[DECISION POLICY LAYER]-----------+  +--[D10: EVALUATION]---------+     |
|  | DecisionPolicy (from profile)      |  | B0-B7 Ablation Ladder      |     |
|  | ObjectiveNormalization (direction- |  | Non-parametric statistical |     |
|  |   aware, signed, saturated)        |  |   protocol                 |     |
|  | Policy precedence (6 levels)       |  | Anti-Overfitting Suite     |     |
|  | PolicyIntegrity (content hash)     |  | R_i Calibration            |     |
|  +------------------------------------+  +----------------------------+     |
|                  |                                                          |
|  +================================================================+         |
|  |        LANGGRAPH ORCHESTRATION KERNEL (D6)                     |         |
|  |        + Coordinator (7 decomposed services)                   |         |
|  |        + Snapshot Epoch Allocation                             |         |
|  |                                                                |         |
|  |  [Ingest] -> [Snapshot] -> [RAG T1] -> [Route] -> [Bind] ->    |         |
|  |  -> [Fan-Out (independent)] -> [Fan-In] ->                     |         |
|  |  -> [Cross-Exam (targeted, bounded)] ->                        |         |
|  |  -> [Evidence Sufficiency Gate (tiered criticality)] ->        |         |
|  |  -> [Candidate Extraction] -> [Normalization Pipeline] ->      |         |
|  |  -> [THREE-TIER IMPACT EVALUATION] ->                          |         |
|  |  -> [Twin Requirement Classification] ->                       |         |
|  |  -> [Twin Simulation (Tier 3)] ->                              |         |
|  |  -> [CD2F Arbitration] -> [ExecutionPolicy] ->                 |         |
|  |  -> [STATE REVALIDATION] -> [Execute/Escalate]                 |         |
|  +================================================================+         |
|       |              |              |              |              |         |
|  +===================================================================+      |
|  |     LANGCHAIN AGENT REASONING LAYER (D3/D4)                       |      |
|  |     + Agent-Internal Tier-2 RAG (MCP-Governed)                    |      |
|  |     + DomainOwnershipPolicy enforcement (validated contracts)     |      |
|  |     + ActionIntent (decision params, NOT impact estimates)        |      |
|  |                                                                   |      |
|  | +-------------------+ +-------------------+ +-------------------+ |      |
|  | | Demand &          | | Inventory &       | | Procurement &     | |      |
|  | | Commerce          | | Asset Mgmt        | | Supplier          | |      |
|  | +-------------------+ +-------------------+ +-------------------+ |      |
|  | +-------------------+ +-------------------+ +-------------------+ |      |
|  | | Logistics &       | | Financial &       | | Risk &            | |      |
|  | | Transport         | | Enterprise Value  | | Resilience        | |      |
|  | +-------------------+ +-------------------+ +-------------------+ |      |
|  +===================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DELIBERATION TABLE (Event-Sourced Cognitive Workspace)     |      |
|  |     Events: PostgreSQL (append-only, sequence-allocated)       |      |
|  |     Views:  Redis (materialized, snapshot-aware cache keys)    |      |
|  |     Transport: Kafka (via outbox, keyed by session_id)         |      |
|  |     State machine: explicit transitions, DB-enforced           |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     IMPACT EVALUATION SERVICE                                  |      |
|  |     Tier 1: BaselineImpact (authoritative facts)               |      |
|  |     Tier 2: PredictiveImpactEstimate (domain models)           |      |
|  |     LLM numbers NEVER enter this computation                   |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DIGITAL TWIN -- COUNTERFACTUAL EVALUATOR (D7)             |      |
|  |     Tier 3: Counterfactual simulation results                  |      |
|  |     Requirement: REQUIRED / RECOMMENDED / ADVISORY             |      |
|  |     Authority: ONLY within isolated Layer-3 scenario scope     |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     CD2F EVIDENCE-BASED ARBITRATION ENGINE (D7)               |      |
|  |     Objective: DecisionObjective (from DecisionPolicy)         |      |
|  |     Normalization: Direction-aware, signed, with saturation    |      |
|  |     Pareto: Proper frontier computation                        |      |
|  |     Labels: SINGLETON_FRONTIER / POLICY_WEIGHT_RESOLVED /      |      |
|  |             GENUINE_PARETO_AMBIGUITY                           |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     D1 + D2: ENTERPRISE DATA FABRIC (Frozen Baseline)         |      |
|  |     PostgreSQL: System of Record                               |      |
|  |     Neo4j: Topology projection (derived)                       |      |
|  |     pgvector: Semantic precedent memory                        |      |
|  |     Redis: Governed cache (fail-closed for critical evidence)  |      |
|  |     Snapshot epochs: common consistency coordinate              |      |
|  +=================================================================+      |
|                                                                             |
+=============================================================================+
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

The single source of truth for ALL action-related metadata. Replaces the separate ActionTypeRegistry and ActionDefinition from earlier drafts.

```python
class ActionRegistryEntry(BaseModel):
    """Single canonical definition of an action type.
    ALL action-related metadata lives here."""
    
    # Identity
    action_type: str
    display_name: str
    description: str
    
    # Domain Classification
    primary_domain: str
    
    # Ownership
    primary_owner_agent: str
    permitted_proposers: list[str]
    parameter_authority: str
    
    # Typed Schema Binding
    intent_schema_class: str
    
    # Impact Evaluation
    impact_evaluation_tier: Literal[
        "BASELINE_ONLY",
        "BASELINE_AND_PREDICTIVE",
    ]
    
    # Twin Simulation
    simulatable: bool
    twin_handler_id: Optional[str]
    
    # Execution
    execution_capability_id: Optional[str]   # None for advisory actions
    advisory_only: bool
    
    def validate(self) -> list[str]:
        errors = []
        if self.advisory_only and self.execution_capability_id is not None:
            errors.append(f"{self.action_type}: advisory_only=True but execution_capability_id set")
        if not self.advisory_only and self.execution_capability_id is None:
            errors.append(f"{self.action_type}: advisory_only=False but no execution_capability_id")
        if self.simulatable and self.twin_handler_id is None:
            errors.append(f"{self.action_type}: simulatable=True but no twin_handler_id")
        if not self.simulatable and self.twin_handler_id is not None:
            errors.append(f"{self.action_type}: simulatable=False but twin_handler_id set")
        return errors


class ActionRegistry:
    """Singleton registry. Loaded and validated at startup."""
    
    _entries: dict[str, ActionRegistryEntry] = {}
    
    @classmethod
    def register(cls, entry: ActionRegistryEntry) -> None:
        if entry.action_type in cls._entries:
            raise ValueError(f"Duplicate: {entry.action_type}")
        cls._entries[entry.action_type] = entry
    
    @classmethod
    def get(cls, action_type: str) -> ActionRegistryEntry:
        if action_type not in cls._entries:
            raise KeyError(f"'{action_type}' not registered")
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

### Canonical Action Definitions

```yaml
actions:
  # ---- Logistics Domain ----
  reroute_shipment:
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  expedite_shipment:
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  change_freight_mode:
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  # ---- Procurement Domain ----
  switch_supplier:
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  increase_purchase_order:
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  cancel_purchase_order:
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  expedite_purchase_order:
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  # ---- Inventory Domain ----
  reallocate_inventory:
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  adjust_safety_stock:
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset, demand_commerce]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  quarantine_inventory:
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset, risk_resilience]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  # ---- Demand Domain ----
  promotion_adjustment:
    primary_domain: demand_commerce
    primary_owner_agent: demand_commerce
    permitted_proposers: [demand_commerce]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  demand_signal_override:
    primary_domain: demand_commerce
    primary_owner_agent: demand_commerce
    permitted_proposers: [demand_commerce]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  # ---- Risk Domain ----
  risk_mitigation_recommendation:
    primary_domain: risk_resilience
    primary_owner_agent: risk_resilience
    permitted_proposers: [risk_resilience]
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    advisory_only: true

  compliance_hold:
    primary_domain: risk_resilience
    primary_owner_agent: risk_resilience
    permitted_proposers: [risk_resilience]
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    advisory_only: false

  # ---- Finance Domain ----
  financial_impact_flag:
    primary_domain: financial_enterprise
    primary_owner_agent: financial_enterprise
    permitted_proposers: [financial_enterprise]
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    advisory_only: true

  budget_escalation:
    primary_domain: financial_enterprise
    primary_owner_agent: financial_enterprise
    permitted_proposers: [financial_enterprise]
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    advisory_only: true

  # ---- Universal ----
  do_nothing:
    primary_domain: universal
    primary_owner_agent: coordinator
    permitted_proposers: [coordinator]
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: true
    advisory_only: false
```

---

## 8. Registry Startup Validation

All three registries (ClaimType, EvidenceClass, ActionRegistry) are cross-validated at system startup. If any validation returns errors, the system MUST NOT start.

```python
def validate_claim_registry(agent_cards: list[AgentCard]) -> list[str]:
    """Validates all agent contracts reference registered claim types
    and valid source agents. Fail-open bug fixed: nonexistent source
    agents produce explicit errors."""
    
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
    """Full cross-registry validation at startup."""
    
    errors = registry.validate_all()
    agent_ids = {card.agent_id for card in agent_cards}
    
    for entry in registry._entries.values():
        if entry.simulatable and entry.twin_handler_id not in twin_handlers:
            errors.append(f"{entry.action_type}: twin_handler '{entry.twin_handler_id}' not found")
        if entry.execution_capability_id and entry.execution_capability_id not in execution_capabilities:
            errors.append(f"{entry.action_type}: capability '{entry.execution_capability_id}' not found")
        if entry.primary_owner_agent not in agent_ids and entry.primary_owner_agent != "coordinator":
            errors.append(f"{entry.action_type}: owner '{entry.primary_owner_agent}' not found")
        for proposer in entry.permitted_proposers:
            if proposer not in agent_ids and proposer != "coordinator":
                errors.append(f"{entry.action_type}: proposer '{proposer}' not found")
    
    return errors
```

---

# PART III: AGENT LAYER (D3/D4)

---

## 9. Agent Roster: Six Specialists + Coordinator

The enterprise surface is consolidated into 6 specialist agents plus a Coordinator. Each specialist governs a logical operational cluster consuming multiple data domains. The roster was refined through Amendments 1-4: Risk & Compliance renamed to Risk & Resilience, Financial Operations reframed as Financial & Enterprise Value, supplier financial health ownership clarified.

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
|       |                                                                     |
|       +-- [4] LOGISTICS & TRANSPORT AGENT                                   |
|       |      Core Question: Can we move it?                                 |
|       |      Domains: Transport Lanes, Shipments, Carriers, Fleet Assets,   |
|       |               Route Optimization, Freight Modes, Corridor Status   |
|       |                                                                     |
|       +-- [5] FINANCIAL & ENTERPRISE VALUE AGENT                            |
|       |      Core Question: What is the economic consequence of this        |
|       |        decision?                                                    |
|       |      Purpose: Economic consequence modeling, NOT accounting          |
|       |      Outputs: Landed cost, working capital, cash impact,            |
|       |               margin impact, penalty exposure, expedite cost        |
|       |                                                                     |
|       +-- [6] RISK & RESILIENCE AGENT                                       |
|              Core Question: What systemic downside, constraint violation,   |
|                or cascading failure could this decision introduce?          |
|              Domains: External threats, Supplier concentration risk,         |
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

### Coordinator Responsibilities

The Coordinator is the meta-orchestrator. It is NOT an agent. It does NOT produce claims, recommendations, or opinions.

| Responsibility | Description |
| :--- | :--- |
| **Deliberation Table Management** | Creates sessions, posts items, manages lifecycle |
| **Domain Affinity Routing** | Computes probabilistic scores, assigns agents |
| **Tier-1 RAG Pre-Retrieval** | Broad, shallow context retrieval for base context package |
| **Capability Resolution** | Invokes Dynamic Capability Registry to bind tools per agent per task |
| **Cross-Examination Mediation** | Routes critiques between agents via the table |
| **Evidence Sufficiency Gating** | Validates that mandatory domains are represented before CD2F |
| **Twin Simulation Dispatch** | Extracts candidate actions, dispatches to Twin |
| **Consensus Hand-Off** | Assembles decision package and submits to CD2F |
| **Snapshot Epoch Allocation** | Atomically allocates common snapshot epochs |
| **Audit Emission** | Emits complete deliberation transcript to D9 |

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

Per-agent ownership contract definitions (complete YAML for all six agents) are specified in Amendment 2 Section 4.2.

---

## 11. Agent Cognitive Runtime: Hybrid ML + LLM

Each agent runs a bounded reasoning chain combining traditional ML pipelines with LLM reasoning.

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
START
    |
    v
ingest_and_route
    |
    v
create_decision_snapshot              (capture world-state boundary, allocate epoch)
    |
    v
tier1_rag_preretrieval
    |
    v
capability_bind
    |
    v
parallel_fan_out                       (agents receive snapshot + base context ONLY,
    |                                    NOT other agents' claims -- independence)
    v
fan_in_collate
    |
    v
cross_examination                      (targeted: agents see ONLY relevant conflicts,
    |                                    not all claims -- reduces conformity bias)
    v
[CONDITIONAL: blocking_critiques?]
    +-- YES: revision_round -> fan_in_revised
    +-- NO:  proceed
    |
    v
evidence_sufficiency_gate              (BEFORE expensive simulation)
    |
    v
[CONDITIONAL: sufficient?]
    +-- INSUFFICIENT:     hitl_escalation -> END
    +-- MARGINALLY:       proceed (with caution flag)
    +-- SUFFICIENT:       proceed
    |
    v
candidate_extraction
    |
    v
candidate_normalization                (schema/entity/constraint/dedup/prune/budget)
    |
    v
three_tier_impact_evaluation           (Tier 1: Baseline + Tier 2: Predictive)
    |
    v
[CONDITIONAL: twin_simulation_needed?]
    +-- YES: twin_dispatch -> twin_collect
    |        |
    |        v
    |        [CONDITIONAL: unexpected_outcome?]
    |            +-- YES (first time): targeted_re_deliberation
    |            |                     -> re_normalize -> re_simulate
    |            +-- NO / YES (second time): proceed
    +-- NO:  proceed
    |
    v
cd2f_arbitration
    |
    v
[CONDITIONAL: cd2f_result_tier?]
    +-- TIER_1: execution_policy_check -> state_revalidation
    |           -> execute_or_hitl -> archive -> END
    +-- TIER_2: extended_deliberation -> parallel_fan_out (cycle, max 1)
    +-- TIER_3: hitl_escalation -> await_human
    |           -> execute_or_hitl -> archive -> END
    +-- NO_FEASIBLE: hitl_escalation -> END
    +-- PARETO:      hitl_with_tradeoff_summary -> await_human -> archive -> END
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

### Verdict Logic (Strict Precedence)

```
SUFFICIENT:
    hard_critical_all_met == True
    AND degraded_critical_all_met == True
    AND domain_coverage.coverage_score >= policy.min_domain_coverage
    AND evidence_quality.avg_evidence_freshness >= policy.min_evidence_freshness
    AND consistency.contradiction_severity != "BLOCKING"
    AND evidence_quality.model_validity_score >= 0.50
    
    -> Full autonomy available.

MARGINALLY_SUFFICIENT:
    hard_critical_all_met == True                      # HARD tier must be met
    AND degraded_critical_present >= degraded_critical_required
    AND degraded_critical_sufficient < degraded_critical_required
    AND domain_coverage.coverage_score >= 0.60
    AND consistency.contradiction_severity != "BLOCKING"
    
    -> Autonomy capped at Tier-2, HITL notification.

INSUFFICIENT:
    hard_critical_all_met == False
    OR hard_critical_present < hard_critical_required
    OR consistency.contradiction_severity == "BLOCKING"
    
    -> NO autonomous decision. HITL escalation mandatory.
```

Key invariant: HARD_CRITICAL failures always produce INSUFFICIENT. No overlap between MARGINALLY_SUFFICIENT and INSUFFICIENT.

---

## 23. Priority and SLA: Two-Dimensional Model

### Business Priority

| Priority | Description | Examples |
| :--- | :--- | :--- |
| **P0: Critical** | System emergency, safety, regulatory | Cold-chain breach, critical supplier force majeure |
| **P1: High** | Human-escalated, active disruption | Operator query, CD2F Tier-3 escalation |
| **P2: Normal** | Routine agent deliberation | Standard disruption handling |
| **P3: Background** | Analytics, risk scanning, batch | Periodic supplier risk scan |

### Execution SLA

| SLA | Description | Target Latency |
| :--- | :--- | :--- |
| **S0: Real-time** | Deterministic safety rules, no LLM | < 100ms |
| **S1: Interactive** | Human-facing response expected | < 2s |
| **S2: Operational** | Standard deliberation cycle | < 5s per agent |
| **S3: Analytical** | Batch/background processing | < 30s |

SLA target values are benchmark targets, not architectural guarantees. D10 benchmarks calibrate actual achievable latency.

### P0 Dual-Path Architecture

```
P0 event arrives
    |
    +---> FAST PATH (S0): Deterministic safety rule
    |     - Pre-defined rule engine (no LLM)
    |     - Executed immediately (< 100ms)
    |     - Applied to Twin Layer 3
    |
    +---> COGNITIVE PATH (S2): Full agent deliberation
          - Standard 6-stage pipeline
          - Runs in parallel with fast path
```

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

```
STEP 1: EXTRACT
    Collect all candidate actions from all revised agent proposals.

STEP 2: SCHEMA VALIDATION
    Validate intent against typed ActionIntent schema.
    Validate action_type exists in ActionRegistry.
    Validate proposer is in permitted_proposers.

STEP 3: ENTITY VALIDATION
    Verify all referenced entity IDs exist in D2 as of the snapshot.

STEP 4: THREE-TIER IMPACT EVALUATION
    Compute Tier 1 BaselineImpact (from authoritative facts).
    Compute Tier 2 PredictiveImpactEstimate (from domain models, where applicable).

STEP 5: HARD-CONSTRAINT PRE-CHECK
    Eliminate candidates violating hard constraints.
    Uses ONLY Tier 1 BaselineImpact values.

STEP 6: DEDUPLICATION
    Merge semantically identical candidates from different agents.

STEP 7: DOMINANCE PRUNING
    A candidate is dominated ONLY if:
        - BOTH have complete Tier 1 BaselineImpact
        - Strictly worse on ALL Tier 1 dimensions
        - Safety margin applies
    Tier 2 is NEVER used for dominance pruning.

STEP 8: CANDIDATE BUDGET SELECTION (HEURISTIC)
    UCB(c) = weighted_score(Tier1 + Tier2) + alpha * uncertainty(c)
    ALWAYS include do-nothing baseline.
    ALWAYS include at least one candidate per assigned domain.
    Maximum output: max_simulation_branches + 1 (baseline)

STEP 9: COMBINATION SYNTHESIS (if warranted)
    Generate composite candidates from non-conflicting actions across domains.
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

### Formal Arbitration Process

```
STAGE 1: FEASIBILITY FILTER
    Eliminate candidates violating hard constraints.
    If no feasible candidates -> CD2F_NO_FEASIBLE_ACTION -> HITL

STAGE 2: OBJECTIVE SCORE
    For each feasible candidate c:
        For each metric m in ObjectiveNormalization.metrics:
            utility(c, m) = m.normalize(raw_value)   # Direction-aware
        J(c) = SUM(m.weight * utility(c, m))
    
    Soft constraint penalties applied.

STAGE 3: UNCERTAINTY ADJUSTMENT
    J_final(c) = J(c) - lambda * uncertainty(c)

STAGE 4: PARETO CHECK
    Sort by J_final descending.
    Apply Pareto frontier computation.
    Classify: SINGLETON_FRONTIER / POLICY_WEIGHT_RESOLVED / GENUINE_PARETO_AMBIGUITY

STAGE 5: EXECUTION AUTHORIZATION
    Proceed to ExecutionPolicyService (separate gate).
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

```
SINGLETON_PARETO_FRONTIER:
    Pareto frontier has exactly one member.

POLICY_WEIGHT_RESOLVED:
    Multiple Pareto-optimal candidates; policy weights select one.

GENUINE_PARETO_AMBIGUITY:
    Real trade-off; no clear winner. HITL escalation.
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
PostgreSQL
    +-- Enterprise truth (D1/D2 System of Record)
    +-- Deliberation state (events, sessions)
    +-- Agent evaluation metrics (R_i data)
    +-- Outbox table (pending Kafka events)

Kafka
    +-- Event backbone (transport, replay, distribution)
    +-- NOT authoritative state

Redis
    +-- Derived cache (populated FROM Kafka consumers)
    +-- Hot deliberation state (mirrors PostgreSQL for active sessions)
    +-- NOT authoritative
    +-- Fail-closed for critical evidence (see Section 59)

Neo4j
    +-- Topology projection (derived from PostgreSQL)

pgvector (inside PostgreSQL)
    +-- Semantic memory (embeddings, precedents)
```

---

## 38. Transactional Outbox Pattern

```
Agent result ----------> PostgreSQL
                              |
                         [Same transaction]
                              |
                         Outbox table INSERT
                              |
                              v
                         Outbox Relay (polls outbox)
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

**Guarantee:** PostgreSQL is always consistent. If PostgreSQL commits a state change, the corresponding event intent is also durably persisted. Kafka provides at-least-once distribution via the outbox relay. Consumers achieve effective exactly-once state transitions through idempotent processing with aggregate version checks.

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

All topics receive events via the transactional outbox. Partition key = session_id for ordering within a decision session.

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
+=============================================================================+
|  Component           | ERP Write | Twin Write | DB Write | Deliberation   |
|  --------------------|-----------|------------|----------|----------------|
|  Agent               |    NO     |    NO      |   NO     | Post verdicts  |
|  Coordinator         |    NO     |    NO      |   NO*    | Manage items   |
|  CD2F                |    NO     |    NO      |   NO     | Post decision  |
|  Twin                |    NO     | SCENARIO   |   NO     | --             |
|  Execution Adapter   |   YES**   |    NO      |   NO     | --             |
|                                                                             |
|  * Coordinator writes ONLY to deliberation_* tables                        |
|  ** Execution Adapter requires HITL or policy authorization                |
|                                                                             |
|  THREE KINDS OF "EXECUTION" (never collapse):                              |
|  1. Simulation execution: Twin (ephemeral scenario state)                  |
|  2. Decision execution: CD2F -> approved decision object                   |
|  3. Real-world execution: Execution Adapter -> ERP/TMS/WMS (gated)       |
+=============================================================================+
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
+=============================================================================+
|                   SCOF V2 COGNITIVE DECISION FABRIC                        |
|         (D3 through D10 -- Contract Freeze Final Draft)                    |
+=============================================================================+
|                                                                             |
|  TEN ARCHITECTURAL INVARIANTS (Frozen)                                      |
|  Source Authority | Cognitive Workspace | Evidence Sufficiency |             |
|  Candidate Discipline | Counterfactual Isolation | Decision Authority |     |
|  Policy Authority | State Freshness | Execution Safety | Replayability |    |
|                                                                             |
|  +--[CANONICAL REGISTRIES]-----------------------------------------------+ |
|  | ClaimTypeRegistry | EvidenceClass (6 classes) | ActionRegistry         | |
|  | (Unified: single source of truth for claims, evidence, actions)       | |
|  | (Cross-validated at startup; system MUST NOT start if invalid)         | |
|  +-----------------------------------------------------------------------+ |
|                                                                             |
|  +--[D9: OBSERVABILITY, EXPLAINABILITY & DESKTOP CONSOLE]----------------+ |
|  | Tauri v2 Desktop Console                                                | |
|  | Decision Trace: trigger -> snapshot -> RAG -> ML -> LLM -> claims ->    | |
|  |   critiques -> candidates -> normalization -> simulation -> CD2F ->      | |
|  |   decision -> execution                                                  | |
|  | HITL Escalation Interface | What-If Lab | Evidence Visualization        | |
|  | Trade-off Explanation Rendering | DecisionRecord Archival               | |
|  | OutcomeObservation (structured) | CriticalitySensitivityReport          | |
|  | Replay: TRACE / LOGICAL / MODEL / EXACT_SYSTEM (bounded fidelity)       | |
|  +-----------------------------------------------------------------------+ |
|       |                    ^                                                |
|  +--[D8: EVENT & RUNTIME BACKBONE]--------------------------------------+ |
|  | FastAPI Gateway | WebSocket Broadcast                                   | |
|  | Transactional Outbox -> Kafka Topics (keyed by session_id)              | |
|  | SCOFEvent Contract (event_id, aggregate_version, causation_id)          | |
|  | Consumer Idempotency (aggregate version checks)                         | |
|  | Session State Machine: CREATED->ACTIVE->{CLOSED|CANCELLED|EXPIRED}      | |
|  | DB Constraints: UNIQUE(session_id, sequence_number)                      | |
|  | State transitions: single transaction + FOR UPDATE lock                  | |
|  +-----------------------------------------------------------------------+ |
|       |                    ^                    ^                           |
|  +--[DECISION POLICY LAYER]----------+  +--[D10: EVALUATION]----------+ |
|  | DecisionPolicy                     |  | B0-B7 Ablation Ladder       | |
|  |   .objective (DecisionObjective)   |  |   B3: no gate, B4: + gate   | |
|  |   .evidence_policy                 |  | Non-parametric statistical   | |
|  |   .deliberation_policy             |  |   protocol (distribution-   | |
|  |   .simulation_policy               |  |   light)                    | |
|  |   .routing_policy                  |  | ECE/Brier acceptance        | |
|  |   .reliability_policy              |  |   thresholds                | |
|  |   .execution_policy                |  | Anti-Overfitting Suite:     | |
|  |   .priority_sla_policy             |  |   held-out scenarios,       | |
|  | ObjectiveNormalization:            |  |   parameter perturbation,   | |
|  |   direction-aware, signed,        |  |   distribution shift,       | |
|  |   saturation (CLIP/LOG_COMPRESS)  |  |   noise injection           | |
|  | Policy precedence (6 levels)      |  | RQ1-RQ4 benchmarks          | |
|  | PolicyIntegrity (content hash     |  +------------------------------+ |
|  |   excluding self-reference)       |                                    |
|  +------------------------------------+                                    |
|                  |                                                          |
|  +=================================================================+      |
|  |        LANGGRAPH ORCHESTRATION KERNEL (D6)                     |      |
|  |        + Coordinator (decomposed into 7 services):             |      |
|  |          RoutingService | DeliberationService |                 |      |
|  |          EvidenceSufficiencyService | CandidateService |        |      |
|  |          SimulationDispatchService | AuditService |             |      |
|  |          ExecutionPolicyService                                 |      |
|  |        + Snapshot Epoch Allocation (atomic, common coordinate)  |      |
|  |        + Session Overlap Detection                             |      |
|  |                                                                 |      |
|  |  Pipeline (canonical ordering):                                 |      |
|  |  [Ingest & Route]                                               |      |
|  |    -> [Create DecisionSnapshot (allocate epoch)]                |      |
|  |    -> [Tier-1 RAG Pre-Retrieval (broad, shallow)]               |      |
|  |    -> [Capability Bind (Dynamic Capability Registry)]           |      |
|  |    -> [Fan-Out (independent: no cross-agent visibility)]        |      |
|  |    -> [Fan-In (collate proposals)]                              |      |
|  |    -> [Cross-Examination (targeted, bounded, 2 rounds max)]     |      |
|  |    -> [Evidence Sufficiency Gate (tiered criticality)]           |      |
|  |         HARD_CRITICAL / DEGRADED_CRITICAL / IMPORTANT           |      |
|  |         Verdict: SUFFICIENT / MARGINALLY / INSUFFICIENT         |      |
|  |    -> [Candidate Extraction]                                    |      |
|  |    -> [Candidate Normalization Pipeline (9 steps)]              |      |
|  |         Schema -> Entity -> Impact(T1+T2) -> Hard Constraint    |      |
|  |         -> Dedup -> Dominance(T1 only) -> Budget(UCB heuristic) |      |
|  |         -> Combination Synthesis                                |      |
|  |    -> [Twin Requirement Classification]                         |      |
|  |         (unified SimulationMaterialityThresholds)               |      |
|  |    -> [Twin Simulation (Tier 3: counterfactual)]                |      |
|  |         (optional EXPLORE->DELIBERATE loop, max 1)              |      |
|  |    -> [CD2F Arbitration]                                        |      |
|  |         Direction-aware normalization | Proper Pareto           |      |
|  |         SINGLETON_FRONTIER / POLICY_WEIGHT_RESOLVED /           |      |
|  |         GENUINE_PARETO_AMBIGUITY                                |      |
|  |    -> [ExecutionPolicy Evaluation (separate gate)]              |      |
|  |    -> [STATE REVALIDATION (epoch drift check)]                  |      |
|  |    -> [Execute / Escalate / Archive]                            |      |
|  +=================================================================+      |
|       |              |              |              |              |         |
|  +=================================================================+      |
|  |     LANGCHAIN AGENT REASONING LAYER (D3/D4)                   |      |
|  |     Framework split:                                           |      |
|  |       LangGraph = macro workflow orchestration                 |      |
|  |       LangChain = agent-level cognitive engine                 |      |
|  |     + Agent-Internal Tier-2 RAG (MCP-Governed)                |      |
|  |     + Two-Class Retrieval (MCP + local hot-path cache)        |      |
|  |     + DomainOwnershipPolicy enforcement (validated contracts) |      |
|  |     + ActionIntent (decision params, NOT impact estimates)    |      |
|  |     + AgentInfluenceStatus (FULL/REDUCED/ADVISORY)            |      |
|  |     + Hybrid ML + Bounded LLM per agent                      |      |
|  |     + ReasoningService abstraction (model-agnostic)           |      |
|  |     + Deterministic fallback on LLM failure                   |      |
|  |                                                                 |      |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  | | [1] Demand &      | | [2] Inventory &   | | [3] Procurement & |     |
|  | | Commerce          | | Asset Mgmt        | | Supplier          |     |
|  | | [validated card]  | | [validated card]  | | [validated card]  |     |
|  | | [ML + Bounded LLM]| | [ML + Bounded LLM]| | [ML + Bounded LLM]|     |
|  | | [two-class RAG]   | | [two-class RAG]   | | [two-class RAG]   |     |
|  | | [domain re-rank]  | | [domain re-rank]  | | [domain re-rank]  |     |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  |                                                                 |      |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  | | [4] Logistics &   | | [5] Financial &   | | [6] Risk &        |     |
|  | | Transport         | | Enterprise Value  | | Resilience        |     |
|  | | [validated card]  | | [validated card]  | | [validated card]  |     |
|  | | [ML + Bounded LLM]| | [ML + Bounded LLM]| | [ML + Bounded LLM]|     |
|  | | [two-class RAG]   | | [two-class RAG]   | | [two-class RAG]   |     |
|  | | [domain re-rank]  | | [domain re-rank]  | | [domain re-rank]  |     |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  |                                                                 |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DELIBERATION TABLE (Event-Sourced Cognitive Workspace)     |      |
|  |                                                                 |      |
|  |  Core Rules:                                                    |      |
|  |    1. No agent-to-agent direct communication                    |      |
|  |    2. Workspace for decision artifacts, NOT enterprise truth    |      |
|  |    3. Coordinator is chairperson                                |      |
|  |                                                                 |      |
|  |  Events:     PostgreSQL (append-only, immutable)               |      |
|  |              UNIQUE(session_id, sequence_number) enforced       |      |
|  |  Views:      Redis (materialized session projection)           |      |
|  |              Cache key: {session_id}:{epoch}:{sequence}        |      |
|  |  Transport:  Kafka (via outbox, keyed by session_id)           |      |
|  |  Replay:     replay_session(session_id, up_to_sequence)        |      |
|  |  State:      Session state machine with DB-enforced transitions |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     IMPACT EVALUATION SERVICE                                  |      |
|  |                                                                 |      |
|  |  Tier 1: BaselineImpact                                        |      |
|  |    Source: PostgreSQL, rate tables, contract terms               |      |
|  |    Nature: Deterministic derivation from authoritative facts    |      |
|  |    Used for: Hard constraint check, dominance pruning           |      |
|  |                                                                 |      |
|  |  Tier 2: PredictiveImpactEstimate                               |      |
|  |    Source: Validated domain models                               |      |
|  |    Nature: Statistical prediction with confidence intervals     |      |
|  |    Used for: UCB budget selection, pre-Twin scoring             |      |
|  |    NOT used for: dominance pruning                              |      |
|  |                                                                 |      |
|  |  LLM numbers NEVER enter this computation                      |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DIGITAL TWIN -- COUNTERFACTUAL EVALUATOR (D7)             |      |
|  |                                                                 |      |
|  |  Tier 3: Counterfactual simulation results                     |      |
|  |  Requirement Classification:                                    |      |
|  |    REQUIRED (financial >$200k, cascade >0.70, novelty >0.80)   |      |
|  |    RECOMMENDED (financial >$10k, service >0.15, risk >0.50)    |      |
|  |    ADVISORY (below all thresholds)                              |      |
|  |  REQUIRED + timeout -> HITL (no autonomous CD2F)               |      |
|  |  Produces: SimulationResult + SimulationManifest               |      |
|  |  Authority: ONLY within isolated Layer-3 scenario scope        |      |
|  |  Branch lifecycle: active -> archive -> GC after retention      |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     CD2F EVIDENCE-BASED ARBITRATION ENGINE (D7)               |      |
|  |                                                                 |      |
|  |  Inputs: candidates + evidence + simulation + policy            |      |
|  |  Process:                                                       |      |
|  |    1. FEASIBILITY FILTER (hard constraints)                     |      |
|  |    2. OBJECTIVE SCORE (direction-aware normalization)            |      |
|  |       J(c) = SUM(w_m * utility(c,m)) - soft_penalty             |      |
|  |    3. UNCERTAINTY ADJUSTMENT                                    |      |
|  |       J_final(c) = J(c) - lambda * uncertainty(c)               |      |
|  |    4. PARETO CHECK (proper Pareto frontier)                     |      |
|  |       SINGLETON_FRONTIER / POLICY_WEIGHT_RESOLVED /             |      |
|  |       GENUINE_PARETO_AMBIGUITY                                  |      |
|  |    5. -> ExecutionPolicy (separate gate)                        |      |
|  |    6. -> StateRevalidation (epoch drift check)                  |      |
|  |  Output: selected action + justification + trade-off summary   |      |
|  |  Pure computation: no LLM, no retrieval, no Twin calls          |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     D1 + D2: ENTERPRISE DATA FABRIC (Frozen Baseline)         |      |
|  |                                                                 |      |
|  |  PostgreSQL: System of Record (operational facts, 96 tables)   |      |
|  |  Neo4j:      Topology projection (3.73M nodes, derived)       |      |
|  |  pgvector:   Semantic precedent memory (384-dim embeddings)    |      |
|  |  Redis:      Governed cache (fail-closed for critical evidence)|      |
|  |  Snapshot epochs: common consistency coordinate                |      |
|  |    (replaces heterogeneous LSN arithmetic)                      |      |
|  +=================================================================+      |
|                                                                             |
|  CROSS-CUTTING INFRASTRUCTURE:                                             |
|  Kafka  = event backbone (via outbox, at-least-once, idempotent)          |
|  MCP    = governed capability access (versioned, side-effect classified)  |
|  A2A    = agent task contract + health + capability                       |
|  Redis  = governed cache (policy-level governance, fail-closed)           |
|                                                                             |
+=============================================================================+
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

**Build:** Candidate normalization pipeline (9-step), three-tier impact evaluation, Twin simulation dispatch with SimulationManifest, CD2F formal objective function (direction-aware), Pareto analysis, execution authorization separation, R_i governance, state revalidation.

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
- ClaimTypeRegistry, EvidenceClass, ActionRegistry (unified)
- DomainOwnershipPolicy contracts
- Three-tier impact model (Baseline / Predictive / Counterfactual)
- Tiered criticality model (HARD_CRITICAL / DEGRADED_CRITICAL / IMPORTANT / SUPPLEMENTARY)
- Common snapshot epoch consistency model
- Full session restart on snapshot advancement (no partial restart)
- Direction-aware signed normalization with saturation policy
- Candidate Budget Selection (UCB heuristic, explicitly not a safety proof)
- Unified SimulationMaterialityThresholds
- Event-sourced Deliberation Table
- Session state machine with explicit transition matrix
- Content-addressable policy hashing (excluding integrity metadata)
- State revalidation before execution
- Corrected B0-B7 ablation ladder (B3/B4 separation)
- Proposition-specific evidence authority
- Execution authorization separation (CD2F vs ExecutionPolicyService)
- DecisionRecord as immutable business artifact
- Replay manifest with bounded fidelity classification

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

> This document represents the consolidated, contract-frozen architecture for SCOF V2 D3-D10 implementation. All P0 blockers from the four amendment cycles are resolved. The vocabulary is closed. The mathematical model is corrected. The state semantics are internally consistent. The evaluation protocol is formalized. The scope is explicitly bounded. The architecture is ready for D3 implementation.
