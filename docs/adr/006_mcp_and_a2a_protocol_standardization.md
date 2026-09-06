# ADR 006: Protocol Standardization — Model Context Protocol (MCP) and Agent-to-Agent (A2A) vs. Proprietary REST/RPC

* **Status**: Accepted
* **Date**: 2026-08-04
* **Deciders**: SCOF Core Architecture Team, Integration Leads
* **Consulted**: Specialist Agent Engineers, Security Leads
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

SCOF is a federated multi-agent architecture where agents must perform two distinct types of communication:
1. **Agent-to-Tool / Data Access**: Agents need to query Neo4j graph topologies, inspect PostgreSQL inventory levels, check supplier lead times, and run route optimization algorithms.
2. **Inter-Agent Communication (Coordinator-to-Agent & Specialist-to-Specialist)**: The coordinator must discover available agents, inspect their capabilities, dispatch disruption payloads, and collect standardized claims.

Hardcoding direct SQL/Cypher queries inside agents tightly couples agent reasoning to database schemas. Similarly, writing ad-hoc proprietary REST endpoints for each agent creates fragile point-to-point dependencies that require modifying coordinator code whenever a new specialist (e.g. Weather, Finance) is introduced.

---

## 2. Decision Drivers

* **Schema Decoupling**: Agents must interact with tools via standardized semantic contracts without knowing database table structures.
* **Dynamic Agent Discovery**: The coordinator must be able to discover which specialist agents are online via standardized metadata cards.
* **Extensibility**: Adding new specialist agents post-MVP must be strictly additive, requiring zero changes to existing agents or the orchestration kernel.
* **Open Industry Standards**: Adoption of emerging open protocols rather than proprietary custom frameworks.

---

## 3. Considered Options

* **Option 1: Proprietary REST / Direct Python Imports**: Custom FastAPI endpoints or in-process module calls.
* **Option 2: gRPC / Protocol Buffers**: High-performance binary RPC.
* **Option 3: Open Protocol Hybrid — Model Context Protocol (MCP) + Agent-to-Agent (A2A)**.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — MCP (Agent-to-Tool) + A2A (Agent-to-Agent)**

### Rationale:
1. **Model Context Protocol (MCP) for Tools**:
   * Anthropic's Model Context Protocol standardizes how LLM-based agents query enterprise data and execute tools.
   * By wrapping database queries and calculation utilities inside MCP servers, tools become discoverable and secure. An agent only sees tool schemas (e.g. `get_safety_stock`, `query_supplier_lead_time`), decoupling the agent prompt from raw SQL/Cypher implementations.
2. **Agent-to-Agent (A2A) Protocol for Discovery & Delegation**:
   * Google's A2A protocol defines standard **Agent Cards** (manifests detailing an agent's domain, description, endpoints, and input/output schemas).
   * At startup, the LangGraph coordinator queries `GET /.well-known/agent.json` across configured agent endpoints. If a new agent (e.g. `weather-agent`) is deployed and added to `agents.yaml`, the coordinator automatically discovers its capabilities and delegates tasks without code refactoring.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Zero code changes required in the coordinator to attach new domain specialists.
* Standardized Pydantic schemas for claims, confidence scores, and reasoning evidence.
* Safe tool execution boundaries isolating database credentials from LLM prompts.

### Negative Consequences / Trade-offs:
* Requires maintaining MCP server wrappers alongside underlying database connection factories.

---

## 6. Implementation & Compliance Notes

* Shared protocol contracts in [shared/scof_shared/protocols/](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/).
* Agent cards published at `/.well-known/agent.json` by each specialist microservice (`8011–8014`).
* A2A discovery client implemented in [services/coordinator/src/a2a_client.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/a2a_client.py).
* Verified via `python scripts/verify_d5.py`.

---

## 7. Related Decisions & Artifacts

* [ADR 001: Orchestration Kernel Selection](./001_langgraph_orchestration_kernel.md)
* [ADR 009: Declarative YAML Domain Profiles](./009_declarative_yaml_domain_profiles.md)
* [D5 Orchestration Documentation](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/README.md)
