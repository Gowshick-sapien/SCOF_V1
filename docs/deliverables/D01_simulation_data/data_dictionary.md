# Deliverable D1 — Data Dictionary

## 1. Overview
This document provides a field-level description of all database entities generated in Deliverable D1, updated with run-keyed isolation (`run_id`), SHA-256 profile hashing (`profile_hash`), generation statistics, and audit columns.

---

## 2. Table Field Specifications

### 2.1 `simulation_runs`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `run_id` | VARCHAR(50) | Primary Key | Unique execution run ID (e.g. `run-20260728-001`) |
| `random_seed` | INT | NOT NULL | Pseudo-random seed used for generation (e.g. `42`) |
| `profile_name` | VARCHAR(100) | NOT NULL | Active Domain Profile name |
| `profile_version` | VARCHAR(50) | NOT NULL | Profile version string |
| `profile_hash` | VARCHAR(64) | NOT NULL | SHA-256 hash of profile YAML files ensuring exact reproducibility |
| `history_days` | INT | NOT NULL | Number of historical days generated (e.g. `180`) |
| `total_entities_generated` | INT | DEFAULT 0 | Count of master topology entities generated |
| `total_orders_generated` | INT | DEFAULT 0 | Count of purchase orders generated |
| `total_shipments_generated` | INT | DEFAULT 0 | Count of shipments generated |
| `total_inventory_rows` | INT | DEFAULT 0 | Count of daily inventory rows generated |
| `total_disruptions_generated` | INT | DEFAULT 0 | Count of disruption events generated |
| `execution_time_ms` | BIGINT | DEFAULT 0 | Pipeline execution duration in milliseconds |
| `generator_version` | VARCHAR(50) | NOT NULL | Code version of simulation generator |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Timestamp when run was recorded |

### 2.2 `scenarios`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `scenario_id` | VARCHAR(50) | Primary Key | Unique scenario ID (e.g. `scen-01`) |
| `run_id` | VARCHAR(50) | Foreign Key | References `simulation_runs.run_id` |
| `name` | VARCHAR(255) | NOT NULL | Human-readable scenario name |
| `description` | TEXT | Nullable | Scenario context description |
| `random_seed` | INT | NOT NULL | Scenario-specific random seed |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Scenario creation timestamp |

### 2.3 `manufacturers`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical identifier (e.g. `mfg-01`) |
| `name` | VARCHAR(255) | NOT NULL | Display name of manufacturing facility |
| `latitude` | NUMERIC(9,6) | NOT NULL | GPS latitude coordinate |
| `longitude` | NUMERIC(9,6) | NOT NULL | GPS longitude coordinate |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.4 `products`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical product ID (e.g. `prod-101`) |
| `name` | VARCHAR(255) | NOT NULL | Commercial product name |
| `sku` | VARCHAR(100) | UNIQUE, NOT NULL | Stock Keeping Unit code |
| `manufacturer_id` | VARCHAR(50) | Foreign Key | References `manufacturers.id` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.5 `suppliers`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical supplier ID (e.g. `sup-01`) |
| `name` | VARCHAR(255) | NOT NULL | Supplier company name |
| `reliability_profile` | VARCHAR(50) | NOT NULL | Baseline reliability category (`high`, `medium`, `volatile`) |
| `base_lead_time_days` | INT | NOT NULL | Standard procurement lead time in days |
| `latitude` | NUMERIC(9,6) | NOT NULL | GPS latitude |
| `longitude` | NUMERIC(9,6) | NOT NULL | GPS longitude |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.6 `supplier_products`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `supplier_id` | VARCHAR(50) | Foreign Key | References `suppliers.id` (Composite PK) |
| `product_id` | VARCHAR(50) | Foreign Key | References `products.id` (Composite PK) |
| `is_preferred_supplier` | BOOLEAN | DEFAULT FALSE | Primary sourcing supplier flag |
| `unit_cost` | NUMERIC(10,2) | NOT NULL | Unit procurement cost |
| `minimum_order_qty` | INT | DEFAULT 1 | Minimum order quantity |
| `lead_time_override_days` | INT | Nullable | Specific lead time override if different from supplier base |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |

