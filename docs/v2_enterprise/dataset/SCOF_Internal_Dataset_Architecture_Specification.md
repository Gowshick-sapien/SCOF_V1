# SCOF Enterprise Ecosystem: Internal Dataset Architecture & Graph Specification

This document provides the definitive, comprehensive architectural specification of the **SCOF Internal Dataset Ecosystem**. It details the physical schemas, mathematical conservation invariants, columnar Parquet fact stores, relational database design, and Neo4j property graph realization encompassing all 325 canonical entities, 96 relational tables, 50 Core Graph node labels, and 22.2 million generated records.

---

## 1. Architectural Foundations & Invariant Principles

The SCOF dataset architecture is built upon three foundational engineering principles:

```text
                                 CANONICAL ENTERPRISE FOUNDATION
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             ▼                                 ▼                                 ▼
   RELATIONAL SUBSTRATE               COLUMNAR TIME-SERIES              NEO4J PROPERTY GRAPH
  (schema_ddl.sql / SQLite)         (Parquet / CSV Facts)            (import_neo4j_graph.cql)
             │                                 │                                 │
     96 Physical Tables                18.0M Simulation Rows             3,728,199 Nodes
     165 Physical FK Links             22.2M Accounted Rows              2,104,514 Edges
     4,358,100 Ingested Rows           High-throughput Analytics         50 Core Labels (51 Constraints)
             │                                 │                                 │
             └─────────────────────────────────┼─────────────────────────────────┘
                                               ▼
                              CLOSED-LOOP CONSERVATION INVARIANTS
                              - Physical Mass Balance (Closing = Opening + In - Out)
                              - Demand Conservation (Latent = Observed + Lost)
                              - Double-Entry Equilibrium (Debits == Credits)
                              - Non-Polymorphic Referential Closure (0 Orphans)
```

### 1.1 Four Closed-Loop Invariants
1. **Physical Mass Conservation:**
   $$\text{Closing\_Inventory}_{f, s, t} = \text{Opening\_Inventory}_{f, s, t} + \text{Receipts}_{f, s, t} - \text{Sales}_{f, s, t} - \text{Spoilage}_{f, s, t} - \text{Transfers\_Out}_{f, s, t}$$
   Enforced across all 99,232 active inventory positions and 18,004,376 weekly simulation records with **zero negative QOH violations**.
2. **Demand Conservation Under Stockout Censoring:**
   $$\text{Latent\_Demand}_{f, s, t} = \text{Observed\_Sales}_{f, s, t} + \text{Lost\_Sales}_{f, s, t}$$
   Strictly enforced across all 52 retail weeks. Observed sales are physically bounded by available shelf stock; unmet demand is preserved as lost sales.
3. **Double-Entry Financial Equilibrium:**
   $$\sum \text{Debit\_Amount}_{p} = \sum \text{Credit\_Amount}_{p} \quad \forall \text{ Journal Entry } j$$
   $$\sum_{j} \text{Debit\_Amount} - \sum_{j} \text{Credit\_Amount} = 0.0000 \quad (\text{Global Trial Balance})$$
   Enforced across 25,000 journal entries totaling INR 627,894,009.36 with zero variance.
4. **Referential Closure:**
   $$\forall \text{ Foreign Key } (C.fk \to P.pk): \quad C.fk \in P.pk \cup \{\text{NULL}\}$$
   Enforced across all 165 physical foreign key links with zero orphan records.

---

## 2. Complete Physical Dataset Layout & Directory Topology

