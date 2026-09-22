# Agent Card Specification (V2 Enterprise)

## 1. Overview & Purpose

In SCOF V2, all autonomous agents must adhere to a declarative **Agent Card Specification**. The Agent Card serves as the machine-readable and human-auditable contract governing an agent's operational boundaries, domain competencies, tool permissions, input/output schemas, and execution Service Level Agreements (SLAs).

This prevents architectural drift, guarantees deterministic orchestration in Deliverable D05, and enforces least-privilege security over the Enterprise Knowledge Fabric (ADR 014, ADR 017).

---

## 2. Agent Card Schema (YAML / JSON Schema)

Each agent configuration file in `agents/cards/` must validate against the following specification:

```yaml
agent_card_version: "2.0"
metadata:
  agent_id: "string (e.g., demand-forecasting-agent)"
  canonical_name: "string (e.g., Enterprise Demand Forecasting Agent)"
  version: "string (e.g., 2.0.0)"
  author: "string"
  description: "string"

operational_boundaries:
  primary_domains:
    - "string (from the 30 data domains: e.g., sales, demand_signals, promotions, catalog)"
  read_permissions:
    relational_tables:
      - "string (e.g., pos_sales, daily_demand, promotional_events)"
    graph_labels:
      - "string (e.g., Store, Product, Category, Department)"
    semantic_collections:
      - "string (e.g., past_demand_remedies)"
  write_permissions:
    allowed_actions:
      - "string (e.g., emit_structured_claim, submit_forecast_adjustment)"
    state_layer_target: "Layer 3 (Scenario Runtime State only - strictly no Layer 1 or 2 writes)"

mcp_tool_allowlist:
  - tool_name: "string (e.g., get_pos_sales_trend)"
    max_invocations_per_cycle: integer
    timeout_ms: integer
  - tool_name: "string (e.g., get_category_assortment_tree)"
    max_depth: 3
    timeout_ms: 150

deliberation_contract:
  output_schema: "StructuredClaimV2" # Refers to structured_claim_contract.md
  deliberation_modes:
    - "proposal"
    - "critique"
    - "vote"
  token_budget_per_cycle: integer (e.g., 2048)
  execution_timeout_ms: integer (e.g., 850)

fallback_and_resilience:
  fallback_mode: "deterministic_rule_baseline"
  fallback_handler: "string (e.g., scof.agents.fallbacks.demand_heuristic)"
  max_retry_attempts: 1
```

---

## 3. Roster of Standard Agent Cards

Under ADR 017, the 30 data domains are decoupled from the agent roster. SCOF V2 defines four operational specialist agent cards:

| Agent ID | Canonical Role | Core Domain Inputs | Target Output Action |
| :--- | :--- | :--- | :--- |
| `demand-agent` | Demand Sensing & Forecasting | POS Sales, Daily Demand, Promotions, Weather | SKU-level demand lift/suppression claims |
| `inventory-agent` | Multi-Echelon Replenishment | Inventory Levels, Safety Stocks, Facilities, Spoilage | Expedited reorder and stock transfer claims |
| `supplier-agent` | Vendor Performance & Procurement | Purchase Orders, Supplier SLA, Quality Inspections | Vendor allocation and purchase order split claims |
| `transport-agent` | Freight Logistics & Routing | Shipments, Transport Lanes, Carriers, Fleet Assets | Alternate route selection and carrier rebooking claims |

---

## 4. Invariant Rules

1. **State Isolation:** No Agent Card may grant write permissions to Layer 1 (Frozen Datasets) or Layer 2 (Baseline State). Writes are confined to Layer 3 simulation runtime contexts.
2. **Bounded Depth:** Any graph tool granted to an agent must enforce `max_depth <= 3` (ADR 014).
3. **Structured Emission:** All agents must emit outputs adhering to [`structured_claim_contract.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/structured_claim_contract.md). Unstructured free text output is rejected by the D05 Orchestration Kernel.
