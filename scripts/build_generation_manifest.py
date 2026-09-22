#!/usr/bin/env python3
"""
SCOF Generation Manifest Compiler (Phase 2A)
Authoritative compiler translating SCOF_Physical_Generation_DAG.yaml into generation_manifest.json.

Enforces strict fail-closed validation:
1. Duplicate generator node -> FAIL
2. Unknown dependency -> FAIL
3. Missing generator class -> FAIL
4. Cycle detected -> FAIL
5. Tier inversion -> FAIL
6. Unassigned RNG namespace -> FAIL
7. Unresolved canonical entity -> FAIL
8. Invalid storage format -> FAIL
"""

import os
import sys
import json
import re
import yaml
from collections import defaultdict, deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAG_YAML_PATH = os.path.join(BASE_DIR, "SCOF_Physical_Generation_DAG.yaml")
MANIFEST_OUT_PATH = os.path.join(BASE_DIR, "generation_manifest.json")
REALIZATION_MAP_PATH = r"C:\Users\Gowshick\.gemini\antigravity-ide\brain\a2c1edf9-ac72-4bf0-8dc2-a71df4430a2a\SCOF_Entity_Realization_Map.md"

VALID_STORAGE_FORMATS = {"SQL", "CSV", "Parquet", "JSON"}

def fail_closed(error_message: str):
    print(f"\n[FAIL-CLOSED COMPILATION ERROR] {error_message}", file=sys.stderr)
    sys.exit(1)