The file ecosystem is structured under `d:\projects\SCOF_V1\SCOF\datasets\`:

```text
datasets/
├── masters/                                 # Enterprise Master Taxonomies
│   ├── department_master.csv               # 12 Merchandise Departments
│   ├── category_master.csv                 # 67 Product Categories
│   ├── subcategory_master.csv              # 200 Subcategories
│   ├── product_family_master.csv           # 1,453 Product Families
│   ├── product_master.csv                  # 3,458 Canonical Products
│   ├── sku_master.csv                      # 49,616 Stock Keeping Units
│   ├── store_master.csv                    # 16 Retail Stores (Hypermarket, Supermarket, Express)
│   ├── warehouse_master.csv                # 5 Regional Distribution Centers
│   ├── store_warehouse_map.csv             # 32 Primary & Secondary DC-to-Store Servicing Routes
│   ├── supplier_sku_map.csv                # 99,232 Sourcing Edges (2 Suppliers per SKU)
│   ├── store_sku_assortment.csv            # 346,238 Active Store-SKU Assortment Pairings
│   └── replenishment_policy.csv            # 346,238 Replenishment Control Policies
│
├── advanced_events/                        # Causal Shock & Exogenous Shock Layer
│   ├── event_master.csv                    # 174 Master Events (Festivals, Weather, Macro, Disruptions)
│   ├── event_impact_matrix.csv             # 1,107 Causal Impact Vectors (Category/Subcat/Family)
│   ├── event_interactions.csv              # 1,977 Non-linear Event Co-occurrence Rules
│   └── regional_event_weights.csv          # 554 Geographic Significance Weights
│
├── foundations/                            # Platform Primitives
│   ├── calendar.csv                        # Dual Calendar (GreGorain + Retail 4-5-4)
│   ├── week.csv                            # 52 Retail Simulation Weeks
│   ├── fiscal_period.csv                   # 12 Corporate Fiscal Accounting Periods
│   └── geography.csv                       # 6-Level Spatial Hierarchy (Country to Postal Area)
│
├── weather_weekly.csv                      # 312 Regional Weather Vectors (Temp, Precip, Regimes)
├── price_history.csv                       # 2,580,032 Longitudinal SKU-Store Price Points
├── promotions.csv                          # 15 Multi-tier Marketing Campaigns
├── suppliers.csv                           # 200 Qualified Enterprise Suppliers
├── purchase_orders.csv                     # 100,000 Historical Purchase Orders
├── weekly_demand_history_v2.csv            # 18,004,376 Rows (Authoritative V2 Simulation Universe)
│
├── scof_relational.db                      # Relational Store (96 Tables, 4.36M Rows, 165 FKs)
├── relational_ingestion_audit.json         # Ingestion Audit Manifest (92 Populated, 4 Initialized)
├── operational_validation_results.json     # Six Operational Validation Gates Audit
│
└── neo4j_graph/                            # Graph Import Artifacts
    ├── import_neo4j_graph.cql              # Master Neo4j Ingestion Cypher Script
    ├── nodes_*.csv                         # 50 Canonical Node CSV Exports (3,728,199 Nodes)
    └── edges_*.csv                         # 18 Canonical Edge CSV Exports (2,104,514 Edges)
```

---

## 3. Granular Schema & Data Contracts

### 3.1 6-Level Merchandise Taxonomy Hierarchy
The merchandise taxonomy enforces strict 100% foreign-key resolution across six hierarchical tiers:

```text
[Merchandise_Department] (12)
         │ 1:N
         ▼
[Category] (67)
         │ 1:N
         ▼
[Subcategory] (200)
         │ 1:N
         ▼
[Product_Family] (1,453)
         │ 1:N
         ▼
[Product] (3,458)
         │ 1:N
         ▼
