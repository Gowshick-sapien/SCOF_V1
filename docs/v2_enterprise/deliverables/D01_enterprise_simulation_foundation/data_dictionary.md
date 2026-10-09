# Deliverable D01 -- Enterprise Data Dictionary

## 1. Overview

This document provides a field-level data dictionary for the core relational tables in Deliverable D01 (Enterprise World & Simulation Foundation). The schema comprises 96 tables modeling 30 unified business domains with 165 physical foreign keys.

All tables include standard audit attributes (`created_at`, `updated_at`, and boolean active flags where applicable) to maintain strict data lifecycle tracking.

---

## 2. Field Specifications by Domain

### 2.1 Corporate Structure & Facilities

#### `legal_entity`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `legal_entity_id` | VARCHAR(50) | PRIMARY KEY | Canonical entity ID (e.g. `LE-CORP-01`) |
| `enterprise_group_id`| VARCHAR(50) | FOREIGN KEY | References `enterprise_group.enterprise_group_id` |
| `entity_name` | VARCHAR(255) | NOT NULL | Registered commercial corporate name |
| `registration_number`| VARCHAR(100) | UNIQUE, NOT NULL | Commercial registry / tax registration number |
| `country_id` | VARCHAR(10) | FOREIGN KEY | References `country.country_id` |
| `functional_currency`| VARCHAR(10) | FOREIGN KEY | References `currency.currency_id` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Operating status indicator |

#### `facility`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `facility_id` | VARCHAR(50) | PRIMARY KEY | Canonical facility identifier (e.g. `FAC-DC-01`) |
| `operating_unit_id` | VARCHAR(50) | FOREIGN KEY | References `operating_unit.operating_unit_id` |
| `facility_name` | VARCHAR(255) | NOT NULL | Facility display name |
| `facility_type` | VARCHAR(50) | NOT NULL, CHECK | Facility node type (`DISTRIBUTION_CENTER`, `REGIONAL_DC`, `STORE`, `CROSS_DOCK`, `CARRIER_HUB`) |
| `postal_code` | VARCHAR(20) | NOT NULL | Postal code string |
| `city_id` | VARCHAR(50) | FOREIGN KEY | References `city.city_id` |
| `latitude` | NUMERIC(9,6) | NOT NULL | Geodetic latitude coordinate |
| `longitude` | NUMERIC(9,6) | NOT NULL | Geodetic longitude coordinate |
| `total_area_sqm` | NUMERIC(10,2) | NOT NULL | Gross facility floor space in square meters |
| `usable_storage_volume_cbm` | NUMERIC(12,2) | NOT NULL | Effective storage volume in cubic meters |
| `is_active` | BOOLEAN | DEFAULT TRUE | Physical operational status |

---

### 2.2 Merchandise Hierarchy & Product Catalog

#### `product`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `product_id` | VARCHAR(50) | PRIMARY KEY | Canonical master product ID (e.g. `PRD-10023`) |
| `product_name` | VARCHAR(255) | NOT NULL | Commercial product name |
| `product_family_id`| VARCHAR(50) | FOREIGN KEY | References `product_family.product_family_id` |
| `brand_id` | VARCHAR(50) | FOREIGN KEY | References `brand.brand_id` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active commercial flag |

#### `sku` (49,616 Master Records)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `sku_id` | VARCHAR(50) | PRIMARY KEY | Canonical SKU ID (e.g. `SKU-000492`) |
| `product_id` | VARCHAR(50) | FOREIGN KEY | References `product.product_id` |
| `sku_code` | VARCHAR(100) | UNIQUE, NOT NULL | Unique commercial Barcode / GTIN code |
| `sku_name` | VARCHAR(255) | NOT NULL | Full descriptive item name |
| `subcategory_id` | VARCHAR(50) | FOREIGN KEY | References `subcategory.subcategory_id` |
| `brand_id` | VARCHAR(50) | FOREIGN KEY | References `brand.brand_id` |
| `unit_of_measure_id`| VARCHAR(50) | FOREIGN KEY | References `unit_of_measure.uom_id` |
| `storage_type` | VARCHAR(50) | NOT NULL, CHECK | Storage classification (`AMBIENT`, `CHILLED`, `FROZEN`, `HAZARDOUS`) |
| `unit_weight_kg` | NUMERIC(10,4) | NOT NULL | Net weight per individual unit in kilograms |
| `unit_volume_cbm` | NUMERIC(10,6) | NOT NULL | Net physical volume per unit in cubic meters |
| `shelf_life_days` | INT | NULLABLE | Maximum shelf-life before expiration |
| `unit_cost` | NUMERIC(12,4) | NOT NULL | Standard unit inventory valuation cost |
| `unit_retail_price`| NUMERIC(12,4) | NOT NULL | Standard MSRP customer retail price |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active inventory catalog flag |

