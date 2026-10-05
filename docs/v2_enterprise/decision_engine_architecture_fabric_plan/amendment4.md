# SCOF V2 Architecture Refinement Revision (Amendment 4) -- Contract Freeze Pass

> [!IMPORTANT]
> This is the final contract correction pass. It addresses the Essential contract-level defects identified in the fourth-pass architecture review of Amendment 3. The architectural direction established in Amendments 1, 2, and 3 is CONFIRMED and FROZEN. No conceptual changes are made. This amendment corrects names, resolves contradictions, fixes mathematical errors, and tightens contract precision to implementation-contract readiness.

> [!IMPORTANT]
> Amendment 3 content is NOT modified. This document adds targeted corrections that SUPERSEDE the corresponding sections in Amendment 3 where explicitly noted.

---

## Table of Contents

1. [Canonical EvidenceClass Registry (Resolves Blocker 5: Vocabulary Collision)](#1-canonical-evidenceclass-registry)
2. [Corrected ClaimTypeRegistry Validator (Resolves Blocker: Fail-Open Bug)](#2-corrected-claimtyperegistry-validator)
3. [Unified ActionRegistry (Resolves Blocker 6: ActionType Drift)](#3-unified-actionregistry)
4. [Corrected CandidateAction Schema (Resolves: Duplicated action_type)](#4-corrected-candidateaction-schema)
5. [Corrected ActionIntent Contract Wording (Resolves: "No Numbers" Ambiguity)](#5-corrected-actionintent-contract-wording)
6. [Three-Tier Impact Evaluation Model (Resolves Blocker: Impact Overclaim)](#6-three-tier-impact-evaluation-model)
7. [Corrected Critical Evidence Criticality Model (Resolves Blockers 5, 6, 7)](#7-corrected-critical-evidence-criticality-model)
8. [Corrected Snapshot Consistency Model (Resolves Blocker 2: Invalid LSN Arithmetic)](#8-corrected-snapshot-consistency-model)
9. [Corrected Snapshot Advancement Policy (Resolves: Partial Restart Invariant Violation)](#9-corrected-snapshot-advancement-policy)
10. [Corrected Freshness Computation (Resolves: WALL_CLOCK Contradiction and Post-Snapshot Bug)](#10-corrected-freshness-computation)
11. [Direction-Aware Objective Normalization (Resolves Blocker 4: Signed Normalization)](#11-direction-aware-objective-normalization)
12. [Renamed Candidate Budget Selection (Resolves Blocker 3: "Safe Pruning" Overclaim)](#12-renamed-candidate-budget-selection)
13. [Unified Twin Simulation Materiality (Resolves Blocker 1: Twin Policy Naming Contradiction)](#13-unified-twin-simulation-materiality)
14. [Corrected CD2F Pipeline Wording (Resolves: ExecutionPolicy vs Execution Authorization)](#14-corrected-cd2f-pipeline-wording)
15. [Database Constraints for Event Sequencing (Resolves: Missing Enforcement)](#15-database-constraints-for-event-sequencing)
16. [Canonical Session State Machine (Resolves: Terminal State Transition Matrix)](#16-canonical-session-state-machine)
17. [Corrected Policy Hash Computation (Resolves Blocker 8: Self-Reference)](#17-corrected-policy-hash-computation)
18. [Corrected B0-B7 Ablation Ladder (Resolves Blocker 12: B3/B4 Overlap)](#18-corrected-b0-b7-ablation-ladder)
19. [Corrected Statistical Protocol Wording (Resolves: Minor Wording Defects)](#19-corrected-statistical-protocol-wording)
20. [Corrected ActionDefinition Schema (Resolves: execution_capability_id Nullability)](#20-corrected-actiondefinition-schema)
21. [Final State Revalidation Before Execution (Resolves: Stale Authorization Risk)](#21-final-state-revalidation-before-execution)
22. [Bounded Replay Exactness (Resolves Blocker 9: Replay Overclaim)](#22-bounded-replay-exactness)
23. [Corrected Pareto Confidence Labels (Resolves: PARETO_DOMINANT Misnomer)](#23-corrected-pareto-confidence-labels)
24. [Saturation Policy in Objective Normalization (Resolves: Reference Scale Saturation)](#24-saturation-policy-in-objective-normalization)
25. [Corrected Unified Architecture Diagram (Incorporates All Amendment 4 Corrections)](#25-corrected-unified-architecture-diagram)
26. [Corrected Candidate Normalization Pipeline (Incorporates All Amendment 4 Corrections)](#26-corrected-candidate-normalization-pipeline)
27. [Improvement and Future Enhancement Backlog (NOT in V2 Scope)](#27-improvement-and-future-enhancement-backlog)
28. [Contract Freeze Declaration](#28-contract-freeze-declaration)

---

## 1. Canonical EvidenceClass Registry

> [!WARNING]
> **RESOLVES vocabulary collision identified in Amendment 3 Section 7.** The critical-fact profiles used `claim_type: current_state` and `claim_type: topological`, which are NOT entries in the `ClaimTypeRegistry`. These represent a different concept: the epistemic class of evidence. This section separates them into an independent vocabulary.

### 1.1 Problem Statement

Amendment 3 Section 7 uses:
```yaml
- claim_type: current_state
- claim_type: topological
- claim_type: forecast
```

These are NOT registered claim types. `supplier_operational_assessment` is a **claim type** (what the agent proposes). `current_state` is an **evidence class** (what kind of knowledge backs the claim). These are orthogonal dimensions that were conflated under the same field name.

### 1.2 EvidenceClass Registry

```python
class EvidenceClass(str, Enum):
    """Canonical classification of evidence by epistemic nature.
    
    This is ORTHOGONAL to ClaimTypeRegistry. A single claim (e.g., 
    supplier_operational_assessment) may be backed by evidence of 
    multiple classes (current_state, historical, topological).
    
    This registry is used in:
        - Critical-fact profiles (which evidence classes are required)
        - Evidence sufficiency assessment (coverage per class)
        - Evidence quality scoring (freshness baselines differ by class)
    """
    
    # ---- Observed State (Direct Measurement) ----
    CURRENT_STATE = "current_state"
    """Evidence derived from direct observation of current entity state.
    Examples: current inventory position, live carrier capacity,
    supplier operational status as of the snapshot.
    Freshness sensitivity: HIGH (stale current_state is dangerous)."""
    
    # ---- Structural / Topological ----
    TOPOLOGICAL = "topological"
    """Evidence derived from supply chain network structure.
    Examples: alternate supplier availability, route connectivity,
    facility-product-supplier relationships, tier-2 sourcing paths.
    Freshness sensitivity: MODERATE (topology changes slowly but matters)."""
    
    # ---- Predictive / Forecast ----
    FORECAST = "forecast"
    """Evidence derived from predictive models.
    Examples: demand forecast, price trajectory, risk probability,
    lead time distribution estimates.
    Freshness sensitivity: VARIABLE (depends on forecast horizon and model)."""
    
    # ---- Historical / Precedent ----
    HISTORICAL = "historical"
    """Evidence derived from past decisions or outcomes.
    Examples: similar disruption outcomes, historical supplier performance
    under similar conditions, past decision effectiveness.
    Freshness sensitivity: LOW (historical data does not expire)."""
    
    # ---- Regulatory / Contractual ----
    REGULATORY = "regulatory"
    """Evidence derived from regulatory requirements or contract terms.
    Examples: import/export restrictions, contract penalties,
    quality certification requirements, environmental compliance.
    Freshness sensitivity: MODERATE (regulations change periodically)."""
    
    # ---- Financial / Economic ----
    FINANCIAL = "financial"
    """Evidence derived from financial data or economic models.
    Examples: cost models, margin structures, penalty schedules,
    working capital constraints, budget allocations.
    Freshness sensitivity: MODERATE (updates with business cycles)."""
```

### 1.3 Corrected Critical-Fact Profile

The disruption-type critical-fact profiles now use `evidence_class` instead of `claim_type` for the epistemic dimension:

```yaml
# profiles/mvp-electronics/critical_facts.yaml
# SUPERSEDES Amendment 3 Section 7.2

disruption_profiles:
  supplier_delay:
    critical_facts:
      - entity_type: supplier
        evidence_class: current_state           # WAS: claim_type: current_state
        claim_types:                             # NEW: which registered claim types
          - supplier_operational_assessment
          - supplier_capacity_assessment
        required_fields: [status, capacity, lead_time, quality_score]
        min_freshness: 0.80
        criticality_tier: HARD_CRITICAL          # NEW: see Section 7
        
      - entity_type: inventory
        evidence_class: current_state
        claim_types:
          - inventory_position_assessment
          - inventory_viability_assessment
        required_fields: [position, days_of_supply, committed_stock]
        min_freshness: 0.80
        criticality_tier: HARD_CRITICAL
        
      - entity_type: alternate_suppliers
        evidence_class: topological
        claim_types:
          - alternate_sourcing_feasibility
          - supplier_capacity_assessment
        required_fields: [availability, capacity, qualification_status]
        min_freshness: 0.60
        criticality_tier: DEGRADED_CRITICAL       # NEW: important but not absolute blocker
    
  demand_spike:
    critical_facts:
      - entity_type: demand_forecast
        evidence_class: forecast
        claim_types:
          - demand_assessment
        required_fields: [base_forecast, trend, seasonality]
        min_freshness: 0.70
        criticality_tier: HARD_CRITICAL
        
      - entity_type: inventory
        evidence_class: current_state
        claim_types:
          - inventory_position_assessment
        required_fields: [position, pipeline_stock, safety_stock]
        min_freshness: 0.80
        criticality_tier: HARD_CRITICAL
```

### 1.4 Relationship between ClaimType and EvidenceClass

```
ClaimTypeRegistry:
    WHAT the agent asserts (proposition domain)
    Example: supplier_operational_assessment
    Used in: agent ownership contracts, cross-examination targeting

EvidenceClass:
    WHAT KIND of knowledge supports the assertion
    Example: current_state
    Used in: critical-fact profiles, evidence quality assessment

Relationship:
    A single claim (supplier_operational_assessment) may be 
    supported by evidence from multiple classes:
        - current_state  (live operational metrics)
        - historical     (past performance patterns)
        - regulatory     (compliance status)
    
    A single evidence class (current_state) may support
    multiple claim types:
        - supplier_operational_assessment
        - inventory_position_assessment
        - transport_feasibility
```

### 1.5 Validation Rule

```python
def validate_critical_fact_profiles(
    profiles: dict,
    claim_registry: ClaimTypeRegistry,
    evidence_classes: type[EvidenceClass]
) -> list[str]:
    """Validate that critical-fact profiles reference only
    registered claim types and valid evidence classes."""
    
    errors = []
    registered_claims = set(vars(claim_registry).values())
    valid_classes = set(e.value for e in evidence_classes)
    
    for profile_name, profile in profiles.items():
        for fact in profile.get("critical_facts", []):
            # Validate evidence class
            if fact["evidence_class"] not in valid_classes:
                errors.append(
                    f"Profile {profile_name}: evidence_class "
                    f"'{fact['evidence_class']}' not in EvidenceClass enum"
                )
            
            # Validate claim types
            for ct in fact.get("claim_types", []):
                if ct not in registered_claims:
                    errors.append(
                        f"Profile {profile_name}: claim_type "
                        f"'{ct}' not in ClaimTypeRegistry"
                    )
    
    return errors
```

**Enforcement:** If `validate_critical_fact_profiles` returns any errors, the system MUST NOT start. All references must be valid.

---

## 2. Corrected ClaimTypeRegistry Validator

> [!WARNING]
> **SUPERSEDES the `validate_claim_registry` function in Amendment 3 Section 2.2.** Fixes the fail-open bug where a reference to a nonexistent source agent was silently accepted.

### 2.1 Problem Statement

Original code:

```python
source_card = find_agent(agent_cards, source_agent)
if source_card and claim not in source_card.ownership_policy.owned_claim_types:
    errors.append(...)
```

If `source_card` is `None` (agent does not exist), the `if` short-circuits and no error is appended. This silently accepts a reference to a nonexistent agent, which contradicts the document's own enforcement statement: "All contract references must be valid."

### 2.2 Corrected Validator

```python
def validate_claim_registry(agent_cards: list[AgentCard]) -> list[str]:
    """Run at system startup. Validates all agent contracts
    reference only registered claim types and valid source agents.
    
    SUPERSEDES Amendment 3 Section 2.2."""
    
    registered = set(vars(ClaimTypeRegistry).values())
    agent_map = {card.agent_id: card for card in agent_cards}
    errors = []
    
    for card in agent_cards:
        policy = card.ownership_policy
        
        # Validate owned claims
        for claim in policy.owned_claim_types:
            if claim not in registered:
                errors.append(
                    f"{card.agent_id}: owned_claim '{claim}' "
                    f"not in ClaimTypeRegistry"
                )
        
        # Validate consumed claims
        for source_agent, claims in policy.consumes_from.items():
            # CRITICAL FIX: validate source agent exists
            if source_agent not in agent_map:
                errors.append(
                    f"{card.agent_id}: consumes_from references "
                    f"agent '{source_agent}' which does not exist"
                )
                continue  # Skip claim validation for nonexistent agent
            
            source_card = agent_map[source_agent]
            
            for claim in claims:
                if claim not in registered:
                    errors.append(
                        f"{card.agent_id}: consumes '{claim}' from "
                        f"{source_agent} but '{claim}' not in ClaimTypeRegistry"
                    )
                
                # Validate source agent actually owns this claim
                if claim not in source_card.ownership_policy.owned_claim_types:
                    errors.append(
                        f"{card.agent_id}: consumes '{claim}' from "
                        f"{source_agent} but {source_agent} does not own '{claim}'"
                    )
        
        # Validate forbidden claims
        for claim in policy.forbidden_claim_types:
            if claim not in registered:
                errors.append(
                    f"{card.agent_id}: forbidden_claim '{claim}' "
                    f"not in ClaimTypeRegistry"
                )
        
        # Validate forbidden action types (cross-reference)
        for action in policy.forbidden_action_types:
            if action not in ActionRegistry.get_all_action_types():
                errors.append(
                    f"{card.agent_id}: forbidden_action '{action}' "
                    f"not in ActionRegistry"
                )
    
    return errors
```

**Changes from Amendment 3:**
1. Uses `dict` lookup instead of linear search (`agent_map` vs `find_agent`)
2. Explicit `source_agent not in agent_map` check with error message
3. `continue` after nonexistent-agent error to avoid redundant errors
4. Added forbidden_action_types cross-validation against ActionRegistry

---

## 3. Unified ActionRegistry

> [!WARNING]
> **SUPERSEDES Amendment 3 Sections 3.1 and 6.** Merges `ActionTypeRegistry` (enum-like) and `ActionDefinition` (object) into a single `ActionRegistry` that is the single source of truth for all action-related metadata.

### 3.1 Problem Statement

Amendment 3 has three separate action-metadata structures:
1. `ActionTypeRegistry` -- enum of string constants
2. `ActionDefinition` -- object with ownership, execution, and simulation metadata
3. Independent maps in Twin handlers, execution adapters, and policy constraints

These can drift. The registry says an action exists, but the definition says something different, and the Twin handler map might not have an entry.

### 3.2 Unified ActionRegistry

```python
class ActionRegistryEntry(BaseModel):
    """Single canonical definition of an action type.
    ALL action-related metadata lives here. There is no
    separate ActionTypeRegistry or ActionDefinition.
    
    This is the ONLY place action types are defined.
    All system components that reference action types
    (agent contracts, Twin handlers, execution adapters,
    policy constraints) MUST reference entries in this registry."""
    
    # Identity
    action_type: str                        # Canonical string identifier
    display_name: str                       # Human-readable name
    description: str                        # What this action does
    
    # Domain Classification
    primary_domain: str                     # Which domain this action primarily belongs to
    
    # Ownership (from Amendment 3 Section 6)
    primary_owner_agent: str                # Agent with parameter authority
    permitted_proposers: list[str]          # Agents who may propose this action
    parameter_authority: str                # Agent that validates/refines parameters
    
    # Typed Schema Binding
    intent_schema_class: str               # Fully qualified class name of ActionIntent subclass
    
    # Impact Evaluation
    impact_evaluation_tier: Literal[
        "BASELINE_ONLY",                   # Only deterministic baseline impact available
        "BASELINE_AND_PREDICTIVE",         # Baseline + model-based predictive estimate
    ]
    
    # Twin Simulation
    simulatable: bool                       # Can Digital Twin simulate this action?
    twin_handler_id: Optional[str]          # If simulatable, which Twin handler processes it
    
    # Execution
    execution_capability_id: Optional[str]  # Which MCP capability handles execution (None for advisory)
    advisory_only: bool                     # Does this action only flag/recommend?
    
    # Consistency invariants (validated at startup)
    def validate(self) -> list[str]:
        errors = []
        if self.advisory_only and self.execution_capability_id is not None:
            errors.append(
                f"{self.action_type}: advisory_only=True but "
                f"execution_capability_id is not None"
            )
        if not self.advisory_only and self.execution_capability_id is None:
            errors.append(
                f"{self.action_type}: advisory_only=False but "
                f"execution_capability_id is None"
            )
        if self.simulatable and self.twin_handler_id is None:
            errors.append(
                f"{self.action_type}: simulatable=True but "
                f"twin_handler_id is None"
            )
        if not self.simulatable and self.twin_handler_id is not None:
            errors.append(
                f"{self.action_type}: simulatable=False but "
                f"twin_handler_id is not None"
            )
        return errors


class ActionRegistry:
    """Singleton registry of all action types.
    Loaded at system startup. Validated before any agent starts.
    
    SUPERSEDES both ActionTypeRegistry and ActionDefinition
    from Amendment 3 Sections 3.1 and 6."""
    
    _entries: dict[str, ActionRegistryEntry] = {}
    
    @classmethod
    def register(cls, entry: ActionRegistryEntry) -> None:
        if entry.action_type in cls._entries:
            raise ValueError(
                f"Duplicate action type registration: {entry.action_type}"
            )
        cls._entries[entry.action_type] = entry
    
    @classmethod
    def get(cls, action_type: str) -> ActionRegistryEntry:
        if action_type not in cls._entries:
            raise KeyError(
                f"Action type '{action_type}' not registered. "
                f"All action types must be in ActionRegistry."
            )
        return cls._entries[action_type]
    
    @classmethod
    def get_all_action_types(cls) -> set[str]:
        return set(cls._entries.keys())
    
    @classmethod
    def get_permitted_proposers(cls, action_type: str) -> list[str]:
        return cls.get(action_type).permitted_proposers
    
    @classmethod
    def get_simulatable_actions(cls) -> list[str]:
        return [k for k, v in cls._entries.items() if v.simulatable]
    
    @classmethod
    def validate_all(cls) -> list[str]:
        """Validate all entries for internal consistency."""
        errors = []
        for entry in cls._entries.values():
            errors.extend(entry.validate())
        return errors
```

### 3.3 Canonical Action Definitions

```yaml
# All action definitions in one canonical location
# SUPERSEDES Amendment 3 Sections 3.1 and 6 per-action definitions

actions:
  # ---- Logistics Domain ----
  reroute_shipment:
    display_name: "Reroute Shipment"
    description: "Change the carrier, route, or freight mode for a shipment"
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    parameter_authority: logistics_transport
    intent_schema_class: "scof.actions.intents.RerouteShipmentIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: logistics_reroute_handler
    execution_capability_id: shipment_management
    advisory_only: false

  expedite_shipment:
    display_name: "Expedite Shipment"
    description: "Expedite delivery of an existing shipment"
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    parameter_authority: logistics_transport
    intent_schema_class: "scof.actions.intents.ExpediteShipmentIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: logistics_expedite_handler
    execution_capability_id: shipment_management
    advisory_only: false

  change_freight_mode:
    display_name: "Change Freight Mode"
    description: "Switch freight mode for a shipment (road/air/sea/rail/multimodal)"
    primary_domain: logistics_transport
    primary_owner_agent: logistics_transport
    permitted_proposers: [logistics_transport]
    parameter_authority: logistics_transport
    intent_schema_class: "scof.actions.intents.ChangeFreightModeIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: logistics_mode_change_handler
    execution_capability_id: shipment_management
    advisory_only: false

  # ---- Procurement Domain ----
  switch_supplier:
    display_name: "Switch Supplier"
    description: "Transfer a purchase order to a different qualified supplier"
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: "scof.actions.intents.SwitchSupplierIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: procurement_switch_handler
    execution_capability_id: procurement_management
    advisory_only: false

  increase_purchase_order:
    display_name: "Increase Purchase Order"
    description: "Increase quantity on an existing or create a new purchase order"
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: "scof.actions.intents.IncreasePurchaseOrderIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: procurement_increase_handler
    execution_capability_id: procurement_management
    advisory_only: false

  cancel_purchase_order:
    display_name: "Cancel Purchase Order"
    description: "Cancel an existing purchase order"
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: "scof.actions.intents.CancelPurchaseOrderIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: procurement_cancel_handler
    execution_capability_id: procurement_management
    advisory_only: false

  expedite_purchase_order:
    display_name: "Expedite Purchase Order"
    description: "Expedite an existing purchase order with the current supplier"
    primary_domain: procurement_supplier
    primary_owner_agent: procurement_supplier
    permitted_proposers: [procurement_supplier]
    parameter_authority: procurement_supplier
    intent_schema_class: "scof.actions.intents.ExpeditePurchaseOrderIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: procurement_expedite_handler
    execution_capability_id: procurement_management
    advisory_only: false

  # ---- Inventory Domain ----
  reallocate_inventory:
    display_name: "Reallocate Inventory"
    description: "Transfer inventory between facilities or reallocate stock"
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset]
    parameter_authority: inventory_asset
    intent_schema_class: "scof.actions.intents.ReallocateInventoryIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: inventory_reallocation_handler
    execution_capability_id: inventory_management
    advisory_only: false

  adjust_safety_stock:
    display_name: "Adjust Safety Stock"
    description: "Modify safety stock levels for a SKU at a facility"
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset, demand_commerce]
    parameter_authority: inventory_asset
    intent_schema_class: "scof.actions.intents.AdjustSafetyStockIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: inventory_safety_stock_handler
    execution_capability_id: inventory_management
    advisory_only: false

  quarantine_inventory:
    display_name: "Quarantine Inventory"
    description: "Place inventory under quarantine hold"
    primary_domain: inventory_asset
    primary_owner_agent: inventory_asset
    permitted_proposers: [inventory_asset, risk_resilience]
    parameter_authority: inventory_asset
    intent_schema_class: "scof.actions.intents.QuarantineInventoryIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: inventory_quarantine_handler
    execution_capability_id: inventory_management
    advisory_only: false

  # ---- Demand Domain ----
  promotion_adjustment:
    display_name: "Promotion Adjustment"
    description: "Modify promotion schedule in response to disruption"
    primary_domain: demand_commerce
    primary_owner_agent: demand_commerce
    permitted_proposers: [demand_commerce]
    parameter_authority: demand_commerce
    intent_schema_class: "scof.actions.intents.PromotionAdjustmentIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: demand_promotion_handler
    execution_capability_id: demand_management
    advisory_only: false

  demand_signal_override:
    display_name: "Demand Signal Override"
    description: "Override demand forecast for a period"
    primary_domain: demand_commerce
    primary_owner_agent: demand_commerce
    permitted_proposers: [demand_commerce]
    parameter_authority: demand_commerce
    intent_schema_class: "scof.actions.intents.DemandSignalOverrideIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: demand_override_handler
    execution_capability_id: demand_management
    advisory_only: false

  # ---- Risk Domain ----
  risk_mitigation_recommendation:
    display_name: "Risk Mitigation Recommendation"
    description: "Recommend a risk mitigation strategy (advisory only)"
    primary_domain: risk_resilience
    primary_owner_agent: risk_resilience
    permitted_proposers: [risk_resilience]
    parameter_authority: risk_resilience
    intent_schema_class: "scof.actions.intents.RiskMitigationRecommendationIntent"
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    twin_handler_id: null
    execution_capability_id: null
    advisory_only: true

  compliance_hold:
    display_name: "Compliance Hold"
    description: "Place a compliance hold on an entity"
    primary_domain: risk_resilience
    primary_owner_agent: risk_resilience
    permitted_proposers: [risk_resilience]
    parameter_authority: risk_resilience
    intent_schema_class: "scof.actions.intents.ComplianceHoldIntent"
    impact_evaluation_tier: BASELINE_AND_PREDICTIVE
    simulatable: true
    twin_handler_id: risk_compliance_handler
    execution_capability_id: compliance_management
    advisory_only: false

  # ---- Finance Domain ----
  financial_impact_flag:
    display_name: "Financial Impact Flag"
    description: "Flag a decision for financial review (advisory only)"
    primary_domain: financial_enterprise
    primary_owner_agent: financial_enterprise
    permitted_proposers: [financial_enterprise]
    parameter_authority: financial_enterprise
    intent_schema_class: "scof.actions.intents.FinancialImpactFlagIntent"
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    twin_handler_id: null
    execution_capability_id: null
    advisory_only: true

  budget_escalation:
    display_name: "Budget Escalation"
    description: "Recommend budget escalation for a decision (advisory only)"
    primary_domain: financial_enterprise
    primary_owner_agent: financial_enterprise
    permitted_proposers: [financial_enterprise]
    parameter_authority: financial_enterprise
    intent_schema_class: "scof.actions.intents.BudgetEscalationIntent"
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: false
    twin_handler_id: null
    execution_capability_id: null
    advisory_only: true

  # ---- Universal ----
  do_nothing:
    display_name: "Do Nothing (Monitor)"
    description: "Take no action; continue monitoring"
    primary_domain: universal
    primary_owner_agent: coordinator
    permitted_proposers: [coordinator]
    parameter_authority: coordinator
    intent_schema_class: "scof.actions.intents.DoNothingIntent"
    impact_evaluation_tier: BASELINE_ONLY
    simulatable: true
    twin_handler_id: universal_baseline_handler
    execution_capability_id: null
    advisory_only: false
```

### 3.4 Startup Validation

```python
def validate_action_registry_completeness(
    registry: ActionRegistry,
    agent_cards: list[AgentCard],
    twin_handlers: dict[str, TwinHandler],
    execution_capabilities: dict[str, ExecutionCapability]
) -> list[str]:
    """Full cross-registry validation at startup."""
    
    errors = registry.validate_all()
    
    for entry in registry._entries.values():
        # Validate Twin handler binding
        if entry.simulatable and entry.twin_handler_id not in twin_handlers:
            errors.append(
                f"{entry.action_type}: twin_handler_id "
                f"'{entry.twin_handler_id}' not found in Twin handlers"
            )
        
        # Validate execution capability binding
        if entry.execution_capability_id is not None:
            if entry.execution_capability_id not in execution_capabilities:
                errors.append(
                    f"{entry.action_type}: execution_capability_id "
                    f"'{entry.execution_capability_id}' not found in capabilities"
                )
        
        # Validate owner agent exists
        agent_ids = {card.agent_id for card in agent_cards}
        if entry.primary_owner_agent not in agent_ids and entry.primary_owner_agent != "coordinator":
            errors.append(
                f"{entry.action_type}: primary_owner_agent "
                f"'{entry.primary_owner_agent}' not found in agent cards"
            )
        
        # Validate permitted proposers exist
        for proposer in entry.permitted_proposers:
            if proposer not in agent_ids and proposer != "coordinator":
                errors.append(
                    f"{entry.action_type}: permitted_proposer "
                    f"'{proposer}' not found in agent cards"
                )
    
    return errors
```

**Enforcement:** If validation returns any errors, the system MUST NOT start.

---

## 4. Corrected CandidateAction Schema

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 5.1.** Removes the duplicated `action_type` field.

### 4.1 Problem Statement

Amendment 3's `CandidateAction` has both `action_type: str` (top-level) and `intent.action_type` (within the intent schema). These can disagree:

```python
CandidateAction(
    action_type="switch_supplier",              # Top-level
    intent=RerouteShipmentIntent(               # Intent says different type
        action_type="reroute_shipment", ...
    )
)
```

This must be structurally impossible.

### 4.2 Corrected Schema

```python
class CandidateAction(BaseModel):
    """What the agent PROPOSES to do.
    The agent specifies INTENT (what to do).
    The ImpactEvaluationService computes IMPACT (what it costs/gains).
    LLM-provided numerical impact estimates NEVER enter CD2F scoring.
    
    SUPERSEDES Amendment 3 Section 5.1."""
    
    action_id: str
    # REMOVED: action_type -- derived from intent to prevent inconsistency
    intent: ActionIntent                   # Agent-provided: WHAT to do
    impact: Optional[ActionImpactEnvelope] # System-computed: WHAT it costs
    impact_computed: bool = False           # True after ImpactEvaluationService runs
    supporting_claims: list[str]           # Claim IDs supporting this action
    evidence: list[EvidenceItem]           # Evidence backing the intent
    proposer_agent_id: str                 # Which agent proposed this
    
    @property
    def action_type(self) -> str:
        """Action type is ALWAYS derived from the intent.
        No independent action_type field exists."""
        return self.intent.action_type
    
    def validate_against_registry(self) -> list[str]:
        """Validate this candidate against the ActionRegistry."""
        errors = []
        
        try:
            entry = ActionRegistry.get(self.action_type)
        except KeyError:
            errors.append(
                f"Candidate {self.action_id}: action_type "
                f"'{self.action_type}' not in ActionRegistry"
            )
            return errors
        
        # Validate proposer is permitted
        if self.proposer_agent_id not in entry.permitted_proposers:
            errors.append(
                f"Candidate {self.action_id}: agent "
                f"'{self.proposer_agent_id}' is not a permitted proposer "
                f"for action type '{self.action_type}'"
            )
        
        return errors
```

### 4.3 Database/Indexing Consideration

If `action_type` is needed as an indexed column in the database for query performance, it is generated at persistence time from the intent field and stored as a denormalized column:

```python
class CandidateActionRow:
    """Database representation. action_type_denorm is generated,
    not independently supplied."""
    action_id: str
    action_type_denorm: str  # = intent->>'action_type', generated at insert
    intent_json: dict
    # ...
```

This maintains the structural invariant while enabling efficient database queries.

---

## 5. Corrected ActionIntent Contract Wording

> [!IMPORTANT]
> **SUPERSEDES the ActionIntent description in Amendment 3 Section 5.2 header.** The schemas themselves are correct; the prose was misleading.

### 5.1 Original Wording (Amendment 3)

> "Intent schemas contain ONLY structural decision parameters -- identifiers, modes, types. They do NOT contain cost, time, or quantity estimates from the LLM."

### 5.2 Corrected Wording

> ActionIntent schemas contain **structural decision parameters**: identifiers (entity IDs, supplier IDs, route IDs), modes (freight mode, adjustment type), and **decision quantities** (order quantity, target days of supply, override factor). These are the parameters the agent is proposing as the action to take.
>
> ActionIntent schemas do NOT contain **impact estimates**: cost deltas, lead time deltas, service level projections, risk scores, or any values that represent the *consequence* of taking the action. Impact estimates are computed by the ImpactEvaluationService (see Section 6) and the Digital Twin, using authoritative data sources.
>
> The distinction is between *what the agent wants to do* (intent) and *what the system predicts will happen* (impact). Agents specify intent. The system computes impact.

### 5.3 Decision Parameter vs Impact Estimate Examples

```
DECISION PARAMETERS (permitted in ActionIntent):
    quantity: 500                  # How many units to order
    target_days_of_supply: 14.0   # Desired stock level
    override_factor: 1.3          # Demand multiplier
    new_supplier_id: "SUP-042"    # Which supplier to switch to
    freight_mode: "air"           # Which freight mode to use
    adjustment_type: "delay"      # What kind of promotion change

IMPACT ESTIMATES (PROHIBITED in ActionIntent, computed by system):
    incremental_cost_usd: 12400   # Cost consequence of this action
    new_lead_time_days: 8.5       # Time consequence of this action
    service_level_improvement: 0.03  # Service consequence
    risk_delta: -0.15             # Risk consequence
    carbon_delta_kg: 250          # Emission consequence
```

---

## 6. Three-Tier Impact Evaluation Model

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 5.3 (DeterministicImpactEvaluator) and Section 5.4 (Pipeline Integration).** The overclaimed "deterministic" prefix is removed. The impact model is restructured into three epistemic tiers.

### 6.1 Problem Statement

Amendment 3 called the impact evaluator "Deterministic" and its output "authoritative." The review correctly identifies that while some impact dimensions (route cost lookup, contract price, carrier eligibility) are deterministic derivations from authoritative facts, other dimensions (service_level_delta, risk_delta, inventory_health_delta) are model-based predictions that carry inherent uncertainty.

Calling both "deterministic" and "authoritative" conflates two levels of confidence and could lead implementers to trust model predictions as if they were facts.

### 6.2 Three-Tier Impact Architecture

```
TIER 1: BASELINE IMPACT (Authoritative Facts)
    Source: PostgreSQL system-of-record data, rate tables, contract terms
    Nature: Deterministic derivation from authoritative facts
    Examples:
        - Route cost difference (rate_table A vs rate_table B)
        - Contract price delta (contract terms for old vs new supplier)
        - Carrier eligibility (binary: has reefer capability or not)
        - Transit time baseline (published lane transit times)
    Confidence: HIGH (bounded by data freshness within snapshot)
    Used for: Hard constraint pre-check, dominance pruning (SAFE)

TIER 2: PREDICTIVE IMPACT ESTIMATE (Model-Based)
    Source: Validated domain models (demand forecast, risk model, service model)
    Nature: Statistical prediction with quantified uncertainty
    Examples:
        - Expected service level delta (from demand/inventory models)
        - Estimated risk reduction (from risk probability models)
        - Projected inventory health impact (from replenishment models)
        - Estimated carbon impact (from emission models with utilization assumptions)
    Confidence: MEDIUM (model-dependent, carries prediction interval)
    Used for: UCB candidate budgeting, pre-Twin scoring (NOT for dominance pruning)

TIER 3: COUNTERFACTUAL IMPACT (Twin Simulation)
    Source: Digital Twin simulation under specific scenario assumptions
    Nature: Counterfactual projection over simulated time horizon
    Examples:
        - Multi-period cascading impact on service levels
        - Interacting effects of combined actions
        - Dynamic risk propagation through supply network
        - Time-resolved financial impact trajectory
    Confidence: VARIABLE (depends on Twin calibration quality and scenario complexity)
    Used for: Final CD2F arbitration, Pareto frontier computation
```

### 6.3 Restructured Impact Schemas

```python
class BaselineImpact(BaseModel):
    """Tier 1: Impact values derived deterministically from authoritative facts.
    These values are correct given the snapshot data. They do not involve
    prediction, estimation, or modeling uncertainty."""
    
    # Cost dimension (from rate tables, contract terms)
    cost_delta_usd: Optional[float]
    cost_data_sources: list[str]
    
    # Transit/lead time (from published lane data)
    lead_time_delta_days: Optional[float]
    lead_time_data_sources: list[str]
    
    # Eligibility (binary hard constraints)
    hard_constraint_violations: list[str]   # Empty if all constraints satisfied
    
    # Provenance
    evaluated_at: datetime
    snapshot_epoch: int
    computation_method: str = "baseline_fact_derivation"


class PredictiveImpactEstimate(BaseModel):
    """Tier 2: Impact values from validated domain models.
    These are the system's best estimate but carry prediction uncertainty.
    NOT deterministic. NOT authoritative. Carry explicit uncertainty bounds."""
    
    # Service level (from demand/inventory models)
    service_level_delta: Optional[float]
    service_level_confidence_interval: Optional[tuple[float, float]]
    service_level_model_id: Optional[str]
    
    # Risk (from risk probability models)
    risk_delta: Optional[float]
    risk_confidence_interval: Optional[tuple[float, float]]
    risk_model_id: Optional[str]
    
    # Inventory health (from replenishment models)
    inventory_health_delta: Optional[float]
    inventory_health_confidence_interval: Optional[tuple[float, float]]
    inventory_model_id: Optional[str]
    
    # Carbon (from emission models)
    carbon_delta_kg: Optional[float]
    carbon_confidence_interval: Optional[tuple[float, float]]
    emission_model_id: Optional[str]
    
    # Cash flow (from financial models)
    cash_flow_delta_usd: Optional[float]
    cash_flow_confidence_interval: Optional[tuple[float, float]]
    financial_model_id: Optional[str]
    
    # Overall confidence
    overall_prediction_confidence: float
    missing_model_flags: list[str]
    
    # Provenance
    evaluated_at: datetime
    snapshot_epoch: int
    computation_method: str = "model_based_prediction"


class ActionImpactEnvelope(BaseModel):
    """Complete impact assessment for a CandidateAction.
    Contains both tiers with explicit epistemic separation.
    
    SUPERSEDES ActionImpact from Amendment 3."""
    
    action_id: str
    
    # Tier 1: Authoritative facts
    baseline: BaselineImpact
    
    # Tier 2: Model-based predictions (may be partially populated)
    predictive: Optional[PredictiveImpactEstimate]
    
    # Tier 3: Twin simulation results (populated after Twin runs)
    simulation: Optional[SimulationResult]
    
    # Evaluation status
    baseline_computed: bool = False
    predictive_computed: bool = False
    simulation_computed: bool = False
    
    def has_complete_baseline(self) -> bool:
        """Can this action be used in deterministic pruning?"""
        return (
            self.baseline_computed
            and self.baseline.cost_delta_usd is not None
            and self.baseline.lead_time_delta_days is not None
        )
```

### 6.4 Impact Evaluation Service

```python
class ImpactEvaluationService:
    """Computes impact for CandidateActions using authoritative data
    and validated models. NEVER uses LLM-generated numbers.
    
    SUPERSEDES DeterministicImpactEvaluator from Amendment 3.
    The name is changed to avoid overclaiming determinism for
    model-based predictions."""
    
    def evaluate_baseline(
        self,
        action: CandidateAction,
        snapshot: DecisionSnapshot,
    ) -> BaselineImpact:
        """Tier 1: Derive impact from authoritative facts only."""
        
        entry = ActionRegistry.get(action.action_type)
        
        if isinstance(action.intent, RerouteShipmentIntent):
            return self._baseline_reroute(action.intent, snapshot)
        elif isinstance(action.intent, SwitchSupplierIntent):
            return self._baseline_switch_supplier(action.intent, snapshot)
        # ... dispatch for each action type
    
    def evaluate_predictive(
        self,
        action: CandidateAction,
        baseline: BaselineImpact,
        snapshot: DecisionSnapshot,
        models: ModelRegistry,
    ) -> PredictiveImpactEstimate:
        """Tier 2: Use domain models to estimate non-deterministic impact."""
        
        if isinstance(action.intent, RerouteShipmentIntent):
            return self._predict_reroute(action.intent, baseline, snapshot, models)
        # ... dispatch for each action type
    
    def evaluate_full(
        self,
        action: CandidateAction,
        snapshot: DecisionSnapshot,
        models: ModelRegistry,
    ) -> ActionImpactEnvelope:
        """Compute both Tier 1 and Tier 2 impact."""
        
        baseline = self.evaluate_baseline(action, snapshot)
        
        entry = ActionRegistry.get(action.action_type)
        predictive = None
        if entry.impact_evaluation_tier == "BASELINE_AND_PREDICTIVE":
            predictive = self.evaluate_predictive(
                action, baseline, snapshot, models
            )
        
        return ActionImpactEnvelope(
            action_id=action.action_id,
            baseline=baseline,
            predictive=predictive,
            baseline_computed=True,
            predictive_computed=(predictive is not None),
        )
```

### 6.5 Pruning Safety Rules (Updated)

```
DOMINANCE PRUNING (Step 7):
    Uses ONLY Tier 1 (BaselineImpact) values.
    A candidate is dominated only if:
        - Both candidates have has_complete_baseline() == True
        - The dominating candidate is strictly better on ALL dimensions
          WHERE baseline values are available
        - Safety margin policy.dominance_pruning_margin applies
    
    Tier 2 (PredictiveImpactEstimate) values are NEVER used for dominance
    because they carry prediction uncertainty.

UCB BUDGET SELECTION (Step 8):
    Uses BOTH Tier 1 and Tier 2 values.
    UCB(c) = weighted_score(baseline + predictive) + alpha * uncertainty(c)
    where uncertainty includes Tier 2 prediction intervals.
    This is explicitly a heuristic, not a safety proof.

CD2F FINAL SCORING:
    Uses ALL THREE tiers when available.
    Tier 3 (Twin simulation) supersedes Tier 2 for the same dimension.
    If Twin is not available, Tier 2 is used with elevated uncertainty penalty.
    Tier 1 values are always authoritative for their dimensions.
```

---

## 7. Corrected Critical Evidence Criticality Model

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 7 (criticality definition) and verdict logic (Section 7.3).** Resolves: (a) vocabulary collision with `claim_type`, (b) circular criticality definition, (c) marginal sufficiency inconsistency.

### 7.1 Problem Statement (Three Defects)

**Defect A (Vocabulary):** Resolved by Section 1 above (EvidenceClass registry).

**Defect B (Circularity):** "A fact is critical if removing it would change candidate ranking" is circular because ranking does not exist when the evidence gate runs. Criticality must be defined BEFORE ranking.

**Defect C (Inconsistency):** A critical fact can be present (incrementing `critical_facts_present`) but stale (setting `all_critical_facts_sufficient = False`). This creates overlap between `MARGINALLY_SUFFICIENT` and `INSUFFICIENT`.

### 7.2 Tiered Criticality Model

```python
class CriticalityTier(str, Enum):
    """Tiered criticality for evidence items.
    Criticality is defined by the disruption profile BEFORE candidate ranking.
    This is the PRIMARY criticality definition (pre-ranking).
    
    SUPERSEDES the single-tier criticality in Amendment 3 Section 7."""
    
    HARD_CRITICAL = "HARD_CRITICAL"
    """Absolute decision blocker if missing or stale.
    Missing/stale HARD_CRITICAL fact -> NO autonomous decision possible.
    Examples: Current inventory position for a stockout decision,
    supplier operational status for a supplier-switch decision."""
    
    DEGRADED_CRITICAL = "DEGRADED_CRITICAL"
    """Decision can proceed but with elevated uncertainty and reduced autonomy.
    Missing/stale DEGRADED_CRITICAL fact -> decision proceeds at lower
    autonomy tier (never Tier-1 autonomous).
    Examples: Alternate supplier qualification status, demand trend data."""
    
    IMPORTANT = "IMPORTANT"
    """Affects decision quality but does not block the decision.
    Missing/stale IMPORTANT fact -> degraded confidence score.
    Examples: Historical precedent data, cost model details."""
    
    SUPPLEMENTARY = "SUPPLEMENTARY"
    """Adds context but is not decision-critical.
    Missing SUPPLEMENTARY fact -> no blocking effect.
    Examples: Commentary, background context, supplementary analytics."""


class CriticalFactStatus(BaseModel):
    """Status of a single critical fact in the evidence assessment.
    
    SUPERSEDES CriticalFactStatus from Amendment 3."""
    
    fact_id: str
    entity_type: str
    entity_id: str
    evidence_class: str              # From EvidenceClass enum (was: claim_type)
    claim_types: list[str]           # From ClaimTypeRegistry
    criticality_tier: CriticalityTier  # From disruption profile (not computed)
    
    present: bool
    freshness: float
    authority_level: str
    
    # Tier-specific assessment
    meets_minimum_threshold: bool    # Freshness >= tier-specific minimum
    
    insufficiency_reason: Optional[str]
```

### 7.3 Corrected Evidence Sufficiency Assessment

```python
class CriticalEvidenceAssessment(BaseModel):
    """Assessment of evidence criticality with tiered precedence.
    
    SUPERSEDES CriticalEvidenceAssessment from Amendment 3."""
    
    # Per-tier counts
    hard_critical_required: int
    hard_critical_present: int
    hard_critical_sufficient: int         # Present AND meets freshness threshold
    
    degraded_critical_required: int
    degraded_critical_present: int
    degraded_critical_sufficient: int
    
    important_required: int
    important_present: int
    important_sufficient: int
    
    # Worst-case metrics per tier (NOT averages)
    min_hard_critical_freshness: Optional[float]      # None if no hard critical facts
    min_degraded_critical_freshness: Optional[float]
    
    # Detail
    critical_fact_details: list[CriticalFactStatus]
    
    # Verdicts (per tier)
    hard_critical_all_met: bool
    degraded_critical_all_met: bool
    important_all_met: bool
```

### 7.4 Corrected Verdict Logic

```
SUFFICIENT:
    hard_critical_all_met == True
    AND degraded_critical_all_met == True
    AND domain_coverage.coverage_score >= policy.min_domain_coverage
    AND evidence_quality.avg_evidence_freshness >= policy.min_evidence_freshness
    AND consistency.contradiction_severity != "BLOCKING"
    AND evidence_quality.model_validity_score >= 0.50
    
    -> Full autonomy available. Proceed to candidate evaluation.

MARGINALLY_SUFFICIENT:
    hard_critical_all_met == True                      # HARD tier must be fully met
    AND degraded_critical_present >= degraded_critical_required  # Present but may be below threshold
    AND degraded_critical_sufficient < degraded_critical_required  # At least one below preferred threshold
    AND domain_coverage.coverage_score >= 0.60
    AND consistency.contradiction_severity != "BLOCKING"
    
    -> Decision proceeds but with:
       - Autonomy capped at Tier-2 (never fully autonomous)
       - Elevated uncertainty penalty in CD2F
       - HITL notification for degraded evidence

INSUFFICIENT:
    hard_critical_all_met == False                     # ANY hard-critical failure blocks decision
    OR hard_critical_present < hard_critical_required  # Missing hard-critical fact
    OR consistency.contradiction_severity == "BLOCKING"
    
    -> NO autonomous decision.
    -> HITL escalation mandatory.
    -> Record: which hard-critical facts are missing/stale.
```

**Key invariant:** The verdict logic has strict precedence. `HARD_CRITICAL` failures always produce `INSUFFICIENT` regardless of other conditions. There is no overlap between `MARGINALLY_SUFFICIENT` and `INSUFFICIENT` because `MARGINALLY_SUFFICIENT` requires `hard_critical_all_met == True` while `INSUFFICIENT` requires `hard_critical_all_met == False`.

### 7.5 Sensitivity-Discovered Criticality (Secondary, Post-Decision)

```python
class CriticalitySensitivityReport(BaseModel):
    """Post-decision analysis of which facts were most decision-sensitive.
    This is the SECONDARY criticality definition (post-ranking).
    Used to refine disruption profiles for future decisions, NOT to
    retroactively change the current decision's evidence verdict.
    
    Resolves the circularity: profile-defined criticality (primary)
    gates the decision. Sensitivity analysis (secondary) improves
    future profiles."""
    
    decision_id: str
    
    # For each fact, how much would the decision change if this fact changed?
    sensitivity_by_fact: list[FactSensitivity]
    
    # Facts that were not marked as critical but turned out to be decision-sensitive
    escalation_candidates: list[CriticalityEscalation]

class FactSensitivity(BaseModel):
    fact_id: str
    entity_type: str
    evidence_class: str
    current_criticality: CriticalityTier
    decision_sensitivity: float         # 0 = no effect, 1 = completely changes decision
    
class CriticalityEscalation(BaseModel):
    """A fact that was IMPORTANT or SUPPLEMENTARY but had high sensitivity.
    Candidate for promotion to a higher criticality tier in the profile."""
    fact_id: str
    current_tier: CriticalityTier
    suggested_tier: CriticalityTier
    sensitivity_score: float
    rationale: str
```

---

## 8. Corrected Snapshot Consistency Model

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 9.1 (consistency assessment fields).** Replaces invalid LSN arithmetic with a common epoch-based consistency model.

### 8.1 Problem Statement

Amendment 3 computes `neo4j_lag_behind_pg = enterprise_state_version - neo4j_source_lsn`. If `enterprise_state_version` is a business-level integer (e.g., `42`) and `neo4j_source_lsn` is a PostgreSQL WAL position (e.g., `0/7A31BC0`), this arithmetic is meaningless. They are different coordinate systems.

### 8.2 Common Snapshot Epoch Model

```python
class DataProjectionStatus(BaseModel):
    """Status of a data projection relative to the common snapshot epoch.
    
    SUPERSEDES the per-subsystem LSN fields in Amendment 3 Section 9.1."""
    
    projection_name: str                    # "neo4j", "pgvector", "redis_cache"
    projection_epoch: int                   # Last snapshot_epoch this projection has materialized
    last_materialized_at: datetime          # Wall-clock time of last materialization
    native_position: Optional[str]          # Native position indicator (WAL LSN, offset, etc.)
                                            # For operational monitoring only, NOT for consistency math

class DecisionSnapshot(BaseModel):
    """SUPERSEDES the consistency fields in Amendment 3 Section 9.1.
    All other fields from Amendment 3 Section 9.1 are RETAINED."""
    
    # ... all existing fields from Amendment 3 (retained unchanged) ...
    
    # REPLACED: Consistency assessment (new epoch-based model)
    snapshot_epoch: int                     # Monotonically increasing common coordinate
                                           # Allocated atomically by the Coordinator
    
    # Per-projection status
    projections: list[DataProjectionStatus]
    
    # Computed consistency class (uses epoch comparison, not LSN arithmetic)
    consistency_class: Literal[
        "FULLY_CONSISTENT",                # All projections at snapshot_epoch
        "ACCEPTABLE_LAG",                  # Max lag within policy threshold
        "STALE_PROJECTION",                # One or more projections too far behind
    ]
    
    # REMOVED: neo4j_source_lsn (was heterogeneous with enterprise_state_version)
    # REMOVED: pgvector_source_lsn (was heterogeneous with enterprise_state_version)
    # REMOVED: neo4j_lag_behind_pg (was invalid arithmetic)
    # REMOVED: pgvector_lag_behind_pg (was invalid arithmetic)
    
    # RETAINED from Amendment 3:
    trigger_event_id: str
    trigger_event_timestamp: datetime
    trigger_event_sequence: Optional[int]
    freshness_reference: Literal["OBSERVATION_CUTOFF"] = "OBSERVATION_CUTOFF"
    # NOTE: "WALL_CLOCK" option REMOVED (see Section 10)


def compute_consistency_class(
    snapshot: DecisionSnapshot,
    policy: ConsistencyPolicy
) -> str:
    """Compute consistency class from epoch-based projections.
    
    No heterogeneous arithmetic. All comparisons are epoch-to-epoch."""
    
    max_lag = 0
    for proj in snapshot.projections:
        lag = snapshot.snapshot_epoch - proj.projection_epoch
        if lag < 0:
            # Projection is somehow ahead of snapshot -- error
            raise SnapshotConsistencyError(
                f"Projection {proj.projection_name} has epoch "
                f"{proj.projection_epoch} > snapshot epoch {snapshot.snapshot_epoch}"
            )
        max_lag = max(max_lag, lag)
    
    if max_lag == 0:
        return "FULLY_CONSISTENT"
    elif max_lag <= policy.max_acceptable_epoch_lag:
        return "ACCEPTABLE_LAG"
    else:
        return "STALE_PROJECTION"
```

### 8.3 Epoch Allocation

```python
class SnapshotEpochAllocator:
    """Allocates snapshot epochs atomically.
    The Coordinator is the only caller of this service."""
    
    def allocate_epoch(self, session_id: str) -> int:
        """Atomically allocate a new snapshot epoch."""
        with db.transaction():
            epoch = db.execute(
                "UPDATE snapshot_epoch_counter "
                "SET current_epoch = current_epoch + 1 "
                "RETURNING current_epoch"
            ).scalar()
        return epoch
```

---

## 9. Corrected Snapshot Advancement Policy

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 8.2 (handle_critical_state_change).** Partial agent restart is replaced with full session restart to maintain the invariant that all agents share the same observation boundary.

### 9.1 Problem Statement

Amendment 3 specified `restart_agents = detected_change.affected_agent_ids`, creating a split-snapshot session where restarted agents reason about Snapshot V2 while non-restarted agents retain results from Snapshot V1.

This violates Invariant 8: "All agents in a session reason over the same observation boundary."

### 9.2 Corrected Policy

```python
def handle_critical_state_change(
    session: DecisionSession,
    detected_change: StateChange,
    coordinator: CoordinatorService
) -> SnapshotAdvancementDecision:
    """When post-snapshot evidence reveals a critical state change,
    the Coordinator must decide how to respond.
    
    SUPERSEDES Amendment 3 Section 8.2.
    
    KEY CHANGE: Partial agent restart is PROHIBITED.
    If snapshot advancement is needed, ALL agents must re-reason
    from the new snapshot."""
    
    if session.status in {"CD2F_IN_PROGRESS", "EXECUTION_AUTHORIZED"}:
        # Too late to advance -- flag as stale decision
        return SnapshotAdvancementDecision(
            action="FLAG_STALE",
            reason="Session too advanced to restart",
            stale_decision_metadata=StaleFlagMetadata(
                detected_change=detected_change,
                session_phase=session.status,
            ),
        )
    
    if not detected_change.affects_critical_facts(session.disruption_type):
        # Non-critical change -- continue with current snapshot
        return SnapshotAdvancementDecision(
            action="CONTINUE",
            reason="State change does not affect critical facts",
        )
    
    # Critical change -- FULL session restart
    if session.advancement_count >= session.policy.max_snapshot_advancements:
        # Guard against infinite advancement loops
        return SnapshotAdvancementDecision(
            action="ESCALATE_HITL",
            reason=(
                f"Session has been advanced {session.advancement_count} times "
                f"(max {session.policy.max_snapshot_advancements}). "
                f"World state is too volatile for autonomous decision."
            ),
        )
    
    new_snapshot = coordinator.create_decision_snapshot(session)
    
    return SnapshotAdvancementDecision(
        action="ADVANCE_AND_RESTART_ALL",    # NOT restart_agents
        new_snapshot=new_snapshot,
        restart_agents="ALL",                # Every agent re-reasons
        advancement_count=session.advancement_count + 1,
        reason=(
            f"Critical state change detected: {detected_change.summary}. "
            f"All agents must re-reason from snapshot epoch "
            f"{new_snapshot.snapshot_epoch}."
        ),
    )
```

### 9.3 Advancement Policy Parameters

```yaml
snapshot_advancement:
  max_snapshot_advancements: 3           # Max times a session can be restarted
  advancement_guard_window_seconds: 30   # Minimum time between advancements
  advancement_escalation: HITL           # What to do when max is reached
```

---

## 10. Corrected Freshness Computation

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 9.1 (`freshness_reference` field) and Section 29 (`compute_freshness` function).** Removes the WALL_CLOCK contradiction and fixes the post-snapshot freshness bug.

### 10.1 WALL_CLOCK Contradiction Resolution

Amendment 3 Section 9.1 defines:
```python
freshness_reference: Literal[
    "OBSERVATION_CUTOFF",  # Default
    "WALL_CLOCK",          # Legacy
] = "OBSERVATION_CUTOFF"
```

But Section 29 states: "All freshness computations throughout the architecture use `observation_cutoff` as the reference point."

These contradict. WALL_CLOCK is removed from the decision context entirely.

### 10.2 Post-Snapshot Freshness Bug

Amendment 3 Section 29 defines:
```python
if age <= timedelta(0):
    return 1.0  # Fact is at or after cutoff (but pre-snapshot)
```

If `data_as_of > observation_cutoff` (post-snapshot evidence), `age` is negative, and the function returns 1.0 (perfectly fresh). This contradicts the post-snapshot rejection rule.

### 10.3 Corrected Freshness Function

```python
def compute_fact_freshness(
    data_as_of: datetime,
    snapshot: DecisionSnapshot
) -> float:
    """Fact freshness is ALWAYS relative to the decision's observation boundary.
    
    SUPERSEDES Amendment 3 Section 29.
    
    POST-SNAPSHOT EVIDENCE: If data_as_of is after the observation cutoff,
    this is a contract violation. The evidence should have been rejected
    by the upstream validator. This function raises an error as a safety net.
    
    AT-CUTOFF EVIDENCE: If data_as_of exactly equals observation_cutoff,
    the evidence is perfectly fresh (freshness = 1.0).
    
    PRE-CUTOFF EVIDENCE: Freshness decreases linearly with age,
    reaching 0.0 at max_fact_age_minutes before the cutoff."""
    
    if data_as_of > snapshot.observation_cutoff:
        raise PostSnapshotEvidenceError(
            f"Evidence timestamp {data_as_of} is after snapshot cutoff "
            f"{snapshot.observation_cutoff}. Post-snapshot evidence must "
            f"be rejected by the upstream validator before reaching "
            f"freshness computation. This indicates a pipeline bug."
        )
    
    fact_age = snapshot.observation_cutoff - data_as_of
    max_age = timedelta(minutes=snapshot.max_fact_age_minutes)
    
    if fact_age == timedelta(0):
        return 1.0  # Exactly at cutoff: perfectly fresh
    
    if fact_age >= max_age:
        return 0.0  # Stale
    
    return 1.0 - (fact_age / max_age)


class PostSnapshotEvidenceError(Exception):
    """Raised when post-snapshot evidence reaches freshness computation.
    This should never happen in correct operation because the upstream
    evidence validator (Amendment 3 Section 8.1) rejects post-snapshot
    evidence before it reaches freshness computation."""
    pass
```

---

## 11. Direction-Aware Objective Normalization

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 11.2 (normalize_metric function) and Section 11.3 (objective score computation).** Fixes the signed normalization bug where `abs()` destroyed directional information.

### 11.1 Problem Statement

Amendment 3 normalizes as:
```python
normalized = min(1.0, max(0.0, abs(raw_value) / reference_scale))
```

This discards sign:
- `cost_delta = -$10,000` (savings) -> `0.1`
- `cost_delta = +$10,000` (cost increase) -> `0.1`

Both are treated identically, which is mathematically incorrect. Savings should be positive utility; additional cost should be negative utility.

### 11.2 Corrected ObjectiveMetricDefinition

```python
class ObjectiveMetricDefinition(BaseModel):
    """Definition of a single objective dimension with explicit
    direction and normalization semantics."""
    
    name: str
    direction: Literal["MINIMIZE", "MAXIMIZE"]
    reference_scale: float
    weight: float
    saturation_policy: Literal["CLIP", "LOG_COMPRESS"] = "CLIP"
    
    def normalize(self, raw_value: float) -> float:
        """Direction-aware normalization that preserves sign.
        
        Output semantics:
            Positive output = GOOD (improves the objective)
            Negative output = BAD (degrades the objective)
            Zero = no change from baseline
            Range: [-1.0, +1.0] (clipped at reference scale boundaries)
        
        For MINIMIZE dimensions (cost, risk, lead_time, carbon):
            Negative raw_value = reduction (GOOD) -> positive normalized
            Positive raw_value = increase (BAD) -> negative normalized
        
        For MAXIMIZE dimensions (service_level):
            Positive raw_value = improvement (GOOD) -> positive normalized
            Negative raw_value = degradation (BAD) -> negative normalized
        """
        
        if self.reference_scale <= 0:
            raise ValueError(
                f"reference_scale must be positive, got {self.reference_scale}"
            )
        
        # Normalize to [-1, 1] range
        normalized = raw_value / self.reference_scale
        
        if self.saturation_policy == "CLIP":
            normalized = max(-1.0, min(1.0, normalized))
        elif self.saturation_policy == "LOG_COMPRESS":
            # Logarithmic compression for extreme values
            sign = 1.0 if normalized >= 0 else -1.0
            normalized = sign * min(1.0, math.log1p(abs(normalized)))
        
        # Apply direction
        if self.direction == "MINIMIZE":
            # For minimization: negative raw = good, flip sign
            return -normalized
        else:
            # For maximization: positive raw = good, keep sign
            return normalized
```

### 11.3 Corrected ObjectiveNormalization

```python
class ObjectiveNormalization(BaseModel):
    """Policy-defined reference scales and directions for objective normalization.
    Fixed per profile. Independent of the candidate set.
    
    SUPERSEDES Amendment 3 Section 11.1."""
    
    metrics: list[ObjectiveMetricDefinition] = [
        ObjectiveMetricDefinition(
            name="cost",
            direction="MINIMIZE",
            reference_scale=100000.0,      # $100k delta = full reference
            weight=0.0,                    # Set by profile
            saturation_policy="CLIP",
        ),
        ObjectiveMetricDefinition(
            name="service_level",
            direction="MAXIMIZE",
            reference_scale=0.10,          # 10% service gap = full reference
            weight=0.0,
            saturation_policy="CLIP",
        ),
        ObjectiveMetricDefinition(
            name="risk",
            direction="MINIMIZE",
            reference_scale=1.0,           # Risk is already [0,1]
            weight=0.0,
            saturation_policy="CLIP",
        ),
        ObjectiveMetricDefinition(
            name="lead_time",
            direction="MINIMIZE",
            reference_scale=30.0,          # 30 days delta = full reference
            weight=0.0,
            saturation_policy="CLIP",
        ),
        ObjectiveMetricDefinition(
            name="carbon",
            direction="MINIMIZE",
            reference_scale=10000.0,       # 10k kg = full reference
            weight=0.0,
            saturation_policy="CLIP",
        ),
        ObjectiveMetricDefinition(
            name="inventory_health",
            direction="MAXIMIZE",
            reference_scale=30.0,          # 30 days-of-supply = full reference
            weight=0.0,
            saturation_policy="CLIP",
        ),
        ObjectiveMetricDefinition(
            name="cash_flow",
            direction="MINIMIZE",
            reference_scale=50000.0,       # $50k impact = full reference
            weight=0.0,
            saturation_policy="CLIP",
        ),
    ]
```

### 11.4 Corrected Objective Score Computation

```
For each feasible candidate c:
    
    For each objective metric m in ObjectiveNormalization.metrics:
        raw_value = get_impact_value(c, m.name)
                    # Source: ActionImpactEnvelope (baseline + predictive + simulation)
        
        utility(c, m) = m.normalize(raw_value)
                    # Output: [-1, +1], positive = good, negative = bad
    
    J(c) = SUM over all metrics m:
        m.weight * utility(c, m)
    
    J(c) = J(c) - uncertainty_penalty(c)
    
    Source hierarchy for raw values:
        1. SimulationResult (Twin Tier 3) -- if available
        2. PredictiveImpactEstimate (Tier 2) -- if available
        3. BaselineImpact (Tier 1) -- always available
    
    Normalization references: From ObjectiveNormalization (in DecisionPolicy)
    
    CRITICAL:
        - Savings (negative cost delta) correctly produce POSITIVE utility
        - Cost increases (positive cost delta) correctly produce NEGATIVE utility
        - Service improvements (positive service delta) correctly produce POSITIVE utility
        - Service degradation (negative service delta) correctly produce NEGATIVE utility
```

---

## 12. Renamed Candidate Budget Selection

> [!IMPORTANT]
> **SUPERSEDES the title and wording of Amendment 3 Section 10.** The pruning pipeline steps are unchanged; the description is corrected to avoid overclaiming safety.

### 12.1 Renamed Section Title

```
BEFORE: "Safe Candidate Pruning"
AFTER:  "Candidate Normalization and Budget Selection"
```

### 12.2 Corrected Step 8 Wording

```
STEP 8: CANDIDATE BUDGET SELECTION (RENAMED from "CANDIDATE BUDGET ENFORCEMENT")
    
    If remaining candidates > max_simulation_branches:
        
        Selection criterion: UPPER CONFIDENCE BOUND
            UCB(c) = estimated_score(c) + alpha * impact_uncertainty(c)
        
        This is a HEURISTIC for selecting the most promising candidates
        within a computational budget. It is NOT a proof that discarded
        candidates would not have won. UCB is used because it balances
        exploitation (high estimated score) with exploration (high 
        uncertainty that might indicate hidden potential).
        
        Guarantees:
            - ALWAYS include "do nothing + buffer" baseline
            - ALWAYS include at least one candidate per assigned domain
              (if that domain produced valid candidates)
            - High-uncertainty candidates with potential upside are retained
        
        Non-guarantee:
            Budget enforcement may discard candidates that would have
            scored highest after Twin simulation. This is an accepted
            trade-off for computational tractability. The UCB heuristic
            minimizes but does not eliminate this risk.
        
        Maximum output: max_simulation_branches + 1 (baseline)
```

### 12.3 Corrected Key Invariant

```
NO candidate is eliminated before Twin simulation unless:
    1. Its intent schema is invalid (Step 2)
    2. Its referenced entities do not exist (Step 3)
    3. It violates a hard constraint using BASELINE impact values (Step 5)
    4. It is a structural duplicate of another candidate (Step 6)
    5. It is PROVABLY dominated using BASELINE impact values with margin (Step 7)
    6. Budget is exceeded AND it has the lowest UCB score (Step 8 -- HEURISTIC)

LLM-estimated impact values are NEVER used for pruning or selection.
Dominance pruning (Step 7) uses ONLY Tier 1 BaselineImpact values.
Budget selection (Step 8) uses Tier 1 + Tier 2 values via UCB heuristic.
```

---

## 13. Unified Twin Simulation Materiality

> [!WARNING]
> **SUPERSEDES both Amendment 3 Section 13 (SimulationPolicy extension) and Section 30 (SimulationMaterialityThresholds).** Resolves the naming contradiction where two sections defined different field names for the same concept.

### 13.1 Problem Statement

Amendment 3 Section 13 defines:
```yaml
twin_required_cost_threshold: 200000.0
cascade_threshold: 0.70
novelty_threshold: 0.80
service_threshold: 0.15
risk_threshold: 0.50
```

Amendment 3 Section 30 defines:
```yaml
twin_required_cost_usd: 200000.0
twin_required_cascade_potential: 0.70
twin_required_novelty: 0.80
twin_recommended_cost_usd: 10000.0
twin_recommended_service_impact: 0.15
twin_recommended_risk: 0.50
```

Different names, different grouping, same concept. This must be one canonical definition.

### 13.2 Canonical SimulationMaterialityThresholds

```python
class SimulationMaterialityThresholds(BaseModel):
    """Single canonical definition of Twin simulation requirement thresholds.
    
    SUPERSEDES both Amendment 3 Section 13 (SimulationPolicy extension)
    and Amendment 3 Section 30 (SimulationMaterialityThresholds).
    
    These are the ONLY names used anywhere in the architecture.
    No legacy field names survive."""
    
    # ---- REQUIRED thresholds ----
    # Exceeding ANY of these triggers TwinRequirement.REQUIRED
    required_financial_exposure_usd: float = 200000.0
    required_cascade_potential: float = 0.70
    required_novelty_score: float = 0.80
    required_regulatory_relevance: bool = True   # Any regulatory flag -> REQUIRED
    
    # ---- RECOMMENDED thresholds ----
    # Exceeding ANY of these triggers TwinRequirement.RECOMMENDED
    # (if no REQUIRED threshold is exceeded)
    recommended_financial_exposure_usd: float = 10000.0
    recommended_service_impact: float = 0.15
    recommended_risk_exposure: float = 0.50
    
    # ---- ADVISORY ----
    # Below all thresholds: TwinRequirement.ADVISORY


class SimulationMateriality(BaseModel):
    """Multi-dimensional assessment of whether Twin simulation is warranted.
    
    SUPERSEDES Amendment 3 Section 13 SimulationMateriality.
    Uses the CANONICAL field names from SimulationMaterialityThresholds."""
    
    financial_exposure_usd: float
    service_level_impact: float
    risk_exposure: float
    regulatory_relevance: bool
    cascade_potential: float
    novelty_score: float
    
    def classify(
        self, thresholds: SimulationMaterialityThresholds
    ) -> TwinRequirement:
        """Classify this assessment against canonical thresholds.
        Uses ONLY the canonical threshold names."""
        
        # Check REQUIRED thresholds
        if (self.financial_exposure_usd > thresholds.required_financial_exposure_usd
            or self.regulatory_relevance and thresholds.required_regulatory_relevance
            or self.cascade_potential > thresholds.required_cascade_potential
            or self.novelty_score > thresholds.required_novelty_score):
            return TwinRequirement.REQUIRED
        
        # Check RECOMMENDED thresholds
        if (self.financial_exposure_usd > thresholds.recommended_financial_exposure_usd
            or self.service_level_impact > thresholds.recommended_service_impact
            or self.risk_exposure > thresholds.recommended_risk_exposure):
            return TwinRequirement.RECOMMENDED
        
        return TwinRequirement.ADVISORY
```

### 13.3 Canonical SimulationPolicy

```python
class SimulationPolicy(BaseModel):
    """SUPERSEDES SimulationPolicy from both Amendment 3 Section 13
    and Section 30. Uses ONLY canonical field names."""
    
    # Materiality thresholds (SINGLE definition)
    materiality_thresholds: SimulationMaterialityThresholds
    
    # Twin execution parameters
    max_simulation_branches: int = 5
    simulation_timeout_seconds: int = 120
    max_simulation_horizon_days: int = 90
    
    # Failure response parameters
    twin_timeout_penalty_factor: float = 1.5
    
    # REMOVED: simulation_trigger_threshold_usd (superseded by materiality_thresholds)
    # REMOVED: twin_required_cost_threshold (superseded by materiality_thresholds)
    # REMOVED: cascade_threshold (superseded by materiality_thresholds)
    # REMOVED: novelty_threshold (superseded by materiality_thresholds)
    # REMOVED: service_threshold (superseded by materiality_thresholds)
    # REMOVED: risk_threshold (superseded by materiality_thresholds)
```

---

## 14. Corrected CD2F Pipeline Wording

> [!IMPORTANT]
> **Corrects wording in Amendment 3 Section 12 (Pareto Analysis).**

### 14.1 Correction

Replace in the Pareto analysis flow:

```
BEFORE:
    "-> Proceed to execution authorization"

AFTER:
    "-> Proceed to ExecutionPolicy evaluation"
```

CD2F selects the best candidate. The ExecutionPolicyService evaluates whether that selection can be executed autonomously. These are separate concerns per Amendment 3 Section 15.

---

## 15. Database Constraints for Event Sequencing

> [!IMPORTANT]
> **EXTENDS Amendment 3 Section 19 (Event Sequence Allocation).** Adds database-level enforcement to complement the application-level single-writer guarantee.

### 15.1 Constraints

```sql
-- Deliberation events table constraints
-- EXTENDS the schema implied by Amendment 3 Section 19

ALTER TABLE deliberation_events
    ADD CONSTRAINT uq_session_sequence 
        UNIQUE (session_id, sequence_number);

ALTER TABLE deliberation_events
    ADD CONSTRAINT chk_sequence_positive 
        CHECK (sequence_number > 0);

ALTER TABLE deliberation_events
    ADD CONSTRAINT chk_sequence_monotonic
        CHECK (sequence_number >= 1);

-- Session counter table constraint
ALTER TABLE deliberation_sessions
    ADD CONSTRAINT chk_current_sequence_positive
        CHECK (current_sequence >= 0);
```

### 15.2 Rationale

The application-level guarantee (Coordinator is the single writer) prevents sequence conflicts under normal operation. The database constraint is a safety net that:
1. Catches bugs if the single-writer invariant is accidentally violated
2. Provides durable enforcement independent of application correctness
3. Has negligible performance impact (unique index on two columns)

---

## 16. Canonical Session State Machine

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 23 (Terminal State Guards).** Adds a complete state transition matrix.

### 16.1 State Transition Diagram

```
                            +------------------+
                            |      CREATED     |
                            +--------+---------+
                                     |
                           [session initialized]
                                     |
                                     v
                     +---------------+--------------+
                     |           ACTIVE             |
                     |  (deliberation in progress)  |
                     +--+--------+--------+--------++
                        |        |        |         |
               [cancel] |  [success]  [timeout]  [advance snapshot]
                        |        |        |         |
                        v        v        v         v
                   +----+--+ +--+---+ +--+----+ +--+------+
                   |CANCELLED| |CLOSED| |EXPIRED| |ACTIVE   |
                   |(absorbing)| |(absorbing)| |(absorbing)| |(new epoch)|
                   +---------+ +------+ +-------+ +---------+
```

### 16.2 Legal Transitions

```python
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "CREATED":   {"ACTIVE", "CANCELLED"},
    "ACTIVE":    {"CLOSED", "CANCELLED", "EXPIRED"},
    "CLOSED":    set(),    # Absorbing state
    "CANCELLED": set(),    # Absorbing state
    "EXPIRED":   set(),    # Absorbing state
}

TERMINAL_STATES = {"CLOSED", "CANCELLED", "EXPIRED"}

def validate_state_transition(
    current_state: str,
    target_state: str
) -> bool:
    """Validate that a state transition is legal."""
    if current_state not in LEGAL_TRANSITIONS:
        raise ValueError(f"Unknown state: {current_state}")
    return target_state in LEGAL_TRANSITIONS[current_state]
```

### 16.3 Corrected Terminal State Guard

```python
def handle_incoming_event(
    event: DeliberationEvent,
    session: DeliberationSessionView
) -> EventHandlingResult:
    """Terminal state guard with explicit transition validation.
    
    SUPERSEDES Amendment 3 Section 23."""
    
    if session.status in TERMINAL_STATES:
        # Session is in a terminal (absorbing) state
        if event.event_type in {"SESSION_CANCELLED", "SESSION_CLOSED", "SESSION_EXPIRED"}:
            # Idempotent: another terminal event for an already-terminal session
            return EventHandlingResult(
                accepted=False,
                reason=(
                    f"Session {session.session_id} is already in terminal "
                    f"state {session.status}. Late terminal event "
                    f"{event.event_type} is a no-op."
                ),
                is_idempotent_duplicate=True,
            )
        
        # Non-terminal event against a terminal session: reject
        return EventHandlingResult(
            accepted=False,
            reason=(
                f"Session {session.session_id} is in terminal state "
                f"{session.status}. Non-terminal event {event.event_type} "
                f"is rejected."
            ),
        )
    
    # Session is not terminal: validate transition if this is a state-changing event
    if event.event_type in {"SESSION_CANCELLED", "SESSION_CLOSED", "SESSION_EXPIRED"}:
        target_state = event.event_type.replace("SESSION_", "")
        if not validate_state_transition(session.status, target_state):
            return EventHandlingResult(
                accepted=False,
                reason=(
                    f"Transition from {session.status} to {target_state} "
                    f"is not a legal state transition."
                ),
            )
    
    return EventHandlingResult(accepted=True)
```

### 16.4 Atomicity Specification

```
State transitions and event insertion MUST occur in a single
database transaction. The pattern is:

BEGIN TRANSACTION;
    -- 1. Read current session status (WITH lock)
    SELECT status FROM deliberation_sessions
        WHERE session_id = :sid FOR UPDATE;
    
    -- 2. Validate transition is legal
    -- (application code using LEGAL_TRANSITIONS)
    
    -- 3. Insert event
    INSERT INTO deliberation_events (...) VALUES (...);
    
    -- 4. Update session status
    UPDATE deliberation_sessions
        SET status = :new_status
        WHERE session_id = :sid;
    
    -- 5. Insert outbox entry
    INSERT INTO outbox (...) VALUES (...);
COMMIT;

This prevents race conditions where two concurrent requests
both see status=ACTIVE and attempt different terminal transitions.
The FOR UPDATE lock serializes access to the session row.
```

---

## 17. Corrected Policy Hash Computation

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 27 (Policy and Profile Integrity).** Fixes the self-referential hash computation.

### 17.1 Problem Statement

Amendment 3 defines:
```python
policy_hash: str   # SHA-256 of serialized policy content
def verify_integrity(self) -> bool:
    return self.policy_hash == compute_hash(self.serialize())
```

The `serialize()` method includes `policy_hash` itself. Computing `SHA-256(content_including_hash)` is self-referential -- the hash would need to be its own input.

Additionally, `computed_at: datetime` would produce different hashes for identical policy content computed at different times.

### 17.2 Corrected Hash Computation

```python
class PolicyIntegrity(BaseModel):
    """Integrity metadata for DecisionPolicy.
    These fields are EXCLUDED from the hash computation.
    
    SUPERSEDES the inline hash fields in Amendment 3 Section 27."""
    
    policy_content_hash: str         # SHA-256 of canonical policy payload
    profile_content_hash: str        # SHA-256 of canonical profile payload
    computed_at: datetime            # When hashes were computed
    hash_algorithm: str = "sha256"   # Algorithm used
    
    # Explicit exclusion set (self-documenting)
    EXCLUDED_FROM_HASH: ClassVar[set[str]] = {
        "policy_content_hash",
        "profile_content_hash", 
        "computed_at",
        "hash_algorithm",
    }


class DecisionPolicy(BaseModel):
    # ... all existing policy fields ...
    
    # Integrity metadata (EXCLUDED from hash computation)
    integrity: PolicyIntegrity
    
    @staticmethod
    def compute_content_hash(policy: "DecisionPolicy") -> str:
        """Compute a content-addressable hash of the policy.
        
        CRITICAL: The integrity metadata itself is EXCLUDED from
        the hash computation to avoid self-reference."""
        
        canonical_payload = policy.model_dump(
            exclude={"integrity"}
        )
        
        # Deterministic JSON serialization
        canonical_json = json.dumps(
            canonical_payload,
            sort_keys=True,
            default=str,          # Handle datetime, Enum, etc.
            separators=(",", ":"),  # No whitespace variation
        )
        
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify that the policy content has not been modified
        since the hash was computed."""
        recomputed = DecisionPolicy.compute_content_hash(self)
        return recomputed == self.integrity.policy_content_hash
```

### 17.3 DecisionRecord Binding

```python
class DecisionRecord(BaseModel):
    # ... existing fields ...
    
    # Policy binding (CORRECTED)
    policy_content_hash: str        # From PolicyIntegrity
    profile_content_hash: str       # From PolicyIntegrity
    policy_version: str             # Semantic version (human-readable)
    
    # Verification: at replay time, recompute hash from the stored
    # policy and compare with the recorded hash. If they differ,
    # the policy was modified between decision time and replay time.
```

---

## 18. Corrected B0-B7 Ablation Ladder

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 32 (B0-B7 table and B0 definition).** Fixes: (a) B3/B4 overlap, (b) hard-coded freeze date, (c) "assumption-free" wording.

### 18.1 Corrected Ablation Ladder

| Baseline | Configuration | Components Added (vs Previous) | What It Tests |
| :--- | :--- | :--- | :--- |
| **B0** | Deterministic rule heuristic | Hard-coded if-then-else. No ML, no LLM, no agents, no Twin. Rules frozen before any system evaluation begins. | Is any intelligence better than deterministic rules? |
| **B1** | Single generalist agent | One LLM+ML agent covering all domains. No specialization. Direct proposal to minimal CD2F (feasibility only). No cross-examination. No Twin. | Does ML+LLM reasoning add value over rules? |
| **B2** | Six independent specialists | All six agents independently assess. Each produces a proposal. No cross-examination. No Deliberation Table interaction. No evidence sufficiency gate. Proposals directly to CD2F (feasibility + objective score). No Twin. | Does domain specialization improve quality? |
| **B3** | B2 + Deliberation Table + cross-examination | B2 + Deliberation Table + cross-examination protocol + independence enforcement. NO evidence sufficiency gate. CD2F with full objective function. No Twin. | Does structured deliberation improve over independent assessment? |
| **B4** | B3 + evidence sufficiency gate | B3 + evidence sufficiency gate actively enforced. Insufficient evidence triggers HITL instead of proceeding. No Twin. | Does evidence gating reduce error rate? |
| **B5** | B4 + Twin simulation (naive scoring) | B4 + Twin counterfactual evaluation. CD2F uses simulation results but with simplified scoring (no Pareto analysis, no uncertainty adjustment). | Does counterfactual simulation add value? |
| **B6** | B5 + full CD2F | B5 + direction-aware objective normalization + proper Pareto frontier + uncertainty adjustment + three-tier impact model. Full candidate normalization pipeline. | Does formal arbitration beat simplified scoring? |
| **B7** | Full system | B6 + all governance: R_i lifecycle, execution authorization, DecisionRecord, replay manifest, failure taxonomy, cancellation propagation, priority admission control, state revalidation. | Full system with all governance layers. |

### 18.2 Key Corrections

1. **B3 vs B4:** B3 now explicitly states "NO evidence sufficiency gate." B4 adds the evidence gate. Each baseline adds exactly one new component.
2. **B6:** Now references "direction-aware objective normalization" and "three-tier impact model" to reflect Amendment 4 corrections.
3. **B7:** Now includes "state revalidation" to reflect Amendment 4 Section 21.

### 18.3 Corrected B0 Definition

```python
class B0_RuleBasedHeuristic:
    """Baseline B0: deterministic rule heuristic for supplier delay.
    
    This definition MUST be frozen before any system-under-test
    evaluation begins. No modification is permitted after freeze.
    
    CORRECTED: Removed hard-coded freeze date. Freeze is a process
    requirement, not a calendar date."""
    
    VERSION = "1.0.0"
    FROZEN = False  # Set to True when frozen; rejection of modifications enforced
    
    def decide(self, disruption: SupplierDelayEvent) -> str:
        """Pure rule-based decision. No ML, no LLM."""
        
        if self.FROZEN:
            pass  # Intentional: this is the frozen logic, no modifications
        
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

## 19. Corrected Statistical Protocol Wording

> [!IMPORTANT]
> **Corrects minor wording defects in Amendment 3 Section 33.**

### 19.1 "Assumption-Free" Correction

```
BEFORE: "Primary test: non-parametric, assumption-free"
AFTER:  "Primary test: non-parametric, distribution-light"
```

All statistical tests have assumptions. Permutation tests assume exchangeability under the null hypothesis. "Distribution-light" accurately conveys that no distributional shape assumptions are required.

### 19.2 Calibration Targets Reframing

```
BEFORE: "ECE target: 0.10", "Brier target: 0.15"
AFTER:  "ECE acceptance threshold: 0.10", "Brier acceptance threshold: 0.15"
```

These are evaluation acceptance criteria, not architectural constants. They may be adjusted based on domain characteristics and calibration data distribution.

### 19.3 Minimum Sample Size Note

```
BEFORE: "Minimum scenarios per test: 30"
AFTER:  "Minimum scenarios per test: 30 (floor for V2 MVP evaluation)

NOTE: 30 scenarios is a practical minimum for non-parametric tests.
Production-grade evaluation should use formal power analysis to 
determine adequate sample size for the target effect size and
desired statistical power. The power analysis methodology is 
listed in the Improvement Backlog (Section 27)."
```

---

## 20. Corrected ActionDefinition Schema

> [!IMPORTANT]
> **Corrects the nullability of execution_capability_id in the ActionRegistryEntry (Amendment 4 Section 3).**

This correction is already incorporated in the `ActionRegistryEntry` definition in Section 3.2 above, where:

```python
execution_capability_id: Optional[str]  # None for advisory actions
```

The consistency invariant is enforced by the `validate()` method:

```python
if self.advisory_only and self.execution_capability_id is not None:
    errors.append(...)
if not self.advisory_only and self.execution_capability_id is None:
    errors.append(...)
```

This is included as a separate section for traceability against the review's Point 63.

---

## 21. Final State Revalidation Before Execution

> [!IMPORTANT]
> **NEW SECTION.** Adds a revalidation step between ExecutionPolicy approval and the Execution Adapter to detect stale authorizations.

### 21.1 Rationale

A decision is computed against a specific `snapshot_epoch`. Between decision approval and execution, the world may have changed (new disruption, supplier status update, inventory movement). The execution adapter should verify that the decision context is still valid before applying the action.

This is the runtime equivalent of optimistic concurrency control.

### 21.2 State Revalidation Schema

```python
class StateRevalidation(BaseModel):
    """Pre-execution revalidation of the decision context.
    
    Runs AFTER ExecutionPolicy approval, BEFORE execution adapter.
    Verifies that the world state has not materially changed since
    the decision was computed."""
    
    decision_id: str
    approved_snapshot_epoch: int        # Epoch of the snapshot the decision used
    current_snapshot_epoch: int         # Current epoch at revalidation time
    
    # Revalidation checks
    epoch_drift: int                    # current - approved
    critical_entity_changes: list[EntityChange]
    revalidation_result: Literal[
        "VALID",                        # No material change; proceed with execution
        "DEGRADED",                     # Minor changes; proceed with caution flag
        "STALE",                        # Material change; decision may be invalid
    ]
    
    # Response
    execution_authorization: Literal[
        "PROCEED",                      # Execute the action
        "PROCEED_WITH_FLAG",            # Execute but flag for review
        "REPLAN",                       # Decision is stale; trigger replanning
        "ESCALATE",                     # Cannot determine; escalate to HITL
    ]

class EntityChange(BaseModel):
    """A detected change to an entity that was part of the decision context."""
    entity_type: str
    entity_id: str
    change_type: Literal["updated", "deleted", "status_changed"]
    change_severity: Literal["LOW", "MODERATE", "HIGH"]
    detail: str
```

### 21.3 Revalidation Logic

```python
def revalidate_before_execution(
    decision: DecisionRecord,
    current_state: WorldStateView,
    policy: RevalidationPolicy
) -> StateRevalidation:
    """Revalidate the decision context before execution.
    
    Runs in the execution pipeline between ExecutionPolicy
    approval and the Execution Adapter."""
    
    epoch_drift = current_state.snapshot_epoch - decision.snapshot_epoch
    
    if epoch_drift == 0:
        # World has not changed since decision
        return StateRevalidation(
            decision_id=decision.decision_id,
            approved_snapshot_epoch=decision.snapshot_epoch,
            current_snapshot_epoch=current_state.snapshot_epoch,
            epoch_drift=0,
            critical_entity_changes=[],
            revalidation_result="VALID",
            execution_authorization="PROCEED",
        )
    
    # Check if entities involved in the decision have changed
    changes = detect_entity_changes(
        decision.affected_entities,
        decision.snapshot_epoch,
        current_state.snapshot_epoch,
    )
    
    critical_changes = [c for c in changes if c.change_severity == "HIGH"]
    
    if critical_changes:
        return StateRevalidation(
            revalidation_result="STALE",
            execution_authorization="REPLAN",
            critical_entity_changes=changes,
            # ... other fields
        )
    
    moderate_changes = [c for c in changes if c.change_severity == "MODERATE"]
    
    if moderate_changes and epoch_drift > policy.max_acceptable_drift:
        return StateRevalidation(
            revalidation_result="DEGRADED",
            execution_authorization="PROCEED_WITH_FLAG",
            critical_entity_changes=changes,
            # ... other fields
        )
    
    return StateRevalidation(
        revalidation_result="VALID",
        execution_authorization="PROCEED",
        critical_entity_changes=changes,
        # ... other fields
    )
```

### 21.4 Pipeline Position

```
... -> CD2F Arbitration -> ExecutionPolicy Evaluation 
    -> STATE REVALIDATION (NEW)    
    -> Execution Adapter
```

---

## 22. Bounded Replay Exactness

> [!IMPORTANT]
> **EXTENDS Amendment 3 Section 28 (Replay Manifest).** Adds `exact_system_available` condition to prevent overclaiming replay fidelity.

### 22.1 Corrected Replay Manifest

```python
class DecisionReplayManifest(BaseModel):
    """EXTENDS Amendment 3 Section 28.
    
    Key addition: exact_system_available is a computed Boolean
    that indicates whether EXACT_SYSTEM replay is actually achievable
    given the captured dependencies."""
    
    # ... all existing fields from Amendment 3 ...
    
    # Replay fidelity (CORRECTED)
    replay_type: Literal[
        "TRACE",          # Replay recorded events and tool responses
        "LOGICAL",        # Rerun decision algorithm with recorded inputs
        "MODEL",          # Rerun model inference (requires same model environment)
        "EXACT_SYSTEM",   # Full deterministic replay (ONLY if requirements met)
    ]
    
    # NEW: Explicit availability check
    exact_system_available: bool
    exact_system_blockers: list[str]   # Why exact replay is not available
    
    exact_replay_requirements: Optional[ExactReplayRequirements]
    
    def determine_max_replay_fidelity(self) -> str:
        """Determine the highest fidelity replay that is actually achievable."""
        
        if self.exact_system_available:
            return "EXACT_SYSTEM"
        
        if self.exact_replay_requirements is not None:
            if (self.exact_replay_requirements.model_weights_captured
                and self.exact_replay_requirements.inference_engine_captured):
                return "MODEL"
        
        if self.tool_invocation_log_ref is not None:
            return "LOGICAL"
        
        return "TRACE"


class ExactReplayRequirements(BaseModel):
    """Documents what is needed for exact system replay.
    
    CORRECTED from Amendment 3: fields now indicate whether
    requirements are MET, not just what is needed."""
    
    # Each field indicates both requirement and capture status
    requires_same_model_weights: bool = True
    model_weights_captured: bool = False          # NEW: was it actually captured?
    model_weights_ref: Optional[str] = None       # Reference to stored weights
    
    requires_same_inference_engine: bool = True
    inference_engine_captured: bool = False
    inference_engine_version: Optional[str] = None
    
    requires_same_quantization: bool = True
    quantization_captured: bool = False
    quantization_config: Optional[str] = None
    
    requires_frozen_tool_responses: bool = True
    tool_responses_captured: bool = False
    tool_response_log_ref: Optional[str] = None
    
    notes: list[str] = []
```

---

## 23. Corrected Pareto Confidence Labels

> [!IMPORTANT]
> **Corrects the confidence label naming in Amendment 3 Section 12.**

### 23.1 Label Corrections

```
BEFORE:
    decision_confidence = "PARETO_DOMINANT"
    decision_confidence = "POLICY_WEIGHT_SELECTED"
    decision_confidence = "AMBIGUOUS_REQUIRES_HITL"

AFTER:
    decision_confidence = "SINGLETON_PARETO_FRONTIER"
    decision_confidence = "POLICY_WEIGHT_RESOLVED"
    decision_confidence = "GENUINE_PARETO_AMBIGUITY"
```

### 23.2 Rationale

- `PARETO_DOMINANT` implies a specific technical meaning (one solution dominates all others on every dimension). The actual situation is that the Pareto frontier has exactly one member, which could be because it is truly dominant or because all other candidates were already eliminated. `SINGLETON_PARETO_FRONTIER` is more precise.
- `POLICY_WEIGHT_SELECTED` is acceptable but `POLICY_WEIGHT_RESOLVED` better conveys that the weights resolved an ambiguity.
- `AMBIGUOUS_REQUIRES_HITL` is replaced with `GENUINE_PARETO_AMBIGUITY` to emphasize that this is a real trade-off, not a system failure.

---

## 24. Saturation Policy in Objective Normalization

> [!IMPORTANT]
> **EXTENDS Amendment 4 Section 11.** Adds explicit saturation behavior documentation.

### 24.1 Saturation Behavior

The `ObjectiveMetricDefinition` (Section 11.2) includes a `saturation_policy` field:

```python
saturation_policy: Literal["CLIP", "LOG_COMPRESS"] = "CLIP"
```

**CLIP (Default for V2):**
- Values beyond `[-reference_scale, +reference_scale]` are clipped to `[-1.0, +1.0]`
- This means a cost delta of `$200,000` against a reference of `$100,000` is treated identically to a cost delta of `$500,000`
- This is acceptable for V2 because the reference scales are calibrated to expected operating ranges
- For extreme-value domains, `LOG_COMPRESS` should be used

**LOG_COMPRESS (Available but not default):**
- Values beyond the reference scale are compressed logarithmically
- `sign(x) * min(1.0, log1p(|x / reference|))`
- This preserves ordering beyond the reference scale while still bounding output

### 24.2 Profile Configuration

```yaml
decision_policy:
  normalization:
    metrics:
      - name: cost
        direction: MINIMIZE
        reference_scale: 100000
        saturation_policy: CLIP        # Default: clip at reference
      - name: service_level
        direction: MAXIMIZE
        reference_scale: 0.10
        saturation_policy: CLIP
      # ... other metrics
```

---

## 25. Corrected Unified Architecture Diagram

> [!WARNING]
> **SUPERSEDES Amendment 3 Section 35.** Incorporates all Amendment 4 corrections.

```
+=============================================================================+
|                   SCOF V2 COGNITIVE DECISION FABRIC                        |
|         (D3 through D10 -- Contract Freeze Revision)                       |
+=============================================================================+
|                                                                             |
|  TEN ARCHITECTURAL INVARIANTS (Frozen)                                      |
|  Wording corrections from Amendments 3 and 4                                |
|                                                                             |
|  +--[CANONICAL REGISTRIES]-----------------------------------------------+ |
|  | ClaimTypeRegistry | EvidenceClass (NEW) | ActionRegistry (UNIFIED)     | |
|  | (Single source of truth for all agent contracts, evidence classes,     | |
|  |  and action definitions including Twin/execution bindings)             | |
|  +-----------------------------------------------------------------------+ |
|                                                                             |
|  +--[D9: OBSERVABILITY, EXPLAINABILITY & DESKTOP CONSOLE]----------------+ |
|  | Tauri v2 | Decision Trace | HITL Escalation | What-If Lab              | |
|  | Evidence Visualization | Trade-off Explanations | DecisionRecord       | |
|  | OutcomeObservation (structured) | CriticalitySensitivityReport         | |
|  +-----------------------------------------------------------------------+ |
|       |                    ^                                                |
|  +--[D8: EVENT & RUNTIME BACKBONE (Kafka + Outbox)]---------------------+ |
|  | FastAPI | WebSocket | Transactional Outbox -> Kafka Topics            | |
|  | SCOFEvent Contract | Consumer Idempotency | Aggregate Versioning      | |
|  | Session State Machine (explicit transitions, DB-enforced)             | |
|  | DB constraints: UNIQUE(session_id, sequence_number)                   | |
|  +-----------------------------------------------------------------------+ |
|       |                    ^                    ^                           |
|  +--[DECISION POLICY LAYER]---------+  +--[D10: EVALUATION]---------+    |
|  | DecisionPolicy (from profile)     |  | B0-B7 Ablation Ladder      |    |
|  | ObjectiveNormalization (direction- |  |   (corrected: B3 no gate,  |    |
|  |   aware, signed, with saturation  |  |    B4 adds gate)           |    |
|  |   policy)                         |  | Non-parametric statistical  |    |
|  | Policy precedence (6 levels)      |  |   protocol (distribution-  |    |
|  | PolicyIntegrity (content hash     |  |   light, not assumption-   |    |
|  |   excluding self-reference)       |  |   free)                    |    |
|  +-----------------------------------+  | ECE/Brier acceptance       |    |
|                  |                      |   thresholds               |    |
|                  |                      | Anti-Overfitting Suite     |    |
|                  |                      +-----------------------------+    |
|                  |                                                          |
|  +=================================================================+      |
|  |        LANGGRAPH ORCHESTRATION KERNEL (D6)                     |      |
|  |        + Coordinator (decomposed into services)                |      |
|  |        + Session Overlap Detection                             |      |
|  |        + Snapshot Epoch Allocation (common coordinate)         |      |
|  |                                                                 |      |
|  |  [Ingest] -> [Snapshot + Trigger Binding] -> [RAG T1] ->       |      |
|  |  -> [Route] -> [Bind] ->                                       |      |
|  |  -> [Fan-Out (independent)] -> [Fan-In] ->                     |      |
|  |  -> [Cross-Exam (targeted, bounded)] ->                        |      |
|  |  -> [Evidence Sufficiency Gate (tiered criticality)] ->         |      |
|  |  -> [Candidate Extraction] ->                                   |      |
|  |  -> [Schema Validation] -> [Entity Validation] ->              |      |
|  |  -> [THREE-TIER IMPACT EVALUATION] ->                           |      |
|  |       (Tier 1: Baseline from facts)                             |      |
|  |       (Tier 2: Predictive from models)                          |      |
|  |  -> [Hard-Constraint Check (Tier 1 only)] ->                   |      |
|  |  -> [Dedup] ->                                                  |      |
|  |  -> [Dominance Pruning (Tier 1 only, with margin)] ->          |      |
|  |  -> [UCB Budget Selection (Tier 1+2, HEURISTIC)] ->            |      |
|  |  -> [Twin Requirement Classification] ->                        |      |
|  |       (Uses unified SimulationMaterialityThresholds)            |      |
|  |  -> [Twin Simulation (Tier 3: counterfactual)] ->              |      |
|  |  -> [CD2F (direction-aware normalization,                       |      |
|  |       proper Pareto, SINGLETON_FRONTIER/                        |      |
|  |       POLICY_WEIGHT_RESOLVED/GENUINE_AMBIGUITY)] ->            |      |
|  |  -> [ExecutionPolicy Evaluation] ->                             |      |
|  |  -> [STATE REVALIDATION (NEW)] ->                               |      |
|  |  -> [Execute/Escalate]                                          |      |
|  +=================================================================+      |
|       |              |              |              |              |         |
|  +=================================================================+      |
|  |     LANGCHAIN AGENT REASONING LAYER (D3/D4)                   |      |
|  |     + Agent-Internal Tier-2 RAG (MCP-Governed)                |      |
|  |     + DomainOwnershipPolicy enforcement (validated contracts) |      |
|  |     + ActionIntent (decision params, NOT impact estimates)    |      |
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
|  |     State machine: explicit transitions, DB-enforced           |      |
|  |     DB: UNIQUE(session_id, sequence_number)                    |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     IMPACT EVALUATION SERVICE (CORRECTED)                     |      |
|  |     Tier 1: BaselineImpact (from authoritative facts)          |      |
|  |     Tier 2: PredictiveImpactEstimate (from domain models)      |      |
|  |     Epistemic separation: Tier 1 is deterministic,             |      |
|  |       Tier 2 carries prediction uncertainty                    |      |
|  |     LLM numbers NEVER enter this computation                   |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DIGITAL TWIN -- COUNTERFACTUAL EVALUATOR (D7)             |      |
|  |     Tier 3: Counterfactual simulation results                  |      |
|  |     Requirement: REQUIRED / RECOMMENDED / ADVISORY             |      |
|  |       (unified SimulationMaterialityThresholds)                |      |
|  |     Failure: REQUIRED+timeout -> HITL (no autonomous CD2F)    |      |
|  |     Produces: SimulationResult + SimulationManifest            |      |
|  |     Authority: ONLY within isolated Layer-3 scenario scope     |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     CD2F EVIDENCE-BASED ARBITRATION ENGINE (D7)               |      |
|  |     Objective: DecisionObjective (from DecisionPolicy)         |      |
|  |     Normalization: Direction-aware, signed, with saturation    |      |
|  |     Pareto: Proper Pareto frontier computation                 |      |
|  |     Labels: SINGLETON_FRONTIER / POLICY_WEIGHT_RESOLVED /      |      |
|  |             GENUINE_PARETO_AMBIGUITY                           |      |
|  |     Math: J(c) = SUM(w_m * utility(c,m)) - penalty            |      |
|  |     "Deterministic arbitration over materialized context"      |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     D1 + D2: ENTERPRISE DATA FABRIC (Frozen Baseline)         |      |
|  |     PostgreSQL: System of Record                               |      |
|  |     Neo4j: Topology projection (derived)                       |      |
|  |     pgvector: Semantic precedent memory                        |      |
|  |     Redis: Governed cache (fail-closed for critical evidence)  |      |
|  |     Snapshot epochs: common consistency coordinate              |      |
|  +=================================================================+      |
|                                                                             |
+=============================================================================+
```

---

## 26. Corrected Candidate Normalization Pipeline

> [!IMPORTANT]
> **SUPERSEDES Amendment 3 Section 10.1.** Incorporates all Amendment 4 naming and tier corrections.

```
STEP 1: EXTRACT
    Collect all candidate actions from all revised agent proposals.
    Raw candidates: up to N (6 agents x max_candidates_per_agent).
    Each candidate has: ActionIntent (with decision parameters) +
    supporting claims + evidence.

STEP 2: SCHEMA VALIDATION
    Validate every candidate intent against its typed ActionIntent schema.
    Validate action_type exists in ActionRegistry (unified).
    Validate proposer_agent_id is in ActionRegistryEntry.permitted_proposers.
    CRITERION: deterministic (schema validation is binary).
    Reject candidates with invalid/missing parameters.

STEP 3: ENTITY VALIDATION
    Verify all referenced entity IDs exist in D2 as of the DecisionSnapshot.
    CRITERION: deterministic (entity existence is factual).
    Reject candidates referencing non-existent entities.

STEP 4: THREE-TIER IMPACT EVALUATION
    Run ImpactEvaluationService for each valid candidate:
        4a: Compute Tier 1 BaselineImpact (from authoritative facts).
        4b: Compute Tier 2 PredictiveImpactEstimate (from domain models).
             Only for actions where ActionRegistryEntry.impact_evaluation_tier
             == "BASELINE_AND_PREDICTIVE".
    Candidates where baseline cannot be computed are flagged but retained.
    SOURCE: authoritative data sources + validated domain models. Never LLM.

STEP 5: HARD-CONSTRAINT PRE-CHECK
    Eliminate candidates violating hard constraints from DecisionPolicy.
    Uses ONLY Tier 1 BaselineImpact values.
    CRITERION: deterministic (hard constraints are binary).
    Example: proposed route has no reefer capability for perishable -> eliminate.

STEP 6: DEDUPLICATION
    Merge semantically identical candidates from different agents.
    CRITERION: structural comparison of intent parameters.
    Merge rule: keep the candidate with higher-authority evidence.

STEP 7: DOMINANCE PRUNING
    A candidate is dominated ONLY if:
        - BOTH candidates have complete Tier 1 BaselineImpact
        - It is strictly worse on ALL Tier 1 dimensions
        - Safety margin: policy.dominance_pruning_margin applies
    
    Tier 2 PredictiveImpactEstimate is NOT used for dominance pruning
    because it carries prediction uncertainty.
    
    If Tier 1 is incomplete for either candidate: DO NOT prune.

STEP 8: CANDIDATE BUDGET SELECTION (renamed from "enforcement")
    If remaining candidates > max_simulation_branches:
        
        Selection criterion: UPPER CONFIDENCE BOUND (HEURISTIC)
            UCB(c) = weighted_score(Tier1 + Tier2) + alpha * uncertainty(c)
        
        This is explicitly a heuristic. It may discard candidates
        that would have scored highest after Twin simulation.
        
        Guarantees:
            - ALWAYS include "do nothing + buffer" baseline
            - ALWAYS include at least one candidate per assigned domain
        
        Maximum output: max_simulation_branches + 1 (baseline)

STEP 9: COMBINATION SYNTHESIS (if warranted)
    Generate up to max_combined_actions composite candidates.
    ONLY for non-conflicting candidates from different domains.
    Conflict check uses ActionRegistryEntry.primary_domain.

OUTPUT: Normalized candidate set ready for Twin simulation.
```

---

## 27. Improvement and Future Enhancement Backlog

> [!IMPORTANT]
> These items are validated architectural observations from the Amendment 3 review. They are NOT required for V2 to demonstrate its central thesis. They are listed here for future reference, NOT embedded in the architecture.

### 27.1 High-Priority Improvements (Consider for V2.1)

| # | Item | Source | Description |
| :--- | :--- | :--- | :--- |
| I-1 | Coverage-aware budget selection | Review Point 12/13 | Mandatory candidate reservations per domain, per policy-critical class, max per-agent caps |
| I-2 | Grouped leakage control | Review Point 56 | Group-aware train/eval splitting by supplier, SKU, facility, scenario family |
| I-3 | Action outcome selection bias control | Review Point 32 | Exposure count, selection rate, scenario difficulty for R_i computation |
| I-4 | Retrieval artifact snapshot binding | Review Point 46 | snapshot_id, corpus_version, index_version in retrieval artifacts |
| I-5 | Resource-level concurrent session detection | Review Point 47 | Resource overlap, capability overlap, constraint overlap |

### 27.2 Medium-Priority Improvements (Consider for V2.2)

| # | Item | Source | Description |
| :--- | :--- | :--- | :--- |
| I-6 | Uncertainty-aware Pareto | Review Point 25 | Interval/robust Pareto analysis with prediction uncertainty |
| I-7 | R_i causal attribution | Review Point 31 | Confound-aware action outcome quality with causal inference |
| I-8 | Action-specific Twin horizons | Review Point 60 | Candidate-level simulation materiality and horizon |
| I-9 | ActionRegistryEntry versioning | Review Point 62 | Schema hash, handler version, cryptographic action definitions |
| I-10 | Replanning refinement | Review Point 39/40 | Entity/capability/failure-class-specific exclusion, policy rebinding |

### 27.3 Future Enhancements (Post-V2)

| # | Item | Source | Description |
| :--- | :--- | :--- | :--- |
| F-1 | Logarithmic/sigmoid utility | Review Point 23 | Advanced utility functions beyond linear CLIP |
| F-2 | Bitemporal evidence semantics | Review Point 68 | valid_time, transaction_time, observed_time triple |
| F-3 | Rich risk realization model | Review Point 42 | Severity, monetary loss, risk class for OutcomeObservation |
| F-4 | Power analysis for sample sizing | Review Point 55 | Formal power analysis replacing 30-scenario floor |
| F-5 | Multi-disruption B0 baselines | Review Point 52 | B0 heuristics for every disruption class |
| F-6 | Controlled component ablations | Review Point 50/51 | Component ON/OFF studies beyond the B0-B7 progression |
| F-7 | Dynamic governance class | Review Point 38 | Context-sensitive governance class assignment |
| F-8 | Full A2A delegation | Review Point N/A | Inter-agent task delegation beyond coordinator mediation |
| F-9 | Production concurrency | Review Point N/A | Multi-instance Coordinator with distributed locking |
| F-10 | Bit-exact replay | Review Point 45 | Container digest, CUDA runtime, tokenizer version capture |

---

## 28. Contract Freeze Declaration

> [!IMPORTANT]
> **SUPERSEDES Amendment 3 Section 34 (Freeze Declaration).**

### 28.1 Frozen (No Further Conceptual Redesign)

```
ALL items from Amendment 3 Section 34 "Frozen" list are RETAINED.

ADDITIONS (from Amendment 4):
- EvidenceClass registry (orthogonal to ClaimTypeRegistry)
- Unified ActionRegistry (single source of truth for all action metadata)
- Three-tier impact model (Baseline / Predictive / Counterfactual)
- Tiered criticality model (HARD_CRITICAL / DEGRADED_CRITICAL / IMPORTANT / SUPPLEMENTARY)
- Common snapshot epoch consistency model
- Full session restart on snapshot advancement (no partial restart)
- Direction-aware signed normalization
- Candidate Budget Selection (renamed from "Safe Pruning")
- Unified SimulationMaterialityThresholds
- Session state machine with explicit transition matrix
- Content-addressable policy hashing (excluding integrity metadata)
- State revalidation before execution
- Corrected B0-B7 ablation ladder (B3/B4 separation)
```

### 28.2 Tunable (Profile Defaults, Not Frozen Architecture)

```
ALL items from Amendment 3 Section 34 "Tunable" list are RETAINED.

ADDITIONS (from Amendment 4):
- Saturation policy per metric (CLIP or LOG_COMPRESS)
- Snapshot advancement limits (max_snapshot_advancements)
- Revalidation drift thresholds
- Calibration acceptance thresholds (ECE, Brier)
- Minimum sample size floor
```

---

## Summary: What This Contract Freeze Pass Changes

| # | Change | Type | Impact | Resolves |
| :--- | :--- | :--- | :--- | :--- |
| 1 | EvidenceClass registry | NEW | Separates epistemic class from proposition type | Blocker 5 |
| 2 | Fixed claim validator fail-open | FIX | Rejects nonexistent source agents | Review Point 5 |
| 3 | Unified ActionRegistry | REPLACE | Single source of truth for all action metadata | Blocker 6 |
| 4 | Removed duplicated action_type | FIX | Structurally prevents intent/type mismatch | Review Point 7 |
| 5 | Corrected ActionIntent wording | FIX | Decision parameters vs impact estimates | Review Point 8 |
| 6 | Three-tier impact model | REPLACE | Epistemic separation of fact/prediction/simulation | Review Point 9/10 |
| 7 | Tiered criticality model | REPLACE | Resolves circularity and sufficiency inconsistency | Blockers 5/6/7 |
| 8 | Common snapshot epoch | REPLACE | Eliminates invalid LSN arithmetic | Blocker 2 |
| 9 | Full session restart policy | FIX | Maintains observation boundary invariant | Review Point 18 |
| 10 | WALL_CLOCK removal + freshness fix | FIX | Resolves contradiction and post-snapshot bug | Review Points 19/20 |
| 11 | Direction-aware normalization | REPLACE | Preserves signed utility (savings vs costs) | Blocker 4 |
| 12 | Renamed budget selection | FIX | Removes "safe pruning" overclaim | Blocker 3 |
| 13 | Unified Twin materiality | REPLACE | One canonical threshold definition | Blocker 1 |
| 14 | CD2F ExecutionPolicy wording | FIX | Correct separation of concerns | Review Point 26 |
| 15 | DB constraints for events | EXTEND | Database-level sequence enforcement | Review Point 34 |
| 16 | Session state machine | REPLACE | Explicit transitions with atomicity | Review Points 35/36 |
| 17 | Policy hash fix | FIX | Removes self-referential hash | Blocker 8 |
| 18 | Corrected ablation ladder | FIX | B3/B4 separation, removed hard-coded date | Blocker 12 |
| 19 | Statistical wording corrections | FIX | "Distribution-light", "acceptance thresholds" | Review Points 54/57 |
| 20 | ActionDefinition nullability | FIX | Optional execution_capability_id for advisory | Review Point 63 |
| 21 | State revalidation before execution | NEW | Detects stale authorizations | Review Point 74 |
| 22 | Bounded replay exactness | EXTEND | Prevents overclaiming replay fidelity | Blocker 9 |
| 23 | Corrected Pareto labels | FIX | SINGLETON_FRONTIER, POLICY_WEIGHT_RESOLVED | Review Point 24 |
| 24 | Saturation policy | EXTEND | Explicit saturation behavior documentation | Review Point 22 |
| 25 | Corrected architecture diagram | REPLACE | Incorporates all Amendment 4 changes | N/A |
| 26 | Corrected candidate pipeline | REPLACE | Tier-aware pipeline with corrected wording | N/A |
| 27 | Improvement/future backlog | NEW | Scoped improvement items for post-V2 | N/A |
| 28 | Contract freeze declaration | REPLACE | Updated frozen/tunable lists | N/A |

---

> [!IMPORTANT]
> After this contract freeze pass, the architecture reaches implementation-contract readiness. All P0 blockers identified by the fourth-pass review are resolved. The vocabulary is closed (ClaimTypeRegistry, EvidenceClass, ActionRegistry). The mathematical model is corrected (direction-aware normalization, three-tier impact, proper Pareto). The state semantics are internally consistent (common epoch, full restart, post-snapshot rejection). The evaluation protocol is corrected (clean ablation ladder, non-parametric wording, acceptance thresholds). The scope is explicitly bounded (V2 Essential vs Improvement vs Future). The architecture is ready for D3 implementation.
