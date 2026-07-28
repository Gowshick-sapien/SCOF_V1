# Deliverable D5 — Agent Orchestration & Protocol Layer

## 🎯 Objective
Wire the four specialist agents together under a LangGraph Coordinator using standardized A2A and MCP protocols.

---

## 📋 Requirements Summary (from SRS)
- **FR-5.1**: LangGraph state graph connecting specialist agents to Coordinator node.
- **FR-5.2**: Formalized MCP servers wrapping agent tool/data access.
- **FR-5.3**: A2A layer where agents publish Agent Cards for dynamic Coordinator discovery and delegation.
- **FR-5.4**: Coordinator collects claim bundles without applying arbitration logic yet.
- **FR-5.5**: Active agent roster read dynamically from active Domain Profile (`agents.yaml`).
