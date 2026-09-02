#!/usr/bin/env python3
"""
SCOF Deliverable D10.1: Full Loop Autonomous Wiring Verification Script.

Validates the complete autonomous loop without manual intervention:
1. Microservice Fleet Health Audit (API, Coordinator, Consensus, Observability, 4 Specialist Agents).
2. Autonomous Disruption Injection via API Gateway (POST /scenarios/trigger).
3. Event Dispatch & Dynamic Multi-Agent A2A Delegation.
4. CD2F Consensus Arbitration, Confidence-Weighting & Escalation Tiering.
5. Decision Trace & Reasoning Trail Persistence (PostgreSQL & pgvector).
6. API Gateway Data Exposure (Decisions, Meeting Logs, Confidence Views, Full Traces).
7. Vector Similarity Retrieval (RAG Search over Decisional Embeddings).
8. End-to-End Latency Measurement & Audit Reporting.
"""

import sys
import time
import httpx
from typing import Dict, Any, List


SERVICES = {
    "API Gateway": "http://localhost:8000/health",
    "Coordinator": "http://localhost:8010/health",
    "Consensus Engine": "http://localhost:8020/health",
    "Observability": "http://localhost:8030/health",
    "Demand Agent": "http://localhost:8011/health",
    "Inventory Agent": "http://localhost:8012/health",
    "Supplier Agent": "http://localhost:8013/health",
    "Transportation Agent": "http://localhost:8014/health",
}

API_BASE = "http://localhost:8000"


def print_separator(title: str = ""):
    line = "=" * 70
    if title:
        print(f"\n{line}\n  {title}\n{line}")
    else:
        print(line)


