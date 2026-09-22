# SCOF Enterprise Ecosystem: Neo4j Property Graph Model Specification (Stage 5)

## 1. Architectural Mission & Graph Design Principles

This document establishes the **authoritative Neo4j Property Graph Model Specification** for the SCOF Enterprise Ecosystem. It translates the relational ERD ([SCOF_Canonical_ERD.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Canonical_ERD.md)), the closed entity inventory ([SCOF_Enterprise_Domain_and_Node_Registry.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Enterprise_Domain_and_Node_Registry.md)), and the relationship network ([SCOF_Enterprise_Relationship_Registry.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Enterprise_Relationship_Registry.md)) into an optimized, graph-native operational digital twin.

### 1.1 Core Graph Engineering Standards
1. **Multi-Label Hierarchy:** Nodes leverage Neo4j multi-label capabilities to capture generalization and specialization (e.g., `:Store:Facility`, `:Warehouse:Facility`, `:Organization:Party`, `:Person:Party`).
2. **Rich Directed Relationships:** Relational junction tables without independent lifecycles are converted into directed edges with properties (e.g., `[:ASSORTS]`, `[:SOURCES]`, `[:SERVICED_BY]`, `[:LANE_TO]`, `[:IMPACTS]`, `[:ALLOCATED_TO]`).
3. **First-Class Auditable Nodes:** Relational associative entities with independent operational lifecycles remain first-class graph nodes (e.g., `:Party_Role_Assignment`, `:Three_Way_Match_Record`).
4. **Index-Backed Traversal:** All primary keys and critical traversal properties are backed by Cypher uniqueness constraints and composite indexes.
5. **Causal Non-Contamination:** The graph structure enforces the synthetic causal mechanism (`(:Event)-[:IMPACTS]->(:Category)` and `(:Demand_Observation)-[:ATTRIBUTED_TO]->(:Event_Instance)`), strictly forbidding direct synthetic event-to-sales transaction bypass edges.

---

## 2. Neo4j Node Label Taxonomy & Property Schemas

### 2.1 Foundational Platform Nodes

```mermaid
graph TD
    subgraph PARTY MULTI-LABELS
        P_BASE[":Party"]
        P_PER[":Person:Party"]
        P_ORG[":Organization:Party"]
        P_BASE --> P_PER
        P_BASE --> P_ORG
    end

    subgraph FACILITY MULTI-LABELS
        F_BASE[":Facility"]
        F_STR[":Store:Facility"]
        F_WH[":Warehouse:Facility"]
        F_PLANT[":Production_Site:Facility"]
        F_OFF[":Office:Facility"]
        F_BASE --> F_STR
        F_BASE --> F_WH
        F_BASE --> F_PLANT
        F_BASE --> F_OFF
    end
```

#### Node Label Specifications:
- **`:Party`**
  - Concrete Labels: `:Person:Party`, `:Organization:Party`
  - Properties: `party_id (String, UUID)`, `party_code (String)`, `party_type (String)`, `legal_name (String)`, `trade_name (String)`, `status (String)`, `created_at (ZonedDateTime)`
- **`:Facility`**
  - Concrete Labels: `:Store:Facility`, `:Warehouse:Facility`, `:Production_Site:Facility`, `:Office:Facility`
  - Properties: `facility_id (String)`, `facility_name (String)`, `facility_category (String)`, `total_area_sqft (Float)`, `operating_status (String)`, `opened_date (Date)`
  - Subtype Specific Properties:
    - `:Store`: `store_format (String)`, `retail_selling_area_sqft (Float)`
    - `:Warehouse`: `facility_type (String: CENTRAL_DC, REGIONAL_DC, FULFILLMENT_CENTER, STORAGE_WAREHOUSE, CROSS_DOCK)`, `storage_capacity_pallets (Integer)`
    - `:Production_Site`: `plant_type (String)`
    - `:Office`: `office_type (String)`
