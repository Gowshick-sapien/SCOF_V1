# SCOF Enterprise Ecosystem: Relationship Registry (Stage 2)

## 1. Architectural Mission & Graph Semantics

This document establishes the **authoritative Relationship Registry** for the SCOF Enterprise Ecosystem. It formally binds the foundational platform primitives ([SCOF_Foundational_Ontology.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Foundational_Ontology.md)) and the closed 30-domain business universe ([SCOF_Enterprise_Domain_and_Node_Registry.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/ontology/SCOF_Enterprise_Domain_and_Node_Registry.md)).

### 1.1 The Relational vs. Graph Realization Standard
To prevent the anti-pattern of turning every relational junction table into an ontological graph node:
- **Tier 3 Relationship Entities Without Independent Lifecycle:** Modeled as **junction / association tables** in relational SQL, but as **rich directed relationships with properties** in Neo4j (e.g., `Store_SKU_Assortment`, `Supplier_SKU_Map`, `Store_Warehouse_Map`, `Transport_Lane`, `Event_Impact`, `Payment_Allocation`).
- **Tier 3 Relationship Entities With Independent Lifecycle or Audit Commitment:** Modeled as **standalone tables** in SQL and as **first-class nodes** in Neo4j (e.g., `Party_Role_Assignment`, `Three_Way_Match_Record`).

### 1.2 Standardized Relationship Attributes
Every relationship documented in this registry defines:
1. `RELATIONSHIP_ID`: Unique canonical identifier (e.g., `REL_FND_001`, `REL_MER_004`).
2. `FROM_NODE`: Origin node (must exist in Stage 0A or Stage 1).
3. `RELATIONSHIP_TYPE`: Standardized uppercase verb phrase.
4. `TO_NODE`: Destination node (must exist in Stage 0A or Stage 1).
5. `CARDINALITY`: `1:1`, `1:N`, `M:N`.
6. `RELATIONSHIP_ATTRIBUTES`: Mandatory edge properties (e.g., `effective_start`, `weight`, `status`).
7. `TEMPORALITY`: `Static`, `Effective-Dated (SCD 2)`, or `Timestamped`.
8. `OPTIONALITY`: `Mandatory` (both ends must exist) vs. `Optional` (nullable foreign key).
9. `GRAPH_MODEL_DECISION`: `Neo4j Relationship with Properties` vs. `Neo4j Node`.
10. `BUSINESS_RULE`: Formal business policy governing the edge.

---

## 2. Tier 3: Cross-Domain Relationship Entities (Deep Specification)

### 2.1 Summary Matrix of Tier 3 Entities

