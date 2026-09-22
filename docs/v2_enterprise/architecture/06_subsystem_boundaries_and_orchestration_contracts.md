# Subsystem Boundaries & Orchestration Contracts

## 1. Executive Summary & Architectural Separation of Concerns

A primary failure mode identified during the architectural evaluation of SCOF V2 was **Subsystem Scope Creep**: the tendency for the Digital Twin Service to absorb agent coordination, consensus arbitration, prompt management, and physical database writes into a monolithic, unmaintainable substrate.

To maintain modularity, testability, and enterprise scalability, SCOF enforces strict subsystem boundaries:

```text
+-------------------------------------------------------------------------------+
|                            SYSTEM SUBSYSTEM MATRIX                            |
+===============================================================================+
| SUBSYSTEM                 | CORE RESPONSIBILITY            | EXPLICIT BOUNDARY|
+---------------------------+--------------------------------+------------------+
| Digital Twin Service      | Authoritative State & Physics  | NO orchestration |
| (Operational Substrate)   | Forward Propagation & Sandbox  | NO consensus     |
|                           | Invariant Enforcement          | NO ERP writes    |
+---------------------------+--------------------------------+------------------+
| LangGraph Orchestration   | Cognitive Workflow State Graph | NO direct physics|
| Kernel                    | Agent Turn-Taking & Fan-Out    | NO consensus calc|
|                           | Tool Discovery & Binding       | NO raw DB writes |
+---------------------------+--------------------------------+------------------+
| CD2F Consensus Engine     | Multi-Agent Trade-Off Arbitr.  | NO simulation run|
|                           | Weighted Scoring & Consensus   | NO agent prompts |
|                           | Gated Escalation (Fast/Slow/H) | NO state custody |
+---------------------------+--------------------------------+------------------+
| Enterprise Data Fabric    | System of Record (PostgreSQL)  | NO scenario runs |
| (D1 & D2 Foundations)     | Materialized Topology (Neo4j)  | NO agent logic   |
|                           | Semantic Embeddings (pgvector) | NO dirty writes  |
+---------------------------+--------------------------------+------------------+
| Execution Gateway         | Real-World ERP / WMS / TMS     | Requires HITL    |
| & Adapters                | Integration Adapters           | Isolated gateway |
+===============================================================================+
```

---

## 2. The Digital Twin: What It Owns vs. What It Does NOT Own

```text
+-------------------------------------------------------------------------------+
| TWIN OWNS:                                                                    |
| 1. Authoritative Layer 3 scenario sandbox state.                              |
| 2. Timeline and discrete event queue (event-stepped DES kernel).               |
| 3. Physical & causal invariant enforcement (mass conservation, capacities).   |
| 4. Deterministic forward propagation of disruptions.                          |
| 5. Counterfactual scenario branching and delta calculation.                   |
| 6. Simulated intervention application inside sandbox.                         |
| 7. Deterministic evidence pack generation with SHA-256 digests.               |
+-------------------------------------------------------------------------------+
                                       ||
                                       || STRICT SEPARATION
                                       \/
+-------------------------------------------------------------------------------+
| TWIN DOES NOT OWN:                                                            |
| 1. Agent orchestration, prompt scheduling, or LLM token budgets.              |
| 2. Multi-agent claim deliberation, trade-off scoring, or consensus voting.    |
| 3. Enterprise financial truth (PostgreSQL owns historical & Day-0 books).    |
| 4. Enterprise network topology truth (Neo4j owns authoritative baseline).     |
| 5. Direct write-back to real-world ERP, WMS, or logistics carrier APIs.       |
+-------------------------------------------------------------------------------+
```

---

## 3. Ingress Channels & Orchestration Triggers

Disruptions and events enter the orchestration kernel via three distinct channels:

