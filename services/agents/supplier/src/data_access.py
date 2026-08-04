"""Data Access layer for Supplier Intelligence Agent.

Queries PostgreSQL and Neo4j for supplier delivery history, lineage, alternate suppliers, and disruptions.
Computes SHA-256 query hashes for machine-traceable evidence logging.
Provides comprehensive fallback mock data when database connections are unavailable.
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import psycopg
from scof_shared.knowledge.graph_client import Neo4jGraphClient

logger = logging.getLogger(__name__)


class SupplierDataAccess:
    """Encapsulates data fetching operations for the Supplier Intelligence Agent."""

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

    def get_supplier_delivery_history(
        self,
        run_id: Optional[str] = None,
        supplier_ids: Optional[List[str]] = None,
        limit_days: int = 180,
    ) -> Tuple[pd.DataFrame, str]:
        """Fetches historical purchase orders and shipment delivery metrics from PostgreSQL."""
        sql = """
            SELECT 
                po.id AS order_id,
                po.supplier_id,
                po.product_id,
                po.order_date,
                po.expected_delivery_date,
                po.actual_delivery_date,
                po.status,
                po.quantity,
                po.unit_price,
                s.carrier,
                s.shipping_cost,
                CASE 
                    WHEN po.actual_delivery_date IS NOT NULL AND po.expected_delivery_date IS NOT NULL 
                    THEN (po.actual_delivery_date - po.expected_delivery_date)
                    ELSE 0 
                END AS delay_days
            FROM purchase_orders po
            LEFT JOIN shipments s ON po.id = s.order_id
            WHERE 1=1
        """
        params_list: List[Any] = []
        if run_id:
            sql += " AND po.run_id = %s"
            params_list.append(run_id)
        if supplier_ids:
            sql += " AND po.supplier_id = ANY(%s)"
            params_list.append(supplier_ids)

        sql += " ORDER BY po.order_date DESC"
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
                logger.warning("PostgreSQL connection failed, using fallback mock delivery history: %s", e)

        return self._generate_mock_delivery_history(supplier_ids), q_hash

    def get_supplier_disruptions(
        self,
        run_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Fetches active disruption events targeting suppliers."""
        sql = """
            SELECT disruption_type, target_entity_type, target_entity_id, severity, start_day, duration_days
            FROM disruption_events
            WHERE target_entity_type = 'supplier'
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
                logger.warning("PostgreSQL connection failed, using empty/mock disruptions: %s", e)

        return [], q_hash

    def get_supplier_graph_data(
        self,
        supplier_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Queries Neo4j for supplier relationships, product catalog, and delivery paths."""
        query_key = f"get_upstream_supplier_lineage:{product_id or 'all'}:{supplier_id or 'all'}"
        q_hash = self.compute_query_hash(query_key, (supplier_id, product_id))

        client = self._get_graph_client()
        if client is not None:
            try:
                if product_id:
                    lineage = client.get_upstream_supplier_lineage(product_id)
                    if supplier_id:
                        lineage = [item for item in lineage if item.get("supplier_id") == supplier_id]
                    if lineage:
                        self._neo4j_available = True
                        return lineage, q_hash
                else:
                    cypher = """
                    MATCH (s:Supplier)
                    OPTIONAL MATCH (s)-[r:SUPPLIES]->(p:Product)
                    RETURN s.id AS supplier_id,
                           s.name AS supplier_name,
                           s.reliability_profile AS reliability_profile,
                           p.id AS product_id,
                           r.unit_cost AS unit_cost,
                           r.lead_time_days AS lead_time_days,
                           r.is_preferred AS is_preferred
                    """
                    records = client.execute_read(cypher)
                    if records:
                        self._neo4j_available = True
                        return records, q_hash
            except Exception as e:
                self._neo4j_available = False
                logger.warning("Neo4j connection failed, using fallback mock supplier graph: %s", e)

        return self._generate_mock_supplier_graph(supplier_id, product_id), q_hash

    def get_alternate_suppliers(
        self,
        supplier_id: str,
        product_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Queries Neo4j for alternative suppliers supplying the same product."""
        query_key = f"get_alternate_suppliers:{supplier_id}:{product_id or 'all'}"
        q_hash = self.compute_query_hash(query_key, (supplier_id, product_id))

        client = self._get_graph_client()
        if client is not None:
            try:
                alternates = client.get_alternate_suppliers(supplier_id, product_id)
                if alternates:
                    self._neo4j_available = True
                    return alternates, q_hash
            except Exception as e:
                self._neo4j_available = False
                logger.warning("Neo4j connection failed, using fallback mock alternates: %s", e)

        return self._generate_mock_alternate_suppliers(supplier_id, product_id), q_hash

    def get_supplier_hop_count(
        self,
        supplier_id: str,
        warehouse_id: str = "wh-01",
    ) -> Tuple[int, str]:
        """Queries shortest path to compute hop count from supplier to destination warehouse."""
        query_key = f"get_shortest_path:{supplier_id}:{warehouse_id}"
        q_hash = self.compute_query_hash(query_key, (supplier_id, warehouse_id))

        client = self._get_graph_client()
        if client is not None:
            try:
                path_res = client.get_shortest_path(supplier_id, warehouse_id)
                if path_res and len(path_res) > 0:
                    self._neo4j_available = True
                    hop_count = path_res[0].get("hop_count", 2)
                    return int(hop_count), q_hash
            except Exception as e:
                self._neo4j_available = False
                logger.warning("Neo4j shortest path query failed, using mock hop count: %s", e)

        # Realistic mock hop counts based on topology
        mock_hops = {
            "sup-01": 2,
            "sup-02": 3,
            "sup-03": 2,
            "sup-04": 4,
            "sup-05": 3,
        }
        return mock_hops.get(supplier_id, 2), q_hash

    # =========================================================================
    # Fallback Mock Generators
    # =========================================================================

    def _generate_mock_delivery_history(
        self,
        supplier_ids: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Generates realistic synthetic delivery history records."""
        all_suppliers = [
            {"id": "sup-01", "profile": "high", "ontime_prob": 0.95, "base_delay": 0.2},
            {"id": "sup-02", "profile": "medium", "ontime_prob": 0.70, "base_delay": 3.5},
            {"id": "sup-03", "profile": "high", "ontime_prob": 0.92, "base_delay": 0.4},
            {"id": "sup-04", "profile": "low", "ontime_prob": 0.55, "base_delay": 5.2},
            {"id": "sup-05", "profile": "high", "ontime_prob": 0.90, "base_delay": 0.5},
        ]
        if supplier_ids:
            all_suppliers = [s for s in all_suppliers if s["id"] in supplier_ids] or all_suppliers

        records = []
        np.random.seed(42)
        order_idx = 1
        for s in all_suppliers:
            n_orders = 30
            for i in range(n_orders):
                is_ontime = np.random.rand() < s["ontime_prob"]
                delay = 0.0 if is_ontime else float(np.random.exponential(s["base_delay"]) + 1.0)
                status = "DELIVERED" if (is_ontime or np.random.rand() > 0.05) else "CANCELLED"
                records.append({
                    "order_id": f"po-{order_idx:04d}",
                    "supplier_id": s["id"],
                    "product_id": "prod-101" if s["id"] in ["sup-01", "sup-02", "sup-03"] else "prod-102",
                    "order_date": f"2026-01-{(i % 28) + 1:02d}",
                    "expected_delivery_date": f"2026-01-{(i % 28) + 5:02d}",
                    "actual_delivery_date": f"2026-01-{(i % 28) + 5 + int(delay):02d}",
                    "status": status,
                    "quantity": int(np.random.randint(100, 1000)),
                    "unit_price": float(round(np.random.uniform(15.0, 50.0), 2)),
                    "carrier": "FastLogistics",
                    "shipping_cost": float(round(np.random.uniform(200.0, 800.0), 2)),
                    "delay_days": delay,
                })
                order_idx += 1

        return pd.DataFrame(records)

    def _generate_mock_supplier_graph(
        self,
        supplier_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generates realistic mock supplier graph topology records."""
        catalog = [
            {
                "supplier_id": "sup-01",
                "supplier_name": "Semico Components",
                "reliability_profile": "high",
                "product_id": "prod-101",
                "unit_cost": 24.50,
                "lead_time_days": 7,
                "minimum_order_qty": 500,
                "is_preferred": True,
                "contract_id": "cnt-01",
                "delivery_routes": [{"route_id": "rt-01", "warehouse_id": "wh-01", "mode": "sea"}],
            },
            {
                "supplier_id": "sup-02",
                "supplier_name": "MicroBattery Global",
                "reliability_profile": "medium",
                "product_id": "prod-101",
                "unit_cost": 22.00,
                "lead_time_days": 12,
                "minimum_order_qty": 300,
                "is_preferred": False,
                "contract_id": "cnt-02",
                "delivery_routes": [{"route_id": "rt-02", "warehouse_id": "wh-01", "mode": "air"}],
            },
            {
                "supplier_id": "sup-03",
                "supplier_name": "Apex Microdevices",
                "reliability_profile": "high",
                "product_id": "prod-101",
                "unit_cost": 26.00,
                "lead_time_days": 5,
                "minimum_order_qty": 200,
                "is_preferred": False,
                "contract_id": "cnt-03",
                "delivery_routes": [{"route_id": "rt-03", "warehouse_id": "wh-01", "mode": "air"}],
            },
            {
                "supplier_id": "sup-04",
                "supplier_name": "Pacific Sensors",
                "reliability_profile": "low",
                "product_id": "prod-102",
                "unit_cost": 45.00,
                "lead_time_days": 14,
                "minimum_order_qty": 100,
                "is_preferred": True,
                "contract_id": "cnt-04",
                "delivery_routes": [{"route_id": "rt-04", "warehouse_id": "wh-02", "mode": "sea"}],
            },
            {
                "supplier_id": "sup-05",
                "supplier_name": "OptiDisplay Ltd",
                "reliability_profile": "high",
                "product_id": "prod-103",
                "unit_cost": 85.00,
                "lead_time_days": 10,
                "minimum_order_qty": 50,
                "is_preferred": True,
                "contract_id": "cnt-05",
                "delivery_routes": [{"route_id": "rt-05", "warehouse_id": "wh-01", "mode": "land"}],
            },
        ]
        results = catalog
        if supplier_id:
            results = [r for r in results if r["supplier_id"] == supplier_id]
        if product_id:
            results = [r for r in results if r["product_id"] == product_id]
        return results

    def _generate_mock_alternate_suppliers(
        self,
        supplier_id: str,
        product_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generates realistic mock alternate supplier options."""
        # For sup-02 (supplying prod-101): alternates are sup-01 and sup-03
        # For sup-01 (supplying prod-101): alternates are sup-02 and sup-03
        # For sup-05 (supplying prod-103): no alternates (disconnected node case)
        if supplier_id == "sup-05":
            return []

        all_alternates = {
            "sup-02": [
                {
                    "alt_supplier_id": "sup-01",
                    "alt_supplier_name": "Semico Components",
                    "reliability_profile": "high",
                    "product_id": "prod-101",
                    "product_name": "Core Sensor Module",
                    "alt_unit_cost": 24.50,
                    "alt_lead_time_days": 7,
                    "alt_is_preferred": True,
                },
                {
                    "alt_supplier_id": "sup-03",
                    "alt_supplier_name": "Apex Microdevices",
                    "reliability_profile": "high",
                    "product_id": "prod-101",
                    "product_name": "Core Sensor Module",
                    "alt_unit_cost": 26.00,
                    "alt_lead_time_days": 5,
                    "alt_is_preferred": False,
                },
            ],
            "sup-01": [
                {
                    "alt_supplier_id": "sup-03",
                    "alt_supplier_name": "Apex Microdevices",
                    "reliability_profile": "high",
                    "product_id": "prod-101",
                    "product_name": "Core Sensor Module",
                    "alt_unit_cost": 26.00,
                    "alt_lead_time_days": 5,
                    "alt_is_preferred": False,
                },
                {
                    "alt_supplier_id": "sup-02",
                    "alt_supplier_name": "MicroBattery Global",
                    "reliability_profile": "medium",
                    "product_id": "prod-101",
                    "product_name": "Core Sensor Module",
                    "alt_unit_cost": 22.00,
                    "alt_lead_time_days": 12,
                    "alt_is_preferred": False,
                },
            ],
            "sup-03": [
                {
                    "alt_supplier_id": "sup-01",
                    "alt_supplier_name": "Semico Components",
                    "reliability_profile": "high",
                    "product_id": "prod-101",
                    "product_name": "Core Sensor Module",
                    "alt_unit_cost": 24.50,
                    "alt_lead_time_days": 7,
                    "alt_is_preferred": True,
                },
            ],
        }
        res = all_alternates.get(supplier_id, [])
        if product_id:
            res = [r for r in res if r.get("product_id") == product_id]
        return res
