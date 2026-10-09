# Deliverable D02 -- Neo4j Enterprise Graph Schema Specification

## 1. Architectural Overview

The Neo4j graph database serves as the **Materialized Topological Projection** for the SCOF V2 platform. Derived directly from the relational System of Record ([ADR 001](file:///d:/projects/SCOF_V1/SCOF/docs/adr/001_enterprise_knowledge_fabric_over_monolithic_generator.md)), the graph provides high-performance, index-backed structural traversal capabilities across the enterprise supply network.

### Summary Metrics (Certified in Gate 6 Audit)
- **Total Materialized Nodes**: 3,728,199
- **Total Materialized Edges**: 2,104,514
- **Node Labels**: 50
- **Total Schema Constraints**: 59 (51 Frozen Core Constraints + 8 Extended Hardening Constraints)
- **Source CSV Files**: 93 CSV files in [`datasets/neo4j_graph/`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/)
- **Import Script**: [`datasets/neo4j_graph/import_neo4j_graph.cql`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/import_neo4j_graph.cql)

---

## 2. Node Taxonomy & Canonical Key Conventions

The graph organizes the supply chain into four structural domains, using strict canonical ID prefix conventions:

### 2.1 Facilities & Physical Infrastructure
| Node Label | Key Property | ID Prefix Example | Description |
|---|---|---|---|
| `Facility` | `facility_id` | `FAC-DC-001` | Base label for all physical nodes |
| `DistributionCenter` | `facility_id` | `FAC-DC-001` | Central multi-temperature fulfillment hub |
| `RegionalDC` | `facility_id` | `FAC-RDC-012` | Regional distribution center |
| `Store` | `facility_id` | `FAC-STR-0491` | Customer-facing retail supermarket / store |
| `CrossDock` | `facility_id` | `FAC-XD-003` | Rapid transshipment consolidation point |
| `StorageLocation` | `location_id` | `LOC-BIN-00912` | Specific aisle / rack / bin location |

### 2.2 Sourcing & Supplier Network
| Node Label | Key Property | ID Prefix Example | Description |
|---|---|---|---|
| `Supplier` | `supplier_id` | `SUP-00142` | Corporate vendor organization |
| `SupplierSite` | `supplier_site_id`| `SUBSITE-0082` | Physical manufacturing or export plant |
| `VendorContract` | `contract_id` | `CTR-2026-004` | Commercial sourcing agreement |

### 2.3 Merchandise Taxonomy & Catalog
| Node Label | Key Property | ID Prefix Example | Description |
|---|---|---|---|
| `Department` | `department_id` | `DEP-01` | Top-level division (e.g. Fresh Produce, Ambient Grocery) |
| `Category` | `category_id` | `CAT-0104` | Major category classification |
| `Subcategory` | `subcategory_id` | `SUBCAT-010402` | Sub-category grouping |
| `ProductFamily` | `product_family_id`| `FAM-00412` | Functional product line |
| `Brand` | `brand_id` | `BRD-0089` | Commercial brand entity |
| `Product` | `product_id` | `PRD-10023` | Abstract product master entity |
| `SKU` | `sku_id` | `SKU-000492` | Stock Keeping Unit (49,616 nodes) |

### 2.4 Multi-Modal Logistics Network
| Node Label | Key Property | ID Prefix Example | Description |
|---|---|---|---|
| `TransportLane` | `lane_id` | `LANE-00492` | Physical origin-to-destination corridor |
| `Carrier` | `carrier_id` | `CAR-0012` | Commercial freight transportation provider |
| `TransportMode` | `mode_id` | `MODE-ROAD` | Transport modality (`ROAD`, `RAIL`, `AIR`, `OCEAN`) |
| `TransportVehicle`| `vehicle_id` | `VEH-TRK-0192` | Individual tractor / trailer / reefer unit |

---

## 3. Relationship Types & Edge Properties

Relationships represent physical movement corridors, organizational containment, and catalog taxonomy. All edge properties maintain exact units of measure:

| Relationship Type | Source Node $\to$ Target Node | Edge Properties |
|---|---|---|
| `CONNECTS_TO` | `(:Facility) -> (:Facility)` | `lane_id`, `distance_km`, `nominal_transit_hours`, `mode` |
| `SERVICED_BY` | `(:Store) -> (:DistributionCenter)` | `service_priority`, `target_fill_rate`, `replenishment_day` |
| `SUPPLIES` | `(:SupplierSite) -> (:SKU)` | `contract_cost`, `lead_time_days`, `moq_units`, `is_primary` |
| `OPERATES_SITE` | `(:Supplier) -> (:SupplierSite)` | `site_type`, `capacity_rating` |
| `STORED_AT` | `(:SKU) -> (:Facility)` | `safety_stock_qty`, `reorder_point_qty`, `storage_type` |
| `PART_OF` | `(:Subcategory) -> (:Category)` | `sequence_order` |
| `PART_OF` | `(:Category) -> (:Department)` | `sequence_order` |
| `BELONGS_TO` | `(:SKU) -> (:Subcategory)` | `effective_date` |
| `PRODUCES` | `(:Brand) -> (:SKU)` | `license_type` |
| `CARRIES` | `(:Carrier) -> (:TransportLane)` | `contract_rate_per_km`, `transit_time_sla_hours` |

---

## 4. Cypher DDL & Schema Constraints

Below is an excerpt from [`datasets/neo4j_graph/import_neo4j_graph.cql`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/import_neo4j_graph.cql) establishing uniqueness constraints and indexes:

```cypher
// Uniqueness Constraints (51 Frozen Core + 8 Hardening Constraints)
CREATE CONSTRAINT c_facility_id IF NOT EXISTS FOR (n:Facility) REQUIRE n.facility_id IS UNIQUE;
CREATE CONSTRAINT c_sku_id IF NOT EXISTS FOR (n:SKU) REQUIRE n.sku_id IS UNIQUE;
CREATE CONSTRAINT c_sku_code IF NOT EXISTS FOR (n:SKU) REQUIRE n.sku_code IS UNIQUE;
CREATE CONSTRAINT c_supplier_id IF NOT EXISTS FOR (n:Supplier) REQUIRE n.supplier_id IS UNIQUE;
CREATE CONSTRAINT c_supplier_site_id IF NOT EXISTS FOR (n:SupplierSite) REQUIRE n.supplier_site_id IS UNIQUE;
CREATE CONSTRAINT c_lane_id IF NOT EXISTS FOR (n:TransportLane) REQUIRE n.lane_id IS UNIQUE;
CREATE CONSTRAINT c_carrier_id IF NOT EXISTS FOR (n:Carrier) REQUIRE n.carrier_id IS UNIQUE;
CREATE CONSTRAINT c_department_id IF NOT EXISTS FOR (n:Department) REQUIRE n.department_id IS UNIQUE;
CREATE CONSTRAINT c_category_id IF NOT EXISTS FOR (n:Category) REQUIRE n.category_id IS UNIQUE;
CREATE CONSTRAINT c_subcategory_id IF NOT EXISTS FOR (n:Subcategory) REQUIRE n.subcategory_id IS UNIQUE;

// High-Throughput Lookup Indexes
CREATE INDEX idx_facility_type IF NOT EXISTS FOR (n:Facility) ON (n.facility_type);
CREATE INDEX idx_sku_storage_type IF NOT EXISTS FOR (n:SKU) ON (n.storage_type);
CREATE INDEX idx_lane_mode IF NOT EXISTS FOR (n:TransportLane) ON (n.mode);
```

---

## 5. Bounded MCP Traversal Tool Contracts

To ensure sub-second response times and prevent server memory exhaustion ([ADR 005b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005b_amendment_materialized_graph_projection_and_bounded_queries.md)), all graph interactions are mediated through depth-bounded query tools:

### Tool 1: `get_upstream_supply_path`
- **Bound**: `max_depth = 3`
- **Cypher Signature**:
  ```cypher
  MATCH path = (s:Store {facility_id: $facility_id})<-[:SERVICED_BY*1..2]-(dc:DistributionCenter)<-[:SUPPLIED_BY*1]-(site:SupplierSite)
  WHERE NONE(n IN nodes(path) WHERE n.facility_id IN $disabled_nodes)
  RETURN path LIMIT 25;
  ```

### Tool 2: `get_affected_downstream_facilities`
- **Bound**: `max_hops = 2`
- **Cypher Signature**:
  ```cypher
  MATCH path = (orig:Facility {facility_id: $disrupted_facility_id})-[:CONNECTS_TO*1..2]->(dest:Facility)
  WHERE NONE(r IN relationships(path) WHERE r.lane_id IN $disabled_edges)
  RETURN dest.facility_id AS facility_id, dest.facility_type AS facility_type, length(path) AS hops;
  ```

### Tool 3: `find_alternate_carrier_routes`
- **Bound**: `max_transit_days = 5.0`
- **Cypher Signature**:
  ```cypher
  MATCH (orig:Facility {facility_id: $origin_id})-[r:CONNECTS_TO]->(dest:Facility {facility_id: $destination_id})
  WHERE NOT r.lane_id IN $disabled_edges AND (r.nominal_transit_hours / 24.0) <= $max_transit_days
  RETURN r.lane_id AS lane_id, r.mode AS mode, r.nominal_transit_hours AS transit_hours;
  ```

### Tool 4: `get_category_assortment_tree`
- **Bound**: `max_depth = 4`
- **Cypher Signature**:
  ```cypher
  MATCH path = (d:Department {department_id: $department_id})<-[:PART_OF*1..3]-(sc:Subcategory)<-[:BELONGS_TO]-(s:SKU)
  RETURN d.department_name, sc.subcategory_name, count(s) AS sku_count;
  ```

---

## 6. Graph Immutability & In-Memory Scenario Masking

In accordance with [ADR 006](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md), graph traversals apply scenario perturbations in-memory using parameters without issuing write transactions:

```cypher
// Parameterized Scenario Masking Query
MATCH path = (origin:Facility)-[r:CONNECTS_TO*1..3]->(dest:Facility)
WHERE NONE(node IN nodes(path) WHERE node.facility_id IN $disabled_nodes)
  AND NONE(edge IN relationships(path) WHERE edge.lane_id IN $disabled_edges)
RETURN path;
```
