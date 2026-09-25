import logging
import os
import sys
from pathlib import Path
import sqlite3
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT / "shared") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "shared"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scof_shared.knowledge.semantic_memory_store import (
    SemanticMemoryStore,
    SemanticDocumentInput,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_DIR = r"d:\projects\SCOF_V1\SCOF"
SQLITE_DB_PATH = os.path.join(WORKSPACE_DIR, "datasets", "scof_relational.db")

def validate_relational_provenance(entity_type: str, entity_id: str, db_path: str = SQLITE_DB_PATH) -> bool:
    """
    Validates that operational provenance references real entities in the relational system.
    """
    if not os.path.exists(db_path):
        logger.warning("Relational database not found at %s. Skipping foreign entity check.", db_path)
        return True

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        if entity_type == "SUPPLIER":
            res = cur.execute("SELECT 1 FROM supplier_profile WHERE supplier_profile_id = ?", (entity_id,)).fetchone()
            return res is not None
        elif entity_type in ("FACILITY", "STORE", "WAREHOUSE"):
            res = cur.execute("SELECT 1 FROM facility WHERE facility_id = ?", (entity_id,)).fetchone()
            return res is not None
        elif entity_type == "PURCHASE_ORDER":
            res = cur.execute("SELECT 1 FROM purchase_order WHERE po_id = ?", (entity_id,)).fetchone()
            return res is not None
        elif entity_type == "SCENARIO":
            res = cur.execute("SELECT 1 FROM scenario WHERE scenario_id = ?", (entity_id,)).fetchone()
            return res is not None
        elif entity_type == "SKU":
            res = cur.execute("SELECT 1 FROM sku WHERE sku_id = ?", (entity_id,)).fetchone()
            return res is not None
        return False
    except Exception as e:
        logger.warning("Provenance validation error against %s: %s", entity_type, e)
        return False
    finally:
        conn.close()
    return True


CONTROLLED_SEED_CORPUS: List[Dict] = [
    # Benchmark Target
    {
        "document_type": "SCENARIO",
        "title": "Supplier Production Delay Causing Downstream Store Stockout Risk",
        "content": (
            "Supplier SUP-PR-001 experiences a 10-day chemical precursor production freeze at the manufacturing facility, "
            "introducing severe delivery delays and immediate stockout risk for SKU APP-CHI-00001 across regional stores "
            "including retail store STR-001."
        ),
        "source_entity_type": "SUPPLIER",
        "source_entity_id": "SUP-PR-001",
        "scenario_id": "SCEN-F3992CF4",
        "run_id": "RUN-20260921-01",
        "agent_id": "SUPPLIER_AGENT",
        "logical_key": "target-supplier-delay-stockout",
        "metadata_json": {"severity": "CRITICAL", "benchmark_role": "TARGET"}
    },
    # Hard Negative 1: Supplier delay -> Transportation rerouting (not stockout)
    {
        "document_type": "SCENARIO",
        "title": "Supplier Lead-Time Surge Mitigated by Expedited Route Diversion",
        "content": (
            "Supplier SUP-PR-004 incurs a 48-hour dispatch delay at the regional depot. "
            "Transport Coordinator executes freight route diversion and lane reassignment from road corridor to dedicated rail "
            "to maintain arrival schedules without impacting warehouse inventory thresholds."
        ),
        "source_entity_type": "SUPPLIER",
        "source_entity_id": "SUP-PR-004",
        "scenario_id": "SCEN-F3992CF4",
        "run_id": "RUN-20260921-01",
        "agent_id": "TRANSPORT_AGENT",
        "logical_key": "negative-supplier-delay-reroute",
        "metadata_json": {"severity": "MEDIUM", "benchmark_role": "HARD_NEGATIVE_1"}
    },
    # Hard Negative 2: Stockout -> Store replenishment schedule (not supplier delay)
    {
        "document_type": "AGENT_EVIDENCE",
        "title": "Store Safety Stock Depletion Handled via Scheduled Cross-Dock Replenishment",
        "content": (
            "Retail store STR-001 experiences high holiday sales velocity, causing SKU APP-CHI-00001 on-shelf quantity "
            "to drop below reserve stock. Scheduled cross-dock transfer from central warehouse WH-001 successfully restores "
            "inventory buffer within normal 24-hour replenishment cycles."
        ),
        "source_entity_type": "FACILITY",
        "source_entity_id": "STR-001",
        "scenario_id": "SCEN-F3992CF4",
        "run_id": "RUN-20260921-01",
        "agent_id": "INVENTORY_AGENT",
        "logical_key": "negative-store-stockout-replenish",
        "metadata_json": {"severity": "LOW", "benchmark_role": "HARD_NEGATIVE_2"}
    },
    # Hard Negative 3: Quality defect -> Quarantine hold (not supplier lead delay)
    {
        "document_type": "AGENT_EVIDENCE",
        "title": "Inbound Lot Quality Non-Conformance Resulting in Warehouse Quarantine",
        "content": (
            "Quality assurance inspection at warehouse WH-001 identifies damaged outer packaging seals on shipment under "
            "PO-2026-000001 from supplier SUP-PR-001. Entire lot of 500 units placed on immediate technical quarantine hold "
            "pending certificate of analysis."
        ),
        "source_entity_type": "PURCHASE_ORDER",
        "source_entity_id": "PO-2026-000001",
        "scenario_id": "SCEN-F3992CF4",
        "run_id": "RUN-20260921-01",
        "agent_id": "INVENTORY_AGENT",
        "logical_key": "negative-quality-quarantine",
        "metadata_json": {"severity": "MEDIUM", "benchmark_role": "HARD_NEGATIVE_3"}
    },
    # Distant Negative: Corporate Tax Audit
    {
        "document_type": "DECISION",
        "title": "Annual Corporate Statutory Tax and Double-Entry Reconciliation",
        "content": (
            "Finance audit committee completes fiscal year-end statutory balance sheet reconciliation, certifying "
            "double-entry ledger parity, capital asset depreciation schedules, and tax withholding compliance."
        ),
        "source_entity_type": "FACILITY",
        "source_entity_id": "WH-001",
        "scenario_id": "SCEN-F3992CF4",
        "run_id": "RUN-20260921-01",
        "agent_id": "CONSENSUS_ENGINE",
        "logical_key": "negative-tax-audit",
        "metadata_json": {"severity": "INFO", "benchmark_role": "DISTANT_NEGATIVE"}
    }
]

# Synthesize the remaining 45 real-ID artifacts across domains
def generate_enterprise_artifacts() -> List[Dict]:
    artifacts = list(CONTROLLED_SEED_CORPUS)
    domains = ["DEMAND", "INVENTORY", "SUPPLIER", "TRANSPORT", "FINANCE"]
    for i in range(1, 46):
        domain = domains[i % len(domains)]
        doc_type = "AGENT_EVIDENCE" if i % 2 == 0 else "DECISION"
        supp_id = "SUP-PR-001" if i % 2 == 0 else "SUP-PR-004"
        fac_id = "STR-001" if i % 3 == 0 else "WH-001"

        if domain == "INVENTORY":
            content = f"Inventory balance audit at {fac_id} verifies safety stock threshold for SKU APP-CHI-00001 with buffer index {i}."
            ent_type, ent_id = "FACILITY", fac_id
        elif domain == "SUPPLIER":
            content = f"Supplier performance evaluation for {supp_id} confirms on-time delivery rate under purchase contract PO-2026-000001 cycle {i}."
            ent_type, ent_id = "SUPPLIER", supp_id
        elif domain == "TRANSPORT":
            content = f"Freight transit lane analysis between {fac_id} and regional distribution hub reveals congestion index factor {i * 0.05:.2f}."
            ent_type, ent_id = "FACILITY", fac_id
        elif domain == "FINANCE":
            content = f"Three-way matching verification for PO-2026-000001 at {fac_id} verifies zero price variance on batch invoice {i}."
            ent_type, ent_id = "PURCHASE_ORDER", "PO-2026-000001"
        else:
            content = f"Causal demand forecast revision for SKU APP-CHI-00001 at {fac_id} projects baseline lift factor of {1.0 + (i * 0.02):.2f}."
            ent_type, ent_id = "SKU", "APP-CHI-00001"

        artifacts.append({
            "document_type": doc_type,
            "title": f"Enterprise Operational Record: {domain} Batch {i}",
            "content": content,
            "source_entity_type": ent_type,
            "source_entity_id": ent_id,
            "scenario_id": "SCEN-F3992CF4",
            "run_id": f"RUN-20260921-{(i % 3) + 1:02d}",
            "agent_id": f"{domain}_AGENT",
            "logical_key": f"artifact-{domain.lower()}-{i}",
            "metadata_json": {"domain": domain, "batch_index": i}
        })
    return artifacts


def seed_semantic_memory(store: Optional[SemanticMemoryStore] = None) -> int:
    """
    Idempotently seeds the 50 controlled multi-domain enterprise artifacts.
    Returns the number of documents successfully processed.
    """
    store = store or SemanticMemoryStore()
    store.sync_active_model_registry()
    artifacts = generate_enterprise_artifacts()
    logger.info("Starting idempotent seeding of %d enterprise semantic artifacts...", len(artifacts))

    validated_count = 0
    for art in artifacts:
        # Validate relational provenance
        is_valid = validate_relational_provenance(art["source_entity_type"], art["source_entity_id"])
        if not is_valid:
            logger.warning("Provenance check failed for %s:%s. Skipping.", art["source_entity_type"], art["source_entity_id"])
            continue

        doc_input = SemanticDocumentInput(
            document_type=art["document_type"],
            title=art["title"],
            content=art["content"],
            source_entity_type=art["source_entity_type"],
            source_entity_id=art["source_entity_id"],
            scenario_id=art["scenario_id"],
            run_id=art["run_id"],
            agent_id=art["agent_id"],
            logical_key=art["logical_key"],
            metadata_json=art["metadata_json"]
        )
        store.upsert_document(doc_input, auto_embed=True)
        validated_count += 1

    logger.info("Successfully seeded and embedded %d enterprise semantic artifacts.", validated_count)
    return validated_count

if __name__ == "__main__":
    seed_semantic_memory()
