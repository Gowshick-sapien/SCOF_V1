# ADR 016: Declarative Domain Binding Profiles over Procedural World Generators

* **Status**: Accepted (Amends ADR 009)
* **Date**: 2026-09-22
* **Deciders**: SCOF Core Architecture Team
* **Consulted**: Systems Architects, Domain Engineers
* **Informed**: Engineering Organization

---

## 1. Context and Problem Statement

In ADR 009, Domain Profiles (`profiles/<profile-name>/`) were defined as declarative YAML packages that directed synthetic generators to create a specific supply chain topology (e.g., `profiles/mvp-electronics/` directed the generator to create 5 suppliers, 2 warehouses, and 5 products).

With the establishment of the frozen 30-domain Enterprise Knowledge Fabric (ADR 013), treating Domain Profiles as generator inputs is obsolete. An enterprise platform should not rebuild or re-synthesize supply chain worlds per deployment. Instead, the enterprise dataset exists as an authoritative reference world, and different operational contexts represent subsets of that world.

---

## 2. Decision Drivers

* **Decoupling Data from Generation:** Move from dynamic generation scripts to declarative runtime operational bindings.
* **Subset Operational Scoping:** Enable SCOF instances to bind to specific facilities, regions, product categories, or supplier tiers without modifying the underlying database.
* **Multi-Vertical Flexibility:** Support regional deployments (e.g., South Zone DC network) or category-specific deployments (e.g., Perishables & Cold-Chain focus) via configuration.

---

## 3. Considered Options

* **Option 1 (Retain Generator-Bound Profiles):** Continue treating profiles as generator configs that synthesize separate SQLite/PostgreSQL databases per vertical.
* **Option 2 (Single Monolithic Hardcoded Runtime):** Force all agents and services to bind to the entire 49,616 SKU enterprise dataset without subset scoping.
* **Option 3 (Declarative Domain Binding Profiles):** Redefine Domain Profiles as declarative operational bindings over the frozen enterprise dataset:
  $$\text{Enterprise Dataset} + \text{Domain Binding Profile} = \text{SCOF Runtime World}$$

---

## 4. Decision Outcome

**Chosen Option**: **Option 3: Declarative Domain Binding Profiles**

### Rationale:
The Domain Profile's responsibility fundamentally shifts:
* **Old V1 Role:** "Generate five suppliers, two warehouses, and five products."
* **New V2 Role:** "This SCOF instance binds to Enterprise Dataset v2.0, activating Regional Zone South (DCs WH-001/WH-002, Stores STR-001 through STR-004), running Demand, Inventory, Supplier, and Logistics agents under CD²F consensus."

### Profile Structure (`profiles/v2-retail-enterprise/`):
* `profile.yaml`: Top-level metadata and dataset version binding (`dataset_version: 2.0.0`).
* `topology_binding.yaml`: Declares active facilities, primary servicing warehouses, and transport lanes.
* `agents.yaml`: Declares active specialist agents, model choices (XGBoost, Prophet, Chronos-2), and MCP tool permissions.
* `consensus.yaml`: Defines CD²F thresholds (Fast-Path $WCS \ge 0.70$, severity scaling, and calibration).

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Eliminates redundant data generation; multiple SCOF profiles run cleanly against the same enterprise dataset.
* Enables realistic localized testing (e.g., evaluating a localized transit shock across a specific regional DC and its 4 stores).
* Preserves domain-agnostic architecture: platform code never hardcodes specific store IDs or supplier names.

### Negative Consequences / Trade-offs:
* Services must read the active profile's binding filters when querying baseline state.

---

## 6. Implementation & Compliance Notes

* **Reference Profile:** Implemented in `profiles/v2-retail-enterprise/`.
* **Binding Logic:** Implemented in `services/api/src/routers/profile.py` and `services/coordinator/`.