- **`:Location`**
  - Properties: `location_id (String, UUID)`, `latitude (Float)`, `longitude (Float)`, `geohash (String)`, `altitude_meters (Float)`
- **`:Calendar_Date`**
  - Properties: `date_id (Date)`, `date_key (Integer)`, `day_of_week (Integer)`, `day_name (String)`, `is_weekend (Boolean)`, `is_business_day (Boolean)`
- **`:Week`**
  - Properties: `week_id (Integer)`, `year_id (Integer)`, `week_number (Integer)`, `start_date (Date)`, `end_date (Date)`, `retail_quarter (Integer)`
- **`:Fiscal_Period`**
  - Properties: `fiscal_period_id (String)`, `fiscal_year_id (String)`, `fiscal_quarter_id (String)`, `period_number (Integer)`, `period_status (String)`

---

### 2.2 Core Business Nodes

- **`:SKU`**
  - Properties: `sku_id (String)`, `product_id (Integer)`, `barcode_ean13 (String)`, `uom_id (String)`, `package_size (String)`, `net_weight_kg (Float)`, `shelf_life_days (Integer)`, `is_perishable (Boolean)`, `storage_condition (String)`
- **`:Product`**
  - Properties: `product_id (Integer)`, `product_name (String)`, `product_family_id (Integer)`, `brand_id (String)`
- **`:Product_Family`**
  - Properties: `product_family_id (Integer)`, `family_name (String)`, `subcategory_id (Integer)`, `demand_elasticity_class (String)`
- **`:Subcategory`**
  - Properties: `subcategory_id (Integer)`, `subcategory_name (String)`, `category_id (Integer)`
- **`:Category`**
  - Properties: `category_id (Integer)`, `category_name (String)`, `department_id (Integer)`
- **`:Merchandise_Department`**
  - Properties: `department_id (Integer)`, `department_name (String)`
- **`:Supplier_Profile`**
  - Properties: `supplier_profile_id (String, UUID)`, `party_id (String, UUID)`, `vendor_tier (String)`, `payment_term_id (String)`, `status (String)`
- **`:Carrier_Profile`**
  - Properties: `carrier_profile_id (String, UUID)`, `party_id (String, UUID)`, `fleet_type (String)`, `scac_code (String)`, `status (String)`
- **`:Customer_Profile`**
  - Properties: `customer_profile_id (String, UUID)`, `party_id (String, UUID)`, `customer_segment_id (String)`, `customer_status (String)`
- **`:Purchase_Order`**
  - Properties: `po_id (String)`, `supplier_profile_id (String, UUID)`, `destination_facility_id (String)`, `order_date (Date)`, `total_amount (Float)`, `po_status (String)`
- **`:PO_Line`**
  - Properties: `po_line_id (String)`, `po_id (String)`, `line_number (Integer)`, `sku_id (String)`, `ordered_qty (Integer)`, `unit_price (Float)`, `line_total (Float)`
- **`:Goods_Receipt`**
  - Properties: `goods_receipt_id (String)`, `po_id (String)`, `receiving_facility_id (String)`, `receipt_timestamp (ZonedDateTime)`
- **`:Goods_Receipt_Line`**
  - Properties: `gr_line_id (String)`, `goods_receipt_id (String)`, `po_line_id (String)`, `sku_id (String)`, `received_qty (Integer)`, `accepted_qty (Integer)`, `rejected_qty (Integer)`
- **`:Shipment`**
  - Properties: `shipment_id (String)`, `origin_facility_id (String)`, `destination_facility_id (String)`, `carrier_profile_id (String, UUID)`, `departure_time (ZonedDateTime)`, `actual_arrival_time (ZonedDateTime)`, `shipment_status (String)`
- **`:Sales_Transaction`**
  - Properties: `transaction_id (String)`, `facility_id (String)`, `channel_id (String)`, `transaction_timestamp (ZonedDateTime)`, `total_net_amount (Float)`, `total_tax_amount (Float)`, `total_gross_amount (Float)`
