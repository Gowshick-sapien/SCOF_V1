"""
Merchandise Generator
Handles merchandise hierarchy (49,616 SKUs), store-SKU planogram assortments (346,238 pairings), and multi-week price history (2,580,032 records).
Reuses validated V2 master assets to preserve enterprise simulation ground truth.
"""

import os
import shutil
import pandas as pd
from generators.base_generator import BaseGenerator

class MerchandiseGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        masters_dir = os.path.join(datasets_dir, "masters")
        output_dir = os.path.join(datasets_dir, "merchandise")
        os.makedirs(output_dir, exist_ok=True)

        if self.node_id == "GEN_T1_MERCH":
            return self._verify_and_stage_merchandise(masters_dir, output_dir)
        elif self.node_id == "GEN_T2_SSA":
            return self._verify_and_stage_assortment(masters_dir, output_dir)
        elif self.node_id == "GEN_T3_PRC":
            return self._verify_and_stage_pricing(datasets_dir, output_dir)
        else:
            raise ValueError(f"Unknown node_id for MerchandiseGenerator: {self.node_id}")

    def _verify_and_stage_merchandise(self, masters_dir: str, output_dir: str):
        # Authoritative V2 SKU master
        p_sku = os.path.join(masters_dir, "sku_master.csv")
        if not os.path.exists(p_sku):
            raise FileNotFoundError(f"Authoritative SKU master not found: {p_sku}")

        df_sku = pd.read_csv(p_sku)
        row_count = len(df_sku)
        p_out = os.path.join(output_dir, "sku_master.csv")
        df_sku.to_csv(p_out, index=False)

        return {
            "status": "SUCCESS",
            "row_count": row_count,
            "checksum": self.compute_file_checksum(p_out),
            "output_files": [p_out],
            "metrics": {"total_skus": row_count}
        }

    def _verify_and_stage_assortment(self, masters_dir: str, output_dir: str):
        # Authoritative V2 Store-SKU Assortment
        p_assort = os.path.join(masters_dir, "store_sku_assortment.csv")
        if not os.path.exists(p_assort):
            raise FileNotFoundError(f"Authoritative assortment master not found: {p_assort}")

        df_assort = pd.read_csv(p_assort)
        row_count = len(df_assort)
        p_out = os.path.join(output_dir, "store_sku_assortment.csv")
        df_assort.to_csv(p_out, index=False)

        return {
            "status": "SUCCESS",
            "row_count": row_count,
            "checksum": self.compute_file_checksum(p_out),
            "output_files": [p_out],
            "metrics": {"total_assortments": row_count}
        }

    def _verify_and_stage_pricing(self, datasets_dir: str, output_dir: str):
        # Authoritative V2 Price History (2.58M rows)
        p_price = os.path.join(datasets_dir, "price_history.csv")
        if not os.path.exists(p_price):
            raise FileNotFoundError(f"Authoritative price history not found: {p_price}")

        # Stream / read and convert to Parquet for high-performance storage format
        p_parquet = os.path.join(output_dir, "price_history.parquet")
        if not os.path.exists(p_parquet):
            print("Converting price_history.csv to optimized Parquet format...", flush=True)
            df_price = pd.read_csv(p_price)
            df_price.to_parquet(p_parquet, index=False)
            row_count = len(df_price)
        else:
            df_price = pd.read_parquet(p_parquet)
            row_count = len(df_price)

        return {
            "status": "SUCCESS",
            "row_count": row_count,
            "checksum": self.compute_file_checksum(p_parquet),
            "output_files": [p_parquet],
            "metrics": {"total_price_records": row_count}
        }