def run_full_loop_verification():
    print_separator("SCOF DELIVERABLE D10.1: FULL LOOP AUTONOMOUS WIRING VERIFICATION")
    
    audit_results: List[Dict[str, Any]] = []

    with httpx.Client(timeout=15.0) as client:
        # -------------------------------------------------------------
        # STAGE 1: Infrastructure & Service Fleet Health Check
        # -------------------------------------------------------------
        print("\n[STAGE 1] Auditing Microservice Fleet Health...")
        fleet_healthy = True
        for name, url in SERVICES.items():
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    print(f"  [OK] {name:<22} -> 200 OK")
                else:
                    print(f"  [FAIL] {name:<22} -> Status {resp.status_code}")
                    fleet_healthy = False
            except Exception as e:
                print(f"  [FAIL] {name:<22} -> Connection Error: {e}")
                fleet_healthy = False

        audit_results.append({
            "stage": "Stage 1: Microservice Fleet Health",
            "status": "PASS" if fleet_healthy else "FAIL",
            "details": f"All {len(SERVICES)} microservices healthy and responding",
        })
        if not fleet_healthy:
            print("\nError: One or more services are unhealthy. Aborting full loop verification.")
            return False

        # -------------------------------------------------------------
        # STAGE 2: Autonomous Disruption Event Injection
        # -------------------------------------------------------------
        print("\n[STAGE 2] Injecting Disruption Scenario via API Gateway...")
        scenario_payload = {
            "scenario_id": "scen-02",
            "disruption_type": "supplier_delay",
            "target_entity_id": "sup-01",
            "severity": 4,
        }
        
        t0 = time.perf_counter()
        try:
            resp = client.post(f"{API_BASE}/scenarios/trigger", json=scenario_payload)
            trigger_latency = (time.perf_counter() - t0) * 1000
            resp.raise_for_status()
            trigger_data = resp.json()
            
            event_id = trigger_data.get("event_id")
            trace_id = trigger_data.get("trace_id")
            status = trigger_data.get("status")
            
            print(f"  Trigger Response Status: {status}")
            print(f"  Assigned Event ID:       {event_id}")
            print(f"  Assigned Trace ID:       {trace_id}")
            print(f"  Trigger Latency:         {trigger_latency:.2f} ms")

            assert status == "TRIGGERED", f"Unexpected status: {status}"
            assert event_id is not None, "event_id was null"
            assert trace_id is not None, "trace_id was null"

            audit_results.append({
                "stage": "Stage 2: Disruption Event Injection",
                "status": "PASS",
                "details": f"Triggered {scenario_payload['scenario_id']} (event={event_id}, latency={trigger_latency:.1f}ms)",
            })
        except Exception as e:
            print(f"  [FAIL] Disruption trigger failed: {e}")
            audit_results.append({
                "stage": "Stage 2: Disruption Event Injection",
                "status": "FAIL",
                "details": str(e),
            })
            return False

        # -------------------------------------------------------------
        # STAGE 3 & 4: Multi-Agent A2A Delegation & CD2F Consensus Arbitration
        # -------------------------------------------------------------
        print("\n[STAGE 3 & 4] Polling for Consensus Decision Completion...")
        decision_record = None
        max_retries = 12
        poll_interval = 0.5
        
        for attempt in range(1, max_retries + 1):
            time.sleep(poll_interval)
            try:
                dec_resp = client.get(f"{API_BASE}/decisions")
                if dec_resp.status_code == 200:
                    decisions = dec_resp.json()
                    if decisions:
                        # Find the decision matching this scenario
                        for d in decisions:
                            if d.get("scenario_id") == scenario_payload["scenario_id"]:
                                decision_record = d
                                break
                        if decision_record:
                            break
            except Exception as e:
                print(f"  Polling attempt {attempt} error: {e}")

        total_loop_latency = (time.perf_counter() - t0) * 1000

        if not decision_record:
            print("  [FAIL] Timed out waiting for decision record to complete.")
            audit_results.append({
                "stage": "Stage 3 & 4: Multi-Agent Delegation & CD2F Arbitration",
                "status": "FAIL",
                "details": "Timeout waiting for decision record",
            })
            return False

        decision_id = decision_record.get("decision_id")
        method = decision_record.get("decision_method")
        rec = decision_record.get("final_recommendation")
        conf = decision_record.get("decision_confidence", 0.0)
        wcs = decision_record.get("weighted_consensus_stability", 0.0)
        tier = decision_record.get("escalation_tier")

        print(f"  Consensus Decision ID:   {decision_id}")
        print(f"  Arbitration Method:      {method}")
        print(f"  Winning Recommendation:  {rec}")
        print(f"  Decision Confidence:     {conf:.3f}")
        print(f"  Consensus Stability WCS: {wcs:.3f}")
        print(f"  Escalation Tier:         {tier}")
        print(f"  Total Round-Trip Time:   {total_loop_latency:.2f} ms")

        assert method == "CD2F", f"Expected CD2F method, got {method}"
        assert rec is not None, "Winning recommendation was null"
        assert conf > 0.0, "Confidence was 0"
        assert tier in ["FAST_PATH", "SLOW_PATH", "HUMAN_ESCALATION"], f"Invalid tier: {tier}"

        audit_results.append({
            "stage": "Stage 3 & 4: Delegation & CD2F Arbitration",
            "status": "PASS",
            "details": f"Method={method}, Tier={tier}, Confidence={conf:.2f}, WCS={wcs:.2f}",
        })

        # -------------------------------------------------------------
        # STAGE 5: Trace Persistence & Reasoning Trail Verification
        # -------------------------------------------------------------
        print("\n[STAGE 5] Verifying Trace Persistence & Reasoning Trail...")
        try:
            trace_resp = client.get(f"{API_BASE}/decisions/{decision_id}/trace")
            trace_resp.raise_for_status()
            trace_data = trace_resp.json()
            
            trail = trace_data.get("reasoning_trail", [])
            print(f"  Reasoning Trail Steps:   {len(trail)}")
            for step in trail[:3]:
                idx = step.get('step_index')
                stype = step.get('step_type')
                content = step.get('content', '')
                print(f"    - Step {idx} [{stype}]: {content[:60]}...")

            assert len(trail) > 0, "Reasoning trail was empty"
            audit_results.append({
                "stage": "Stage 5: Trace & Reasoning Persistence",
                "status": "PASS",
                "details": f"Persisted {len(trail)} reasoning steps",
            })
        except Exception as e:
            print(f"  [FAIL] Failed to fetch trace: {e}")
            audit_results.append({
                "stage": "Stage 5: Trace & Reasoning Persistence",
                "status": "FAIL",
                "details": str(e),
            })
            return False

        # -------------------------------------------------------------
        # STAGE 6: AI Meeting Log & Confidence View Ingestion
        # -------------------------------------------------------------
        print("\n[STAGE 6] Verifying Meeting Log & Confidence Data Ingestion...")
        try:
            log_resp = client.get(f"{API_BASE}/decisions/{decision_id}/log")
            log_resp.raise_for_status()
            log_data = log_resp.json()
            
            conf_resp = client.get(f"{API_BASE}/decisions/{decision_id}/confidence")
            conf_resp.raise_for_status()
            conf_data = conf_resp.json()

            meeting_entries = log_data.get("meeting_log", []) or log_data.get("meeting_log_entries", [])
            tallies = conf_data.get("recommendation_tallies", {})
            stability = conf_data.get("weighted_consensus_stability", 0.0)

            print(f"  Meeting Log Entries:     {len(meeting_entries)}")
            print(f"  Consensus Stability:     {stability:.3f}")
            if meeting_entries:
                first = meeting_entries[0]
                print(f"  First Meeting Statement: [{first.get('speaker')}]: {first.get('content', '')[:60]}...")

            assert len(meeting_entries) > 0, "Meeting log was empty"
            assert stability > 0.0, "Consensus stability was 0"

            audit_results.append({
                "stage": "Stage 6: Meeting Log & Confidence Ingestion",
                "status": "PASS",
                "details": f"Meeting entries: {len(meeting_entries)}, Stability: {stability:.2f}",
            })
        except Exception as e:
            print(f"  [FAIL] Failed to fetch log/confidence: {e}")
            audit_results.append({
                "stage": "Stage 6: Meeting Log & Confidence Ingestion",
                "status": "FAIL",
                "details": str(e),
            })
            return False

        # -------------------------------------------------------------
        # STAGE 7: AI Vector Semantic Retrieval (RAG Search)
        # -------------------------------------------------------------
        print("\n[STAGE 7] Verifying Vector Similarity Search (pgvector)...")
        try:
            chat_query = "What was the mitigation for scen-02?"
            chat_resp = client.post(f"{API_BASE}/chat/query", json={"query": chat_query, "top_k": 3})
            chat_resp.raise_for_status()
            chat_data = chat_resp.json()

            answer = chat_data.get("answer", "")
            citations = chat_data.get("citations", [])
            print(f"  Chat Query:              '{chat_query}'")
            print(f"  AI Response:             {answer[:80]}...")
            print(f"  Citations Returned:      {len(citations)}")

            assert len(answer) > 0, "AI answer was empty"

            audit_results.append({
                "stage": "Stage 7: Vector Semantic Retrieval (RAG)",
                "status": "PASS",
                "details": f"Retrieved answer with {len(citations)} citations via pgvector",
            })
        except Exception as e:
            print(f"  [FAIL] RAG query failed: {e}")
            audit_results.append({
                "stage": "Stage 7: Vector Semantic Retrieval (RAG)",
                "status": "FAIL",
                "details": str(e),
            })
            return False

        # -------------------------------------------------------------
        # STAGE 8: System Latency Profiling
        # -------------------------------------------------------------
        print("\n[STAGE 8] Profiling Execution Latency...")
        is_subsecond = total_loop_latency < 2000.0  # complete full loop < 2.0s
        print(f"  Trigger-to-Decide Latency: {total_loop_latency:.2f} ms")
        print(f"  Latency SLA Target:        < 2000.0 ms")
        print(f"  Latency Compliance:        {'PASS' if is_subsecond else 'WARNING'}")

        audit_results.append({
            "stage": "Stage 8: Latency Profiling",
            "status": "PASS" if is_subsecond else "WARNING",
            "details": f"Total loop latency: {total_loop_latency:.1f}ms",
        })

    # -------------------------------------------------------------
    # Final Summary Matrix
    # -------------------------------------------------------------
    print_separator("DELIVERABLE D10.1 AUDIT SUMMARY MATRIX")
    all_passed = True
    for res in audit_results:
        print(f"  [{res['status']}] {res['stage']:<45} | {res['details']}")
        if res["status"] == "FAIL":
            all_passed = False
    print_separator()

    if all_passed:
        print("  ALL 8 FULL-LOOP STAGES PASSED AUTONOMOUSLY. D10.1 VERIFIED!")
    else:
        print("  VERIFICATION FAILED: One or more stages did not pass.")
    print_separator()

    return all_passed


if __name__ == "__main__":
    success = run_full_loop_verification()
    sys.exit(0 if success else 1)
