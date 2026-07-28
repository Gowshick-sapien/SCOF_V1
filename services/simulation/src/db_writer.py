"""Database Persistence Writer for SCOF Simulation Datasets.

Executes batch-insert transactions into PostgreSQL via psycopg3.
"""

from typing import Dict, List, Any
import psycopg


class DBWriter:
    """Handles batch insertion of simulation run metadata, master entities,"""

    def __init__(self, dsn: str):
        self.dsn = dsn

    def write_simulation_dataset(
        self,
        run_metadata: Dict[str, Any],
        master_entities: Dict[str, List[Dict[str, Any]]],
        operational_logs: Dict[str, List[Dict[str, Any]]],
        disruption_data: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Persists the complete generated simulation dataset within a single database transaction block."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # 1. Insert simulation run metadata
                cur.execute(
                    """
                    INSERT INTO scof.simulation_runs (
                        run_id, random_seed, profile_name, profile_version, profile_hash,
                        history_days, total_entities_generated, total_orders_generated,
                        total_shipments_generated, total_inventory_rows, total_disruptions_generated,
                        execution_time_ms, generator_version
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                        profile_hash = EXCLUDED.profile_hash,
                        total_entities_generated = EXCLUDED.total_entities_generated,
                        total_orders_generated = EXCLUDED.total_orders_generated,
                        total_shipments_generated = EXCLUDED.total_shipments_generated,
                        total_inventory_rows = EXCLUDED.total_inventory_rows,
                        total_disruptions_generated = EXCLUDED.total_disruptions_generated,
                        execution_time_ms = EXCLUDED.execution_time_ms;
                    """,
                    (
                        run_metadata["run_id"],
                        run_metadata["random_seed"],
                        run_metadata["profile_name"],
                        run_metadata["profile_version"],
                        run_metadata["profile_hash"],
                        run_metadata["history_days"],
                        run_metadata["total_entities_generated"],
                        run_metadata["total_orders_generated"],
                        run_metadata["total_shipments_generated"],
                        run_metadata["total_inventory_rows"],
                        run_metadata["total_disruptions_generated"],
                        run_metadata["execution_time_ms"],
                        run_metadata["generator_version"],
                    ),
                )

                # 2. Insert Manufacturers
                for mfg in master_entities["manufacturers"]:
                    cur.execute(
                        """
                        INSERT INTO scof.manufacturers (id, name, latitude, longitude)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude;
                        """,
                        (mfg["id"], mfg["name"], mfg["latitude"], mfg["longitude"]),
                    )

                # 3. Insert Products
                for prod in master_entities["products"]:
                    cur.execute(
                        """
                        INSERT INTO scof.products (id, name, sku, manufacturer_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, sku = EXCLUDED.sku;
                        """,
                        (prod["id"], prod["name"], prod["sku"], prod["manufacturer_id"]),
                    )

                # 4. Insert Suppliers
                for sup in master_entities["suppliers"]:
                    cur.execute(
                        """
                        INSERT INTO scof.suppliers (id, name, reliability_profile, base_lead_time_days, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, reliability_profile = EXCLUDED.reliability_profile;
                        """,
                        (
                            sup["id"],
                            sup["name"],
                            sup["reliability_profile"],
                            sup["base_lead_time_days"],
                            sup["latitude"],
                            sup["longitude"],
                        ),
                    )

                # 5. Insert Supplier Products Junction
                for sp in master_entities["supplier_products"]:
                    cur.execute(
                        """
                        INSERT INTO scof.supplier_products (
                            supplier_id, product_id, is_preferred_supplier, unit_cost,
                            minimum_order_qty, lead_time_override_days
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (supplier_id, product_id) DO UPDATE SET
                            unit_cost = EXCLUDED.unit_cost,
                            is_preferred_supplier = EXCLUDED.is_preferred_supplier;
                        """,
                        (
                            sp["supplier_id"],
                            sp["product_id"],
                            sp["is_preferred_supplier"],
                            sp["unit_cost"],
                            sp["minimum_order_qty"],
                            sp["lead_time_override_days"],
                        ),
                    )

                # 6. Insert Warehouses
                for wh in master_entities["warehouses"]:
                    cur.execute(
                        """
                        INSERT INTO scof.warehouses (id, name, capacity_units, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, capacity_units = EXCLUDED.capacity_units;
                        """,
                        (wh["id"], wh["name"], wh["capacity_units"], wh["latitude"], wh["longitude"]),
                    )

                # 7. Insert Distribution Centers
                for dc in master_entities["distribution_centers"]:
                    cur.execute(
                        """
                        INSERT INTO scof.distribution_centers (id, name, latitude, longitude)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
                        """,
                        (dc["id"], dc["name"], dc["latitude"], dc["longitude"]),
                    )

                # 8. Insert Routes
                for r in master_entities["routes"]:
                    cur.execute(
                        """
                        INSERT INTO scof.routes (
                            id, origin_type, origin_id, destination_type, destination_id,
                            mode, distance_km, standard_transit_days
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            mode = EXCLUDED.mode,
                            distance_km = EXCLUDED.distance_km,
                            standard_transit_days = EXCLUDED.standard_transit_days;
                        """,
                        (
                            r["id"],
                            r["origin_type"],
                            r["origin_id"],
                            r["destination_type"],
                            r["destination_id"],
                            r["mode"],
                            r["distance_km"],
                            r["standard_transit_days"],
                        ),
                    )

                # 9. Insert Scenarios
                for sc in disruption_data["scenarios"]:
                    cur.execute(
                        """
                        INSERT INTO scof.scenarios (scenario_id, run_id, name, description, random_seed)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (scenario_id) DO NOTHING;
                        """,
                        (sc["scenario_id"], sc["run_id"], sc["name"], sc["description"], sc["random_seed"]),
                    )

                # 10. Insert Purchase Orders
                po_rows = [
                    (
                        po["id"],
                        po["run_id"],
                        po["supplier_id"],
                        po["destination_warehouse_id"],
                        po["order_date"],
                        po["expected_delivery_date"],
                        po["actual_delivery_date"],
                        po["status"],
                    )
                    for po in operational_logs["purchase_orders"]
                ]
                cur.executemany(
                    """
                    INSERT INTO scof.purchase_orders (
                        id, run_id, supplier_id, destination_warehouse_id, order_date,
                        expected_delivery_date, actual_delivery_date, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    po_rows,
                )

                # 11. Insert Order Items
                item_rows = [
                    (it["order_id"], it["product_id"], it["quantity"], it["unit_cost"])
                    for it in operational_logs["order_items"]
                ]
                cur.executemany(
                    """
                    INSERT INTO scof.order_items (order_id, product_id, quantity, unit_cost)
                    VALUES (%s, %s, %s, %s);
                    """,
                    item_rows,
                )

                # 12. Insert Shipments
                ship_rows = [
                    (
                        s["id"],
                        s["run_id"],
                        s["order_id"],
                        s["route_id"],
                        s["departure_date"],
                        s["estimated_arrival"],
                        s["actual_arrival"],
                        s["status"],
                    )
                    for s in operational_logs["shipments"]
                ]
                cur.executemany(
                    """
                    INSERT INTO scof.shipments (
                        id, run_id, order_id, route_id, departure_date,
                        estimated_arrival, actual_arrival, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    ship_rows,
                )

                # 13. Insert Inventory Levels
                inv_rows = [
                    (
                        inv["run_id"],
                        inv["warehouse_id"],
                        inv["product_id"],
                        inv["date"],
                        inv["stock_on_hand"],
                        inv["safety_stock_threshold"],
                        inv["reorder_point"],
                        inv["units_in_transit"],
                    )
                    for inv in operational_logs["inventory_levels"]
                ]
                cur.executemany(
                    """
                    INSERT INTO scof.inventory_levels (
                        run_id, warehouse_id, product_id, date, stock_on_hand,
                        safety_stock_threshold, reorder_point, units_in_transit
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id, warehouse_id, product_id, date) DO UPDATE SET
                        stock_on_hand = EXCLUDED.stock_on_hand,
                        units_in_transit = EXCLUDED.units_in_transit;
                    """,
                    inv_rows,
                )

                # 14. Insert Disruption Events
                disrupt_rows = [
                    (
                        d["id"],
                        d["run_id"],
                        d["scenario_id"],
                        d["disruption_type"],
                        d["target_entity_type"],
                        d["target_entity_id"],
                        d["severity"],
                        d["start_date"],
                        d["end_date"],
                        d["status"],
                    )
                    for d in disruption_data["disruption_events"]
                ]
                cur.executemany(
                    """
                    INSERT INTO scof.disruption_events (
                        id, run_id, scenario_id, disruption_type, target_entity_type,
                        target_entity_id, severity, start_date, end_date, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    disrupt_rows,
                )

            conn.commit()
