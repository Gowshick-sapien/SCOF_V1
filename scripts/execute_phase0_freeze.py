import os
import shutil
import json
import subprocess
import pandas as pd
import numpy as np

def run_phase0():
    base_dir = r"d:\projects\SCOF_V1\SCOF"
    datasets_dir = os.path.join(base_dir, "datasets")
    archive_dir = os.path.join(datasets_dir, "archive")
    src_file = os.path.join(datasets_dir, "weekly_demand_history.csv")
    dst_file = os.path.join(archive_dir, "weekly_demand_history_v1_baseline.csv")
    engine_file = os.path.join(base_dir, "advanced_demand_engine.py")
    engine_archive = os.path.join(archive_dir, "advanced_demand_engine_v1_snapshot.py")

    print("Phase 0: Freezing V1 Baseline...")

    # 1. Snapshot the engine
    if os.path.exists(engine_file):
        shutil.copy2(engine_file, engine_archive)
        print(f"Archived engine snapshot to: {engine_archive}")

    # 2. Get Git commit hash if available
    git_hash = "UNKNOWN"
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=base_dir, capture_output=True, text=True, check=True)
        git_hash = res.stdout.strip()
    except Exception as e:
        print(f"Git commit hash lookup: {e}")

    # 3. Copy baseline file if not already copied
    if not os.path.exists(dst_file):
        print(f"Copying {src_file} to {dst_file}...")
        shutil.copy2(src_file, dst_file)
        print("Copy complete.")
    else:
        print(f"Baseline file already exists at {dst_file}.")

    # 4. Compute baseline metrics in chunks to be memory safe
    print("Computing baseline audit metrics from V1 baseline dataset...")
    chunk_size = 500000
    total_rows = 0
    skus = set()
    stores = set()
    weeks = set()
    
    sum_latent_demand = 0.0
    sum_observed_sales = 0.0
    sum_lost_sales = 0.0
    total_stockouts = 0
    sum_closing_inv = 0.0
    total_zero_sales = 0
    sum_event_factors = 0.0

    # For median calculation, sample or collect
    latent_samples = []

    for chunk in pd.read_csv(dst_file, chunksize=chunk_size):
        total_rows += len(chunk)
        skus.update(chunk["SKU_ID"].unique())
        stores.update(chunk["Store_ID"].unique())
        weeks.update(chunk["Week"].unique())

        sum_latent_demand += chunk["Latent_Demand"].sum()
        sum_observed_sales += chunk["Observed_Sales"].sum()
        sum_lost_sales += chunk["Lost_Sales"].sum()
        total_stockouts += (chunk["Stockout_Flag"] == 1).sum()
        sum_closing_inv += chunk["Closing_Inventory"].sum()
        total_zero_sales += (chunk["Observed_Sales"] == 0).sum()

        combined_event = (chunk["Festival_Factor"] * chunk["Commercial_Factor"] * 
                          chunk["Lifecycle_Factor"] * chunk["Weather_Factor"])
        sum_event_factors += combined_event.sum()

        # sample 1% for median estimation
        sample = chunk["Latent_Demand"].sample(frac=0.01, random_state=42)
        latent_samples.extend(sample.tolist())

    mean_latent = sum_latent_demand / total_rows if total_rows > 0 else 0
    median_latent = float(np.median(latent_samples)) if latent_samples else 0
    mean_sales = sum_observed_sales / total_rows if total_rows > 0 else 0
    stockout_rate = total_stockouts / total_rows if total_rows > 0 else 0
    mean_inventory = sum_closing_inv / total_rows if total_rows > 0 else 0
    zero_sales_rate = total_zero_sales / total_rows if total_rows > 0 else 0
    mean_event_factor = sum_event_factors / total_rows if total_rows > 0 else 0
    inventory_turnover = sum_observed_sales / sum_closing_inv if sum_closing_inv > 0 else 0

    metrics = {
        "git_commit_hash": git_hash,
        "source_file": dst_file,
        "row_count": total_rows,
        "sku_count": len(skus),
        "store_count": len(stores),
        "weeks_covered": len(weeks),
        "mean_latent_demand": round(mean_latent, 4),
        "median_latent_demand": round(median_latent, 4),
        "mean_observed_sales": round(mean_sales, 4),
        "total_lost_sales": int(sum_lost_sales),
        "stockout_rate": round(stockout_rate, 4),
        "mean_inventory": round(mean_inventory, 4),
        "inventory_turnover": round(inventory_turnover, 4),
        "zero_sales_rate": round(zero_sales_rate, 4),
        "mean_event_factor": round(mean_event_factor, 4)
    }

    metrics_file = os.path.join(archive_dir, "v1_baseline_metrics.json")
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print("Baseline Metrics Summary:")
    print(json.dumps(metrics, indent=2))
    print(f"Saved baseline metrics to {metrics_file}")

if __name__ == "__main__":
    run_phase0()
