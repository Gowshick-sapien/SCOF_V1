import urllib.request
import json
import sys

API_BASE = "http://localhost:8000"

def log(msg):
    print(f"[VERIFY] {msg}")

def check_catalog():
    log("Checking scenario catalog API (/scenarios)...")
    req = urllib.request.Request(f"{API_BASE}/scenarios")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        scenarios = data.get("scenarios", [])
        log(f"Received {len(scenarios)} scenarios from API.")
        if len(scenarios) != 25:
            log(f"ERROR: Expected 25 scenarios, found {len(scenarios)}")
            return False
        
        scenario_ids = [s["scenario_id"] for s in scenarios]
        for i in range(1, 26):
            expected_id = f"scen-{i:02d}"
            if expected_id not in scenario_ids:
                log(f"ERROR: Missing scenario {expected_id}")
                return False
    log("Catalog API verification passed: All 25 scenarios present.")
    return True

def check_whatif_matrix():
    log("Checking What-If simulation matrix (/whatif/run)...")
    samples = [
        ("scen-01", "global", "RESOLVED"),
        ("scen-06", "sup-02", "RESOLVED"),
        ("scen-11", "wh-01", "RESOLVED"),
        ("scen-12", "wh-02", "ESCALATED_TO_HUMAN"),
        ("scen-16", "route-sup-07-mfg-01", "RESOLVED"),
        ("scen-24", "sup-01", "ESCALATED_TO_HUMAN"),
        ("scen-25", "mfg-01", "ESCALATED_TO_HUMAN"),
    ]

    for scen_id, expected_target, expected_status in samples:
        req = urllib.request.Request(
            f"{API_BASE}/whatif/run",
            data=json.dumps({"scenario_id": scen_id}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("target_entity") != expected_target:
                log(f"ERROR in {scen_id}: Expected target {expected_target}, got {res.get('target_entity')}")
                return False
            if res.get("consensus_status") != expected_status:
                log(f"ERROR in {scen_id}: Expected status {expected_status}, got {res.get('consensus_status')}")
                return False
            cost_var = res.get("cost_variance", "")
            if not cost_var.startswith("+\u20b9"):
                log(f"ERROR in {scen_id}: Cost variance missing INR prefix: {cost_var}")
                return False
            log(f"Validated {scen_id}: target={res['target_entity']}, severity={res['severity']}, status={res['consensus_status']}, cost={cost_var.encode('ascii', 'backslashreplace').decode()}")
    
    log("What-If simulation matrix verification passed.")
    return True

def check_trigger_dispatch():
    log("Checking scenario trigger dispatch (/scenarios/trigger)...")
    payload = {
        "scenario_id": "scen-06",
        "disruption_type": "supplier_delay",
        "target_entity_id": "sup-02",
        "severity": 4
    }
    req = urllib.request.Request(
        f"{API_BASE}/scenarios/trigger",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        if not res.get("event_id") or not res.get("trace_id"):
            log(f"ERROR: Invalid trigger dispatch response: {res}")
            return False
        log(f"Trigger dispatch successful: event_id={res['event_id']}, trace_id={res['trace_id']}, status={res.get('status')}")
    return True

def main():
    log("Starting End-to-End Scenario Suite Verification...")
    if not check_catalog():
        sys.exit(1)
    if not check_whatif_matrix():
        sys.exit(1)
    if not check_trigger_dispatch():
        sys.exit(1)
    log("All verification checks PASSED successfully.")

if __name__ == "__main__":
    main()
