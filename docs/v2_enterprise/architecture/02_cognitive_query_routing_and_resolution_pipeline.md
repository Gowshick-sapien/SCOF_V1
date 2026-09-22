# Cognitive Query Routing & Resolution Pipeline

## 1. Executive Summary & Problem Formulation

In a multi-agent enterprise cognitive architecture operating across 30 business domains and 49,616 SKUs, agent queries exhibit wide diversity in computational complexity, data requirements, and execution urgency.

### The Monolithic Twin Gateway Fallacy
A naive architecture routes every agent query through the Digital Twin Service:

```text
[ANTI-PATTERN: Monolithic Twin Gateway]
Every Agent Query ----> [ Twin Service Gateway ] ----> [ PostgreSQL / Neo4j / Models ]
```

This design introduces severe architectural failure modes:
1. **Severe Latency Degradation:** Simple read-only lookups (e.g., retrieving a store address or supplier payment term) suffer the full latency overhead of the simulation engine.
2. **Computational Bottleneck:** The Twin simulation kernel becomes congested with non-simulation traffic, starving high-priority disruption propagations.
3. **Premature Coupling:** Agents become tightly bound to simulation runtime schemas rather than accessing standard enterprise data fabric projections.

### The Hardcoded Segregation Fallacy
Conversely, manually hardcoding query categorization rules (e.g., hardcoding 4 fixed demand query types, 3 inventory query types) is brittle and unmaintainable. As new business questions, promotions, or regulatory checks arise, hardcoded rules require continuous code rewrites.

---

## 2. The Three Operational Classes of Inquiries

SCOF formally classifies all cognitive inquiries into three distinct operational classes:

| Class | Inquiry Type | Target Subsystem | Example Operational Questions | Latency SLA |
| :--- | :--- | :--- | :--- | :--- |
| **Class A** | **Direct Read-Only Enterprise Facts** | **Enterprise Knowledge Fabric (D2)** | *"What are the payment terms for Supplier SUP-0142?"*, *"Which stores are assigned to DC-003?"*, *"Retrieve inventory on hand at Store STR-0012 for SKU-8841."* | $< 50\text{ ms}$ |
| **Class B** | **Derived Operational Metrics & Analytics** | **Analytic & Machine Learning Services** | *"Compute the 90-day lead-time variance for Carrier CR-009."*, *"Generate a 4-week demand forecast ensemble for Beverage Category."*, *"Identify suppliers with OTIF compliance $< 85\%$."* | $< 250\text{ ms}$ |
| **Class C** | **Counterfactual Simulation & State Mutation** | **Digital Twin Service (Simulation Substrate)** | *"If Supplier SUP-0044 delays shipments by 14 days, which store shelves stock out by Day 7?"*, *"Simulate impact of rerouting PO-9912 via Air Freight vs alternate vendor."* | $< 500\text{ ms}$ |

---

## 3. The Tri-Zone Cognitive Routing Architecture

To decouple agents from hardcoded query logic while protecting the Twin from bottlenecking, SCOF implements a **Tri-Zone Cognitive Query Routing Pipeline**:

```text
+-------------------------------------------------------------------------------+
|                            INCOMING AGENT QUERY                               |
|   Caller: Specialist Agent | Intent: Natural Language / Structured Request    |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                   ZONE 1: FAST-PATH DETERMINISTIC ROUTER                      |
|   Signature & Schema Matching  |  Metadata Inspection  |  Confidence Scoring  |
+---------------------------------------+---------------------------------------+
                                        |
                  +---------------------+---------------------+
                  |                                           |
         Confidence >= 0.85                           0.50 <= Confidence < 0.85
                  |                                           |
                  v                                           v
+-----------------------------------+       +-----------------------------------+
| DIRECT DISPATCH                   |       | ZONE 2: AMBIGUOUS-PATH            |
| (Sub-10ms deterministic bypass)   |       |         DEEPER RESOLVER           |
|                                   |       | Intent Disambiguation             |
| -> Class A: D2 PostgreSQL / Neo4j |       | Entity Resolution & Binding       |
| -> Class B: Analytic Services     |       | Capability Registry Matching      |
| -> Class C: Twin Simulation       |       | Parameter Synthesis               |
+-----------------------------------+       +-----------------+-----------------+
                                                              |
                                            +-----------------+-----------------+
                                            |                                   |
                                   Disambiguated Route                  Unresolvable
                                            |                           (Confidence < 0.50)
                                            v                                   |
                                    [ DIRECT DISPATCH ]                         v
                                                                +-----------------------------------+
                                                                | ZONE 3: FALLBACK HANDLER          |
                                                                | Structured Clarification Contract |
                                                                | Anomaly Audit Logging to D07      |
                                                                +-----------------------------------+
```

