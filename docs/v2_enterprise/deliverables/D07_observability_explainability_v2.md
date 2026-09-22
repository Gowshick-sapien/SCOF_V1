# Deliverable D07 (V2): Observability & Explainability Framework

## 1. Overview & Objectives

Deliverable D07 upgrades the basic logging of V1 into a comprehensive **Enterprise Observability & Explainability Framework**. It captures the full cognitive lifecycle of multi-agent deliberations, maintains immutable audit trails, generates contrastive counterfactual explanations for human executives, and embeds resolved incidents into a pgvector semantic memory projection for precedent retrieval.

---

## 2. The 8-Stage Cognitive Reasoning Trace

Every operational incident processed by the platform generates an immutable 8-stage trace:

| Stage | Name | Description | Captured Artifact |
| :--- | :--- | :--- | :--- |
| **1** | **Disruption Ingestion** | Sensor, human, or scenario trigger is received and validated | Ingestion timestamp, disruption payload |
| **2** | **Context Scoping** | Subgraph of affected SKUs, facilities, and contracts identified | Bounded graph query IDs, node list |
| **3** | **Proposal Generation** | Specialists independently emit initial structured claims | Claim vectors, confidence scores, rationale |
| **4** | **Cross-Examination** | Agents challenge assumptions and constraints in peer claims | Structured critiques, contradiction flags |
| **5** | **Consensus Resolution** | CD²F calculates composite weights and determines tier | Weight matrix, conflict metric, tier outcome |
| **6** | **Twin Simulation Projection** | Proposed remedy projected into Layer 3 ephemeral state | Delta metrics (cost, fill rate, service level) |
| **7** | **Outcome Verification** | Post-execution validation against business constraints | Validation gates, constraint checks |
| **8** | **Semantic Archival** | Incident summary embedded and stored in pgvector | 384-dim vector, incident index ID |

---

## 3. Contrastive Explainability Engine

A critical enterprise requirement is explaining not just what was chosen, but **why plausible alternatives were rejected**. The explainability engine generates contrastive explanations:

$$\text{Explanation}(C^* \text{ over } C_j) = \langle \Delta\text{FinancialRisk}, \Delta\text{ServiceLevel}, \Delta\text{ExecutionTime}, \text{ViolatedConstraints}(C_j) \rangle$$

* **Executive Summary:** Generates clear natural-language rationales summarizing trade-offs (e.g., *"Air freight via Carrier CAR-002 was rejected despite saving 48 hours because it exceeded the emergency freight budget by $34,200 with an incremental fill rate gain of only 2.1%"*).
* **Audit Lineage:** Every explanation links directly to underlying database records, contracts, and model inference IDs.

---

## 4. Semantic Precedent Memory (pgvector Projection)

To enable Case-Based Reasoning (CBR), resolved incidents are indexed into PostgreSQL via pgvector:
* **Embedding Model:** `all-MiniLM-L6-v2` generating 384-dimensional dense vectors over incident descriptions and resolved actions.
* **Retrieval Tool:** Agents invoke `find_historical_precedents(disruption_embedding, top_k=3, min_similarity=0.80)` via MCP to ground their proposals in corporate historical precedent.

---

## 5. Acceptance Criteria & Verification Evidence

1. **Trace Completeness Gate:** 100% of multi-agent interactions, tool calls, and state transitions recorded without data loss.
2. **Precedent Retrieval Gate:** pgvector similarity search over 10,000 incident vectors executes in $\le 45\text{ ms}$.
3. **Contrastive Explanation Gate:** Automatically generated explanations accurately identify the dominant rejected candidate and quantify the margin of preference.
4. **Audit Immutability Gate:** Traces are stored in append-only tables with cryptographic sequence hashes.
