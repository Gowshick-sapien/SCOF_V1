# Structured Claim Contract Specification (V2)

## 1. Overview & Purpose

The **Structured Claim** is the universal inter-agent communication contract in SCOF. Regardless of whether an agent specializes in Demand, Inventory, Sourcing, or Logistics, every recommendation emitted during multi-agent deliberation must conform strictly to this schema.

This standardization enables the **CD²F Dynamic Consensus Engine** to arbitrate conflicting proposals algorithmically using objective mathematical weighting.

---

## 2. JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StructuredClaim",
  "type": "object",
  "required": [
    "claim_id",
    "agent_id",
    "disruption_id",
    "recommended_action",
    "situational_confidence",
    "estimated_cost",
    "projected_service_level_impact",
    "reasoning_summary",
    "evidence_references",
    "timestamp"
  ],
  "properties": {
    "claim_id": {
      "type": "string",
      "description": "Unique identifier for this claim instance (e.g., CLM-9F812A)."
    },
    "agent_id": {
      "type": "string",
      "enum": ["demand_agent", "inventory_agent", "supplier_agent", "transport_agent"],
      "description": "Identifier of the emitting specialist agent."
    },
    "disruption_id": {
      "type": "string",
      "description": "ID of the disruption scenario being addressed."
    },
    "recommended_action": {
      "type": "string",
      "enum": [
        "EXPEDITE_TRANSIT",
        "REROUTE_CORRIDOR",
        "REALLOCATE_INVENTORY",
        "EMERGENCY_REPLENISHMENT",
        "HOLD_SAFETY_STOCK",
        "PRICE_PROMOTION_ADJUSTMENT",
        "ESCALATE_TO_HUMAN"
      ],
      "description": "Canonical operational action proposed by the agent."
    },
    "action_parameters": {
      "type": "object",
      "description": "Action-specific parameters (e.g., source facility, target facility, quantity, transport lane ID)."
    },
    "situational_confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Agent's self-assessed confidence score (c_i) in this specific claim."
    },
    "estimated_cost": {
      "type": "number",
      "minimum": 0.0,
      "description": "Estimated financial cost of executing this action in INR."
    },
    "projected_service_level_impact": {
      "type": "number",
      "minimum": -1.0,
      "maximum": 1.0,
      "description": "Projected net delta on store SKU on-shelf availability (fill rate)."
    },
    "reasoning_summary": {
      "type": "string",
      "description": "Verbatim natural language rationale suitable for display in the Meeting Log."
    },
    "evidence_references": {
      "type": "array",
      "items": { "type": "string" },
      "description": "IDs of underlying entities, Twin Service calculation results, or historical precedent IDs supporting this claim."
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```