def load_canonical_entities(realization_map_path: str) -> set:
    if not os.path.exists(realization_map_path):
        fail_closed(f"Canonical realization map not found at {realization_map_path}")
    
    with open(realization_map_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Table rows: | <num> | `NOD_...` | **`Node_Name`** | ...
    entities = set(re.findall(r"\|\s*\d+\s*\|\s*`NOD_[^`]+`\s*\|\s*\*\*`([^`]+)`\*\*", content))
    if not entities:
        # Fallback to any node in column 3
        entities = set(re.findall(r"\|\s*\d+\s*\|\s*`NOD_[^`]+`\s*\|\s*`?([^`|\n]+)`?\s*\|", content))
    
    clean_entities = {e.strip("`* ") for e in entities if e.strip("`* ")}
    return clean_entities

def compile_manifest():
    print("=== Starting SCOF Generation Manifest Compiler (Phase 2A) ===")
    print(f"Reading structured DAG from: {DAG_YAML_PATH}")

    if not os.path.exists(DAG_YAML_PATH):
        fail_closed(f"Structured generation DAG file does not exist: {DAG_YAML_PATH}")

    with open(DAG_YAML_PATH, "r", encoding="utf-8") as f:
        try:
            dag_data = yaml.safe_load(f)
        except Exception as e:
            fail_closed(f"Failed to parse YAML DAG: {str(e)}")

    nodes = dag_data.get("generator_nodes", [])
    if not nodes:
        fail_closed("No generator_nodes defined in DAG file.")

    # 1. Check for duplicate generator nodes
    node_registry = {}
    for node in nodes:
        node_id = node.get("generator_node")
        if not node_id:
            fail_closed("Encountered generator node without 'generator_node' identifier.")
        if node_id in node_registry:
            fail_closed(f"Duplicate generator node detected: '{node_id}'")
        node_registry[node_id] = node

    print(f"Loaded {len(node_registry)} distinct generator nodes.")

    # 2. Validate node schemas and constraints
    for node_id, node in node_registry.items():
        tier = node.get("scheduling_tier")
        if tier is None or not isinstance(tier, int) or tier < 0 or tier > 7:
            fail_closed(f"Node '{node_id}' has invalid scheduling_tier: {tier}. Must be integer between 0 and 7.")

        gen_class = node.get("generator_class")
        if not gen_class or not isinstance(gen_class, str) or not gen_class.strip():
            fail_closed(f"Missing generator class for node '{node_id}'")

        fmt = node.get("storage_format")
        if not fmt or fmt not in VALID_STORAGE_FORMATS:
            fail_closed(f"Node '{node_id}' has invalid storage_format '{fmt}'. Expected one of {VALID_STORAGE_FORMATS}")

        rng_ns = node.get("rng_namespace")
        if not rng_ns or not isinstance(rng_ns, str) or not rng_ns.strip():
            fail_closed(f"Unassigned RNG namespace for node '{node_id}'")

        card_drv = node.get("cardinality_driver")
        if not card_drv or not isinstance(card_drv, str) or not card_drv.strip():
            fail_closed(f"Missing cardinality_driver for node '{node_id}'")

    # 3. Validate dependencies & tier consistency
    for node_id, node in node_registry.items():
        deps = node.get("depends_on", [])
        current_tier = node.get("scheduling_tier")
        for dep in deps:
            if dep not in node_registry:
                fail_closed(f"Unknown dependency: Node '{node_id}' depends on non-existent node '{dep}'")
            
            dep_tier = node_registry[dep].get("scheduling_tier")
            if dep_tier > current_tier:
                fail_closed(f"Tier inversion detected: Node '{node_id}' in Tier {current_tier} depends on node '{dep}' in Tier {dep_tier}")

    # 4. Verify canonical entities against authoritative registry
    canonical_entities = load_canonical_entities(REALIZATION_MAP_PATH)
    print(f"Loaded {len(canonical_entities)} canonical entities from authoritative realization map.")

    claimed_entities = set()
    for node_id, node in node_registry.items():
        entities = node.get("canonical_entities", [])
        for ent in entities:
            if ent not in canonical_entities:
                fail_closed(f"Unresolved canonical entity: Node '{node_id}' references unknown canonical entity '{ent}'")
            claimed_entities.add(ent)

    print(f"Verified {len(claimed_entities)} canonical entities claimed across all generator nodes.")

    # 5. Topological Sort & Cycle Detection (Kahn's Algorithm)
    in_degree = {n: 0 for n in node_registry}
    adj_list = defaultdict(list)

    for node_id, node in node_registry.items():
        for dep in node.get("depends_on", []):
            adj_list[dep].append(node_id)
            in_degree[node_id] += 1

    queue = deque([n for n, d in in_degree.items() if d == 0])
    scheduled_nodes = []

    # Sort queue by scheduling_tier to preserve tier priority
    while queue:
        # Pick node with lowest tier first
        queue = deque(sorted(queue, key=lambda x: (node_registry[x]["scheduling_tier"], x)))
        curr = queue.popleft()
        scheduled_nodes.append(curr)

        for neighbor in adj_list[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(scheduled_nodes) != len(node_registry):
        unresolved = [n for n, d in in_degree.items() if d > 0]
        fail_closed(f"Cycle detected in generator dependency graph! Unresolved nodes: {unresolved}")

    print("Topological sort successful: 0 cycles detected across all 8 tiers.")

    # 6. Verify Tier 7 Internal Dependency Sequence
    tier7_nodes = [n for n in scheduled_nodes if node_registry[n]["scheduling_tier"] == 7]
    tier7_order = {n: i for i, n in enumerate(tier7_nodes)}
    
    expected_tier7_order = [
        "GEN_T7_SUPP_INVOICE",
        "GEN_T7_THREE_WAY_MATCH",
        "GEN_T7_PAYMENT",
        "GEN_T7_GL_LEDGER"
    ]
    
    for i in range(len(expected_tier7_order) - 1):
        n1 = expected_tier7_order[i]
        n2 = expected_tier7_order[i + 1]
        if n1 in tier7_order and n2 in tier7_order:
            if tier7_order[n1] > tier7_order[n2]:
                fail_closed(f"Tier 7 internal sequencing violation: '{n1}' must execute before '{n2}'")

    print("Tier 7 internal DAG sequencing verified: Supplier_Invoice -> Three_Way_Match -> Payment -> GL.")

    # 7. Construct and emit final manifest
    execution_plan = []
    for step_idx, node_id in enumerate(scheduled_nodes, 1):
        node = node_registry[node_id]
        execution_plan.append({
            "step": step_idx,
            "generator_node": node_id,
            "name": node.get("name"),
            "scheduling_tier": node.get("scheduling_tier"),
            "generator_class": node.get("generator_class"),
            "storage_format": node.get("storage_format"),
            "rng_namespace": node.get("rng_namespace"),
            "cardinality_driver": node.get("cardinality_driver"),
            "depends_on": node.get("depends_on", []),
            "canonical_entities": node.get("canonical_entities", [])
        })

    manifest = {
        "manifest_version": "1.0.0",
        "ecosystem": "SCOF Enterprise Cognitive Twin",
        "compilation_status": "CERTIFIED_VALID",
        "total_nodes": len(execution_plan),
        "tiers": 8,
        "execution_plan": execution_plan
    }

    with open(MANIFEST_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully compiled generation manifest: {MANIFEST_OUT_PATH}")
    print("\n=== TOPOLOGICAL EXECUTION SCHEDULE ===")
    for step in execution_plan:
        print(f"Step {step['step']:02d} | Tier {step['scheduling_tier']} | [{step['generator_node']}] {step['name']} ({step['storage_format']})")

    print("\nManifest compilation completed successfully with zero violations.")

if __name__ == "__main__":
    compile_manifest()
