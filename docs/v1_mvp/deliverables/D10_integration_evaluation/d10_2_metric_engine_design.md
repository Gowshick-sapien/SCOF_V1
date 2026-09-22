# Deliverable D10.2 — Design and Specification: Evaluation Engine & Metrics Calculator

## 1. Executive Overview

Sub-deliverable **D10.2** establishes the formal scientific evaluation microservice (`services/evaluation/`) within the Supply Chain Cognitive Orchestration Framework (SCOF). The purpose of this service is to quantify decision accuracy, arbitration stability, agent consensus alignment, judge calibration reliability, latency performance, and supply chain risk mitigation across automated multi-agent arbitration runs.

This document formalizes the mathematical specifications, data contracts, architectural integration, and verification plan for the metric calculation engine.

---

## 2. Architectural Positioning

The Evaluation Service operates as an independent microservice containerized on port `8040`, interfaced through the API Gateway on port `8000`:

```
+-------------------------------------------------------------+
|                      Desktop Console                        |
|                  (Evaluation View: Ctrl+7)                  |
+-------------------------------------------------------------+
                               |
                               v (HTTP GET /evaluation/benchmark)
+-------------------------------------------------------------+
|                     API Gateway (:8000)                     |
+-------------------------------------------------------------+
                               |
                               v (HTTP Proxy / Direct Ingest)
+-------------------------------------------------------------+
|               Evaluation Service (Port 8040)               |
|                                                             |
|   +---------------------+        +----------------------+   |
|   |   Harness Engine    | <----> |  Metric Calculators  |   |
|   |    (harness.py)     |        |     (metrics.py)     |   |
|   +---------------------+        +----------------------+   |
|              ^                                              |
|              | Ingests Scenario Bundles & Ground Truth      |
|   +----------------------------------------------------+    |
|   | profiles/mvp-electronics/scenarios/calibration_set |    |
|   +----------------------------------------------------+    |
+-------------------------------------------------------------+
```

---

## 3. Mathematical Metric Formulations

The evaluation engine implements six core metric calculators adhering to SRS Section 20 and the SCOF Scientific Design.

### 3.1. Decision Accuracy (A)
Measures the proportion of arbitration decisions that match the ground-truth mitigation policy established by human supply chain domain experts.

Both exact-match and normalized semantic alignment are supported:

$$A_{\text{exact}} = \frac{1}{N} \sum_{k=1}^{N} \mathbb{I}(y_k = \hat{y}_k)$$

Where:
* $N$ is the total number of evaluated scenarios.
* $y_k$ is the ground-truth mitigation action.
* $\hat{y}_k$ is the recommendation produced by the decision method.
* $\mathbb{I}(\cdot)$ is the indicator function ($\mathbb{I} = 1$ if true, $0$ otherwise).

Normalized matching strips case variations, punctuation, and leading/trailing whitespace to avoid false negatives on cosmetic differences.

### 3.2. Weighted Consensus Stability (WCS)
Quantifies the strength and cohesion of the winning recommendation based on historical agent credibility and situational confidence:

$$\text{WCS} = \frac{\sum_{i \in \mathcal{W}} w_i \cdot c_i}{\sum_{j \in \mathcal{A}} w_j \cdot c_j}$$

Where:
* $\mathcal{W}$ is the subset of specialist agents supporting the winning recommendation.
* $\mathcal{A}$ is the set of all participating specialist agents.
* $w_i \in [0.1, 1.0]$ is the historical domain accuracy weight of agent $i$.
* $c_i \in [0.0, 1.0]$ is the self-reported situational confidence of agent $i$.
* Domain: $\text{WCS} \in [0.0, 1.0]$. A value near $1.0$ indicates decisive consensus; a value below $0.5$ signals heavy inter-agent conflict.

### 3.3. Specialist Agreement Rate (AR)
Calculates the mean pairwise agreement frequency across all participating specialist claims within a scenario bundle:

$$\text{AR} = \frac{2}{M(M - 1)} \sum_{i=1}^{M-1} \sum_{j=i+1}^{M} \mathbb{I}(r_i = r_j)$$

Where:
* $M$ is the number of reporting specialist agents ($M \ge 2$).
* $r_i, r_j$ are the recommendations from agents $i$ and $j$.
* If $M < 2$, $\text{AR} \equiv 1.0$.

### 3.4. Judge Calibration Reliability (Cohen's Kappa, \kappa)
Measures inter-rater agreement between the automated arbitration engine and the human expert ground truth, correcting for agreement occurring by chance:

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

Where:
* $p_o$ is the observed proportionate agreement:
  $$p_o = \frac{1}{N} \sum_{k=1}^{N} \mathbb{I}(y_k = \hat{y}_k)$$
* $p_e$ is the hypothetical probability of chance agreement, computed from the marginal category distributions:
  $$p_e = \sum_{c \in \mathcal{C}} P(y = c) \cdot P(\hat{y} = c)$$
* Evaluated across two independent targets:
  1. **Recommendation Kappa ($\kappa_{\text{rec}}$)**: Action choice reliability.
  2. **Escalation Tier Kappa ($\kappa_{\text{tier}}$)**: Correctness of gating (`FAST_PATH`, `SLOW_PATH`, `HUMAN_ESCALATION`).
