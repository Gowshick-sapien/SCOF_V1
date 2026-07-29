"""Order and Operational Log Generator for SCOF.

Generates realistic historical Purchase Orders, Order Items, Shipments,
and Daily Inventory Levels keyed to run_id over history_days.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Any
import numpy as np
# pyrefly: ignore [missing-import]
from src.constants import OrderStatus, ShipmentStatus, Prefix


class OrderGenerator:
    """Generates time-series purchase orders, shipments, and inventory histories."""

    def __init__(
        self,
        run_id: str,
        history_days: int,
        suppliers: List[Dict[str, Any]],
        products: List[Dict[str, Any]],
        supplier_products: List[Dict[str, Any]],
        warehouses: List[Dict[str, Any]],
        routes: List[Dict[str, Any]],
        random_seed: int = 42,
    ):
        self.run_id = run_id
        self.history_days = history_days
        self.suppliers = suppliers
        self.products = products
        self.supplier_products = supplier_products
        self.warehouses = warehouses
        self.routes = routes
        self.random_seed = random_seed

        # Fast lookup map for supplier-product unit costs and lead times
        self.sp_map = {
            (sp["supplier_id"], sp["product_id"]): sp for sp in supplier_products
        }

        # Fast lookup for supplier-warehouse routes
        self.sw_routes = {
            (r["origin_id"], r["destination_id"]): r
            for r in routes
            if r["origin_type"] == "supplier" and r["destination_type"] == "warehouse"
        }

    def generate_all(self, start_date: date) -> Dict[str, List[Dict[str, Any]]]:
        """Executes transaction and inventory log generation logic."""
        np.random.seed(self.random_seed)

        purchase_orders: List[Dict[str, Any]] = []
        order_items: List[Dict[str, Any]] = []
        shipments: List[Dict[str, Any]] = []
        inventory_levels: List[Dict[str, Any]] = []

        po_counter = 1
        ship_counter = 1

        # Track stock for inventory level time series
        # Key: (warehouse_id, product_id) -> current stock
        stock_tracker: Dict[tuple, int] = {}
        in_transit_tracker: Dict[tuple, int] = {}

        for wh in self.warehouses:
            for prod in self.products:
                stock_tracker[(wh["id"], prod["id"])] = int(np.random.randint(4000, 8000))
                in_transit_tracker[(wh["id"], prod["id"])] = 0

        # Generate orders day by day
        for day_offset in range(self.history_days):
            current_date = start_date + timedelta(days=day_offset)

            # Daily demand consumption at warehouses
            for wh in self.warehouses:
                for prod in self.products:
                    key = (wh["id"], prod["id"])
                    daily_demand = int(np.random.normal(loc=150, scale=30))
                    daily_demand = max(50, daily_demand)
                    stock_tracker[key] = max(0, stock_tracker[key] - daily_demand)

            # Check if any POs arrive today
            for po in purchase_orders:
                if po["actual_delivery_date"] == current_date:
                    # Stock arrival
                    po["status"] = OrderStatus.DELIVERED
                    # Find items for this PO
                    items = [it for it in order_items if it["order_id"] == po["id"]]
                    for item in items:
                        key = (po["destination_warehouse_id"], item["product_id"])
                        stock_tracker[key] += item["quantity"]

            # Trigger new reorders periodically or when stock < reorder_point
            if day_offset % 4 == 0 or np.random.rand() < 0.2:
                for wh in self.warehouses:
                    for prod in self.products:
                        key = (wh["id"], prod["id"])
                        current_stock = stock_tracker[key]
                        reorder_point = 3500

                        if current_stock <= reorder_point:
                            # Pick primary or alternate supplier
                            sourcing = [
                                sp for sp in self.supplier_products if sp["product_id"] == prod["id"]
                            ]
                            if not sourcing:
                                continue

                            # Preferred supplier 80% of the time
                            pref = next((s for s in sourcing if s["is_preferred_supplier"]), sourcing[0])
                            sup_id = pref["supplier_id"]

                            route = self.sw_routes.get((sup_id, wh["id"]))
                            transit_days = route["standard_transit_days"] if route else 7
                            lead_days = pref["lead_time_override_days"] or 7

                            total_lead = lead_days + transit_days
                            expected_delivery = current_date + timedelta(days=total_lead)

                            # Actual delivery has slight random variance (-1 to +2 days)
                            delay_variance = int(np.random.choice([-1, 0, 0, 1, 2], p=[0.1, 0.5, 0.2, 0.1, 0.1]))
                            actual_delivery = current_date + timedelta(days=max(1, total_lead + delay_variance))

                            po_id = f"{Prefix.PURCHASE_ORDER}{po_counter:05d}"
                            po_counter += 1

                            # Determine status based on current simulation date vs delivery date
                            today = start_date + timedelta(days=self.history_days - 1)
                            if actual_delivery <= current_date:
                                status = OrderStatus.DELIVERED
                            elif actual_delivery <= today:
                                status = OrderStatus.DELIVERED
                            elif delay_variance > 0:
                                status = OrderStatus.DELAYED
                            else:
                                status = OrderStatus.IN_TRANSIT

                            purchase_orders.append({
                                "id": po_id,
                                "run_id": self.run_id,
                                "supplier_id": sup_id,
                                "destination_warehouse_id": wh["id"],
                                "order_date": current_date,
                                "expected_delivery_date": expected_delivery,
                                "actual_delivery_date": actual_delivery,
                                "status": status,
                            })

                            # Order Item
                            order_qty = int(np.random.randint(500, 1500))
                            order_items.append({
                                "order_id": po_id,
                                "product_id": prod["id"],
                                "quantity": order_qty,
                                "unit_cost": float(pref["unit_cost"]),
                            })

                            # Shipment
                            if route:
                                ship_id = f"{Prefix.SHIPMENT}{ship_counter:05d}"
                                ship_counter += 1

                                dep_ts = datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
                                est_ts = datetime.combine(expected_delivery, datetime.min.time(), tzinfo=timezone.utc)
                                act_ts = datetime.combine(actual_delivery, datetime.min.time(), tzinfo=timezone.utc)

                                ship_status = ShipmentStatus.ARRIVED if actual_delivery <= today else ShipmentStatus.IN_TRANSIT
                                if ship_status == ShipmentStatus.ARRIVED and delay_variance > 0:
                                    ship_status = ShipmentStatus.DELAYED

                                shipments.append({
                                    "id": ship_id,
                                    "run_id": self.run_id,
                                    "order_id": po_id,
                                    "route_id": route["id"],
                                    "departure_date": dep_ts,
                                    "estimated_arrival": est_ts,
                                    "actual_arrival": act_ts,
                                    "status": ship_status,
                                })

            # Record daily inventory level snapshot
            for wh in self.warehouses:
                for prod in self.products:
                    key = (wh["id"], prod["id"])
                    inventory_levels.append({
                        "run_id": self.run_id,
                        "warehouse_id": wh["id"],
                        "product_id": prod["id"],
                        "date": current_date,
                        "stock_on_hand": stock_tracker[key],
                        "safety_stock_threshold": 1500,
                        "reorder_point": 3500,
                        "units_in_transit": 500,
                    })

        return {
            "purchase_orders": purchase_orders,
            "order_items": order_items,
            "shipments": shipments,
            "inventory_levels": inventory_levels,
        }
