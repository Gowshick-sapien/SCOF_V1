"""
Network Generator
Handles physical network topology, facilities, store-warehouse servicing links, transport lanes, physical assets, and logistics shipments.
"""

import os
import pandas as pd
import numpy as np
from generators.base_generator import BaseGenerator

class NetworkGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        masters_dir = os.path.join(datasets_dir, "masters")
        output_dir = os.path.join(datasets_dir, "network")
        os.makedirs(output_dir, exist_ok=True)

        if self.node_id == "GEN_T1_FAC":
            return self._generate_facilities(masters_dir, output_dir)
        elif self.node_id == "GEN_T2_SWM":
            return self._generate_store_warehouse_map(masters_dir, output_dir)
        elif self.node_id == "GEN_T2_LANE":
            return self._generate_transport_lanes(masters_dir, output_dir)
        elif self.node_id == "GEN_T2_AST":
            return self._generate_physical_assets(masters_dir, output_dir)
        elif self.node_id == "GEN_T5_LOGISTICS":
            return self._generate_logistics_shipments(output_dir)
        else:
            raise ValueError(f"Unknown node_id for NetworkGenerator: {self.node_id}")

    def _generate_facilities(self, masters_dir: str, output_dir: str):
        # Load existing store_master and warehouse_master
        p_store = os.path.join(masters_dir, "store_master.csv")
        p_wh = os.path.join(masters_dir, "warehouse_master.csv")
        
        df_stores = pd.read_csv(p_store) if os.path.exists(p_store) else pd.DataFrame()
        df_wh = pd.read_csv(p_wh) if os.path.exists(p_wh) else pd.DataFrame()

        facilities = []
        for _, r in df_stores.iterrows():
            facilities.append({
                "facility_id": r["STORE_ID"],
                "facility_name": r.get("STORE_NAME", f"Store {r['STORE_ID']}"),
                "facility_category": "STORE",
                "operating_status": "OPERATIONAL"
            })
        for _, r in df_wh.iterrows():
            facilities.append({
                "facility_id": r["WAREHOUSE_ID"],
                "facility_name": r.get("WAREHOUSE_NAME", f"Warehouse {r['WAREHOUSE_ID']}"),
                "facility_category": "WAREHOUSE",
                "operating_status": "OPERATIONAL"
            })

        df_fac = pd.DataFrame(facilities)
        p_fac = os.path.join(output_dir, "facility_master.csv")
        df_fac.to_csv(p_fac, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_fac),
            "checksum": self.compute_file_checksum(p_fac),
            "output_files": [p_fac],
            "metrics": {"stores": len(df_stores), "warehouses": len(df_wh)}
        }

    def _generate_store_warehouse_map(self, masters_dir: str, output_dir: str):
        p_swm = os.path.join(masters_dir, "store_warehouse_map.csv")
        df_swm = pd.read_csv(p_swm) if os.path.exists(p_swm) else pd.DataFrame()
        
        p_out = os.path.join(output_dir, "store_warehouse_map.csv")
        df_swm.to_csv(p_out, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_swm),
            "checksum": self.compute_file_checksum(p_out),
            "output_files": [p_out],
            "metrics": {"servicing_links": len(df_swm)}
        }

    def _generate_transport_lanes(self, masters_dir: str, output_dir: str):
        # 45 inter-facility transport lanes
        lanes = []
        wh_ids = ["WH-001", "WH-002", "WH-003", "WH-004", "WH-005"]
        store_ids = [f"STR-{i:03d}" for i in range(1, 17)]
        
        idx = 1
        for wh in wh_ids:
            for st in store_ids[:7]:
                lanes.append({
                    "lane_id": f"LANE-{idx:03d}",
                    "origin_facility_id": wh,
                    "destination_facility_id": st,
                    "standard_transit_days": int(self.rng.integers(1, 4)),
                    "distance_km": float(np.round(self.rng.uniform(25.0, 350.0), 2)),
                    "is_active": True
                })
                idx += 1
                if idx > 45:
                    break
            if idx > 45:
                break

        df_lanes = pd.DataFrame(lanes)
        p_lane = os.path.join(output_dir, "transport_lanes.csv")
        df_lanes.to_csv(p_lane, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_lanes),
            "checksum": self.compute_file_checksum(p_lane),
            "output_files": [p_lane],
            "metrics": {"total_lanes": len(df_lanes)}
        }

    def _generate_physical_assets(self, masters_dir: str, output_dir: str):
        # 150 physical assets across facilities
        categories = ["REFRIGERATION", "MATERIAL_HANDLING", "POS_TERMINAL", "FLEET_VEHICLE"]
        assets = []
        for i in range(1, 151):
            assets.append({
                "asset_id": f"AST-{i:04d}",
                "asset_name": f"Physical Asset {i:04d}",
                "asset_category": self.rng.choice(categories),
                "facility_id": f"STR-{((i % 16) + 1):03d}" if i <= 120 else f"WH-{((i % 5) + 1):03d}",
                "operating_status": "OPERATIONAL"
            })

        df_assets = pd.DataFrame(assets)
        p_ast = os.path.join(output_dir, "physical_assets.csv")
        df_assets.to_csv(p_ast, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_assets),
            "checksum": self.compute_file_checksum(p_ast),
            "output_files": [p_ast],
            "metrics": {"total_assets": len(df_assets)}
        }

    def _generate_logistics_shipments(self, output_dir: str):
        # 18,000 shipments with 150,000 shipment lines
        n_shipments = 18000
        shipments = []
        shipment_lines = []

        carrier_ids = [f"CARR-{i:03d}" for i in range(1, 26)]
        wh_ids = ["WH-001", "WH-002", "WH-003", "WH-004", "WH-005"]
        store_ids = [f"STR-{i:03d}" for i in range(1, 17)]

        for s_idx in range(1, n_shipments + 1):
            shp_id = f"SHP-2026-{s_idx:06d}"
            orig = self.rng.choice(wh_ids)
            dest = self.rng.choice(store_ids)
            shipments.append({
                "shipment_id": shp_id,
                "origin_facility_id": orig,
                "destination_facility_id": dest,
                "carrier_id": self.rng.choice(carrier_ids),
                "shipment_status": "DELIVERED",
                "shipped_date": "2026-06-15",
                "delivered_date": "2026-06-17"
            })

            # 8 to 10 lines per shipment on average
            n_lines = int(self.rng.integers(7, 11))
            for l_idx in range(1, n_lines + 1):
                shipment_lines.append({
                    "shipment_line_id": f"{shp_id}-L{l_idx:02d}",
                    "shipment_id": shp_id,
                    "sku_id": f"SKU-{int(self.rng.integers(1, 49616)):06d}",
                    "shipped_quantity": int(self.rng.integers(10, 200)),
                    "received_quantity": int(self.rng.integers(10, 200))
                })

        p_shp = os.path.join(output_dir, "shipments.parquet")
        df_shp = pd.DataFrame(shipments)
        df_shp.to_parquet(p_shp, index=False)

        p_lines = os.path.join(output_dir, "shipment_lines.parquet")
        df_lines = pd.DataFrame(shipment_lines)
        df_lines.to_parquet(p_lines, index=False)

        total_rows = len(df_shp) + len(df_lines)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_shp),
            "output_files": [p_shp, p_lines],
            "metrics": {"shipments": len(df_shp), "shipment_lines": len(df_lines)}
        }