* Requirement threshold: $\kappa \ge 0.85$ indicates near-perfect calibration.

### 3.5. Decision Latency Profiling (L)
Tracks execution latency distributions in milliseconds, computing key statistical percentiles:

* **p50 (Median)**: 50th percentile response time.
* **p90**: 90th percentile response time.
* **p95**: 95th percentile response time.
* **p99**: 99th percentile response time.
* **Mean ($\mu$)**: Arithmetic mean latency.

Latency is segmented into two operational pathways:
1. **Fast-Path Latency**: Unanimous or high-confidence consensus scenarios with no severe safety conflicts (Target: $< 500\text{ ms}$).
2. **Slow-Path Latency**: Multi-round deliberative arbitration or conflicting claims requiring extended evidence cross-examination.

### 3.6. Supply Chain Impact Estimators
Estimates expected operational risk reduction based on empirical mitigation efficacy:

* **Stockout Risk Reduction ($\Delta S$)**:
  $$\Delta S = \frac{S_{\text{unmitigated}} - S_{\text{mitigated}}}{S_{\text{unmitigated}}} \times 100\%$$
* **Fill Rate Delta ($\Delta F$)**:
  $$\Delta F = F_{\text{mitigated}} - F_{\text{unmitigated}}$$

---

## 4. Module Specifications

### 4.1. `services/evaluation/src/metrics.py`
Pure functional calculation library implementing:
* `calculate_decision_accuracy(predictions, ground_truth, normalized=True) -> float`
* `calculate_wcs_stability(agent_weights, winning_agents) -> float`
* `calculate_agreement_rate(agent_claims) -> float`
* `calculate_cohens_kappa(predictions, ground_truth) -> float`
* `calculate_latency_percentiles(latencies_ms) -> Dict[str, float]`
* `calculate_stockout_risk_reduction(baseline_risk, post_mitigation_risk) -> float`
* `calculate_fill_rate_delta(baseline_fill_rate, post_mitigation_fill_rate) -> float`

### 4.2. `services/evaluation/src/harness.py`
Evaluation harness coordinator managing:
* `load_calibration_dataset(path: str) -> List[Dict[str, Any]]`: Parses `calibration_set.json` into structured scenario bundles and ground truth pairs.
* `evaluate_dataset(dataset, decision_fn) -> EvaluationRunResult`: Executes decision function against each bundle, collects outputs and latencies, and computes all aggregate metrics.
* `generate_benchmark_summary(results_map) -> BenchmarkSummaryResponse`: Constructs the comparative matrix comparing CD²F, Naive Majority, and Single-Agent.

### 4.3. `services/evaluation/src/main.py`
FastAPI REST application exposing:
* `GET /health`: Health and readiness probe.
* `POST /evaluate/run`: Triggers a synchronous evaluation run over the loaded calibration dataset.
* `GET /benchmark/summary`: Returns the latest comparative benchmark metrics.
* `GET /metrics/calibration`: Detailed Cohen's Kappa and tier classification calibration report.
* `GET /metrics/latency`: Latency percentiles breakdown (overall, fast-path, slow-path).

---

## 5. API Data Contracts

### 5.1. Benchmark Summary Item
```json
{
  "method": "CD2F (Consensus Dynamic Arbitration)",
  "accuracy": 0.942,
  "wcs_stability": 0.887,
  "latency_p50_ms": 320.5,
  "latency_p90_ms": 485.0,
  "latency_p95_ms": 525.0,
  "cohens_kappa": 0.912,
  "stockout_reduction_pct": 38.4,
  "fill_rate_delta": 0.125,
  "sample_count": 50
}
```

### 5.2. Calibration Report
```json
{
  "evaluation_id": "eval-20260904-01",
  "dataset": "mvp-electronics/calibration_set.json",
  "sample_count": 50,
  "recommendation_kappa": 0.912,
  "escalation_tier_kappa": 0.894,
  "agreement_rate_mean": 0.782,
  "status": "VALIDATED"
}
```

---

## 6. Verification and Acceptance Criteria

1. **Unit Test Coverage**:
   * All functions in `metrics.py` must have unit tests covering normal inputs, edge conditions (empty lists, single inputs, zero variance), and error cases.
   * Tests run via `python -m pytest services/evaluation/tests/test_metrics.py -v`.
2. **Harness Integration Test**:
   * `harness.py` successfully loads all scenarios from `profiles/mvp-electronics/scenarios/calibration_set.json`.
   * Evaluator executes without exceptions and produces non-null, bounded metrics ($[0.0, 1.0]$ for accuracy, WCS, agreement rate, kappa).
   * Tests run via `python -m pytest services/evaluation/tests/test_harness.py -v`.
3. **REST Endpoint Validation**:
   * `curl -s http://localhost:8040/health` returns status `ok`.
   * `curl -s http://localhost:8040/benchmark/summary` returns complete benchmark comparative matrix.
   * `curl -s http://localhost:8040/metrics/calibration` returns valid Cohen's Kappa score $\ge 0.85$.
