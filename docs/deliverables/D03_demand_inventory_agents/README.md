# Deliverable D3 — Forecasting Agent Slice: Demand + Inventory

##  Objective
Build the two data-heaviest forecasting agents as standalone callable services conforming to the Structured Claim contract.

---

##  Requirements Summary (from SRS)
- **FR-3.1**: Demand Agent ensembling XGBoost/Prophet with time-series foundation model (Chronos-2), MCP-connected.
- **FR-3.2**: Inventory Agent using same ensembling approach over D1/D2 inventory data.
- **FR-3.3**: Output structured claims (recommendation, confidence, priority, impact, evidence) in isolation.

---

##  Standalone Acceptance Criteria
Calling each agent's endpoint directly with a synthetic scenario ID returns a valid structured claim verifiable against D1 ground truth without Coordinator existing.
