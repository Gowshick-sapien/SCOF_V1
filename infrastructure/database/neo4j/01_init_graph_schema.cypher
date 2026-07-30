// Neo4j Graph Schema DDL Initialization Script (v2.0.0)
// Establishes schema versioning, node uniqueness constraints, and performance indexes.

// Schema Migration & Version Tracking
MERGE (v:SchemaVersion {id: 'schema_v2'})
ON CREATE SET v.version = '2.0.0', v.applied_at = datetime();

// Unique Node Constraints
CREATE CONSTRAINT cst_manufacturer_id IF NOT EXISTS FOR (m:Manufacturer) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT cst_supplier_id IF NOT EXISTS FOR (s:Supplier) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT cst_product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT cst_warehouse_id IF NOT EXISTS FOR (w:Warehouse) REQUIRE w.id IS UNIQUE;
CREATE CONSTRAINT cst_dc_id IF NOT EXISTS FOR (d:DistributionCenter) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT cst_route_id IF NOT EXISTS FOR (r:Route) REQUIRE r.id IS UNIQUE;

// Node Property Performance Indexes
CREATE INDEX idx_manufacturer_id IF NOT EXISTS FOR (m:Manufacturer) ON (m.id);
CREATE INDEX idx_supplier_id IF NOT EXISTS FOR (s:Supplier) ON (s.id);
CREATE INDEX idx_product_id IF NOT EXISTS FOR (p:Product) ON (p.id);
CREATE INDEX idx_warehouse_id IF NOT EXISTS FOR (w:Warehouse) ON (w.id);
CREATE INDEX idx_dc_id IF NOT EXISTS FOR (d:DistributionCenter) ON (d.id);
CREATE INDEX idx_route_id IF NOT EXISTS FOR (r:Route) ON (r.id);

CREATE INDEX idx_supplier_reliability IF NOT EXISTS FOR (s:Supplier) ON (s.reliability_profile);
CREATE INDEX idx_route_mode IF NOT EXISTS FOR (r:Route) ON (r.mode);
