"""Data access layer for Transportation Agent.

Interacts with PostgreSQL for shipment execution history and Neo4j for route topology,
with seamless fallback mock generators for testing and offline scenarios.
"""

import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import psycopg
from scof_shared.knowledge.graph_client import Neo4jGraphClient

logger = logging.getLogger(__name__)


class TransportDataAccess:
    """Encapsulates data fetching operations for the Transportation Agent."""

    def __init__(
        self,
        db_config: Optional[Dict[str, Any]] = None,
        graph_client: Optional[Neo4jGraphClient] = None,
    ):
        self.db_config = db_config or {}
        self.graph_client = graph_client
        self._postgres_available: Optional[bool] = None
        self._neo4j_available: Optional[bool] = None

    def _get_graph_client(self) -> Optional[Neo4jGraphClient]:
        if self._neo4j_available is False:
            return None
        if self.graph_client is None:
            try:
                self.graph_client = Neo4jGraphClient(max_retries=1)
            except Exception:
                self._neo4j_available = False
                return None
        return self.graph_client

    def _get_connection_string(self) -> str:
        host = self.db_config.get("host", "localhost")
        port = self.db_config.get("port", 5432)
        dbname = self.db_config.get("dbname", "scof_db")
        user = self.db_config.get("user", "postgres")
        password = self.db_config.get("password", "postgres")
        return f"host={host} port={port} dbname={dbname} user={user} password={password} connect_timeout=1"

    def compute_query_hash(self, query_str: str, params: Any) -> str:
        """Computes deterministic SHA-256 query hash."""
        raw = f"{query_str}|{params}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_shipment_delivery_history(
        self,
        run_id: Optional[str] = None,
        carrier_ids: Optional[List[str]] = None,
        route_ids: Optional[List[str]] = None,
        limit_days: int = 180,
    ) -> Tuple[pd.DataFrame, str]:
        """Fetches historical shipment deliveries and carrier transit delays from PostgreSQL."""
        sql = """
            SELECT 
                s.id AS shipment_id,
                s.order_id,
                s.route_id,
                s.carrier AS carrier_id,
                s.shipping_cost,
                s.departure_date,
                s.estimated_arrival_date,
                s.actual_arrival_date,
                s.status,
                CASE 
                    WHEN s.actual_arrival_date IS NOT NULL AND s.estimated_arrival_date IS NOT NULL 
                    THEN (s.actual_arrival_date - s.estimated_arrival_date)
                    ELSE 0 
                END AS delay_days
            FROM shipments s
            WHERE 1=1
        """
        params_list: List[Any] = []
        if run_id:
            sql += " AND s.run_id = %s"
            params_list.append(run_id)
        if carrier_ids:
            sql += " AND s.carrier = ANY(%s)"
            params_list.append(carrier_ids)
        if route_ids:
            sql += " AND s.route_id = ANY(%s)"
            params_list.append(route_ids)

        sql += " ORDER BY s.departure_date DESC"
        params = tuple(params_list)
        q_hash = self.compute_query_hash(sql, params)

        if self._postgres_available is not False:
            try:
                conn_str = self._get_connection_string()
                with psycopg.connect(conn_str) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, params)
                        cols = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        if rows:
                            self._postgres_available = True
                            df = pd.DataFrame(rows, columns=cols)
                            return df, q_hash
            except Exception as e:
                self._postgres_available = False
                logger.warning("PostgreSQL connection failed, using fallback mock shipment history: %s", e)

        return self._generate_mock_shipment_history(carrier_ids, route_ids), q_hash

    def get_transport_disruptions(
        self,
        run_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Fetches active disruption events targeting transport lanes, ports, or carriers."""
        sql = """
            SELECT disruption_type, target_entity_type, target_entity_id, severity, start_day, duration_days
            FROM disruption_events
            WHERE target_entity_type IN ('transport', 'route', 'carrier', 'port')
        """
        params_list: List[Any] = []
        if run_id:
            sql += " AND run_id = %s"
            params_list.append(run_id)
        if scenario_id:
            sql += " AND scenario_id = %s"
            params_list.append(scenario_id)

        params = tuple(params_list)
        q_hash = self.compute_query_hash(sql, params)

        if self._postgres_available is not False:
            try:
                conn_str = self._get_connection_string()
                with psycopg.connect(conn_str) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, params)
                        cols = [desc[0] for desc in cur.description]
                        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
                        self._postgres_available = True
                        return rows, q_hash
            except Exception as e:
                self._postgres_available = False
                logger.warning("PostgreSQL connection failed, using empty/mock transport disruptions: %s", e)

        return [], q_hash

    def get_route_graph_data(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Queries Neo4j for transport routes between origin and destination."""
        query_key = f"get_route_details:{origin or 'all'}:{destination or 'all'}"
        q_hash = self.compute_query_hash(query_key, (origin, destination))

        client = self._get_graph_client()
        if client is not None:
            try:
                if origin and destination:
                    routes = client.get_route_details(origin, destination)
                    if routes:
                        self._neo4j_available = True
                        return routes, q_hash
                else:
                    cypher = """
                    MATCH (o)-[r:CONNECTED_TO|SHIPPED_VIA]->(d)
                    RETURN coalesce(r.id, 'route-' + id(r)) AS route_id,
                           coalesce(r.mode, 'road') AS mode,
                           coalesce(r.carrier, 'Standard Carrier') AS carrier,
                           coalesce(r.transit_time_days, 5.0) AS transit_time_days,
                           coalesce(r.cost, 1000.0) AS cost,
                           coalesce(r.reliability_rating, 0.90) AS reliability_rating,
                           o.id AS origin_id,
                           d.id AS destination_id
                    """
                    records = client.execute_read(cypher)
                    if records:
                        self._neo4j_available = True
                        return records, q_hash
            except Exception as e:
                self._neo4j_available = False
                logger.warning("Neo4j connection failed, using fallback mock route graph: %s", e)

        return self._generate_mock_route_graph(origin, destination), q_hash

    def get_alternate_routes(
        self,
        disrupted_route_id: str,
        destination: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Queries Neo4j for alternative routes/modes bypassing a disrupted route."""
        query_key = f"get_alternate_routes:{disrupted_route_id}:{destination or 'wh-01'}"
        q_hash = self.compute_query_hash(query_key, (disrupted_route_id, destination))

        client = self._get_graph_client()
        if client is not None:
            try:
                cypher = """
                MATCH (r1:TransportRoute {id: $disrupted_route_id})
                MATCH (r2:TransportRoute)
                WHERE r2.id <> $disrupted_route_id 
                  AND (r2.destination = r1.destination OR r2.destination = $destination)
                RETURN r2.id AS alt_route_id,
                       r2.mode AS alt_mode,
                       r2.carrier AS alt_carrier,
                       r2.transit_time_days AS alt_transit_time_days,
                       r2.cost AS alt_cost,
                       r2.reliability_rating AS alt_reliability_rating
                ORDER BY r2.reliability_rating DESC
                """
                records = client.execute_read(cypher, {"disrupted_route_id": disrupted_route_id, "destination": destination or "wh-01"})
                if records:
                    self._neo4j_available = True
                    return records, q_hash
            except Exception as e:
                self._neo4j_available = False
                logger.warning("Neo4j route query failed, using fallback mock alternate routes: %s", e)

        return self._generate_mock_alternate_routes(disrupted_route_id, destination), q_hash

    # =========================================================================
    # Fallback Mock Generators
    # =========================================================================

    def _generate_mock_shipment_history(
        self,
        carrier_ids: Optional[List[str]] = None,
        route_ids: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Generates realistic synthetic shipment delivery history records."""
        carriers = carrier_ids or ["PacificFreight", "ApexLogistics", "SwiftTransit", "GlobalAirCargo"]
        routes = route_ids or ["route-sea-01", "route-air-02", "route-rail-03", "route-road-04"]

        records = [
            # PacificFreight (Sea corridor, nominal small delays)
            {"shipment_id": "shp-101", "order_id": "po-101", "route_id": "route-sea-01", "carrier_id": "PacificFreight", "shipping_cost": 1200.0, "departure_date": "2026-06-01", "estimated_arrival_date": "2026-06-15", "actual_arrival_date": "2026-06-15", "status": "DELIVERED", "delay_days": 0.0},
            {"shipment_id": "shp-102", "order_id": "po-102", "route_id": "route-sea-01", "carrier_id": "PacificFreight", "shipping_cost": 1250.0, "departure_date": "2026-06-10", "estimated_arrival_date": "2026-06-24", "actual_arrival_date": "2026-06-25", "status": "DELIVERED", "delay_days": 1.0},
            {"shipment_id": "shp-103", "order_id": "po-103", "route_id": "route-sea-01", "carrier_id": "PacificFreight", "shipping_cost": 1180.0, "departure_date": "2026-06-20", "estimated_arrival_date": "2026-07-04", "actual_arrival_date": "2026-07-04", "status": "DELIVERED", "delay_days": 0.0},
            {"shipment_id": "shp-104", "order_id": "po-104", "route_id": "route-sea-01", "carrier_id": "PacificFreight", "shipping_cost": 1300.0, "departure_date": "2026-07-01", "estimated_arrival_date": "2026-07-15", "actual_arrival_date": "2026-07-20", "status": "DELIVERED", "delay_days": 5.0},

            # ApexLogistics (Road/Rail corridor, fast and reliable)
            {"shipment_id": "shp-201", "order_id": "po-201", "route_id": "route-road-04", "carrier_id": "ApexLogistics", "shipping_cost": 850.0, "departure_date": "2026-06-05", "estimated_arrival_date": "2026-06-08", "actual_arrival_date": "2026-06-08", "status": "DELIVERED", "delay_days": 0.0},
            {"shipment_id": "shp-202", "order_id": "po-202", "route_id": "route-road-04", "carrier_id": "ApexLogistics", "shipping_cost": 860.0, "departure_date": "2026-06-18", "estimated_arrival_date": "2026-06-21", "actual_arrival_date": "2026-06-21", "status": "DELIVERED", "delay_days": 0.0},
            {"shipment_id": "shp-203", "order_id": "po-203", "route_id": "route-rail-03", "carrier_id": "ApexLogistics", "shipping_cost": 920.0, "departure_date": "2026-07-02", "estimated_arrival_date": "2026-07-06", "actual_arrival_date": "2026-07-06", "status": "DELIVERED", "delay_days": 0.0},

            # GlobalAirCargo (Air expedite, high cost, zero delay)
            {"shipment_id": "shp-301", "order_id": "po-301", "route_id": "route-air-02", "carrier_id": "GlobalAirCargo", "shipping_cost": 3200.0, "departure_date": "2026-06-12", "estimated_arrival_date": "2026-06-14", "actual_arrival_date": "2026-06-14", "status": "DELIVERED", "delay_days": 0.0},
            {"shipment_id": "shp-302", "order_id": "po-302", "route_id": "route-air-02", "carrier_id": "GlobalAirCargo", "shipping_cost": 3150.0, "departure_date": "2026-07-05", "estimated_arrival_date": "2026-07-07", "actual_arrival_date": "2026-07-07", "status": "DELIVERED", "delay_days": 0.0},

            # SwiftTransit (Moderate delay history)
            {"shipment_id": "shp-401", "order_id": "po-401", "route_id": "route-road-05", "carrier_id": "SwiftTransit", "shipping_cost": 750.0, "departure_date": "2026-06-08", "estimated_arrival_date": "2026-06-12", "actual_arrival_date": "2026-06-14", "status": "DELIVERED", "delay_days": 2.0},
            {"shipment_id": "shp-402", "order_id": "po-402", "route_id": "route-road-05", "carrier_id": "SwiftTransit", "shipping_cost": 760.0, "departure_date": "2026-06-25", "estimated_arrival_date": "2026-06-29", "actual_arrival_date": "2026-07-02", "status": "DELIVERED", "delay_days": 3.0},
        ]

        df = pd.DataFrame(records)
        if carrier_ids:
            df = df[df["carrier_id"].isin(carrier_ids)]
        if route_ids:
            df = df[df["route_id"].isin(route_ids)]
        return df if not df.empty else pd.DataFrame(records)

    def _generate_mock_route_graph(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generates realistic mock route details."""
        routes = [
            {
                "route_id": "route-sea-01",
                "origin_id": "sup-01",
                "destination_id": "wh-01",
                "mode": "ocean",
                "carrier": "PacificFreight",
                "transit_time_days": 14.0,
                "cost": 1200.0,
                "reliability_rating": 0.88,
                "hop_count": 2,
            },
            {
                "route_id": "route-air-02",
                "origin_id": "sup-01",
                "destination_id": "wh-01",
                "mode": "air",
                "carrier": "GlobalAirCargo",
                "transit_time_days": 2.0,
                "cost": 3200.0,
                "reliability_rating": 0.98,
                "hop_count": 1,
            },
            {
                "route_id": "route-rail-03",
                "origin_id": "sup-02",
                "destination_id": "wh-01",
                "mode": "rail",
                "carrier": "ApexLogistics",
                "transit_time_days": 5.0,
                "cost": 920.0,
                "reliability_rating": 0.94,
                "hop_count": 2,
            },
            {
                "route_id": "route-road-04",
                "origin_id": "sup-03",
                "destination_id": "wh-01",
                "mode": "road",
                "carrier": "ApexLogistics",
                "transit_time_days": 3.0,
                "cost": 850.0,
                "reliability_rating": 0.95,
                "hop_count": 1,
            },
            {
                "route_id": "route-sea-05",
                "origin_id": "port-la",
                "destination_id": "wh-01",
                "mode": "ocean",
                "carrier": "SwiftTransit",
                "transit_time_days": 16.0,
                "cost": 1100.0,
                "reliability_rating": 0.78,
                "hop_count": 3,
            },
        ]
        if origin and destination:
            matched = [r for r in routes if r["origin_id"] == origin and r["destination_id"] == destination]
            if matched:
                return matched
        return routes

    def _generate_mock_alternate_routes(
        self,
        disrupted_route_id: str,
        destination: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generates realistic mock alternate routes."""
        all_alts = {
            "route-sea-01": [
                {
                    "alt_route_id": "route-air-02",
                    "alt_mode": "air",
                    "alt_carrier": "GlobalAirCargo",
                    "alt_transit_time_days": 2.0,
                    "alt_cost": 3200.0,
                    "alt_reliability_rating": 0.98,
                    "hop_count": 1,
                },
                {
                    "alt_route_id": "route-rail-03",
                    "alt_mode": "rail",
                    "alt_carrier": "ApexLogistics",
                    "alt_transit_time_days": 5.0,
                    "alt_cost": 920.0,
                    "alt_reliability_rating": 0.94,
                    "hop_count": 2,
                },
            ],
            "route-sea-05": [
                {
                    "alt_route_id": "route-road-04",
                    "alt_mode": "road",
                    "alt_carrier": "ApexLogistics",
                    "alt_transit_time_days": 3.0,
                    "alt_cost": 850.0,
                    "alt_reliability_rating": 0.95,
                    "hop_count": 1,
                },
                {
                    "alt_route_id": "route-air-02",
                    "alt_mode": "air",
                    "alt_carrier": "GlobalAirCargo",
                    "alt_transit_time_days": 2.0,
                    "alt_cost": 3200.0,
                    "alt_reliability_rating": 0.98,
                    "hop_count": 1,
                },
            ],
            "route-road-04": [
                {
                    "alt_route_id": "route-rail-03",
                    "alt_mode": "rail",
                    "alt_carrier": "ApexLogistics",
                    "alt_transit_time_days": 5.0,
                    "alt_cost": 920.0,
                    "alt_reliability_rating": 0.94,
                    "hop_count": 2,
                },
            ],
        }
        return all_alts.get(disrupted_route_id, [
            {
                "alt_route_id": "route-air-02",
                "alt_mode": "air",
                "alt_carrier": "GlobalAirCargo",
                "alt_transit_time_days": 2.0,
                "alt_cost": 3200.0,
                "alt_reliability_rating": 0.98,
                "hop_count": 1,
            }
        ])
