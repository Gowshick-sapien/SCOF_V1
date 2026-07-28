# Deliverable D4 — Reliability Agent Slice: Supplier + Transportation

##  Objective
Build the two network & reliability-focused agents as standalone callable services conforming to the Structured Claim contract.

---

##  Requirements Summary (from SRS)
- **FR-4.1**: Supplier Agent scoring vendor reliability & predicting failure from Neo4j graph & delivery history.
- **FR-4.2**: Transportation Agent predicting delays and generating rerouting options over the route network.
- **FR-4.3**: Structured claim output contract (recommendation, confidence, priority, impact, evidence), MCP-connected.

---

##  Standalone Acceptance Criteria
Injecting a D1 disruption event directly into agent endpoints produces sensible structured claims without Coordinator involvement.
