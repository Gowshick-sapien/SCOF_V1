# SCOF Enterprise Dataset Ecosystem: Big-Picture Architecture & File-by-File Reference Guide

---

## 1. Big-Picture Architecture & Multi-Modal Dataset Flow

The SCOF (Supply Chain Operations Framework) dataset ecosystem is an enterprise-scale, multi-modal data architecture designed to model physical supply-chain dynamics, retail commerce, financial ledgering, and causal shock responses.

Rather than treating data as disconnected flat files, the SCOF dataset operates across four synchronized operational modalities:

```text
                                  THE SCOF MULTI-MODAL DATASET FLOW
                                  
     [ 1. FILE SYSTEM DATASETS ]               [ 2. RELATIONAL CONTRACT ]
     8-Tier Deterministic DAG                     Canonical PostgreSQL Schema
     Isolated RNGs (PCG64)                        96 Tables / 165 Physical FKs
     CSV & Parquet Storage                        Topological Dependency Order
              │                                                │
              │ (scripts/generate_synthetic_ecosystem.py)       │ (scripts/load_postgresql_data.py)
              ▼                                                ▼
     datasets/foundations/                      datasets/scof_relational.db
     datasets/masters/                          (Authoritative DDL: scripts/schema_ddl.sql)
     datasets/network/                                         │
     datasets/procurement/                                     │ (scripts/materialize_neo4j_graph.py)
     datasets/inventory/                                       ▼
     datasets/commerce/                         [ 3. PROPERTY GRAPH ECOSYSTEM ]
     datasets/finance/                            datasets/neo4j_graph/
     datasets/demand/                             3,728,199 Nodes (50 Core Labels)
     datasets/weekly_demand_history_v2.csv        2,104,514 Edges (30 Rel Types)
              │                                   59 Uniqueness Constraints (51 Core + 8 Ext)
              │                                                │
              └────────────────────────┬───────────────────────┘
                                       │ (scripts/validate_operational_twin.py)
                                       ▼
                         [ 4. OPERATIONAL TWIN SERVICES ]
                         services/twin_service.py
                         - Lineage Tracing (Farm-to-Store)
                         - Causal Shock Propagation
                         - Asset Disruption & Spoilage Simulation
                         - Automated Three-Way Match Auditing
                         - Double-Entry General Ledger Trial Balance
```

### Directory Structure Overview

The dataset directory tree is partitioned by business and architectural domains:

```text
d:/projects/SCOF_V1/SCOF/datasets/
├── foundations/          # Platform Foundations A-D (Party, Geography, Time, Reference Dimensions)
├── governance/           # Legal entities, corporate structure, business units
├── masters/              # Merchandise taxonomy, stores, DCs, assortments, sourcing, replenishment
├── merchandise/          # Partitioned SKU catalogs, store-SKU assortments, price history
├── network/              # Facilities, physical assets, transport lanes, shipments, shipment lines
├── sourcing/             # Suppliers, carriers, employee profiles, vendor contracts, sourcing maps
├── procurement/          # Purchase orders and purchase order lines
├── inventory/            # Goods receipts, goods receipt lines, inventory positions
├── commerce/             # Sales channels, customer sales transactions, transaction line items
├── finance/              # Invoices, lines, three-way match, payments, allocations, GL journal, COA
├── demand/               # Master events, weekly regional weather
├── advanced_events/      # Causal event master, impact vectors, interactions, regional weights
├── neo4j_graph/          # Materialized Neo4j Admin import CSVs (nodes and edges) & Cypher scripts
└── root datasets/        # Simulation ground truth (18M rows), price history, promotions, category catalogs
```

---

## 1.1 Population Scope & Materialization Semantics: Multi-Tier Reconciliation

To maintain rigorous auditability across all tiers of the SCOF framework, the documentation explicitly decouples four distinct operational scopes:
1. **Theoretical Annual Enterprise Run-Rate:** Theoretical annualized capacity of a multi-billion dollar conglomerate across all historical years (e.g., 100K+ POs, 95K+ shipments).
2. **Canonical Persisted Dataset:** The exact, deterministic, foreign-key validated dataset generated in Phase 2 and persisted under `datasets/` (e.g., 15,000 POs, 18,000 shipments, 15,000 receipts, 15,000 supplier invoices, 50,000 customer transactions, 25,000 journal entries).
3. **Relational Ingestion Population:** The data ingested into `datasets/scof_relational.db` (4,358,100 rows across 92 populated tables).
4. **Graph Materialization Population:** The nodes and edges exported into `datasets/neo4j_graph/` (3,728,199 nodes and 2,104,514 edges).

### Entity Population Reconciliation Table

| Entity / Concept | Canonical Persisted Dataset | Relational Ingested | Graph Materialized | Transformation & Realization Semantics |
| :--- | :---: | :---: | :---: | :--- |
| **Party** | 230 parties (`party_master.csv`: 228 orgs + 2 persons) | 230 rows (`party`) | 230 nodes (`:Party`: 228 `:Organization:Party` + 2 `:Person:Party`) | **Resolved:** Exactly 230 parties across all three tiers (228 organizations + 2 sample persons: employee and customer). |
| **Purchase Order** | 15,000 POs (`purchase_orders.parquet`) | 15,000 rows (`purchase_order`) | 15,000 nodes (`:Purchase_Order`) | 1:1 direct relational-to-graph realization. |
| **PO Line** | 90,227 lines (`po_lines.parquet`) | 90,227 rows (`po_line`) | 90,227 nodes (`:PO_Line`) | 1:1 direct realization with `ORDERED_IN` and `FOR_SKU_POLINE` edges. |
| **Shipment** | 18,000 shipments (`shipments.parquet`) | 18,000 rows (`shipment`) | 18,000 nodes (`:Shipment`) | 1:1 direct realization tracking multi-echelon transit. |
| **Shipment Line** | 152,876 lines (`shipment_lines.parquet`) | 152,876 rows (`shipment_line`) | 152,876 nodes (`:Shipment_Line`) | 1:1 direct realization with `PART_OF_SHIPMENT` edges. |
| **Goods Receipt** | 15,000 receipts (`goods_receipts.parquet`) | 15,000 rows (`goods_receipt`) | 15,000 nodes (`:Goods_Receipt`) | 1:1 dock inspection records matching PO deliveries. |
| **Goods Receipt Line** | 89,871 lines (`goods_receipt_lines.parquet`) | 89,871 rows (`goods_receipt_line`) | 72,917 nodes (`:Goods_Receipt_Line`) | Active accepted dock receipt lines with resolved PO line links. |
| **Supplier Invoice** | 15,000 invoices (`supplier_invoices.parquet`) | 15,000 rows (`supplier_invoice`) | Subtype of `:Invoice` | Ingested into table `supplier_invoice` and unified table `invoice`. |
| **Customer Invoice** | 50,000 invoices (`customer_invoices.parquet`) | 50,000 rows (`customer_invoice`) | Subtype of `:Invoice` | Ingested into table `customer_invoice` and unified table `invoice`. |
| **Total Invoices** | **65,000 invoices** (15K Supplier + 50K Customer) | **65,000 rows** (`invoice`) | **65,000 nodes** (`:Invoice`) | **Resolved:** Table `invoice` unifies 15K supplier invoices + 50K customer invoices. Neo4j exports `SELECT * FROM invoice` (65,000 nodes). |
| **Supplier Invoice Line** | 75,268 lines (`supplier_invoice_lines.parquet`) | 75,268 rows (`supplier_invoice_line`) | 66,673 nodes (`:Supplier_Invoice_Line`)| Active lines with verified PO line bindings. |
| **Three-Way Match** | 75,268 records (`three_way_match_records.parquet`) | 75,268 rows (`three_way_match_record`) | 60,965 nodes (`:Three_Way_Match_Record`)| **Resolved:** 60,965 represents the active 1:1:1 three-way matched subset simultaneously resolving PO line, GR line, and Invoice line. |
| **Payments** | 65,000 payments (`payments.parquet`) | 65,000 rows (`payment`) | 65,000 nodes (`:Payment`) | Encompasses 15,000 supplier payments and 50,000 customer payments. |
| **Journal Entry** | 25,000 entries (`journal_entries.parquet`) | 25,000 rows (`journal_entry`) | 25,000 nodes (`:Journal_Entry`) | 1:1 double-entry vouchers maintaining global equilibrium. |
| **Journal Line** | 50,000 lines (`journal_lines.parquet`) | 50,000 rows (`journal_line`) | 50,000 nodes (`:Journal_Line`) | 1:1 debits and credits posted to `:GL_Account`. |
| **Regional Event Weight** | 554 rules (`regional_event_weights.csv`) | 174 rows (`regional_event_weight`) | 174 edges (`[:REGIONAL_WEIGHT]`) | **Resolved:** The 554 raw rows define multi-region weights across India (PAN_INDIA, North, South, East, West). The relational loader localizes weights to the active anchor zone (`ZONE_SOUTH`), generating exactly 174 distinct event weight rows (1 per event), exported to 174 graph edges. |

---

## 2. Platform Foundations (`datasets/foundations/`)

The foundations establish universal identifiers and dimensions shared across all 30 business domains.

### 2.1 `datasets/foundations/party_master.csv`
- **File Path:** [datasets/foundations/party_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/party_master.csv)
- **Format & Size:** CSV | 230 rows | 17,000 bytes
- **What it Intends to Do:** Models Foundation A (Party & Identity). Represents all legal actors, individuals, corporate entities, suppliers, carriers, and sample retail personas.
- **What it Achieves:** Serves as the polymorphic root for all enterprise agents, eliminating duplicate identity definitions across vendor, customer, employee, and carrier tables.
- **Row Titles (Columns):**
  - `party_id` (VARCHAR(32), Primary Key): Unique party identifier (`PTY-ENT-001` to `PTY-CUST-001`, 230 total).
  - `party_code` (VARCHAR(32), Unique): Enterprise human-readable party code (`PTY-ENT-001`, `PTY-SUP-001`, `PTY-EMP-001`).
  - `party_type` (VARCHAR(16)): Legal classification (`ORGANIZATION` [228 rows] or `PERSON` [2 rows]).
  - `legal_name` (VARCHAR(255)): Registered legal name.
  - `status` (VARCHAR(16)): Operational status (`ACTIVE`, `INACTIVE`).