```text
+-------------------------------------------------------------------------------+
|                             INGRESS CHANNELS                                  |
|                                                                               |
|  [CHANNEL A: Automated Ingress]        [CHANNEL B: Human Escalation]          |
|  - IoT cold-chain sensor alert         - Operations Director reports issue    |
|  - WMS conveyor breakdown webhook      - Desktop console manual entry         |
|  - Carrier EDI transit delay notice    - Tactical priority rebalancing        |
|                                                                               |
|                   [CHANNEL C: Injected Benchmark Scenario]                    |
|                   - D10 empirical evaluation harness                          |
|                   - Stress-test disruption injection                          |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                   LANGGRAPH ORCHESTRATION KERNEL (D05)                        |
|                                                                               |
|   1. Ingress Ingestion & State Initialization                                 |
|   2. Cognitive Query Router & Capability Resolution                           |
|   3. Parallel Fan-Out: Specialist Agents Deliberate Concurrently              |
|      - Demand Agent        -> Assesses customer lift & store stockout risk    |
|      - Inventory Agent     -> Evaluates buffer depletion & safety stocks      |
|      - Supplier Agent      -> Investigates alternate vendor capacity          |
|      - Transport Agent     -> Evaluates alternate corridors & freight modes   |
|   4. Fan-In: Collate Structured Claims into Arbitration Payload               |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                   CD2F DYNAMIC CONSENSUS ENGINE (D06)                         |
|                                                                               |
|   1. Multi-factor weighting: W_i = w_i * c_i                                  |
|   2. Greedy bias override (suppress overconfident single-domain claims)       |
|   3. Tri-tier escalation gating:                                              |
|      - Fast-Path (WCS >= 0.70, low risk)  -> Autonomous sandbox commit        |
|      - Slow-Path (moderate consensus)     -> Secondary what-if refinement     |
|      - HITL Escalation (WCS < 0.70)       -> Desktop Console operator sign-off|
+---------------------------------------+---------------------------------------+
                                        |
                  +---------------------+---------------------+
                  |                                           |
         Approved Scenario Action                     Real-World Actuation
                  |                                           |
                  v                                           v
+-----------------------------------+       +-----------------------------------+
| TWIN SERVICE SANDBOX              |       | EXECUTION ADAPTER (HITL REQUIRED) |
| Applies intervention to Layer 3   |       | Dispatches POs to ERP             |
| Advances DES simulation clock     |       | Books freight with Carrier API    |
+-----------------------------------+       +-----------------------------------+
```

---

## 4. Subsystem Interaction Contracts

### 4.1 Orchestrator to Specialist Agent Contract
Agents are invoked asynchronously using the standard Agent Card contract (see [`agent_card_spec.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/agent_card_spec.md)). Agents interact exclusively through bounded MCP tools dynamically injected by the [Dynamic Capability Registry](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md).

### 4.2 Specialist Agent to CD²F Contract
Specialist agents communicate their proposals using the [Structured Claim Contract](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/structured_claim_contract.md):
```json
{
  "claim_id": "CLM-TRANS-0089",
  "agent_id": "transportation_specialist",
  "disruption_id": "DISR-SUP-0042",
  "proposed_action": {
    "action_type": "reroute_freight",
    "parameters": {
      "po_id": "PO-009142",
      "carrier_id": "CR-0012",
      "mode": "air_freight",
      "incremental_cost": 4200.00
    }
  },
  "confidence_score": 0.88,
  "cost_impact_usd": 4200.00,
  "service_level_delta": 0.08,
  "evidence_pack_id": "evp-88219-4412"
}
```

### 4.3 CD²F to Twin Sandbox Contract
When CD²F reaches consensus, it issues an `ApprovedAction` to the Twin:
```json
{
  "consensus_decision_id": "DEC-CD2F-20260923-01",
  "scenario_id": "scen-disruption-sup-042",
  "weighted_consensus_score": 0.84,
  "escalation_tier": "fast_path",
  "approved_action": {
    "action_type": "reroute_freight",
    "target_po": "PO-009142",
    "parameters": {
      "carrier_id": "CR-0012",
      "mode": "air_freight"
    }
  },
  "timestamp": "2026-09-23T00:46:12Z"
}
```

The Twin validates physical invariants, applies the intervention to Layer 3, advances the simulation clock, and produces an execution receipt.

---

## 5. Architectural Invariants Across Boundaries

1. **No Out-of-Band State Mutation:** An agent can never directly modify PostgreSQL, Neo4j, or Twin state. All proposals must pass through CD²F arbitration.
2. **Deterministic Traceability:** Every decision records the verbatim meeting transcript, all claims, the evidence pack hashes, the CD²F scoring matrix, and the final Twin state delta.
3. **Fail-Safe Containment:** If any specialist agent times out ($> 500\text{ ms}$) or crashes, the LangGraph kernel proceeds with available claims, adjusting CD²F quorum requirements dynamically without freezing the conglomerate.
