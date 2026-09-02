from typing import List, Dict, Any
from sklearn.metrics import cohen_kappa_score


def calculate_decision_accuracy(predictions: List[str], ground_truth: List[str]) -> float:
    """Calculate overall accuracy matching ground truth mitigations."""
    if not predictions or not ground_truth or len(predictions) != len(ground_truth):
        return 0.0
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    return float(correct / len(predictions))


def calculate_agreement_rate(agent_claims: List[Dict[str, Any]]) -> float:
    """Calculate pairwise agent recommendation agreement rate."""
    if len(agent_claims) < 2:
        return 1.0
    recommendations = [c.get("action", "") for c in agent_claims]
    total_pairs = 0
    agreeing_pairs = 0
    for i in range(len(recommendations)):
        for j in range(i + 1, len(recommendations)):
            total_pairs += 1
            if recommendations[i] == recommendations[j]:
                agreeing_pairs += 1
    return float(agreeing_pairs / total_pairs) if total_pairs > 0 else 1.0


def calculate_cohens_kappa(rater_a: List[str], rater_b: List[str]) -> float:
    """Calculate Cohen's kappa score for inter-rater calibration reliability."""
    if not rater_a or not rater_b or len(rater_a) != len(rater_b):
        return 0.0
    try:
        return float(cohen_kappa_score(rater_a, rater_b))
    except Exception:
        return 0.0


def calculate_latency_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculate p50, p90, and p99 response time percentiles in milliseconds."""
    if not latencies:
        return {"p50": 0.0, "p90": 0.0, "p99": 0.0, "mean": 0.0}
    sorted_lats = sorted(latencies)
    n = len(sorted_lats)
    return {
        "p50": sorted_lats[int(n * 0.50)],
        "p90": sorted_lats[min(int(n * 0.90), n - 1)],
        "p99": sorted_lats[min(int(n * 0.99), n - 1)],
        "mean": sum(sorted_lats) / n,
    }
