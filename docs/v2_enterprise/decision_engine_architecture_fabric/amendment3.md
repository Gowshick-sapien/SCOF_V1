# SCOF V2 Architecture Refinement Revision (Amendment 3)

> [!IMPORTANT]
> This is a targeted refinement pass, not a conceptual redesign. It addresses the contract-level defects identified by the third-pass architecture review. The architectural direction established in Amendments 1 and 2 is CONFIRMED and FROZEN. No conceptual changes are made.

---

## Table of Contents

1. [Invariant Wording Refinements (Corrects Sections 1, 16.1 of Amendment 2)](#1-invariant-wording-refinements)
2. [Canonical ClaimTypeRegistry (New Section -- Fixes Agent Contracts)](#2-canonical-claimtyperegistry)
3. [Canonical ActionTypeRegistry (New Section -- Fixes Action Schemas)](#3-canonical-actiontyperegistry)
4. [Corrected Agent Ownership Contracts (Replaces Section 4.2 of Amendment 2)](#4-corrected-agent-ownership-contracts)
5. [ActionIntent / ActionImpact Separation (Replaces Section 9 of Amendment 2)](#5-actionintent--actionimpact-separation)
6. [ActionDefinition Ownership Model (New Section)](#6-actiondefinition-ownership-model)
7. [Critical Evidence Assessment (Extends Section 6 of Amendment 2)](#7-critical-evidence-assessment)
8. [Post-Snapshot Evidence Resolution (Corrects Section 7.2 of Amendment 2)](#8-post-snapshot-evidence-resolution)
9. [Decision Snapshot Refinements (Extends Section 7 of Amendment 2)](#9-decision-snapshot-refinements)
10. [Safe Candidate Pruning (Replaces Section 8 of Amendment 2)](#10-safe-candidate-pruning)
11. [Policy-Fixed Objective Normalization (Replaces Section 11.2 of Amendment 2)](#11-policy-fixed-objective-normalization)
12. [Proper Pareto Analysis (Replaces Section 11.2 Stage 4 of Amendment 2)](#12-proper-pareto-analysis)
13. [Twin Requirement Classification (Extends Section 10 of Amendment 2)](#13-twin-requirement-classification)
14. [Corrected Policy Precedence (Replaces Section 13.3 of Amendment 2)](#14-corrected-policy-precedence)
15. [Policy Deduplication (Corrects Sections 11.1 and 13.1 of Amendment 2)](#15-policy-deduplication)
16. [CD2F Description Refinement (Corrects Section 11.3 of Amendment 2)](#16-cd2f-description-refinement)
17. [R_i Agent Influence Status (Extends Section 18 of Amendment 2)](#17-r_i-agent-influence-status)
18. [Decomposed Reliability Metrics (Extends Section 18 of Amendment 2)](#18-decomposed-reliability-metrics)
19. [Event Sequence Allocation (Extends Section 16 of Amendment 2)](#19-event-sequence-allocation)
20. [Aggregate vs Session Sequence Relationship (Extends Sections 16 and 19 of Amendment 2)](#20-aggregate-vs-session-sequence-relationship)
21. [Hot-Path Cache Key Correction (Corrects Section 26 of Amendment 2)](#21-hot-path-cache-key-correction)
22. [Governance Fail-Closed Policy (Extends Section 28 of Amendment 2)](#22-governance-fail-closed-policy)
23. [Terminal State Guards (Extends Section 22 of Amendment 2)](#23-terminal-state-guards)
24. [Replanning Context (Extends Section 23 of Amendment 2)](#24-replanning-context)
25. [Outcome Observation Schema (Replaces actual_outcome in Section 24 of Amendment 2)](#25-outcome-observation-schema)
26. [Claim-Criticality Failure Responses (Extends Section 21 of Amendment 2)](#26-claim-criticality-failure-responses)
27. [Policy and Profile Integrity (Extends Section 13 of Amendment 2)](#27-policy-and-profile-integrity)
28. [Replay Manifest Retrieval Artifacts (Extends Section 25 of Amendment 2)](#28-replay-manifest-retrieval-artifacts)
29. [Historical Freshness Computation (Corrects Section 7 of Amendment 2)](#29-historical-freshness-computation)
30. [Simulation Materiality (Replaces simulation_trigger_threshold_usd in Amendment 2)](#30-simulation-materiality)
31. [Concurrent Session Interference (New Section)](#31-concurrent-session-interference)
32. [Complete B0-B7 Ablation Ladder (Replaces Section 31 Evaluation of Amendment 2)](#32-complete-b0-b7-ablation-ladder)
33. [Corrected Evaluation Protocol (Extends Section 31 of Amendment 2)](#33-corrected-evaluation-protocol)
34. [Freeze Declaration (New Section)](#34-freeze-declaration)
35. [Corrected Unified Architecture Diagram (Replaces Section 30 of Amendment 2)](#35-corrected-unified-architecture-diagram)

---

## 1. Invariant Wording Refinements

> [!IMPORTANT]
> **CORRECTS Invariants 1, 2, and 8 wording in Section 1 of Amendment 2.** Mechanism unchanged; prose refined for precision.

### Invariant 1: Source Authority (Refined)

```
PostgreSQL:
    Authoritative operational facts (System of Record).

Neo4j:
    Authoritative representation of the current materialized
    topology projection, subject to projection freshness/version.
    Derived from PostgreSQL via batch/streaming sync.

No operational fact may be made authoritative solely
because it exists in Neo4j. If PostgreSQL and Neo4j
disagree on an operational fact, PostgreSQL wins.
```

### Invariant 2: Cognitive Workspace Boundary (Refined)

```
The Deliberation Table stores decision artifacts
(claims, critiques, verdicts, directives).
It NEVER stores or replicates enterprise operational truth.

DeliberationEvents are authoritative for the historical
cognitive session state.

PostgreSQL operational tables remain authoritative for
enterprise operational state.

These are separate authority domains. "Events are the
source of truth" applies ONLY to the deliberation event
stream, not globally.
```

### Invariant 8: State Freshness (Corrected)

```
Every decision is bound to a declared world-state snapshot.
All agents in a session reason over the same observation boundary.

Post-snapshot evidence is REJECTED from the decision state.
If critical state changes are detected after the snapshot:
    - Evidence is rejected (default)
    - OR the snapshot is advanced and affected agents restart
    
Post-snapshot evidence may be QUARANTINED as auxiliary information
for HITL review, but it MUST NOT influence automated scoring,
evidence sufficiency assessment, or CD2F arbitration.
```

---

## 2. Canonical ClaimTypeRegistry

> [!IMPORTANT]
> **NEW SECTION.** Creates the single source of truth for all claim types in the system. Every `owned_claim_type`, `consumes_from` reference, and `forbidden_claim_type` in agent contracts MUST reference an entry in this registry.

### 2.1 Registry Definition

```python
class ClaimTypeRegistry:
    """Canonical registry of all valid claim types.
    Enforced at system startup: all agent DomainOwnershipPolicy
    references are validated against this registry.
    
    Naming convention: {domain}_{assessment_type}
    """
    
    # ---- Procurement & Supplier Domain ----
    SUPPLIER_OPERATIONAL_ASSESSMENT = "supplier_operational_assessment"
    PROCUREMENT_COST_ANALYSIS = "procurement_cost_analysis"
    ALTERNATE_SOURCING_FEASIBILITY = "alternate_sourcing_feasibility"
    SUPPLIER_CAPACITY_ASSESSMENT = "supplier_capacity_assessment"
    
    # ---- Risk & Resilience Domain ----
    SUPPLIER_FINANCIAL_DISTRESS = "supplier_financial_distress"
    SYSTEMIC_RISK_ASSESSMENT = "systemic_risk_assessment"
    CASCADE_FAILURE_ANALYSIS = "cascade_failure_analysis"
    REGULATORY_COMPLIANCE_STATUS = "regulatory_compliance_status"
    CORRIDOR_RISK_ASSESSMENT = "corridor_risk_assessment"
    GEOPOLITICAL_RISK_ASSESSMENT = "geopolitical_risk_assessment"
    SUPPLIER_CONCENTRATION_RISK = "supplier_concentration_risk"
    NETWORK_FRAGILITY_ASSESSMENT = "network_fragility_assessment"
    
    # ---- Demand & Commerce Domain ----
    DEMAND_ASSESSMENT = "demand_assessment"
    COMMERCIAL_IMPACT_ANALYSIS = "commercial_impact_analysis"
    PRICING_RECOMMENDATION = "pricing_recommendation"
    REVENUE_IMPACT_ASSESSMENT = "revenue_impact_assessment"
    PROMOTIONAL_IMPACT_ANALYSIS = "promotional_impact_analysis"
    
    # ---- Inventory & Asset Management Domain ----
    INVENTORY_VIABILITY_ASSESSMENT = "inventory_viability_assessment"
    REPLENISHMENT_ANALYSIS = "replenishment_analysis"
    ASSET_CONDITION_REPORT = "asset_condition_report"
    INVENTORY_CONCENTRATION_ASSESSMENT = "inventory_concentration_assessment"
    INVENTORY_POSITION_ASSESSMENT = "inventory_position_assessment"
    
    # ---- Logistics & Transport Domain ----
    TRANSPORT_FEASIBILITY = "transport_feasibility"
    ROUTE_OPTIMIZATION_ANALYSIS = "route_optimization_analysis"
    CARBON_IMPACT_ASSESSMENT = "carbon_impact_assessment"
    ROUTE_VULNERABILITY_ASSESSMENT = "route_vulnerability_assessment"
    TRANSPORT_COST_ASSESSMENT = "transport_cost_assessment"
    CARRIER_CAPACITY_ASSESSMENT = "carrier_capacity_assessment"
    
    # ---- Financial & Enterprise Value Domain ----
    ECONOMIC_CONSEQUENCE_ASSESSMENT = "economic_consequence_assessment"
    COST_IMPACT_ANALYSIS = "cost_impact_analysis"
    WORKING_CAPITAL_PROJECTION = "working_capital_projection"
    MARGIN_IMPACT_ANALYSIS = "margin_impact_analysis"
    PENALTY_EXPOSURE_ASSESSMENT = "penalty_exposure_assessment"
```

### 2.2 Validation Rule

```python
def validate_claim_registry(agent_cards: list[AgentCard]) -> list[str]:
    """Run at system startup. Validates all agent contracts
    reference only registered claim types."""
    
    registered = set(vars(ClaimTypeRegistry).values())
    errors = []
    
    for card in agent_cards:
        policy = card.ownership_policy
        
        # Validate owned claims
        for claim in policy.owned_claim_types:
            if claim not in registered:
                errors.append(
                    f"{card.agent_id}: owned_claim '{claim}' not in ClaimTypeRegistry"
                )
        
        # Validate consumed claims
        for source_agent, claims in policy.consumes_from.items():
            for claim in claims:
                if claim not in registered:
                    errors.append(
                        f"{card.agent_id}: consumes '{claim}' from {source_agent} "
                        f"but '{claim}' not in ClaimTypeRegistry"
                    )
                # Also verify the source agent actually owns this claim
                source_card = find_agent(agent_cards, source_agent)
                if source_card and claim not in source_card.ownership_policy.owned_claim_types:
                    errors.append(
                        f"{card.agent_id}: consumes '{claim}' from {source_agent} "
                        f"but {source_agent} does not own '{claim}'"
                    )
        
        # Validate forbidden claims
        for claim in policy.forbidden_claim_types:
            if claim not in registered:
                errors.append(
                    f"{card.agent_id}: forbidden_claim '{claim}' not in ClaimTypeRegistry"
                )
    
    return errors
```

**Enforcement:** If `validate_claim_registry` returns any errors, the system MUST NOT start. All contract references must be valid.

---

## 3. Canonical ActionTypeRegistry

> [!IMPORTANT]
> **NEW SECTION.** Creates the single source of truth for all action types. Every `permitted_action_type`, typed ActionIntent schema, Twin handler, execution capability, and policy constraint MUST derive from this registry.

### 3.1 Registry Definition

```python
class ActionTypeRegistry:
    """Canonical registry of all valid action types.
    Each entry must have:
        - A typed ActionIntent schema
        - A DeterministicImpactEvaluator
        - A Twin handler (or explicit 'not_simulatable' flag)
        - An execution capability binding (or 'advisory_only' flag)
    """
    
    # ---- Logistics Domain ----
    REROUTE_SHIPMENT = "reroute_shipment"
    EXPEDITE_SHIPMENT = "expedite_shipment"
    CHANGE_FREIGHT_MODE = "change_freight_mode"
    
    # ---- Procurement Domain ----
    SWITCH_SUPPLIER = "switch_supplier"
    INCREASE_PURCHASE_ORDER = "increase_purchase_order"
    CANCEL_PURCHASE_ORDER = "cancel_purchase_order"
    EXPEDITE_PURCHASE_ORDER = "expedite_purchase_order"
    
    # ---- Inventory Domain ----
    REALLOCATE_INVENTORY = "reallocate_inventory"
    ADJUST_SAFETY_STOCK = "adjust_safety_stock"
    QUARANTINE_INVENTORY = "quarantine_inventory"
    
    # ---- Demand Domain ----
    PROMOTION_ADJUSTMENT = "promotion_adjustment"
    DEMAND_SIGNAL_OVERRIDE = "demand_signal_override"
    
    # ---- Risk Domain ----
    RISK_MITIGATION_RECOMMENDATION = "risk_mitigation_recommendation"
    COMPLIANCE_HOLD = "compliance_hold"
    
    # ---- Finance Domain ----
    FINANCIAL_IMPACT_FLAG = "financial_impact_flag"
    BUDGET_ESCALATION = "budget_escalation"
    
    # ---- Universal ----
    DO_NOTHING = "do_nothing"
```

### 3.2 Missing Typed Intent Schemas

The following schemas are NEW -- they were declared as permitted actions in agent ownership contracts but had no corresponding typed schema in Amendment 2.

```python
# ---- Demand Domain ----

class PromotionAdjustmentIntent(BaseModel):
    """Agent proposes modifying a promotion schedule in response to disruption."""
    action_type: Literal["promotion_adjustment"] = "promotion_adjustment"
    promotion_id: str
    adjustment_type: Literal["delay", "cancel", "modify_scope", "extend"]
    original_start_date: str                    # ISO 8601
    proposed_start_date: Optional[str]          # ISO 8601 (if delay/extend)
    affected_sku_ids: list[str]
    affected_facility_ids: list[str]
    rationale_claim_ids: list[str]              # Claims supporting this intent

class DemandSignalOverrideIntent(BaseModel):
    """Agent proposes overriding demand forecast for a period."""
    action_type: Literal["demand_signal_override"] = "demand_signal_override"
    sku_id: str
    facility_id: str
    override_type: Literal["increase", "decrease", "hold_current"]
    override_period_start: str                  # ISO 8601
    override_period_end: str                    # ISO 8601
    override_factor: float                      # Multiplier on base forecast
    rationale_claim_ids: list[str]

# ---- Risk Domain ----

class RiskMitigationRecommendationIntent(BaseModel):
    """Agent recommends a risk mitigation strategy."""
    action_type: Literal["risk_mitigation_recommendation"] = "risk_mitigation_recommendation"
    risk_type: Literal[
        "supplier_financial", "geopolitical", "concentration",
        "cascade", "regulatory", "operational"
    ]
    affected_entity_type: str
    affected_entity_id: str
    mitigation_strategy: Literal[
        "diversify_sources", "increase_buffer", "qualify_alternate",
        "hedge_position", "accelerate_qualification", "monitor_closely"
    ]
    urgency: Literal["immediate", "short_term", "medium_term"]
    rationale_claim_ids: list[str]

class ComplianceHoldIntent(BaseModel):
    """Agent recommends placing a compliance hold on an entity."""
    action_type: Literal["compliance_hold"] = "compliance_hold"
    entity_type: Literal["supplier", "product", "shipment", "facility"]
    entity_id: str
    hold_reason: Literal["regulatory", "quality_failure", "safety", "audit_pending"]
    hold_scope: Literal["full_stop", "restricted_operations"]
    recommended_duration_days: Optional[int]
    regulatory_reference: Optional[str]
    rationale_claim_ids: list[str]

# ---- Finance Domain ----

class FinancialImpactFlagIntent(BaseModel):
    """Agent flags a decision for financial review."""
    action_type: Literal["financial_impact_flag"] = "financial_impact_flag"
    flag_type: Literal[
        "budget_threshold_exceeded", "margin_erosion",
        "working_capital_impact", "penalty_exposure",
        "unexpected_cost_escalation"
    ]
    affected_decision_context: str
    threshold_description: str
    rationale_claim_ids: list[str]

class BudgetEscalationIntent(BaseModel):
    """Agent recommends budget escalation for a decision."""
    action_type: Literal["budget_escalation"] = "budget_escalation"
    budget_category: str
    current_allocation_context: str
    escalation_justification: str
    urgency: Literal["immediate", "next_cycle", "advisory"]
    rationale_claim_ids: list[str]
```

### 3.3 Updated ActionIntent Union

```python
# Complete discriminated union of all action intent types
ActionIntent = Union[
    # Logistics
    RerouteShipmentIntent,
    ExpediteShipmentIntent,
    ChangeFreightModeIntent,
    # Procurement
    SwitchSupplierIntent,
    IncreasePurchaseOrderIntent,
    CancelPurchaseOrderIntent,
    ExpeditePurchaseOrderIntent,
    # Inventory
    ReallocateInventoryIntent,
    AdjustSafetyStockIntent,
    QuarantineInventoryIntent,
    # Demand
    PromotionAdjustmentIntent,
    DemandSignalOverrideIntent,
    # Risk
    RiskMitigationRecommendationIntent,
    ComplianceHoldIntent,
    # Finance
    FinancialImpactFlagIntent,
    BudgetEscalationIntent,
    # Universal
    DoNothingIntent,
]
```

### 3.4 Validation

Same pattern as ClaimTypeRegistry: at system startup, validate that every `permitted_action_type` in every agent's DomainOwnershipPolicy has a corresponding entry in the ActionTypeRegistry and a corresponding ActionIntent schema.

---

## 4. Corrected Agent Ownership Contracts

> [!WARNING]
> **REPLACES Section 4.2 of Amendment 2.** All `consumes_from` references now use registered claim types that exist in the source agent's `owned_claim_types`.

```yaml
# Procurement & Supplier Agent (CORRECTED)
ownership:
  owned_entity_types:
    - supplier_operational_performance
    - purchase_order
    - contract_terms
    - vendor_qualification
  owned_metric_types:
    - otif_score
    - lead_time_distribution
    - defect_rate
    - supplier_capacity
  owned_claim_types:
    - supplier_operational_assessment
    - procurement_cost_analysis
    - alternate_sourcing_feasibility
    - supplier_capacity_assessment            # NEW: was missing
  permitted_action_types:
    - switch_supplier
    - increase_purchase_order
    - cancel_purchase_order
    - expedite_purchase_order
  consumes_from:
    risk_resilience:
      - supplier_financial_distress           # EXISTS in Risk owned_claim_types
      - supplier_concentration_risk           # EXISTS in Risk owned_claim_types
      - geopolitical_risk_assessment          # EXISTS in Risk owned_claim_types
  forbidden_claim_types:
    - supplier_financial_distress             # Risk domain
    - economic_consequence_assessment         # Finance domain
  forbidden_action_types:
    - financial_impact_flag
    - compliance_hold

# Risk & Resilience Agent (CORRECTED)
ownership:
  owned_entity_types:
    - supplier_financial_health
    - geopolitical_exposure
    - network_fragility
    - cascade_impact
  owned_metric_types:
    - financial_distress_score
    - concentration_risk_index
    - recovery_time_estimate
    - cascade_propagation_depth
  owned_claim_types:
    - supplier_financial_distress
    - systemic_risk_assessment
    - cascade_failure_analysis
    - regulatory_compliance_status
    - corridor_risk_assessment                # NEW: was missing
    - geopolitical_risk_assessment            # NEW: was missing
    - supplier_concentration_risk             # NEW: was missing
    - network_fragility_assessment            # NEW: was missing
  permitted_action_types:
    - quarantine_inventory
    - risk_mitigation_recommendation
    - compliance_hold
  consumes_from:
    procurement_supplier:
      - supplier_operational_assessment       # FIXED: was 'supplier_operational_assessment' (correct)
      - supplier_capacity_assessment          # FIXED: now exists in Procurement
    logistics_transport:
      - route_vulnerability_assessment        # FIXED: now exists in Logistics
      - transport_feasibility                 # ADDED: also useful
    inventory_asset:
      - inventory_concentration_assessment    # FIXED: now exists in Inventory
      - inventory_position_assessment         # ADDED: for cascade analysis
  forbidden_claim_types:
    - supplier_operational_assessment         # Procurement domain
    - demand_assessment                       # Demand domain
    - cost_impact_analysis                    # Finance domain
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment

# Demand & Commerce Agent (CORRECTED)
ownership:
  owned_entity_types:
    - demand_forecast
    - sales_pattern
    - promotion_calendar
    - pricing_elasticity
  owned_metric_types:
    - forecast_accuracy
    - demand_volatility
    - seasonal_index
    - promotional_lift
  owned_claim_types:
    - demand_assessment
    - commercial_impact_analysis
    - pricing_recommendation
    - revenue_impact_assessment               # NEW: was missing
    - promotional_impact_analysis             # NEW: was missing
  permitted_action_types:
    - adjust_safety_stock
    - promotion_adjustment
    - demand_signal_override
  consumes_from:
    inventory_asset:
      - inventory_position_assessment         # FIXED: now exists in Inventory
    risk_resilience:
      - geopolitical_risk_assessment          # FIXED: now exists in Risk
      - systemic_risk_assessment              # ADDED: for demand impact
  forbidden_claim_types:
    - supplier_operational_assessment
    - transport_feasibility
    - supplier_financial_distress
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment

# Inventory & Asset Management Agent (CORRECTED)
ownership:
  owned_entity_types:
    - inventory_position
    - storage_capacity
    - shelf_life
    - replenishment_schedule
    - goods_receipt
  owned_metric_types:
    - days_of_supply
    - fill_rate
    - inventory_turns
    - storage_utilization
  owned_claim_types:
    - inventory_viability_assessment
    - replenishment_analysis
    - asset_condition_report
    - inventory_concentration_assessment      # NEW: was missing
    - inventory_position_assessment           # NEW: was missing
  permitted_action_types:
    - reallocate_inventory
    - adjust_safety_stock
    - quarantine_inventory
  consumes_from:
    demand_commerce:
      - demand_assessment                     # EXISTS in Demand
    procurement_supplier:
      - supplier_capacity_assessment          # FIXED: now exists in Procurement
      - supplier_operational_assessment       # ADDED: for replenishment timing
  forbidden_claim_types:
    - transport_feasibility
    - supplier_financial_distress
    - route_optimization_analysis
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment

# Logistics & Transport Agent (CORRECTED)
ownership:
  owned_entity_types:
    - transport_lane
    - carrier_capability
    - route_status
    - fleet_asset
    - freight_mode
  owned_metric_types:
    - transit_time
    - route_reliability
    - carrier_performance
    - carbon_per_route
  owned_claim_types:
    - transport_feasibility
    - route_optimization_analysis
    - carbon_impact_assessment
    - route_vulnerability_assessment          # NEW: was missing
    - transport_cost_assessment               # NEW: was missing
    - carrier_capacity_assessment             # NEW: was missing
  permitted_action_types:
    - reroute_shipment
    - expedite_shipment
    - change_freight_mode
  consumes_from:
    risk_resilience:
      - corridor_risk_assessment              # FIXED: now exists in Risk
      - geopolitical_risk_assessment          # ADDED: for route risk
    inventory_asset:
      - inventory_position_assessment         # FIXED: now exists in Inventory
  forbidden_claim_types:
    - supplier_operational_assessment
    - demand_assessment
    - supplier_financial_distress
  forbidden_action_types:
    - switch_supplier
    - cancel_purchase_order

# Financial & Enterprise Value Agent (CORRECTED)
ownership:
  owned_entity_types:
    - cost_model
    - working_capital_impact
    - margin_structure
    - penalty_exposure
  owned_metric_types:
    - landed_cost
    - cash_impact
    - margin_delta
    - expedite_cost
    - penalty_liability
  owned_claim_types:
    - economic_consequence_assessment
    - cost_impact_analysis
    - working_capital_projection
    - margin_impact_analysis                  # NEW: was missing
    - penalty_exposure_assessment             # NEW: was missing
  permitted_action_types:
    - financial_impact_flag
    - budget_escalation
  consumes_from:
    procurement_supplier:
      - procurement_cost_analysis             # EXISTS in Procurement
    logistics_transport:
      - transport_cost_assessment             # FIXED: now exists in Logistics
    demand_commerce:
      - revenue_impact_assessment             # FIXED: now exists in Demand
  forbidden_claim_types:
    - supplier_operational_assessment
    - demand_assessment
    - transport_feasibility
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment
    - reallocate_inventory
```

**Verification:** Every `consumes_from` entry in every agent now references a claim type that:
1. Exists in the `ClaimTypeRegistry`
2. Exists in the source agent's `owned_claim_types`

The ownership vocabulary is now closed and machine-verifiable.

---

## 5. ActionIntent / ActionImpact Separation

> [!WARNING]
> **REPLACES Section 9 of Amendment 2.** Agent-provided actions now contain ONLY intent (structural parameters). Numerical impact values are computed by a deterministic evaluator.

### 5.1 Revised CandidateAction

```python
class CandidateAction(BaseModel):
    """What the agent PROPOSES to do.
    The agent specifies INTENT (what to do).
    The DeterministicImpactEvaluator computes IMPACT (what it costs/gains).
    LLM-provided numerical values NEVER enter CD2F scoring."""
    
    action_id: str
    action_type: str
    intent: ActionIntent                   # Agent-provided: WHAT to do (no numbers)
    impact: Optional[ActionImpact]         # System-computed: WHAT it costs (authoritative)
    impact_computed: bool = False           # True after DeterministicImpactEvaluator runs
    supporting_claims: list[str]           # Claim IDs supporting this action
    evidence: list[EvidenceItem]           # Evidence backing the intent
    proposer_agent_id: str                 # Which agent proposed this
```

### 5.2 Revised Intent Schemas (Logistics/Procurement/Inventory Examples)

Intent schemas contain ONLY structural decision parameters -- identifiers, modes, types. They do NOT contain cost, time, or quantity estimates from the LLM.

```python
class RerouteShipmentIntent(BaseModel):
    action_type: Literal["reroute_shipment"] = "reroute_shipment"
    shipment_id: str
    original_carrier_id: str
    new_carrier_id: str
    new_route_lane_id: str
    freight_mode: Literal["road", "air", "sea", "rail", "multimodal"]
    # NO estimated_transit_days -- computed by impact evaluator
    # NO incremental_cost_usd -- computed by impact evaluator

class SwitchSupplierIntent(BaseModel):
    action_type: Literal["switch_supplier"] = "switch_supplier"
    po_id: str
    original_supplier_id: str
    new_supplier_id: str
    product_id: str
    quantity: int                      # Intent quantity (validated against capacity)
    # NO new_lead_time_days -- computed from supplier capability data
    # NO price_delta_usd -- computed from contract/pricing data

class AdjustSafetyStockIntent(BaseModel):
    action_type: Literal["adjust_safety_stock"] = "adjust_safety_stock"
    facility_id: str
    sku_id: str
    direction: Literal["increase", "decrease"]
    target_days_of_supply: float      # Desired target (not current value)
    adjustment_reason_claim_ids: list[str]
    # NO current_safety_stock -- retrieved from authoritative source
    # NO new_safety_stock -- computed from target_dos and demand forecast
```

### 5.3 DeterministicImpactEvaluator

```python
class ActionImpact(BaseModel):
    """Authoritatively computed impact of a candidate action.
    Produced by deterministic evaluation, not by LLM inference."""
    
    action_id: str
    evaluated_at: datetime
    
    # Impact dimensions (same as CD2F objective dimensions)
    cost_delta_usd: float              # From authoritative cost models
    service_level_delta: float         # From demand/inventory models
    risk_delta: float                  # From risk models
    lead_time_delta_days: float        # From logistics/carrier data
    carbon_delta_kg: float             # From emission factor tables
    cash_flow_delta_usd: float         # From financial models
    inventory_health_delta: float      # From inventory models
    
    # Provenance
    data_sources: list[str]            # Which authoritative sources were used
    computation_method: str            # Which evaluator computed this
    computation_version: str           # Evaluator version
    
    # Confidence
    impact_confidence: float           # How confident is the computation
    missing_data_flags: list[str]      # Any data gaps that affect accuracy

class DeterministicImpactEvaluator:
    """Computes authoritative impact for a CandidateAction.
    Uses only authoritative data sources (PostgreSQL, cost tables,
    carrier capability data, demand models). Never uses LLM output."""
    
    def evaluate(
        self,
        action: CandidateAction,
        snapshot: DecisionSnapshot,
        policy: DecisionPolicy
    ) -> ActionImpact:
        """Compute deterministic impact for a single action."""
        
        if isinstance(action.intent, RerouteShipmentIntent):
            return self._evaluate_reroute(action.intent, snapshot)
        elif isinstance(action.intent, SwitchSupplierIntent):
            return self._evaluate_switch_supplier(action.intent, snapshot)
        # ... dispatch for each action type
    
    def _evaluate_reroute(
        self,
        intent: RerouteShipmentIntent,
        snapshot: DecisionSnapshot
    ) -> ActionImpact:
        # Query authoritative carrier capability data
        carrier = self.data_service.get_carrier(
            intent.new_carrier_id, as_of=snapshot.observation_cutoff
        )
        route = self.data_service.get_route(
            intent.new_route_lane_id, as_of=snapshot.observation_cutoff
        )
        
        # Compute from authoritative sources
        transit_days = route.base_transit_days
        cost_delta = route.rate_per_unit - original_route.rate_per_unit
        carbon_delta = route.emission_factor - original_route.emission_factor
        
        return ActionImpact(
            cost_delta_usd=cost_delta,
            lead_time_delta_days=transit_days - original_transit,
            carbon_delta_kg=carbon_delta,
            # ... other dimensions
            data_sources=["carrier_capability_table", "route_rate_table"],
            computation_method="deterministic_route_evaluation",
        )
```

### 5.4 Pipeline Integration

The DeterministicImpactEvaluator runs as part of the candidate normalization pipeline, AFTER schema and entity validation, BEFORE pruning:

```
STEP 1: EXTRACT
STEP 2: SCHEMA VALIDATION
STEP 3: ENTITY VALIDATION
STEP 4: DETERMINISTIC IMPACT EVALUATION    (NEW)
STEP 5: HARD-CONSTRAINT PRE-CHECK         (now uses authoritative impact)
STEP 6: DEDUPLICATION
STEP 7: SAFE DOMINANCE PRUNING            (now uses authoritative impact)
STEP 8: CANDIDATE BUDGET ENFORCEMENT
STEP 9: COMBINATION SYNTHESIS
```

This ensures that all pruning decisions use deterministic impact values, not LLM estimates.

---

## 6. ActionDefinition Ownership Model

> [!IMPORTANT]
> **NEW SECTION.** Defines ownership semantics for action types that can be proposed by multiple agents.

```python
class ActionDefinition(BaseModel):
    """Canonical definition of an action type with ownership semantics.
    Stored in the ActionTypeRegistry."""
    
    action_type: str
    
    # Ownership
    primary_owner_agent: str               # Agent with parameter authority
    permitted_proposers: list[str]         # Agents who may propose this action
    
    # Authority
    parameter_authority: str               # Agent that validates/refines parameters
    impact_authority: str                  # "deterministic_impact_service" (always)
    
    # Execution
    execution_capability_id: str           # Which MCP capability handles execution
    simulatable: bool                      # Can Twin simulate this action?
    advisory_only: bool                    # Does this action only flag/recommend?
```

### Per-Action Definitions

```yaml
# Actions with shared proposers
adjust_safety_stock:
  primary_owner: inventory_asset
  permitted_proposers: [inventory_asset, demand_commerce]
  parameter_authority: inventory_asset
  impact_authority: deterministic_impact_service
  execution_capability: inventory_management
  simulatable: true
  advisory_only: false

quarantine_inventory:
  primary_owner: inventory_asset
  permitted_proposers: [inventory_asset, risk_resilience]
  parameter_authority: inventory_asset
  impact_authority: deterministic_impact_service
  execution_capability: inventory_management
  simulatable: true
  advisory_only: false

# Advisory-only actions (no physical execution)
risk_mitigation_recommendation:
  primary_owner: risk_resilience
  permitted_proposers: [risk_resilience]
  parameter_authority: risk_resilience
  impact_authority: deterministic_impact_service
  execution_capability: null
  simulatable: false
  advisory_only: true

financial_impact_flag:
  primary_owner: financial_enterprise
  permitted_proposers: [financial_enterprise]
  parameter_authority: financial_enterprise
  impact_authority: deterministic_impact_service
  execution_capability: null
  simulatable: false
  advisory_only: true

budget_escalation:
  primary_owner: financial_enterprise
  permitted_proposers: [financial_enterprise]
  parameter_authority: financial_enterprise
  impact_authority: deterministic_impact_service
  execution_capability: null
  simulatable: false
  advisory_only: true

compliance_hold:
  primary_owner: risk_resilience
  permitted_proposers: [risk_resilience]
  parameter_authority: risk_resilience
  impact_authority: deterministic_impact_service
  execution_capability: compliance_management
  simulatable: true
  advisory_only: false
```

**Cross-Proposer Resolution:** When both Demand and Inventory propose `adjust_safety_stock`, the Coordinator:
1. Passes both intents to Inventory (the `parameter_authority`)
2. Inventory validates and refines the parameters
3. The DeterministicImpactEvaluator computes impact for each variant
4. Both enter the candidate set as separate candidates (potentially merged during deduplication if parameters are identical)

---

## 7. Critical Evidence Assessment

> [!IMPORTANT]
> **EXTENDS Section 6 of Amendment 2.** Adds critical-fact-specific assessment to prevent average freshness from concealing stale critical facts.

### 7.1 CriticalEvidenceAssessment Schema

```python
class CriticalEvidenceAssessment(BaseModel):
    """Assessment of evidence items that are decision-critical.
    A fact is 'critical' if removing it would change the candidate ranking
    or if it is required by the disruption type profile."""
    
    critical_facts_identified: int        # How many critical facts are needed
    critical_facts_present: int           # How many are actually present
    critical_facts_fresh: int             # How many are within freshness threshold
    critical_facts_authoritative: int     # How many are from authoritative source
    
    # Worst-case metrics (NOT averages)
    min_critical_freshness: float         # Freshness of the STALEST critical fact
    min_critical_authority: str           # Authority level of the WEAKEST critical fact
    
    # Detail
    critical_fact_details: list[CriticalFactStatus]
    
    # Verdict
    all_critical_facts_sufficient: bool

class CriticalFactStatus(BaseModel):
    fact_id: str
    entity_type: str
    entity_id: str
    claim_type: str
    present: bool
    freshness: float
    authority_level: str
    sufficient: bool
    insufficiency_reason: Optional[str]
```

### 7.2 Disruption Type Critical Fact Profiles

```yaml
# profiles/mvp-electronics/critical_facts.yaml
disruption_profiles:
  supplier_delay:
    critical_facts:
      - entity_type: supplier
        claim_type: current_state
        required_fields: [status, capacity, lead_time, quality_score]
        min_freshness: 0.80
      - entity_type: inventory
        claim_type: current_state
        required_fields: [position, days_of_supply, committed_stock]
        min_freshness: 0.80
      - entity_type: alternate_suppliers
        claim_type: topological
        required_fields: [availability, capacity, qualification_status]
        min_freshness: 0.60
    
  demand_spike:
    critical_facts:
      - entity_type: demand_forecast
        claim_type: forecast
        required_fields: [base_forecast, trend, seasonality]
        min_freshness: 0.70
      - entity_type: inventory
        claim_type: current_state
        required_fields: [position, pipeline_stock, safety_stock]
        min_freshness: 0.80
```

### 7.3 Revised Verdict Logic

```
SUFFICIENT:
    domain_coverage.coverage_score >= policy.min_domain_coverage
    AND evidence_quality.avg_evidence_freshness >= policy.min_evidence_freshness
    AND critical_evidence.all_critical_facts_sufficient == True    (NEW)
    AND consistency.contradiction_severity != "BLOCKING"
    AND evidence_quality.model_validity_score >= 0.50

MARGINALLY_SUFFICIENT:
    domain_coverage.coverage_score >= 0.60
    AND evidence_quality.avg_evidence_freshness >= 0.40
    AND critical_evidence.critical_facts_present >= critical_evidence.critical_facts_identified
    AND critical_evidence.min_critical_freshness >= 0.50    (NEW: critical facts must meet minimum)
    AND consistency.contradiction_severity != "BLOCKING"

INSUFFICIENT:
    Any of the above fail
    OR critical_evidence.all_critical_facts_sufficient == False    (NEW)
    OR consistency.contradiction_severity == "BLOCKING"
```

The key addition: a single stale critical fact can independently trigger INSUFFICIENT even if the overall average is high.

---

## 8. Post-Snapshot Evidence Resolution

> [!WARNING]
> **CORRECTS Section 7.2 of Amendment 2.** Removes the "allowed but noted" language that contradicted Invariant 8.

### 8.1 Corrected Evidence Validation

```python
def validate_evidence_against_snapshot(
    evidence: EvidenceItem,
    snapshot: DecisionSnapshot
) -> EvidenceValidation:
    """Validate evidence against the decision snapshot boundary."""
    
    if evidence.data_as_of > snapshot.observation_cutoff:
        # POST-SNAPSHOT EVIDENCE: REJECT from decision state
        return EvidenceValidation(
            status="REJECTED",
            reason="POST_SNAPSHOT",
            detail=f"Evidence timestamp {evidence.data_as_of} is after "
                   f"snapshot cutoff {snapshot.observation_cutoff}",
            quarantine=True,              # Record for audit/HITL review
            influences_decision=False,     # MUST NOT affect scoring
        )
    
    fact_age = snapshot.observation_cutoff - evidence.data_as_of
    
    if fact_age > timedelta(minutes=snapshot.max_fact_age_minutes):
        return EvidenceValidation(
            status="STALE",
            reason="EXCEEDS_FRESHNESS_THRESHOLD",
            freshness_score=max(0.0, 1.0 - (fact_age.total_seconds() / 
                               (snapshot.max_fact_age_minutes * 60))),
            influences_decision=True,      # Allowed but downgrades quality score
        )
    
    return EvidenceValidation(
        status="VALID",
        freshness_score=1.0 - (fact_age.total_seconds() / 
                              (snapshot.max_fact_age_minutes * 60)),
        influences_decision=True,
    )
```

### 8.2 Snapshot Advancement (When Post-Snapshot Evidence Is Critical)

```python
def handle_critical_state_change(
    session: DecisionSession,
    detected_change: StateChange,
    coordinator: CoordinatorService
) -> SnapshotAdvancementDecision:
    """When post-snapshot evidence reveals a critical state change,
    the Coordinator must decide whether to advance the snapshot."""
    
    if session.status in {"CD2F_IN_PROGRESS", "EXECUTION_AUTHORIZED"}:
        # Too late to advance -- flag as stale decision
        return SnapshotAdvancementDecision(
            action="FLAG_STALE",
            reason="Session too advanced to restart"
        )
    
    if detected_change.affects_critical_facts(session.disruption_type):
        # Critical change -- advance snapshot and restart affected agents
        return SnapshotAdvancementDecision(
            action="ADVANCE_AND_RESTART",
            new_snapshot=create_decision_snapshot(session),
            restart_agents=detected_change.affected_agent_ids,
        )
    
    # Non-critical change -- continue with current snapshot
    return SnapshotAdvancementDecision(
        action="CONTINUE",
        reason="State change does not affect critical facts"
    )
```

---

## 9. Decision Snapshot Refinements

> [!IMPORTANT]
> **EXTENDS Section 7 of Amendment 2.** Adds consistency assessment, trigger-state binding, and corrected freshness computation.

### 9.1 Enhanced DecisionSnapshot

```python
class DecisionSnapshot(BaseModel):
    # ... all existing fields from Amendment 2 ...
    
    # Consistency assessment (NEW)
    neo4j_source_lsn: int                      # Which PostgreSQL LSN Neo4j is projected from
    pgvector_source_lsn: int                   # Which PostgreSQL LSN pgvector corpus covers
    neo4j_lag_behind_pg: int                   # enterprise_state_version - neo4j_source_lsn
    pgvector_lag_behind_pg: int                # enterprise_state_version - pgvector_source_lsn
    
    consistency_class: Literal[
        "FULLY_CONSISTENT",                    # All projections current (lag = 0)
        "ACCEPTABLE_LAG",                      # Lag within policy thresholds
        "STALE_PROJECTION",                    # One or more projections significantly behind
    ]
    
    # Trigger binding (NEW)
    trigger_event_id: str                      # The disruption event that started this session
    trigger_event_timestamp: datetime          # When the trigger event occurred
    trigger_event_sequence: Optional[int]      # Kafka offset or event sequence

    # Freshness computation method (NEW)
    freshness_reference: Literal[
        "OBSERVATION_CUTOFF",                  # Default: age = observation_cutoff - data_as_of
        "WALL_CLOCK",                          # Legacy: age = now - data_as_of
    ] = "OBSERVATION_CUTOFF"
```

### 9.2 Corrected Freshness Computation

```python
def compute_fact_freshness(
    fact: EvidenceItem,
    snapshot: DecisionSnapshot
) -> float:
    """Fact freshness is ALWAYS relative to the decision's observation boundary,
    not to wall-clock time. This enables historical scenario evaluation."""
    
    fact_age = snapshot.observation_cutoff - fact.data_as_of
    max_age = timedelta(minutes=snapshot.max_fact_age_minutes)
    
    if fact_age <= timedelta(0):
        return 1.0  # Fact is at or after cutoff (but pre-snapshot)
    
    if fact_age >= max_age:
        return 0.0  # Fact is stale
    
    return 1.0 - (fact_age / max_age)
```

---

## 10. Safe Candidate Pruning

> [!WARNING]
> **REPLACES Section 8 of Amendment 2.** Pre-Twin pruning is restricted to deterministic criteria. Budget enforcement uses upper confidence bounds.

### 10.1 Revised Pipeline

```
STEP 1: EXTRACT
    Collect all candidate actions from all revised agent proposals
    Raw candidates: up to N (6 agents x max_candidates_per_agent)

STEP 2: SCHEMA VALIDATION
    Validate every candidate intent against its typed ActionIntent schema
    CRITERION: deterministic (schema validation is binary)
    Reject candidates with invalid/missing parameters

STEP 3: ENTITY VALIDATION
    Verify all referenced entity IDs exist in D2 as of the DecisionSnapshot
    CRITERION: deterministic (entity existence is factual)
    Reject candidates referencing non-existent entities

STEP 4: DETERMINISTIC IMPACT EVALUATION (NEW)
    Run DeterministicImpactEvaluator for each valid candidate
    Compute authoritative cost, time, risk, service impact
    SOURCE: authoritative data sources, not LLM estimates
    Candidates where impact cannot be computed are flagged but retained

STEP 5: HARD-CONSTRAINT PRE-CHECK
    Eliminate candidates violating hard constraints from DecisionPolicy
    CRITERION: deterministic (hard constraints are binary)
    SOURCE: DeterministicImpactEvaluator output + policy constraints
    Example: proposed route has no reefer capability for perishable -> eliminate

STEP 6: DEDUPLICATION
    Merge semantically identical candidates from different agents
    CRITERION: structural comparison of intent parameters
    Merge rule: keep the candidate with higher-authority evidence

STEP 7: SAFE DOMINANCE PRUNING (REVISED)
    A candidate is dominated ONLY if:
        - It is strictly worse than another on ALL objective dimensions
        - Using DETERMINISTIC impact evaluations (from Step 4)
        - Comparison uses only authoritative computed values
    
    If impact_computed == False for either candidate:
        -> DO NOT prune. Retain for Twin evaluation.
    
    Safety margin:
        dominance_margin = policy.dominance_pruning_margin (default 0.10)
        A is dominated by B only if B is better by at least dominance_margin
        on every dimension. This prevents pruning candidates that are
        very close on any dimension.

STEP 8: CANDIDATE BUDGET ENFORCEMENT (REVISED)
    If remaining candidates > max_simulation_branches:
        
        Selection criterion: UPPER CONFIDENCE BOUND
            UCB(c) = estimated_score(c) + alpha * impact_uncertainty(c)
        
        where:
            estimated_score = policy-normalized weighted objective (from Step 4 impact)
            impact_uncertainty = confidence width from DeterministicImpactEvaluator
            alpha = policy.exploration_factor (default 1.0)
        
        Retain top-K candidates by UCB
        
        Guarantees:
            - ALWAYS include "do nothing + buffer" baseline
            - ALWAYS include at least one candidate per assigned domain
              (if that domain produced valid candidates)
            - High-uncertainty candidates with potential upside are retained
        
        Maximum output: max_simulation_branches + 1 (baseline)

STEP 9: COMBINATION SYNTHESIS (if warranted)
    Generate up to max_combined_actions composite candidates
    ONLY for non-conflicting candidates from different domains
    
    Conflict check uses ActionDefinition:
        If two actions share the same primary_owner_agent:
            -> Not combined (already considered by the agent)
        If two actions affect the same entity:
            -> Validate compatibility before combining

OUTPUT: Normalized candidate set ready for Twin simulation
```

### 10.2 Key Invariant

```
NO candidate is eliminated before Twin simulation unless:
    1. Its intent schema is invalid (Step 2)
    2. Its referenced entities do not exist (Step 3)
    3. It violates a hard constraint using deterministic evaluation (Step 5)
    4. It is a structural duplicate of another candidate (Step 6)
    5. It is PROVABLY dominated using deterministic impact values (Step 7)
    6. Budget is exceeded AND it has the lowest upper confidence bound (Step 8)

LLM-estimated impact values are NEVER used for pruning decisions.
```

---

## 11. Policy-Fixed Objective Normalization

> [!WARNING]
> **REPLACES the normalization approach in Section 11.2 of Amendment 2.** Candidate-relative normalization is replaced with policy-fixed reference scales.

### 11.1 ObjectiveNormalization Schema

```python
class ObjectiveNormalization(BaseModel):
    """Policy-defined reference scales for objective normalization.
    Fixed per profile. Independent of the candidate set.
    Ensures that adding/removing a candidate does not change
    other candidates' scores."""
    
    cost_reference_usd: float = 100000.0
    service_reference_pct: float = 10.0        # 10% service gap = normalized 1.0
    risk_reference: float = 1.0                # Risk is already [0,1]
    inventory_reference_dos: float = 30.0      # 30 days-of-supply gap = normalized 1.0
    lead_time_reference_days: float = 30.0
    carbon_reference_kg: float = 10000.0
    cash_flow_reference_usd: float = 50000.0
```

### 11.2 Normalization Functions

```python
def normalize_metric(
    raw_value: float,
    reference_scale: float,
    direction: Literal["minimize", "maximize"]
) -> float:
    """Normalize a metric against a policy-fixed reference scale.
    Output is [0, 1] where 1.0 = worst possible (full reference magnitude)."""
    
    normalized = min(1.0, max(0.0, abs(raw_value) / reference_scale))
    
    if direction == "maximize":
        normalized = 1.0 - normalized  # Invert for maximization objectives
    
    return normalized
```

### 11.3 Revised Objective Score Computation

```
For each feasible candidate c:
    
    J(c) = (
        + w.service_level * (1.0 - normalize(service_gap(c), ref.service_reference_pct, "minimize"))
        - w.cost          * normalize(cost_delta(c), ref.cost_reference_usd, "minimize")
        - w.risk          * normalize(risk_score(c), ref.risk_reference, "minimize")
        - w.inventory     * normalize(inventory_gap(c), ref.inventory_reference_dos, "minimize")
        - w.lead_time     * normalize(lead_time_delta(c), ref.lead_time_reference_days, "minimize")
        - w.carbon        * normalize(carbon_delta(c), ref.carbon_reference_kg, "minimize")
        - w.cash_flow     * normalize(cash_impact(c), ref.cash_flow_reference_usd, "minimize")
    )
    
    Source for all raw values: ActionImpact (from DeterministicImpactEvaluator)
                              + SimulationResult (from Twin, when available)

    Normalization references: ObjectiveNormalization (from DecisionPolicy)
```

**The ObjectiveNormalization is part of the DecisionPolicy and loaded from the profile YAML:**

```yaml
decision_policy:
  normalization:
    cost_reference_usd: 100000
    service_reference_pct: 10.0
    risk_reference: 1.0
    inventory_reference_dos: 30
    lead_time_reference_days: 30
    carbon_reference_kg: 10000
    cash_flow_reference_usd: 50000
```

---

## 12. Proper Pareto Analysis

> [!WARNING]
> **REPLACES Stage 4 of the CD2F arbitration process (Section 11.2 of Amendment 2).**

```
STAGE 4: PARETO FRONTIER AND AMBIGUITY ANALYSIS (Revised)

    STEP 4a: COMPUTE PARETO FRONTIER
        For each pair of feasible candidates (A, B):
            A_dominates_B = True if:
                A.impact[d] >= B.impact[d] for ALL objective dimensions d
                AND A.impact[d] > B.impact[d] for AT LEAST ONE dimension d
                (respecting direction: higher is better for service, lower is
                better for cost/risk/lead_time/carbon)
            
            If A dominates B:
                Mark B as PARETO_DOMINATED
        
        Pareto frontier = all candidates NOT marked as PARETO_DOMINATED
        
        Record: for each dominated candidate, which candidate dominates it
                and on which dimensions.

    STEP 4b: FRONTIER SIZE ANALYSIS
        If Pareto frontier has exactly 1 candidate:
            -> PARETO_DOMINANT: clear winner on all trade-offs
            -> Proceed to execution authorization
            -> decision_confidence = "PARETO_DOMINANT"
        
        If Pareto frontier has > 1 candidate:
            -> Apply weighted objective scores to frontier candidates ONLY
            -> Compute J_final for each frontier candidate
            
            If |J_final(rank_1) - J_final(rank_2)| >= policy.ambiguity_threshold:
                -> POLICY_RESOLVED: weights break the tie
                -> Select rank_1
                -> decision_confidence = "POLICY_WEIGHT_SELECTED"
                -> Record which dimensions favored each candidate
            
            If |J_final(rank_1) - J_final(rank_2)| < policy.ambiguity_threshold:
                -> GENUINE_PARETO_AMBIGUITY
                -> Generate trade-off summary:
                    For each frontier candidate:
                        List dimensions where it is superior
                        List dimensions where it is inferior
                -> HITL escalation with Pareto frontier visualization
                -> decision_confidence = "AMBIGUOUS_REQUIRES_HITL"

    STEP 4c: PARETO METADATA
        Record in DecisionRecord:
            pareto_frontier_size: int
            dominated_candidates: list[DominatedCandidate]
            decision_confidence: str
            winning_dimensions: list[str]  # If policy-resolved, which dimensions mattered
```

---

## 13. Twin Requirement Classification

> [!IMPORTANT]
> **EXTENDS Section 10 of Amendment 2.** Adds a classification system that determines whether Twin simulation is required, recommended, or advisory for each decision.

```python
class TwinRequirement(str, Enum):
    REQUIRED = "REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    ADVISORY = "ADVISORY"

class SimulationMateriality(BaseModel):
    """Multi-dimensional assessment of whether Twin simulation is warranted."""
    financial_exposure_usd: float
    service_level_impact: float
    risk_exposure: float
    regulatory_relevance: bool
    cascade_potential: float
    novelty_score: float
    
    def classify(self, policy: SimulationPolicy) -> TwinRequirement:
        if (self.financial_exposure_usd > policy.twin_required_cost_threshold
            or self.regulatory_relevance
            or self.cascade_potential > policy.cascade_threshold
            or self.novelty_score > policy.novelty_threshold):
            return TwinRequirement.REQUIRED
        
        if (self.financial_exposure_usd > policy.simulation_trigger_threshold_usd
            or self.service_level_impact > policy.service_threshold
            or self.risk_exposure > policy.risk_threshold):
            return TwinRequirement.RECOMMENDED
        
        return TwinRequirement.ADVISORY
```

### Failure Response by Requirement Level

```
REQUIRED + TWIN_TIMEOUT:
    -> NO autonomous CD2F decision
    -> HITL escalation (Tier-3)
    -> Record: "Twin required but timed out; autonomous decision prohibited"

RECOMMENDED + TWIN_TIMEOUT:
    -> CD2F proceeds with DEGRADED_MODE flag
    -> Autonomy reduced: max Tier-2 (never Tier-1)
    -> Uncertainty penalty increased by policy.twin_timeout_penalty_factor
    -> Record: "Twin recommended but timed out; proceeding with elevated caution"

ADVISORY + TWIN_TIMEOUT:
    -> CD2F proceeds normally
    -> Log timeout for operational monitoring
    -> No autonomy or uncertainty adjustment
```

### SimulationPolicy Extension

```yaml
simulation_policy:
  # ... existing fields ...
  
  # Twin requirement thresholds (NEW)
  twin_required_cost_threshold: 200000.0      # USD above which Twin is REQUIRED
  cascade_threshold: 0.70                      # Cascade potential above which Twin is REQUIRED
  novelty_threshold: 0.80                      # Novelty score above which Twin is REQUIRED
  service_threshold: 0.15                      # Service impact above which Twin is RECOMMENDED
  risk_threshold: 0.50                         # Risk exposure above which Twin is RECOMMENDED
  twin_timeout_penalty_factor: 1.5             # Multiplier on uncertainty when Twin times out
```

---

## 14. Corrected Policy Precedence

> [!WARNING]
> **REPLACES Section 13.3 of Amendment 2.** Separates platform safety invariants (domain-agnostic) from profile-defined regulations (domain-specific).

```
LEVEL 1: PLATFORM SAFETY INVARIANTS                (hard-coded, domain-agnostic)
    These are structural properties of the SCOF platform.
    No profile can override them.
    Examples:
        - No autonomous execution in non-production contexts
        - No external side effects from read-only capabilities
        - No mutation of Layer 1 or Layer 2 state from Twin operations
        - No decision without evidence sufficiency assessment
        - No execution without decision approval
    
    These are NOT domain-specific rules. "Cold-chain quarantine"
    is NOT a platform invariant -- it is a domain regulation.

LEVEL 2: PROFILE REGULATORY CONSTRAINTS             (from profile YAML, domain-specific)
    These are domain-specific regulations configured per deployment.
    Examples:
        - Cold-chain temperature requirements
        - Pharmaceutical recall procedures  
        - Hazardous material transport restrictions
        - Dual-source procurement requirements
    
    Defined in: profile YAML under regulatory_constraints section
    Enforced as: additional hard constraints in DecisionPolicy

LEVEL 3: ENTERPRISE HARD CONSTRAINTS                (from DecisionPolicy.hard_constraints)
    Examples: capacity limits, budget thresholds, reefer requirements.

LEVEL 4: PROFILE-SPECIFIC POLICIES                  (from DecisionPolicy)
    Examples: objective weights, evidence thresholds, deliberation bounds.

LEVEL 5: SOFT OBJECTIVES                            (from DecisionPolicy.soft_constraints)
    Examples: preferred carrier preference, sustainability targets.

LEVEL 6: AGENT PREFERENCES                          (lowest authority)
    Examples: agent's recommended_action_id.
```

---

## 15. Policy Deduplication

> [!IMPORTANT]
> **CORRECTS Sections 11.1 and 13.1 of Amendment 2.** Removes duplicate policy fields and defines clear boundary between CD2F and ExecutionPolicy.

### Removed from DecisionObjective

```python
class DecisionObjective(BaseModel):
    """The organization's formal definition of 'best'."""
    
    weights: ObjectiveWeights
    normalization: ObjectiveNormalization     # NEW: reference scales
    hard_constraints: list[HardConstraint]
    soft_constraints: list[SoftConstraint]
    
    # REMOVED: max_acceptable_risk -- moved to CD2F feasibility config
    # REMOVED: max_autonomous_cost_usd -- belongs ONLY in ExecutionPolicy
    
    pareto_ambiguity_threshold: float
    uncertainty_escalation_threshold: float
```

### Clarified Boundaries

```
CD2F (DecisionObjective):
    Defines what "best" means.
    Weights, constraints, normalization.
    Determines WHICH candidate wins.
    Does NOT determine whether execution is autonomous.

ExecutionPolicyService (ExecutionPolicy):
    Defines execution authorization rules.
    max_autonomous_cost_usd
    max_autonomous_risk
    hitl_required_action_types
    Determines WHETHER the winner is executed autonomously.

Invariant:
    These are separate concerns. CD2F selects the best candidate.
    ExecutionPolicy decides if that selection can be auto-executed.
    There is no duplication because they answer different questions.
```

---

## 16. CD2F Description Refinement

> [!IMPORTANT]
> **CORRECTS Section 11.3 of Amendment 2.** Refines the description of CD2F's nature.

Replace:

> "CD2F is a pure computation engine"

With:

> "CD2F is a deterministic arbitration engine over an explicitly materialized DecisionContext. Given identical inputs (candidates, evidence, simulation results, reliability scores, and policy), CD2F produces identical outputs. The determinism applies to CD2F's own computation; the upstream subsystems that produce its inputs are architecturally complex but their complexity does not contaminate CD2F's arbitration logic."

---

## 17. R_i Agent Influence Status

> [!IMPORTANT]
> **EXTENDS Section 18 of Amendment 2.** Adds graduated influence status to prevent unreliable agents from influencing decisions while maintaining their ability to recover.

```python
class AgentInfluenceStatus(str, Enum):
    FULL = "FULL"
    REDUCED = "REDUCED"
    ADVISORY = "ADVISORY"

def determine_influence_status(
    r_i: ReliabilityScore,
    policy: ReliabilityGovernancePolicy
) -> AgentInfluenceStatus:
    
    if r_i.composite_r_i >= policy.full_influence_threshold:     # default 0.40
        return AgentInfluenceStatus.FULL
    
    if r_i.composite_r_i >= policy.advisory_threshold:           # default 0.20
        return AgentInfluenceStatus.REDUCED
    
    return AgentInfluenceStatus.ADVISORY
```

**Behavioral differences:**

```
FULL:
    Agent proposals enter CD2F scoring normally.
    Agent R_i is used in uncertainty calculation.

REDUCED:
    Agent proposals enter CD2F scoring with elevated uncertainty penalty.
    Agent proposals are flagged for extra scrutiny in HITL review.
    Agent R_i is used with a dampening factor.

ADVISORY:
    Agent proposals are RECORDED in the Deliberation Table.
    Agent proposals do NOT enter CD2F scoring.
    Agent proposals are visible in D9 console for human review.
    Agent continues generating proposals (enabling R_i recovery
    when its model is retrained or improved).
```

---

## 18. Decomposed Reliability Metrics

> [!IMPORTANT]
> **EXTENDS Section 18 of Amendment 2.** Separates R_i into causal sub-metrics.

```python
class DecomposedReliability(BaseModel):
    """Separate reliability dimensions for clearer causal attribution."""
    
    agent_id: str
    disruption_type: str
    model_version: str
    evaluation_window: tuple[datetime, datetime]
    
    # Claim reliability: did the agent's factual claims match reality?
    claim_accuracy: float                  # Fraction of claims verified as correct
    claim_sample_size: int
    
    # Calibration quality: did stated confidence match actual accuracy?
    calibration_quality: float             # ECE or similar calibration metric
    
    # Constraint compliance: did proposed actions satisfy constraints?
    constraint_compliance: float           # Fraction of proposals without violations
    
    # Action outcome quality: when THIS agent's action was selected, did it work?
    # Only computed for sessions where this agent's action was chosen by CD2F.
    action_outcome_quality: Optional[float]
    action_outcome_sample_size: int
    
    # Composite
    composite_r_i: float
    confidence_interval: tuple[float, float]
    
    # Status
    influence_status: AgentInfluenceStatus
```

---

## 19. Event Sequence Allocation

> [!IMPORTANT]
> **EXTENDS Section 16 of Amendment 2.** Defines how monotonically increasing sequence numbers are allocated.

### Mechanism

The Coordinator is the **single writer** to the deliberation event stream. Agents do not write events directly. Therefore sequence allocation is naturally serialized:

```python
class DeliberationService:
    """The Coordinator's internal service for managing deliberation events.
    All events are posted through this service, ensuring serial sequence allocation."""
    
    def post_event(
        self,
        session_id: str,
        event_type: str,
        actor: str,
        payload: dict,
        causation_id: str
    ) -> DeliberationEvent:
        """Atomically allocate sequence number and persist event."""
        
        # Atomic increment + insert in a single PostgreSQL transaction
        with db.transaction():
            sequence = db.execute(
                "UPDATE deliberation_sessions "
                "SET current_sequence = current_sequence + 1 "
                "WHERE session_id = %s "
                "RETURNING current_sequence",
                [session_id]
            ).scalar()
            
            event = DeliberationEvent(
                event_id=generate_uuid_v7(),
                session_id=session_id,
                sequence_number=sequence,
                event_type=event_type,
                actor=actor,
                payload=payload,
                timestamp=datetime.utcnow(),
                causation_id=causation_id,
                correlation_id=session_id,
            )
            
            db.insert("deliberation_events", event)
            # Outbox entry created in same transaction
            db.insert("outbox", create_outbox_entry(event))
        
        return event
```

**Why single-writer is safe:** The LangGraph state machine executes steps sequentially (fan-out is parallel agent execution, but event posting is done by the Coordinator during fan-in). Even if agents submit proposals concurrently, the Coordinator serializes event posting.

---

## 20. Aggregate vs Session Sequence Relationship

> [!IMPORTANT]
> **EXTENDS Sections 16 and 19 of Amendment 2.** Defines the explicit relationship between the two ordering systems.

```
AGGREGATE VERSION (in SCOFEvent):
    Scope: per aggregate instance (e.g., deliberation_item "DI-003")
    Purpose: consumer idempotency
    Rule: event.aggregate_version must equal current_stored_version + 1
    
SESSION SEQUENCE (in DeliberationEvent):
    Scope: per decision session
    Purpose: session replay, event ordering
    Rule: monotonically increasing within session
    
RELATIONSHIP:
    These are INDEPENDENT orderings serving different purposes.
    A single DeliberationEvent may have:
        sequence_number = 72
        AND affect aggregate "DI-003" at aggregate_version = 5
    
    The next event (sequence 73) may affect a different aggregate
    (e.g., "DI-007" at aggregate_version = 2).
    
    Consumer idempotency checks aggregate_version.
    Session replay uses sequence_number.
    
    They do NOT need to be synchronized or correlated.
```

---

## 21. Hot-Path Cache Key Correction

> [!WARNING]
> **CORRECTS the cache key in Section 26 of Amendment 2.**

```python
# BEFORE (Amendment 2):
cache_key = (session_id, agent_id, entity_type, entity_id)

# AFTER (Amendment 3):
cache_key = (
    session_id,
    snapshot_id,           # Snapshot binding (ensures cache invalidation on advancement)
    agent_id,
    capability_id,         # Which MCP capability was invoked
    query_hash,            # Hash of query parameters (different views of same entity)
)
```

---

## 22. Governance Fail-Closed Policy

> [!IMPORTANT]
> **EXTENDS Section 28 of Amendment 2.**

```python
class GovernedDataAccessRecord(BaseModel):
    # ... existing fields ...
    
    # Governance failure policy (NEW)
    governance_class: Literal[
        "CRITICAL_EVIDENCE",        # Fail-closed: retrieval fails if audit fails
        "STANDARD_EVIDENCE",        # Degrade with warning: proceed but flag
        "OPERATIONAL_TELEMETRY",    # Best-effort: proceed regardless
    ]

def enforce_governance(
    access: GovernedDataAccessRecord,
    audit_success: bool
) -> bool:
    """Returns True if the retrieved data may be used."""
    if audit_success:
        return True
    
    if access.governance_class == "CRITICAL_EVIDENCE":
        return False  # Data cannot be used without audit trail
    
    if access.governance_class == "STANDARD_EVIDENCE":
        access.audit_degraded = True
        return True  # Data can be used but flagged
    
    return True  # Telemetry: always proceed
```

---

## 23. Terminal State Guards

> [!IMPORTANT]
> **EXTENDS Section 22 of Amendment 2.**

```python
TERMINAL_STATES = {"CANCELLED", "CLOSED", "EXPIRED"}
TERMINAL_EVENT_TYPES = {"SESSION_CANCELLED", "SESSION_CLOSED", "SESSION_EXPIRED"}

def handle_incoming_event(
    event: DeliberationEvent,
    session: DeliberationSessionView
) -> EventHandlingResult:
    """Terminal state guard prevents cancelled sessions from resurrecting."""
    
    if session.status in TERMINAL_STATES:
        if event.event_type not in TERMINAL_EVENT_TYPES:
            return EventHandlingResult(
                accepted=False,
                reason=f"Session {session.session_id} is in terminal state "
                       f"{session.status}; rejecting late event {event.event_type}",
            )
    
    return EventHandlingResult(accepted=True)
```

---

## 24. Replanning Context

> [!IMPORTANT]
> **EXTENDS Section 23 of Amendment 2.**

```python
class ReplanningContext(BaseModel):
    """Context for a replanning decision session triggered by execution failure."""
    
    original_decision_id: str
    original_session_id: str
    execution_outcome: ExecutionOutcome
    
    # Post-execution state (CRITICAL: must reflect partial execution)
    post_execution_snapshot: DecisionSnapshot
    
    # Causal chain
    causation_event_id: str                  # The execution failure event
    
    # Inheritance
    inherited_hard_constraints: list[HardConstraint]
    excluded_action_ids: list[str]           # Actions that already failed
    excluded_action_types: list[str]         # Action types to avoid
    
    # Context for agents
    what_was_decided: str                    # Summary of original decision
    what_succeeded: list[str]               # Actions that were applied
    what_failed: list[FailedAction]         # Actions that failed and why
    current_state_summary: str              # State after partial execution
```

---

## 25. Outcome Observation Schema

> [!WARNING]
> **REPLACES `actual_outcome: Optional[dict]` in Section 24 of Amendment 2.**

```python
class OutcomeObservation(BaseModel):
    """Structured observation of actual outcomes for R_i calibration.
    Replaces the untyped dict."""
    
    observation_id: str
    decision_id: str
    
    # Measurement window
    observation_window_start: datetime
    observation_window_end: datetime
    
    # Actual metrics (same dimensions as DecisionObjective)
    actual_cost_delta_usd: Optional[float]
    actual_service_level_delta: Optional[float]
    actual_lead_time_delta_days: Optional[float]
    actual_risk_realized: Optional[bool]
    actual_inventory_impact_dos: Optional[float]
    actual_carbon_delta_kg: Optional[float]
    actual_cash_impact_usd: Optional[float]
    
    # Data provenance
    data_source: str
    observed_at: datetime
    observation_snapshot_version: int
    
    # Quality
    observation_completeness: float        # Fraction of metrics available
    observation_confidence: float          # Reliability of measurement
    
    # Comparison
    predicted_vs_actual_deviation: Optional[dict]  # Per-dimension deviation
```

---

## 26. Claim-Criticality Failure Responses

> [!IMPORTANT]
> **EXTENDS Section 21 of Amendment 2.** Failure response depends on claim criticality.

```python
class ClaimCriticality(str, Enum):
    CRITICAL = "CRITICAL"           # Removing this fact would change the decision
    IMPORTANT = "IMPORTANT"         # Affects decision quality but not binary outcome
    SUPPLEMENTARY = "SUPPLEMENTARY" # Adds context but not decision-critical

# Extended failure response map
def determine_failure_response(
    failure: FailureType,
    criticality: ClaimCriticality,
    policy: DecisionPolicy
) -> FailureResponse:
    
    if criticality == ClaimCriticality.CRITICAL:
        if failure in {FailureType.RETRIEVAL_FAILURE, FailureType.RETRIEVAL_STALE}:
            return FailureResponse.HITL_ESCALATION
        if failure == FailureType.AGENT_TIMEOUT:
            if policy.ml_fallback_validated:
                return FailureResponse.ML_FALLBACK_WITH_ELEVATED_UNCERTAINTY
            return FailureResponse.HITL_ESCALATION
    
    if criticality == ClaimCriticality.IMPORTANT:
        if failure == FailureType.RETRIEVAL_FAILURE:
            return FailureResponse.RETRY_THEN_DEGRADE
        if failure == FailureType.AGENT_TIMEOUT:
            return FailureResponse.ML_FALLBACK_WITH_FLAG
    
    # SUPPLEMENTARY
    return FailureResponse.STANDARD_FALLBACK
```

---

## 27. Policy and Profile Integrity

> [!IMPORTANT]
> **EXTENDS Section 13 of Amendment 2.**

```python
class DecisionPolicy(BaseModel):
    # ... existing fields ...
    
    # Integrity (NEW)
    policy_hash: str             # SHA-256 of serialized policy content
    profile_hash: str            # SHA-256 of complete profile
    computed_at: datetime        # When the hash was computed
    
    def verify_integrity(self) -> bool:
        return self.policy_hash == compute_hash(self.serialize())
```

The DecisionRecord binds `policy_hash` and `profile_hash`, not just `policy_version`. This ensures that two deployments claiming the same version with different contents are detectable.

---

## 28. Replay Manifest Retrieval Artifacts

> [!IMPORTANT]
> **EXTENDS Section 25 of Amendment 2.**

```python
class DecisionReplayManifest(BaseModel):
    # ... existing fields from Amendment 2 ...
    
    # Retrieval artifacts (NEW)
    retrieval_artifacts: list[RetrievalArtifactRef]
    tool_invocation_log_ref: str          # Reference to stored tool invocation log
    
    # Replay fidelity (REFINED)
    replay_type: Literal[
        "TRACE",          # Replay recorded events and tool responses
        "LOGICAL",        # Rerun decision algorithm with recorded inputs
        "MODEL",          # Rerun model inference (requires same model environment)
        "EXACT_SYSTEM",   # Full deterministic replay (requires controlled environment)
    ]
    
    exact_replay_requirements: Optional[ExactReplayRequirements]

class RetrievalArtifactRef(BaseModel):
    retrieval_id: str
    agent_id: str
    capability_id: str
    query_hash: str
    result_hash: str
    stored_result_ref: str             # Reference to stored retrieval result

class ExactReplayRequirements(BaseModel):
    """Documents what is needed for exact system replay."""
    requires_same_model_weights: bool = True
    requires_same_inference_engine: bool = True
    requires_same_quantization: bool = True
    requires_frozen_tool_responses: bool = True
    notes: list[str]
```

---

## 29. Historical Freshness Computation

> [!WARNING]
> **CORRECTS the implicit assumption in Amendment 2 that freshness is relative to wall-clock time.**

All freshness computations throughout the architecture use `observation_cutoff` as the reference point:

```python
def compute_freshness(data_as_of: datetime, snapshot: DecisionSnapshot) -> float:
    """Freshness is ALWAYS relative to the decision's observation boundary."""
    age = snapshot.observation_cutoff - data_as_of
    max_age = timedelta(minutes=snapshot.max_fact_age_minutes)
    if age <= timedelta(0):
        return 1.0
    if age >= max_age:
        return 0.0
    return 1.0 - (age / max_age)
```

This enables:
- Live operational decisions: `observation_cutoff = now`
- Historical scenario replay: `observation_cutoff = scenario_timestamp`
- D10 evaluation: facts from 2026-01-01 are fresh when the scenario is set at 2026-01-01

---

## 30. Simulation Materiality

> [!WARNING]
> **REPLACES the `simulation_trigger_threshold_usd` in Amendment 2's SimulationPolicy.** Twin triggering is now multi-dimensional.

```python
class SimulationPolicy(BaseModel):
    # ... existing fields ...
    
    # REMOVED: simulation_trigger_threshold_usd (too narrow)
    
    # NEW: Multi-dimensional materiality thresholds
    materiality_thresholds: SimulationMaterialityThresholds

class SimulationMaterialityThresholds(BaseModel):
    """Thresholds for determining Twin simulation requirement level."""
    
    # REQUIRED thresholds (exceeding ANY triggers TwinRequired)
    twin_required_cost_usd: float = 200000.0
    twin_required_cascade_potential: float = 0.70
    twin_required_novelty: float = 0.80
    
    # RECOMMENDED thresholds (exceeding ANY triggers TwinRecommended)
    twin_recommended_cost_usd: float = 10000.0
    twin_recommended_service_impact: float = 0.15
    twin_recommended_risk: float = 0.50
    
    # Below all thresholds: TwinAdvisory
```

---

## 31. Concurrent Session Interference

> [!IMPORTANT]
> **NEW SECTION.** Addresses what happens when overlapping disruption events create concurrent decision sessions affecting the same entities.

### 31.1 Overlap Detection

```python
class SessionOverlapDetector:
    """Detects when two concurrent decision sessions affect overlapping entities."""
    
    def detect_overlap(
        self,
        new_session: DecisionSession,
        active_sessions: list[DecisionSession]
    ) -> list[SessionOverlap]:
        overlaps = []
        
        for active in active_sessions:
            shared_entities = (
                set(new_session.affected_entity_ids) &
                set(active.affected_entity_ids)
            )
            
            if shared_entities:
                overlaps.append(SessionOverlap(
                    session_a=new_session.session_id,
                    session_b=active.session_id,
                    shared_entities=list(shared_entities),
                    severity=classify_overlap_severity(shared_entities),
                ))
        
        return overlaps
```

### 31.2 Overlap Resolution

```
OVERLAP DETECTED:
    |
    +-- severity == LOW (shared entities are peripheral):
    |       -> Log overlap. Proceed independently.
    |       -> Both sessions get a cross-reference flag.
    |
    +-- severity == MODERATE (shared entities are relevant but not central):
    |       -> Proceed independently.
    |       -> Evidence sufficiency gate receives overlap warning.
    |       -> CD2F receives overlap flag (applies uncertainty premium).
    |
    +-- severity == HIGH (shared entities are central to both):
    |       -> OPTION A: Serialize (hold new session until active completes)
    |       -> OPTION B: Merge into compound session
    |       -> OPTION C: Escalate to HITL
    |       -> Default: OPTION A unless SLA prohibits waiting
```

---

## 32. Complete B0-B7 Ablation Ladder

> [!WARNING]
> **REPLACES the incomplete baseline references in Section 31 of Amendment 2.**

| Baseline | Configuration | Components | What It Tests |
| :--- | :--- | :--- | :--- |
| **B0** | Deterministic rule heuristic | Hard-coded if-then-else for supplier delay. No ML, no LLM, no agents, no Twin. Rules frozen before D3. | Is any intelligence better than deterministic rules? |
| **B1** | Single generalist agent | One LLM+ML agent covering all domains. No specialization. Direct proposal to minimal CD2F (feasibility only). No cross-examination. No Twin. | Does ML+LLM reasoning add value over rules? |
| **B2** | Six independent specialists | All six agents independently assess. Each produces a proposal. No cross-examination. No Deliberation Table interaction. Proposals directly to CD2F (feasibility + objective score). No Twin. | Does domain specialization improve quality? |
| **B3** | Specialists + cross-examination | B2 + Deliberation Table + cross-examination protocol + independence enforcement. Evidence sufficiency gate active. No Twin. CD2F with full objective function. | Does structured deliberation improve over independent assessment? |
| **B4** | B3 + evidence sufficiency gate | B3 with evidence sufficiency gate actively enforced. Insufficient evidence triggers HITL instead of proceeding. No Twin. Tests whether gating prevents bad automated decisions. | Does evidence gating reduce error rate? |
| **B5** | B4 + Twin simulation (naive scoring) | B4 + Twin counterfactual evaluation. CD2F uses simulation results but with simplified scoring (no Pareto analysis, no uncertainty adjustment). | Does counterfactual simulation add value? |
| **B6** | B5 + full CD2F | B5 + deterministic objective function with proper Pareto analysis, uncertainty adjustment, policy-fixed normalization. Full candidate normalization pipeline. | Does formal arbitration beat simplified scoring? |
| **B7** | Full system | B6 + all governance: R_i lifecycle, execution authorization, DecisionRecord, replay manifest, failure taxonomy, cancellation propagation, priority admission control. | Full system with all governance layers. |

### B0 Definition (Frozen Before D3)

```python
class B0_RuleBasedHeuristic:
    """Baseline B0: deterministic rule heuristic for supplier delay.
    This definition is FROZEN before D3 experiments begin.
    No modification is permitted after freeze date."""
    
    FREEZE_DATE = "2026-10-15"  # Must be frozen before D3 coding starts
    VERSION = "1.0.0"
    
    def decide(self, disruption: SupplierDelayEvent) -> str:
        """Pure rule-based decision. No ML, no LLM."""
        
        if disruption.delay_days > 14:
            if disruption.alternate_suppliers_available > 0:
                return "switch_supplier"
            else:
                return "expedite_purchase_order"
        
        elif disruption.delay_days > 7:
            if disruption.current_inventory_dos > 10:
                return "do_nothing"
            else:
                return "expedite_purchase_order"
        
        else:  # delay <= 7 days
            return "do_nothing"
```

---

## 33. Corrected Evaluation Protocol

> [!IMPORTANT]
> **EXTENDS Section 31 of Amendment 2.** Replaces the overly prescriptive statistical methodology with a distribution-appropriate protocol.

### 33.1 Statistical Methodology

```yaml
evaluation:
  statistical_protocol:
    # Primary test: non-parametric, assumption-free
    primary_test: paired_permutation_test
    permutations: 10000
    
    # Secondary test: when data is at least ordinal
    secondary_test: wilcoxon_signed_rank
    
    # Effect size: non-parametric
    effect_size_metric: cliffs_delta
    effect_size_thresholds:
      negligible: 0.147
      small: 0.33
      medium: 0.474
      large: 0.70
    
    # Confidence intervals
    confidence_level: 0.95
    ci_method: bootstrap
    bootstrap_samples: 5000
    
    # Multiple comparison correction (for pairwise ablation)
    correction_method: holm_bonferroni
    
    # Significance
    alpha: 0.05
    
    # Minimum sample size per comparison
    min_scenarios_per_test: 30
```

### 33.2 Corrected Calibration Metrics

```yaml
calibration:
  # PRIMARY: Expected Calibration Error
  primary_metric: expected_calibration_error
  ece_bins: 10
  ece_target: 0.10              # ECE <= 0.10
  
  # SECONDARY: Brier Score
  secondary_metric: brier_score
  brier_target: 0.15            # Brier <= 0.15
  
  # VISUALIZATION
  reliability_diagram: true
  calibration_slope_target: [0.85, 1.15]  # Slope should be near 1.0
  calibration_intercept_target: [-0.05, 0.05]  # Intercept should be near 0.0
```

### 33.3 Anti-Overfitting Protocol

```yaml
anti_overfitting:
  # Scenario split
  train_eval_split: 80_20
  split_method: stratified_by_disruption_type
  
  # Twin independence
  twin_calibration_data: separate_from_evaluation_data
  twin_evaluation_scenarios: held_out
  
  # Perturbation tests
  parameter_perturbation:
    range: 10%
    dimensions: [cost_model, lead_time_model, demand_model]
  
  # Distribution shift
  distribution_shift:
    method: test_on_unseen_disruption_combinations
    minimum_shift_scenarios: 10
  
  # Policy sensitivity
  policy_sensitivity:
    vary: [objective_weights, evidence_thresholds, candidate_budgets]
    method: one_at_a_time_perturbation
    range: 20%
  
  # Candidate pruning ablation
  pruning_ablation:
    compare: [no_pruning, safe_pruning, aggressive_pruning]
    measure: decision_quality_change
  
  # Oracle independence
  hindsight_oracle:
    method: exhaustive_search_with_independent_simulator
    independence: oracle_does_not_share_twin_calibration_data
```

---

## 34. Freeze Declaration

> [!IMPORTANT]
> **NEW SECTION.** Explicitly declares which architectural decisions are frozen and which remain tunable.

### Frozen (No Further Conceptual Redesign)

```
- Six specialist agents + Coordinator
- Deliberation Table as cognitive workspace
- Event-sourced deliberation state
- MCP-governed retrieval with two-class model
- A2A task lifecycle protocol
- Kafka as event backbone (via transactional outbox)
- PostgreSQL as operational System of Record
- Neo4j as topology projection (derived, not dual SoR)
- pgvector as semantic precedent/evidence memory
- Twin as isolated counterfactual evaluator (Layer 3 only)
- CD2F as deterministic arbitration over materialized DecisionContext
- DecisionPolicy as centralized policy authority (profile-driven)
- Separate decision approval and execution authorization
- DecisionRecord + ReplayManifest as durable business artifacts
- Ten Architectural Invariants
- Canonical D3-D10 numbering
- Six cognitive stages (KNOW -> UNDERSTAND -> DELIBERATE -> EXPLORE -> DECIDE -> EXPLAIN)
- LangGraph orchestration kernel
- DomainOwnershipPolicy enforcement
- Typed ActionIntent schemas
- DeterministicImpactEvaluator
- ClaimTypeRegistry / ActionTypeRegistry
```

### Tunable (Profile Defaults, Not Frozen Architecture)

```
- Objective weights and normalization reference scales
- Evidence sufficiency thresholds
- R_i floor/ceiling and influence status thresholds
- Simulation materiality thresholds
- Candidate budget limits
- Cross-examination round limits
- Pareto ambiguity threshold
- Priority worker allocations
- MCP latency targets
- Twin simulation horizons
- Preemption policy mode
- Statistical test methodology (adapt to data distribution)
```

---

## 35. Corrected Unified Architecture Diagram

> [!WARNING]
> **REPLACES Section 30 of Amendment 2.** Incorporates Amendment 3 corrections: ActionIntent/Impact separation, DeterministicImpactEvaluator, ClaimTypeRegistry, ActionTypeRegistry, TwinRequirement, corrected pruning.

```
+=============================================================================+
|                   SCOF V2 COGNITIVE DECISION FABRIC                        |
|         (D3 through D10 -- Architecture Refinement Revision)               |
+=============================================================================+
|                                                                             |
|  TEN ARCHITECTURAL INVARIANTS (Frozen -- see Amendment 2 Section 1,        |
|  with wording corrections from Amendment 3 Section 1)                      |
|                                                                             |
|  +--[CANONICAL REGISTRIES]-----------------------------------------------+ |
|  | ClaimTypeRegistry | ActionTypeRegistry | ActionDefinitions             | |
|  | (Single source of truth for all agent contracts and action schemas)    | |
|  +-----------------------------------------------------------------------+ |
|                                                                             |
|  +--[D9: OBSERVABILITY, EXPLAINABILITY & DESKTOP CONSOLE]----------------+ |
|  | Tauri v2 | Decision Trace | HITL Escalation | What-If Lab              | |
|  | Evidence Visualization | Trade-off Explanations | DecisionRecord       | |
|  | OutcomeObservation (structured, not dict)                              | |
|  +-----------------------------------------------------------------------+ |
|       |                    ^                                                |
|  +--[D8: EVENT & RUNTIME BACKBONE (Kafka + Outbox)]---------------------+ |
|  | FastAPI | WebSocket | Transactional Outbox -> Kafka Topics            | |
|  | SCOFEvent Contract | Consumer Idempotency | Aggregate Versioning      | |
|  | Terminal State Guards | Preemption Policy                             | |
|  +-----------------------------------------------------------------------+ |
|       |                    ^                    ^                           |
|  +--[DECISION POLICY LAYER]---------+  +--[D10: EVALUATION]---------+    |
|  | DecisionPolicy (from profile)     |  | B0-B7 Ablation Ladder      |    |
|  | ObjectiveNormalization (fixed     |  | Corrected Statistical      |    |
|  |   reference scales, not           |  |   Protocol                 |    |
|  |   candidate-relative)             |  | ECE/Brier Calibration      |    |
|  | Policy precedence (6 levels,      |  | Anti-Overfitting Suite     |    |
|  |   no hard-coded domain rules)     |  | Policy Sensitivity         |    |
|  | policy_hash + profile_hash        |  | Oracle Independence        |    |
|  +-----------------------------------+  +-----------------------------+    |
|                  |                                                          |
|  +=================================================================+      |
|  |        LANGGRAPH ORCHESTRATION KERNEL (D6)                     |      |
|  |        + Coordinator (decomposed into services)                |      |
|  |        + Session Overlap Detection                             |      |
|  |                                                                 |      |
|  |  [Ingest] -> [Snapshot + Trigger Binding] -> [RAG T1] ->       |      |
|  |  -> [Route] -> [Bind] ->                                       |      |
|  |  -> [Fan-Out (independent)] -> [Fan-In] ->                     |      |
|  |  -> [Cross-Exam (targeted, bounded)] ->                        |      |
|  |  -> [Evidence Sufficiency Gate (critical fact assessment)] ->   |      |
|  |  -> [Candidate Extraction] ->                                   |      |
|  |  -> [Schema Validation] -> [Entity Validation] ->              |      |
|  |  -> [DETERMINISTIC IMPACT EVALUATION] ->                       |      |
|  |  -> [Hard-Constraint Check] -> [Dedup] ->                      |      |
|  |  -> [Safe Dominance Pruning (deterministic only)] ->           |      |
|  |  -> [UCB Budget Enforcement] ->                                 |      |
|  |  -> [Twin Requirement Classification] ->                        |      |
|  |  -> [Twin Simulation (budgeted, with requirement level)] ->    |      |
|  |  -> [CD2F (Pareto frontier + policy-fixed normalization)] ->   |      |
|  |  -> [Execution Policy Check] -> [Execute/Escalate]            |      |
|  +=================================================================+      |
|       |              |              |              |              |         |
|  +=================================================================+      |
|  |     LANGCHAIN AGENT REASONING LAYER (D3/D4)                   |      |
|  |     + Agent-Internal Tier-2 RAG (MCP-Governed)                |      |
|  |     + DomainOwnershipPolicy enforcement (validated contracts) |      |
|  |     + ActionIntent schemas (NO impact numbers from LLM)       |      |
|  |     + AgentInfluenceStatus (FULL/REDUCED/ADVISORY)            |      |
|  |                                                                 |      |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  | | Demand &          | | Inventory &       | | Procurement &     |     |
|  | | Commerce          | | Asset Mgmt        | | Supplier          |     |
|  | | [validated card]  | | [validated card]  | | [validated card]  |     |
|  | | [ML + Bounded LLM]| | [ML + Bounded LLM]| | [ML + Bounded LLM]|     |
|  | | [two-class RAG]   | | [two-class RAG]   | | [two-class RAG]   |     |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  |                                                                 |      |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  | | Logistics &       | | Financial &       | | Risk &            |     |
|  | | Transport         | | Enterprise Value  | | Resilience        |     |
|  | | [validated card]  | | [validated card]  | | [validated card]  |     |
|  | | [ML + Bounded LLM]| | [ML + Bounded LLM]| | [ML + Bounded LLM]|     |
|  | | [two-class RAG]   | | [two-class RAG]   | | [two-class RAG]   |     |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  |                                                                 |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DELIBERATION TABLE (Event-Sourced Cognitive Workspace)     |      |
|  |     Events: PostgreSQL (append-only, sequence-allocated)       |      |
|  |     Views:  Redis (materialized, snapshot-aware cache keys)    |      |
|  |     Transport: Kafka (via outbox, keyed by session_id)         |      |
|  |     Terminal state guards for cancelled sessions               |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DETERMINISTIC IMPACT EVALUATOR (NEW)                      |      |
|  |     Computes authoritative ActionImpact from ActionIntent      |      |
|  |     Uses only authoritative data sources                       |      |
|  |     LLM numbers NEVER enter this computation                   |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DIGITAL TWIN -- COUNTERFACTUAL EVALUATOR (D7)             |      |
|  |     Requirement: REQUIRED / RECOMMENDED / ADVISORY             |      |
|  |     Failure: REQUIRED+timeout -> HITL (no autonomous CD2F)    |      |
|  |     Produces: SimulationResult + SimulationManifest            |      |
|  |     Authority: ONLY within isolated Layer-3 scenario scope     |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     CD2F EVIDENCE-BASED ARBITRATION ENGINE (D7)               |      |
|  |     Objective: DecisionObjective (from DecisionPolicy)         |      |
|  |     Normalization: Policy-fixed reference scales               |      |
|  |     Pareto: Proper Pareto frontier computation                 |      |
|  |     Math: J(c) = weighted_objective - penalty - uncertainty    |      |
|  |     "Deterministic arbitration over materialized context"      |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     D1 + D2: ENTERPRISE DATA FABRIC (Frozen Baseline)         |      |
|  |     PostgreSQL: System of Record                               |      |
|  |     Neo4j: Topology projection (derived)                       |      |
|  |     pgvector: Semantic precedent memory                        |      |
|  |     Redis: Governed cache (fail-closed for critical evidence)  |      |
|  +=================================================================+      |
|                                                                             |
+=============================================================================+
```

---

## Summary: What This Refinement Revision Changes

| # | Change | Type | Impact |
| :--- | :--- | :--- | :--- |
| 1 | Invariant wording refinements (1, 2, 8) | FIX | Precision, not mechanism change |
| 2 | ClaimTypeRegistry | NEW | Closes agent contract vocabulary |
| 3 | ActionTypeRegistry + missing schemas | NEW | Closes action type vocabulary |
| 4 | Corrected agent ownership contracts | FIX | All consumes_from references valid |
| 5 | ActionIntent/ActionImpact separation | REPLACE | LLM numbers removed from actions |
| 6 | ActionDefinition ownership model | NEW | Clarifies shared action authority |
| 7 | Critical evidence assessment | EXTEND | Prevents avg freshness masking |
| 8 | Post-snapshot evidence resolution | FIX | Resolves Invariant 8 contradiction |
| 9 | Decision snapshot refinements | EXTEND | Consistency, trigger binding, freshness |
| 10 | Safe candidate pruning | REPLACE | Deterministic-only pre-Twin pruning |
| 11 | Policy-fixed normalization | REPLACE | Stable scoring, not candidate-relative |
| 12 | Proper Pareto analysis | REPLACE | Genuine Pareto frontier, not scalar proximity |
| 13 | Twin requirement classification | NEW | REQUIRED/RECOMMENDED/ADVISORY |
| 14 | Corrected policy precedence | FIX | Platform invariants vs domain regulations |
| 15 | Policy deduplication | FIX | Clear CD2F vs ExecutionPolicy boundary |
| 16 | CD2F description refinement | FIX | Deterministic arbitration over context |
| 17 | R_i agent influence status | EXTEND | FULL/REDUCED/ADVISORY graduated status |
| 18 | Decomposed reliability metrics | EXTEND | Causal attribution per dimension |
| 19 | Event sequence allocation | EXTEND | Coordinator as single writer |
| 20 | Aggregate/session sequence relationship | EXTEND | Explicit independence |
| 21 | Hot-path cache key correction | FIX | Includes capability and query hash |
| 22 | Governance fail-closed | EXTEND | Critical evidence requires audit trail |
| 23 | Terminal state guards | EXTEND | Prevents cancelled session resurrection |
| 24 | Replanning context | EXTEND | Post-execution state inheritance |
| 25 | OutcomeObservation schema | REPLACE | Typed outcomes for R_i calibration |
| 26 | Claim-criticality failure responses | EXTEND | Fallback depends on criticality |
| 27 | Policy/profile integrity hashes | EXTEND | Content-addressable policy versioning |
| 28 | Replay manifest retrieval artifacts | EXTEND | Tool response replay for TRACE mode |
| 29 | Historical freshness computation | FIX | Relative to observation_cutoff |
| 30 | Simulation materiality | REPLACE | Multi-dimensional trigger, not USD-only |
| 31 | Concurrent session interference | NEW | Overlap detection and resolution |
| 32 | Complete B0-B7 ablation ladder | NEW | All 8 baselines with exact configurations |
| 33 | Corrected evaluation protocol | REPLACE | ECE, permutation tests, anti-overfitting |
| 34 | Freeze declaration | NEW | Explicit frozen vs tunable classification |
| 35 | Corrected architecture diagram | REPLACE | Incorporates all Amendment 3 changes |

---

> [!IMPORTANT]
> After this refinement revision, the architecture reaches implementation-contract readiness. The contract-level defects identified by the third-pass review are resolved. The vocabulary is closed (ClaimTypeRegistry, ActionTypeRegistry). The mathematical model is corrected (policy-fixed normalization, proper Pareto, safe pruning). The state semantics are internally consistent (post-snapshot rejection, historical freshness). The evaluation protocol is research-grade (ECE calibration, permutation tests, complete ablation ladder). The architecture is ready for D3 implementation.
