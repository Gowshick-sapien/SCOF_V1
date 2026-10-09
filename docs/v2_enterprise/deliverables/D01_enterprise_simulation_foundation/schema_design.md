# Deliverable D01 -- Relational Database Schema Design

## 1. Architectural Overview

The relational database schema serves as the authoritative System of Record (SoR) for Deliverable D01 and the wider SCOF platform ([ADR 001](file:///d:/projects/SCOF_V1/SCOF/docs/adr/001_enterprise_knowledge_fabric_over_monolithic_generator.md)). The schema models an end-to-end retail supply chain enterprise spanning:
- **30 Unified Business Domains**
- **96 Relational Tables**
- **165 Physical Foreign Key Constraints**
- **49,616 Product SKUs**
- **4,358,100 Ingested Operational Records**

The schema is maintained with strict cross-dialect compatibility between the SQLite development harness ([`datasets/scof_relational.db`](file:///d:/projects/SCOF_V1/SCOF/datasets/scof_relational.db)) and PostgreSQL 16 ([`scripts/schema_ddl.sql`](file:///d:/projects/SCOF_V1/SCOF/scripts/schema_ddl.sql)).

---

## 2. Business Domain Architecture & Table Directory

The 96 tables are organized into 10 cohesive operational macro-groups covering 30 unified business domains:

### Group 1: Foundations, Temporal & Measurement (Domains 1-3)
Models calendar timelines, 4-4-5 retail fiscal calendars, ISO currency codes, and physical unit conversions.
- `unit_of_measure`, `currency`, `currency_exchange_rate`
- `calendar`, `calendar_year`, `month`, `week`, `calendar_date`
- `fiscal_calendar`, `fiscal_year`, `fiscal_quarter`, `fiscal_period`

### Group 2: Geographic Hierarchy & Spatial Topology (Domain 4)
Models jurisdictional and spatial relationships from global macro-regions down to postal centroids.
- `country`, `zone_macro_region`, `state_province`, `district`, `city`, `postal_code_area`, `transport_zone`

### Group 3: Corporate Structure & Enterprise Facilities (Domains 5-7)
Models legal entity hierarchies, divisions, operating units, facility groups, physical facilities, and dock loading infrastructure.
- `enterprise_group`, `legal_entity`, `operating_unit`, `division`
- `facility_group`, `facility`, `facility_dock_door`, `facility_operating_hours`
- `party`, `party_role`, `party_contact`

### Group 4: Merchandise Hierarchy & Product Catalog (Domains 8-11)
Models the 4-tier retail merchandise taxonomy, brand registries, physical SKUs, packaging conversions, storage temperature specifications, and bills of materials.
- `department`, `category`, `subcategory`, `product_family`, `brand`
- `product`, `sku`, `sku_packaging`, `sku_storage_spec`
- `bill_of_materials`, `bom_component`

### Group 5: Sourcing, Suppliers & Vendor Contracting (Domains 12-14)
Models supplier corporate profiles, physical supplier sites, tiered capabilities, multi-sourcing catalog junction, and performance scorecards.
- `supplier`, `supplier_site`, `supplier_capability`, `supplier_product`
- `supplier_contract`, `vendor_scorecard`, `vendor_compliance_audit`

### Group 6: Logistics Network & Multi-Modal Transport (Domains 15-18)
Models freight carriers, transport modes, origin-destination transport lanes, tariff schedules, logistics fleets, routes, and waypoints.
- `transport_mode`, `carrier`, `transport_lane`, `lane_rate_schedule`
- `transport_vehicle`, `logistics_route`, `route_stop`, `corridor_restriction`

### Group 7: Storage Architecture, Inventory & Tracking (Domains 19-21)
Models warehouse bin topologies, inventory positions across echelons, daily snapshots, lot batches, serial registries, and physical movement logs.
- `inventory_storage_type`, `facility_storage_location`, `inventory_position`
- `inventory_snapshot`, `lot_master`, `serial_registry`, `inventory_transaction_log`

### Group 8: Procurement, Invoicing & Three-Way Matching (Domains 22-24)
Models purchase orders, order lines, physical goods receipts, vendor invoices, invoice line items, and automated accounts payable reconciliations.
- `purchase_order`, `purchase_order_line`
- `goods_receipt`, `goods_receipt_line`
- `vendor_invoice`, `vendor_invoice_line`, `three_way_match_log`

### Group 9: Fulfillment, POS Commerce & Demand (Domains 25-27)
Models customer orders, shipment dispatch lines, point-of-sale store transactions, weekly demand history, latent lost sales observations, and promotional lifts.
- `customer_order`, `customer_order_line`
- `shipment`, `shipment_line`
- `pos_sales_transaction`, `demand_observation`, `promotion_event`

### Group 10: Financial General Ledger & Exogenous Disruptions (Domains 28-30)
Models the enterprise chart of accounts, double-entry journal entries, trial balance snapshots, simulation runs, scenarios, disruption events, and telemetry.
- `chart_of_accounts`, `general_ledger_account`, `accounting_period`
- `journal_entry_header`, `journal_entry_line`, `trial_balance_snapshot`
- `sim_run`, `scenario`, `disruption_event`, `disruption_impact_log`, `asset_telemetry_event`

---

## 3. Core Relational Schema DDL Highlights

Below are representative DDL definitions extracted from [`scripts/schema_ddl.sql`](file:///d:/projects/SCOF_V1/SCOF/scripts/schema_ddl.sql) demonstrating table structures, primary keys, and foreign key cascades:

```sql
-- 1. Physical Facility Definition
CREATE TABLE IF NOT EXISTS facility (
    facility_id VARCHAR(50) PRIMARY KEY,
    operating_unit_id VARCHAR(50) NOT NULL,
    facility_name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(50) NOT NULL CHECK (facility_type IN ('DISTRIBUTION_CENTER', 'REGIONAL_DC', 'STORE', 'CROSS_DOCK', 'CARRIER_HUB')),
    postal_code VARCHAR(20) NOT NULL,
    city_id VARCHAR(50) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    total_area_sqm NUMERIC(10,2) NOT NULL,
    usable_storage_volume_cbm NUMERIC(12,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operating_unit_id) REFERENCES operating_unit(operating_unit_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

-- 2. Master SKU Definition (49,616 Records)
CREATE TABLE IF NOT EXISTS sku (
    sku_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    sku_name VARCHAR(255) NOT NULL,
    subcategory_id VARCHAR(50) NOT NULL,
    brand_id VARCHAR(50) NOT NULL,
    unit_of_measure_id VARCHAR(50) NOT NULL,
    storage_type VARCHAR(50) NOT NULL CHECK (storage_type IN ('AMBIENT', 'CHILLED', 'FROZEN', 'HAZARDOUS')),
    unit_weight_kg NUMERIC(10,4) NOT NULL,
    unit_volume_cbm NUMERIC(10,6) NOT NULL,
    shelf_life_days INT,
    unit_cost NUMERIC(12,4) NOT NULL,
    unit_retail_price NUMERIC(12,4) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (subcategory_id) REFERENCES subcategory(subcategory_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id),
    FOREIGN KEY (unit_of_measure_id) REFERENCES unit_of_measure(uom_id)
);

-- 3. Supplier Multi-Sourcing Junction
CREATE TABLE IF NOT EXISTS supplier_product (
    supplier_product_id VARCHAR(50) PRIMARY KEY,
    supplier_id VARCHAR(50) NOT NULL,
    sku_id VARCHAR(50) NOT NULL,
    is_primary_supplier BOOLEAN DEFAULT FALSE,
    contract_unit_cost NUMERIC(12,4) NOT NULL,
    moq_units INT DEFAULT 1,
    lead_time_days INT NOT NULL,
    quality_rating NUMERIC(3,2) DEFAULT 1.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id),
    FOREIGN KEY (sku_id) REFERENCES sku(sku_id),
    UNIQUE (supplier_id, sku_id)
);

-- 4. Multi-Echelon Inventory Position
CREATE TABLE IF NOT EXISTS inventory_position (
    position_id VARCHAR(50) PRIMARY KEY,
    facility_id VARCHAR(50) NOT NULL,
    sku_id VARCHAR(50) NOT NULL,
    location_id VARCHAR(50) NOT NULL,
    on_hand_qty INT NOT NULL CHECK (on_hand_qty >= 0),
    reserved_qty INT NOT NULL DEFAULT 0 CHECK (reserved_qty >= 0),
    in_transit_qty INT NOT NULL DEFAULT 0 CHECK (in_transit_qty >= 0),
    safety_stock_qty INT NOT NULL DEFAULT 0,
    reorder_point_qty INT NOT NULL DEFAULT 0,
    last_cycle_count_date DATE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facility_id) REFERENCES facility(facility_id),
    FOREIGN KEY (sku_id) REFERENCES sku(sku_id),
    FOREIGN KEY (location_id) REFERENCES facility_storage_location(location_id),
    UNIQUE (facility_id, sku_id, location_id)
);

-- 5. Double-Entry General Ledger Line Item
CREATE TABLE IF NOT EXISTS journal_entry_line (
    line_id VARCHAR(50) PRIMARY KEY,
    header_id VARCHAR(50) NOT NULL,
    account_id VARCHAR(50) NOT NULL,
    entry_side VARCHAR(10) NOT NULL CHECK (entry_side IN ('DEBIT', 'CREDIT')),
    amount NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    currency_id VARCHAR(10) NOT NULL,
    reference_entity_type VARCHAR(50),
    reference_entity_id VARCHAR(50),
    line_memo TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (header_id) REFERENCES journal_entry_header(header_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES general_ledger_account(account_id),
    FOREIGN KEY (currency_id) REFERENCES currency(currency_id)
);
```

---

## 4. Indexing & Query Optimization Strategy

To support high-throughput agent retrieval ($< 50\text{ ms}$) and complex analytical joins, specific indexing tiers are applied:

1. **Foreign Key Coverage**: Every single foreign key column across all 96 tables is covered by a dedicated B-Tree index to eliminate full-table scans during cascading joins.
2. **Operational Join Indexes**:
   - `inventory_position(facility_id, sku_id)`: Composite index optimizing real-time stock availability queries.
   - `purchase_order_line(po_id, sku_id)`: Composite index for PO line item lookups and three-way matching.
   - `goods_receipt_line(receipt_id, po_line_id)`: Composite index for receipt verification against purchase orders.
   - `journal_entry_line(header_id, account_id)`: Optimizes trial balance aggregation and balance validation.
3. **Temporal Range Indexes**:
   - `inventory_snapshot(snapshot_date, facility_id)`: Range scan index for multi-echelon inventory history.
   - `pos_sales_transaction(transaction_date, store_id)`: Partitioned/composite index for demand extraction.
   - `demand_observation(observation_date, sku_id)`: Composite index for time-series forecasting benchmarks.