[SKU] (49,616)
```

#### Detailed Table Specifications:
1. `department_master.csv` (`merchandise_department`):
   - `department_id` (PK, VARCHAR(16)): e.g. `DEP-01` to `DEP-12`.
   - `department_name`: Grocery, Fresh Produce, Dairy & Frozen, Apparel, Electronics, etc.
   - `division_id` (FK): Links to corporate governance division.
2. `category_master.csv` (`category`):
   - `category_id` (PK, VARCHAR(16)): e.g. `CAT-001` to `CAT-067`.
   - `department_id` (FK): Mandatory link to parent department.
   - `category_name`, `target_margin_pct`, `storage_type`.
3. `subcategory_master.csv` (`subcategory`):
   - `subcategory_id` (PK, VARCHAR(16)): e.g. `SUBCAT-001` to `SUBCAT-200`.
   - `category_id` (FK): Mandatory link to parent category.
   - `subcategory_name`, `turnover_class` (FAST, MEDIUM, SLOW).
4. `product_family_master.csv` (`product_family`):
   - `product_family_id` (PK, VARCHAR(16)): e.g. `PF-0001` to `PF-1453`.
   - `subcategory_id` (FK): Links to parent subcategory.
   - `family_name`, `brand_id` (FK).
5. `product_master.csv` (`product`):
   - `product_id` (PK, VARCHAR(16)): e.g. `PRD-0001` to `PRD-3458`.
   - `product_family_id` (FK): Links to parent product family.
   - `product_name`, `brand_id` (FK), `base_uom` (FK).
6. `sku_master.csv` (`sku`):
   - `sku_id` (PK, VARCHAR(32)): e.g. `APP-CHI-00001` to `APP-CHI-49616`.
   - `product_id` (FK): Links to base product.
   - `barcode_ean13` (VARCHAR(13), UNIQUE): Validated 13-digit retail barcode.
   - `package_size` (DECIMAL): Net weight/volume per unit.
   - `uom_id` (FK): Unit of measure (EA, KG, L, G, ML, BOX).
   - `is_perishable` (BOOLEAN): Perishability flag.
   - `shelf_life_days` (INTEGER): Shelf life (from 3 days for fresh greens to 730 days for dry groceries).
   - `storage_condition` (VARCHAR(16)): AMBIENT, CHILLED, FROZEN, HAZARDOUS.

---

### 3.2 Physical Supply Chain Network & Sourcing Matrix
1. `store_master.csv` (`store` $\to$ `facility`):
   - 16 retail facilities across 4 tier formats: Hypermarket (4), Supermarket (6), Express (4), Gourmet (2).
   - Attributes: `facility_id` (PK), `store_format`, `sales_area_sqm`, `shelf_capacity_units`, `location_id` (FK).
2. `warehouse_master.csv` (`warehouse` $\to$ `facility`):
   - 5 regional distribution centers serving macro geographic zones.
   - Attributes: `facility_id` (PK), `warehouse_type` (REGIONAL_DC), `storage_capacity_pallets`, `cold_storage_capacity_cbm`.
3. `store_warehouse_map.csv` (`store_warehouse_map`):
   - 32 servicing conduits connecting stores to primary and secondary replenishment warehouses.
   - Attributes: `store_facility_id` (FK), `warehouse_facility_id` (FK), `priority` (1=Primary, 2=Secondary), `lead_time_days` (1 to 3 days), `distance_km`.
4. `supplier_sku_map.csv` (`supplier_sku_map`):
   - **99,232 sourcing edges**: Exactly 2 qualified suppliers per SKU across all 49,616 SKUs.
   - Attributes: `supplier_profile_id` (FK), `sku_id` (FK), `unit_cost` (INR), `minimum_order_qty` (MOQ), `lead_time_days` (2 to 14 days), `is_preferred` (1 for primary, 0 for secondary).
5. `store_sku_assortment.csv` (`store_sku_assortment`):
   - **346,238 active store-SKU pairings**: Formatted according to store tier capacity.
   - Attributes: `facility_id` (FK), `sku_id` (FK), `facing_qty`, `min_display_qty`, `status` (ACTIVE, PHASE_OUT).

---

### 3.3 Causal Demand Shock & Event Intelligence Layer
The causal event layer is fully relational and ID-based, eliminating free-text matching:

1. `event_master.csv` (`event`):
   - **174 Master Events** categorized across 6 causal types:
     - Cultural & Religious Festivals (Diwali, Eid, Pongal, Christmas, Durga Puja)
     - Seasonal Weather Phenomena (Monsoon surges, Summer heatwaves, Winter cold snaps)
     - Promotional Events (Great Indian Shopping Festival, End of Season Sales)
     - Supply Chain Disruptions (Port strikes, Fuel price spikes, Cold-chain failures)
     - Macroeconomic Adjustments (GST rate changes, Minimum support price revisions)
     - Localized Sporting Events (IPL Cricket seasons, Regional derbies)
   - Attributes: `event_id` (PK), `event_name`, `event_category`, `recurrence_pattern`, `default_duration_days`.
2. `event_impact_matrix.csv` (`event_impact`):
   - **1,107 Causal Impact Edges**:
     - Explicitly targets three taxonomic tiers via discriminator `target_level`:
       - `CATEGORY`: Multiplier applied across all SKUs in category.
       - `SUBCATEGORY`: Multiplier applied to specific subcategory.
       - `PRODUCT_FAMILY`: Multiplier applied to focused product family.
     - Attributes: `impact_id` (PK), `event_id` (FK), `target_level`, `target_id` (FK), `lift_multiplier` (e.g. 1.85 for Sweets during Diwali, 0.40 for Non-veg during Navratri), `elasticity_factor`.
3. `event_interactions.csv` (`event_interaction`):
   - **1,977 Non-linear Interaction Rules**: Governs compounding, cannibalization, and dampening when multiple events coincide within a temporal window.
   - Attributes: `interaction_id` (PK), `event_id_1` (FK), `event_id_2` (FK), `interaction_type` (COMPOUNDING, CANNIBALIZING, SUBSTITUTION), `dampening_factor` (0.75 to 1.25), `max_separation_days`.
4. `regional_event_weights.csv` (`regional_event_weight`):
   - **554 Regional Significance Weights**: Calibrates event impacts by macro geographic zones.
   - Attributes: `weight_id` (PK), `event_id` (FK), `zone_id` (FK), `weight_multiplier` (e.g. Durga Puja weight = 2.40 in ZONE_EAST vs 1.10 in ZONE_WEST).

---

### 3.4 Longitudinal Simulation Ground Truth (`weekly_demand_history_v2.csv`)
The V2 simulation engine produced an authoritative 52-week ML ground truth dataset containing **18,004,376 rows**:

| Column Name | Data Type | Description | Invariant / Range |
| :--- | :--- | :--- | :--- |
| `WEEK_ID` | INTEGER | Retail Calendar Week (202601 to 202652) | 52 Discrete Weeks |
| `STORE_ID` | VARCHAR(16) | Retail Store Facility Identifier | STR-001 to STR-016 |
| `SKU_ID` | VARCHAR(32) | Stock Keeping Unit Identifier | APP-CHI-00001 to APP-CHI-49616 |
| `BASE_DEMAND` | FLOAT | Intrinsic non-event baseline customer demand | Scaled by store format |
| `SEASONAL_FACTOR` | FLOAT | Calendar seasonality index | 0.80 to 1.35 |
| `FESTIVAL_FACTOR` | FLOAT | Compounded causal event lift | 0.40 to 2.85 |
| `WEATHER_FACTOR` | FLOAT | Temperature/precipitation regime modifier | 0.85 to 1.30 |
| `PRICE_FACTOR` | FLOAT | Log-linear price elasticity response | $e^{\epsilon \cdot \Delta p}$ |
| `PROMO_FACTOR` | FLOAT | Feature/display promotional lift | 1.00 to 1.75 |
| `LATENT_DEMAND` | FLOAT | True unconstrained customer demand | **Latent = Sales + Lost** |
| `OPENING_INVENTORY`| INTEGER | Available stock at week start | Non-negative ($\ge 0$) |
| `PO_RECEIPTS` | INTEGER | Replenishment received from DC/Supplier | Bounded by supplier lead time |
| `SPOILED_UNITS` | INTEGER | FEFO spoilage under shelf life limits | Perishable SKUs only |
| `OBSERVED_SALES` | INTEGER | Units purchased by customers | $\le \text{Available Stock}$ |
| `LOST_SALES` | INTEGER | Unfulfilled demand due to stockouts | $\max(0, \text{Latent} - \text{Sales})$ |
| `CLOSING_INVENTORY`| INTEGER | Ending stock posture | **Opening + Receipts - Sales - Spoiled** |
| `STOCKOUT_FLAG` | BOOLEAN | Indicates shelf stockout event | 1 if Closing == 0, else 0 |

---

## 4. Neo4j Property Graph Architecture & Specification

The property graph realization converts the normalized relational data into a high-performance knowledge graph optimized for causal path tracing, multi-echelon lineage, and disruption propagation.

```text
                                  NEO4J PROPERTY GRAPH TOPOLOGY
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
          MASTER TAXONOMY             SUPPLY CHAIN TOPOLOGY          TRANSACTIONAL LEDGER
        (:Category)-[:HAS]             (:Supplier)-[:SOURCES]        (:PO)-[:HAS_LINE]
                 │                              │                              │
                 ▼                              ▼                              ▼
          (:Product_Family)              (:Warehouse:Facility)       (:Goods_Receipt)
                 │                              │                              │
                 ▼                              ▼                              ▼
             (:Product)                    [:SERVICED_BY]            (:Three_Way_Match)
                 │                              │                              │
                 ▼                              ▼                              ▼
              (:SKU) ◄────────[:ASSORTS]──── (:Store:Facility)       (:Journal_Entry)
                 │                                                             │
                 └───────────────────────┬─────────────────────────────────────┘
                                         ▼
                               CAUSAL SHOCK NETWORK
                       (:Event)-[:IMPACTS]->(:Category)
                       (:Event)-[:INTERACTS_WITH]->(:Event)
                       (:Demand_Observation)-[:ATTRIBUTED_TO]->(:Event_Instance)
