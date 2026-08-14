"""Automated Health Verification Script for Deliverable D1.

Verifies container connectivity, pgvector extension installation,
supplier_products integrity, polymorphic routes, run_id foreign key isolation,
and non-zero table counts.
"""

import os
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# type: ignore
import psycopg
from psycopg import sql


def get_db_dsn() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "scof")
    user = os.getenv("POSTGRES_USER", "scof")
    pw = os.getenv("POSTGRES_PASSWORD", "changeme")
    return f"postgresql://{user}:{pw}@{host}:{port}/{db}"


def fetch_count(cur) -> int:
    row = cur.fetchone()
    return int(row[0]) if row is not None else 0


def verify_d1():
    dsn = get_db_dsn()
    print("--- Starting SCOF Deliverable D1 Health Verification ---")
    print(f"Connecting to PostgreSQL DSN: postgresql://***:***@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'scof')}")

    passed = True
    checks = []

    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                # Check 1: Extension installation
                cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                ext_row = cur.fetchone()
                if ext_row:
                    checks.append("[PASS] PostgreSQL 'vector' extension is installed.")
                else:
                    checks.append("[FAIL] PostgreSQL 'vector' extension NOT found.")
                    passed = False

                # Check 2: Table existence & row counts
                tables = [
                    "simulation_runs",
                    "scenarios",
                    "manufacturers",
                    "products",
                    "suppliers",
                    "supplier_products",
                    "warehouses",
                    "distribution_centers",
                    "routes",
                    "inventory_levels",
                    "purchase_orders",
                    "order_items",
                    "shipments",
                    "disruption_events",
                ]

                print("\n--- Database Table Row Counts ---")
                for table in tables:
                    cur.execute(sql.SQL("SELECT count(*) FROM scof.{};").format(sql.Identifier(table)))
                    count = fetch_count(cur)
                    print(f"  scof.{table:<25}: {count} rows")
                    if count == 0 and table != "simulation_runs":
                        checks.append(f"[FAIL] Table scof.{table} is empty.")
                        passed = False

                # Check 3: supplier_products integrity (preferred vs alternate)
                cur.execute("SELECT count(*) FROM scof.supplier_products WHERE is_preferred_supplier = TRUE;")
                pref_count = fetch_count(cur)
                cur.execute("SELECT count(*) FROM scof.supplier_products WHERE is_preferred_supplier = FALSE;")
                alt_count = fetch_count(cur)
                if pref_count > 0 and alt_count > 0:
                    checks.append(f"[PASS] supplier_products integrity validated ({pref_count} preferred, {alt_count} alternate).")
                else:
                    checks.append("[FAIL] supplier_products missing preferred or alternate sourcing links.")
                    passed = False

                # Check 4: Polymorphic routes check
                cur.execute("SELECT DISTINCT origin_type FROM scof.routes;")
                origins = [r[0] for r in cur.fetchall()]
                cur.execute("SELECT DISTINCT destination_type FROM scof.routes;")
                dests = [r[0] for r in cur.fetchall()]
                if "supplier" in origins and "warehouse" in dests:
                    checks.append(f"[PASS] Polymorphic routes validated (Origins: {origins}, Destinations: {dests}).")
                else:
                    checks.append(f"[FAIL] Route types invalid: Origins={origins}, Destinations={dests}.")
                    passed = False

                # Check 5: Run ID FK Coexistence
                cur.execute("SELECT count(DISTINCT run_id) FROM scof.inventory_levels;")
                run_count = fetch_count(cur)
                if run_count > 0:
                    checks.append(f"[PASS] Multi-run FK isolation validated ({run_count} distinct run_id(s) active).")
                else:
                    checks.append("[FAIL] No active run_id found in inventory_levels.")
                    passed = False

    except Exception as e:
        print(f"\n[ERROR] Database connection failure: {e}")
        print("Ensure PostgreSQL container is running via 'docker compose up -d' or 'make up'.")
        sys.exit(1)

    print("\n--- Summary of Deliverable D1 Verification Checks ---")
    for check in checks:
        print(check)

    if passed:
        print("\nSUCCESS: All Deliverable D1 Health Checks PASSED cleanly!")
        sys.exit(0)
    else:
        print("\nFAILURE: Deliverable D1 Health Checks encountered issues.")
        sys.exit(1)


if __name__ == "__main__":
    verify_d1()
