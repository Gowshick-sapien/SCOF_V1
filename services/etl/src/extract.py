import logging
import math
from pathlib import Path
from typing import Any, Dict, List
import psycopg
from services.etl.src.config import config
from scof_shared.profile.loader import ProfileLoader

logger = logging.getLogger(__name__)

class DataExtractor:
    """
    Extracts raw topology, sourcing links, routes, and disruption events
    from D1 PostgreSQL operational database tables, with automatic fallback to loading
    directly from active Domain Profile YAML files when database connection is offline.
    """

    def __init__(self, db_url: str = config.postgres_connection_string, profile_path: str = config.profile_path):
        self.db_url = db_url
        self.profile_path = Path(profile_path)

    def _get_connection(self) -> psycopg.Connection:
        return psycopg.connect(self.db_url, autocommit=True, connect_timeout=3)

    def extract_from_postgres(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, latitude, longitude FROM scof.manufacturers;")
                mfgs = [{"id": r[0], "name": r[1], "latitude": float(r[2]), "longitude": float(r[3])} for r in cur.fetchall()]

                cur.execute("SELECT id, name, sku, manufacturer_id FROM scof.products;")
                prods = [{"id": r[0], "name": r[1], "sku": r[2], "manufacturer_id": r[3]} for r in cur.fetchall()]

                cur.execute("SELECT id, name, reliability_profile, base_lead_time_days, latitude, longitude FROM scof.suppliers;")
                sups = [{"id": r[0], "name": r[1], "reliability_profile": r[2], "base_lead_time_days": r[3], "latitude": float(r[4]), "longitude": float(r[5])} for r in cur.fetchall()]

                cur.execute("SELECT supplier_id, product_id, is_preferred_supplier, unit_cost, minimum_order_qty, lead_time_override_days FROM scof.supplier_products;")
                s_prods = [{"supplier_id": r[0], "product_id": r[1], "is_preferred": r[2], "unit_cost": float(r[3]), "minimum_order_qty": r[4], "lead_time_override_days": r[5]} for r in cur.fetchall()]

                cur.execute("SELECT id, name, capacity_units, latitude, longitude FROM scof.warehouses;")
                whs = [{"id": r[0], "name": r[1], "capacity_units": r[2], "latitude": float(r[3]), "longitude": float(r[4])} for r in cur.fetchall()]

                cur.execute("SELECT id, name, latitude, longitude FROM scof.distribution_centers;")
                dcs = [{"id": r[0], "name": r[1], "latitude": float(r[2]), "longitude": float(r[3])} for r in cur.fetchall()]

                cur.execute("SELECT id, origin_type, origin_id, destination_type, destination_id, mode, distance_km, standard_transit_days FROM scof.routes;")
                routes = [{"id": r[0], "origin_type": r[1], "origin_id": r[2], "destination_type": r[3], "destination_id": r[4], "mode": r[5], "distance_km": float(r[6]), "standard_transit_days": r[7]} for r in cur.fetchall()]

                cur.execute("SELECT id, run_id, scenario_id, disruption_type, target_entity_type, target_entity_id, severity, start_date, end_date, status FROM scof.disruption_events;")
                disrupts = [{"id": r[0], "run_id": r[1], "scenario_id": r[2], "disruption_type": r[3], "target_entity_type": r[4], "target_entity_id": r[5], "severity": r[6], "start_date": str(r[7]), "end_date": str(r[8]), "status": r[9]} for r in cur.fetchall()]

                return {
                    "manufacturers": mfgs,
                    "products": prods,
                    "suppliers": sups,
                    "supplier_products": s_prods,
                    "warehouses": whs,
                    "distribution_centers": dcs,
                    "routes": routes,
                    "disruptions": disrupts
                }

    def extract_from_profile(self) -> Dict[str, Any]:
        logger.info("Reading topology & disruption models directly from profile path: %s", self.profile_path)
        profile_bundle = ProfileLoader.load_profile(self.profile_path)
        topo = profile_bundle.topology
        disrupts_model = profile_bundle.disruptions

        mfgs = [{
            "id": topo.manufacturer.id,
            "name": topo.manufacturer.name,
            "latitude": topo.manufacturer.location.lat,
            "longitude": topo.manufacturer.location.lon
        }]

        prods = [{
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "manufacturer_id": topo.manufacturer.id
        } for p in topo.products]

        sups = [{
            "id": s.id,
            "name": s.name,
            "reliability_profile": s.reliability_profile,
            "base_lead_time_days": s.lead_time_days,
            "latitude": s.location.lat,
            "longitude": s.location.lon
        } for s in topo.suppliers]

        whs = [{
            "id": w.id,
            "name": w.name,
            "capacity_units": w.capacity_units,
            "latitude": w.location.lat,
            "longitude": w.location.lon
        } for w in topo.warehouses]

        dcs = [{
            "id": d.id,
            "name": d.name,
            "latitude": d.location.lat,
            "longitude": d.location.lon
        } for d in topo.distribution_centers]

        # Sourcing links
        s_prods = []
        for idx_s, s in enumerate(sups):
            for idx_p, p in enumerate(prods):
                s_prods.append({
                    "supplier_id": s["id"],
                    "product_id": p["id"],
                    "is_preferred": (idx_s % len(prods) == idx_p),
                    "unit_cost": 45.0 + (idx_s * 5),
                    "minimum_order_qty": 50,
                    "lead_time_override_days": s["base_lead_time_days"]
                })

        # Routes
        routes = []
        for s in sups:
            for w in whs:
                r_id = f"route-{s['id']}-{w['id']}"
                dist = math.sqrt((s["latitude"] - w["latitude"])**2 + (s["longitude"] - w["longitude"])**2) * 111.0
                routes.append({
                    "id": r_id,
                    "origin_type": "supplier",
                    "origin_id": s["id"],
                    "destination_type": "warehouse",
                    "destination_id": w["id"],
                    "mode": "ocean",
                    "distance_km": round(dist, 2),
                    "standard_transit_days": max(1, int(dist / 200.0))
                })

        for w in whs:
            for d in dcs:
                r_id = f"route-{w['id']}-{d['id']}"
                dist = math.sqrt((w["latitude"] - d["latitude"])**2 + (w["longitude"] - d["longitude"])**2) * 111.0
                routes.append({
                    "id": r_id,
                    "origin_type": "warehouse",
                    "origin_id": w["id"],
                    "destination_type": "distribution_center",
                    "destination_id": d["id"],
                    "mode": "truck",
                    "distance_km": round(dist, 2),
                    "standard_transit_days": max(1, int(dist / 300.0))
                })

        # Disruptions
        disruptions = []
        for idx, de in enumerate(disrupts_model.disruption_types, start=1):
            target_id = sups[0]["id"] if sups else "sup-01"
            severity_val = de.severity_range[-1] if de.severity_range else 3
            disruptions.append({
                "id": f"disrupt-{idx:05d}",
                "run_id": "run-offline-001",
                "scenario_id": "scen-01",
                "disruption_type": de.id.upper(),
                "target_entity_type": de.target_entity,
                "target_entity_id": target_id,
                "severity": severity_val,
                "start_date": "2026-07-01",
                "end_date": "2026-07-15",
                "status": "ACTIVE"
            })

        return {
            "manufacturers": mfgs,
            "products": prods,
            "suppliers": sups,
            "supplier_products": s_prods,
            "warehouses": whs,
            "distribution_centers": dcs,
            "routes": routes,
            "disruptions": disruptions
        }

    def extract_all(self) -> Dict[str, Any]:
        try:
            data = self.extract_from_postgres()
            if data.get("manufacturers"):
                return data
            logger.info("PostgreSQL operational tables empty. Loading topology from profile fallback.")
            return self.extract_from_profile()
        except Exception as e:
            logger.warning("PostgreSQL connection unavailable (%s). Falling back to direct Domain Profile parsing.", e)
            return self.extract_from_profile()
