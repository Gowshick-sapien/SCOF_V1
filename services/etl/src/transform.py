import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class DataTransformer:
    """
    Transforms extracted relational supply chain data into structured graph payload
    dictionaries (with explicit relationship edge properties) and pgvector decision records.
    """

    def transform_graph_payloads(self, raw_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        manufacturers = raw_data.get("manufacturers", [])
        products = raw_data.get("products", [])
        suppliers = raw_data.get("suppliers", [])
        supplier_products = raw_data.get("supplier_products", [])
        warehouses = raw_data.get("warehouses", [])
        dcs = raw_data.get("distribution_centers", [])
        routes = raw_data.get("routes", [])

        # Relationships
        produces_edges = []
        for p in products:
            if p.get("manufacturer_id"):
                produces_edges.append({
                    "manufacturer_id": p["manufacturer_id"],
                    "product_id": p["id"],
                    "production_capacity_units": 10000
                })

        supplies_edges = []
        for sp in supplier_products:
            lead_time = sp["lead_time_override_days"] if sp.get("lead_time_override_days") is not None else 7
            supplies_edges.append({
                "supplier_id": sp["supplier_id"],
                "product_id": sp["product_id"],
                "unit_cost": sp["unit_cost"],
                "lead_time_days": lead_time,
                "minimum_order_qty": sp.get("minimum_order_qty", 1),
                "is_preferred": sp.get("is_preferred", False),
                "contract_id": f"cnt-{sp['supplier_id']}-{sp['product_id']}"
            })

        stored_in_edges = []
        for p in products:
            for w in warehouses:
                stored_in_edges.append({
                    "product_id": p["id"],
                    "warehouse_id": w["id"],
                    "max_storage_units": 15000,
                    "storage_cost_per_unit": 0.50
                })

        ships_via_edges = []
        delivers_to_edges = []
        for r in routes:
            origin_id = r["origin_id"]
            destination_id = r["destination_id"]
            route_id = r["id"]

            ships_via_edges.append({
                "origin_id": origin_id,
                "route_id": route_id,
                "mode": r["mode"],
                "transit_days": r["standard_transit_days"],
                "cost": r["distance_km"] * 1.25,
                "risk_score": 0.10 if r["mode"] == "truck" else 0.25
            })

            delivers_to_edges.append({
                "route_id": route_id,
                "destination_id": destination_id,
                "service_level_agreement_days": r["standard_transit_days"] + 1
            })

        # Alternate Supplier Relationships
        alternate_for_edges = []
        product_suppliers: Dict[str, List[Dict[str, Any]]] = {}
        for sp in supplies_edges:
            product_suppliers.setdefault(sp["product_id"], []).append(sp)

        for p_id, sups in product_suppliers.items():
            if len(sups) > 1:
                pref = next((s for s in sups if s["is_preferred"]), sups[0])
                for s in sups:
                    if s["supplier_id"] != pref["supplier_id"]:
                        cost_delta = ((s["unit_cost"] - pref["unit_cost"]) / pref["unit_cost"]) * 100.0
                        lead_delta = s["lead_time_days"] - pref["lead_time_days"]
                        alternate_for_edges.append({
                            "alt_supplier_id": s["supplier_id"],
                            "primary_supplier_id": pref["supplier_id"],
                            "product_id": p_id,
                            "cost_delta_pct": round(cost_delta, 2),
                            "lead_time_delta_days": lead_delta
                        })

        return {
            "manufacturers": manufacturers,
            "products": products,
            "suppliers": suppliers,
            "warehouses": warehouses,
            "distribution_centers": dcs,
            "routes": routes,
            "produces_edges": produces_edges,
            "supplies_edges": supplies_edges,
            "stored_in_edges": stored_in_edges,
            "ships_via_edges": ships_via_edges,
            "delivers_to_edges": delivers_to_edges,
            "alternate_for_edges": alternate_for_edges
        }

    def transform_vector_payloads(self, raw_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        disruptions = raw_data.get("disruptions", [])
        decisions = []
        evidence_snippets = []
        embedding_items = []

        for idx, d in enumerate(disruptions, start=1):
            dec_id = f"dec-{idx:05d}"
            ev_id = f"ev-{idx:05d}"
            emb_dec_id = f"emb-dec-{idx:05d}"
            emb_ev_id = f"emb-ev-{idx:05d}"

            target_entity = d.get("target_entity_id", "sup-01")
            disruption_type = d.get("disruption_type", "SUPPLIER_DELAY")
            rec_text = f"Reroute shipments from {target_entity} due to severe {disruption_type.lower()} event."
            impact_text = f"High risk of stockout for downstream warehouses. Severity level {d.get('severity', 3)}."
            snippet_text = f"Historical disruption signal: {disruption_type} recorded on {target_entity} from {d.get('start_date')} to {d.get('end_date')}."

            decisions.append({
                "id": dec_id,
                "scenario_id": d.get("scenario_id"),
                "run_id": d.get("run_id"),
                "disruption_id": d.get("id"),
                "decision_type": "REROUTE" if "delay" in disruption_type.lower() else "SUPPLIER_SWITCH",
                "recommendation": rec_text,
                "confidence": 0.92,
                "priority": "HIGH",
                "impact_summary": impact_text,
                "created_by": "SupplierAgent",
                "simulation_tick": idx * 10,
                "outcome": "APPROVED",
                "status": "ACTIVE"
            })

            evidence_snippets.append({
                "id": ev_id,
                "decision_id": dec_id,
                "source_type": "graph_query",
                "source_id": d.get("id", f"disrupt-{idx:05d}"),
                "snippet_text": snippet_text,
                "metadata_json": {"disruption_type": disruption_type, "severity": d.get("severity", 3)}
            })

            embedding_items.append({
                "id": emb_dec_id,
                "entity_type": "decision",
                "entity_id": dec_id,
                "content_text": f"{rec_text} {impact_text}",
                "metadata_json": {"decision_type": "REROUTE", "target_entity": target_entity}
            })

            embedding_items.append({
                "id": emb_ev_id,
                "entity_type": "evidence",
                "entity_id": ev_id,
                "content_text": snippet_text,
                "metadata_json": {"disruption_type": disruption_type, "source_id": d.get("id")}
            })

        return {
            "decisions": decisions,
            "evidence_snippets": evidence_snippets,
            "embedding_items": embedding_items
        }
