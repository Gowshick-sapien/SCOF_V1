-- Deliverable D1 PostgreSQL DDL Schema Initialization Script
-- Creates scof schema, vector extension, master tables, operational log tables, and indexes.

CREATE SCHEMA IF NOT EXISTS scof;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Simulation Runs Metadata
CREATE TABLE IF NOT EXISTS scof.simulation_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    random_seed INT NOT NULL,
    profile_name VARCHAR(100) NOT NULL,
    profile_version VARCHAR(50) NOT NULL,
    profile_hash VARCHAR(64) NOT NULL,
    history_days INT NOT NULL,
    total_entities_generated INT DEFAULT 0,
    total_orders_generated INT DEFAULT 0,
    total_shipments_generated INT DEFAULT 0,
    total_inventory_rows INT DEFAULT 0,
    total_disruptions_generated INT DEFAULT 0,
    execution_time_ms BIGINT DEFAULT 0,
    generator_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Scenarios Metadata
CREATE TABLE IF NOT EXISTS scof.scenarios (
    scenario_id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES scof.simulation_runs(run_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    random_seed INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Manufacturers
CREATE TABLE IF NOT EXISTS scof.manufacturers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Products
CREATE TABLE IF NOT EXISTS scof.products (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    manufacturer_id VARCHAR(50) REFERENCES scof.manufacturers(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Suppliers
CREATE TABLE IF NOT EXISTS scof.suppliers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    reliability_profile VARCHAR(50) NOT NULL,
    base_lead_time_days INT NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Supplier Products Junction
CREATE TABLE IF NOT EXISTS scof.supplier_products (
    supplier_id VARCHAR(50) REFERENCES scof.suppliers(id),
    product_id VARCHAR(50) REFERENCES scof.products(id),
    is_preferred_supplier BOOLEAN DEFAULT FALSE,
    unit_cost NUMERIC(10,2) NOT NULL,
    minimum_order_qty INT DEFAULT 1,
    lead_time_override_days INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (supplier_id, product_id)
);

-- 7. Warehouses
CREATE TABLE IF NOT EXISTS scof.warehouses (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    capacity_units INT NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Distribution Centers
CREATE TABLE IF NOT EXISTS scof.distribution_centers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Routes (Polymorphic Origin & Destination)
CREATE TABLE IF NOT EXISTS scof.routes (
    id VARCHAR(50) PRIMARY KEY,
    origin_type VARCHAR(50) NOT NULL,
    origin_id VARCHAR(50) NOT NULL,
    destination_type VARCHAR(50) NOT NULL,
    destination_id VARCHAR(50) NOT NULL,
    mode VARCHAR(50) NOT NULL,
    distance_km NUMERIC(10,2) NOT NULL,
    standard_transit_days INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Daily Inventory Levels (Run-Keyed)
CREATE TABLE IF NOT EXISTS scof.inventory_levels (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES scof.simulation_runs(run_id) ON DELETE CASCADE,
    warehouse_id VARCHAR(50) REFERENCES scof.warehouses(id),
    product_id VARCHAR(50) REFERENCES scof.products(id),
    date DATE NOT NULL,
    stock_on_hand INT NOT NULL,
    safety_stock_threshold INT NOT NULL,
    reorder_point INT NOT NULL,
    units_in_transit INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_run_wh_product_date UNIQUE (run_id, warehouse_id, product_id, date)
);

-- 11. Purchase Orders (Run-Keyed)
CREATE TABLE IF NOT EXISTS scof.purchase_orders (
    id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES scof.simulation_runs(run_id) ON DELETE CASCADE,
    supplier_id VARCHAR(50) REFERENCES scof.suppliers(id),
    destination_warehouse_id VARCHAR(50) REFERENCES scof.warehouses(id),
    order_date DATE NOT NULL,
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. Order Items
CREATE TABLE IF NOT EXISTS scof.order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES scof.purchase_orders(id) ON DELETE CASCADE,
    product_id VARCHAR(50) REFERENCES scof.products(id),
    quantity INT NOT NULL,
    unit_cost NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. Shipments (Run-Keyed)
CREATE TABLE IF NOT EXISTS scof.shipments (
    id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES scof.simulation_runs(run_id) ON DELETE CASCADE,
    order_id VARCHAR(50) REFERENCES scof.purchase_orders(id) ON DELETE CASCADE,
    route_id VARCHAR(50) REFERENCES scof.routes(id),
    departure_date TIMESTAMP WITH TIME ZONE NOT NULL,
    estimated_arrival TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_arrival TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. Disruption Events (Run-Keyed & Scenario-Keyed)
CREATE TABLE IF NOT EXISTS scof.disruption_events (
    id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES scof.simulation_runs(run_id) ON DELETE CASCADE,
    scenario_id VARCHAR(50) REFERENCES scof.scenarios(scenario_id) ON DELETE CASCADE,
    disruption_type VARCHAR(50) NOT NULL,
    target_entity_type VARCHAR(50) NOT NULL,
    target_entity_id VARCHAR(50) NOT NULL,
    severity INT CHECK (severity BETWEEN 1 AND 5),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_inventory_run_date ON scof.inventory_levels(run_id, date, warehouse_id);
CREATE INDEX IF NOT EXISTS idx_po_run_supplier ON scof.purchase_orders(run_id, supplier_id, order_date);
CREATE INDEX IF NOT EXISTS idx_shipments_run ON scof.shipments(run_id, route_id, status);
CREATE INDEX IF NOT EXISTS idx_routes_polymorphic ON scof.routes(origin_type, origin_id, destination_type, destination_id);
CREATE INDEX IF NOT EXISTS idx_disruption_scenario ON scof.disruption_events(run_id, scenario_id, target_entity_id);