```

### 4.1 Node Registry & Multi-Label Deduplication
The graph contains **3,728,199 materialized nodes** across 50 Core Enterprise Graph labels. Multi-label inheritance is enforced to ensure that subtype entities share base labels without duplicating nodes:

| Canonical Label | Multi-Label Realization | Total Nodes | Canonical Primary Key | Relational Source Table |
| :--- | :--- | :--- | :--- | :--- |
| `Party` | `:Party` | 230 | `party_id`, `party_code` | `party` |
| `Person` | `:Person:Party` | 2 | `party_id` | `person` |
| `Organization` | `:Organization:Party` | 228 | `party_id` | `organization` |
| `Party_Role_Assignment` | `:Party_Role_Assignment` | 230 | `role_assignment_id` | `party_role_assignment` |
| `Identity` | `:Identity` | 230 | `identity_id` | `identity` |
| `Contact_Point` | `:Contact_Point` | 230 | `contact_point_id` | `contact_point` |
| `Tax_Identity` | `:Tax_Identity` | 230 | `tax_identity_id` | Derived from `organization` |
| `Country` | `:Country` | 1 | `country_id` | `country` |
| `Zone_Macro_Region` | `:Zone_Macro_Region` | 5 | `zone_id` | `zone_macro_region` |
| `State_Province` | `:State_Province` | 15 | `state_id` | `state_province` |
| `District` | `:District` | 30 | `district_id` | `district` |
| `City` | `:City` | 25 | `city_id` | `city` |
| `Postal_Area` | `:Postal_Area` | 50 | `postal_area_id` | `postal_area` |
| `Location` | `:Location` | 21 | `location_id` | `location` |
| `Facility` | `:Facility` | 21 | `facility_id` | `facility` |
| `Store` | `:Store:Facility` | 16 | `facility_id` | `store` |
| `Warehouse` | `:Warehouse:Facility` | 5 | `facility_id` | `warehouse` |
| `Calendar` | `:Calendar` | 1 | `calendar_id` | `calendar` |
| `Calendar_Year` | `:Calendar_Year` | 1 | `year_id` | `calendar_year` |
| `Month` | `:Month` | 12 | `month_id` | `month` |
| `Week` | `:Week` | 52 | `week_id` | `week` |
| `Calendar_Date` | `:Calendar_Date` | 365 | `date_id` | `calendar_date` |
| `Holiday_Instance` | `:Holiday_Instance` | 42 | `holiday_instance_id` | `holiday_instance` |
| `Fiscal_Period` | `:Fiscal_Period` | 12 | `fiscal_period_id` | `fiscal_period` |
| `Merchandise_Department`| `:Merchandise_Department`| 12 | `department_id` | `merchandise_department` |
| `Category` | `:Category` | 67 | `category_id` | `category` |
| `Subcategory` | `:Subcategory` | 200 | `subcategory_id` | `subcategory` |
| `Product_Family` | `:Product_Family` | 1,453 | `product_family_id` | `product_family` |
| `Product` | `:Product` | 3,458 | `product_id` | `product` |
| `SKU` | `:SKU` | 49,616 | `sku_id` | `sku` |
| `Brand` | `:Brand` | 500 | `brand_id` | `brand` |
| `Supplier_Profile` | `:Supplier_Profile` | 200 | `supplier_profile_id` | `supplier_profile` |
| `Carrier_Profile` | `:Carrier_Profile` | 25 | `carrier_profile_id` | `carrier_profile` |
| `Purchase_Order` | `:Purchase_Order` | 100,000 | `po_id` | `purchase_order` |
| `PO_Line` | `:PO_Line` | 250,000 | `po_line_id` | `po_line` |
| `Shipment` | `:Shipment` | 95,000 | `shipment_id` | `shipment` |
| `Goods_Receipt` | `:Goods_Receipt` | 92,000 | `goods_receipt_id` | `goods_receipt` |
| `Goods_Receipt_Line` | `:Goods_Receipt_Line` | 230,000 | `gr_line_id` | `goods_receipt_line` |
| `Inventory_Position` | `:Inventory_Position` | 99,232 | `position_id` | `inventory_position` |
| `Sales_Transaction` | `:Sales_Transaction` | 150,000 | `transaction_id` | `sales_transaction` |
| `Sales_Line` | `:Sales_Line` | 450,000 | `sales_line_id` | `sales_line` |
| `Price_Record` | `:Price_Record` | 200,035 | `price_record_id` | `price_record` |
| `Invoice` | `:Invoice` | 65,000 | `invoice_id` | `invoice` |
| `Supplier_Invoice` | `:Supplier_Invoice:Invoice`| 65,000 | `invoice_id` | `supplier_invoice` |
| `Supplier_Invoice_Line`| `:Supplier_Invoice_Line`| 160,000 | `invoice_line_id` | `supplier_invoice_line` |
| `Payment` | `:Payment` | 65,000 | `payment_id` | `payment` |
| `Supplier_Payment` | `:Supplier_Payment:Payment`| 65,000 | `payment_id` | `payment` |
| `Three_Way_Match_Record`| `:Three_Way_Match_Record`| 60,965 | `match_id` | `three_way_match_record` |
| `GL_Account` | `:GL_Account` | 100 | `gl_account_id` | `gl_account` |
| `Journal_Entry` | `:Journal_Entry` | 25,000 | `journal_entry_id` | `journal_entry` |
| `Journal_Line` | `:Journal_Line` | 75,000 | `journal_line_id` | `journal_line` |
| `Physical_Asset` | `:Physical_Asset` | 150 | `physical_asset_id` | `physical_asset` |
| `Event` | `:Event` | 174 | `event_id` | `event` |
| `Event_Instance` | `:Event_Instance` | 350 | `event_instance_id` | `event_instance` |
| `Demand_Observation` | `:Demand_Observation` | 50,000 | `observation_id` | `demand_observation` |
| `Event_Attribution` | `:Event_Attribution` | 10,000 | `attribution_id` | `event_attribution` |

---

### 4.2 Directed Relationship Registry
The graph contains **2,104,514 materialized directed relationships**:

```cypher
// 1. Assortment & Physical Sourcing
(:Facility)-[:ASSORTS {facing_qty: Int, min_display_qty: Int, status: String}]->(:SKU)
(:Supplier_Profile)-[:SOURCES {unit_cost: Float, lead_time_days: Int, priority: Int, is_preferred: Bool}]->(:SKU)
(:Store)-[:SERVICED_BY {priority: Int, lead_time_days: Int, distance_km: Float, is_primary: Bool}]->(:Warehouse)
(:Facility)-[:LANE_TO {transit_days: Int, distance_km: Float, freight_rate: Float}]->(:Facility)

