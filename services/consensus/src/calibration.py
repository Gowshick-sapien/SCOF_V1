import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from sklearn.metrics import cohen_kappa_score
import warnings

from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.profile.consensus_config import ConsensusConfig
from services.consensus.src.engine import run_consensus
from services.consensus.src.accuracy_tracker import AccuracyTracker
from services.consensus.src.config import logger

class GroundTruthLabel(BaseModel):
    expected_recommendation: str
    expected_escalation_tier: str
    reasoning: str

class CalibrationScenario(BaseModel):
    bundle: ClaimBundle
    ground_truth: GroundTruthLabel

class CalibrationReport(BaseModel):
    recommendation_kappa: float | None
    escalation_tier_kappa: float | None
    exact_match_rate: float
    confusion_breakdown: Dict[str, Any]
    sample_size: int
    pass_status: bool
    warnings: List[str]

def load_calibration_set(path: Path) -> List[CalibrationScenario]:
    if not path.exists():
        raise FileNotFoundError(f"Calibration set not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CalibrationScenario(**item) for item in data]

def run_calibration(
    calibration_set_path: Path, 
    config: ConsensusConfig, 
    tracker: AccuracyTracker
) -> CalibrationReport:
    scenarios = load_calibration_set(calibration_set_path)
    sample_size = len(scenarios)
    
    warnings_list = []
    if sample_size < 5:
        warnings_list.append("Insufficient calibration set size (fewer than 5 scenarios). Kappa may be unreliable.")

    y_rec_true = []
    y_rec_pred = []
    
    y_esc_true = []
    y_esc_pred = []
    
    exact_matches = 0

    for scenario in scenarios:
        # Run engine (does not mutate production accuracy)
        decision = run_consensus(scenario.bundle, config, tracker)
        
        expected_rec = scenario.ground_truth.expected_recommendation
        pred_rec = decision.final_recommendation or "None"
        
        expected_esc = scenario.ground_truth.expected_escalation_tier
        pred_esc = decision.escalation_tier
        
        y_rec_true.append(expected_rec)
        y_rec_pred.append(pred_rec)
        
        y_esc_true.append(expected_esc)
        y_esc_pred.append(pred_esc)
        
        if expected_rec == pred_rec and expected_esc == pred_esc:
            exact_matches += 1

    # Compute Kappa
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            rec_kappa = cohen_kappa_score(y_rec_true, y_rec_pred)
            if str(rec_kappa) == "nan":
                rec_kappa = None
                warnings_list.append("Recommendation kappa is undefined (likely single-class sample).")
        except Exception:
            rec_kappa = None
            warnings_list.append("Failed to compute recommendation kappa.")
            
        try:
            esc_kappa = cohen_kappa_score(y_esc_true, y_esc_pred)
            if str(esc_kappa) == "nan":
                esc_kappa = None
                warnings_list.append("Escalation tier kappa is undefined (likely single-class sample).")
        except Exception:
            esc_kappa = None
            warnings_list.append("Failed to compute escalation tier kappa.")

    exact_match_rate = exact_matches / sample_size if sample_size > 0 else 0.0
    
    # Check pass status
    pass_status = True
    if sample_size < 5:
        pass_status = False
    if rec_kappa is None or rec_kappa < config.calibration.min_kappa:
        pass_status = False
    if esc_kappa is None or esc_kappa < config.calibration.min_kappa:
        pass_status = False

    # Confusion breakdown logic
    confusion = {
        "recommendation_classes_true": list(set(y_rec_true)),
        "recommendation_classes_pred": list(set(y_rec_pred)),
        "escalation_classes_true": list(set(y_esc_true)),
        "escalation_classes_pred": list(set(y_esc_pred))
    }

    return CalibrationReport(
        recommendation_kappa=rec_kappa,
        escalation_tier_kappa=esc_kappa,
        exact_match_rate=exact_match_rate,
        confusion_breakdown=confusion,
        sample_size=sample_size,
        pass_status=pass_status,
        warnings=warnings_list
    )
