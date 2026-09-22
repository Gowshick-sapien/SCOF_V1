"""
Commerce Generator
Handles omnichannel sales channels, customer sessions, shopping carts, baskets, POS sales transactions, and sales lines.
"""

import os
import pandas as pd
import numpy as np
from generators.base_generator import BaseGenerator

class CommerceGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        output_dir = os.path.join(datasets_dir, "commerce")
        os.makedirs(output_dir, exist_ok=True)

        # 1. Sales Channels
        channels = [
            {"sales_channel_id": "CHAN-POS-STORE", "channel_name": "In-Store Physical POS", "channel_type": "POS"},
            {"sales_channel_id": "CHAN-ECOM-WEB", "channel_name": "Web E-Commerce Storefront", "channel_type": "WEB"},
            {"sales_channel_id": "CHAN-ECOM-APP", "channel_name": "Mobile E-Commerce App", "channel_type": "APP"},
            {"sales_channel_id": "CHAN-B2B-DIRECT", "channel_name": "B2B Direct Institutional Sales", "channel_type": "B2B"}
        ]
        df_chan = pd.DataFrame(channels)
        p_chan = os.path.join(output_dir, "sales_channels.csv")
        df_chan.to_csv(p_chan, index=False)

        # 2. Synthesize Representative Commercial Transactions
        n_tx = 50000
        store_ids = [f"STR-{i:03d}" for i in range(1, 17)]
        transactions = []
        sales_lines = []

        for tx_idx in range(1, n_tx + 1):
            tx_id = f"TX-2026-{tx_idx:07d}"
            st_id = self.rng.choice(store_ids)
            ch_id = self.rng.choice(["CHAN-POS-STORE", "CHAN-ECOM-WEB", "CHAN-ECOM-APP"])
            n_items = int(self.rng.integers(1, 8))

            tx_subtotal = 0.0
            for l_idx in range(1, n_items + 1):
                qty = int(self.rng.integers(1, 5))
                unit_price = float(np.round(self.rng.uniform(15.0, 450.0), 2))
                line_total = np.round(qty * unit_price, 2)
                tx_subtotal += line_total

                sales_lines.append({
                    "sales_line_id": f"{tx_id}-L{l_idx:02d}",
                    "sales_transaction_id": tx_id,
                    "sku_id": f"SKU-{int(self.rng.integers(1, 49616)):06d}",
                    "quantity": qty,
                    "unit_price": unit_price,
                    "line_amount": line_total
                })

            tax_amt = np.round(tx_subtotal * 0.18, 2)
            transactions.append({
                "sales_transaction_id": tx_id,
                "sales_channel_id": ch_id,
                "facility_id": st_id,
                "transaction_date": "2026-06-15",
                "subtotal_amount": np.round(tx_subtotal, 2),
                "tax_amount": tax_amt,
                "total_amount": np.round(tx_subtotal + tax_amt, 2),
                "payment_status": "PAID"
            })

        p_tx = os.path.join(output_dir, "sales_transactions.parquet")
        df_tx = pd.DataFrame(transactions)
        df_tx.to_parquet(p_tx, index=False)

        p_sl = os.path.join(output_dir, "sales_lines.parquet")
        df_sl = pd.DataFrame(sales_lines)
        df_sl.to_parquet(p_sl, index=False)

        total_rows = len(df_chan) + len(df_tx) + len(df_sl)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_tx),
            "output_files": [p_chan, p_tx, p_sl],
            "metrics": {"transactions": len(df_tx), "sales_lines": len(df_sl)}
        }
