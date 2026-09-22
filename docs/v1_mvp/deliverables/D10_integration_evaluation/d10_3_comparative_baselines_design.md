# Deliverable D10.3 — Design and Specification: Comparative Baseline Benchmarking Engine

## 1. Executive Summary

Sub-deliverable **D10.3** establishes the **Comparative Baseline Benchmarking Engine** within the Supply Chain Cognitive Orchestration Framework (SCOF). The primary objective is to execute a rigorous, side-by-side scientific benchmark comparing the **Consensus-Driven Collaborative Decision Framework (CD²F)** against two established arbitration baselines:
1. **Single-Agent Specialist (Isolated Greedy Baseline)**: Evaluates decision quality when relying exclusively on the single specialist agent that reports the highest raw confidence, ignoring corroborating or conflicting domain evidence.
2. **Naive Majority Voting (Democratic Unweighted Baseline)**: Evaluates decision quality under standard democratic tallying where each agent receives equal vote weighting ($1.0$), with alphabetical tie-breaking on deadlocks.
3. **CD²F Engine (Proposed Framework)**: Combines normalized claims, historical domain credibility priors, situational confidence weighting, and risk-gated escalation tiering.

This document formalizes the algorithmic specifications, comparative metrics (Pairwise Discordance Rate, Tie-Breaker Frequency, Escalation Gating Fidelity), data contracts, CLI tooling, and verification procedures.

---

## 2. Architectural Positioning

The Comparative Baseline Benchmarking Engine connects the consensus algorithms implemented in `services/consensus/src/baselines/` with the evaluation service in `services/evaluation/`:

```
+---------------------------------------------------------------------------------+
|                       Evaluation Service (:8040)                                |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                 Benchmark Runner (benchmark_runner.py)                   |   |
|   |  - Iterates over ClaimBundles from calibration_set.json                 |   |
|   |  - Executes identical inputs across all 3 decision methods              |   |
|   |  - Computes Discordance, Tie-Breaking Rate, Accuracy & Latency          |   |
|   +-------------------------------------------------------------------------+   |
|            |                           |                           |            |
|            v                           v                           v            |
|   +-----------------+         +-----------------+         +-----------------+   |
|   |   CD2F Engine   |         | Naive Majority  |         |  Single Agent   |   |
|   |   (engine.py)   |         | (naive_majority)|         | (single_agent)  |   |
|   +-----------------+         +-----------------+         +-----------------+   |
|            |                           |                           |            |
|            +---------------------------+---------------------------+            |
|                                        |                                        |
|                                        v                                        |
|   +-------------------------------------------------------------------------+   |
|   |                 Comparative Metrics & Report Generation                 |   |
|   |  - Pairwise Discordance Rate (PDR)                                      |   |
|   |  - Tie-Breaker Frequency (TBR)                                          |   |
|   |  - Escalation Gating Fidelity (Cohen's Kappa on Tiers)                  |   |
|   |  - Comparative Matrix (Accuracy, Stability, Latency, Escalation)        |   |
|   +-------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------+
```

---

## 3. Algorithmic Specifications of Evaluated Methods

### 3.1. Method 1: CD²F (Consensus-Driven Collaborative Decision Framework)
* **Mathematical Basis**:
  Each agent $i \in \mathcal{A}$ provides a recommendation $r_i$ and confidence $c_i \in [0.0, 1.0]$. The engine weights each claim by the agent's historical domain accuracy prior $w_i \in [0.1, 1.0]$:
  $$\text{Effective Weight: } W_i = w_i \cdot c_i$$
  For each distinct recommendation $R$:
  $$\text{Score}(R) = \sum_{i: r_i = R} W_i$$
  $$\text{Winning Recommendation: } R^* = \arg\max_{R} \text{Score}(R)$$
  $$\text{Weighted Consensus Stability (WCS): } \text{WCS} = \frac{\text{Score}(R^*)}{\sum_{j \in \mathcal{A}} W_j}$$
* **Escalation Gating**:
  Dynamically maps stability to escalation tiers based on risk profile:
  * $\text{WCS} \ge 0.80$ and agreement $\to \text{FAST\_PATH}$
  * $0.55 \le \text{WCS} < 0.80$ or moderate conflict $\to \text{SLOW\_PATH}$
  * $\text{WCS} < 0.55$ or severe hazard $\to \text{HUMAN\_ESCALATION}$

### 3.2. Method 2: Naive Majority Voting (Baseline)
* **Mathematical Basis**:
  Treats all reporting agents equally regardless of domain credibility or confidence:
  $$\text{Score}_{\text{naive}}(R) = \sum_{i: r_i = R} 1$$
  $$\text{Winning Recommendation: } R^*_{\text{naive}} = \arg\max_{R} \text{Score}_{\text{naive}}(R)$$
* **Tie-Breaking Mode**:
  When two or more recommendations share the maximum vote count:
  $$R^*_{\text{tied}} = \min_{\text{alphabetical}} \{ R : \text{Score}_{\text{naive}}(R) = \max_k \text{Score}_{\text{naive}}(k) \}$$
  This deliberately exposes the failure mode where unweighted voting randomly selects arbitrary actions on evenly split agent panels.
* **Escalation Gating**:
  Static assignment to `SLOW_PATH` (cannot differentiate between unanimous agreement and deadlock).

### 3.3. Method 3: Single-Agent Specialist (Baseline)
* **Mathematical Basis**:
  Emulates an isolated system without cross-domain consensus, greedily trusting the agent with the highest self-reported confidence:
  $$i^* = \arg\max_{i \in \mathcal{A}} c_i$$
  $$R^*_{\text{single}} = r_{i^*}$$