- **PostgreSQL Mapping:** Table `party` (230 rows: 228 organizations + 2 persons; DDL: `scripts/schema_ddl.sql`). Non-polymorphic primary key `party_id`.
- **Neo4j Connections:**
  - Node Label: `:Party` (230 total nodes), with subtype labels `:Organization:Party` (228 nodes) and `:Person:Party` (2 nodes).
  - Outgoing Edges: `(:Party)-[:LOCATED_AT]->(:Location)`.
  - Incoming Edges: `(:Supplier_Profile)-[:BELONGS_TO_PARTY]->(:Party)`, `(:Carrier_Profile)-[:BELONGS_TO_PARTY]->(:Party)`.

### 2.2 `datasets/foundations/geography_nodes.csv`
- **File Path:** [datasets/foundations/geography_nodes.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/geography_nodes.csv)
- **Format & Size:** CSV | 4 rows | 223 bytes
- **What it Intends to Do:** Models Foundation B (Geography & Spatial Hierarchy). Defines administrative boundaries and urban centers.
- **What it Achieves:** Anchors all physical facilities, stores, distribution centers, and customer addresses to verified geographic coordinates.
- **Row Titles (Columns):**
  - `city_id` (VARCHAR(32), Primary Key): City identifier (`CTY-001` to `CTY-004`).
  - `district_id` (VARCHAR(32), Foreign Key): References `district.district_id`.
  - `city_name` (VARCHAR(100)): City name (e.g., Mumbai, Delhi, Bengaluru, Chennai).
  - `tier` (VARCHAR(16)): Urban tier classification (`TIER_1`, `TIER_2`).
  - `population` (INTEGER): Metropolitan census population.
- **PostgreSQL Mapping:** Table `city` (DDL: `scripts/schema_ddl.sql`). Foreign key to `district`.
- **Neo4j Connections:**
  - Node Label: `:City`.
  - Outgoing Edges: `(:City)-[:LOCATED_IN]->(:District)-[:LOCATED_IN]->(:State_Province)-[:LOCATED_IN]->(:Country)`.
  - Incoming Edges: `(:Postal_Area)-[:IN_CITY]->(:City)`, `(:Location)-[:IN_CITY]->(:City)`.

### 2.3 `datasets/foundations/calendar_date.csv`
- **File Path:** [datasets/foundations/calendar_date.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/calendar_date.csv)
- **Format & Size:** CSV | 1,095 rows | 74,086 bytes
- **What it Intends to Do:** Models Foundation C (Time & Calendar). Daily temporal dimension covering a full 3-year horizon (2025–2027).
- **What it Achieves:** Enables daily transaction timestamping, lead-time day arithmetic, and holiday calendar offsets.
- **Row Titles (Columns):**
  - `date_id` (VARCHAR(16), Primary Key): Date key string (`2026-01-01`).
  - `date_key` (INTEGER): Integer surrogate key (`20260101`).
  - `year_id` (VARCHAR(16)): Calendar year (`2026`).
  - `month_id` (VARCHAR(16)): Calendar month (`2026-01`).
  - `week_id` (VARCHAR(16), Foreign Key): References `week.week_id` (`2026W01`).
  - `day_of_week` (INTEGER): 1 (Monday) to 7 (Sunday).
  - `day_name` (VARCHAR(16)): Monday through Sunday.
  - `day_of_month` (INTEGER): 1 to 31.
  - `day_of_year` (INTEGER): 1 to 365.
  - `is_weekend` (BOOLEAN): 1 for Saturday/Sunday, else 0.
  - `is_business_day` (BOOLEAN): 1 for non-holiday weekdays, else 0.
- **PostgreSQL Mapping:** Table `calendar_date`. Foreign keys to `week`, `month`, `calendar_year`.
- **Neo4j Connections:**
  - Node Label: `:Calendar_Date`.
  - Outgoing Edges: `(:Calendar_Date)-[:PART_OF_WEEK]->(:Week)`, `(:Calendar_Date)-[:PART_OF_MONTH]->(:Month)`.

### 2.4 `datasets/foundations/week.csv`
- **File Path:** [datasets/foundations/week.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/week.csv)
- **Format & Size:** CSV | 157 rows | 6,317 bytes
- **What it Intends to Do:** Operational weekly calendar dimension (National Retail Federation 4-5-4 retail calendar).
- **What it Achieves:** Unifies weekly demand simulation (`weekly_demand_history_v2.csv`), longitudinal price history, and weekly replenishment planning.
- **Row Titles (Columns):**
  - `week_id` (VARCHAR(16), Primary Key): Standardized week code (`2026W01` to `2026W52`).
  - `year_id` (VARCHAR(16)): Year code (`2026`).
  - `start_date` (DATE): Week commencement date (Monday).
  - `end_date` (DATE): Week termination date (Sunday).
  - `week_number` (INTEGER): Sequential week number (1 to 52).
  - `retail_quarter` (VARCHAR(8)): Retail quarter (`Q1`, `Q2`, `Q3`, `Q4`).
- **PostgreSQL Mapping:** Table `week`.
- **Neo4j Connections:**
  - Node Label: `:Week`.
  - Outgoing Edges: `(:Week)-[:PART_OF_YEAR]->(:Calendar_Year)`.
  - Incoming Edges: `(:Demand_Observation)-[:OBSERVED_IN_WEEK]->(:Week)`, `(:Price_Record)-[:EFFECTIVE_IN_WEEK]->(:Week)`.

### 2.5 `datasets/foundations/fiscal_period.csv`
- **File Path:** [datasets/foundations/fiscal_period.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/fiscal_period.csv)
- **Format & Size:** CSV | 36 rows | 1,474 bytes
- **What it Intends to Do:** Corporate accounting calendar dimension. 12 monthly fiscal periods per year across 3 years.
- **What it Achieves:** Enables double-entry financial posting and general ledger trial balance reconciliation.
- **Row Titles (Columns):**
  - `fiscal_period_id` (VARCHAR(16), Primary Key): Fiscal period code (`FP-2026-01`).
  - `fiscal_year_id` (VARCHAR(16)): Fiscal year code (`FY-2026`).
  - `period_number` (INTEGER): Period index (1 to 12).
  - `period_name` (VARCHAR(32)): Period name (`January 2026`).
  - `calendar_year` (INTEGER): Calendar year (2026).
  - `calendar_month` (INTEGER): Calendar month (1).
- **PostgreSQL Mapping:** Table `fiscal_period`. Foreign key to `fiscal_year`.
- **Neo4j Connections:**
  - Node Label: `:Fiscal_Period`.
  - Outgoing Edges: `(:Fiscal_Period)-[:PART_OF_QUARTER]->(:Fiscal_Quarter)-[:PART_OF_YEAR]->(:Fiscal_Year)`.
  - Incoming Edges: `(:Journal_Entry)-[:POSTED_IN_PERIOD]->(:Fiscal_Period)`.

### 2.6 `datasets/foundations/currency.csv`, `unit_of_measure.csv`, `payment_terms.csv`, `incoterm.csv`
- **File Paths:**
  - [datasets/foundations/currency.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/currency.csv) (4 rows)
  - [datasets/foundations/unit_of_measure.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/unit_of_measure.csv) (7 rows)
  - [datasets/foundations/payment_terms.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/payment_terms.csv) (4 rows)
  - [datasets/foundations/incoterm.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/foundations/incoterm.csv) (4 rows)
- **What it Intends to Do:** Foundation D (Reference Dimensions). Standardizes ISO currencies, UNECE units of measure, commercial settlement terms, and shipping risk terms.
- **What it Achieves:** Prevents unstandardized string attributes in commercial contracts, purchase orders, invoices, and physical packaging.
- **Key Schemas:**
  - `currency`: `currency_id` (ISO code: INR, USD, EUR, GBP), `decimal_places`, `symbol`.
  - `unit_of_measure`: `uom_id` (EA, KG, L, G, ML, BOX, PALLET), `base_unit_id` (Self-referencing FK), `conversion_factor_to_base`.
  - `payment_terms`: `payment_term_id` (NET30, NET60, 2/10 NET30, COD), `net_days`, `discount_percentage`.
  - `incoterm`: `incoterm_id` (FOB, CIF, EXW, DDP), `risk_transfer_point`.
- **PostgreSQL Mapping:** Tables `currency`, `unit_of_measure`, `payment_terms`, `incoterm`.
- **Neo4j Connections:** Direct nodes `:Currency`, `:Unit_of_Measure`, `:Payment_Terms`, `:Incoterm` referenced by commercial transactions.

---

## 3. Governance & Enterprise Structure (`datasets/governance/`)

Defines corporate entities, subsidiary structures, and operational business units.

### 3.1 `enterprise_structure.csv`, `legal_entities.csv`, `business_units.csv`
- **File Paths:**
  - [datasets/governance/enterprise_structure.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/governance/enterprise_structure.csv) (1 row)
  - [datasets/governance/legal_entities.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/governance/legal_entities.csv) (2 rows)
  - [datasets/governance/business_units.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/governance/business_units.csv) (2 rows)
- **What it Intends to Do:** Encapsulates Domain 01 (Enterprise & Organization).
- **What it Achieves:** Establishes the corporate parent (`enterprise`), corporate legal entities registered with corporate affairs (`legal_entity`), and operational segments (`business_unit`).
- **Row Titles & Foreign Keys:**
  - `enterprise`: `enterprise_id`, `party_id` (FK to `party`), `corporate_name`, `headquarters_country_id`.
  - `legal_entity`: `legal_entity_id`, `enterprise_id` (FK to `enterprise`), `registered_name`, `cin` (Corporate Identity Number).
  - `business_unit`: `business_unit_id`, `legal_entity_id` (FK to `legal_entity`), `bu_name`, `currency_id` (FK to `currency`).