- **`:Sales_Line`**
  - Properties: `sales_line_id (String)`, `transaction_id (String)`, `line_number (Integer)`, `sku_id (String)`, `quantity (Integer)`, `unit_price (Float)`, `net_line_total (Float)`
- **`:Invoice`**
  - Concrete Labels: `:Customer_Invoice:Invoice`, `:Supplier_Invoice:Invoice`, `:Carrier_Invoice:Invoice`
  - Properties: `invoice_id (String)`, `invoice_type (String)`, `invoice_number (String)`, `party_id (String, UUID)`, `invoice_date (Date)`, `total_amount (Float)`, `balance_outstanding (Float)`, `invoice_status (String)`
- **`:Supplier_Invoice_Line`**
  - Properties: `invoice_line_id (String)`, `invoice_id (String)`, `po_line_id (String)`, `sku_id (String)`, `invoiced_qty (Integer)`, `unit_price (Float)`, `line_total (Float)`, `tax_amount (Float)`
- **`:Payment`**
  - Concrete Labels: `:Customer_Payment:Payment`, `:Supplier_Payment:Payment`, `:Carrier_Payment:Payment`
  - Properties: `payment_id (String)`, `payment_type (String)`, `payment_date (Date)`, `amount (Float)`, `payment_status (String)`
- **`:Inventory_Position`**
  - Properties: `position_id (String, UUID)`, `facility_id (String)`, `sku_id (String)`, `lot_id (String)`, `quantity_on_hand (Integer)`, `quantity_reserved (Integer)`, `quantity_available (Integer)`, `quantity_damaged (Integer)`, `quantity_expired (Integer)`
- **`:Event`**
  - Properties: `event_id (String)`, `event_name (String)`, `event_type (String)`, `baseline_duration_days (Integer)`
- **`:Event_Instance`**
  - Properties: `event_instance_id (String)`, `event_id (String)`, `year_id (Integer)`, `start_date (Date)`, `end_date (Date)`, `intensity_score (Float)`
- **`:Demand_Observation`**
  - Properties: `observation_id (String, UUID)`, `sku_id (String)`, `facility_id (String)`, `week_id (Integer)`, `latent_demand (Float)`, `observed_sales (Float)`, `lost_sales (Float)`, `inventory_available (Integer)`, `service_level_pct (Float)`
- **`:Physical_Asset`**
  - Concrete Labels: `:Refrigeration_Unit:Physical_Asset`, `:Equipment:Physical_Asset`
  - Properties: `physical_asset_id (String)`, `facility_id (String)`, `category_id (String)`, `asset_tag (String)`, `make (String)`, `model (String)`, `status (String)`
- **`:Work_Order`**
  - Properties: `work_order_id (String)`, `work_order_type (String: PRODUCTION, MAINTENANCE)`, `facility_id (String)`, `priority (String)`, `work_order_status (String)`

---

## 3. Directed Relationships with Property Schemas

### 3.1 Network & Sourcing Relationships
```cypher
// Sourcing Link: Supplier supplies SKU
(:Supplier_Profile)-[:SOURCES {
    unit_cost: Float,
    minimum_order_qty: Integer,
    lead_time_days: Integer,
    supplier_priority: Integer,
    is_preferred: Boolean
}]->(:SKU)

// Store Assortment: Store stocks SKU
(:Store)-[:ASSORTS {
    effective_start: Date,
    effective_end: Date,
    facing_qty: Integer,
    min_display_qty: Integer,
    status: String
}]->(:SKU)

// Servicing Link: Warehouse supplies Store
(:Store)-[:SERVICED_BY {
    priority: Integer,
    lead_time_days: Integer,
    distance_km: Float,
    is_primary: Boolean
}]->(:Warehouse)

// Transportation Conduit
(:Facility)-[:LANE_TO {
    lane_id: String,
    transit_days: Integer,
    distance_km: Float,
    freight_rate: Float,
    is_active: Boolean
}]->(:Facility)
```

---

