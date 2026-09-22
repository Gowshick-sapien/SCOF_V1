# Deliverable D2 — Neo4j Graph Schema Documentation

## 1. Overview
The Knowledge Layer uses Neo4j to model the multi-echelon supply chain network topology, sourcing relationships, product-to-location mappings, and transport routing graphs. The graph structure allows specialist agents (such as the Supplier Agent in D4 and Transportation Agent in D4) and the Consensus Engine (D6) to execute Graph RAG operations, traverse multi-hop supply routes, discover alternate suppliers, and perform upstream bottleneck impact analysis.

---

## 2. Node Schema Specifications & Primary Key Alignment
Node `id` properties strictly mirror PostgreSQL primary keys (UUIDs or canonical string IDs like `mfg-01`, `sup-01`, `prod-101`, `wh-01`, `dc-01`, `route-sup01-wh01`). No Neo4j-specific synthetic keys are generated.

### Node: `:Manufacturer`
- **Properties**:
  - `id` (STRING, Primary Key, Indexed): e.g. `"mfg-01"`
  - `name` (STRING): e.g. `"Apex Electronics Manufacturing"`
  - `latitude` (FLOAT): e.g. `22.5431`
  - `longitude` (FLOAT): e.g. `114.0579`

### Node: `:Supplier`
- **Properties**:
  - `id` (STRING, Primary Key, Indexed): e.g. `"sup-01"`
  - `name` (STRING): e.g. `"Semico Components"`
  - `reliability_profile` (STRING, Indexed): `"high"`, `"medium"`, or `"volatile"`
  - `lead_time_days` (INTEGER): e.g. `7`
  - `latitude` (FLOAT): e.g. `24.1477`
  - `longitude` (FLOAT): e.g. `120.6736`

### Node: `:Product`
- **Properties**:
  - `id` (STRING, Primary Key, Indexed): e.g. `"prod-101"`
  - `name` (STRING): e.g. `"Smart IoT Controller"`
  - `sku` (STRING, Unique): e.g. `"SKU-IOT-101"`

### Node: `:Warehouse`
- **Properties**:
  - `id` (STRING, Primary Key, Indexed): e.g. `"wh-01"`
  - `name` (STRING): e.g. `"East Asia Transit Hub"`
  - `capacity_units` (INTEGER): e.g. `50000`
  - `latitude` (FLOAT): e.g. `22.3193`
  - `longitude` (FLOAT): e.g. `114.1694`

### Node: `:DistributionCenter`
- **Properties**:
  - `id` (STRING, Primary Key, Indexed): e.g. `"dc-01"`
  - `name` (STRING): e.g. `"Central Distribution Hub"`
  - `latitude` (FLOAT): e.g. `25.0330`
  - `longitude` (FLOAT): e.g. `121.5654`

### Node: `:Route`
- **Properties**:
  - `id` (STRING, Primary Key, Indexed): e.g. `"route-sup01-wh01"`
  - `mode` (STRING, Indexed): `"ocean"`, `"air"`, or `"truck"`
  - `distance_km` (FLOAT): e.g. `750.50`
  - `standard_transit_days` (INTEGER): e.g. `3`
  - `origin_type` (STRING): `"supplier"`, `"warehouse"`, or `"manufacturer"`
  - `origin_id` (STRING): e.g. `"sup-01"`
  - `destination_type` (STRING): `"warehouse"` or `"distribution_center"`
  - `destination_id` (STRING): e.g. `"wh-01"`

---

## 3. Relationship Specifications & Edge Properties

| Origin Node | Relationship | Destination Node | Standard Edge Properties |
| ----------- | ------------ | ---------------- | ----------------------- |
| `:Manufacturer` | `PRODUCES` | `:Product` | `production_capacity_units`, `created_at` |
| `:Supplier` | `SUPPLIES` | `:Product` | `lead_time_days`, `unit_cost`, `minimum_order_qty`, `capacity`, `is_preferred`, `contract_id` |
| `:Product` | `STORED_IN` | `:Warehouse` | `max_storage_units`, `storage_cost_per_unit`, `created_at` |
| `:Supplier` | `SHIPS_VIA` | `:Route` | `mode`, `transit_days`, `cost`, `risk_score` |
| `:Warehouse` | `SHIPS_VIA` | `:Route` | `mode`, `transit_days`, `cost`, `risk_score` |
| `:Route` | `DELIVERS_TO` | `:Warehouse` | `service_level_agreement_days`, `created_at` |
| `:Route` | `DELIVERS_TO` | `:DistributionCenter` | `service_level_agreement_days`, `created_at` |
| `:Supplier` | `ALTERNATE_FOR` | `:Supplier` | `product_id`, `cost_delta_pct`, `lead_time_delta_days` |

---

## 4. Cypher DDL Initialization (`01_init_graph_schema.cypher`)

```cypher
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

// Comprehensive Performance Indexes
CREATE INDEX idx_manufacturer_id IF NOT EXISTS FOR (m:Manufacturer) ON (m.id);
CREATE INDEX idx_supplier_id IF NOT EXISTS FOR (s:Supplier) ON (s.id);
CREATE INDEX idx_product_id IF NOT EXISTS FOR (p:Product) ON (p.id);
CREATE INDEX idx_warehouse_id IF NOT EXISTS FOR (w:Warehouse) ON (w.id);
CREATE INDEX idx_dc_id IF NOT EXISTS FOR (d:DistributionCenter) ON (d.id);
CREATE INDEX idx_route_id IF NOT EXISTS FOR (r:Route) ON (r.id);

CREATE INDEX idx_supplier_reliability IF NOT EXISTS FOR (s:Supplier) ON (s.reliability_profile);
CREATE INDEX idx_route_mode IF NOT EXISTS FOR (r:Route) ON (r.mode);
```

---

## 5. Key Cypher Query Patterns for Graph RAG

### Shortest Supply Route Traversal
```cypher
MATCH p=shortestPath((s:Supplier {id: $supplier_id})-[*..6]-(w:Warehouse {id: $warehouse_id}))
RETURN p;
```

### Upstream Product Sourcing Lineage & Edge Property Evaluation
```cypher
MATCH (p:Product {id: $product_id})<-[r:SUPPLIES]-(s:Supplier)
RETURN s.id AS supplier_id, s.name AS supplier_name, s.reliability_profile AS reliability,
       r.unit_cost AS cost, r.lead_time_days AS lead_time, r.is_preferred AS is_preferred;
```

### Alternate Supplier Discovery
```cypher
MATCH (primary:Supplier {id: $supplier_id})-[:SUPPLIES]->(p:Product)<-[r:SUPPLIES]-(alt:Supplier)
WHERE alt.id <> primary.id
RETURN alt.id AS alt_supplier_id, alt.name AS alt_supplier_name, r.unit_cost AS alt_cost, r.lead_time_days AS alt_lead_time;
```
