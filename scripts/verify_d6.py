import json
import os
import sys
from pathlib import Path
from colorama import init, Fore, Style

# Add root to python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from scof_shared.profile.loader import load_profile
from scof_shared.schemas.claim_bundle import ClaimBundle
from services.consensus.src.config import SCOF_PROFILE_PATH, ACCURACY_STORE_PATH
from services.consensus.src.accuracy_tracker import AccuracyTracker
from services.consensus.src.engine import run_consensus
from services.consensus.src.calibration import run_calibration

init(autoreset=True)

def verify():
    print(Fore.CYAN + "=== CD2F Consensus Engine Verification (D6) ===")
    
    try:
        profile = load_profile(SCOF_PROFILE_PATH)
        print(Fore.GREEN + f"Loaded profile: {profile.meta.name} v{profile.meta.version}")
        if not profile.consensus:
            print(Fore.RED + "ERROR: Profile missing consensus configuration!")
            sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"Failed to load profile: {e}")
        sys.exit(1)
        
    tracker = AccuracyTracker(
        store_path=ACCURACY_STORE_PATH,
        window_size=profile.consensus.accuracy.window_size,
        default_accuracy=profile.consensus.accuracy.default_accuracy
    )
    
    fixtures_dir = Path("services/consensus/fixtures")
    cases = [
        ("Agreement Case", "agreement_case.json", "FAST_PATH"),
        ("Disagreement Case", "disagreement_case.json", "SLOW_PATH"),
        ("Conflicting Evidence Case", "conflicting_evidence_case.json", "HUMAN_ESCALATION"),
        ("Partial Bundle Case", "partial_bundle_case.json", "HUMAN_ESCALATION")
    ]
    
    print("\n" + Fore.CYAN + "--- Running Fixture Tests ---")
    all_passed = True
    
    for case_name, filename, expected_tier in cases:
        print(f"\n{Style.BRIGHT}{case_name}:")
        filepath = fixtures_dir / filename
        if not filepath.exists():
            print(Fore.YELLOW + f"  [SKIP] Fixture {filename} not found.")
            all_passed = False
            continue
            
        with open(filepath, "r") as f:
            data = json.load(f)
            
        bundle = ClaimBundle(**data)
        
        try:
            decision = run_consensus(bundle, profile.consensus, tracker)
            tier = decision.escalation_tier
            
            if tier == expected_tier:
                print(Fore.GREEN + f"  [PASS] Escalation Tier: {tier} (Expected: {expected_tier})")
                print(Fore.WHITE + f"  Recommendation: {decision.final_recommendation}")
                print(Fore.WHITE + f"  WCS: {decision.weighted_consensus_stability:.2f}")
                print(Fore.WHITE + f"  Decision Method: {decision.decision_method}")
            else:
                print(Fore.RED + f"  [FAIL] Escalation Tier: {tier} (Expected: {expected_tier})")
                print(Fore.RED + f"  Rationale: {decision.escalation_rationale}")
                all_passed = False
        except Exception as e:
            print(Fore.RED + f"  [ERROR] {e}")
            all_passed = False
            
    print("\n" + Fore.CYAN + "--- Running Judge Calibration ---")
    calib_path = Path("profiles/mvp-electronics/scenarios/calibration_set.json")
    if calib_path.exists():
        try:
            report = run_calibration(calib_path, profile.consensus, tracker)
            print(f"Sample Size: {report.sample_size}")
            print(f"Recommendation Kappa: {report.recommendation_kappa}")
            print(f"Escalation Tier Kappa: {report.escalation_tier_kappa}")
            print(f"Exact Match Rate: {report.exact_match_rate:.2f}")
            for w in report.warnings:
                print(Fore.YELLOW + f"Warning: {w}")
                
            if report.pass_status:
                print(Fore.GREEN + "[PASS] Calibration met requirements.")
            else:
                print(Fore.RED + "[FAIL] Calibration failed requirements.")
                all_passed = False
        except Exception as e:
            print(Fore.RED + f"[ERROR] Calibration failed: {e}")
            all_passed = False
    else:
        print(Fore.YELLOW + f"[SKIP] Calibration set not found at {calib_path}")
        
    print("\n" + Fore.CYAN + "=== Verification Summary ===")
    if all_passed:
        print(Fore.GREEN + Style.BRIGHT + "SUCCESS: All D6 components verified.")
        sys.exit(0)
    else:
        print(Fore.RED + Style.BRIGHT + "FAILURE: One or more D6 components failed verification.")
        sys.exit(1)

if __name__ == "__main__":
    verify()