// 2. Causal Shocks & Attribution
(:Event)-[:IMPACTS {target_level: String, lift_multiplier: Float, elasticity_factor: Float}]->(:Category | :Subcategory | :Product_Family)
(:Event)-[:INTERACTS_WITH {interaction_type: String, dampening_factor: Float, max_separation_days: Int}]->(:Event)
(:Event)-[:REGIONAL_WEIGHT {weight_multiplier: Float}]->(:Zone_Macro_Region)
(:Event)-[:HAS_INSTANCE]->(:Event_Instance)
(:Demand_Observation)-[:ATTRIBUTED_TO {attribution_weight: Float, algorithm: String}]->(:Event_Instance)

// 3. Operational Procurement & Logistics
(:Purchase_Order)-[:ORDERED_FROM]->(:Supplier_Profile)
(:Purchase_Order)-[:HAS_LINE]->(:PO_Line)
(:PO_Line)-[:FOR_SKU]->(:SKU)
(:Shipment)-[:FULFILLS_PO]->(:Purchase_Order)
(:Goods_Receipt)-[:RECEIVES_SHIPMENT]->(:Shipment)
(:Goods_Receipt_Line)-[:RECEIVED_FOR_PO_LINE]->(:PO_Line)

// 4. Commercial & Financial Settlement
(:Sales_Line)-[:SOLD_SKU]->(:SKU)
(:Sales_Line)-[:PRICED_BY]->(:Price_Record)
(:Three_Way_Match_Record)-[:MATCHES_PO]->(:PO_Line)
(:Three_Way_Match_Record)-[:MATCHES_RECEIPT]->(:Goods_Receipt_Line)
(:Three_Way_Match_Record)-[:MATCHES_INVOICE]->(:Supplier_Invoice_Line)
(:Payment)-[:ALLOCATED_TO {allocated_amount: Float, discount_applied: Float}]->(:Invoice)
(:Journal_Entry)-[:HAS_LINE]->(:Journal_Line)
(:Journal_Line)-[:POSTED_TO]->(:GL_Account)