### 3.2 Demand Shocks & Causal Attribution Relationships
```cypher
// Master Event Definition spawns Annual Instance
(:Event)-[:HAS_INSTANCE]->(:Event_Instance)

// Causal Shock Vector: Event impacts Category/Subcategory/Product_Family
(:Event)-[:IMPACTS {
    target_level: String, // 'CATEGORY', 'SUBCATEGORY', or 'PRODUCT_FAMILY'
    lift_multiplier: Float,
    elasticity_factor: Float
}]->(:Category | :Subcategory | :Product_Family)

// Event Interaction: Co-occurrence interaction rule
(:Event)-[:INTERACTS_WITH {
    interaction_type: String, // 'COMPOUNDING', 'CANNIBALIZING', or 'SUBSTITUTION'
    dampening_factor: Float,
    max_separation_days: Integer
}]->(:Event)

// Geographic Cultural Modifier
(:Event)-[:REGIONAL_WEIGHT {
    weight_multiplier: Float,
    cultural_significance_tier: String
}]->(:Zone_Macro_Region)

// Causal Demand Attribution (Derived Analytics)
(:Demand_Observation)-[:ATTRIBUTED_TO {
    attribution_weight: Float,
    algorithm_version: String
}]->(:Event_Instance)
```

---

### 3.3 Commercial, Financial & Asset Relationships
```cypher
// Sales Pricing Link
(:Sales_Line)-[:PRICED_BY]->(:Price_Record)

// Non-Polymorphic Payment Allocation
(:Payment)-[:ALLOCATED_TO {
    allocation_id: String,
    allocated_amount: Float,
    discount_applied: Float,
    allocation_date: Date
}]->(:Invoice)

// Three-Way Match Reconciliation
(:Three_Way_Match_Record)-[:MATCHES_PO]->(:PO_Line)
(:Three_Way_Match_Record)-[:MATCHES_RECEIPT]->(:Goods_Receipt_Line)
(:Three_Way_Match_Record)-[:MATCHES_INVOICE]->(:Supplier_Invoice_Line)

// Asset Downtime and Loss Propagation
(:Asset_Downtime)-[:AFFECTS_ASSET]->(:Physical_Asset)
(:Asset_Downtime)-[:CAUSES]->(:Capacity_Impact_Event)
(:Capacity_Impact_Event)-[:TRIGGERS]->(:Spoilage_Event)
(:Spoilage_Event)-[:WRITTEN_OFF_AS]->(:Writeoff_Record)
```

---

## 4. Production Cypher Constraints & Indexes

The production schema declarations are maintained in `scripts/neo4j_schema_ddl.cql`.

### 4.1 Node Uniqueness Constraints: Core Enterprise Graph Inclusion Set (Option A Formalization)
The Neo4j property graph model explicitly indexes and constrains all primary operational, master, transactional, and causal nodes that participate in active graph traversals, path lineages, and pattern queries (the Core Enterprise Graph Inclusion Set, under Option A). Exactly 51 Cypher uniqueness constraints are declared, covering 50 Core Enterprise Graph node labels (Party maintains two uniqueness constraints: `party_id` and `party_code`), while the broader 240+ entity relational catalog is fully enforced at the relational layer (`schema_ddl.sql`). Complete production declarations are maintained in `scripts/neo4j_schema_ddl.cql`.