- **PostgreSQL Mapping:** Tables `enterprise`, `legal_entity`, `business_unit`.
- **Neo4j Connections:** `(:Business_Unit)-[:OWNED_BY]->(:Legal_Entity)-[:PART_OF_ENTERPRISE]->(:Enterprise)`.

---

## 4. Merchandise & Product Taxonomy (`datasets/masters/` & `datasets/merchandise/`)

The merchandise domain defines the complete 6-level taxonomy and physical SKU definitions.

```text
[department_master.csv] (12 Departments)
         │ 1:N
         ▼
[category_master.csv] (67 Categories)
         │ 1:N
         ▼
[subcategory_master.csv] (200 Subcategories)
         │ 1:N
         ▼
[product_family_master.csv] (1,453 Families)
         │ 1:N
         ▼
[product_master.csv] (3,458 Products)
         │ 1:N
         ▼
[sku_master.csv] (49,616 SKUs)
```

### 4.1 `datasets/masters/department_master.csv`
- **File Path:** [datasets/masters/department_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/department_master.csv)
- **Format & Size:** CSV | 12 rows | 427 bytes
- **What it Intends to Do:** Top-level merchandise division (Grocery, Fresh Produce, Apparel, Electronics, Personal Care, etc.).
- **What it Achieves:** Macro merchandise reporting and high-level inventory budget allocations.
- **Row Titles:** `DEPARTMENT_ID` (PK), `DEPARTMENT_NAME`.
- **PostgreSQL Mapping:** Table `merchandise_department` (`department_id`, `department_name`).
- **Neo4j Connections:** Node `:Merchandise_Department`. Target of `(:Category)-[:IN_DEPARTMENT]->(:Merchandise_Department)`.