| ENTITY_NAME | SQL REALIZATION | NEO4J REALIZATION | GRAPH TYPE / LABEL | PRIMARY KEY | CRITICAL ATTRIBUTES |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Party_Role_Assignment`** | Standalone Entity | Node | `:Party_Role_Assignment` | `role_assignment_id (UUID)` | `role_type, effective_start, effective_end, status` |
| **`Store_Warehouse_Map`** | Junction Table | Rich Relationship | `(:Store)-[:SERVICED_BY]->(:Warehouse)` | `(store_facility_id, wh_facility_id)` | `lead_time_days, priority, distance_km, is_primary` |
| **`Store_SKU_Assortment`** | Junction Table | Rich Relationship | `(:Store)-[:ASSORTS]->(:SKU)` | `(facility_id, sku_id, effective_start)` | `facing_qty, status, eye_level_flag, min_display_qty` |
| **`Supplier_SKU_Map`** | Junction Table | Rich Relationship | `(:Supplier_Profile)-[:SOURCES]->(:SKU)` | `(supplier_profile_id, sku_id)` | `unit_cost, moq, lead_time_days, priority, currency_id` |
| **`Transport_Lane`** | Association Table | Rich Relationship | `(:Facility)-[:LANE_TO]->(:Facility)` | `lane_id (VARCHAR(32))` | `transit_days, distance_km, primary_carrier_id, freight_rate` |
| **`Event_Impact`** | Association Table | Rich Relationship | `(:Event)-[:IMPACTS]->(:Category \| :Subcategory \| :Product_Family)` | `impact_id (UUID)` | `lift_multiplier, target_level, elasticity_factor` |
| **`Event_Interaction`** | Association Table | Rich Relationship | `(:Event)-[:INTERACTS_WITH]->(:Event)` | `interaction_id (UUID)` | `interaction_type, dampening_factor, min_separation_days` |
| **`Regional_Event_Weight`** | Association Table | Rich Relationship | `(:Event)-[:REGIONAL_WEIGHT]->(:Zone_Macro_Region)` | `weight_id (UUID)` | `weight_multiplier, cultural_significance_tier` |
| **`Payment_Allocation`** | Associative Transaction Table | Rich Relationship | `(:Payment)-[:ALLOCATED_TO]->(:Invoice)` | `allocation_id (UUID)` | `allocated_amount, discount_applied, allocation_date` |
| **`Three_Way_Match_Record`** | Audit Transaction | Node | `:Three_Way_Match_Record` | `match_id (UUID)` | `variance_amount, match_status, verified_timestamp` |

---

### 2.2 Deep Architectural Specification: Tier 3 Entities

#### 1. `Party_Role_Assignment`
- **Identifier:** `NOD_REL_ROLE_001`
- **Concept:** Canonical realization bridging legal parties to operational roles.
- **Relational DDL:**
  ```sql
  CREATE TABLE party_role_assignment (
      role_assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
      role_type VARCHAR(32) NOT NULL CHECK (role_type IN (
          'CUSTOMER', 'SUPPLIER', 'MANUFACTURER', 'PRODUCER', 'AGGREGATOR',
          'WHOLESALER', 'DISTRIBUTOR', 'IMPORTER', 'EXPORTER', 'CARRIER',
          '3PL_PROVIDER', 'EMPLOYEE', 'DRIVER', 'MARKETPLACE_SELLER'
      )),
      effective_start_date DATE NOT NULL,
      effective_end_date DATE,
      status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      CONSTRAINT uq_party_role_effective UNIQUE (party_id, role_type, effective_start_date)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Party)-[:HAS_ROLE_ASSIGNMENT {effective_start: date('2026-01-01'), status: 'ACTIVE'}]->(:Party_Role_Assignment {role_assignment_id: 'PRA-001', role_type: 'SUPPLIER'})-[:HAS_PROFILE]->(:Supplier_Profile)
  ```

#### 2. `Store_Warehouse_Map`
- **Identifier:** `NOD_REL_SWM_001`
- **Concept:** Authoritative routing map defining which warehouse or distribution center supplies each retail store.
- **Relational DDL:**
  ```sql
  CREATE TABLE store_warehouse_map (
      store_facility_id VARCHAR(32) NOT NULL REFERENCES store(facility_id),
      warehouse_facility_id VARCHAR(32) NOT NULL REFERENCES warehouse(facility_id),
      priority INTEGER NOT NULL DEFAULT 1,
      lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 1),
      distance_km DECIMAL(8,2) NOT NULL,
      is_primary BOOLEAN NOT NULL DEFAULT TRUE,
      status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
      PRIMARY KEY (store_facility_id, warehouse_facility_id)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Store)-[:SERVICED_BY {priority: 1, lead_time_days: 2, distance_km: 142.5, is_primary: true}]->(:Warehouse)
  ```

#### 3. `Store_SKU_Assortment`
- **Identifier:** `NOD_REL_SSA_001`
- **Concept:** Active merchandise planogram assortment authorizing a store to stock and sell a specific SKU.
- **Relational DDL:**
  ```sql
  CREATE TABLE store_sku_assortment (
      facility_id VARCHAR(32) NOT NULL REFERENCES store(facility_id),
      sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id),
      effective_start_date DATE NOT NULL,
      effective_end_date DATE,
      facing_qty INTEGER NOT NULL DEFAULT 1,
      min_display_qty INTEGER NOT NULL DEFAULT 1,
      status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DISCONTINUED', 'SEASONAL_HOLD')),
      PRIMARY KEY (facility_id, sku_id, effective_start_date)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Store)-[:ASSORTS {effective_start: date('2026-01-01'), facing_qty: 2, status: 'ACTIVE'}]->(:SKU)
  ```

#### 4. `Supplier_SKU_Map`
- **Identifier:** `NOD_REL_SSM_001`
- **Concept:** Sourcing contract mapping an authorized supplier to a SKU, establishing unit procurement cost, lead times, and minimum order quantities (MOQ).
- **Relational DDL:**
  ```sql
  CREATE TABLE supplier_sku_map (
      supplier_profile_id UUID NOT NULL REFERENCES supplier_profile(supplier_profile_id),
      sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id),
      unit_cost DECIMAL(12,4) NOT NULL CHECK (unit_cost > 0),
      currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id),
      minimum_order_qty INTEGER NOT NULL DEFAULT 1 CHECK (minimum_order_qty >= 1),
      lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 1),
      supplier_priority INTEGER NOT NULL DEFAULT 1,
      is_preferred BOOLEAN NOT NULL DEFAULT TRUE,
      PRIMARY KEY (supplier_profile_id, sku_id)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Supplier_Profile)-[:SOURCES {unit_cost: 14.50, moq: 100, lead_time_days: 7, priority: 1}]->(:SKU)
  ```

#### 5. `Transport_Lane`
- **Identifier:** `NOD_REL_TLN_001`
- **Concept:** Physical transportation conduit between two enterprise facilities (Store to DC, Supplier Site to DC, Plant to DC).
- **Relational DDL:**
  ```sql
  CREATE TABLE transport_lane (
      lane_id VARCHAR(32) PRIMARY KEY,
      origin_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id),
      destination_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id),
      standard_transit_days INTEGER NOT NULL CHECK (standard_transit_days >= 1),
      distance_km DECIMAL(8,2) NOT NULL,
      primary_carrier_profile_id UUID REFERENCES carrier_profile(carrier_profile_id),
      standard_freight_cost DECIMAL(12,2),
      is_active BOOLEAN NOT NULL DEFAULT TRUE,
      CONSTRAINT uq_origin_dest UNIQUE (origin_facility_id, destination_facility_id)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Facility)-[:LANE_TO {lane_id: 'LANE-001', transit_days: 2, distance_km: 350.0}]->(:Facility)
  ```

#### 6. `Event_Impact`
- **Identifier:** `NOD_REL_EIM_001`
- **Concept:** Multi-attribute causal shock vector mapping a demand event to affected merchandise categories or subcategories.
- **Relational DDL:**
  ```sql
  CREATE TABLE event_impact (
      impact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      event_id VARCHAR(32) NOT NULL REFERENCES event(event_id),
      target_level VARCHAR(16) NOT NULL CHECK (target_level IN ('CATEGORY', 'SUBCATEGORY', 'PRODUCT_FAMILY')),
      target_id INTEGER NOT NULL,
      lift_multiplier DECIMAL(6,4) NOT NULL CHECK (lift_multiplier > 0),
      elasticity_factor DECIMAL(5,3) DEFAULT 1.0,
      CONSTRAINT uq_event_target UNIQUE (event_id, target_level, target_id)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Event)-[:IMPACTS {target_level: 'CATEGORY' | 'SUBCATEGORY' | 'FAMILY', lift_multiplier: 1.45, elasticity: 1.1}]->(:Category | :Subcategory | :Product_Family)
  ```

#### 7. `Event_Interaction`
- **Identifier:** `NOD_REL_EIN_001`
- **Concept:** Non-linear interaction rule governing the co-occurrence or close temporal proximity of two demand events.
- **Relational DDL:**
  ```sql
  CREATE TABLE event_interaction (
      interaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      event_id_1 VARCHAR(32) NOT NULL REFERENCES event(event_id),
      event_id_2 VARCHAR(32) NOT NULL REFERENCES event(event_id),
      interaction_type VARCHAR(32) NOT NULL CHECK (interaction_type IN ('COMPOUNDING', 'CANNIBALIZING', 'SUBSTITUTION')),
      dampening_factor DECIMAL(5,3) NOT NULL DEFAULT 1.0,
      max_separation_days INTEGER NOT NULL DEFAULT 7,
      CONSTRAINT uq_event_pair UNIQUE (event_id_1, event_id_2)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Event)-[:INTERACTS_WITH {interaction_type: 'COMPOUNDING', dampening_factor: 0.85, max_days: 7}]->(:Event)
  ```

#### 8. `Regional_Event_Weight`
- **Identifier:** `NOD_REL_REW_001`
- **Concept:** Geographic cultural significance modifier scaling event impact across macro-regions.
- **Relational DDL:**
  ```sql
  CREATE TABLE regional_event_weight (
      weight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      event_id VARCHAR(32) NOT NULL REFERENCES event(event_id),
      zone_id VARCHAR(32) NOT NULL REFERENCES zone_macro_region(zone_id),
      weight_multiplier DECIMAL(5,3) NOT NULL CHECK (weight_multiplier >= 0),
      cultural_significance_tier VARCHAR(16) NOT NULL DEFAULT 'PRIMARY',
      CONSTRAINT uq_event_zone UNIQUE (event_id, zone_id)
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Event)-[:REGIONAL_WEIGHT {weight_multiplier: 1.50, tier: 'PRIMARY'}]->(:Zone_Macro_Region)
  ```

#### 9. `Payment_Allocation`
- **Identifier:** `NOD_REL_PAL_001`
- **Concept:** Associative financial transaction resolving M:N settlement allocations between payments and invoices.
- **Relational DDL:**
  ```sql
  CREATE TABLE payment_allocation (
      allocation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      payment_id VARCHAR(64) NOT NULL REFERENCES payment(payment_id),
      invoice_id VARCHAR(64) NOT NULL REFERENCES invoice(invoice_id),
      allocated_amount DECIMAL(14,2) NOT NULL CHECK (allocated_amount > 0),
      discount_applied DECIMAL(12,2) DEFAULT 0.0,
      allocation_date DATE NOT NULL,
      gl_posting_ref VARCHAR(64),
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Payment)-[:ALLOCATED_TO {allocation_id: 'AL-001', allocated_amount: 5400.00, discount: 0.00}]->(:Invoice)
  ```

#### 10. `Three_Way_Match_Record`
- **Identifier:** `NOD_REL_TWM_001`
- **Concept:** Statutory procurement audit transaction reconciling Purchase Order lines, Goods Receipt lines, and Supplier Invoice lines.
- **Relational DDL:**
  ```sql
  CREATE TABLE three_way_match_record (
      match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      po_line_id VARCHAR(64) NOT NULL REFERENCES po_line(po_line_id),
      gr_line_id VARCHAR(64) NOT NULL REFERENCES goods_receipt_line(gr_line_id),
      supplier_invoice_line_id VARCHAR(64) NOT NULL REFERENCES supplier_invoice_line(invoice_line_id),
      ordered_qty INTEGER NOT NULL,
      received_accepted_qty INTEGER NOT NULL,
      invoiced_qty INTEGER NOT NULL,
      po_unit_price DECIMAL(12,4) NOT NULL,
      invoiced_unit_price DECIMAL(12,4) NOT NULL,
      variance_amount DECIMAL(14,2) NOT NULL,
      match_status VARCHAR(16) NOT NULL CHECK (match_status IN ('EXACT_MATCH', 'WITHIN_TOLERANCE', 'PRICE_VARIANCE', 'QTY_VARIANCE', 'REJECTED')),
      verified_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
  ```
- **Neo4j Pattern:**
  ```cypher
  (:Three_Way_Match_Record {match_id: 'TWM-001', status: 'EXACT_MATCH', variance: 0.00})
    -[:MATCHES_PO]->(:PO_Line),
  (:Three_Way_Match_Record)-[:MATCHES_RECEIPT]->(:Goods_Receipt_Line),
  (:Three_Way_Match_Record)-[:MATCHES_INVOICE]->(:Supplier_Invoice_Line)
  ```

---

## 3. Cross-Domain Directed Edge Master Registry

The following master table documents the complete cross-domain relationship network linking all 34 foundations and business domains.

| RELATIONSHIP_ID | FROM_NODE | RELATIONSHIP_TYPE | TO_NODE | CARDINALITY | TEMPORALITY | OPTIONALITY | GRAPH_DECISION | BUSINESS_RULE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `REL_FND_001` | `Party` | `HAS_ROLE_ASSIGNMENT` | `Party_Role_Assignment` | `1:N` | Effective-Dated | Mandatory | Node (`:Party_Role_Assignment`) | A party must possess at least one role to execute enterprise transactions. |
| `REL_FND_002` | `Party` | `HAS_IDENTITY` | `Identity` | `1:N` | State-Machine | Optional | Relationship `[:HAS_IDENTITY]` | Digital users/accounts authenticate through linked credentials. |
| `REL_FND_003` | `Party` | `HAS_CONTACT` | `Contact_Point` | `1:N` | Effective-Dated | Mandatory | Relationship `[:HAS_CONTACT]` | Every legal party must maintain a primary legal/physical contact point. |
| `REL_FND_004` | `Party` | `HAS_TAX_ID` | `Tax_Identity` | `1:N` | Effective-Dated | Mandatory | Relationship `[:HAS_TAX_ID]` | Commercial organizations must hold statutory tax registrations (GSTIN/PAN). |
| `REL_FND_005` | `Party` | `HOLDS_ACCOUNT` | `Bank_Account` | `1:N` | Effective-Dated | Optional | Relationship `[:HOLDS_ACCOUNT]` | Financial disbursements and collections map to verified bank accounts. |
| `REL_FND_006` | `Location` | `ANCHORS` | `Facility` | `1:1` | Static | Mandatory | Relationship `[:ANCHORS]` | Every facility is anchored to exactly one sub-meter geopoint. |
| `REL_FND_007` | `Facility` | `SUBTYPED_AS` | `Store` | `1:1` | Static | Optional | Dual Labels (`:Store:Facility`) | Retail stores specialize the base facility master. |
| `REL_FND_008` | `Facility` | `SUBTYPED_AS` | `Warehouse` | `1:1` | Static | Optional | Dual Labels (`:Warehouse:Facility`) | Warehouses and DCs specialize the base facility master. |
| `REL_FND_009` | `Facility` | `SUBTYPED_AS` | `Production_Site` | `1:1` | Static | Optional | Dual Labels (`:Production_Site:Facility`) | Production plants specialize the base facility master. |
| `REL_FND_010` | `Facility` | `SUBTYPED_AS` | `Office` | `1:1` | Static | Optional | Dual Labels (`:Office:Facility`) | Corporate offices specialize the base facility master. |
| `REL_FND_011` | `Calendar_Date` | `BELONGS_TO` | `Fiscal_Period` | `N:1` | Static | Mandatory | Relationship `[:BELONGS_TO]` | Every calendar day maps deterministically to exactly one fiscal period. |
| `REL_FND_012` | `Week` | `BELONGS_TO` | `Fiscal_Period` | `N:1` | Static | Mandatory | Relationship `[:BELONGS_TO]` | Retail 52-week calendar weeks map deterministically to corporate accounting periods. |
| `REL_FND_013` | `Holiday_Instance` | `REFERENCES` | `Event_Instance` | `N:1` | Static | Optional | Relationship `[:REFERENCES]` | Bank/gazetted holidays reference commercial demand shocks where co-occurring. |
| `REL_FND_014A` | `Party_Role_Assignment` | `HAS_PROFILE` | `Supplier_Profile` | `1:1` | Effective-Dated | Conditional | Relationship `[:HAS_PROFILE]` | Role assignment for `SUPPLIER` / `PRODUCER` / `AGGREGATOR` roles links to specialized Supplier_Profile. |
| `REL_FND_014B` | `Party_Role_Assignment` | `HAS_PROFILE` | `Customer_Profile` | `1:1` | Effective-Dated | Conditional | Relationship `[:HAS_PROFILE]` | Role assignment for `CUSTOMER` role links to specialized Customer_Profile. |
| `REL_FND_014C` | `Party_Role_Assignment` | `HAS_PROFILE` | `Carrier_Profile` | `1:1` | Effective-Dated | Conditional | Relationship `[:HAS_PROFILE]` | Role assignment for `CARRIER` / `3PL_PROVIDER` roles links to specialized Carrier_Profile. |
| `REL_FND_014D` | `Party_Role_Assignment` | `HAS_PROFILE` | `Employee_Profile` | `1:1` | Effective-Dated | Conditional | Relationship `[:HAS_PROFILE]` | Role assignment for `EMPLOYEE` / `DRIVER` roles links to specialized Employee_Profile. |
| `REL_FND_014E` | `Party_Role_Assignment` | `HAS_PROFILE` | `Marketplace_Seller_Profile` | `1:1` | Effective-Dated | Conditional | Relationship `[:HAS_PROFILE]` | Role assignment for `MARKETPLACE_SELLER` role links to specialized Marketplace_Seller_Profile. |
| `REL_FND_015` | `Location` | `WITHIN_POSTAL_AREA` | `Postal_Area` | `N:1` | Static | Mandatory | Relationship `[:WITHIN_POSTAL_AREA]` | Every geographic location is contained within an administrative postal area. |
| `REL_FND_016` | `Postal_Area` | `WITHIN_CITY` | `City` | `N:1` | Static | Mandatory | Relationship `[:WITHIN_CITY]` | Postal areas roll up to municipal city administrative boundaries. |
| `REL_FND_017` | `City` | `WITHIN_DISTRICT` | `District` | `N:1` | Static | Mandatory | Relationship `[:WITHIN_DISTRICT]` | Cities roll up to administrative districts within a state. |
| `REL_FND_018` | `District` | `WITHIN_STATE` | `State_Province` | `N:1` | Static | Mandatory | Relationship `[:WITHIN_STATE]` | Districts roll up to state/provincial tax and administrative boundaries. |
| `REL_FND_019` | `State_Province` | `WITHIN_ZONE` | `Zone_Macro_Region` | `N:1` | Static | Mandatory | Relationship `[:WITHIN_ZONE]` | States roll up to commercial/climatic macro-regions. |
| `REL_FND_020` | `Zone_Macro_Region` | `WITHIN_COUNTRY` | `Country` | `N:1` | Static | Mandatory | Relationship `[:WITHIN_COUNTRY]` | Macro-regions roll up to sovereign countries. |
| `REL_FND_021` | `Facility` | `LOCATED_AT` | `Location` | `1:1` | Static | Mandatory | Relationship `[:LOCATED_AT]` | Enterprise facility anchored at a specific geospatial coordinate location (inverse of `[:ANCHORS]`). |
| `REL_MER_001` | `Merchandise_Department`| `CONTAINS` | `Category` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Strict 6-level merchandise hierarchy step 1. |
| `REL_MER_002` | `Category` | `CONTAINS` | `Subcategory` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Strict 6-level merchandise hierarchy step 2. |
| `REL_MER_003` | `Subcategory` | `CONTAINS` | `Product_Family` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Strict 6-level merchandise hierarchy step 3. |
| `REL_MER_004` | `Product_Family` | `CONTAINS` | `Product` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Strict 6-level merchandise hierarchy step 4. |
| `REL_MER_005` | `Product` | `CONTAINS` | `SKU` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Strict 6-level merchandise hierarchy step 5. |
| `REL_MER_006` | `Brand` | `BRANDS` | `Product` | `1:N` | Static | Mandatory | Relationship `[:BRANDS]` | Every commercial product is branded by a recognized brand master. |
| `REL_MER_007` | `SKU` | `PRODUCED_IN` | `Batch` | `1:N` | Immutable | Mandatory | Relationship `[:PRODUCED_IN]` | Traceable production output is grouped into batches. |
| `REL_MER_008` | `Batch` | `DIVIDED_INTO` | `Lot` | `1:N` | Immutable | Mandatory | Relationship `[:DIVIDED_INTO]` | Batches are partitioned into inspection lots for quality release. |
| `REL_SUP_001` | `Supplier_Profile` | `OPERATES` | `Supplier_Site` | `1:N` | Effective-Dated | Mandatory | Relationship `[:OPERATES]` | Suppliers dispatch goods from one or more registered production sites. |
| `REL_SUP_002` | `Supplier_Profile` | `SOURCES` | `SKU` | `M:N` | Effective-Dated | Mandatory | Rich Relationship (`Supplier_SKU_Map`) | Multi-sourcing network: suppliers supply multiple SKUs at specific unit costs. |
| `REL_PRO_001` | `Purchase_Requisition` | `SOLICITS` | `RFQ` | `1:1` | State-Machine | Optional | Relationship `[:SOLICITS]` | Unfulfilled replenishment needs generate supplier RFQs. |
| `REL_PRO_002` | `Purchase_Order` | `CONTAINS` | `PO_Line` | `1:N` | State-Machine | Mandatory | Relationship `[:CONTAINS]` | Purchase orders contain line-item SKU commitments. |
| `REL_PRO_003` | `PO_Line` | `DELIVERED_IN` | `Goods_Receipt_Line` | `1:N` | Immutable | Optional | Relationship `[:DELIVERED_IN]` | PO lines are fulfilled across one or more partial goods receipts. |
| `REL_LOG_001` | `Transport_Order` | `EXECUTED_AS` | `Shipment` | `1:N` | State-Machine | Mandatory | Relationship `[:EXECUTED_AS]` | Logistics orders are executed as one or more multi-modal shipments. |
| `REL_LOG_002` | `Shipment` | `CONTAINS` | `Shipment_Line` | `1:N` | Immutable | Mandatory | Relationship `[:CONTAINS]` | Shipments aggregate multiple handling units, PO lines, or transfer orders. |
| `REL_LOG_003` | `Shipment` | `SHIPPED_VIA` | `Carrier_Profile` | `N:1` | State-Machine | Mandatory | Relationship `[:SHIPPED_VIA]` | Every shipment is assigned to an authorized carrier profile. |
| `REL_LOG_004` | `Shipment` | `COSTED_AS` | `Freight_Cost` | `1:1` | State-Machine | Mandatory | Relationship `[:COSTED_AS]` | Completed shipments accrue freight liabilities billed via carrier invoices. |
| `REL_WH_001` | `Warehouse` | `CONTAINS` | `Zone` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Physical warehouse zoning (Cold Storage, Dry Storage, Hazmat). |
| `REL_WH_002` | `Zone` | `CONTAINS` | `Warehouse_Aisle` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Warehouse storage topology step 1. |
| `REL_WH_003` | `Warehouse_Aisle` | `CONTAINS` | `Rack` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Warehouse storage topology step 2. |
| `REL_WH_004` | `Rack` | `CONTAINS` | `Warehouse_Shelf` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Warehouse storage topology step 3. |
| `REL_WH_005` | `Warehouse_Shelf` | `CONTAINS` | `Bin` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Warehouse storage topology step 4 (lowest storage unit). |
| `REL_WH_006` | `Bin` | `STORES` | `Handling_Unit` | `1:N` | State-Machine | Optional | Relationship `[:STORES]` | Bins hold pallets, cartons, or loose inventory lots. |
| `REL_STR_001` | `Store` | `CONTAINS` | `Floor` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Retail store layout hierarchy step 1. |
| `REL_STR_002` | `Floor` | `CONTAINS` | `Store_Aisle` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Retail store layout hierarchy step 2. |
| `REL_STR_003` | `Store_Aisle` | `CONTAINS` | `Store_Shelf` | `1:N` | Static | Mandatory | Relationship `[:CONTAINS]` | Retail store layout hierarchy step 3. |
| `REL_STR_004` | `Store_Shelf` | `ANCHORS` | `Planogram` | `1:N` | Effective-Dated | Mandatory | Relationship `[:ANCHORS]` | Planograms dictate shelf facings, layout, and visual merchandising. |
| `REL_STR_005` | `Store` | `ASSORTS` | `SKU` | `M:N` | Effective-Dated | Mandatory | Rich Relationship (`Store_SKU_Assortment`) | Multi-format store assortment authorizing SKU stocking and display. |
| `REL_NET_001` | `Store` | `SERVICED_BY` | `Warehouse` | `M:N` | Effective-Dated | Mandatory | Rich Relationship (`Store_Warehouse_Map`) | Multi-echelon distribution network assigning regional warehouses to supply retail stores. |
| `REL_NET_002` | `Facility` | `LANE_TO` | `Facility` | `M:N` | Effective-Dated | Mandatory | Rich Relationship (`Transport_Lane`) | Physical transportation conduit connecting enterprise origin and destination facilities. |
| `REL_INV_001` | `Inventory_Position` | `LOCATED_AT` | `Facility` | `N:1` | Mutable | Mandatory | Relationship `[:LOCATED_AT]` | Inventory positions are facility-specific (Store, Warehouse, Plant). |
| `REL_INV_002` | `Inventory_Position` | `TRACKS_SKU` | `SKU` | `N:1` | Mutable | Mandatory | Relationship `[:TRACKS_SKU]` | Inventory positions maintain on-hand, reserved, and available stock per SKU. |
| `REL_COM_001` | `Customer_Profile` | `CREATES` | `Cart` | `1:N` | State-Machine | Optional | Relationship `[:CREATES]` | Customer digital intent forms within mutable shopping carts. |
| `REL_COM_002` | `Cart` | `CONVERTS_TO` | `Basket` | `1:1` | State-Machine | Optional | Relationship `[:CONVERTS_TO]` | Checkout initiation freezes the cart into an immutable commercial basket. |
| `REL_COM_003` | `Basket` | `COMMITTED_AS` | `Sales_Transaction` | `1:1` | Immutable | Mandatory | Relationship `[:COMMITTED_AS]` | Completed sales convert baskets into legal sales transactions. |
| `REL_COM_004` | `Sales_Transaction` | `CONTAINS` | `Sales_Line` | `1:N` | Immutable | Mandatory | Relationship `[:CONTAINS]` | Sales transactions record SKU-level pricing, quantities, and taxes. |
| `REL_COM_005` | `Sales_Transaction` | `PAID_VIA` | `Customer_Payment` | `1:N` | State-Machine | Mandatory | Relationship `[:PAID_VIA]` | POS and online sales require settlement via customer payments. |
| `REL_COM_006` | `Sales_Transaction` | `INVOICED_AS` | `Customer_Invoice` | `1:1` | State-Machine | Mandatory | Relationship `[:INVOICED_AS]` | Legal sales generate customer invoices and GST compliance records. |
| `REL_ORD_001` | `Sales_Order` | `CONTAINS` | `Order_Line` | `1:N` | State-Machine | Mandatory | Relationship `[:CONTAINS]` | Asynchronous orders contain line-item fulfillment requests. |
| `REL_ORD_002` | `Order_Line` | `ALLOCATES_FROM` | `Inventory_Position` | `N:1` | Operational | Mandatory | Relationship `[:ALLOCATES_FROM]` | Order lines place reservations against facility inventory positions. |
| `REL_ORD_003` | `Order_Allocation` | `FULFILLED_BY` | `Fulfillment_Order` | `1:1` | State-Machine | Mandatory | Relationship `[:FULFILLED_BY]` | Sourced allocations trigger warehouse picking and packing waves. |
| `REL_PRC_001` | `Sales_Line` | `PRICED_BY` | `Price_Record` | `N:1` | Snapshot | Mandatory | Relationship `[:PRICED_BY]` | Every sales transaction line is priced according to active price records. |
| `REL_PRC_002` | `Price_Record` | `FOR_WEEK` | `Week` | `N:1` | Static | Mandatory | Relationship `[:FOR_WEEK]` | Temporal price history is partitioned by Retail 52-Week Calendar (`WEEK_SYSTEM = RETAIL_52_WEEK`). |
| `REL_PRM_001` | `Promotion` | `DISCOUNTS` | `Sales_Line` | `1:N` | Effective-Dated | Optional | Relationship `[:DISCOUNTS]` | Active promotional campaigns apply discounts against eligible sales lines. |
| `REL_RET_001` | `Return_Request` | `CONTAINS` | `Return_Line` | `1:N` | State-Machine | Mandatory | Relationship `[:CONTAINS]` | Post-sale returns document specific items, quantities, and return reasons. |
| `REL_RET_002` | `Return_Receipt` | `INSPECTED_VIA` | `Quality_Inspection` | `1:1` | State-Machine | Mandatory | Relationship `[:INSPECTED_VIA]` | Returned merchandise must undergo quality inspection before disposition. |
| `REL_RET_003` | `Quality_Inspection` | `DETERMINES` | `Disposition` | `1:1` | Immutable | Mandatory | Relationship `[:DETERMINES]` | Quality inspection results dictate restocking, liquidation, or scrapping. |
| `REL_FIN_001` | `Purchase_Order` | `INVOICED_AS` | `Supplier_Invoice` | `1:N` | State-Machine | Mandatory | Relationship `[:INVOICED_AS]` | Supplier shipments generate supplier invoices billed to Accounts Payable. |
| `REL_FIN_002` | `Payment` | `ALLOCATED_TO` | `Invoice` | `M:N` | Immutable | Mandatory | Rich Relationship (`[:ALLOCATED_TO]`) | Non-polymorphic payment allocation edge carrying `allocation_id`, `allocated_amount`, `discount_applied`, and `allocation_date`. |
| `REL_FIN_003` | `Three_Way_Match_Record` | `MATCHES_PO` | `PO_Line` | `N:1` | Immutable | Mandatory | Relationship `[:MATCHES_PO]` | Three-way match reconciles accepted purchase order line commitments. |
| `REL_FIN_004` | `Journal_Entry` | `CONTAINS` | `Journal_Line` | `1:N` | Immutable | Mandatory | Relationship `[:CONTAINS]` | Double-entry accounting entries contain balanced debit and credit lines. |
| `REL_FIN_005` | `Journal_Line` | `POSTS_TO` | `GL_Account` | `N:1` | Immutable | Mandatory | Relationship `[:POSTS_TO]` | Journal lines post financial debits and credits to the Chart of Accounts. |
| `REL_FIN_006` | `Three_Way_Match_Record` | `MATCHES_RECEIPT` | `Goods_Receipt_Line` | `N:1` | Immutable | Mandatory | Relationship `[:MATCHES_RECEIPT]` | Three-way match reconciles verified warehouse goods receipt lines. |
| `REL_FIN_007` | `Three_Way_Match_Record` | `MATCHES_INVOICE` | `Supplier_Invoice_Line` | `N:1` | Immutable | Mandatory | Relationship `[:MATCHES_INVOICE]` | Three-way match reconciles billed supplier invoice lines. |
| `REL_TAX_001` | `Invoice` | `TAXED_BY` | `GST_Transaction` | `1:1` | Immutable | Mandatory | Relationship `[:TAXED_BY]` | Every customer and supplier invoice generates statutory GST transaction records. |
| `REL_DEM_001` | `Event` | `HAS_INSTANCE` | `Event_Instance` | `1:N` | Versioned | Mandatory | Relationship `[:HAS_INSTANCE]` | Master event definitions spawn recurring annual event instances. |
| `REL_DEM_002A`| `Event` | `IMPACTS` | `Category` | `M:N` | Static | Optional | Rich Relationship (`Event_Impact`) | Causal shock vector driving latent demand lift at the merchandise category level (`target_level = 'CATEGORY'`). |
| `REL_DEM_002B`| `Event` | `IMPACTS` | `Subcategory` | `M:N` | Static | Optional | Rich Relationship (`Event_Impact`) | Causal shock vector driving latent demand lift at the subcategory level (`target_level = 'SUBCATEGORY'`). |
| `REL_DEM_002C`| `Event` | `IMPACTS` | `Product_Family` | `M:N` | Static | Optional | Rich Relationship (`Event_Impact`) | Causal shock vector driving latent demand lift at the product family level (`target_level = 'PRODUCT_FAMILY'`). |
| `REL_DEM_003` | `Event_Instance` | `DRIVES_SIGNAL` | `Demand_Signal` | `1:N` | Snapshot | Mandatory | Relationship `[:DRIVES_SIGNAL]` | Concrete event instances generate demand signals during the simulation week. |
| `REL_DEM_004` | `Demand_Signal` | `CREATES` | `Demand_Observation` | `1:1` | Snapshot | Mandatory | Relationship `[:CREATES]` | Signals translate into unconstrained latent demand and observed sales. |
| `REL_DEM_005` | `Demand_Observation` | `ATTRIBUTED_TO` | `Event_Instance` | `N:1` | Snapshot | Optional | Relationship `[:ATTRIBUTED_TO]` | Observed sales receive causal attribution weights from active events. |
| `REL_DEM_006` | `Event` | `INTERACTS_WITH` | `Event` | `M:N` | Static | Optional | Rich Relationship (`Event_Interaction`) | Co-occurrence interaction rule defining compounding, cannibalizing, or substitution effects between overlapping events. |
| `REL_DEM_007` | `Event` | `REGIONAL_WEIGHT` | `Zone_Macro_Region` | `M:N` | Static | Optional | Rich Relationship (`Regional_Event_Weight`) | Geographic cultural significance modifier scaling event impact across macro-regions. |
| `REL_PROC_005`| `Purchase_Order` | `ISSUED_TO` | `Supplier_Profile` | `N:1` | State-Machine | Mandatory | Relationship `[:ISSUED_TO]` | Purchase orders are formally issued to registered supplier profiles. |
| `REL_AST_001` | `Physical_Asset` | `LOCATED_IN` | `Facility` | `N:1` | Effective-Dated | Mandatory | Relationship `[:LOCATED_IN]` | Equipment and assets are installed in specific facilities and zones. |
| `REL_AST_002` | `Asset_Downtime` | `CAUSES` | `Capacity_Impact_Event` | `1:1` | Immutable | Mandatory | Relationship `[:CAUSES]` | Equipment failure (e.g., chiller breakdown) causes cold storage capacity loss. |
| `REL_AST_003` | `Capacity_Impact_Event` | `TRIGGERS` | `Spoilage_Event` | `1:1` | Immutable | Optional | Relationship `[:TRIGGERS]` | Capacity loss in perishable storage triggers spoilage and inventory write-offs. |
| `REL_AST_004` | `Asset_Downtime` | `AFFECTS_ASSET` | `Physical_Asset` | `N:1` | Immutable | Mandatory | Relationship `[:AFFECTS_ASSET]` | Asset downtime directly records failure on a specific physical asset. |
| `REL_INV_003` | `Spoilage_Event` | `SPOILS_SKU` | `SKU` | `N:1` | Immutable | Mandatory | Relationship `[:SPOILS_SKU]` | Spoilage events identify the specific perishable SKU lost. |
| `REL_INV_004` | `Spoilage_Event` | `WRITTEN_OFF_AS` | `Writeoff_Record` | `1:1` | Immutable | Mandatory | Relationship `[:WRITTEN_OFF_AS]` | Physical spoilage triggers financial write-off records. |
| `REL_INV_005` | `Writeoff_Record` | `POSTS_TO` | `Journal_Entry` | `1:1` | Immutable | Mandatory | Relationship `[:POSTS_TO]` | Write-off records post financial loss entries to the General Ledger. |
| `REL_WRK_001` | `Employee_Profile` | `CLASSIFIED_AS` | `Workforce_Role` | `N:1` | Effective-Dated | Mandatory | Relationship `[:CLASSIFIED_AS]` | Employees are assigned to organizational job roles (e.g., Cashier, Manager). |
| `REL_WRK_002` | `POS_Terminal` | `OPERATED_BY` | `Employee_Profile` | `N:1` | Timestamped | Optional | Relationship `[:OPERATED_BY]` | POS terminals log cashier shift logins for transaction accountability. |
| `REL_RSK_001` | `Scenario` | `EXECUTED_IN` | `Simulation_Run` | `1:N` | Immutable | Optional | Relationship `[:EXECUTED_IN]` | Supply, demand, and disruption scenarios drive synthetic simulation runs. |
| `REL_GOV_001` | `Simulation_Run` | `PRODUCES` | `Demand_Observation` | `1:N` | Immutable | Mandatory | Relationship `[:PRODUCES]` | Simulation runs generate the 18-million-row ground truth demand history. |
| `REL_GOV_002` | `Simulation_Run` | `AUDITED_BY` | `Validation_Result` | `1:N` | Immutable | Mandatory | Relationship `[:AUDITED_BY]` | Simulation runs must pass Tier A through D validation gates. |

---

## 4. Neo4j Cypher Relationship & Constraint DDL

```cypher
// -----------------------------------------------------------------------------
// Uniqueness Constraints for Tier 3 Relationship Nodes
// -----------------------------------------------------------------------------
CREATE CONSTRAINT cst_pra_id IF NOT EXISTS FOR (pra:Party_Role_Assignment) REQUIRE pra.role_assignment_id IS UNIQUE;
CREATE CONSTRAINT cst_twm_id IF NOT EXISTS FOR (twm:Three_Way_Match_Record) REQUIRE twm.match_id IS UNIQUE;

// -----------------------------------------------------------------------------
// Directed Relationship Indexing & Constraints
// -----------------------------------------------------------------------------
// Merchandise Hierarchy Index
CREATE INDEX idx_rel_merch_contains IF NOT EXISTS FOR ()-[r:CONTAINS]-() ON (r.effective_date);

// Assortment & Sourcing Relationship Indexes
CREATE INDEX idx_rel_store_assorts IF NOT EXISTS FOR ()-[r:ASSORTS]-() ON (r.status, r.facing_qty);
CREATE INDEX idx_rel_supplier_sources IF NOT EXISTS FOR ()-[r:SOURCES]-() ON (r.priority, r.unit_cost);
CREATE INDEX idx_rel_serviced_by IF NOT EXISTS FOR ()-[r:SERVICED_BY]-() ON (r.is_primary, r.lead_time_days);

// Demand & Event Causal Indexes
CREATE INDEX idx_rel_event_impacts IF NOT EXISTS FOR ()-[r:IMPACTS]-() ON (r.target_level, r.lift_multiplier);
CREATE INDEX idx_rel_demand_attributed IF NOT EXISTS FOR ()-[r:ATTRIBUTED_TO]-() ON (r.attribution_weight);

// Finance & Payment Allocation Indexes
CREATE INDEX idx_rel_payment_allocated IF NOT EXISTS FOR ()-[r:ALLOCATED_TO]-() ON (r.allocated_amount);
```

---

## 5. Relationship Closure & Integrity Verification

| Verification Gate | Validation Criteria | Verification Outcome |
| :--- | :--- | :--- |
| **Referential Closure** | 100% of `FROM_NODE` and `TO_NODE` definitions strictly resolve to registered entities in Stage 0A and Stage 1. | Passed (0 unresolved endpoints) |
| **Zero Orphan Domains** | Graph connectivity check confirms every one of the 30 domains connects directly or transitively to the enterprise core. | Passed (Fully connected enterprise graph) |
| **Relational vs. Graph Integrity** | Associative entities lacking independent lifecycles are mapped as rich edges; lifecycle-bearing entities remain nodes. | Passed |
| **Non-Polymorphic Financial Edges** | `Payment_Allocation` strictly links canonical `Payment` and `Invoice` parents. | Passed |
| **Causal Non-Contamination** | `Event` impacts `Category`, driving `Demand_Signal` -> `Demand_Observation`. Zero direct synthetic event-to-sales bypass edges. | Passed |

---

### Stage 2 Sign-Off Status
**Stage 2 (SCOF Enterprise Relationship Registry) is COMPLETE and LOCKED.**
Execution is ready to proceed to **Sprint 2 / Sub-Plan 2B: Stage 3 — End-to-End Enterprise Lifecycle Flows**.
