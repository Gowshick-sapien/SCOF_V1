ADR 013: Tri-Zone Query Routing and Deeper Resolver Pipeline

* **Status**: Accepted

---


## 1. Context and Problem Statement

As specialist cognitive agents formulate inquiries across 30 enterprise domains, requests vary from basic database lookups (e.g., retrieving a supplier profile) to multi-echelon forward simulations (e.g., simulating supply chain collapse under hurricane disruptions).

Two failure modes were observed:
1. Routing every query through the Digital Twin Service created an expensive, slow bottleneck.
2. Manually hardcoding query classification rules (e.g., 4 hardcoded demand queries) was brittle and unmaintainable as new operational queries arose.

An architectural mechanism was required to route queries deterministically, handle ambiguous multi-domain queries safely, and prevent simulation bottlenecking.

---

## 2. Decision Drivers

* **Latency Budgets:** Sub-10ms routing for high-confidence operational queries.
* **Extensibility:** Ability to absorb new query intents without continuous code refactoring.
* **Disambiguation Precision:** Safe handling of ambiguous or underspecified agent inquiries before expensive computation is invoked.
* **Subsystem Protection:** Isolating the Twin Service simulation kernel from routine relational database traffic.

---

## 3. Considered Options

* **Option 1 -- Monolithic Twin Gateway:** Route 100% of agent queries through the Twin Service facade.
* **Option 2 -- Hardcoded Rule Segregation:** Write static switch/case or if/else rules categorizing queries by hardcoded domain keywords.
* **Option 3 -- Tri-Zone Cognitive Query Routing with Deeper Resolver:** Implement a three-zone pipeline: Zone 1 (Fast-Path Deterministic Evaluator for high confidence $c \ge 0.85$), Zone 2 (Ambiguous-Path Deeper Resolver for $0.50 \le c < 0.85$ performing intent disambiguation, entity binding, and capability matching), and Zone 3 (Fallback Handler for $c < 0.50$).

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 -- Tri-Zone Cognitive Query Routing with Deeper Resolver**

### Rationale:
1. **Class-Based Segregation:** Categorizes operations into Class A (D2 direct read-only), Class B (derived analytics), and Class C (Twin simulation).
2. **Fast-Path Efficiency:** $> 80\%$ of routine operational queries match deterministic signatures and bypass heavy reasoning, executing in $< 10\text{ ms}$.
3. **Deeper Resolver Gating:** Ambiguous queries are clarified before execution, preventing hallucinated simulation runs or wrong tool calls.
4. **Decoupled Discovery:** Leverages the Dynamic Capability Registry rather than hardcoded domain lists.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Protects the Digital Twin Service from non-simulation query traffic.
* Sub-10ms dispatch for high-confidence requests; sub-150ms intent synthesis for ambiguous queries.
* Underspecified queries trigger structured clarification back to the calling agent rather than failing silently.
* Fully auditable routing decisions recorded in D07 observability logs.

### Negative Consequences / Trade-offs:
* Introduces a Deeper Resolver component that must be maintained and monitored for latency.
* Requires continuous calibration of the confidence threshold boundaries ($0.85$ and $0.50$).

---

## 6. Implementation & Compliance Notes

* Architectural specification in [Cognitive Query Routing & Resolution Pipeline](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md).
* Integrated with LangGraph Orchestration Kernel in Deliverable [D05](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D05_orchestration_kernel_v2.md).
* Latency and routing accuracy verified under benchmark tests in Deliverable [D10](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D10_benchmarking_evaluation_v2.md).

---

## 7. Related Decisions & Artifacts

* [ADR ADR 016: Dual-Path Execution Routing](file:///d:/projects/SCOF_V1/SCOF/docs/adr/016_dual_path_execution_routing.md)
* [ADR ADR 008: Operational Digital Twin Substrate Layer](file:///d:/projects/SCOF_V1/SCOF/docs/adr/008_operational_digital_twin_substrate_layer.md)
* [ADR ADR 012 (Amendment): Dynamic Capability Registry Over Static MCP Endpoints](file:///d:/projects/SCOF_V1/SCOF/docs/adr/012b_amendment_dynamic_capability_registry_over_static_mcp.md)
* [Cognitive Query Routing Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md)
