# ADR 025: Five-Tier State Hierarchy and Actuation Boundaries

* **Status**: Accepted

---

## 1. Context and Problem Statement

In an enterprise cognitive orchestration system, confusion easily arises between:
1. What has historically happened (historical fact).
2. What is currently true in the enterprise (baseline operational reality).
3. What could happen under a disruption (simulated scenario projection).
4. What an individual specialist agent proposes (agent recommendation / claim).
5. What the enterprise has decided to do (arbitrated consensus decision).

Furthermore, early blueprints risked conflating simulated sandbox actuation with real-world physical actuation (e.g., an autonomous agent directly firing an automated API call to place a $500,000 purchase order or reroute fleet trucks without human oversight).

A formal state hierarchy and strict actuation boundary were required to maintain operational governance, legal compliance, and benchmark integrity.

---

## 2. Decision Drivers

* **Enterprise Governance & Risk Containment:** Zero unauthorized physical mutations or automated unconstrained expenditures.
* **Semantic Clarity:** Absolute distinction between facts, projections, agent claims, and binding decisions.
* **Auditability & Compliance:** Verifiable provenance connecting every real-world action to its supporting evidence pack and consensus transcript.
* **Human Oversight:** Clear integration points for Human-in-the-Loop (HITL) authorization.

---

## 3. Considered Options

* **Option 1 — Binary State Model (Real vs. Simulated):** Simple two-way split; fails to distinguish between agent opinions, consensus choices, and authoritative baseline data.
* **Option 2 — Fully Autonomous Cyber-Physical Actuation:** Authorize the Digital Twin or consensus engine to call external ERP/WMS APIs directly upon reaching decision thresholds.
* **Option 3 — Five-Tier State Hierarchy with Gated Consensus and HITL Actuation:** Enforce a strict five-tier state hierarchy (Tier 1 Historical Fact, Tier 2 Baseline State, Tier 3 Scenario Projection, Tier 4 Agent Recommendation, Tier 5 CD²F Decision) coupled with an isolated Execution Gateway requiring Human-in-the-Loop sign-off for real-world physical actuation.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Five-Tier State Hierarchy with Gated Consensus and HITL Actuation**

### Rationale:
1. **Semantic Precision:** Every piece of data in the system is explicitly typed into one of the five tiers:
   - **Tier 1 (Historical Fact):** Sealed in files with SHA-256 provenance.
   - **Tier 2 (Baseline State):** Live PostgreSQL Day-0 books and Neo4j baseline.
   - **Tier 3 (Scenario Projection):** Simulated sandbox state in the Twin.
   - **Tier 4 (Agent Recommendation):** Structured claims submitted to CD²F.
   - **Tier 5 (CD²F Decision):** Approved cross-domain arbitration outcome.
2. **Sandbox Actuation vs. Real-World Execution:**
   - Applying an action to **Tier 3 (Scenario Projection)** is purely simulated, safe, and fast.
   - Translating an approved Tier 5 decision into **Real-World Actuation** (SAP/Oracle ERP purchase orders, EDI carrier dispatch) is strictly gated:
     - High-consensus, low-risk actions can execute autonomously in pre-approved test environments.
     - Enterprise-critical actions require operator authorization via the Tauri v2 Desktop Operations Console (D09).
3. **Execution Adapter Isolation:** The Digital Twin Service never possesses credentials or network paths to external ERP production systems. Only isolated Execution Adapters can interface externally.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Eliminates the risk of catastrophic automated actions in physical supply chains.
* Establishes complete, end-to-end legal and operational auditability.
* Clean separation of concerns between simulation sandboxing and physical execution.
* Seamless integration with D07 explainability logs and D09 operations dashboards.

### Negative Consequences / Trade-offs:
* Real-world operational actuation introduces human latency when HITL escalation is triggered.
* Required building a dedicated Execution Gateway interface rather than direct API calls.

---

## 6. Implementation & Compliance Notes

* Architectural specification in [State Isolation & Evidence Fabric Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/05_state_isolation_and_evidence_fabric.md) and [Subsystem Boundaries](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/06_subsystem_boundaries_and_orchestration_contracts.md).
* Integrated into CD²F consensus arbitration in Deliverable [D06](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D06_cd2f_consensus_v2.md).
* HITL console escalation interface implemented in Deliverable [D09](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D09_desktop_console_v2.md).

---

## 7. Related Decisions & Artifacts

* [ADR 004: CD2F Consensus Arbitration](file:///d:/projects/SCOF_V1/SCOF/docs/adr/004_cd2f_consensus_arbitration.md)
* [ADR 008: Tauri v2 Desktop Operations Console](file:///d:/projects/SCOF_V1/SCOF/docs/adr/008_tauri_v2_desktop_operations_console.md)
* [ADR 015: Tripartite State Isolation for Benchmark Integrity](file:///d:/projects/SCOF_V1/SCOF/docs/adr/015_tripartite_state_isolation_for_benchmark_integrity.md)
* [ADR 019: Operational Digital Twin Substrate Layer](file:///d:/projects/SCOF_V1/SCOF/docs/adr/019_operational_digital_twin_substrate_layer.md)
* [Subsystem Boundaries Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/06_subsystem_boundaries_and_orchestration_contracts.md)
