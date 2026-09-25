"""
Deliverable D02 Live Semantic Search Test Script
------------------------------------------------
Executes interactive similarity search against PostgreSQL pgvector
using the authoritative SemanticMemoryStore.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "shared") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "shared"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ensure database URL is set
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://scof:changeme@localhost:5432/scof"

from scof_shared.knowledge.semantic_memory_store import SemanticMemoryStore

def main():
    store = SemanticMemoryStore()
    query = "historical situation where supplier delay caused inventory stockout risk"
    results = store.similarity_search(query, top_k=5)

    print("=" * 70)
    print(f"QUERY: \"{query}\"")
    print("=" * 70)
    for idx, r in enumerate(results, 1):
        print(f"Rank {idx}: [{r.similarity_score:.4f}] {r.document_type} | {r.source_entity_type}:{r.source_entity_id}")
        print(f"        Title  : {r.title}")
        print(f"        Snippet: {r.content[:100]}...")
        print("-" * 70)

if __name__ == "__main__":
    main()