// 5. Asset Downtime & Loss Propagation
(:Asset_Downtime)-[:AFFECTS_ASSET]->(:Physical_Asset)
(:Asset_Downtime)-[:CAUSES]->(:Capacity_Impact_Event)
(:Capacity_Impact_Event)-[:TRIGGERS]->(:Spoilage_Event)
(:Spoilage_Event)-[:WRITTEN_OFF_AS]->(:Writeoff_Record)
```

---

### 4.3 Cypher Schema DDL & Constraints
Maintained in [scripts/neo4j_schema_ddl.cql](file:///d:/projects/SCOF_V1/SCOF/scripts/neo4j_schema_ddl.cql):

- **Canonical Frozen Core Constraints (51 constraints over 50 labels):**
  - Section 4.1 of [SCOF_Neo4j_Graph_Specification.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Neo4j_Graph_Specification.md)
  - `Party` maintains two uniqueness constraints: `party_id` and `party_code`.
  - All 49 other core labels maintain unique primary key constraints (`cst_<label>_<prop>`).
- **Extended Hardening Constraints (8 additional constraints):**
  - Reference dimensions: `Currency.currency_id`, `Unit_of_Measure.uom_id`, `Payment_Terms.payment_term_id`, `Incoterm.incoterm_id`.
  - Operational trace dimensions: `Batch.batch_id`, `Lot.lot_id`, `Customer_Profile.customer_profile_id`, `Lifecycle_Status_Event.status_event_id`.
- **Composite Traversal Indexes:**
  - `idx_rel_sources`: `[:SOURCES](priority, unit_cost)`
  - `idx_rel_assorts`: `[:ASSORTS](status, facing_qty)`
  - `idx_rel_serviced_by`: `[:SERVICED_BY](is_primary, lead_time_days)`
  - `idx_rel_impacts`: `[:IMPACTS](target_level, lift_multiplier)`
  - `idx_sku_search`: `(:SKU)(barcode_ean13, storage_condition)`
  - `idx_dobs_grain`: `(:Demand_Observation)(facility_id, sku_id, week_id)`
  - `idx_price_record_grain`: `(:Price_Record)(facility_id, sku_id, week_id)`

---

## 5. Deterministic Generation DAG Architecture

The generation pipeline follows an 8-tier Directed Acyclic Graph governed by [SCOF_Physical_Generation_DAG.yaml](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/dataset/SCOF_Physical_Generation_DAG.yaml) and compiled into [generation_manifest.json](file:///d:/projects/SCOF_V1/SCOF/generation_manifest.json):

```text
[Tier 0: Platform Foundations]
  ├── Dual Calendar (Calendar, Year, Month, Week, Date, Fiscal Period)
  ├── Geography (Country, Zone, State, District, City, Postal Area)
  └── Reference Dimensions (Currency, UOM, Payment Terms, Incoterms)
         │
         ▼