```cypher
// Party & Identity
CREATE CONSTRAINT cst_party_id IF NOT EXISTS FOR (p:Party) REQUIRE p.party_id IS UNIQUE;
CREATE CONSTRAINT cst_party_code IF NOT EXISTS FOR (p:Party) REQUIRE p.party_code IS UNIQUE;
CREATE CONSTRAINT cst_role_assignment_id IF NOT EXISTS FOR (pra:Party_Role_Assignment) REQUIRE pra.role_assignment_id IS UNIQUE;
CREATE CONSTRAINT cst_identity_id IF NOT EXISTS FOR (i:Identity) REQUIRE i.identity_id IS UNIQUE;
CREATE CONSTRAINT cst_contact_point_id IF NOT EXISTS FOR (c:Contact_Point) REQUIRE c.contact_point_id IS UNIQUE;
CREATE CONSTRAINT cst_tax_identity_id IF NOT EXISTS FOR (t:Tax_Identity) REQUIRE t.tax_identity_id IS UNIQUE;

// Geography & Facilities (Foundation B Hierarchy)
CREATE CONSTRAINT cst_country_id IF NOT EXISTS FOR (c:Country) REQUIRE c.country_id IS UNIQUE;
CREATE CONSTRAINT cst_zone_id IF NOT EXISTS FOR (z:Zone_Macro_Region) REQUIRE z.zone_id IS UNIQUE;
CREATE CONSTRAINT cst_state_id IF NOT EXISTS FOR (s:State_Province) REQUIRE s.state_id IS UNIQUE;
CREATE CONSTRAINT cst_district_id IF NOT EXISTS FOR (d:District) REQUIRE d.district_id IS UNIQUE;
CREATE CONSTRAINT cst_city_id IF NOT EXISTS FOR (cty:City) REQUIRE cty.city_id IS UNIQUE;
CREATE CONSTRAINT cst_postal_area_id IF NOT EXISTS FOR (pa:Postal_Area) REQUIRE pa.postal_area_id IS UNIQUE;
CREATE CONSTRAINT cst_facility_id IF NOT EXISTS FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;
CREATE CONSTRAINT cst_location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE;

// Time & Dual Calendar (Foundation C)
CREATE CONSTRAINT cst_calendar_id IF NOT EXISTS FOR (c:Calendar) REQUIRE c.calendar_id IS UNIQUE;
CREATE CONSTRAINT cst_year_id IF NOT EXISTS FOR (y:Calendar_Year) REQUIRE y.year_id IS UNIQUE;
CREATE CONSTRAINT cst_month_id IF NOT EXISTS FOR (m:Month) REQUIRE m.month_id IS UNIQUE;
CREATE CONSTRAINT cst_week_id IF NOT EXISTS FOR (w:Week) REQUIRE w.week_id IS UNIQUE;
CREATE CONSTRAINT cst_date_id IF NOT EXISTS FOR (d:Calendar_Date) REQUIRE d.date_id IS UNIQUE;
CREATE CONSTRAINT cst_holiday_id IF NOT EXISTS FOR (h:Holiday_Instance) REQUIRE h.holiday_instance_id IS UNIQUE;
CREATE CONSTRAINT cst_fiscal_period_id IF NOT EXISTS FOR (fp:Fiscal_Period) REQUIRE fp.fiscal_period_id IS UNIQUE;

// Merchandise Hierarchy (6 Levels + Product_Family)
CREATE CONSTRAINT cst_sku_id IF NOT EXISTS FOR (s:SKU) REQUIRE s.sku_id IS UNIQUE;
CREATE CONSTRAINT cst_product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE;
CREATE CONSTRAINT cst_product_family_id IF NOT EXISTS FOR (pf:Product_Family) REQUIRE pf.product_family_id IS UNIQUE;
CREATE CONSTRAINT cst_subcategory_id IF NOT EXISTS FOR (sc:Subcategory) REQUIRE sc.subcategory_id IS UNIQUE;
CREATE CONSTRAINT cst_category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.category_id IS UNIQUE;
CREATE CONSTRAINT cst_department_id IF NOT EXISTS FOR (d:Merchandise_Department) REQUIRE d.department_id IS UNIQUE;
CREATE CONSTRAINT cst_brand_id IF NOT EXISTS FOR (b:Brand) REQUIRE b.brand_id IS UNIQUE;

// Supply Chain & Operations
CREATE CONSTRAINT cst_supplier_profile_id IF NOT EXISTS FOR (sp:Supplier_Profile) REQUIRE sp.supplier_profile_id IS UNIQUE;
CREATE CONSTRAINT cst_carrier_profile_id IF NOT EXISTS FOR (cp:Carrier_Profile) REQUIRE cp.carrier_profile_id IS UNIQUE;
CREATE CONSTRAINT cst_po_id IF NOT EXISTS FOR (po:Purchase_Order) REQUIRE po.po_id IS UNIQUE;
CREATE CONSTRAINT cst_po_line_id IF NOT EXISTS FOR (pol:PO_Line) REQUIRE pol.po_line_id IS UNIQUE;
CREATE CONSTRAINT cst_shipment_id IF NOT EXISTS FOR (s:Shipment) REQUIRE s.shipment_id IS UNIQUE;
CREATE CONSTRAINT cst_grn_id IF NOT EXISTS FOR (grn:Goods_Receipt) REQUIRE grn.goods_receipt_id IS UNIQUE;
CREATE CONSTRAINT cst_gr_line_id IF NOT EXISTS FOR (grl:Goods_Receipt_Line) REQUIRE grl.gr_line_id IS UNIQUE;
CREATE CONSTRAINT cst_inv_position_id IF NOT EXISTS FOR (ip:Inventory_Position) REQUIRE ip.position_id IS UNIQUE;

// Commerce & Pricing
CREATE CONSTRAINT cst_transaction_id IF NOT EXISTS FOR (st:Sales_Transaction) REQUIRE st.transaction_id IS UNIQUE;
CREATE CONSTRAINT cst_sales_line_id IF NOT EXISTS FOR (sl:Sales_Line) REQUIRE sl.sales_line_id IS UNIQUE;
CREATE CONSTRAINT cst_price_record_id IF NOT EXISTS FOR (pr:Price_Record) REQUIRE pr.price_record_id IS UNIQUE;

// Finance, Settlement & Reconciliation
CREATE CONSTRAINT cst_invoice_id IF NOT EXISTS FOR (inv:Invoice) REQUIRE inv.invoice_id IS UNIQUE;
CREATE CONSTRAINT cst_supplier_invoice_line_id IF NOT EXISTS FOR (sil:Supplier_Invoice_Line) REQUIRE sil.invoice_line_id IS UNIQUE;
CREATE CONSTRAINT cst_payment_id IF NOT EXISTS FOR (pay:Payment) REQUIRE pay.payment_id IS UNIQUE;
CREATE CONSTRAINT cst_match_id IF NOT EXISTS FOR (twm:Three_Way_Match_Record) REQUIRE twm.match_id IS UNIQUE;
CREATE CONSTRAINT cst_gl_account_id IF NOT EXISTS FOR (gla:GL_Account) REQUIRE gla.gl_account_id IS UNIQUE;
CREATE CONSTRAINT cst_journal_entry_id IF NOT EXISTS FOR (je:Journal_Entry) REQUIRE je.journal_entry_id IS UNIQUE;
CREATE CONSTRAINT cst_journal_line_id IF NOT EXISTS FOR (jl:Journal_Line) REQUIRE jl.journal_line_id IS UNIQUE;

// Assets, Downtime & Spoilage
CREATE CONSTRAINT cst_physical_asset_id IF NOT EXISTS FOR (pa:Physical_Asset) REQUIRE pa.physical_asset_id IS UNIQUE;

// Demand Intelligence & Simulation
CREATE CONSTRAINT cst_event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE;
CREATE CONSTRAINT cst_event_instance_id IF NOT EXISTS FOR (ei:Event_Instance) REQUIRE ei.event_instance_id IS UNIQUE;
CREATE CONSTRAINT cst_observation_id IF NOT EXISTS FOR (dobs:Demand_Observation) REQUIRE dobs.observation_id IS UNIQUE;
CREATE CONSTRAINT cst_attribution_id IF NOT EXISTS FOR (ea:Event_Attribution) REQUIRE ea.attribution_id IS UNIQUE;
```

