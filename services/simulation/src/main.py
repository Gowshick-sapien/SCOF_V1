"""SCOF Simulation Service CLI Entry Point.

Executes the 8 sequential generator phases:
1. Load Domain Profile
2. Validate Topology Integrity
3. Register Simulation Run & SHA-256 Profile Hash
4. Generate Master Data Entities
5. Generate Transactions & Daily Inventory Snapshots
6. Generate Scenarios & Disruption Events
7. Persist Dataset to PostgreSQL & Export generation_manifest.json
8. Execution Verification & Summary Logging
"""

import json
import logging
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from scof_shared.profile.loader import ProfileLoader
from scof_shared.profile.validators import validate_profile_topology
from src.config import settings
from src.constants import GENERATOR_VERSION, Prefix
from src.db_writer import DBWriter
from src.disruption_generator import DisruptionGenerator
from src.entity_generator import EntityGenerator
from src.order_generator import OrderGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("simulation.main")


def run_pipeline(db_persist: bool = True) -> dict:
    start_time = time.time()
    logger.info("Starting SCOF Simulation Pipeline")

    # Phase 1: Load Domain Profile
    logger.info(f"Phase 1: Loading profile from {settings.profile_path}")
    profile = ProfileLoader.load_profile(settings.profile_path)
    logger.info(f"Loaded profile '{profile.meta.name}' v{profile.meta.version} (Hash: {profile.profile_hash[:8]}...)")

    # Phase 2: Validate Topology Integrity
    logger.info("Phase 2: Validating topology integrity...")
    errors = validate_profile_topology(profile)
    if errors:
        logger.error(f"Topology validation failed with {len(errors)} errors:")
        for err in errors:
            logger.error(f"  - {err}")
        sys.exit(1)
    logger.info("Topology validation passed successfully.")

    # Phase 3: Register Run & Hash
    today_str = date.today().strftime("%Y%m%d")
    run_id = f"{Prefix.RUN}{today_str}-001"
    logger.info(f"Phase 3: Registered simulation run_id={run_id}")

    # Phase 4: Master Entities Generation
    logger.info("Phase 4: Generating master topology entities...")
    entity_gen = EntityGenerator(profile)
    master_entities = entity_gen.generate_all()
    total_entities = sum(len(v) for v in master_entities.values())
    logger.info(f"Generated {total_entities} master topology entities.")

    # Phase 5: Transactions & Inventory Log Generation
    logger.info(f"Phase 5: Generating historical transactions over {settings.history_days} days...")
    start_date = date.today() - timedelta(days=settings.history_days)
    order_gen = OrderGenerator(
        run_id=run_id,
        history_days=settings.history_days,
        suppliers=master_entities["suppliers"],
        products=master_entities["products"],
        supplier_products=master_entities["supplier_products"],
        warehouses=master_entities["warehouses"],
        routes=master_entities["routes"],
        random_seed=settings.random_seed,
    )
    operational_logs = order_gen.generate_all(start_date=start_date)
    logger.info(
        f"Generated {len(operational_logs['purchase_orders'])} POs, "
        f"{len(operational_logs['shipments'])} Shipments, and "
        f"{len(operational_logs['inventory_levels'])} Daily Inventory snapshots."
    )

    # Phase 6: Disruptions & Scenarios Generation
    logger.info("Phase 6: Generating scenarios and disruption events...")
    disrupt_gen = DisruptionGenerator(
        run_id=run_id,
        profile=profile,
        master_entities=master_entities,
        random_seed=settings.random_seed,
    )
    disruption_data = disrupt_gen.generate_all(start_date=start_date, history_days=settings.history_days)
    logger.info(f"Generated {len(disruption_data['scenarios'])} scenarios and {len(disruption_data['disruption_events'])} disruption events.")

    execution_time_ms = int((time.time() - start_time) * 1000)

    run_metadata = {
        "run_id": run_id,
        "random_seed": settings.random_seed,
        "profile_name": profile.meta.profile_id,
        "profile_version": profile.meta.version,
        "profile_hash": profile.profile_hash,
        "history_days": settings.history_days,
        "total_entities_generated": total_entities,
        "total_orders_generated": len(operational_logs["purchase_orders"]),
        "total_shipments_generated": len(operational_logs["shipments"]),
        "total_inventory_rows": len(operational_logs["inventory_levels"]),
        "total_disruptions_generated": len(disruption_data["disruption_events"]),
        "execution_time_ms": execution_time_ms,
        "generator_version": GENERATOR_VERSION,
    }

    # Phase 7: Persist & Export Manifest
    if db_persist:
        logger.info(f"Phase 7: Persisting simulation run data to PostgreSQL at {settings.postgres_host}:{settings.postgres_port}...")
        try:
            db_writer = DBWriter(settings.postgres_dsn)
            db_writer.write_simulation_dataset(
                run_metadata=run_metadata,
                master_entities=master_entities,
                operational_logs=operational_logs,
                disruption_data=disruption_data,
            )
            logger.info("Database persistence completed successfully.")
        except Exception as e:
            logger.warning(f"Database persistence skipped or failed: {e}")

    manifest_path = Path("generation_manifest.json")
    manifest_data = {
        **run_metadata,
        "row_counts": {
            "manufacturers": len(master_entities["manufacturers"]),
            "products": len(master_entities["products"]),
            "suppliers": len(master_entities["suppliers"]),
            "supplier_products": len(master_entities["supplier_products"]),
            "warehouses": len(master_entities["warehouses"]),
            "distribution_centers": len(master_entities["distribution_centers"]),
            "routes": len(master_entities["routes"]),
            "purchase_orders": len(operational_logs["purchase_orders"]),
            "order_items": len(operational_logs["order_items"]),
            "shipments": len(operational_logs["shipments"]),
            "inventory_levels": len(operational_logs["inventory_levels"]),
            "scenarios": len(disruption_data["scenarios"]),
            "disruption_events": len(disruption_data["disruption_events"]),
        },
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    logger.info(f"Exported generation manifest to {manifest_path.resolve()}")

    # Phase 8: Verification Log Summary
    logger.info("Phase 8: Execution complete.")
    logger.info(f"Summary: run_id={run_id}, duration={execution_time_ms}ms, rows={sum(manifest_data['row_counts'].values())}")

    return manifest_data


if __name__ == "__main__":
    run_pipeline()