### 2.7 `warehouses`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical warehouse ID (e.g. `wh-01`) |
| `name` | VARCHAR(255) | NOT NULL | Warehouse facility name |
| `capacity_units` | INT | NOT NULL | Maximum unit storage capacity |
| `latitude` | NUMERIC(9,6) | NOT NULL | GPS latitude |
| `longitude` | NUMERIC(9,6) | NOT NULL | GPS longitude |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.8 `routes`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical route ID (e.g. `route-sup01-wh01`) |
| `origin_type` | VARCHAR(50) | NOT NULL | Type of origin entity (`supplier`, `warehouse`, `manufacturer`) |
| `origin_id` | VARCHAR(50) | NOT NULL | ID of origin entity |
| `destination_type` | VARCHAR(50) | NOT NULL | Type of destination entity (`warehouse`, `distribution_center`, `manufacturer`) |
| `destination_id` | VARCHAR(50) | NOT NULL | ID of destination entity |
| `mode` | VARCHAR(50) | NOT NULL | Transport mode (`sea`, `air`, `road`, `rail`) |
| `distance_km` | NUMERIC(10,2) | NOT NULL | Route distance in kilometers |
| `standard_transit_days` | INT | NOT NULL | Expected transit duration in days |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.9 `inventory_levels`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGSERIAL | Primary Key | Auto-incrementing surrogate ID |
| `run_id` | VARCHAR(50) | Foreign Key | References `simulation_runs.run_id` for run isolation |
| `warehouse_id` | VARCHAR(50) | Foreign Key | References `warehouses.id` |
| `product_id` | VARCHAR(50) | Foreign Key | References `products.id` |
| `date` | DATE | NOT NULL | Observation date |
| `stock_on_hand` | INT | NOT NULL | Actual stock level available on date |
| `safety_stock_threshold`| INT | NOT NULL | Minimum required safety stock level |
| `reorder_point` | INT | NOT NULL | Stock level that triggers reorder |
| `units_in_transit` | INT | DEFAULT 0 | Units ordered but not yet received |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |

### 2.10 `purchase_orders`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical order ID (e.g. `po-00001`) |
| `run_id` | VARCHAR(50) | Foreign Key | References `simulation_runs.run_id` |
| `supplier_id` | VARCHAR(50) | Foreign Key | References `suppliers.id` |
| `destination_warehouse_id` | VARCHAR(50) | Foreign Key | References `warehouses.id` |
| `order_date` | DATE | NOT NULL | Date purchase order was placed |
| `expected_delivery_date` | DATE | NOT NULL | Expected arrival date |
| `actual_delivery_date` | DATE | Nullable | Actual arrival date |
| `status` | VARCHAR(50) | NOT NULL | Order status (`PLACED`, `IN_TRANSIT`, `DELIVERED`, `DELAYED`, `CANCELLED`) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.11 `shipments`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Canonical shipment ID (e.g. `ship-00001`) |
| `run_id` | VARCHAR(50) | Foreign Key | References `simulation_runs.run_id` |
| `order_id` | VARCHAR(50) | Foreign Key | References `purchase_orders.id` |
| `route_id` | VARCHAR(50) | Foreign Key | References `routes.id` |
| `departure_date` | TIMESTAMPTZ | NOT NULL | Transit departure timestamp |
| `estimated_arrival` | TIMESTAMPTZ | NOT NULL | Expected arrival timestamp |
| `actual_arrival` | TIMESTAMPTZ | Nullable | Actual arrival timestamp |
| `status` | VARCHAR(50) | NOT NULL | Shipment status (`DISPATCHED`, `IN_TRANSIT`, `ARRIVED`, `DELAYED`) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### 2.12 `disruption_events`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(50) | Primary Key | Disruption event ID (e.g. `disrupt-00001`) |
| `run_id` | VARCHAR(50) | Foreign Key | References `simulation_runs.run_id` |
| `scenario_id` | VARCHAR(50) | Foreign Key | References `scenarios.scenario_id` |
| `disruption_type` | VARCHAR(50) | NOT NULL | Event type (`supplier_delay`, `transport_failure`, `demand_spike`, `adverse_weather`) |
| `target_entity_type` | VARCHAR(50) | NOT NULL | Affected entity class (`supplier`, `route`, `product`) |
| `target_entity_id` | VARCHAR(50) | NOT NULL | Target entity ID (e.g. `sup-04`) |
| `severity` | INT | 1–5 | Impact scale (1 = minor, 5 = severe) |
| `start_date` | DATE | NOT NULL | Event start date |
| `end_date` | DATE | NOT NULL | Event end date |
| `status` | VARCHAR(50) | NOT NULL | Disruption status (`SCHEDULED`, `ACTIVE`, `RESOLVED`) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |
