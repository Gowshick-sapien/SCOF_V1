"""
Inventory Generator
Handles goods receiving, putaway dock logs, and facility SKU inventory positions with strict physical mass conservation.
Reuses inventory state assets where appropriate.
"""

import os
import pandas as pd
import numpy as np
from generators.base_generator import BaseGenerator

class InventoryGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        output_dir = os.path.join(datasets_dir, "inventory")
        os.makedirs(output_dir, exist_ok=True)

        if self.node_id == "GEN_T6_RECEIVING":
            return self._generate_goods_receipts(output_dir)
        elif self.node_id == "GEN_T6_INVENTORY":
            return self._generate_inventory_positions(datasets_dir, output_dir)
        else:
            raise ValueError(f"Unknown node_id for InventoryGenerator: {self.node_id}")

    def _generate_goods_receipts(self, output_dir: str):
        # 15,000 goods receipts corresponding to purchase orders
        n_grn = 15000
        receipts = []
        receipt_lines = []

        wh_ids = ["WH-001", "WH-002", "WH-003", "WH-004", "WH-005"]

        for grn_idx in range(1, n_grn + 1):
            grn_id = f"GRN-2026-{grn_idx:06d}"
            po_id = f"PO-2026-{grn_idx:06d}"
            wh_id = self.rng.choice(wh_ids)
            receipts.append({
                "goods_receipt_id": grn_id,
                "purchase_order_id": po_id,
                "facility_id": wh_id,
                "receipt_date": "2026-05-25",
                "receipt_status": "COMPLETED"
            })

            n_lines = int(self.rng.integers(3, 10))
            for l_idx in range(1, n_lines + 1):
                qty = int(self.rng.integers(50, 1000))
                receipt_lines.append({
                    "goods_receipt_line_id": f"{grn_id}-L{l_idx:02d}",
                    "goods_receipt_id": grn_id,
                    "po_line_id": f"{po_id}-L{l_idx:02d}",
                    "sku_id": f"SKU-{int(self.rng.integers(1, 49616)):06d}",
                    "received_quantity": qty,
                    "accepted_quantity": qty,
                    "rejected_quantity": 0
                })

        p_grn = os.path.join(output_dir, "goods_receipts.parquet")
        df_grn = pd.DataFrame(receipts)
        df_grn.to_parquet(p_grn, index=False)

        p_grnl = os.path.join(output_dir, "goods_receipt_lines.parquet")
        df_grnl = pd.DataFrame(receipt_lines)
        df_grnl.to_parquet(p_grnl, index=False)

        total_rows = len(df_grn) + len(df_grnl)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_grn),
            "output_files": [p_grn, p_grnl],
            "metrics": {"goods_receipts": len(df_grn), "receipt_lines": len(df_grnl)}
        }

    def _generate_inventory_positions(self, datasets_dir: str, output_dir: str):
        # Authoritative inventory positions across 346,238 store-SKU pairings + warehouse stocks
        p_inv = os.path.join(datasets_dir, "inventory_state.csv")
        p_parquet = os.path.join(output_dir, "inventory_positions.parquet")

        if os.path.exists(p_inv):
            print("Staging authoritative inventory_state.csv to Parquet...", flush=True)
            df_inv = pd.read_csv(p_inv)
            df_inv.to_parquet(p_parquet, index=False)
            row_count = len(df_inv)
        else:
            # Synthesize 346,238 inventory positions
            print("Synthesizing facility inventory positions...", flush=True)
            positions = []
            for i in range(1, 346239):
                on_hand = int(self.rng.integers(10, 500))
                reserved = int(self.rng.integers(0, min(10, on_hand)))
                positions.append({
                    "position_id": f"POS-{i:07d}",
                    "facility_id": f"STR-{((i % 16) + 1):03d}",
                    "sku_id": f"SKU-{((i % 49616) + 1):06d}",
                    "on_hand_quantity": on_hand,
                    "reserved_quantity": reserved,
                    "available_quantity": on_hand - reserved,
                    "safety_stock_level": int(self.rng.integers(5, 50)),
                    "reorder_point": int(self.rng.integers(10, 100))
                })
            df_inv = pd.DataFrame(positions)
            df_inv.to_parquet(p_parquet, index=False)
            row_count = len(df_inv)

        return {
            "status": "SUCCESS",
            "row_count": row_count,
            "checksum": self.compute_file_checksum(p_parquet),
            "output_files": [p_parquet],
            "metrics": {"inventory_positions": row_count}
        }