---

### 2.3 Sourcing & Multi-Vendor Network

#### `supplier`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `supplier_id` | VARCHAR(50) | PRIMARY KEY | Canonical supplier identifier (e.g. `SUP-0012`) |
| `legal_name` | VARCHAR(255) | NOT NULL | Legal corporate supplier name |
| `supplier_tier` | VARCHAR(20) | NOT NULL, CHECK | Tier classification (`TIER_1`, `TIER_2`, `STRATEGIC`, `COMMODITY`) |
| `country_id` | VARCHAR(10) | FOREIGN KEY | References `country.country_id` |
| `reliability_rating`| NUMERIC(3,2) | NOT NULL | Historical on-time delivery score (0.00 to 1.00) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Vendor active onboarding flag |

#### `supplier_product` (Multi-Sourcing Junction)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `supplier_product_id` | VARCHAR(50) | PRIMARY KEY | Unique junction record ID |
| `supplier_id` | VARCHAR(50) | FOREIGN KEY | References `supplier.supplier_id` |
| `sku_id` | VARCHAR(50) | FOREIGN KEY | References `sku.sku_id` |
| `is_primary_supplier` | BOOLEAN | DEFAULT FALSE | Flag indicating default primary sourcing vendor |
| `contract_unit_cost` | NUMERIC(12,4) | NOT NULL | Negotiated contractual unit procurement price |
| `moq_units` | INT | DEFAULT 1 | Minimum order quantity in base units |
| `lead_time_days` | INT | NOT NULL | Contractual replenishment lead time in days |
| `quality_rating` | NUMERIC(3,2) | DEFAULT 1.00 | Historical quality acceptance rate |

---

### 2.4 Multi-Modal Logistics Network

#### `transport_lane`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `lane_id` | VARCHAR(50) | PRIMARY KEY | Canonical lane ID (e.g. `LANE-DC01-ST04`) |
| `origin_facility_id` | VARCHAR(50) | FOREIGN KEY | References `facility.facility_id` |
| `destination_facility_id`| VARCHAR(50)| FOREIGN KEY | References `facility.facility_id` |
| `primary_carrier_id` | VARCHAR(50) | FOREIGN KEY | References `carrier.carrier_id` |
| `transport_mode_id` | VARCHAR(20) | FOREIGN KEY | References `transport_mode.mode_id` |
| `distance_km` | NUMERIC(10,2) | NOT NULL | Physical transit distance in kilometers |
| `nominal_transit_hours` | NUMERIC(8,2) | NOT NULL | Planned scheduled transit time in hours |
| `is_active` | BOOLEAN | DEFAULT TRUE | Transport corridor availability flag |

---

### 2.5 Multi-Echelon Inventory Substrate

#### `inventory_position`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `position_id` | VARCHAR(50) | PRIMARY KEY | Unique inventory position identifier |
| `facility_id` | VARCHAR(50) | FOREIGN KEY | References `facility.facility_id` |
| `sku_id` | VARCHAR(50) | FOREIGN KEY | References `sku.sku_id` |
| `location_id` | VARCHAR(50) | FOREIGN KEY | References `facility_storage_location.location_id` |
| `on_hand_qty` | INT | NOT NULL, CHECK (>= 0) | Physical inventory present in bin |
| `reserved_qty` | INT | DEFAULT 0, CHECK (>= 0) | Stock committed to open orders |
| `in_transit_qty` | INT | DEFAULT 0, CHECK (>= 0) | Goods dispatched but not yet received |
| `safety_stock_qty` | INT | DEFAULT 0 | Target buffer stock level |
| `reorder_point_qty` | INT | DEFAULT 0 | Replenishment trigger threshold |
| `last_cycle_count_date`| DATE | NULLABLE | Date of last physical inventory audit |

---

### 2.6 Procurement & Three-Way Matching

