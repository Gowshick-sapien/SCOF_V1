from typing import List, Dict, Any, Union, Set
import numpy as np
from sklearn.metrics import cohen_kappa_score


def _normalize_string(val: str) -> str:
    """Normalize string by trimming whitespace and lowercasing."""
    if not isinstance(val, str):
        val = str(val)
    return " ".join(val.strip().lower().split())


def calculate_decision_accuracy(
    predictions: List[str],
    ground_truth: List[str],
    normalized: bool = True
) -> float:
    """Calculate overall accuracy matching ground truth mitigations.
    
    Args:
        predictions: List of model/arbitration recommendations.
        ground_truth: List of ground-truth mitigation recommendations.
        normalized: If True, performs whitespace and case-insensitive comparison.
        
    Returns:
        Float in range [0.0, 1.0]. Returns 0.0 if lists are empty or mismatched.
    """
    if not predictions or not ground_truth or len(predictions) != len(ground_truth):
        return 0.0

    if normalized:
        correct = sum(
            1 for p, g in zip(predictions, ground_truth)
            if _normalize_string(p) == _normalize_string(g)
        )
    else:
        correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)

    return float(correct / len(predictions))


def calculate_wcs_stability(
    agent_weights: Dict[str, float],
    winning_agents: Union[List[str], Set[str]]
) -> float:
    """Calculate Weighted Consensus Stability (WCS).
    
    Formula:
        WCS = sum(weights of winning agents) / sum(weights of all participating agents)
        
    Args:
        agent_weights: Mapping of agent_id to effective weight (weight * confidence).
        winning_agents: Collection of agent IDs supporting the winning recommendation.
        
    Returns:
        Float in range [0.0, 1.0]. Returns 1.0 for single-agent or empty denominators.
    """
    if not agent_weights:
        return 1.0

    total_weight = sum(agent_weights.values())
    if total_weight <= 0.0:
        return 0.0

    winning_set = set(winning_agents)
    winning_weight = sum(
        weight for agent_id, weight in agent_weights.items()
        if agent_id in winning_set
    )

    stability = winning_weight / total_weight
    return float(min(max(stability, 0.0), 1.0))


def calculate_agreement_rate(agent_claims: Union[List[Dict[str, Any]], Dict[str, Any]]) -> float:
    """Calculate pairwise agent recommendation agreement rate across specialist claims.
    
    Args:
        agent_claims: List of claim dicts or dict mapping agent_id to claim dict.
        
    Returns:
        Float in range [0.0, 1.0]. Returns 1.0 if fewer than 2 claims exist.
    """
    if isinstance(agent_claims, dict):
        claims_list = list(agent_claims.values())
    else:
        claims_list = agent_claims

    if not claims_list or len(claims_list) < 2:
        return 1.0

    recommendations: List[str] = []
    for claim in claims_list:
        if isinstance(claim, dict):
            rec = claim.get("recommendation") or claim.get("action") or ""
        else:
            rec = getattr(claim, "recommendation", None) or getattr(claim, "action", "")
        recommendations.append(_normalize_string(rec))

    total_pairs = 0
    agreeing_pairs = 0
    num_claims = len(recommendations)

    for i in range(num_claims):
        for j in range(i + 1, num_claims):
            total_pairs += 1
            if recommendations[i] == recommendations[j]:
                agreeing_pairs += 1

    return float(agreeing_pairs / total_pairs) if total_pairs > 0 else 1.0


def calculate_cohens_kappa(rater_a: List[str], rater_b: List[str]) -> float:
    """Calculate Cohen's kappa score for inter-rater calibration reliability.
    
    Args:
        rater_a: List of predictions/evaluations from rater A.
        rater_b: List of ground-truth/evaluations from rater B.
        
    Returns:
        Float in range [-1.0, 1.0]. Bounded to 0.0 on zero-variance or invalid inputs.
    """
    if not rater_a or not rater_b or len(rater_a) != len(rater_b):
        return 0.0

    norm_a = [_normalize_string(x) for x in rater_a]
    norm_b = [_normalize_string(x) for x in rater_b]

    # Handle edge case: single unique class and complete agreement
    if set(norm_a) == set(norm_b) and len(set(norm_a)) == 1:
        return 1.0

    try:
        kappa = cohen_kappa_score(norm_a, norm_b)
        if np.isnan(kappa):
            # If all ratings are identical between raters
            if norm_a == norm_b:
                return 1.0
            return 0.0
        return float(kappa)
    except Exception:
        return 0.0


def calculate_latency_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculate p50, p90, p95, p99, and mean response time percentiles in milliseconds.
    
    Args:
        latencies: List of latency measurements in milliseconds.
        
    Returns:
        Dictionary containing p50, p90, p95, p99, and mean.
    """
    if not latencies:
        return {
            "p50": 0.0,
            "p90": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "mean": 0.0
        }

    sorted_lats = sorted(latencies)
    n = len(sorted_lats)

    def _get_pct(p: float) -> float:
        idx = int(n * p)
        return float(sorted_lats[min(idx, n - 1)])

    return {
        "p50": _get_pct(0.50),
        "p90": _get_pct(0.90),
        "p95": _get_pct(0.95),
        "p99": _get_pct(0.99),
        "mean": float(sum(sorted_lats) / n)
    }


def calculate_stockout_risk_reduction(baseline_risk: float, post_mitigation_risk: float) -> float:
    """Calculate percentage reduction in stockout risk following mitigation.
    
    Args:
        baseline_risk: Baseline probability/level of stockout before mitigation (e.g. 0.45).
        post_mitigation_risk: Evaluated probability/level of stockout after mitigation (e.g. 0.15).
        
    Returns:
        Percentage reduction in range [0.0, 100.0].
    """
    if baseline_risk <= 0.0:
        return 0.0
    delta = baseline_risk - post_mitigation_risk
    reduction = (delta / baseline_risk) * 100.0
    return float(max(reduction, 0.0))


def calculate_fill_rate_delta(baseline_fill_rate: float, post_mitigation_fill_rate: float) -> float:
    """Calculate absolute delta increase in service fill rate.
    
    Args:
        baseline_fill_rate: Fill rate before mitigation (e.g. 0.82).
        post_mitigation_fill_rate: Fill rate after mitigation (e.g. 0.95).
        
    Returns:
        Signed float difference (positive indicates improvement).
    """
    return float(post_mitigation_fill_rate - baseline_fill_rate)
