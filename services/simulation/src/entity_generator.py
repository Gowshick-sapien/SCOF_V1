"""Entity Generator for SCOF Master Data.

Parses topology from DomainProfile and instantiates Manufacturers, Products,
Suppliers, Supplier-Product sourcing links, Warehouses, Distribution Centers,
and Polymorphic Routes using canonical ID conventions.
"""

import math
from typing import Dict, List, Any
from scof_shared.profile.loader import DomainProfile
from src.constants import TransportMode, Prefix


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic coordinates in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


class EntityGenerator:
    """Generates canonical master data entities from a DomainProfile."""

    def __init__(self, profile: DomainProfile):
        self.profile = profile
        self.topology = profile.topology

    def generate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generates all master topology entities."""
        manufacturers = self.generate_manufacturers()
        products = self.generate_products(manufacturers[0]["id"])
        suppliers = self.generate_suppliers()
        supplier_products = self.generate_supplier_products(suppliers, products)
        warehouses = self.generate_warehouses()
        dcs = self.generate_distribution_centers()
        routes = self.generate_routes(suppliers, warehouses, dcs, manufacturers)

        return {
            "manufacturers": manufacturers,
            "products": products,
            "suppliers": suppliers,
            "supplier_products": supplier_products,
            "warehouses": warehouses,
            "distribution_centers": dcs,
            "routes": routes,
        }

    def generate_manufacturers(self) -> List[Dict[str, Any]]:
        mfg = self.topology.manufacturer
        return [{
            "id": mfg.id,
            "name": mfg.name,
            "latitude": mfg.location.lat,
            "longitude": mfg.location.lon,
        }]

    def generate_products(self, manufacturer_id: str) -> List[Dict[str, Any]]:
        results = []
        for p in self.topology.products:
            results.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "manufacturer_id": manufacturer_id,
            })
        return results

    def generate_suppliers(self) -> List[Dict[str, Any]]:
        results = []
        for s in self.topology.suppliers:
            results.append({
                "id": s.id,
                "name": s.name,
                "reliability_profile": s.reliability_profile,
                "base_lead_time_days": s.lead_time_days,
                "latitude": s.location.lat,
                "longitude": s.location.lon,
            })
        return results

    def generate_supplier_products(
        self, suppliers: List[Dict[str, Any]], products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Maps suppliers to products establishing preferred and alternate sourcing links."""
        results = []
        base_costs = {
            "prod-101": 45.00,
            "prod-102": 85.00,
            "prod-103": 120.00,
        }

        # Multi-sourcing map
        for i, prod in enumerate(products):
            prod_id = prod["id"]
            cost = base_costs.get(prod_id, 50.00 + (i * 25.00))

            # Preferred supplier
            pref_sup = suppliers[i % len(suppliers)]
            results.append({
                "supplier_id": pref_sup["id"],
                "product_id": prod_id,
                "is_preferred_supplier": True,
                "unit_cost": cost,
                "minimum_order_qty": 100,
                "lead_time_override_days": pref_sup["base_lead_time_days"],
            })

            # Alternate supplier
            alt_sup = suppliers[(i + 1) % len(suppliers)]
            results.append({
                "supplier_id": alt_sup["id"],
                "product_id": prod_id,
                "is_preferred_supplier": False,
                "unit_cost": round(cost * 1.12, 2),  # 12% premium for alternate
                "minimum_order_qty": 50,
                "lead_time_override_days": alt_sup["base_lead_time_days"] + 2,
            })

        return results

    def generate_warehouses(self) -> List[Dict[str, Any]]:
        results = []
        for w in self.topology.warehouses:
            results.append({
                "id": w.id,
                "name": w.name,
                "capacity_units": w.capacity_units,
                "latitude": w.location.lat,
                "longitude": w.location.lon,
            })
        return results

    def generate_distribution_centers(self) -> List[Dict[str, Any]]:
        results = []
        for dc in self.topology.distribution_centers:
            results.append({
                "id": dc.id,
                "name": dc.name,
                "latitude": dc.location.lat,
                "longitude": dc.location.lon,
            })
        return results

    def generate_routes(
        self,
        suppliers: List[Dict[str, Any]],
        warehouses: List[Dict[str, Any]],
        dcs: List[Dict[str, Any]],
        manufacturers: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generates polymorphic routes between suppliers, warehouses, DCs, and manufacturer."""
        routes = []

        # 1. Supplier -> Warehouse routes
        for sup in suppliers:
            for wh in warehouses:
                dist = calculate_haversine_distance(
                    sup["latitude"], sup["longitude"], wh["latitude"], wh["longitude"]
                )
                mode = TransportMode.SEA if dist > 800 else TransportMode.ROAD
                transit = max(2, int(dist / 400.0) + (5 if mode == TransportMode.SEA else 1))

                route_id = f"route-{sup['id']}-{wh['id']}"
                routes.append({
                    "id": route_id,
                    "origin_type": "supplier",
                    "origin_id": sup["id"],
                    "destination_type": "warehouse",
                    "destination_id": wh["id"],
                    "mode": mode,
                    "distance_km": dist,
                    "standard_transit_days": transit,
                })

        # 2. Warehouse -> DC routes
        for wh in warehouses:
            for dc in dcs:
                dist = calculate_haversine_distance(
                    wh["latitude"], wh["longitude"], dc["latitude"], dc["longitude"]
                )
                mode = TransportMode.SEA if dist > 600 else TransportMode.ROAD
                transit = max(1, int(dist / 450.0) + (3 if mode == TransportMode.SEA else 1))

                route_id = f"route-{wh['id']}-{dc['id']}"
                routes.append({
                    "id": route_id,
                    "origin_type": "warehouse",
                    "origin_id": wh["id"],
                    "destination_type": "distribution_center",
                    "destination_id": dc["id"],
                    "mode": mode,
                    "distance_km": dist,
                    "standard_transit_days": transit,
                })

        # 3. Warehouse -> Manufacturer routes
        mfg = manufacturers[0]
        for wh in warehouses:
            dist = calculate_haversine_distance(
                wh["latitude"], wh["longitude"], mfg["latitude"], mfg["longitude"]
            )
            transit = max(1, int(dist / 500.0) + 1)
            route_id = f"route-{wh['id']}-{mfg['id']}"
            routes.append({
                "id": route_id,
                "origin_type": "warehouse",
                "origin_id": wh["id"],
                "destination_type": "manufacturer",
                "destination_id": mfg["id"],
                "mode": TransportMode.ROAD,
                "distance_km": dist,
                "standard_transit_days": transit,
            })

        return routes