---

### 4.2 Composite & Full-Text Traversal Indexes
```cypher
// Sourcing & Assortment Traversal Indexes
CREATE INDEX idx_rel_sources IF NOT EXISTS FOR ()-[r:SOURCES]-() ON (r.priority, r.unit_cost);
CREATE INDEX idx_rel_assorts IF NOT EXISTS FOR ()-[r:ASSORTS]-() ON (r.status, r.facing_qty);
CREATE INDEX idx_rel_serviced_by IF NOT EXISTS FOR ()-[r:SERVICED_BY]-() ON (r.is_primary, r.lead_time_days);

// Demand Causal & Attribution Indexes
CREATE INDEX idx_rel_impacts IF NOT EXISTS FOR ()-[r:IMPACTS]-() ON (r.target_level, r.lift_multiplier);
CREATE INDEX idx_rel_attributed IF NOT EXISTS FOR ()-[r:ATTRIBUTED_TO]-() ON (r.attribution_weight);

// Operational Node Indexes
CREATE INDEX idx_sku_search IF NOT EXISTS FOR (s:SKU) ON (s.barcode_ean13, s.storage_condition);
CREATE INDEX idx_facility_geo IF NOT EXISTS FOR (f:Facility) ON (f.facility_category, f.operating_status);
CREATE INDEX idx_dobs_grain IF NOT EXISTS FOR (d:Demand_Observation) ON (d.facility_id, d.sku_id, d.week_id);
```

