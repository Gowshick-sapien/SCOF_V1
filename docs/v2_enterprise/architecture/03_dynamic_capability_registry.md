# Dynamic Capability Registry Architecture

## 1. Executive Summary & Problem Context

In an enterprise supply chain cognitive framework spanning 30 domains and dozens of operational queries, exposing capabilities via static, manually coded tool signatures creates severe architectural friction:

```text
[ANTI-PATTERN: Static Tool Proliferation]
Agent Prompt Context <--- [ 50+ Hardcoded MCP Tool Definitions ] <--- Brittle Maintenance
Result: Prompt context dilution, increased token cost, hallucinated tool calls, poor accuracy.
```

### Critical Flaws of Static Tool Enumeration:
1. **Context Window Dilution:** Injecting dozens of JSON tool schemas into every agent prompt consumes precious context tokens and degrades model reasoning performance.
2. **Brittle Schema Maintenance:** Whenever a database table changes or a new analytical algorithm is added, every tool schema, agent prompt, and adapter must be manually re-engineered.
3. **Tight Coupling:** Specialist agents become tightly coupled to specific database views rather than expressing business intents.

---

## 2. The Dynamic Capability Registry Pattern

SCOF V2 implements the **Dynamic Capability Registry Pattern**. Under this architecture, internal and external service providers register their computational capabilities declaratively using standardized **Capability Cards**.

```text
+-------------------------------------------------------------------------------+
|                       DYNAMIC CAPABILITY REGISTRY                             |
|                                                                               |
|  +------------------------+  +------------------------+  +-----------------+  |
|  | D2 Knowledge Fabric    |  | Analytic Services      |  | Twin Substrate  |  |
|  | - Table lookups        |  | - Demand ensembles     |  | - DES simulation|  |
|  | - Graph traversals     |  | - Carrier scoring      |  | - Branching     |  |
|  | - Vector search        |  | - Safety stock compute |  | - Invariant chk |  |
|  +-----------+------------+  +-----------+------------+  +--------+--------+  |
|              |                           |                        |           |
|              +---------------------------+------------------------+           |
|                                          | Declarative Registration           |
|                                          v                                    |
|              +----------------------------------------------------+           |
|              |           CENTRAL CAPABILITY CATALOG               |           |
|              | Semantic Index | Input/Output Schemas | SLAs       |           |
|              +---------------------------+------------------------+           |
+------------------------------------------|------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
     +------------------------------+              +------------------------------+
     | COGNITIVE QUERY ROUTER       |              | LANGGRAPH ORCHESTRATION      |
     | Intent matching & resolution |              | Dynamic MCP tool binding     |
     +------------------------------+              | (Injects 3-5 bounded tools)  |
                                                   +------------------------------+
```

---

## 3. The Capability Card Specification

Every capability registered in the system is defined by an immutable, typed **Capability Card**:

```yaml
capability_id: "twin.simulation.counterfactual_branch"
version: "2.1.0"
provider_subsystem: "digital_twin_service"
operational_class: "Class_C"

metadata:
  display_name: "Counterfactual Scenario Branching"
  description: "Forks active Layer 3 scenario to evaluate candidate operational interventions."
  domain_scope: ["inventory", "transportation", "sourcing"]
  sla_latency_ms: 500

semantic_intents:
  - "evaluate impact of alternate supplier"
  - "simulate expedited freight rerouting"
  - "compare intervention branches for stockout mitigation"
  - "what happens if we reallocate DC inventory"

access_policy:
  required_role: "operational_specialist"
  state_isolation_level: "layer_3_ephemeral"
  requires_hitl: false

input_schema:
  type: "object"
  required: ["parent_scenario_id", "branch_name", "candidate_interventions"]
  properties:
    parent_scenario_id:
      type: "string"
      format: "uuid"
    branch_name:
      type: "string"
    candidate_interventions:
      type: "array"
      items:
        $ref: "#/definitions/InterventionAction"

output_schema:
  type: "object"
  required: ["branch_scenario_id", "state_delta", "invariant_status"]
  properties:
    branch_scenario_id:
      type: "string"
    state_delta:
      $ref: "#/definitions/ScenarioStateDelta"
    invariant_status:
      type: "string"
      enum: ["passed", "violated"]
```

---

## 4. Dynamic MCP Tool Binding Lifecycle

Rather than overwhelming an agent with the entire enterprise tool catalog, SCOF binds tools dynamically on demand:

```text
1. Disruption Ingested ---> 2. Task Stated ---> 3. Registry Queried ---> 4. Bounded MCP Tools Bound
   (e.g., Supplier Delay)   (Demand Agent       (Match top-3 capabilities    (Agent receives ONLY:
                            investigates)        via semantic embeddings)    - get_inventory_position
                                                                             - get_demand_forecast
                                                                             - evaluate_counterfactual)
```

### Lifecycle Steps:
1. **Task Initialization:** When a specialist agent (e.g., Demand Specialist) is invoked by the LangGraph kernel to handle a disruption, its prompt contains the operational context.
2. **Semantic Capability Discovery:** The Orchestration Kernel queries the Capability Registry using semantic similarity search (via pgvector) over the task description.
3. **Dynamic MCP Synthesis:** The top $k$ matching capabilities (typically $k \in [3, 5]$) are converted into standard Model Context Protocol (MCP) tool schemas and mounted into the agent's active execution context.
4. **Tool Execution & Unmounting:** The agent reasons and calls the bounded tools. Once the task completes and the structured claim is posted, ephemeral tool bindings are unmounted, keeping agent contexts lean and focused.

---

## 5. Architectural Benefits & Governance

| Metric | Static Tool Approach | Dynamic Capability Registry | Architectural Advantage |
| :--- | :--- | :--- | :--- |
| **Agent Prompt Tokens** | $\approx 4,500$ tokens (50 tool schemas) | $\approx 400$ tokens (3-5 bound schemas) | **$91\%$ token reduction; zero context pollution** |
| **Tool Selection Accuracy** | $\approx 78\%$ (hallucinated parameters) | $> 98\%$ (focused intent matching) | **Eliminates wrong tool selection errors** |
| **New Domain Extensibility** | Requires editing agent core code | Register new Capability Card | **Zero code rewrite for existing agents** |
| **Governance & Access** | Hardcoded per endpoint | Centralized policy enforcement | **Unified security, isolation, and audit logging** |

---

## 6. Implementation References

* Formal Data Contract: [`capability_registry_spec.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/capability_registry_spec.md)
* Protocol Standardization: [ADR 006 (MCP and A2A)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_mcp_and_a2a_protocol_standardization.md)
* Architecture Decision: [ADR 021 (Dynamic Capability Registry)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/021_dynamic_capability_registry_over_static_mcp_endpoints.md)