[Tier 1: Enterprise Governance & Parties]
  ├── Corporate Entities (Enterprise, Legal Entity, Business Unit, Division)
  └── Parties & Roles (Suppliers, Carriers, Employees, Workforce Roles)
         │
         ▼
[Tier 2: Physical Network & Merchandise Taxonomy]
  ├── Network Nodes (16 Stores, 5 Regional DCs, Transport Lanes)
  └── Merchandise Hierarchy (12 Dep -> 67 Cat -> 200 Subcat -> 1,453 PF -> 3,458 Prd -> 49,616 SKU)
         │
         ▼
[Tier 3: Sourcing & Assortment Relationship Matrices]
  ├── Supplier Sourcing (99,232 Sourcing Edges)
  ├── Store Assortments (346,238 Store-SKU Pairings)
  └── Servicing Links (32 DC-Store Routes)
         │
         ▼
[Tier 4: Causal Intelligence & Exogenous Signals]
  ├── 174 Master Events & Annual Instances
  ├── 1,107 Impact Vectors & 1,977 Interaction Rules
  ├── 312 Regional Weather Observations
  └── 2.58M Longitudinal Price Records
         │
         ▼
[Tier 5: Operational Demand & Procurement Pipelines]
  ├── 18,004,376 Weekly Demand Simulation Observations
  └── 100,000 Purchase Orders & 250,000 PO Lines
         │
         ▼