---

## 5. Canonical Cypher Query Patterns for Enterprise Scenarios

### 5.1 Multi-Tier Farm-to-Store Supply Lineage
Traces the physical and commercial supply path from agricultural producer to retail store shelf:

```cypher
MATCH path = (prod:Organization:Party)-[:HAS_ROLE_ASSIGNMENT]->(pra:Party_Role_Assignment {role_type: 'PRODUCER'})
             -[:HAS_PROFILE]->(sup:Supplier_Profile)
             -[:SOURCES]->(sku:SKU)
             <-[:ASSORTS]-(str:Store:Facility)
             -[:SERVICED_BY]->(dc:Warehouse:Facility)
WHERE sku.sku_id = 'SKU-000491' AND str.facility_id = 'FAC-STR-001'
RETURN path;
```

---

### 5.2 Causal Demand Shock Propagation & Attribution (Category-Level Traversal)
Finds all SKUs impacted by Category-Level Event Impacts for Diwali 2026 in the Southern Zone and compares latent demand against observed sales (with analogous traversals applicable to Subcategory and Product_Family impact levels):

```cypher
MATCH (e:Event {event_id: 'EVT-DIWALI'})-[:HAS_INSTANCE]->(ei:Event_Instance {year_id: 2026})
MATCH (e)-[imp:IMPACTS]->(cat:Category)
MATCH (cat)-[:CONTAINS*4]->(sku:SKU)
MATCH (e)-[rw:REGIONAL_WEIGHT]->(z:Zone_Macro_Region {zone_id: 'ZONE_SOUTH'})
MATCH (str:Store:Facility)<-[:ANCHORS]-(:Location)
      -[:WITHIN_POSTAL_AREA]->(:Postal_Area)
      -[:WITHIN_CITY]->(:City)
      -[:WITHIN_DISTRICT]->(:District)
      -[:WITHIN_STATE]->(:State_Province)
      -[:WITHIN_ZONE]->(z)
// Note: In production deployments with generic spatial edge indexing, the administrative rollup can equivalently be traversed as: (:Location)-[:WITHIN*5]->(z)
MATCH (dobs:Demand_Observation {week_id: 202641, facility_id: str.facility_id, sku_id: sku.sku_id})
RETURN sku.sku_id, str.facility_id,
       imp.lift_multiplier AS category_lift,
       rw.weight_multiplier AS regional_weight,
       dobs.latent_demand AS unconstrained_demand,
       dobs.observed_sales AS realized_sales,
       dobs.lost_sales AS lost_sales
ORDER BY dobs.lost_sales DESC
LIMIT 50;
```

