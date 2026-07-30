import os
import logging
import time
from typing import Any, Dict, List, Optional
# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase, Driver, Session

logger = logging.getLogger(__name__)

class Neo4jGraphClient:
    """
    Reusable Neo4j Client providing connection pooling, exponential retries,
    and high-level Graph RAG helper methods for specialist agents and services.
    """

    def __init__(self, uri: Optional[str] = None, auth: Optional[tuple] = None, max_retries: int = 5):
        if uri is None:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        if auth is None:
            user = os.getenv("NEO4J_USER", "neo4j")
            pw = os.getenv("NEO4J_PASSWORD", "changeme")
            auth = (user, pw)
        self.uri = uri
        self.auth = auth
        self.max_retries = max_retries
        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        if self._driver is not None:
            return self._driver

        retry_count = 0
        backoff = 1.0
        while retry_count < self.max_retries:
            try:
                driver = GraphDatabase.driver(self.uri, auth=self.auth)
                driver.verify_connectivity()
                self._driver = driver
                logger.info("Successfully connected to Neo4j graph database at %s", self.uri)
                return self._driver
            except Exception as e:
                retry_count += 1
                if retry_count >= self.max_retries:
                    logger.error("Failed to connect to Neo4j after %d retries: %s", self.max_retries, e)
                    raise
                logger.warning("Neo4j connection attempt %d failed: %s. Retrying in %.1fs...", retry_count, e, backoff)
                time.sleep(backoff)
                backoff *= 2.0
        raise RuntimeError("Could not establish Neo4j connection.")

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def execute_read(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        driver = self.connect()
        with driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        driver = self.connect()
        with driver.session() as session:
            result = session.run(cypher, parameters or {})
            records = [record.data() for record in result]
            result.consume()
            return records

    def execute_batch(self, cypher: str, batch: List[Dict[str, Any]]) -> None:
        driver = self.connect()
        with driver.session() as session:
            result = session.run(cypher, {"batch": batch})
            result.consume()

    def get_shortest_path(self, origin_id: str, destination_id: str, max_depth: int = 6) -> List[Dict[str, Any]]:
        cypher = f"""
        MATCH (start {{id: $origin_id}}), (target {{id: $destination_id}})
        MATCH p = shortestPath((start)-[*..{max_depth}]-(target))
        RETURN [node IN nodes(p) | {{id: node.id, labels: labels(node), name: node.name}}] AS path_nodes,
               [rel IN relationships(p) | {{type: type(rel), props: properties(rel)}}] AS path_relationships,
               length(p) AS hop_count
        """
        return self.execute_read(cypher, {"origin_id": origin_id, "destination_id": destination_id})

    def get_upstream_supplier_lineage(self, product_id: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (p:Product {id: $product_id})<-[r:SUPPLIES]-(s:Supplier)
        OPTIONAL MATCH (s)-[:SHIPS_VIA]->(rt:Route)-[:DELIVERS_TO]->(w:Warehouse)
        RETURN s.id AS supplier_id,
               s.name AS supplier_name,
               s.reliability_profile AS reliability_profile,
               r.unit_cost AS unit_cost,
               r.lead_time_days AS lead_time_days,
               r.minimum_order_qty AS minimum_order_qty,
               r.is_preferred AS is_preferred,
               r.contract_id AS contract_id,
               collect(DISTINCT {route_id: rt.id, warehouse_id: w.id, mode: rt.mode}) AS delivery_routes
        """
        return self.execute_read(cypher, {"product_id": product_id})

    def get_alternate_suppliers(self, supplier_id: str, product_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (primary:Supplier {id: $supplier_id})-[:SUPPLIES]->(p:Product)<-[r:SUPPLIES]-(alt:Supplier)
        WHERE alt.id <> primary.id AND ($product_id IS NULL OR p.id = $product_id)
        RETURN alt.id AS alt_supplier_id,
               alt.name AS alt_supplier_name,
               alt.reliability_profile AS reliability_profile,
               p.id AS product_id,
               p.name AS product_name,
               r.unit_cost AS alt_unit_cost,
               r.lead_time_days AS alt_lead_time_days,
               r.is_preferred AS alt_is_preferred
        """
        return self.execute_read(cypher, {"supplier_id": supplier_id, "product_id": product_id})

    def get_route_details(self, route_id: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (r:Route {id: $route_id})
        OPTIONAL MATCH (origin)-[sv:SHIPS_VIA]->(r)-[dt:DELIVERS_TO]->(dest)
        RETURN r.id AS route_id,
               r.mode AS mode,
               r.distance_km AS distance_km,
               r.standard_transit_days AS standard_transit_days,
               r.origin_type AS origin_type,
               r.origin_id AS origin_id,
               r.destination_type AS destination_type,
               r.destination_id AS destination_id,
               sv.cost AS transport_cost,
               sv.risk_score AS risk_score
        """
        return self.execute_read(cypher, {"route_id": route_id})
