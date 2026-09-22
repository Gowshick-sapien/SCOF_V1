#!/usr/bin/env python3
"""
SCOF Deterministic Synthetic Ecosystem Generation Engine (Phase 2B)
Topological Scheduler & Executor governed strictly by generation_manifest.json.

Responsibilities:
1. Load generation_manifest.json
2. Topological execution schedule
3. Resolve generator class dynamically
4. Execute generator with isolated RNG stream
5. Validate output invariants
6. Generator-level checkpointing in run_manifest.json
7. Support --resume for incremental runs
"""

import os
import sys
import time
import json
import argparse
import importlib
from datetime import datetime, timezone
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

MANIFEST_PATH = os.path.join(BASE_DIR, "generation_manifest.json")
RUN_MANIFEST_PATH = os.path.join(BASE_DIR, "run_manifest.json")
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

def load_or_init_run_manifest() -> Dict[str, Any]:
    if os.path.exists(RUN_MANIFEST_PATH):
        try:
            with open(RUN_MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "run_id": f"RUN_{int(time.time())}",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "status": "IN_PROGRESS",
        "completed_steps": {},
        "total_rows_generated": 0
    }

def save_run_manifest(run_manifest: Dict[str, Any]):
    with open(RUN_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2)

def resolve_generator_class(class_path: str):
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def run_ecosystem_generation(resume: bool = False, max_tier: int = 7):
    print("================================================================================")
    print("SCOF ENTERPRISE COGNITIVE TWIN — DETERMINISTIC GENERATION ENGINE (PHASE 2B)")
    print("================================================================================")
    print(f"Manifest Path:     {MANIFEST_PATH}")
    print(f"Run Manifest Path: {RUN_MANIFEST_PATH}")
    print(f"Datasets Dir:      {DATASETS_DIR}")
    print(f"Resume Mode:       {resume}")
    print(f"Max Tier Filter:   Tier {max_tier}")
    print("================================================================================\n")

    if not os.path.exists(MANIFEST_PATH):
        print(f"[ERROR] Manifest file does not exist: {MANIFEST_PATH}", file=sys.stderr)
        print("Please run scripts/build_generation_manifest.py first.", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    execution_plan = manifest.get("execution_plan", [])
    if not execution_plan:
        print("[ERROR] Execution plan in manifest is empty.", file=sys.stderr)
        sys.exit(1)

    run_manifest = load_or_init_run_manifest()
    completed_steps = run_manifest.get("completed_steps", {})

    context = {
        "base_dir": BASE_DIR,
        "datasets_dir": DATASETS_DIR,
        "rng_seed_base": 42
    }

    start_engine_time = time.time()
    total_steps = len(execution_plan)
    executed_count = 0
    skipped_count = 0

    print(f"Starting execution of {total_steps} scheduled generator steps...\n")

    for step in execution_plan:
        step_idx = step["step"]
        node_id = step["generator_node"]
        name = step["name"]
        tier = step["scheduling_tier"]
        gen_class_path = step["generator_class"]
        storage_fmt = step["storage_format"]

        if tier > max_tier:
            continue

        # Check if already completed and valid
        if resume and node_id in completed_steps:
            prev_result = completed_steps[node_id]
            if prev_result.get("status") == "SUCCESS":
                print(f"[{step_idx:02d}/{total_steps:02d}] Tier {tier} | [{node_id}] {name} -> SKIPPED (Already Certified)")
                skipped_count += 1
                continue

        print(f"[{step_idx:02d}/{total_steps:02d}] Tier {tier} | [{node_id}] {name} ({storage_fmt})...", end="", flush=True)
        step_start_time = time.time()

        try:
            # Dynamically resolve and instantiate generator
            GeneratorClass = resolve_generator_class(gen_class_path)
            generator_instance = GeneratorClass(step, context)

            # Execute generation
            result = generator_instance.execute()
            step_duration = round(time.time() - step_start_time, 3)

            # Validate output
            if not generator_instance.validate_output(result):
                print(f" FAILED!")
                print(f"[VALIDATION FAILURE] Output invariant check failed for node '{node_id}'", file=sys.stderr)
                run_manifest["status"] = "FAILED"
                save_run_manifest(run_manifest)
                sys.exit(1)

            # Checkpoint step
            row_count = result.get("row_count", 0)
            checksum = result.get("checksum", "UNKNOWN")
            checkpoint_record = {
                "step": step_idx,
                "generator_node": node_id,
                "name": name,
                "scheduling_tier": tier,
                "status": "SUCCESS",
                "row_count": row_count,
                "checksum": checksum,
                "duration_seconds": step_duration,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "output_files": result.get("output_files", []),
                "metrics": result.get("metrics", {})
            }

            completed_steps[node_id] = checkpoint_record
            run_manifest["completed_steps"] = completed_steps
            run_manifest["total_rows_generated"] = sum(s.get("row_count", 0) for s in completed_steps.values())
            save_run_manifest(run_manifest)

            executed_count += 1
            print(f" SUCCESS! ({row_count:,} rows in {step_duration}s | SHA: {checksum[:12]})")

        except Exception as e:
            print(f" FAILED!")
            print(f"[FATAL EXECUTION ERROR in {node_id}]: {str(e)}", file=sys.stderr)
            run_manifest["status"] = "FAILED"
            save_run_manifest(run_manifest)
            sys.exit(1)

    total_engine_duration = round(time.time() - start_engine_time, 2)
    run_manifest["status"] = "COMPLETED"
    run_manifest["end_time"] = datetime.now(timezone.utc).isoformat()
    run_manifest["total_duration_seconds"] = total_engine_duration
    save_run_manifest(run_manifest)

    print("\n================================================================================")
    print("PHASE 2B DETERMINISTIC GENERATION ENGINE EXECUTION SUMMARY")
    print("================================================================================")
    print(f"Total Steps in DAG:     {total_steps}")
    print(f"Executed Steps:         {executed_count}")
    print(f"Skipped (Resumed):      {skipped_count}")
    print(f"Total Rows Accounted:   {run_manifest['total_rows_generated']:,}")
    print(f"Total Engine Duration:  {total_engine_duration}s")
    print(f"Checkpoint Manifest:    {RUN_MANIFEST_PATH}")
    print("Certification Status:   ALL SCHEDULED GENERATORS PASSED WITH ZERO VIOLATIONS")
    print("================================================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCOF Deterministic Synthetic Ecosystem Generation Engine")
    parser.add_argument("--resume", action="store_true", help="Resume from previous checkpoint in run_manifest.json")
    parser.add_argument("--max-tier", type=int, default=7, help="Maximum scheduling tier to execute (0 to 7)")
    args = parser.parse_args()

    run_ecosystem_generation(resume=args.resume, max_tier=args.max_tier)