### Zone 1: Fast-Path Deterministic Router
* **Mechanism:** Rule-based parser matching structured query schemas, explicit tool invocations, and high-frequency intent embeddings.
* **Confidence Gate:** When query confidence $c \ge 0.85$, the router immediately dispatches the request to the bound subsystem.
* **Performance:** Executes in $< 10\text{ ms}$, bypassing heavy language model deliberation for standard operational traffic.

### Zone 2: Ambiguous-Path Deeper Resolver
When a query is ambiguous ($0.50 \le c < 0.85$), spans multiple domains, or lacks explicit parameters, it is escalated to the **Deeper Resolver**.
* **Role:** A specialized, lightweight cognitive arbitrator designed to inspect context, clarify user/agent intent, and match capabilities without blind execution.
* **Operational Mechanics:**
  1. **Intent Disambiguation:** Disentangles whether the agent wants historical observation (Class A), predictive forecasting (Class B), or hypothetical counterfactual simulation (Class C).
  2. **Entity & Context Binding:** Resolves ambiguous entity names (e.g., mapping *"the Dallas warehouse"* to `DC-002`) using semantic vector search in D2.
  3. **Capability Matching:** Consults the [Dynamic Capability Registry](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md) to discover registered providers capable of fulfilling the synthesized request.
  4. **Parameter Synthesis:** Assembles required operational arguments (e.g., extracting `horizon_days`, `disruption_delta`, `cost_ceiling`).

### The Three Outcomes of the Deeper Resolver:
1. **Resolved Route:** The intent is successfully classified and mapped to a specific capability provider; dispatched directly to Class A, B, or C.
2. **Clarification Request:** The query is fundamentally underspecified (e.g., *"What is the impact of a delay?"* without specifying supplier, SKU, or duration). The resolver returns a structured clarification payload to the calling agent.
3. **Gated Rejection / Escalation:** The request attempts unauthorized state mutations or invalid operations; rejected with a typed error contract.

### Zone 3: Fallback Handler
* **Trigger:** Query confidence falls below minimum threshold ($c < 0.50$) or Deeper Resolver fails to synthesize a valid contract.
* **Action:** Rejects execution, logs routing failure to the D07 observability trace for engineering review, and returns a safe fallback response preventing hallucinated execution.

---

## 4. Query Intent Routing Matrix

The following matrix illustrates how real-world agent inquiries are classified, routed, and executed:

| Incoming Query Text | Fast-Path Classification | Deeper Resolver Action | Target Subsystem | Output Artifact |
| :--- | :--- | :--- | :--- | :--- |
| `"SELECT * FROM purchase_orders WHERE supplier_id = 'SUP-0012'"` | Class A ($c = 1.0$) | Bypassed | D2 Fabric (PostgreSQL) | Raw relational records |
| `"Show upstream supply chain path for SKU-1049 at Store STR-0004"` | Class A ($c = 0.98$) | Bypassed | D2 Fabric (Neo4j Bounded) | Materialized graph path |
| `"What is the projected 4-week demand for Dairy category in Zone 2?"` | Class B ($c = 0.92$) | Bypassed | Analytic Forecasting Engine | Quantile forecast series |
| `"What happens to our stores if Supplier SUP-0088 halts deliveries for 2 weeks?"` | Class C ($c = 0.95$) | Bypassed | Twin Simulation Substrate | Forward propagation impact report |
| `"Can we handle a surge in soft drink sales next weekend?"` | Ambiguous ($c = 0.64$) | Clarifies: Maps to 554 regional events; checks promo calendar; synthesizes Class C counterfactual shock test. | Twin Simulation Substrate | Counterfactual fill-rate projection |
| `"Is Supplier SUP-0044 reliable?"` | Ambiguous ($c = 0.58$) | Clarifies: Synthesizes Class B metric query (historical OTIF, lead-time variance, 3-way match defect rate). | Analytic Metrics Service | Multi-dimensional vendor scorecard |

---

## 5. Integration Contracts & Governance

1. **Sub-second SLA Enforcement:** The Fast-Path router must complete evaluation within $10\text{ ms}$. The Deeper Resolver must complete intent synthesis within $150\text{ ms}$.
2. **Deterministic Fallback:** No agent query may hang indefinitely waiting for routing resolution. Timeouts trigger immediate Zone 3 fallback after $250\text{ ms}$.
3. **Observability Traceability:** Every routing decision records:
   - `query_id`: Unique trace identifier.
   - `caller_agent_id`: Agent originating the query.
   - `initial_confidence`: Score assigned by Fast-Path evaluator.
   - `resolver_invoked`: Boolean flag indicating whether Deeper Resolver was triggered.
   - `final_subsystem`: Target subsystem receiving the request.
   - `execution_latency_ms`: Total routing overhead.