* **Failure Vulnerability**:
  Exposes the platform to local agent hallucinations or skewed confidence when an agent lacks cross-functional visibility (e.g. inventory agent recommending immediate fulfillment while supplier agent possesses unobserved disruption signals).
* **Escalation Gating**:
  Trivially selects `FAST_PATH` because it considers only a single agent's perspective.

---

## 4. Comparative Metrics Formulations

In addition to standard Decision Accuracy and Latency, the benchmarking engine calculates specialized comparative metrics:

### 4.1. Pairwise Discordance Rate (PDR)
Measures the frequency with which a baseline method produces a recommendation that diverges from the CD²F engine:

$$\text{PDR}(M, \text{CD}^2\text{F}) = \frac{1}{N} \sum_{k=1}^{N} \mathbb{I}\left(\hat{y}_k^M \ne \hat{y}_k^{\text{CD}^2\text{F}}\right)$$

Where:
* $M \in \{\text{Naive Majority}, \text{Single Agent}\}$.
* High discordance in complex scenarios illustrates where multi-agent weighted arbitration overrides naive votes.

### 4.2. Tie-Breaker Frequency (TBR)
Quantifies the vulnerability of unweighted voting to deadlock:

$$\text{TBR} = \frac{1}{N} \sum_{k=1}^{N} \mathbb{I}\left(|\{ R : \text{Score}(R) = \max \}| > 1\right)$$

CD²F virtually eliminates arbitrary tie-breaking due to continuous real-valued weight multipliers ($W_i = w_i \cdot c_i$).

### 4.3. Escalation Gating Fidelity
Measures inter-rater reliability of escalation tier assignment against human expert ground truth using Cohen's Kappa ($\kappa_{\text{tier}}$):
* CD²F Target: $\kappa_{\text{tier}} \ge 0.85$
* Baselines: Expected low or near-zero $\kappa_{\text{tier}}$ due to static tier assignments.

---

## 5. Module & File Architecture

### 5.1. `services/evaluation/src/benchmark_runner.py`
The core comparative benchmarking engine containing:
* `run_benchmark_comparison(dataset_path: Optional[str] = None) -> BenchmarkComparisonReport`:
  Executes all three decision methods across all scenario bundles in the calibration dataset.
* `compare_single_bundle(bundle: ClaimBundle, ground_truth: Optional[Dict[str, Any]] = None) -> BundleComparisonResult`:
  Executes on-demand comparative arbitration for a single ClaimBundle.
* Command-line interface (`__main__` entrypoint) for standalone execution with table formatting and JSON export.

### 5.2. `services/evaluation/src/main.py`
Exposes the comparative benchmarking engine via REST endpoints:
* `GET /benchmark/baselines`: Returns detailed side-by-side performance metrics, discordance rates, and tie-breaker statistics.
* `POST /benchmark/compare`: Takes an arbitrary ClaimBundle payload and returns the decision outputs from all 3 methods simultaneously.

### 5.3. `services/api/src/routers/evaluation.py`
API Gateway router updates to forward comparative endpoints:
* `GET /evaluation/baselines` $\to$ `http://evaluation:8040/benchmark/baselines`
* `POST /evaluation/compare` $\to$ `http://evaluation:8040/benchmark/compare`

---

## 6. API Data Contracts

### 6.1. Baseline Comparison Report (`GET /benchmark/baselines`)
```json
{
  "report_id": "report-d10-3-20260904",
  "dataset_name": "profiles/mvp-electronics/scenarios/calibration_set.json",
  "scenario_count": 50,
  "methods": [
    {
      "method_name": "CD2F (Consensus Dynamic Arbitration)",
      "accuracy": 0.942,
      "wcs_stability": 0.887,
      "latency_p50_ms": 330.0,
      "cohens_kappa_rec": 0.912,
      "cohens_kappa_tier": 0.894,
      "tie_breaker_rate": 0.0,
      "human_escalation_rate": 14.2
    },
    {
      "method_name": "Naive Majority Voting",
      "accuracy": 0.784,
      "wcs_stability": 0.710,
      "latency_p50_ms": 285.0,
      "cohens_kappa_rec": 0.640,
      "cohens_kappa_tier": 0.0,
      "tie_breaker_rate": 22.4,
      "human_escalation_rate": 0.0
    },
    {
      "method_name": "Single Specialist Agent",
      "accuracy": 0.625,
      "wcs_stability": 0.650,
      "latency_p50_ms": 185.0,
      "cohens_kappa_rec": 0.450,
      "cohens_kappa_tier": 0.0,
      "tie_breaker_rate": 0.0,
      "human_escalation_rate": 0.0
    }
  ],
  "discordance": {
    "naive_majority_vs_cd2f": 0.240,
    "single_agent_vs_cd2f": 0.380
  },
  "status": "VALIDATED"
}
```

---

## 7. Verification and Test Plan

1. **Automated Unit & Integration Tests**:
   * Create `services/evaluation/tests/test_benchmark_runner.py`:
     * Test execution of all three methods against identical bundles.
     * Test tie-breaker rate calculation when votes are deliberately tied.
     * Test pairwise discordance rate calculation on differing recommendations.
     * Test single-bundle on-demand comparison.
2. **CLI Runner Verification**:
   * Execute `python -m services.evaluation.src.benchmark_runner` and verify formatted table output and JSON export file.
3. **Containerized REST Endpoint Verification**:
   * Call `GET http://localhost:8040/benchmark/baselines`.
   * Call `POST http://localhost:8040/benchmark/compare`.
   * Call `GET http://localhost:8000/evaluation/baselines` via API Gateway.