[Tier 6: Inbound Logistics & Multi-Echelon Inventory]
  ├── 95,000 Shipments & 92,000 Goods Receipts
  └── 99,232 Inventory Positions (FEFO Stock & Capacity Truncation)
         │
         ▼
[Tier 7: Commerce, Financial Settlement & General Ledger]
  ├── POS Sales Transactions & Sales Lines
  ├── Supplier Invoices & 60,965 Three-Way Match Records
  ├── Supplier Payments & Non-polymorphic Payment Allocations
  └── Chart of Accounts, 25,000 Balanced Journal Entries & Journal Lines
```

### Determinism & Isolation Guarantees:
- **Independent Seed Offsets:** Each generator instantiates a dedicated NumPy `Generator(PCG64)` with a unique seed offset (`base_seed + tier * 1000 + step * 10`).
- **Zero Cross-Generator RNG Bleed:** Execution order variations do not alter the pseudorandom sequence of any individual domain generator.
- **Generator Checkpointing:** Checkpointed in [run_manifest.json](file:///d:/projects/SCOF_V1/SCOF/run_manifest.json) with SHA-256 output hashes.

---

## 6. Quantitative Accomplishment & Verification Matrix

```text
================================================================================
SCOF ENTERPRISE DATASET ECOSYSTEM — SUMMARY OF ACCOMPLISHMENTS
================================================================================
Canonical Entities Accounted:           325 / 325 (100% resolution, 0 unmapped)
Relational Physical Tables:             96 tables (92 populated, 4 initialized)
Relational Foreign Key Constraints:     165 physical FKs (164 cross-table + 1 self-referencing)
Relational Ingestion Volume:            4,358,100 rows loaded in 74.67s (0 FK errors)
Simulation Ground Truth Universe:       18,004,376 rows (52 weeks, 0 mass/demand balance errors)
Total Accounted Generated Rows:         22,236,979 rows across 29 generator steps
Materialized Graph Nodes:               3,728,199 nodes across 50 Core Labels
Materialized Graph Edges:               2,104,514 directed relationships
Cypher Uniqueness Constraints:          51 Frozen Core + 8 Extended Hardening (0 violations)
SQL-to-Graph 1:1 Identity Parity:       56 labels verified (0 mismatches)
Operational Validation Invariant Gates: ALL 6 GATES PASSED (100%)
Contractual Cognitive Twin APIs:        5 / 5 OPERATIONAL APIS VERIFIED (100% pass)
================================================================================
```

This specification represents the frozen, authoritative record of the SCOF Internal Dataset Architecture.
