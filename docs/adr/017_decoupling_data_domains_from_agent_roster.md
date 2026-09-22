# ADR 017: Decoupling Enterprise Data Domains from Multi-Agent Operational Roster

* **Status**: Accepted

---

## 1. Context and Problem Statement

The SCOF enterprise dataset defines **30 unified business domains** (Corporate Structure, Merchandise, Sourcing, Procurement, Inventory, Network Logistics, Commerce, Finance, Governance, Exogenous Events, etc.). 

A common architectural trap in multi-agent system design is the naive assumption that every business domain requires a dedicated agent (e.g., creating a "Finance Agent", "Packaging Agent", "Legal Entity Agent", and "Pricing Agent", totaling 30 distinct agents). 

Deploying 30 autonomous LLM agents creates catastrophic operational bottlenecks:
1. Excessive inter-agent communication overhead and token latency.
2. Fragmented decision boundaries where agents dispute trivial sub-domain boundaries.
3. Violation of the sub-second decision SLA ($< 500\text{ ms}$).

---

## 2. Decision Drivers

* **Decision Latency SLA:** Preserve the $< 500\text{ ms}$ fast-path autonomous execution budget.
* **Operational Cohesion:** Align agents with primary operational decision boundaries (Demand, Inventory, Supply, Logistics) rather than data storage schemas.
* **Cross-Domain Data Synthesis:** Enable an individual specialist agent to synthesize facts across multiple data domains (e.g., Inventory Agent examining both physical stock and purchase order delivery dates).

---

## 3. Considered Options

* **Option 1 (1:1 Domain-to-Agent Mapping):** Build 30 separate agent microservices, each wrapping one of the 30 business domains.
* **Option 2 (Single Monolithic Agent):** Consolidate all 30 domains into a single monolithic LLM prompt.
* **Option 4 (Decoupled 4-Specialist Federation):** Maintain a lean federation of **4 primary operational specialist agents**, where each agent consumes multiple underlying data domains via Model Context Protocol (MCP) tools.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3: Decoupled 4-Specialist Federation**

### Rationale:
* **Ontology vs. Roster:** The 30 business domains represent the **enterprise data ontology and schema**, NOT the agent roster.
* **Cross-Domain Multi-Tool Binding:**
  * **Demand Agent:** Consumes Commerce, Sales Transactions, Promotions, Calendar Events, Weather, and Macroeconomic data.
  * **Inventory Agent:** Consumes Inventory Positions, Goods Receipts, Store Assortments, Replenishment Policies, and Physical Assets.
  * **Supplier Agent:** Consumes Supplier Profiles, Commercial Contracts, Purchase Orders, Supplier Invoices, and Three-Way Match records.
  * **Transportation Agent:** Consumes Transport Lanes, Shipments, Carrier Profiles, Fleet Assets, and Route Disruptions.
* **Consensus Efficiency:** CD²F arbitrates among 4 well-bounded, cross-functional claims rather than resolving a chaotic 30-agent shouting match.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Keeps multi-agent coordination lean, fast, and explainable in the Meeting Log.
* Agents possess cross-functional context (e.g., Inventory Agent understands supplier lead times before proposing stock re-allocation).
* Allows future addition of optional extension agents (e.g., Risk & ESG Agent in D11) without altering core operational dynamics.

### Negative Consequences / Trade-offs:
* MCP tool registries per agent must bundle tools across multiple underlying relational schemas.

---

## 6. Implementation & Compliance Notes

* **Agent Roster:** Defined in `profiles/v2-retail-enterprise/agents.yaml`.
* **Agent Implementation:** Governed by Deliverables D03 (`services/agents/demand`, `services/agents/inventory`) and D04 (`services/agents/supplier`, `services/agents/transportation`).
* **Tool Bindings:** Governed by `docs/v2_enterprise/contracts/bounded_mcp_tools_spec.md`.
