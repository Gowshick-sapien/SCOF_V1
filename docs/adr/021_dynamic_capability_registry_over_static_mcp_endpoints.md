# ADR 021: Dynamic Capability Registry Over Static MCP Endpoints

* **Status**: Accepted

---

## 1. Context and Problem Statement

In early SCOF implementations, agent capabilities were exposed via statically coded tool signatures (e.g., `get_demand_forecast`, `get_inventory_position`, `evaluate_disruption`). As the enterprise expanded to 30 domains and 96 tables, enumerating individual MCP endpoints resulted in an explosion of 50+ tool definitions.

Injecting 50+ JSON tool schemas into LLM agent prompts caused severe prompt context dilution, increased token consumption, and elevated hallucinated tool argument rates. Conversely, allowing raw SQL or Cypher execution violated security boundaries. A declarative, extensible mechanism was required.

---

## 2. Decision Drivers

* **Prompt Efficiency:** Reducing agent prompt context overhead by $> 80\%$.
* **Tool Selection Accuracy:** Minimizing hallucinated tool calls and incorrect parameter schemas.
* **Extensibility:** Allowing new analytical services, simulation models, and database projections to be registered with zero code changes to agent prompts.
* **Governance & Isolation:** Enforcing operational class restrictions and isolation levels centrally.

---

## 3. Considered Options

* **Option 1 — Static MCP Tool Enumeration:** Manually code and register 50+ individual MCP tool functions into each agent's active system prompt.
* **Option 2 — Generic Raw Execution Tools:** Expose generic `execute_sql` and `execute_cypher` tools, allowing LLM agents to write raw database queries.
* **Option 3 — Dynamic Capability Registry:** Central catalog of declarative Capability Cards. Agents specify operational intents; the registry dynamically binds only the 3-5 most relevant, bounded MCP tool schemas into the agent's active execution context on demand.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Dynamic Capability Registry**

### Rationale:
1. **Dynamic Binding:** Specialist agents receive lean, contextual tool interfaces containing only the capabilities required for the active disruption, reducing prompt tokens from $\approx 4,500$ to $\approx 400$ ($91\%$ reduction).
2. **Declarative Registration:** Service providers (D2, Analytics, Twin) register their schemas, latency profiles, and semantic triggers via YAML/JSON Capability Cards.
3. **Strict Bounds:** Prohibits unconstrained database writes while maintaining high expressive power.
4. **Decoupled Architecture:** Adding a new operational domain requires publishing a new Capability Card; existing agents immediately discover it via semantic search without code refactoring.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Dramatically improves agent reasoning speed and tool call accuracy ($> 98\%$).
* Completely eliminates the maintenance burden of static endpoint sprawl.
* Centralizes policy enforcement, rate limiting, and observability instrumentation.
* Bridges the gap between 30 enterprise domains and the 4-agent operational roster.

### Negative Consequences / Trade-offs:
* Adds a semantic capability discovery step during task initialization ($\approx 20\text{ ms}$ overhead).
* Requires rigorous schema validation for all registered Capability Cards.

---

## 6. Implementation & Compliance Notes

* Architectural specification in [Dynamic Capability Registry Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md).
* Data contracts defined in [`capability_registry_spec.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/capability_registry_spec.md).
* Integrated with MCP server infrastructure in Deliverable [D08](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D08_api_event_bus_v2.md).

---

## 7. Related Decisions & Artifacts

* [ADR 006: MCP and A2A Protocol Standardization](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_mcp_and_a2a_protocol_standardization.md)
* [ADR 017: Decoupling Data Domains from Agent Roster](file:///d:/projects/SCOF_V1/SCOF/docs/adr/017_decoupling_data_domains_from_agent_roster.md)
* [ADR 020: Tri-Zone Query Routing and Deeper Resolver](file:///d:/projects/SCOF_V1/SCOF/docs/adr/020_tri_zone_query_routing_and_deeper_resolver.md)
* [Dynamic Capability Registry Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md)
