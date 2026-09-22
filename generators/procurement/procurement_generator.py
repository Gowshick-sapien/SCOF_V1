"""
Procurement Generator
Handles purchase orders and PO lines generated from inventory replenishment triggers.
Reuses existing purchase order patterns.
"""

import os
import pandas as pd
import numpy as np
from generators.base_generator import BaseGenerator

class ProcurementGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        output_dir = os.path.join(datasets_dir, "procurement")
        os.makedirs(output_dir, exist_ok=True)

        n_po = 15000
        po_records = []
        po_lines = []

        wh_ids = ["WH-001", "WH-002", "WH-003", "WH-004", "WH-005"]
        supp_ids = [f"SUP-PR-{i:03d}" for i in range(1, 201)]

        for po_idx in range(1, n_po + 1):
            po_id = f"PO-2026-{po_idx:06d}"
            supp_id = self.rng.choice(supp_ids)
            dest_wh = self.rng.choice(wh_ids)
            n_lines = int(self.rng.integers(3, 10))

            po_total = 0.0
            for l_idx in range(1, n_lines + 1):
                qty = int(self.rng.integers(50, 1000))
                unit_cost = float(np.round(self.rng.uniform(10.0, 250.0), 2))
                l_total = np.round(qty * unit_cost, 2)
                po_total += l_total

                po_lines.append({
                    "po_line_id": f"{po_id}-L{l_idx:02d}",
                    "purchase_order_id": po_id,
                    "sku_id": f"SKU-{int(self.rng.integers(1, 49616)):06d}",
                    "ordered_quantity": qty,
                    "unit_cost": unit_cost,
                    "line_amount": l_total
                })

            po_records.append({
                "purchase_order_id": po_id,
                "supplier_profile_id": supp_id,
                "destination_facility_id": dest_wh,
                "order_date": "2026-05-10",
                "expected_delivery_date": "2026-05-24",
                "total_amount": np.round(po_total, 2),
                "order_status": "APPROVED"
            })

        p_po = os.path.join(output_dir, "purchase_orders.parquet")
        df_po = pd.DataFrame(po_records)
        df_po.to_parquet(p_po, index=False)

        p_pol = os.path.join(output_dir, "po_lines.parquet")
        df_pol = pd.DataFrame(po_lines)
        df_pol.to_parquet(p_pol, index=False)

        total_rows = len(df_po) + len(df_pol)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_po),
            "output_files": [p_po, p_pol],
            "metrics": {"purchase_orders": len(df_po), "po_lines": len(df_pol)}
        }