#### `purchase_order`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `po_id` | VARCHAR(50) | PRIMARY KEY | Canonical purchase order ID (e.g. `PO-2026-004921`) |
| `supplier_id` | VARCHAR(50) | FOREIGN KEY | References `supplier.supplier_id` |
| `destination_facility_id`| VARCHAR(50)| FOREIGN KEY | References `facility.facility_id` |
| `order_date` | DATE | NOT NULL | Commercial PO placement date |
| `expected_delivery_date`| DATE | NOT NULL | Agreed contractual delivery date |
| `status` | VARCHAR(30) | NOT NULL | PO lifecycle state (`DRAFT`, `ISSUED`, `CONFIRMED`, `PARTIALLY_RECEIVED`, `CLOSED`) |
| `total_order_amount` | NUMERIC(14,2) | NOT NULL | Net financial obligation value |

#### `three_way_match_log`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `match_id` | VARCHAR(50) | PRIMARY KEY | Unique match verification record |
| `po_line_id` | VARCHAR(50) | FOREIGN KEY | References `purchase_order_line.po_line_id` |
| `receipt_line_id` | VARCHAR(50) | FOREIGN KEY | References `goods_receipt_line.receipt_line_id` |
| `invoice_line_id` | VARCHAR(50) | FOREIGN KEY | References `vendor_invoice_line.invoice_line_id` |
| `matched_quantity` | INT | NOT NULL | Quantity reconciled across all 3 documents |
| `unit_price_variance`| NUMERIC(10,4) | DEFAULT 0.00 | Variance between PO price and Invoice price |
| `match_status` | VARCHAR(30) | NOT NULL | Reconciliation state (`MATCHED`, `QTY_VARIANCE`, `PRICE_VARIANCE`) |

---

### 2.7 Financial Accounting & General Ledger

#### `journal_entry_header`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `header_id` | VARCHAR(50) | PRIMARY KEY | Unique general ledger entry ID |
| `legal_entity_id` | VARCHAR(50) | FOREIGN KEY | References `legal_entity.legal_entity_id` |
| `posting_date` | DATE | NOT NULL | Effective financial accounting date |
| `accounting_period_id`| VARCHAR(50) | FOREIGN KEY | References `accounting_period.period_id` |
| `source_module` | VARCHAR(50) | NOT NULL | Source business domain (`PROCUREMENT`, `INVENTORY`, `SALES`) |
| `is_posted` | BOOLEAN | DEFAULT TRUE | Ledger post status flag |

#### `journal_entry_line`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `line_id` | VARCHAR(50) | PRIMARY KEY | Individual debit or credit line ID |
| `header_id` | VARCHAR(50) | FOREIGN KEY | References `journal_entry_header.header_id` |
| `account_id` | VARCHAR(50) | FOREIGN KEY | References `general_ledger_account.account_id` |
| `entry_side` | VARCHAR(10) | NOT NULL, CHECK | Entry type (`DEBIT` or `CREDIT`) |
| `amount` | NUMERIC(14,2) | NOT NULL, CHECK (> 0) | Monetary transaction magnitude |
| `currency_id` | VARCHAR(10) | FOREIGN KEY | References `currency.currency_id` |
| `reference_entity_type`| VARCHAR(50) | NULLABLE | Originating entity name (e.g. `GOODS_RECEIPT`) |
| `reference_entity_id` | VARCHAR(50) | NULLABLE | Originating record ID |

---

### 2.8 Digital Twin & Simulation Runtime

#### `sim_run`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `sim_run_id` | VARCHAR(50) | PRIMARY KEY | Unique simulation execution ID |
| `scenario_id` | VARCHAR(50) | FOREIGN KEY | References `scenario.scenario_id` |
| `random_seed` | INT | NOT NULL | Deterministic pseudo-random generator seed |
| `start_sim_time` | TIMESTAMP | NOT NULL | Simulated epoch start timestamp |
| `end_sim_time` | TIMESTAMP | NOT NULL | Simulated epoch termination timestamp |
| `wall_clock_duration_s`| NUMERIC(10,2)| DEFAULT 0.00 | Wall-clock execution duration in seconds |
| `profile_hash` | VARCHAR(64) | NOT NULL | Cryptographic SHA-256 hash of configuration |
| `status` | VARCHAR(30) | NOT NULL | Run state (`INITIALIZING`, `RUNNING`, `COMPLETED`, `FAILED`) |