---

### 5.3 Cold Chain Failure, Spoilage & Financial Writeoff Lineage
Traces a refrigeration compressor failure down to perishable inventory spoilage, financial writeoff, and double-entry GL expense posting:

```cypher
MATCH (ru:Refrigeration_Unit:Physical_Asset)<-[:AFFECTS_ASSET]-(dt:Asset_Downtime)
MATCH (dt)-[:CAUSES]->(cap:Capacity_Impact_Event)-[:TRIGGERS]->(spoil:Spoilage_Event)
MATCH (spoil)-[:SPOILS_SKU]->(sku:SKU)
MATCH (spoil)-[:WRITTEN_OFF_AS]->(woff:Writeoff_Record)
MATCH (woff)-[:POSTS_TO]->(je:Journal_Entry)-[:CONTAINS]->(jl:Journal_Line)-[:POSTS_TO]->(gl:GL_Account)
WHERE ru.physical_asset_id = 'AST-CHILLER-01'
RETURN ru.asset_tag, dt.downtime_reason, cap.capacity_loss_pct,
       sku.sku_id, spoil.quantity AS spoiled_units,
       woff.writeoff_cost, gl.account_code, jl.debit_amount, jl.credit_amount;
```

---

### 5.4 Procurement Three-Way Match Audit Traversal
Identifies PO lines with price or quantity variances exceeding authorized thresholds:

```cypher
MATCH (twm:Three_Way_Match_Record)
WHERE twm.match_status IN ['PRICE_VARIANCE', 'QTY_VARIANCE', 'REJECTED']
MATCH (twm)-[:MATCHES_PO]->(pol:PO_Line)<-[:CONTAINS]-(po:Purchase_Order)
MATCH (twm)-[:MATCHES_RECEIPT]->(grl:Goods_Receipt_Line)
MATCH (twm)-[:MATCHES_INVOICE]->(sil:Supplier_Invoice_Line)<-[:CONTAINS]-(sinv:Supplier_Invoice)
MATCH (po)-[:ISSUED_TO]->(sup:Supplier_Profile)
RETURN po.po_id, pol.line_number, sup.party_id,
       pol.ordered_qty, grl.accepted_qty, sil.invoiced_qty,
       pol.unit_price, sil.unit_price AS invoiced_price,
       twm.variance_amount, twm.match_status;
```

---

## 6. Graph Model Verification & Sign-Off Checklist

| Verification Gate | Validation Criteria | Verification Outcome |
| :--- | :--- | :--- |
| **Multi-Label Specialization** | All facility and party subtypes carry primary and secondary labels (`:Store:Facility`, `:Organization:Party`). | Passed |
| **Constraint Completeness** | 51 Cypher uniqueness constraints declared covering 50 Core Enterprise Graph node labels (Party maintains two uniqueness constraints: `party_id` and `party_code`) for the Core Enterprise Graph Inclusion Set (full 240+ enterprise catalog enforced in relational DDL). | Passed |
| **Rich Directed Edges** | Associative entities (`Store_SKU_Assortment`, `Supplier_SKU_Map`, `Transport_Lane`, `Event_Impact`, `Payment_Allocation`) mapped as rich relationships with properties. | Passed |
| **First-Class Audit Nodes** | `Party_Role_Assignment` and `Three_Way_Match_Record` maintained as first-class nodes. | Passed |
| **Causal Query Traversal** | Canonical queries execute multi-tier farm-to-store, demand attribution, and asset failure lineages with zero relational join overhead against registered relationships. | Passed |

---

### Stage 5 Sign-Off Status
**Stage 5 (Neo4j Property Graph Model Specification) is COMPLETE and LOCKED.**
The executable DDL script is generated at `scripts/neo4j_schema_ddl.cql`.
Execution is ready to proceed to **Sprint 3 / Sub-Plan 3B: Stage 6 — Physical Schema Specification & Data-Generation Dependency DAG**.
