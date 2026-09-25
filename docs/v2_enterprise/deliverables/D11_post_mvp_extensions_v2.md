# Deliverable D11 (V2): Modular Extension Agents & Advanced Horizons

## 1. Overview & Objectives

Deliverable D11 expands the SCOF platform beyond the initial four operational specialists into a modular, extensible ecosystem. It defines the formal architectural plug-in interfaces for secondary intelligence agents, cross-enterprise Agent-to-Agent (A2A) protocols, and closed-loop reinforcement learning from deliberation feedback.

---

## 2. Modular Extension Specialists

Under the decoupled architecture established in ADR ADR 003, new specialist agents plug into the platform seamlessly via the standard Agent Card Specification (`agent_card_spec.md`):

### 2.1 Risk & Resilience Agent (`risk-resilience-agent`)
* **Role:** Proactive macro-vulnerability sensing.
* **Domain Focus:** Geopolitical instability, supplier financial default risk, severe weather tracking, and commodity price volatility.
* **Consensus Contribution:** Injects early-warning vulnerability penalties into the CD2F engine before physical disruptions materialize.

### 2.2 Sustainability & ESG Agent (`sustainability-agent`)
* **Role:** Environmental impact auditing and green logistics optimization.
* **Domain Focus:** Scope 1, 2, and 3 carbon emissions ($CO_2\text{e}$), recyclable packaging compliance, and supplier ethical labor certifications.
* **Consensus Contribution:** Challenges high-emission freight rerouting claims (e.g., air-freight expediting) and introduces carbon budget constraints to decision scoring.

---

## 3. External Cross-Enterprise A2A Protocol

While V2 focuses on intra-enterprise orchestration across internal business units, D11 establishes the foundation for **B2B Autonomous Negotiation**:

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│        SCOF RETAIL ENTERPRISE          │       │           EXTERNAL SUPPLIER            │
│   (Internal Multi-Agent Kernel)        │       │             (Vendor Twin)              │
│                                        │       │                                        │
│  ┌──────────────┐     ┌─────────────┐  │       │  ┌─────────────┐     ┌──────────────┐  │
│  │ Demand Agent │ ──► │  Supplier   │  │       │  │ Sales Agent │ ◄── │ Production   │  │
│  └──────────────┘     │    Agent    │  │       │  └──────┬──────┘     │    Agent     │  │
│                       └──────┬──────┘  │       │         │            └──────────────┘  │
└──────────────────────────────┼─────────┘       └─────────┼──────────────────────────────┘
                               │                           │
                               └──────► [ SECURE B2B ] ◄───┘
                                     A2A PROTOCOL
                               - Mutual TLS (mTLS)
                               - Cryptographic Claim Signatures
                               - Automated Price/Slot Negotiation
```

* **Standardized Protocol:** Leverages authenticated, signed JSON-RPC/REST payloads allowing the internal `supplier-agent` to negotiate purchase volumes and delivery windows directly with external supplier agents.
* **Boundary Security:** Internal enterprise databases, cost structures, and store sales are strictly shielded; only contractual order requests and confirmations cross the enterprise boundary.

---

## 4. Reinforcement Learning from Deliberation Feedback (RLDF)

To enable continuous self-improvement, D11 establishes a closed-loop learning pipeline:
1. **Feedback Collection:** Deliberation logs, CD2F arbitration decisions, and human escalation overrides from D09 are aggregated into training datasets.
2. **Outcome Verification:** Actual physical outcomes recorded in `twin_service.py` Layer 3 state (e.g., realized fill rates and financial costs) are compared against agent predictions.
3. **Weight Calibration:** Dynamic regression calibrates agent reliability factors ($R_i$) and domain weights ($w_i$), progressively dampening over-confident or prone-to-error agents.

---

## 5. Architectural Invariants & Integration Rules

1. **Zero Core Disruption:** Adding an extension agent requires only registering a new Agent Card in `agents/cards/` and adding its bounded tools to the MCP registry. The D05 Orchestration Kernel and D06 Consensus Engine require zero code modifications.
2. **SLA Preservation:** Extension agents participate in Phase 2 proposals concurrently, bounded by the same 850 ms deadline, ensuring overall deliberation convergence remains $\le 3.5\text{ s}$.
3. **State Isolation:** Extension agents are strictly subject to Layer 3 write isolation (ADR ADR 002).
