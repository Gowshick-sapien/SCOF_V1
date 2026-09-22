-- =============================================================================
-- SCOF Enterprise Ecosystem: Complete Relational Schema DDL
-- Stage 6 Architecture Freeze - Production PostgreSQL DDL Script
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TIER 0: PLATFORM FOUNDATIONS
-- =============================================================================

-- Foundation D: Reference Dimensions
CREATE TABLE currency (
    currency_id CHAR(3) PRIMARY KEY,
    currency_name VARCHAR(50) NOT NULL,
    symbol VARCHAR(8) NOT NULL,
    decimal_places INTEGER NOT NULL DEFAULT 2,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE unit_of_measure (
    uom_id VARCHAR(16) PRIMARY KEY,
    uom_name VARCHAR(50) NOT NULL,
    uom_category VARCHAR(32) NOT NULL,
    base_unit_id VARCHAR(16) REFERENCES unit_of_measure(uom_id),
    conversion_factor_to_base DECIMAL(18,6) DEFAULT 1.0
);

CREATE TABLE payment_terms (
    payment_term_id VARCHAR(32) PRIMARY KEY,
    term_name VARCHAR(100) NOT NULL,
    net_days INTEGER NOT NULL,
    discount_days INTEGER DEFAULT 0,
    discount_percentage DECIMAL(5,2) DEFAULT 0.0,
    description VARCHAR(255)
);

CREATE TABLE incoterm (
    incoterm_id CHAR(3) PRIMARY KEY,
    incoterm_name VARCHAR(100) NOT NULL,
    risk_transfer_point VARCHAR(255) NOT NULL,
    freight_payer VARCHAR(16) NOT NULL,
    insurance_payer VARCHAR(16) NOT NULL,
    customs_clearance_responsible VARCHAR(16) NOT NULL
);

-- Foundation C: Time & Dual Calendar
CREATE TABLE calendar (
    calendar_id VARCHAR(32) PRIMARY KEY,
    calendar_name VARCHAR(100) NOT NULL,
    week_start_day VARCHAR(16) NOT NULL DEFAULT 'MONDAY',
    is_leap_year_aware BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE calendar_year (
    year_id INTEGER PRIMARY KEY,
    calendar_id VARCHAR(32) NOT NULL REFERENCES calendar(calendar_id),
    is_leap_year BOOLEAN NOT NULL,
    total_weeks INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE month (
    month_id INTEGER PRIMARY KEY,
    year_id INTEGER NOT NULL REFERENCES calendar_year(year_id),
    month_number INTEGER NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    total_days INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE week (
    week_id INTEGER PRIMARY KEY,
    year_id INTEGER NOT NULL REFERENCES calendar_year(year_id),
    week_number INTEGER NOT NULL CHECK (week_number BETWEEN 1 AND 53),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    retail_quarter INTEGER NOT NULL CHECK (retail_quarter BETWEEN 1 AND 4)
);

CREATE TABLE calendar_date (
    date_id DATE PRIMARY KEY,
    date_key INTEGER NOT NULL UNIQUE,
    year_id INTEGER NOT NULL REFERENCES calendar_year(year_id),
    month_id INTEGER NOT NULL REFERENCES month(month_id),
    week_id INTEGER NOT NULL REFERENCES week(week_id),
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    day_name VARCHAR(10) NOT NULL,
    day_of_month INTEGER NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_of_year INTEGER NOT NULL CHECK (day_of_year BETWEEN 1 AND 366),
    is_weekend BOOLEAN NOT NULL,
    is_business_day BOOLEAN NOT NULL
);

CREATE TABLE fiscal_calendar (
    fiscal_calendar_id VARCHAR(32) PRIMARY KEY,
    fiscal_calendar_name VARCHAR(100) NOT NULL,
    start_month INTEGER NOT NULL CHECK (start_month BETWEEN 1 AND 12),
    periods_per_year INTEGER NOT NULL DEFAULT 12
);

CREATE TABLE fiscal_year (
    fiscal_year_id VARCHAR(16) PRIMARY KEY,
    fiscal_calendar_id VARCHAR(32) NOT NULL REFERENCES fiscal_calendar(fiscal_calendar_id),
    fiscal_year_name VARCHAR(32) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE fiscal_quarter (
    fiscal_quarter_id VARCHAR(16) PRIMARY KEY,
    fiscal_year_id VARCHAR(16) NOT NULL REFERENCES fiscal_year(fiscal_year_id),
    quarter_number INTEGER NOT NULL CHECK (quarter_number BETWEEN 1 AND 4),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE fiscal_period (
    fiscal_period_id VARCHAR(16) PRIMARY KEY,
    fiscal_year_id VARCHAR(16) NOT NULL REFERENCES fiscal_year(fiscal_year_id),
    fiscal_quarter_id VARCHAR(16) NOT NULL REFERENCES fiscal_quarter(fiscal_quarter_id),
    period_number INTEGER NOT NULL CHECK (period_number BETWEEN 1 AND 12),
    period_name VARCHAR(32) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    period_status VARCHAR(16) NOT NULL DEFAULT 'OPEN'
);

-- Foundation B: Geography & Location
CREATE TABLE country (
    country_id CHAR(3) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    iso_2_code CHAR(2) NOT NULL UNIQUE,
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id),
    phone_country_code VARCHAR(8)
);

CREATE TABLE zone_macro_region (
    zone_id VARCHAR(32) PRIMARY KEY,
    country_id CHAR(3) NOT NULL REFERENCES country(country_id),
    zone_name VARCHAR(100) NOT NULL,
    climate_zone VARCHAR(32) NOT NULL
);

CREATE TABLE state_province (
    state_id VARCHAR(16) PRIMARY KEY,
    country_id CHAR(3) NOT NULL REFERENCES country(country_id),
    zone_id VARCHAR(32) NOT NULL REFERENCES zone_macro_region(zone_id),
    state_name VARCHAR(100) NOT NULL,
    gst_state_code CHAR(2)
);

CREATE TABLE district (
    district_id VARCHAR(32) PRIMARY KEY,
    state_id VARCHAR(16) NOT NULL REFERENCES state_province(state_id),
    district_name VARCHAR(100) NOT NULL
);

CREATE TABLE city (
    city_id VARCHAR(32) PRIMARY KEY,
    district_id VARCHAR(32) NOT NULL REFERENCES district(district_id),
    city_name VARCHAR(100) NOT NULL,
    tier VARCHAR(16) NOT NULL,
    population INTEGER
);

CREATE TABLE postal_area (
    postal_area_id VARCHAR(16) PRIMARY KEY,
    city_id VARCHAR(32) NOT NULL REFERENCES city(city_id),
    postal_code VARCHAR(16) NOT NULL,
    area_name VARCHAR(100) NOT NULL
);

CREATE TABLE location (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    postal_area_id VARCHAR(16) NOT NULL REFERENCES postal_area(postal_area_id),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    altitude_meters DECIMAL(7,2),
    geohash VARCHAR(12) NOT NULL
);

CREATE TABLE facility (
    facility_id VARCHAR(32) PRIMARY KEY,
    location_id UUID NOT NULL REFERENCES location(location_id),
    facility_name VARCHAR(255) NOT NULL,
    facility_category VARCHAR(32) NOT NULL,
    total_area_sqft DECIMAL(12,2),
    operating_status VARCHAR(32) NOT NULL DEFAULT 'OPERATIONAL',
    opened_date DATE,
    closed_date DATE
);

-- Foundation A: Party & Identity
CREATE TABLE party (
    party_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_code VARCHAR(32) NOT NULL UNIQUE,
    party_type VARCHAR(16) NOT NULL CHECK (party_type IN ('PERSON', 'ORGANIZATION')),
    legal_name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE person (
    party_id UUID PRIMARY KEY REFERENCES party(party_id) ON DELETE RESTRICT,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(16),
    nationality CHAR(3)
);

CREATE TABLE organization (
    party_id UUID PRIMARY KEY REFERENCES party(party_id) ON DELETE RESTRICT,
    registered_name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(32) NOT NULL,
    incorporation_date DATE,
    incorporation_country_id CHAR(3) REFERENCES country(country_id),
    website_url VARCHAR(255)
);

CREATE TABLE identity (
    identity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE CASCADE,
    identity_type VARCHAR(32) NOT NULL,
    credential_identifier VARCHAR(255) NOT NULL UNIQUE,
    auth_provider VARCHAR(64) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    last_login_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE contact_point (
    contact_point_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE CASCADE,
    contact_type VARCHAR(32) NOT NULL,
    purpose VARCHAR(32) NOT NULL,
    address_line_1 VARCHAR(255),
    address_line_2 VARCHAR(255),
    postal_area_id VARCHAR(16) REFERENCES postal_area(postal_area_id),
    city_id VARCHAR(32) REFERENCES city(city_id),
    phone_number VARCHAR(32),
    email_address VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE
);

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

-- =============================================================================
-- TIER 1: ENTERPRISE & COMMERCIAL MASTERS
-- =============================================================================

CREATE TABLE enterprise (
    enterprise_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    corporate_name VARCHAR(255) NOT NULL,
    tax_identifier VARCHAR(64) NOT NULL,
    headquarters_country_id CHAR(3) NOT NULL REFERENCES country(country_id)
);

CREATE TABLE legal_entity (
    legal_entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enterprise_id UUID NOT NULL REFERENCES enterprise(enterprise_id) ON DELETE RESTRICT,
    registered_name VARCHAR(255) NOT NULL,
    cin_number VARCHAR(32) NOT NULL UNIQUE,
    pan_number VARCHAR(32) NOT NULL,
    country_id CHAR(3) NOT NULL REFERENCES country(country_id)
);

CREATE TABLE business_unit (
    business_unit_id VARCHAR(32) PRIMARY KEY,
    legal_entity_id UUID NOT NULL REFERENCES legal_entity(legal_entity_id) ON DELETE RESTRICT,
    bu_name VARCHAR(100) NOT NULL,
    operating_model VARCHAR(32) NOT NULL,
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id)
);

CREATE TABLE division (
    division_id VARCHAR(32) PRIMARY KEY,
    business_unit_id VARCHAR(32) NOT NULL REFERENCES business_unit(business_unit_id) ON DELETE RESTRICT,
    division_name VARCHAR(100) NOT NULL,
    segment_type VARCHAR(32) NOT NULL
);

CREATE TABLE org_department (
    org_department_id VARCHAR(32) PRIMARY KEY,
    division_id VARCHAR(32) NOT NULL REFERENCES division(division_id) ON DELETE RESTRICT,
    department_name VARCHAR(100) NOT NULL,
    department_head_id UUID REFERENCES party(party_id)
);

CREATE TABLE cost_center (
    cost_center_id VARCHAR(32) PRIMARY KEY,
    org_department_id VARCHAR(32) NOT NULL REFERENCES org_department(org_department_id) ON DELETE RESTRICT,
    cost_center_name VARCHAR(100) NOT NULL,
    budget_currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id)
);

CREATE TABLE profit_center (
    profit_center_id VARCHAR(32) PRIMARY KEY,
    division_id VARCHAR(32) NOT NULL REFERENCES division(division_id) ON DELETE RESTRICT,
    profit_center_name VARCHAR(100) NOT NULL,
    target_margin_pct DECIMAL(5,2)
);

-- Facility Subtypes
CREATE TABLE store (
    facility_id VARCHAR(32) PRIMARY KEY REFERENCES facility(facility_id) ON DELETE RESTRICT,
    store_name VARCHAR(255) NOT NULL,
    store_format VARCHAR(32) NOT NULL CHECK (store_format IN ('HYPERMARKET', 'SUPERMARKET', 'CONVENIENCE', 'EXPRESS')),
    retail_selling_area_sqft DECIMAL(10,2) NOT NULL,
    operating_status VARCHAR(32) NOT NULL DEFAULT 'OPERATIONAL'
);

CREATE TABLE warehouse (
    facility_id VARCHAR(32) PRIMARY KEY REFERENCES facility(facility_id) ON DELETE RESTRICT,
    warehouse_name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(32) NOT NULL CHECK (facility_type IN ('CENTRAL_DC', 'REGIONAL_DC', 'FULFILLMENT_CENTER', 'STORAGE_WAREHOUSE', 'CROSS_DOCK')),
    total_storage_capacity_pallets INTEGER NOT NULL,
    operating_status VARCHAR(32) NOT NULL DEFAULT 'OPERATIONAL'
);

CREATE TABLE production_site (
    facility_id VARCHAR(32) PRIMARY KEY REFERENCES facility(facility_id) ON DELETE RESTRICT,
    site_name VARCHAR(255) NOT NULL,
    plant_type VARCHAR(32) NOT NULL,
    operating_status VARCHAR(32) NOT NULL DEFAULT 'OPERATIONAL'
);

CREATE TABLE office (
    facility_id VARCHAR(32) PRIMARY KEY REFERENCES facility(facility_id) ON DELETE RESTRICT,
    office_name VARCHAR(255) NOT NULL,
    office_type VARCHAR(32) NOT NULL CHECK (office_type IN ('CORPORATE_HQ', 'REGIONAL_OFFICE', 'BRANCH'))
);

-- Merchandise Hierarchy
CREATE TABLE brand (
    brand_id VARCHAR(32) PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL,
    brand_tier VARCHAR(32) NOT NULL,
    owner_org_id UUID REFERENCES party(party_id)
);

CREATE TABLE merchandise_department (
    department_id INTEGER PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    buyer_role_id UUID REFERENCES party(party_id)
);

CREATE TABLE category (
    category_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES merchandise_department(department_id) ON DELETE RESTRICT,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE subcategory (
    subcategory_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES category(category_id) ON DELETE RESTRICT,
    subcategory_name VARCHAR(100) NOT NULL,
    target_margin_pct DECIMAL(5,2)
);

CREATE TABLE product_family (
    product_family_id INTEGER PRIMARY KEY,
    subcategory_id INTEGER NOT NULL REFERENCES subcategory(subcategory_id) ON DELETE RESTRICT,
    family_name VARCHAR(100) NOT NULL,
    demand_elasticity_class VARCHAR(32)
);

CREATE TABLE product (
    product_id INTEGER PRIMARY KEY,
    product_family_id INTEGER NOT NULL REFERENCES product_family(product_family_id) ON DELETE RESTRICT,
    brand_id VARCHAR(32) NOT NULL REFERENCES brand(brand_id) ON DELETE RESTRICT,
    product_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255)
);

CREATE TABLE sku (
    sku_id VARCHAR(32) PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
    barcode_ean13 VARCHAR(13) NOT NULL UNIQUE,
    uom_id VARCHAR(16) NOT NULL REFERENCES unit_of_measure(uom_id) ON DELETE RESTRICT,
    package_size VARCHAR(50) NOT NULL,
    net_weight_kg DECIMAL(8,4) NOT NULL,
    shelf_life_days INTEGER NOT NULL,
    is_perishable BOOLEAN NOT NULL DEFAULT FALSE,
    storage_condition VARCHAR(32) NOT NULL CHECK (storage_condition IN ('DRY', 'CHILLED', 'FROZEN', 'AMBIENT'))
);

CREATE TABLE batch (
    batch_id VARCHAR(64) PRIMARY KEY,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    mfg_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    producer_org_id UUID REFERENCES party(party_id)
);

CREATE TABLE lot (
    lot_id VARCHAR(64) PRIMARY KEY,
    batch_id VARCHAR(64) NOT NULL REFERENCES batch(batch_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    inspection_status VARCHAR(16) NOT NULL DEFAULT 'PASSED'
);

-- Profiles
CREATE TABLE supplier_profile (
    supplier_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    role_assignment_id UUID NOT NULL REFERENCES party_role_assignment(role_assignment_id) ON DELETE RESTRICT,
    vendor_tier VARCHAR(16) NOT NULL DEFAULT 'TIER_1',
    payment_term_id VARCHAR(32) NOT NULL REFERENCES payment_terms(payment_term_id) ON DELETE RESTRICT,
    default_currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    incoterm_id CHAR(3) NOT NULL REFERENCES incoterm(incoterm_id) ON DELETE RESTRICT,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE customer_segment (
    customer_segment_id VARCHAR(32) PRIMARY KEY,
    segment_name VARCHAR(100) NOT NULL,
    rfm_score_range VARCHAR(32),
    price_sensitivity_tier VARCHAR(16)
);

CREATE TABLE customer_profile (
    customer_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    role_assignment_id UUID NOT NULL REFERENCES party_role_assignment(role_assignment_id) ON DELETE RESTRICT,
    customer_segment_id VARCHAR(32) REFERENCES customer_segment(customer_segment_id) ON DELETE RESTRICT,
    customer_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    acquisition_channel VARCHAR(32)
);

CREATE TABLE carrier_profile (
    carrier_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    role_assignment_id UUID NOT NULL REFERENCES party_role_assignment(role_assignment_id) ON DELETE RESTRICT,
    fleet_type VARCHAR(32) NOT NULL,
    scac_code VARCHAR(16),
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE workforce_role (
    workforce_role_id VARCHAR(32) PRIMARY KEY,
    role_title VARCHAR(100) NOT NULL,
    base_hourly_rate DECIMAL(10,2) NOT NULL
);

CREATE TABLE employee_profile (
    employee_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    role_assignment_id UUID NOT NULL REFERENCES party_role_assignment(role_assignment_id) ON DELETE RESTRICT,
    assigned_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    workforce_role_id VARCHAR(32) NOT NULL REFERENCES workforce_role(workforce_role_id) ON DELETE RESTRICT,
    hire_date DATE NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
);

-- =============================================================================
-- TIER 2: PHYSICAL NETWORK & SOURCING TOPOLOGY
-- =============================================================================

CREATE TABLE store_warehouse_map (
    store_facility_id VARCHAR(32) NOT NULL REFERENCES store(facility_id) ON DELETE RESTRICT,
    warehouse_facility_id VARCHAR(32) NOT NULL REFERENCES warehouse(facility_id) ON DELETE RESTRICT,
    priority INTEGER NOT NULL DEFAULT 1,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 1),
    distance_km DECIMAL(8,2) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (store_facility_id, warehouse_facility_id)
);

CREATE TABLE supplier_sku_map (
    supplier_profile_id UUID NOT NULL REFERENCES supplier_profile(supplier_profile_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    unit_cost DECIMAL(12,4) NOT NULL CHECK (unit_cost > 0),
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    minimum_order_qty INTEGER NOT NULL DEFAULT 1 CHECK (minimum_order_qty >= 1),
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 1),
    supplier_priority INTEGER NOT NULL DEFAULT 1,
    is_preferred BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (supplier_profile_id, sku_id)
);

CREATE TABLE store_sku_assortment (
    facility_id VARCHAR(32) NOT NULL REFERENCES store(facility_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    facing_qty INTEGER NOT NULL DEFAULT 1,
    min_display_qty INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DISCONTINUED', 'SEASONAL_HOLD')),
    PRIMARY KEY (facility_id, sku_id, effective_start_date)
);

CREATE TABLE transport_lane (
    lane_id VARCHAR(32) PRIMARY KEY,
    origin_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    destination_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    standard_transit_days INTEGER NOT NULL CHECK (standard_transit_days >= 1),
    distance_km DECIMAL(8,2) NOT NULL,
    primary_carrier_profile_id UUID REFERENCES carrier_profile(carrier_profile_id) ON DELETE RESTRICT,
    standard_freight_cost DECIMAL(12,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_origin_dest UNIQUE (origin_facility_id, destination_facility_id)
);

CREATE TABLE asset_category (
    category_id VARCHAR(32) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE physical_asset (
    physical_asset_id VARCHAR(32) PRIMARY KEY,
    facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    category_id VARCHAR(32) NOT NULL REFERENCES asset_category(category_id) ON DELETE RESTRICT,
    asset_tag VARCHAR(64) NOT NULL UNIQUE,
    serial_number VARCHAR(100),
    make VARCHAR(100),
    model VARCHAR(100),
    purchase_date DATE,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE'
);

-- =============================================================================
-- TIER 3: POLICIES, CONTRACTS & PRICING
-- =============================================================================

CREATE TABLE contract (
    contract_id VARCHAR(32) PRIMARY KEY,
    contract_type VARCHAR(32) NOT NULL CHECK (contract_type IN ('SUPPLIER', 'CARRIER', 'CUSTOMER', 'SERVICE')),
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_term_id VARCHAR(32) NOT NULL REFERENCES payment_terms(payment_term_id) ON DELETE RESTRICT,
    incoterm_id CHAR(3) NOT NULL REFERENCES incoterm(incoterm_id) ON DELETE RESTRICT,
    contract_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE price_list (
    price_list_id VARCHAR(32) PRIMARY KEY,
    price_list_name VARCHAR(100) NOT NULL,
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    effective_start DATE NOT NULL,
    effective_end DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE price_record (
    price_record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    week_id INTEGER NOT NULL REFERENCES week(week_id) ON DELETE RESTRICT,
    price_type VARCHAR(16) NOT NULL CHECK (price_type IN ('BASE', 'RETAIL', 'MARKDOWN', 'PROMOTIONAL', 'OVERRIDE')),
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    effective_start DATE NOT NULL,
    effective_end DATE
);

-- =============================================================================
-- TIER 4: SIGNALS, EVENTS & DEMAND INTELLIGENCE
-- =============================================================================

CREATE TABLE event (
    event_id VARCHAR(32) PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    recur_rule VARCHAR(64),
    baseline_duration_days INTEGER NOT NULL
);

CREATE TABLE event_instance (
    event_instance_id VARCHAR(32) PRIMARY KEY,
    event_id VARCHAR(32) NOT NULL REFERENCES event(event_id) ON DELETE RESTRICT,
    year_id INTEGER NOT NULL REFERENCES calendar_year(year_id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    intensity_score DECIMAL(4,2) NOT NULL DEFAULT 1.0
);

CREATE TABLE event_impact (
    impact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(32) NOT NULL REFERENCES event(event_id) ON DELETE RESTRICT,
    target_level VARCHAR(16) NOT NULL CHECK (target_level IN ('DEPARTMENT', 'CATEGORY', 'SUBCATEGORY', 'PRODUCT_FAMILY')),
    target_id INTEGER NOT NULL,
    lift_multiplier DECIMAL(6,4) NOT NULL CHECK (lift_multiplier > 0),
    elasticity_factor DECIMAL(5,3) DEFAULT 1.0,
    CONSTRAINT uq_event_target UNIQUE (event_id, target_level, target_id)
);

CREATE TABLE event_interaction (
    interaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id_1 VARCHAR(32) NOT NULL REFERENCES event(event_id) ON DELETE RESTRICT,
    event_id_2 VARCHAR(32) NOT NULL REFERENCES event(event_id) ON DELETE RESTRICT,
    interaction_type VARCHAR(32) NOT NULL CHECK (interaction_type IN ('COMPOUNDING', 'CANNIBALIZING', 'SUBSTITUTION')),
    dampening_factor DECIMAL(5,3) NOT NULL DEFAULT 1.0,
    max_separation_days INTEGER NOT NULL DEFAULT 7,
    CONSTRAINT uq_event_pair UNIQUE (event_id_1, event_id_2)
);

CREATE TABLE regional_event_weight (
    weight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(32) NOT NULL REFERENCES event(event_id) ON DELETE RESTRICT,
    zone_id VARCHAR(32) NOT NULL REFERENCES zone_macro_region(zone_id) ON DELETE RESTRICT,
    weight_multiplier DECIMAL(5,3) NOT NULL CHECK (weight_multiplier >= 0),
    cultural_significance_tier VARCHAR(16) NOT NULL DEFAULT 'PRIMARY',
    CONSTRAINT uq_event_zone UNIQUE (event_id, zone_id)
);

CREATE TABLE weather_observation (
    weather_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id VARCHAR(32) NOT NULL REFERENCES zone_macro_region(zone_id) ON DELETE RESTRICT,
    week_id INTEGER NOT NULL REFERENCES week(week_id) ON DELETE RESTRICT,
    mean_temperature_c DECIMAL(5,2) NOT NULL,
    rainfall_mm DECIMAL(7,2) NOT NULL,
    humidity_pct DECIMAL(5,2) NOT NULL,
    severe_weather_flag BOOLEAN NOT NULL DEFAULT FALSE
);

-- =============================================================================
-- TIER 5: TRANSACTION ENGINES
-- =============================================================================

CREATE TABLE purchase_order (
    po_id VARCHAR(32) PRIMARY KEY,
    supplier_profile_id UUID NOT NULL REFERENCES supplier_profile(supplier_profile_id) ON DELETE RESTRICT,
    destination_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    order_date DATE NOT NULL,
    expected_delivery_date DATE NOT NULL,
    payment_term_id VARCHAR(32) NOT NULL REFERENCES payment_terms(payment_term_id) ON DELETE RESTRICT,
    incoterm_id CHAR(3) NOT NULL REFERENCES incoterm(incoterm_id) ON DELETE RESTRICT,
    total_amount DECIMAL(14,2) NOT NULL,
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    po_status VARCHAR(16) NOT NULL DEFAULT 'ISSUED'
);

CREATE TABLE po_line (
    po_line_id VARCHAR(64) PRIMARY KEY,
    po_id VARCHAR(32) NOT NULL REFERENCES purchase_order(po_id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    ordered_qty INTEGER NOT NULL CHECK (ordered_qty > 0),
    unit_price DECIMAL(12,4) NOT NULL CHECK (unit_price > 0),
    tax_rate_pct DECIMAL(5,2) DEFAULT 0.0,
    line_total DECIMAL(14,2) NOT NULL,
    received_qty INTEGER NOT NULL DEFAULT 0,
    line_status VARCHAR(16) NOT NULL DEFAULT 'ISSUED'
);

CREATE TABLE shipment (
    shipment_id VARCHAR(32) PRIMARY KEY,
    origin_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    destination_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    carrier_profile_id UUID NOT NULL REFERENCES carrier_profile(carrier_profile_id) ON DELETE RESTRICT,
    departure_time TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_arrival_time TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_arrival_time TIMESTAMP WITH TIME ZONE,
    shipment_status VARCHAR(16) NOT NULL DEFAULT 'BOOKED'
);

CREATE TABLE shipment_line (
    shipment_line_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(32) NOT NULL REFERENCES shipment(shipment_id) ON DELETE CASCADE,
    po_line_id VARCHAR(64) REFERENCES po_line(po_line_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    shipped_qty INTEGER NOT NULL CHECK (shipped_qty > 0)
);

CREATE TABLE sales_channel (
    channel_id VARCHAR(32) PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL
);

CREATE TABLE customer_session (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_profile_id UUID NOT NULL REFERENCES customer_profile(customer_profile_id) ON DELETE CASCADE,
    start_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    end_timestamp TIMESTAMP WITH TIME ZONE,
    channel_id VARCHAR(32) NOT NULL REFERENCES sales_channel(channel_id) ON DELETE RESTRICT
);

CREATE TABLE cart (
    cart_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES customer_session(session_id) ON DELETE CASCADE,
    customer_profile_id UUID NOT NULL REFERENCES customer_profile(customer_profile_id) ON DELETE CASCADE,
    cart_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    total_estimated_value DECIMAL(12,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE basket (
    basket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID REFERENCES cart(cart_id) ON DELETE RESTRICT,
    customer_profile_id UUID REFERENCES customer_profile(customer_profile_id) ON DELETE RESTRICT,
    facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    finalized_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    gross_amount DECIMAL(14,2) NOT NULL,
    net_amount DECIMAL(14,2) NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL
);

CREATE TABLE basket_line (
    basket_line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    basket_id UUID NOT NULL REFERENCES basket(basket_id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_retail_price DECIMAL(12,2) NOT NULL,
    discount_applied DECIMAL(12,2) DEFAULT 0.0,
    net_line_total DECIMAL(12,2) NOT NULL
);

CREATE TABLE sales_transaction (
    transaction_id VARCHAR(64) PRIMARY KEY,
    basket_id UUID NOT NULL REFERENCES basket(basket_id) ON DELETE RESTRICT,
    facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    channel_id VARCHAR(32) NOT NULL REFERENCES sales_channel(channel_id) ON DELETE RESTRICT,
    transaction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_net_amount DECIMAL(14,2) NOT NULL,
    total_tax_amount DECIMAL(12,2) NOT NULL,
    total_gross_amount DECIMAL(14,2) NOT NULL
);

CREATE TABLE sales_line (
    sales_line_id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) NOT NULL REFERENCES sales_transaction(transaction_id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0.0,
    net_sales_amount DECIMAL(12,2) NOT NULL,
    price_record_id UUID NOT NULL REFERENCES price_record(price_record_id) ON DELETE RESTRICT
);

-- =============================================================================
-- TIER 6: OPERATIONAL STATE & REVERSE LOGISTICS
-- =============================================================================

CREATE TABLE goods_receipt (
    goods_receipt_id VARCHAR(32) PRIMARY KEY,
    po_id VARCHAR(32) NOT NULL REFERENCES purchase_order(po_id) ON DELETE RESTRICT,
    receiving_facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    receipt_timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE goods_receipt_line (
    gr_line_id VARCHAR(64) PRIMARY KEY,
    goods_receipt_id VARCHAR(32) NOT NULL REFERENCES goods_receipt(goods_receipt_id) ON DELETE CASCADE,
    po_line_id VARCHAR(64) NOT NULL REFERENCES po_line(po_line_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    received_qty INTEGER NOT NULL,
    accepted_qty INTEGER NOT NULL,
    rejected_qty INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE inventory_position (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    lot_id VARCHAR(64) REFERENCES lot(lot_id) ON DELETE RESTRICT,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    quantity_reserved INTEGER NOT NULL DEFAULT 0,
    quantity_allocated INTEGER NOT NULL DEFAULT 0,
    quantity_available INTEGER NOT NULL DEFAULT 0,
    quantity_damaged INTEGER NOT NULL DEFAULT 0,
    quantity_quarantined INTEGER NOT NULL DEFAULT 0,
    quantity_expired INTEGER NOT NULL DEFAULT 0,
    quantity_in_transit INTEGER NOT NULL DEFAULT 0,
    uom_id VARCHAR(16) NOT NULL REFERENCES unit_of_measure(uom_id) ON DELETE RESTRICT,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_available_calc CHECK (quantity_available = quantity_on_hand - quantity_reserved - quantity_allocated - (quantity_damaged + quantity_quarantined + quantity_expired))
);

-- =============================================================================
-- TIER 7: FINANCIAL LEDGERS, SIMULATION GROUND TRUTH & GOVERNANCE
-- =============================================================================

CREATE TABLE invoice (
    invoice_id VARCHAR(64) PRIMARY KEY,
    invoice_type VARCHAR(16) NOT NULL CHECK (invoice_type IN ('CUSTOMER', 'SUPPLIER', 'CARRIER')),
    invoice_number VARCHAR(64) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    party_id UUID NOT NULL REFERENCES party(party_id) ON DELETE RESTRICT,
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    total_amount DECIMAL(14,2) NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0.0,
    balance_outstanding DECIMAL(14,2) NOT NULL,
    invoice_status VARCHAR(16) NOT NULL DEFAULT 'ISSUED'
);

CREATE TABLE customer_invoice (
    invoice_id VARCHAR(64) PRIMARY KEY REFERENCES invoice(invoice_id) ON DELETE CASCADE,
    sales_transaction_id VARCHAR(64) REFERENCES sales_transaction(transaction_id) ON DELETE RESTRICT,
    customer_profile_id UUID NOT NULL REFERENCES customer_profile(customer_profile_id) ON DELETE RESTRICT
);

CREATE TABLE supplier_invoice (
    invoice_id VARCHAR(64) PRIMARY KEY REFERENCES invoice(invoice_id) ON DELETE CASCADE,
    po_id VARCHAR(32) NOT NULL REFERENCES purchase_order(po_id) ON DELETE RESTRICT,
    supplier_profile_id UUID NOT NULL REFERENCES supplier_profile(supplier_profile_id) ON DELETE RESTRICT,
    three_way_match_status VARCHAR(16) NOT NULL DEFAULT 'MATCHED'
);

CREATE TABLE supplier_invoice_line (
    invoice_line_id VARCHAR(64) PRIMARY KEY,
    invoice_id VARCHAR(64) NOT NULL REFERENCES supplier_invoice(invoice_id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    po_line_id VARCHAR(64) NOT NULL REFERENCES po_line(po_line_id) ON DELETE RESTRICT,
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    invoiced_qty INTEGER NOT NULL CHECK (invoiced_qty > 0),
    unit_price DECIMAL(12,4) NOT NULL CHECK (unit_price > 0),
    line_total DECIMAL(14,2) NOT NULL,
    tax_amount DECIMAL(14,2) NOT NULL DEFAULT 0.0,
    CONSTRAINT uq_supplier_invoice_line UNIQUE (invoice_id, line_number)
);

CREATE TABLE payment (
    payment_id VARCHAR(64) PRIMARY KEY,
    payment_type VARCHAR(16) NOT NULL CHECK (payment_type IN ('CUSTOMER', 'SUPPLIER', 'CARRIER')),
    payment_date DATE NOT NULL,
    amount DECIMAL(14,2) NOT NULL CHECK (amount > 0),
    currency_id CHAR(3) NOT NULL REFERENCES currency(currency_id) ON DELETE RESTRICT,
    payment_status VARCHAR(16) NOT NULL DEFAULT 'SETTLED'
);

CREATE TABLE payment_allocation (
    allocation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id VARCHAR(64) NOT NULL REFERENCES payment(payment_id) ON DELETE CASCADE,
    invoice_id VARCHAR(64) NOT NULL REFERENCES invoice(invoice_id) ON DELETE RESTRICT,
    allocated_amount DECIMAL(14,2) NOT NULL CHECK (allocated_amount > 0),
    discount_applied DECIMAL(12,2) DEFAULT 0.0,
    allocation_date DATE NOT NULL
);

CREATE TABLE three_way_match_record (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_line_id VARCHAR(64) NOT NULL REFERENCES po_line(po_line_id) ON DELETE RESTRICT,
    gr_line_id VARCHAR(64) NOT NULL REFERENCES goods_receipt_line(gr_line_id) ON DELETE RESTRICT,
    supplier_invoice_line_id VARCHAR(64) NOT NULL REFERENCES supplier_invoice_line(invoice_line_id) ON DELETE RESTRICT,
    ordered_qty INTEGER NOT NULL,
    received_accepted_qty INTEGER NOT NULL,
    invoiced_qty INTEGER NOT NULL,
    po_unit_price DECIMAL(12,4) NOT NULL,
    invoiced_unit_price DECIMAL(12,4) NOT NULL,
    variance_amount DECIMAL(14,2) NOT NULL,
    match_status VARCHAR(16) NOT NULL CHECK (match_status IN ('EXACT_MATCH', 'WITHIN_TOLERANCE', 'PRICE_VARIANCE', 'QTY_VARIANCE', 'REJECTED')),
    verified_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chart_of_accounts (
    coa_id VARCHAR(32) PRIMARY KEY,
    enterprise_id UUID NOT NULL REFERENCES enterprise(enterprise_id) ON DELETE RESTRICT,
    coa_name VARCHAR(100) NOT NULL
);

CREATE TABLE gl_account (
    gl_account_id VARCHAR(32) PRIMARY KEY,
    coa_id VARCHAR(32) NOT NULL REFERENCES chart_of_accounts(coa_id) ON DELETE RESTRICT,
    account_code VARCHAR(32) NOT NULL UNIQUE,
    account_name VARCHAR(100) NOT NULL,
    account_class VARCHAR(16) NOT NULL CHECK (account_class IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE'))
);

CREATE TABLE journal_entry (
    journal_entry_id VARCHAR(64) PRIMARY KEY,
    fiscal_period_id VARCHAR(16) NOT NULL REFERENCES fiscal_period(fiscal_period_id) ON DELETE RESTRICT,
    entry_date DATE NOT NULL,
    posting_date DATE NOT NULL,
    total_debit DECIMAL(16,2) NOT NULL,
    total_credit DECIMAL(16,2) NOT NULL,
    is_posted BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_debit_credit_balance CHECK (total_debit = total_credit)
);

CREATE TABLE journal_line (
    journal_line_id VARCHAR(64) PRIMARY KEY,
    journal_entry_id VARCHAR(64) NOT NULL REFERENCES journal_entry(journal_entry_id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    gl_account_id VARCHAR(32) NOT NULL REFERENCES gl_account(gl_account_id) ON DELETE RESTRICT,
    debit_amount DECIMAL(14,2) NOT NULL DEFAULT 0.0,
    credit_amount DECIMAL(14,2) NOT NULL DEFAULT 0.0
);

CREATE TABLE demand_observation (
    observation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id VARCHAR(32) NOT NULL REFERENCES sku(sku_id) ON DELETE RESTRICT,
    facility_id VARCHAR(32) NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    week_id INTEGER NOT NULL REFERENCES week(week_id) ON DELETE RESTRICT,
    latent_demand DECIMAL(10,2) NOT NULL,
    observed_sales DECIMAL(10,2) NOT NULL,
    lost_sales DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    inventory_available INTEGER NOT NULL,
    inventory_ending INTEGER NOT NULL,
    service_level_pct DECIMAL(5,2) NOT NULL,
    CONSTRAINT chk_lost_sales CHECK (latent_demand - lost_sales = observed_sales)
);

CREATE TABLE event_attribution (
    attribution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    observation_id UUID NOT NULL REFERENCES demand_observation(observation_id) ON DELETE CASCADE,
    event_instance_id VARCHAR(32) NOT NULL REFERENCES event_instance(event_instance_id) ON DELETE RESTRICT,
    attribution_weight DECIMAL(6,4) NOT NULL CHECK (attribution_weight BETWEEN 0 AND 1),
    algorithm_version VARCHAR(32) NOT NULL
);

CREATE TABLE lifecycle_status_event (
    status_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(32) NOT NULL CHECK (entity_type IN (
        'PURCHASE_ORDER', 'PRODUCTION_ORDER', 'SALES_ORDER', 'SHIPMENT',
        'INVOICE', 'PAYMENT', 'RETURN_ORDER', 'WORK_ORDER', 'CONTRACT'
    )),
    entity_id VARCHAR(64) NOT NULL,
    from_status VARCHAR(32) NOT NULL,
    to_status VARCHAR(32) NOT NULL,
    effective_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason_code VARCHAR(64),
    actor_party_id UUID REFERENCES party(party_id) ON DELETE RESTRICT
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE & TRAVERSAL
-- =============================================================================
CREATE INDEX idx_sku_product ON sku (product_id);
CREATE INDEX idx_price_record_lookup ON price_record (facility_id, sku_id, week_id);
CREATE INDEX idx_dobs_lookup ON demand_observation (facility_id, sku_id, week_id);
CREATE INDEX idx_sales_line_stxn ON sales_line (transaction_id);
CREATE INDEX idx_palloc_lookup ON payment_allocation (invoice_id, payment_id);
CREATE INDEX idx_jline_je ON journal_line (journal_entry_id);
CREATE INDEX idx_status_event_entity ON lifecycle_status_event (entity_type, entity_id);
