#!/usr/bin/env python3
"""Database Seeder for the 25 Enterprise South Indian Disruption Scenarios.

Generates and populates scof.scenarios and scof.disruption_events in PostgreSQL.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import psycopg2

from scof_shared.profile.loader import ProfileLoader
from services.simulation.src.entity_generator import EntityGenerator
from services.simulation.src.disruption_generator import DisruptionGenerator
from services.simulation.src.config import settings

def seed_scenarios():
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(settings.postgres_dsn)
    cur = conn.cursor()

    # Get latest run_id or default
    cur.execute("SELECT run_id FROM scof.simulation_runs ORDER BY created_at DESC LIMIT 1;")
    row = cur.fetchone()
    run_id = row[0] if row else "run-20261012-001"
    print(f"Using run_id: {run_id}")

    profile = ProfileLoader.load_profile(settings.profile_path)
    entity_gen = EntityGenerator(profile)
    master_entities = entity_gen.generate_all()

    disrupt_gen = DisruptionGenerator(
        run_id=run_id,
        profile=profile,
        master_entities=master_entities,
        random_seed=settings.random_seed,
    )

    start_date = date.today() - timedelta(days=settings.history_days)
    disruption_data = disrupt_gen.generate_all(start_date=start_date, history_days=settings.history_days)

    scenarios = disruption_data["scenarios"]
    disruptions = disruption_data["disruption_events"]

    print(f"Seeding {len(scenarios)} scenarios into scof.scenarios...")
    for sc in scenarios:
        cur.execute(
            """
            INSERT INTO scof.scenarios (scenario_id, run_id, name, description, random_seed)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (scenario_id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                random_seed = EXCLUDED.random_seed,
                run_id = EXCLUDED.run_id;
            """,
            (sc["scenario_id"], sc["run_id"], sc["name"], sc["description"], sc["random_seed"]),
        )

    print(f"Seeding {len(disruptions)} disruption events into scof.disruption_events...")
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
        for d in disruptions
    ]

    cur.executemany(
        """
        INSERT INTO scof.disruption_events (
            id, run_id, scenario_id, disruption_type, target_entity_type,
            target_entity_id, severity, start_date, end_date, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            run_id = EXCLUDED.run_id,
            scenario_id = EXCLUDED.scenario_id,
            disruption_type = EXCLUDED.disruption_type,
            target_entity_type = EXCLUDED.target_entity_type,
            target_entity_id = EXCLUDED.target_entity_id,
            severity = EXCLUDED.severity,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            status = EXCLUDED.status,
            updated_at = CURRENT_TIMESTAMP;
        """,
        disrupt_rows,
    )

    conn.commit()

    # Verification query
    cur.execute("SELECT count(*) FROM scof.scenarios;")
    scen_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM scof.disruption_events WHERE run_id = %s;", (run_id,))
    disrupt_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"Successfully seeded database: {scen_count} scenarios, {disrupt_count} disruption events.")
    return scen_count

if __name__ == "__main__":
    count = seed_scenarios()
    if count != 25:
        sys.exit(1)
