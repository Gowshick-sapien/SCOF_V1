import logging
from typing import Any, Dict, List, Optional
from shared.scof_shared.knowledge.graph_client import Neo4jGraphClient
from services.etl.src.config import config

logger = logging.getLogger(__name__)

class GraphLoader:
    """
    High-performance Cypher Graph Loader executing UNWIND batch queries
    with MERGE clauses and retry logic to populate Neo4j nodes and edges idempotently.
    """

    def __init__(self, client: Optional[Neo4jGraphClient] = None):
        self.client = client or Neo4jGraphClient(uri=config.neo4j_uri, auth=(config.neo4j_user, config.neo4j_password))

    def load_nodes(self, payload: Dict[str, List[Dict[str, Any]]]) -> None:
        mfg_cypher = """
        UNWIND $batch AS row
        MERGE (m:Manufacturer {id: row.id})
        ON CREATE SET m.name = row.name, m.latitude = row.latitude, m.longitude = row.longitude, m.created_at = datetime()
        ON MATCH SET m.name = row.name, m.latitude = row.latitude, m.longitude = row.longitude, m.updated_at = datetime();
        """
        if payload.get("manufacturers"):
            self.client.execute_batch(mfg_cypher, payload["manufacturers"])

        sup_cypher = """
        UNWIND $batch AS row
        MERGE (s:Supplier {id: row.id})
        ON CREATE SET s.name = row.name, s.reliability_profile = row.reliability_profile,
                      s.lead_time_days = row.base_lead_time_days, s.latitude = row.latitude,
                      s.longitude = row.longitude, s.created_at = datetime()
        ON MATCH SET s.name = row.name, s.reliability_profile = row.reliability_profile,
                     s.lead_time_days = row.base_lead_time_days, s.latitude = row.latitude,
                     s.longitude = row.longitude, s.updated_at = datetime();
        """
        if payload.get("suppliers"):
            self.client.execute_batch(sup_cypher, payload["suppliers"])

        prod_cypher = """
        UNWIND $batch AS row
        MERGE (p:Product {id: row.id})
        ON CREATE SET p.name = row.name, p.sku = row.sku, p.created_at = datetime()
        ON MATCH SET p.name = row.name, p.sku = row.sku, p.updated_at = datetime();
        """
        if payload.get("products"):
            self.client.execute_batch(prod_cypher, payload["products"])

        wh_cypher = """
        UNWIND $batch AS row
        MERGE (w:Warehouse {id: row.id})
        ON CREATE SET w.name = row.name, w.capacity_units = row.capacity_units,
                      w.latitude = row.latitude, w.longitude = row.longitude, w.created_at = datetime()
        ON MATCH SET w.name = row.name, w.capacity_units = row.capacity_units,
                     w.latitude = row.latitude, w.longitude = row.longitude, w.updated_at = datetime();
        """
        if payload.get("warehouses"):
            self.client.execute_batch(wh_cypher, payload["warehouses"])

        dc_cypher = """
        UNWIND $batch AS row
        MERGE (d:DistributionCenter {id: row.id})
        ON CREATE SET d.name = row.name, d.latitude = row.latitude, d.longitude = row.longitude, d.created_at = datetime()
        ON MATCH SET d.name = row.name, d.latitude = row.latitude, d.longitude = row.longitude, d.updated_at = datetime();
        """
        if payload.get("distribution_centers"):
            self.client.execute_batch(dc_cypher, payload["distribution_centers"])

        route_cypher = """
        UNWIND $batch AS row
        MERGE (r:Route {id: row.id})
        ON CREATE SET r.mode = row.mode, r.distance_km = row.distance_km,
                      r.standard_transit_days = row.standard_transit_days,
                      r.origin_type = row.origin_type, r.origin_id = row.origin_id,
                      r.destination_type = row.destination_type, r.destination_id = row.destination_id,
                      r.created_at = datetime()
        ON MATCH SET r.mode = row.mode, r.distance_km = row.distance_km,
                     r.standard_transit_days = row.standard_transit_days,
                     r.origin_type = row.origin_type, r.origin_id = row.origin_id,
                     r.destination_type = row.destination_type, r.destination_id = row.destination_id,
                     r.updated_at = datetime();
        """
        if payload.get("routes"):
            self.client.execute_batch(route_cypher, payload["routes"])

    def load_edges(self, payload: Dict[str, List[Dict[str, Any]]]) -> None:
        produces_cypher = """
        UNWIND $batch AS row
        MATCH (m:Manufacturer {id: row.manufacturer_id})
        MATCH (p:Product {id: row.product_id})
        MERGE (m)-[r:PRODUCES]->(p)
        ON CREATE SET r.production_capacity_units = row.production_capacity_units, r.created_at = datetime()
        ON MATCH SET r.production_capacity_units = row.production_capacity_units;
        """
        if payload.get("produces_edges"):
            self.client.execute_batch(produces_cypher, payload["produces_edges"])

        supplies_cypher = """
        UNWIND $batch AS row
        MATCH (s:Supplier {id: row.supplier_id})
        MATCH (p:Product {id: row.product_id})
        MERGE (s)-[r:SUPPLIES]->(p)
        ON CREATE SET r.unit_cost = row.unit_cost, r.lead_time_days = row.lead_time_days,
                      r.minimum_order_qty = row.minimum_order_qty, r.is_preferred = row.is_preferred,
                      r.contract_id = row.contract_id, r.created_at = datetime()
        ON MATCH SET r.unit_cost = row.unit_cost, r.lead_time_days = row.lead_time_days,
                     r.minimum_order_qty = row.minimum_order_qty, r.is_preferred = row.is_preferred,
                     r.contract_id = row.contract_id;
        """
        if payload.get("supplies_edges"):
            self.client.execute_batch(supplies_cypher, payload["supplies_edges"])

        stored_cypher = """
        UNWIND $batch AS row
        MATCH (p:Product {id: row.product_id})
        MATCH (w:Warehouse {id: row.warehouse_id})
        MERGE (p)-[r:STORED_IN]->(w)
        ON CREATE SET r.max_storage_units = row.max_storage_units, r.storage_cost_per_unit = row.storage_cost_per_unit, r.created_at = datetime()
        ON MATCH SET r.max_storage_units = row.max_storage_units, r.storage_cost_per_unit = row.storage_cost_per_unit;
        """
        if payload.get("stored_in_edges"):
            self.client.execute_batch(stored_cypher, payload["stored_in_edges"])

        ships_cypher = """
        UNWIND $batch AS row
        MATCH (r:Route {id: row.route_id})
        WITH row, r
        OPTIONAL MATCH (s:Supplier {id: row.origin_id})
        OPTIONAL MATCH (w:Warehouse {id: row.origin_id})
        OPTIONAL MATCH (m:Manufacturer {id: row.origin_id})
        WITH row, r, coalesce(s, w, m) AS origin
        FOREACH (_ IN CASE WHEN origin IS NOT NULL THEN [1] ELSE [] END |
            MERGE (origin)-[rel:SHIPS_VIA]->(r)
            ON CREATE SET rel.mode = row.mode, rel.transit_days = row.transit_days, rel.cost = row.cost, rel.risk_score = row.risk_score
            ON MATCH SET rel.mode = row.mode, rel.transit_days = row.transit_days, rel.cost = row.cost, rel.risk_score = row.risk_score
        );
        """
        if payload.get("ships_via_edges"):
            self.client.execute_batch(ships_cypher, payload["ships_via_edges"])

        delivers_cypher = """
        UNWIND $batch AS row
        MATCH (r:Route {id: row.route_id})
        WITH row, r
        OPTIONAL MATCH (w:Warehouse {id: row.destination_id})
        OPTIONAL MATCH (d:DistributionCenter {id: row.destination_id})
        OPTIONAL MATCH (m:Manufacturer {id: row.destination_id})
        WITH row, r, coalesce(w, d, m) AS dest
        FOREACH (_ IN CASE WHEN dest IS NOT NULL THEN [1] ELSE [] END |
            MERGE (r)-[rel:DELIVERS_TO]->(dest)
            ON CREATE SET rel.service_level_agreement_days = row.service_level_agreement_days
            ON MATCH SET rel.service_level_agreement_days = row.service_level_agreement_days
        );
        """
        if payload.get("delivers_to_edges"):
            self.client.execute_batch(delivers_cypher, payload["delivers_to_edges"])

        alt_cypher = """
        UNWIND $batch AS row
        MATCH (alt:Supplier {id: row.alt_supplier_id})
        MATCH (primary:Supplier {id: row.primary_supplier_id})
        MERGE (alt)-[r:ALTERNATE_FOR]->(primary)
        ON CREATE SET r.product_id = row.product_id, r.cost_delta_pct = row.cost_delta_pct, r.lead_time_delta_days = row.lead_time_delta_days
        ON MATCH SET r.product_id = row.product_id, r.cost_delta_pct = row.cost_delta_pct, r.lead_time_delta_days = row.lead_time_delta_days;
        """
        if payload.get("alternate_for_edges"):
            self.client.execute_batch(alt_cypher, payload["alternate_for_edges"])

    def load_all(self, payload: Dict[str, List[Dict[str, Any]]]) -> None:
        try:
            logger.info("Loading Neo4j Graph Nodes...")
            self.load_nodes(payload)
            logger.info("Loading Neo4j Graph Edges & Properties...")
            self.load_edges(payload)
            logger.info("Neo4j Graph Ingestion Complete.")
        except Exception as e:
            logger.warning("Neo4j database connection unavailable (%s). Skipped Neo4j write.", e)
