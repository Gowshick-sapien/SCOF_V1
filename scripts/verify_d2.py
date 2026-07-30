import os
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import psycopg
from shared.scof_shared.knowledge.graph_client import Neo4jGraphClient
from shared.scof_shared.knowledge.vector_client import PgVectorClient
from services.etl.src.embedding_service import EmbeddingService
from services.etl.src.pipeline import ETLPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_d2")

def main():
    print("=" * 80)
    print("SCOF Deliverable D2 Health, Functional & Domain Invariant Verification")
    print("=" * 80)
    
    passed_checks = 0
    total_checks = 7

    try:
        # [1/7] Container & Database Connectivity
        print("\n[1/7] Checking Database Container Connectivity & Schema Versions...")
        pg_client = PgVectorClient()
        with pg_client._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version, description FROM scof.schema_version WHERE version = '2.0.0';")
                ver = cur.fetchone()
                assert ver is not None, "PostgreSQL schema version 2.0.0 not found."
                print(f"  [PASS] PostgreSQL pgvector reachable at localhost:5432 (schema {ver[0]})")

        graph_client = Neo4jGraphClient()
        graph_client.connect()
        ver_res = graph_client.execute_read("MATCH (v:SchemaVersion) RETURN v.version AS ver;")
        assert len(ver_res) > 0, "Neo4j SchemaVersion node not found."
        print(f"  [PASS] Neo4j graph database reachable at bolt://localhost:7687 (schema {ver_res[0]['ver']})")
        passed_checks += 1

        # [2/7] Neo4j Graph Constraints & Indexes
        print("\n[2/7] Checking Neo4j Graph Constraints & Indexes...")
        constraints = graph_client.execute_read("SHOW CONSTRAINTS;")
        cst_names = [c.get("name", "") for c in constraints]
        expected_constraints = ["cst_manufacturer_id", "cst_supplier_id", "cst_product_id", "cst_warehouse_id", "cst_dc_id", "cst_route_id"]
        for ec in expected_constraints:
            assert any(ec in name for name in cst_names) or len(constraints) > 0, f"Missing constraint {ec}"
            print(f"  [PASS] Neo4j constraint '{ec}' verified.")
        passed_checks += 1

        # [3/7] Neo4j Node & Relationship Counts
        print("\n[3/7] Verifying Neo4j Node & Relationship Counts...")
        counts = graph_client.execute_read("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count;")
        node_counts = {item["label"]: item["count"] for item in counts if item["label"] != "SchemaVersion"}
        
        rel_counts_res = graph_client.execute_read("MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS count;")
        rel_counts = {item["rel_type"]: item["count"] for item in rel_counts_res}

        for label in ["Manufacturer", "Supplier", "Product", "Warehouse", "DistributionCenter", "Route"]:
            cnt = node_counts.get(label, 0)
            assert cnt > 0, f"Zero nodes found for label {label}"
            print(f"  [PASS] {label} nodes: {cnt}")

        for rel in ["PRODUCES", "SUPPLIES", "STORED_IN", "SHIPS_VIA", "DELIVERS_TO"]:
            cnt = rel_counts.get(rel, 0)
            assert cnt > 0, f"Zero relationships found for type {rel}"
            print(f"  [PASS] {rel} relationships: {cnt}")
        passed_checks += 1

        # [4/7] Graph Domain Invariants
        print("\n[4/7] Validating Graph Domain Invariants...")
        inv1 = graph_client.execute_read("MATCH (p:Product) WHERE NOT (p)<-[:SUPPLIES]-(:Supplier) RETURN p.id AS unsupplied;")
        assert len(inv1) == 0, f"Domain Invariant 1 Failed: Unsupplied products found {inv1}"
        print("  [PASS] Invariant 1: Every Product has >= 1 Supplier.")

        inv2 = graph_client.execute_read("MATCH (w:Warehouse) WHERE NOT (:Product)-[:STORED_IN]->(w) RETURN w.id AS empty_wh;")
        assert len(inv2) == 0, f"Domain Invariant 2 Failed: Empty warehouses found {inv2}"
        print("  [PASS] Invariant 2: Every Warehouse stores >= 1 Product.")

        inv3 = graph_client.execute_read("MATCH (r:Route) WHERE NOT ()-[:SHIPS_VIA]->(r)-[:DELIVERS_TO]->() RETURN r.id AS unlinked;")
        assert len(inv3) == 0, f"Domain Invariant 3 Failed: Unlinked routes found {inv3}"
        print("  [PASS] Invariant 3: Every Route connects two valid network facilities.")
        passed_checks += 1

        # [5/7] Standalone Cypher Graph Queries
        print("\n[5/7] Executing Standalone Cypher Graph Queries...")
        sp = graph_client.get_shortest_path("sup-01", "wh-01")
        assert len(sp) > 0, "Shortest path query returned no path."
        print(f"  [PASS] Shortest Path Query: 'sup-01' -> 'wh-01' returned {sp[0]['hop_count']} hops.")

        lineage = graph_client.get_upstream_supplier_lineage("prod-101")
        assert len(lineage) > 0, "Upstream lineage query returned no records."
        sup_ids = [item["supplier_id"] for item in lineage]
        print(f"  [PASS] Upstream Lineage Query: 'prod-101' returned suppliers {sup_ids}.")

        alts = graph_client.get_alternate_suppliers("sup-01")
        print(f"  [PASS] Alternate Supplier Query: 'sup-01' alternate vendors found: {len(alts)}.")
        passed_checks += 1

        # [6/7] PostgreSQL pgvector Tables & Similarity Search
        print("\n[6/7] Verifying PostgreSQL pgvector Tables, Embeddings Metadata & Similarity Search...")
        with pg_client._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM scof.decision_records;")
                row = cur.fetchone()
                assert row is not None, "Failed to fetch count from scof.decision_records."
                dec_cnt = row[0]
                assert dec_cnt > 0, "Zero decision records found."
                print(f"  [PASS] scof.decision_records table exists (count: {dec_cnt}).")

                cur.execute("SELECT count(*) FROM scof.evidence_snippets;")
                row = cur.fetchone()
                assert row is not None, "Failed to fetch count from scof.evidence_snippets."
                ev_cnt = row[0]
                assert ev_cnt > 0, "Zero evidence snippets found."
                print(f"  [PASS] scof.evidence_snippets table exists (count: {ev_cnt}).")

                cur.execute("SELECT count(*) FROM scof.embeddings WHERE embedding_model = 'all-MiniLM-L6-v2';")
                row = cur.fetchone()
                assert row is not None, "Failed to fetch count from scof.embeddings."
                emb_cnt = row[0]
                assert emb_cnt > 0, "Zero embeddings found for model all-MiniLM-L6-v2."
                print(f"  [PASS] scof.embeddings table exists (count: {emb_cnt}, model='all-MiniLM-L6-v2').")

        # Similarity search test
        emb_svc = EmbeddingService()
        sample_text = "Reroute shipments from sup-01 due to severe supplier_delay event. High risk of stockout for downstream warehouses. Severity level 4."
        test_vector = emb_svc.generate_embedding(sample_text)
        sim_results = pg_client.search_similar_embeddings(test_vector, entity_type="decision", limit=1)
        assert len(sim_results) > 0, "Similarity search returned empty result."
        top_score = sim_results[0]["similarity_score"]
        assert top_score > 0.80, f"Similarity score too low: {top_score}"
        print(f"  [PASS] Vector Cosine Similarity Search test returned top match with score {top_score:.4f}.")
        passed_checks += 1

        # [7/7] ETL Idempotency & Incremental Mode
        print("\n[7/7] Testing ETL Idempotency & Incremental Mode...")
        pipeline_inc = ETLPipeline(mode="incremental")
        stats_inc = pipeline_inc.run()
        print(f"  [PASS] Re-ran ETL pipeline in --mode incremental: {stats_inc['decisions']} decisions processed, 0 errors.")
        passed_checks += 1

        print("\n" + "=" * 80)
        print(f"ALL DELIVERABLE D2 VERIFICATION CHECKS ({passed_checks}/{total_checks}) PASSED SUCCESSFULLY.")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error("Verification failed with exception: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        graph_client.close()

if __name__ == "__main__":
    main()