### 4.2 `datasets/masters/category_master.csv`
- **File Path:** [datasets/masters/category_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/category_master.csv)
- **Format & Size:** CSV | 67 rows | 2,747 bytes
- **What it Intends to Do:** Commercial product categories (Dairy, Beverages, Men's Apparel, Kitchen Appliances, etc.).
- **What it Achieves:** Primary target for macro causal event impacts (e.g., festival demand lifts, heatwave beverage lifts).
- **Row Titles:** `CATEGORY_ID` (PK), `DEPARTMENT_ID` (FK to `department_master`), `CATEGORY_NAME`.
- **PostgreSQL Mapping:** Table `category` (`category_id`, `department_id`, `category_name`).
- **Neo4j Connections:** Node `:Category`. Outgoing: `(:Category)-[:IN_DEPARTMENT]->(:Merchandise_Department)`. Incoming: `(:Subcategory)-[:IN_CATEGORY]->(:Category)`, `(:Event)-[:IMPACTS]->(:Category)`.

### 4.3 `datasets/masters/subcategory_master.csv`
- **File Path:** [datasets/masters/subcategory_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/subcategory_master.csv)
- **Format & Size:** CSV | 200 rows | 6,311 bytes
- **What it Intends to Do:** Subcategory classification dividing categories by storage condition and velocity.
- **Row Titles:** `SUBCATEGORY_ID` (PK), `CATEGORY_ID` (FK to `category_master`), `SUBCATEGORY_NAME`.
- **PostgreSQL Mapping:** Table `subcategory` (`subcategory_id`, `category_id`, `subcategory_name`).
- **Neo4j Connections:** Node `:Subcategory`. Outgoing: `(:Subcategory)-[:IN_CATEGORY]->(:Category)`.

### 4.4 `datasets/masters/product_family_master.csv`
- **File Path:** [datasets/masters/product_family_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/product_family_master.csv)
- **Format & Size:** CSV | 1,453 rows | 50,477 bytes
- **What it Intends to Do:** Formulations and functionally substitutable product groups.
- **What it Achieves:** Governs cannibalization rules and substitution during stockouts.
- **Row Titles:** `FAMILY_ID` (PK), `SUBCATEGORY_ID` (FK to `subcategory_master`), `FAMILY_NAME`.
- **PostgreSQL Mapping:** Table `product_family` (`product_family_id`, `subcategory_id`, `family_name`).
- **Neo4j Connections:** Node `:Product_Family`. Outgoing: `(:Product_Family)-[:IN_SUBCATEGORY]->(:Subcategory)`.

### 4.5 `datasets/masters/product_master.csv`
- **File Path:** [datasets/masters/product_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/product_master.csv)
- **Format & Size:** CSV | 3,458 rows | 318,939 bytes
- **What it Intends to Do:** Commercial brand products (e.g., Brand X Premium Basmati Rice).
- **Row Titles:** `PRODUCT_ID` (PK), `FAMILY_ID` (FK to `product_family_master`), `PRODUCT_NAME`, `BRAND_ID`, `MANUFACTURER_ID`, `PRODUCT_TYPE`.
- **PostgreSQL Mapping:** Table `product`.
- **Neo4j Connections:** Node `:Product`. Outgoing: `(:Product)-[:BELONGS_TO_FAMILY]->(:Product_Family)`.

### 4.6 `datasets/masters/sku_master.csv` (and `datasets/merchandise/sku_master.csv`)
- **File Path:** [datasets/masters/sku_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/sku_master.csv)
- **Format & Size:** CSV | 49,616 rows | 7,418,813 bytes
- **What it Intends to Do:** Physical Stock Keeping Unit master. The atomic physical article in the supply chain.
- **What it Achieves:** Encapsulates all physical simulation parameters: pack size, shelf life, perishability, base cost, base retail price, and elasticity.
- **Row Titles (Columns):**
  - `SKU_ID` (VARCHAR(32), Primary Key): Canonical SKU code (`APP-CHI-00001` to `APP-CHI-49616`).
  - `PRODUCT_ID` (VARCHAR(32), Foreign Key): References `product_master.PRODUCT_ID`.
  - `SKU_NAME` (VARCHAR(255)): Item description.
  - `BASE_UNIT_COST` (FLOAT): Inbound wholesale cost.
  - `BASE_RETAIL_PRICE` (FLOAT): Standard baseline retail price.
  - `UNIT_OF_MEASURE` (VARCHAR(16)): Base unit (EA, KG, L, etc.).
  - `PACK_SIZE` (VARCHAR(32)): Physical packaging unit.
  - `SHELF_LIFE_DAYS` (INTEGER): Perishable expiration window (3 to 730 days).
  - `PERISHABILITY_TIER` (VARCHAR(16)): `ULTRA_FRESH`, `FRESH`, `AMBIENT_PERISHABLE`, `NON_PERISHABLE`.
  - `DEMAND_VOLATILITY` (FLOAT): Coefficient of variation for demand draws.
  - `SEASONALITY_PROFILE` (VARCHAR(32)): Reference to seasonal curve.
  - `WEATHER_SENSITIVITY` (VARCHAR(16)): `HIGH`, `MEDIUM`, `NONE`.
  - `FESTIVAL_AFFINITY` (VARCHAR(32)): Festival affinity tag.
  - `PROMOTION_SENSITIVITY` (FLOAT): Promo lift sensitivity.
  - `PRICE_ELASTICITY` (FLOAT): Price elasticity exponent (typically -0.8 to -2.5).
- **PostgreSQL Mapping:** Table `sku`. Non-polymorphic foreign keys to `product` and `unit_of_measure`.
- **Neo4j Connections:**
  - Node Label: `:SKU` (49,616 nodes).
  - Outgoing Edges: `(:SKU)-[:PART_OF_PRODUCT]->(:Product)`.
  - Incoming Edges: `(:Supplier)-[:SOURCES]->(:SKU)`, `(:Facility:Store)-[:ASSORTS]->(:SKU)`, `(:Inventory_Position)-[:HOLDS_SKU]->(:SKU)`.

### 4.7 `datasets/masters/store_sku_assortment.csv`
- **File Path:** [datasets/masters/store_sku_assortment.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/store_sku_assortment.csv)
- **Format & Size:** CSV | 346,238 rows | 13,000,630 bytes
- **What it Intends to Do:** Binds the 49,616 SKUs to the 16 retail stores according to store format tier (Hypermarkets carry ~35K SKUs, Express stores carry ~5K SKUs).
- **What it Achieves:** Governs shelf capacity, planogram facings, and minimum presentation stock.
- **Row Titles:** `STORE_ID` (FK to `store_master`), `SKU_ID` (FK to `sku_master`), `ASSORTMENT_TIER`, `ASSORTMENT_START_WEEK`, `ASSORTMENT_END_WEEK`, `ALLOCATED_SHELF_CAPACITY_UNITS`.
- **PostgreSQL Mapping:** Table `store_sku_assortment`. Composite primary key `(store_id, sku_id)`.
- **Neo4j Connections:** Relationship `(:Facility:Store)-[:ASSORTS {facing_qty, min_display_qty}]->(:SKU)` (346,238 edges).

### 4.8 `datasets/masters/replenishment_policy.csv`
- **File Path:** [datasets/masters/replenishment_policy.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/replenishment_policy.csv)
- **Format & Size:** CSV | 346,238 rows | 15,219,816 bytes
- **What it Intends to Do:** Parameterizes $(s, S)$ continuous review inventory control policies for every active store-SKU pairing.
- **What it Achieves:** Drives automated purchase requisition and replenishment orders when stock breaches reorder points.
- **Row Titles:** `STORE_ID`, `SKU_ID`, `REPLENISHMENT_METHOD` (MIN_MAX, PERIODIC_REVIEW), `REVIEW_PERIOD_WEEKS`, `SAFETY_STOCK_WEEKS`, `REORDER_POINT_UNITS`, `TARGET_MAX_UNITS`, `ORDER_QUANTITY_MULTIPLE`.
- **PostgreSQL Mapping:** Table `replenishment_policy`. Foreign keys to `facility` and `sku`.

### 4.9 `datasets/merchandise/price_history.parquet` (and `datasets/price_history.csv`)
- **File Path:** [datasets/merchandise/price_history.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/merchandise/price_history.parquet)
- **Format & Size:** Parquet / CSV | 2,580,032 rows | 15,417,408 bytes (Parquet) / 211MB (CSV)
- **What it Intends to Do:** Longitudinal weekly price facts across facility, SKU, and week coordinates.
- **What it Achieves:** Captures base price, promotional discounts, markdown events, and effective selling prices.
- **Row Titles:** `WEEK`, `SKU_ID`, `BASE_PRICE`, `SELLING_PRICE`, `DISCOUNT_PCT`, `PRICE_INDEX`, `PRICE_CHANGE_REASON`.
- **PostgreSQL Mapping:** Table `price_record`. Composite key `(facility_id, sku_id, week_id)`.
- **Neo4j Connections:** Node `:Price_Record` (2,580,032 nodes). Connected via `(:Price_Record)-[:PRICED_FOR]->(:SKU)`.

---

## 5. Physical Supply Network & Assets (`datasets/network/`)

Models physical buildings, storage capacities, transport lanes, and transit shipments.

### 5.1 `store_master.csv`, `warehouse_master.csv`, `facility_master.csv`
- **File Paths:**
  - [datasets/masters/store_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/store_master.csv) (16 stores)
  - [datasets/masters/warehouse_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/masters/warehouse_master.csv) (5 regional DCs)
  - [datasets/network/facility_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/network/facility_master.csv) (21 facilities)
- **What it Intends to Do:** Domain 07 (Warehousing) and Domain 08 (Store). Defines the physical footprint of the supply chain.
- **What it Achieves:**
  - Stores: 4 Hypermarkets (8,000 sqm), 6 Supermarkets (3,500 sqm), 4 Express (800 sqm), 2 Gourmet Boutiques (1,200 sqm).
  - Warehouses: 5 Regional DCs (`WH-001` to `WH-005`) with pallet capacities and cold-storage chambers.
- **Row Titles:**
  - `facility_master`: `facility_id` (PK), `facility_name`, `facility_category` (`RETAIL_STORE`, `DISTRIBUTION_CENTER`), `operating_status`.
  - `store_master`: `STORE_ID`, `STORE_NAME`, `STORE_FORMAT`, `REGION`, `STATE`, `CITY`, `TIER`, `PRIMARY_DC_ID`, `MAX_SHELF_CAPACITY_UNITS`.
  - `warehouse_master`: `WAREHOUSE_ID`, `WAREHOUSE_NAME`, `REGION`, `STATE`, `CITY`, `TOTAL_CAPACITY_PALLETS`, `INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK`.
- **PostgreSQL Mapping:** Table `facility` with single-table inheritance subtypes `store` and `warehouse`.
- **Neo4j Connections:**
  - Nodes: `:Store:Facility` (16 nodes) and `:Warehouse:Facility` (5 nodes).
  - Geographic Links: `(:Facility)-[:LOCATED_AT]->(:Location)`.

### 5.2 `datasets/network/store_warehouse_map.csv`
- **File Path:** [datasets/network/store_warehouse_map.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/network/store_warehouse_map.csv)
- **Format & Size:** CSV | 32 rows | 920 bytes
- **What it Intends to Do:** Replenishment routing network.
- **What it Achieves:** Links each of the 16 stores to a primary DC (1-day lead time) and a secondary emergency DC (2–3 day lead time).
- **Row Titles:** `STORE_ID` (FK to `store`), `WAREHOUSE_ID` (FK to `warehouse`), `ROUTE_PRIORITY` (`PRIMARY`, `SECONDARY`), `TRANSIT_TIME_DAYS`.
- **PostgreSQL Mapping:** Table `store_warehouse_map`.
- **Neo4j Connections:** Relationship `(:Facility:Store)-[:SERVICED_BY {priority, lead_time_days}]->(:Facility:Warehouse)` (32 edges).

### 5.3 `datasets/network/transport_lanes.csv`
- **File Path:** [datasets/network/transport_lanes.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/network/transport_lanes.csv)
- **Format & Size:** CSV | 35 rows | 1,456 bytes
- **What it Intends to Do:** Domain 06 (Logistics). Inter-facility transit corridors.
- **What it Achieves:** Specifies distances in km, freight rate cards, and transit times between facilities.
- **Row Titles:** `lane_id` (PK), `origin_facility_id` (FK), `destination_facility_id` (FK), `standard_transit_days`, `distance_km`, `is_active`.
- **PostgreSQL Mapping:** Table `transport_lane`.
- **Neo4j Connections:** Relationship `(:Facility)-[:LANE_TO {distance_km, transit_days}]->(:Facility)` (35 edges).

### 5.4 `datasets/network/physical_assets.csv`
- **File Path:** [datasets/network/physical_assets.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/network/physical_assets.csv)
- **Format & Size:** CSV | 150 rows | 9,695 bytes
- **What it Intends to Do:** Domain 23 (Assets). Models forklifts, cold-storage chillers, HVAC units, and point-of-sale terminals.
- **What it Achieves:** Enables operational twin disruption simulations (e.g., chiller breakdown causing perishables spoilage).
- **Row Titles:** `asset_id` (PK), `asset_name`, `asset_category` (`COLD_STORAGE_CHILLER`, `MATERIAL_HANDLING`), `facility_id` (FK), `operating_status`.
- **PostgreSQL Mapping:** Table `physical_asset`.
- **Neo4j Connections:** Node `:Physical_Asset` (150 nodes). Edge: `(:Physical_Asset)-[:INSTALLED_AT]->(:Facility)`.

### 5.5 `datasets/network/shipments.parquet` & `shipment_lines.parquet`
- **File Paths:**
  - [datasets/network/shipments.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/network/shipments.parquet) (18,000 rows | 155KB)
  - [datasets/network/shipment_lines.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/network/shipment_lines.parquet) (152,876 rows | 1.96MB)
- **What it Intends to Do:** Physical transit movement tracking.
- **What it Achieves:** Reconciles physical freight in transit between suppliers, warehouses, and stores.
- **Row Titles:**
  - `shipments`: `shipment_id` (PK), `origin_facility_id`, `destination_facility_id`, `carrier_id`, `shipment_status`, `shipped_date`, `delivered_date`.
  - `shipment_lines`: `shipment_line_id` (PK), `shipment_id` (FK), `sku_id` (FK), `shipped_quantity`, `received_quantity`.
- **PostgreSQL Mapping:** Tables `shipment` and `shipment_line`.
- **Neo4j Connections:** Nodes `:Shipment` (18,000) and `:Shipment_Line` (152,876). Edges: `(:Shipment_Line)-[:PART_OF_SHIPMENT]->(:Shipment)`.

---

## 6. Sourcing & Supplier Network (`datasets/sourcing/`)

Defines qualified vendors, sourcing allocations, and commercial contracts.

### 6.1 `datasets/sourcing/supplier_profiles.csv` (and `datasets/sourcing/carrier_profiles.csv`)
- **File Paths:**
  - [datasets/sourcing/supplier_profiles.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/sourcing/supplier_profiles.csv) (200 suppliers)
  - [datasets/sourcing/carrier_profiles.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/sourcing/carrier_profiles.csv) (25 carriers)
  - [datasets/sourcing/employee_profiles.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/sourcing/employee_profiles.csv) (300 employees)
  - [datasets/sourcing/commercial_contracts.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/sourcing/commercial_contracts.csv) (225 contracts)
- **What it Intends to Do:** Domain 03 (Sourcing) and Domain 06 (Logistics). Extends base `party` entities into operational supplier, carrier, and labor profiles.
- **Row Titles (Supplier Profiles):** `supplier_profile_id` (PK), `party_id` (FK to `party`), `vendor_tier`, `payment_term_id` (FK), `default_currency_id` (FK), `incoterm_id` (FK), `status`.
- **PostgreSQL Mapping:** Table `supplier_profile` and `carrier_profile`.
- **Neo4j Connections:** Node `:Supplier_Profile` (200 nodes). Edge: `(:Supplier_Profile)-[:BELONGS_TO_PARTY]->(:Party)`.

### 6.2 `datasets/sourcing/supplier_sku_map.csv` (and `datasets/masters/supplier_sku_map.csv`)
- **File Path:** [datasets/sourcing/supplier_sku_map.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/sourcing/supplier_sku_map.csv)
- **Format & Size:** CSV | 99,232 rows | 6,278,309 bytes
- **What it Intends to Do:** Sourcing allocation matrix.
- **What it Achieves:** Establishes exactly 2 qualified suppliers per SKU across all 49,616 SKUs ($49,616 \times 2 = 99,232$ sourcing links). Defines minimum order quantities (MOQ), lead times, purchase costs, and primary supplier designation.
- **Row Titles (Columns):**
  - `SUPPLIER_ID` (VARCHAR(32), Foreign Key): References `supplier_profile.supplier_profile_id`.
  - `SKU_ID` (VARCHAR(32), Foreign Key): References `sku_master.SKU_ID`.
  - `SUPPLIER_SKU` (VARCHAR(64)): Vendor's internal item catalog number.
  - `PURCHASE_COST` (FLOAT): Negotiated wholesale purchase price.
  - `MOQ_UNITS` (INTEGER): Minimum order quantity (e.g., 24, 48, 100 units).
  - `LEAD_TIME_DAYS` (INTEGER): Contractual order fulfillment lead time (1 to 21 days).
  - `ORDER_MULTIPLE` (INTEGER): Case pack or batch multiple.
  - `PRIMARY_FLAG` (BOOLEAN): 1 for primary supplier, 0 for secondary backup.
  - `ACTIVE_FLAG` (BOOLEAN): Operational status.
- **PostgreSQL Mapping:** Table `supplier_sku_map`. Composite primary key `(supplier_profile_id, sku_id)`.
- **Neo4j Connections:** Relationship `(:Supplier_Profile)-[:SOURCES {unit_cost, minimum_order_qty, lead_time_days, is_preferred}]->(:SKU)` (99,232 edges).

---

## 7. Procurement Pipeline (`datasets/procurement/`)

Models commercial replenishment orders placed with external suppliers.

### 7.1 `datasets/procurement/purchase_orders.parquet` & `po_lines.parquet`
- **File Paths:**
  - [datasets/procurement/purchase_orders.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/procurement/purchase_orders.parquet) (15,000 orders | 244KB)
  - [datasets/procurement/po_lines.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/procurement/po_lines.parquet) (90,227 lines | 2.24MB)
- **What it Intends to Do:** Domain 05 (Procurement). Tracks legally binding replenishment commitments.
- **What it Achieves:** Forms the baseline for upstream physical receipts and downstream supplier invoicing.
- **Row Titles:**
  - `purchase_orders`: `purchase_order_id` (PK), `supplier_profile_id` (FK), `destination_facility_id` (FK), `order_date`, `expected_delivery_date`, `total_amount`, `order_status`.
  - `po_lines`: `po_line_id` (PK), `purchase_order_id` (FK), `sku_id` (FK), `ordered_quantity`, `unit_cost`, `line_amount`.
- **PostgreSQL Mapping:** Tables `purchase_order` and `po_line`.
- **Neo4j Connections:**
  - Nodes: `:Purchase_Order` (15,000) and `:PO_Line` (90,227).
  - Edges: `(:PO_Line)-[:ORDERED_IN]->(:Purchase_Order)`, `(:PO_Line)-[:FOR_SKU_POLINE]->(:SKU)`.

---

## 8. Physical Inventory & Warehouse Receiving (`datasets/inventory/`)

Maintains stock balances and tracks warehouse receiving docks.

### 8.1 `datasets/inventory/goods_receipts.parquet` & `goods_receipt_lines.parquet`
- **File Paths:**
  - [datasets/inventory/goods_receipts.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/inventory/goods_receipts.parquet) (15,000 receipts | 211KB)
  - [datasets/inventory/goods_receipt_lines.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/inventory/goods_receipt_lines.parquet) (89,871 lines | 1.89MB)
- **What it Intends to Do:** Inbound physical dock receiving inspection logs.
- **What it Achieves:** Reconciles physical deliveries against PO lines, recording accepted vs. rejected quantities.
- **Row Titles:**
  - `goods_receipts`: `goods_receipt_id` (PK), `purchase_order_id` (FK), `facility_id` (FK), `receipt_date`, `receipt_status`.
  - `goods_receipt_lines`: `goods_receipt_line_id` (PK), `goods_receipt_id` (FK), `po_line_id` (FK), `sku_id` (FK), `received_quantity`, `accepted_quantity`, `rejected_quantity`.
- **PostgreSQL Mapping:** Tables `goods_receipt` and `goods_receipt_line`.
- **Neo4j Connections:**
  - Nodes: `:Goods_Receipt` (15,000) and `:Goods_Receipt_Line` (72,917).
  - Edges: `(:Goods_Receipt_Line)-[:RECEIVED_IN]->(:Goods_Receipt)`, `(:Goods_Receipt_Line)-[:FULFILLS_PO_LINE]->(:PO_Line)`.

### 8.2 `datasets/inventory/inventory_positions.parquet` (and `datasets/inventory_state.csv`)
- **File Path:** [datasets/inventory/inventory_positions.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/inventory/inventory_positions.parquet)
- **Format & Size:** Parquet / CSV | 99,232 rows | 542KB (Parquet) / 9.2MB (CSV)
- **What it Intends to Do:** Domain 09 (Inventory). Snapshot of physical stock on hand.
- **What it Achieves:** Models opening stock across all 49,616 SKUs at the 2 anchor facilities (`WH-001` and `STR-001`), confirming zero negative stock and zero bucket mismatches.
- **Row Titles:**
  - `SKU` (`sku_id`, FK to `sku_master`).
  - `Location_ID` (`facility_id`, FK to `facility`).
  - `Quantity_On_Hand` (INTEGER): Physical stock in building.
  - `Reorder_Point` (INTEGER): Replenishment trigger.
  - `Target_Safety_Stock` (INTEGER): Buffer stock.
  - `Shrinkage_Rate` (FLOAT): Estimated shrink/damage factor.
  - `As_Of_Date` (DATE): Snapshot timestamp.
- **PostgreSQL Mapping:** Table `inventory_position` (`position_id`, `facility_id`, `sku_id`, `quantity_on_hand`, `quantity_reserved`, `quantity_available`).
- **Neo4j Connections:**
  - Node Label: `:Inventory_Position` (99,232 nodes).
  - Edges: `(:Inventory_Position)-[:LOCATED_AT]->(:Facility)` (99,232 edges), `(:Inventory_Position)-[:HOLDS_SKU]->(:SKU)` (99,232 edges).

---

## 9. Retail Commerce & Customer Transactions (`datasets/commerce/`)

Captures retail customer demand across physical point-of-sale registers and digital channels.

### 9.1 `sales_channels.csv`, `sales_transactions.parquet`, `sales_lines.parquet`
- **File Paths:**
  - [datasets/commerce/sales_channels.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/commerce/sales_channels.csv) (4 channels)
  - [datasets/commerce/sales_transactions.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/commerce/sales_transactions.parquet) (50,000 transactions | 1.8MB)
  - [datasets/commerce/sales_lines.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/commerce/sales_lines.parquet) (200,035 lines | 5.2MB)
- **What it Intends to Do:** Domain 11 (Commerce) and Domain 12 (Orders). Point-of-sale customer checkouts.
- **What it Achieves:** Records actual customer purchases, tax breakdowns, and basket item combinations.
- **Row Titles:**
  - `sales_transactions`: `sales_transaction_id` (PK), `sales_channel_id` (FK), `facility_id` (FK), `transaction_date`, `subtotal_amount`, `tax_amount`, `total_amount`, `payment_status`.
  - `sales_lines`: `sales_line_id` (PK), `sales_transaction_id` (FK), `sku_id` (FK), `quantity`, `unit_price`, `line_amount`.
- **PostgreSQL Mapping:** Tables `sales_transaction` and `sales_line`.
- **Neo4j Connections:**
  - Nodes: `:Sales_Transaction` (50,000) and `:Sales_Line` (200,035).
  - Edges: `(:Sales_Line)-[:PART_OF_TRANSACTION]->(:Sales_Transaction)`, `(:Sales_Line)-[:FOR_SKU_SALES]->(:SKU)`.

---

## 10. Financial Settlement & General Ledger (`datasets/finance/`)

Models commercial billing, three-way matching, payments, and double-entry accounting.

### 10.1 `datasets/finance/supplier_invoices.parquet` & `customer_invoices.parquet`
- **File Paths:**
  - [datasets/finance/supplier_invoices.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/supplier_invoices.parquet) (15,000 supplier invoices)
  - [datasets/finance/customer_invoices.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/customer_invoices.parquet) (50,000 customer invoices)
  - [datasets/finance/supplier_invoice_lines.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/supplier_invoice_lines.parquet) (75,268 supplier invoice lines)
- **What it Intends to Do:** Models commercial billing across both supply (Accounts Payable) and demand (Accounts Receivable).
- **What it Achieves:** Inbound billing records matched against POs and Goods Receipts, alongside customer checkout invoices.
- **Population & Realization Resolution:**
  - `supplier_invoices.parquet`: Exactly **15,000 supplier invoices** ($15,000$ rows in table `supplier_invoice`).
  - `customer_invoices.parquet`: Exactly **50,000 customer invoices** ($50,000$ rows in table `customer_invoice`).
  - **Relational Ingestion:** Ingested into unified relational table `invoice` ($15,000 + 50,000 = \mathbf{65,000}$ rows in table `invoice`, partitioned by `invoice_type IN ('SUPPLIER', 'CUSTOMER')`).
  - **Neo4j Materialization:** `nodes_invoice.csv` exports `SELECT * FROM invoice` (exactly **65,000 nodes**), with multi-label realization `:Invoice:Supplier_Invoice` (15K) and `:Invoice:Customer_Invoice` (50K), guaranteeing 1:1 parity between relational `invoice` rows and graph `:Invoice` nodes.
- **Row Titles (Supplier Invoices):** `invoice_id` (PK), `invoice_number`, `supplier_profile_id` (FK), `purchase_order_id` (FK), `invoice_date`, `due_date`, `total_amount`, `status`.
- **PostgreSQL Mapping:** Tables `supplier_invoice`, `customer_invoice`, and unified `invoice`.
- **Neo4j Connections:** Nodes `:Invoice` (65,000 total nodes) and `:Supplier_Invoice_Line` (66,673 nodes).

### 10.2 `datasets/finance/three_way_match_records.parquet`
- **File Path:** [datasets/finance/three_way_match_records.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/three_way_match_records.parquet)
- **Format & Size:** Parquet | 75,268 rows (60,965 active reconciliations) | 2,587,495 bytes
- **What it Intends to Do:** Domain 05 / 18 Audit Entity. Automated Three-Way Matching.
- **What it Achieves:** Simultaneously links `po_line`, `goods_receipt_line`, and `supplier_invoice_line`, auditing quantity variances and price variances before payment approval.
- **Row Titles (Columns):**
  - `match_id` (VARCHAR(32), Primary Key): Unique audit record identifier.
  - `po_line_id` (VARCHAR(32), Foreign Key): References `po_line.po_line_id`.
  - `goods_receipt_line_id` (VARCHAR(32), Foreign Key): References `goods_receipt_line.goods_receipt_line_id`.
  - `invoice_line_id` (VARCHAR(32), Foreign Key): References `supplier_invoice_line.invoice_line_id`.
  - `po_quantity` (INTEGER): Units authorized on PO.
  - `received_quantity` (INTEGER): Units physically received at dock.
  - `invoiced_quantity` (INTEGER): Units billed by vendor.
  - `po_unit_price` (DECIMAL): Contracted price.
  - `invoiced_unit_price` (DECIMAL): Billed price.
  - `quantity_variance` (INTEGER): $\text{Invoiced} - \text{Received}$.
  - `price_variance` (DECIMAL): $\text{Invoiced Price} - \text{PO Price}$.
  - `match_status` (VARCHAR(16)): `PERFECT_MATCH`, `QTY_VARIANCE`, `PRICE_VARIANCE`, `DISCREPANCY`.
  - `verified_at` (TIMESTAMP): Automated audit timestamp.
- **PostgreSQL Mapping:** Table `three_way_match_record`. 3 explicit non-polymorphic foreign keys.
- **Neo4j Connections:**
  - Node Label: `:Three_Way_Match_Record` (60,965 nodes).
  - Outgoing Edges:
    - `(:Three_Way_Match_Record)-[:MATCHES_PO]->(:PO_Line)`
    - `(:Three_Way_Match_Record)-[:MATCHES_RECEIPT]->(:Goods_Receipt_Line)`
    - `(:Three_Way_Match_Record)-[:MATCHES_INVOICE]->(:Supplier_Invoice_Line)`

### 10.3 `payments.parquet` & `payment_allocations.parquet`
- **File Paths:**
  - [datasets/finance/payments.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/payments.parquet) (65,000 payments)
  - [datasets/finance/payment_allocations.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/payment_allocations.parquet) (65,000 allocations)
- **What it Intends to Do:** Cash disbursement and settlement.
- **What it Achieves:** Binds payments to specific invoices via allocation records, supporting partial payments and discounts.
- **PostgreSQL Mapping:** Tables `payment` and `payment_allocation`.
- **Neo4j Connections:** Node `:Payment` (65,000 nodes, carrying subtype labels `:Supplier_Payment:Payment` [15,000] and `:Customer_Payment:Payment` [50,000]). Relationship: `(:Payment)-[:ALLOCATED_TO]->(:Invoice)` (65,000 edges), specializing to `(:Supplier_Payment)-[:ALLOCATED_TO]->(:Supplier_Invoice)` and `(:Customer_Payment)-[:ALLOCATED_TO]->(:Customer_Invoice)`.

### 10.4 `chart_of_accounts.csv`, `gl_accounts.csv`, `journal_entries.parquet`, `journal_lines.parquet`
- **File Paths:**
  - [datasets/finance/chart_of_accounts.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/chart_of_accounts.csv) (1 row)
  - [datasets/finance/gl_accounts.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/gl_accounts.csv) (6 accounts)
  - [datasets/finance/journal_entries.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/journal_entries.parquet) (25,000 entries)
  - [datasets/finance/journal_lines.parquet](file:///d:/projects/SCOF_V1/SCOF/datasets/finance/journal_lines.parquet) (50,000 lines)
- **What it Intends to Do:** Domain 18 (Finance). Double-entry general ledger.
- **What it Achieves:** Enforces strict financial equilibrium ($\sum \text{Debits} = \sum \text{Credits} = \text{INR } 627,894,009.36$ with diff = 0.0000).
- **Key Accounts:** Cash (1010), Inventory (1200), Accounts Payable (2010), Revenue (4010), Cost of Goods Sold (5010), Operating Expense (6010).
- **PostgreSQL Mapping:** Tables `chart_of_accounts`, `gl_account`, `journal_entry`, `journal_line`.
- **Neo4j Connections:**
  - Nodes: `:Journal_Entry` (25,000), `:Journal_Line` (50,000), `:GL_Account` (6).
  - Edges: `(:Journal_Line)-[:LINE_OF_JOURNAL]->(:Journal_Entry)`, `(:Journal_Line)-[:POSTED_TO]->(:GL_Account)`.

---

## 11. Causal Shock & Exogenous Events (`datasets/advanced_events/` & `datasets/demand/`)

Governs external causal drivers that perturb consumer demand and supply network operations.

### 11.1 `datasets/advanced_events/event_master.csv`
- **File Path:** [datasets/advanced_events/event_master.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/advanced_events/event_master.csv)
- **Format & Size:** CSV | 174 rows | 21,192 bytes
- **What it Intends to Do:** Domain 21 (Demand). Master repository of causal events.
- **What it Achieves:** Categorizes festivals (Diwali, Eid, Christmas), seasonal phenomena (Monsoon, Summer Heatwave), commercial promotions (Big Billion Day, End of Season Sale), and physical disruptions (Port Strike, Transport Blockade).
- **Row Titles:** `Event_ID` (PK), `Event_Name`, `Event_Type`, `Sub_Type`, `Region`, `Calendar_Anchor`, `Annual_Week_Peak`, `Typical_Start_Week`, `Typical_End_Week`, `Lead_Time_Weeks`, `Decay_Weeks`, `Category_Impact_Keywords`, `Impact_Profile`, `Demand_Multiplier`, `Weather_Sensitivity`.
- **PostgreSQL Mapping:** Table `event` (and `event_instance`).
- **Neo4j Connections:** Node `:Event` (174 nodes). Outgoing: `(:Event)-[:IMPACTS]->(:Category)`, `(:Event)-[:INTERACTS_WITH]->(:Event)`.

### 11.2 `datasets/advanced_events/event_impact_matrix.csv`
- **File Path:** [datasets/advanced_events/event_impact_matrix.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/advanced_events/event_impact_matrix.csv)
- **Format & Size:** CSV | 1,107 rows | 58,276 bytes
- **What it Intends to Do:** Direct causal lift/drop vectors targeting specific levels of the merchandise taxonomy.
- **What it Achieves:** Directs demand multipliers to `CATEGORY`, `SUBCATEGORY`, or `PRODUCT_FAMILY`.
- **Row Titles:** `EVENT_ID` (FK to `event_master`), `TARGET_LEVEL`, `TARGET_ID` (FK to taxonomy), `IMPACT_DIRECTION` (POSITIVE, NEGATIVE), `DEMAND_MULTIPLIER` (e.g., 1.45 for +45%), `IMPACT_STRENGTH`, `APPLY_MODE`.
- **PostgreSQL Mapping:** Table `event_impact`.
- **Neo4j Connections:** Relationship `(:Event)-[:IMPACTS {target_level, lift_multiplier}]->(:Category / :Subcategory / :Product_Family)` (1,107 edges).

### 11.3 `datasets/advanced_events/event_interactions.csv`
- **File Path:** [datasets/advanced_events/event_interactions.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/advanced_events/event_interactions.csv)
- **Format & Size:** CSV | 1,977 rows | 114,176 bytes
- **What it Intends to Do:** Models non-linear event co-occurrence rules.
- **What it Achieves:** Prevents unrealistic compounding when multiple events coincide (e.g., dampening combined lift when Diwali coincides with a Heatwave).
- **Row Titles:** `EVENT_ID_1`, `EVENT_ID_2`, `INTERACTION_TYPE` (COMPOUNDING, CANNIBALIZATION, DAMPENING, OVERRIDE), `INTERACTION_CAP`, `DESCRIPTION`.
- **PostgreSQL Mapping:** Table `event_interaction`.
- **Neo4j Connections:** Relationship `(:Event)-[:INTERACTS_WITH {interaction_type, dampening_factor}]->(:Event)` (1,977 edges).

### 11.4 `datasets/advanced_events/regional_event_weights.csv`
- **File Path:** [datasets/advanced_events/regional_event_weights.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/advanced_events/regional_event_weights.csv)
- **Format & Size:** CSV | 554 rows | 9,150 bytes
- **What it Intends to Do:** Regional geographic calibration.
- **What it Achieves:** Scales event intensity based on cultural and geographic relevance (e.g., Durga Puja has weight 1.5 in East Zone, but 0.8 in South Zone).
- **Transformation & Realization Semantics (554 Rows to 174 Edges):**
  - **Source File (`regional_event_weights.csv`):** Contains **554 raw rows** defining multi-region weights across macro geographic zones and states (PAN_INDIA, North, South, East, West).
  - **Relational Ingestion (`regional_event_weight`):** Because the anchor facilities (`WH-001`, `STR-001`) are physically situated in `ZONE_SOUTH`, the relational loader filters and localizes weights to the active anchor zone (`ZONE_SOUTH`), producing exactly **174 distinct event weight rows** (one per event for `ZONE_SOUTH`), with zero duplicate `(event_id, zone_id)` pairs.
  - **Graph Materialization (`rel_regional_weight.csv`):** Materialized directly from the relational table `regional_event_weight`, exporting exactly **174 edges** (`(:Event)-[:REGIONAL_WEIGHT]->(:Zone_Macro_Region)`).
- **Row Titles:** `EVENT_ID`, `GEOGRAPHIC_LEVEL` (`ZONE`, `STATE`), `GEOGRAPHIC_TARGET` (`NORTH_ZONE`, `WEST_ZONE`), `GEOGRAPHIC_WEIGHT`.
- **PostgreSQL Mapping:** Table `regional_event_weight` (174 rows in active execution harness).
- **Neo4j Connections:** Relationship `(:Event)-[:REGIONAL_WEIGHT {weight_multiplier}]->(:Zone_Macro_Region)` (174 edges).

### 11.5 `datasets/demand/weather_weekly.csv` (and `datasets/weather_weekly.csv`)
- **File Path:** [datasets/demand/weather_weekly.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/demand/weather_weekly.csv)
- **Format & Size:** CSV | 312 rows | 24KB
- **What it Intends to Do:** Weekly regional weather conditions across 6 macro regions over 52 weeks.
- **Row Titles:** `WEEK`, `REGION`, `AVG_TEMPERATURE_C`, `TEMP_ANOMALY_C`, `RAINFALL_MM`, `RAINFALL_ANOMALY_MM`, `HUMIDITY_PCT`, `HEAT_INDEX`, `EXTREME_WEATHER_FLAG`, `DERIVED_REGIME` (NORMAL, HEATWAVE, MONSOON_SURGE, COLD_WAVE).
- **PostgreSQL Mapping:** Table `weather_weekly`.

---

## 12. Simulation Ground Truth & Root Datasets (`datasets/`)

The root of `datasets/` contains the massive simulation universe, historical pricing, promotions, and the 67 shopping mall retail catalogs.

### 12.1 `datasets/weekly_demand_history_v2.csv`
- **File Path:** [datasets/weekly_demand_history_v2.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/weekly_demand_history_v2.csv)
- **Format & Size:** CSV | 18,004,376 rows | ~1.4GB
- **What it Intends to Do:** The authoritative, unconstrained ground-truth simulation universe. Models 52 retail weeks across 346,238 active store-SKU pairings.
- **What it Achieves:** Solves the naive sales generator problem by decoupling customer demand from inventory availability:
  $$\text{Observed Sales} = \min(\text{Latent Demand}, \text{On-Hand Stock})$$
  $$\text{Lost Sales} = \max(0, \text{Latent Demand} - \text{Observed Sales})$$
  $$\text{Demand Conservation Invariant:} \quad \text{Latent} = \text{Observed} + \text{Lost} \quad (\text{0 violations})$$
  $$\text{Mass Balance Invariant:} \quad \text{Closing} = \text{Opening} + \text{Receipts} - \text{Sales} - \text{Spoiled} \quad (\text{0 violations})$$
- **Row Titles (17 Columns):**
  1. `WEEK_ID`: Retail week (202601 to 202652).
  2. `STORE_ID`: Store identifier (`STR-001` to `STR-016`).
  3. `SKU_ID`: SKU identifier (`APP-CHI-00001` to `APP-CHI-49616`).
  4. `BASE_DEMAND`: Intrinsic customer demand.
  5. `SEASONAL_FACTOR`: Annual seasonality multiplier (0.80 to 1.35).
  6. `FESTIVAL_FACTOR`: Compounded festival event lift (0.40 to 2.85).
  7. `WEATHER_FACTOR`: Weather regime multiplier (0.85 to 1.30).
  8. `PRICE_FACTOR`: Price response factor ($e^{\epsilon \cdot \Delta p}$).
  9. `PROMO_FACTOR`: Promotional display lift (1.00 to 1.75).
  10. `LATENT_DEMAND`: Total unconstrained customer demand.
  11. `OPENING_INVENTORY`: Stock at week commencement.
  12. `PO_RECEIPTS`: Inbound replenishment receipts.
  13. `SPOILED_UNITS`: Discarded expired units.
  14. `OBSERVED_SALES`: Physically bounded units sold.
  15. `LOST_SALES`: Unfulfilled demand due to shelf stockout.
  16. `CLOSING_INVENTORY`: Physical stock at week close.
  17. `STOCKOUT_FLAG`: 1 if `CLOSING_INVENTORY == 0`, else 0.
- **PostgreSQL Mapping:** Ingested into `demand_observation` (active 50K runtime sample in `datasets/scof_relational.db`; full 18M rows stored in Parquet fact store).
- **Neo4j Connections:** Node `:Demand_Observation` (50,000 nodes). Edge: `(:Demand_Observation)-[:OBSERVED_AT]->(:Facility:Store)`, `(:Demand_Observation)-[:OBSERVED_FOR]->(:SKU)`.

### 12.2 `datasets/promotions.csv`
- **File Path:** [datasets/promotions.csv](file:///d:/projects/SCOF_V1/SCOF/datasets/promotions.csv)
- **Format & Size:** CSV | 15 rows | 2.1KB
- **What it Intends to Do:** Domain 15 (Promotions). Marketing campaigns (e.g., "Weekend Mega Saver", "Diwali Bonanza").
- **Row Titles:** `PROMO_ID`, `PROMO_NAME`, `DISCOUNT_PCT`, `START_WEEK`, `END_WEEK`, `TARGET_DEPARTMENT`, `MARKETING_CHANNEL`.
- **PostgreSQL Mapping:** Table `promotions`.

### 12.3 The 67 Retail Category Catalogs (`datasets/*.csv`)
- **File Paths:** 67 individual CSVs in `datasets/` (e.g., `GROCERY & FOOD STAPLES.csv`, `DAIRY & REFRIGERATED PRODUCTS.csv`, `BEVERAGES.csv`, `APPAREL – MEN.csv`, `CONSUMER ELECTRONICS.csv`, etc.).
- **Format & Size:** CSV | 49,616 total SKUs distributed across 67 files | ~15MB total
- **What it Intends to Do:** Source domain catalogs representing the physical retail complex / shopping mall merchandise hierarchy.
- **What it Achieves:** Serves as the seed data from which the normalized 6-level taxonomy was compiled and cross-validated.

---

## 13. Materialized Neo4j Knowledge Graph (`datasets/neo4j_graph/`)

The property graph was materialized downstream from the relational database to enable graph queries, multi-echelon lineage tracing, and causal impact propagation.

### 13.1 High-Level Graph Topology
- **Total Materialized Nodes:** **3,728,199 nodes**
- **Total Materialized Edges:** **2,104,514 relationships**
- **Import Script:** [datasets/neo4j_graph/import_neo4j_graph.cql](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/import_neo4j_graph.cql) (contains all constraints, node loaders, and edge loaders)

### 13.2 Summary of Node CSVs (`nodes_*.csv`)

| Node File | Rows | Neo4j Label | Key Attributes | PostgreSQL Source Table |
| :--- | :---: | :--- | :--- | :--- |
| `nodes_party_org.csv` | 228 | `:Organization:Party` | `party_id`, `party_code`, `legal_name`, `status` | `organization` + `party` |
| `nodes_party_person.csv` | 2 | `:Person:Party` | `party_id`, `party_code`, `legal_name`, `status` | `person` + `party` |
| `nodes_facility_store.csv` | 16 | `:Store:Facility` | `facility_id`, `facility_name`, `operating_status` | `store` + `facility` |
| `nodes_facility_warehouse.csv`| 5 | `:Warehouse:Facility`| `facility_id`, `facility_name`, `operating_status` | `warehouse` + `facility`|
| `nodes_category.csv` | 67 | `:Category` | `category_id`, `category_name`, `storage_condition` | `category` |
| `nodes_sku.csv` | 49,616 | `:SKU` | `sku_id`, `barcode_ean13`, `package_size`, `shelf_life_days`| `sku` |
| `nodes_inventory_position.csv`| 99,232 | `:Inventory_Position`| `position_id`, `facility_id`, `sku_id`, `quantity_on_hand`| `inventory_position` |
| `nodes_purchase_order.csv` | 15,000 | `:Purchase_Order` | `po_id`, `supplier_profile_id`, `order_date`, `total_amount` | `purchase_order` |
| `nodes_po_line.csv` | 90,227 | `:PO_Line` | `po_line_id`, `ordered_qty`, `unit_price`, `line_total` | `po_line` |
| `nodes_shipment.csv` | 18,000 | `:Shipment` | `shipment_id`, `carrier_id`, `departure_time`, `status` | `shipment` |
| `nodes_shipment_line.csv` | 152,876 | `:Shipment_Line` | `shipment_line_id`, `shipped_qty` | `shipment_line` |
| `nodes_goods_receipt.csv` | 15,000 | `:Goods_Receipt` | `goods_receipt_id`, `receipt_date`, `receipt_status` | `goods_receipt` |
| `nodes_goods_receipt_line.csv`| 72,917 | `:Goods_Receipt_Line`| `goods_receipt_line_id`, `received_qty`, `accepted_qty` | `goods_receipt_line` |
| `nodes_invoice.csv` | 65,000 | `:Invoice` (`:Supplier_Invoice` [15K] + `:Customer_Invoice` [50K]) | `invoice_id`, `invoice_number`, `total_amount`, `status` | `invoice` (`supplier_invoice` [15K] + `customer_invoice` [50K]) |
| `nodes_supplier_invoice_line.csv`| 66,673| `:Supplier_Invoice_Line`| `invoice_line_id`, `invoiced_qty`, `unit_price`, `line_total`| `supplier_invoice_line`|
| `nodes_three_way_match_record.csv`| 60,965| `:Three_Way_Match_Record`| `match_id`, `ordered_qty`, `invoiced_qty`, `match_status` | `three_way_match_record`|
| `nodes_payment.csv` | 65,000 | `:Payment` (`:Supplier_Payment` [15K] + `:Customer_Payment` [50K]) | `payment_id`, `payment_date`, `amount`, `status` | `payment` (15K supplier + 50K customer) |
| `nodes_sales_transaction.csv` | 50,000 | `:Sales_Transaction` | `transaction_id`, `transaction_timestamp`, `total_amount`| `sales_transaction` |
| `nodes_sales_line.csv` | 200,035 | `:Sales_Line` | `sales_line_id`, `quantity`, `unit_price`, `net_sales` | `sales_line` |
| `nodes_price_record.csv` | 2,580,032| `:Price_Record` | `price_record_id`, `sku_id`, `facility_id`, `amount` | `price_record` |
| `nodes_demand_observation.csv`| 50,000 | `:Demand_Observation`| `observation_id`, `observed_sales`, `lost_sales` | `demand_observation` |
| `nodes_journal_entry.csv` | 25,000 | `:Journal_Entry` | `journal_entry_id`, `posting_date`, `total_debit`, `is_posted`| `journal_entry` |
| `nodes_journal_line.csv` | 50,000 | `:Journal_Line` | `journal_line_id`, `debit_amount`, `credit_amount` | `journal_line` |
| `nodes_gl_account.csv` | 6 | `:GL_Account` | `gl_account_id`, `account_name`, `account_type` | `gl_account` |
| `nodes_event.csv` | 174 | `:Event` | `event_id`, `event_name`, `event_type`, `peak_week` | `event` |
| `nodes_physical_asset.csv` | 150 | `:Physical_Asset` | `physical_asset_id`, `asset_name`, `category_id`, `status` | `physical_asset` |

### 13.3 Summary of Relationship CSVs (`rel_*.csv`)

| Relationship File | Count | Relationship Type | Start Node (:START_ID) | End Node (:END_ID) | Edge Properties |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `rel_sources.csv` | 99,232 | `[:SOURCES]` | `:Supplier_Profile` | `:SKU` | `unit_cost`, `minimum_order_qty`, `lead_time_days`, `is_preferred` |
| `rel_assorts.csv` | 346,238 | `[:ASSORTS]` | `:Facility:Store` | `:SKU` | `facing_qty`, `min_display_qty`, `status` |
| `rel_serviced_by.csv` | 32 | `[:SERVICED_BY]` | `:Facility:Store` | `:Facility:Warehouse` | `priority`, `lead_time_days`, `distance_km`, `is_primary` |
| `rel_lane_to.csv` | 35 | `[:LANE_TO]` | `:Facility` | `:Facility` | `standard_transit_days`, `distance_km`, `standard_freight_cost` |
| `rel_invpos_facility.csv` | 99,232 | `[:LOCATED_AT]` | `:Inventory_Position` | `:Facility` | none |
| `rel_invpos_sku.csv` | 99,232 | `[:HOLDS_SKU]` | `:Inventory_Position` | `:SKU` | none |
| `rel_poline_po.csv` | 90,227 | `[:ORDERED_IN]` | `:PO_Line` | `:Purchase_Order` | none |
| `rel_poline_sku.csv` | 90,227 | `[:FOR_SKU_POLINE]` | `:PO_Line` | `:SKU` | none |
| `rel_grl_gr.csv` | 72,917 | `[:RECEIVED_IN]` | `:Goods_Receipt_Line`| `:Goods_Receipt` | none |
| `rel_grl_poline.csv` | 72,917 | `[:FULFILLS_PO_LINE]`| `:Goods_Receipt_Line`| `:PO_Line` | none |
| `rel_sil_inv.csv` | 66,673 | `[:INVOICED_IN]` | `:Supplier_Invoice_Line`| `:Supplier_Invoice`| none |
| `rel_sil_poline.csv` | 66,673 | `[:INVOICING_PO_LINE]`| `:Supplier_Invoice_Line`| `:PO_Line`| none |
| `rel_matches_po.csv` | 60,965 | `[:MATCHES_PO]` | `:Three_Way_Match_Record`| `:PO_Line` | `ordered_qty`, `match_status` |
| `rel_matches_receipt.csv`| 60,965 | `[:MATCHES_RECEIPT]`| `:Three_Way_Match_Record`| `:Goods_Receipt_Line`| `ordered_qty`, `match_status` |
| `rel_matches_invoice.csv`| 60,965 | `[:MATCHES_INVOICE]`| `:Three_Way_Match_Record`| `:Supplier_Invoice_Line`| `invoiced_qty`, `match_status` |
| `rel_allocated_to.csv` | 65,000 | `[:ALLOCATED_TO]` | `:Payment` | `:Invoice` | `allocated_amount`, `discount_applied`, `allocation_date` (Binds `:Payment` $\to$ `:Invoice`, specialized by `:Supplier_Payment` $\to$ `:Supplier_Invoice` [15K] and `:Customer_Payment` $\to$ `:Customer_Invoice` [50K]) |
| `rel_salesline_trans.csv`| 200,035 | `[:PART_OF_TRANSACTION]`| `:Sales_Line` | `:Sales_Transaction` | none |
| `rel_salesline_sku.csv` | 200,035 | `[:FOR_SKU_SALES]` | `:Sales_Line` | `:SKU` | none |
| `rel_priced_by.csv` | 200,035 | `[:PRICED_BY]` | `:Sales_Line` | `:Price_Record` | none |
| `rel_jl_je.csv` | 50,000 | `[:LINE_OF_JOURNAL]`| `:Journal_Line` | `:Journal_Entry` | none |
| `rel_jl_gla.csv` | 50,000 | `[:POSTED_TO]` | `:Journal_Line` | `:GL_Account` | none |
| `rel_impacts.csv` | 1,107 | `[:IMPACTS]` | `:Event` | `:Category` | `target_level`, `lift_multiplier`, `elasticity_factor` |
| `rel_interacts_with.csv` | 1,977 | `[:INTERACTS_WITH]`| `:Event` | `:Event` | `interaction_type`, `dampening_factor`, `max_separation_days` |
| `rel_regional_weight.csv`| 174 | `[:REGIONAL_WEIGHT]`| `:Event` | `:Zone_Macro_Region` | `weight_multiplier`, `cultural_significance_tier` (174 distinct event weights localized to active anchor `ZONE_SOUTH`) |
| `rel_sku_product.csv` | 49,616 | `[:PART_OF_PRODUCT]`| `:SKU` | `:Product` | none |

---

## 14. Relational Database & Invariant Validation (`datasets/scof_relational.db`)

The relational database compiles all CSV and Parquet files into a unified, foreign-key enforced relational engine.

### 14.1 Key Relational Database Files
- **`datasets/scof_relational.db`:** SQLite database file (633MB) serving as the local development execution harness.
- **`scripts/schema_ddl.sql`:** Canonical PostgreSQL DDL contract (96 tables, 165 foreign keys).
- **`datasets/relational_ingestion_audit.json`:** Audit report proving 4,358,100 rows loaded across 92 tables in 74.67s with 0 FK errors.
- **`datasets/operational_validation_results.json`:** Comprehensive test report proving 100% pass rate across all six operational gates:
  1. Gate 1: 165/165 physical foreign keys resolved (0 orphans).
  2. Gate 2: 99,232 inventory positions conserved (0 negative QOH).
  3. Gate 3: 25,000 balanced journal entries ($\sum \text{Debits} = \sum \text{Credits}$, diff = 0.0000).
  4. Gate 4: 60,965 three-way match records verified (0 invalid statuses).
  5. Gate 5: 18,004,376 simulation rows + 50,000 twin observations demand balance verified ($\text{Latent} = \text{Observed} + \text{Lost}$).
  6. Gate 6: Relational-to-Graph Parity for Materialized Populations: Verified 1:1 identity parity and constraint satisfaction across the entire materialized graph population (3,728,199 nodes, 2,104,514 edges, 59 constraints satisfied with 0 violations). Active operational subsets are rigorously bounded (e.g., 72,917 goods receipt lines, 66,673 supplier invoice lines, and 60,965 three-way match records representing the fully resolved 1:1:1 transactional subsets rather than unconstrained raw staging rows).

---

## 15. Complete Inter-File Relationship Matrix

The table below summarizes how major files across different folders connect to one another through foreign-key and graph associations:

```text
  Source Dataset File                  Connecting Key           Target Dataset File                  Relationship Semantics
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  datasets/masters/sku_master.csv      PRODUCT_ID          ──>  datasets/masters/product_master.csv  Taxonomic hierarchy (SKU -> Product)
  datasets/masters/sku_master.csv      UNIT_OF_MEASURE     ──>  datasets/foundations/unit_of_measure Physical dimension resolution
  datasets/sourcing/supplier_sku_map   SUPPLIER_ID         ──>  datasets/sourcing/supplier_profiles  Vendor qualification
  datasets/sourcing/supplier_sku_map   SKU_ID              ──>  datasets/masters/sku_master.csv      Sourcing allocation (99,232 edges)
  datasets/masters/store_sku_assortmentSTORE_ID            ──>  datasets/masters/store_master.csv    Store format assortment
  datasets/masters/store_sku_assortmentSKU_ID              ──>  datasets/masters/sku_master.csv      Assortment allocation (346,238 edges)
  datasets/masters/store_warehouse_map STORE_ID            ──>  datasets/masters/store_master.csv    Store replenishment source
  datasets/masters/store_warehouse_map WAREHOUSE_ID        ──>  datasets/masters/warehouse_master.csvServicing DC route (32 conduits)
  datasets/procurement/po_lines        purchase_order_id   ──>  datasets/procurement/purchase_orders Order line grouping
  datasets/procurement/po_lines        sku_id              ──>  datasets/masters/sku_master.csv      Replenishment item
  datasets/inventory/goods_receipt_linepo_line_id          ──>  datasets/procurement/po_lines        Dock receipt fulfillment
  datasets/finance/supplier_invoice_linpo_line_id          ──>  datasets/procurement/po_lines        Invoiced item against PO
  datasets/finance/three_way_match     po_line_id          ──>  datasets/procurement/po_lines        3-Way Match: PO Line
  datasets/finance/three_way_match     goods_receipt_line_id─>  datasets/inventory/goods_receipt_line3-Way Match: Receipt Line
  datasets/finance/three_way_match     invoice_line_id     ──>  datasets/finance/supplier_invoice_lin3-Way Match: Invoice Line
  datasets/finance/payment_allocations payment_id          ──>  datasets/finance/payments.parquet    Payment source (:Payment)
  datasets/finance/payment_allocations invoice_id          ──>  datasets/finance/supplier_invoices & customer_invoices Invoice settlement (:Invoice)
  datasets/finance/journal_lines       journal_entry_id    ──>  datasets/finance/journal_entries     Double-entry voucher line
  datasets/finance/journal_lines       gl_account_id       ──>  datasets/finance/gl_accounts.csv     General Ledger account posting
  datasets/weekly_demand_history_v2    STORE_ID, SKU_ID    ──>  datasets/masters/store_sku_assortmentGround-truth simulation coordinate
```

---

## 16. Architectural Summary & Big-Picture Takeaways

1. **Relationally Bound Ground Truth:** Every observation in the 18,004,376-row simulation universe (`weekly_demand_history_v2.csv`) maps to a physically valid store-SKU pairing, validated against inventory positions, supplier sourcing links, and replenishment policies.
2. **Dual Representation (Relational + Graph):** The dataset exists simultaneously as 96 physical relational tables in PostgreSQL/SQLite and as a 3.73M-node property graph in Neo4j, synchronized with zero identity mismatches.
3. **Audit & Traceability:** All 244 dataset files are indexed in `generation_manifest.json`, validated in `datasets/operational_validation_results.json`, and surfaced through `services/twin_service.py` for operational cognitive-twin capabilities.
