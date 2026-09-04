# Deliverable D10.4 — Design and Specification: Automated Multi-Scenario Benchmark Suite & Desktop Live Sync

## 1. Executive Summary

Sub-deliverable **D10.4** establishes the **Automated Multi-Scenario Benchmark Suite & Desktop Live Sync** within the Supply Chain Cognitive Orchestration Framework (SCOF). Building on the evaluation service (D10.2) and baseline comparator (D10.3), D10.4 expands scenario evaluation into a comprehensive multi-category benchmark suite across the 4 core supply chain disruption categories and establishes full bidirectional live data synchronization with the **Desktop Operations Console** (`Ctrl + 7`).

This deliverable bridges backend scientific evaluation directly into the Tauri operator desktop experience, enabling interactive benchmark execution, live metric inspection, category performance breakdown, and real-time SLA compliance audits.

---

## 2. Multi-Scenario Disruption Coverage

The benchmark suite systematically evaluates multi-agent arbitration across all four canonical disruption categories defined in SRS Section 3:

```
+---------------------------------------------------------------------------------+
|                       Multi-Category Disruption Suite                           |
+--------------------+--------------------+-------------------+-------------------+
|  1. Supplier Delay | 2. Transport Break |  3. Demand Spike  | 4. Adverse Weather|
+--------------------+--------------------+-------------------+-------------------+
| - Yield shortfall  | - Port congestion  | - Unforecasted    | - Hurricane storm |
| - Raw material lag | - Route blockade   |   order surge     |   grounding air   |
| - Quality hold     | - Carrier outage   | - Promotional run | - Blizzard rail   |
+--------------------+--------------------+-------------------+-------------------+
```

### 2.1. Disruption Archetypes & Conflict Profiles
Each category tests three distinct conflict profiles:
1. **Unanimous Alignment (Low Conflict)**:
   * All specialist agents agree on the optimal mitigation.
   * Tests autonomous `FAST_PATH` resolution with low latency ($< 500\text{ ms}$) and zero human intervention.
2. **Specialist Divergence (Moderate Conflict)**:
   * Inventory and supplier agents propose divergent actions based on localized trade-offs.
   * Tests CD²F cross-domain evidence weighting and escalation to `SLOW_PATH`.
3. **Severe Conflict & Safety Anomaly (High Conflict)**:
   * Unresolved trade-offs involving severe financial exposure or high stockout risk.
   * Tests safety gating into `HUMAN_ESCALATION` without artificial tie-breaking.

---

## 3. Mathematical Category-Level Metric Formulations

In addition to system-wide metrics, D10.4 computes category-stratified performance:

### 3.1. Category Decision Accuracy ($A_c$)
$$\text{Accuracy}_c = \frac{1}{N_c} \sum_{k \in \mathcal{S}_c} \mathbb{I}(y_k = \hat{y}_k)$$
Where $\mathcal{S}_c$ is the subset of scenarios belonging to disruption category $c \in \{\text{Supplier}, \text{Transportation}, \text{Demand}, \text{Weather}\}$.

### 3.2. Category Consensus Stability ($\text{WCS}_c$)
$$\text{WCS}_c = \frac{1}{N_c} \sum_{k \in \mathcal{S}_c} \text{WCS}_k$$

### 3.3. Conflict Intensity Index ($\text{CII}_c$)
Measures the average rate of inter-agent recommendation divergence within each category:
$$\text{CII}_c = 1.0 - \text{AR}_c$$
Where $\text{AR}_c$ is the mean specialist agreement rate for category $c$. A high $\text{CII}$ indicates complex multi-variable disruptions requiring slow-path arbitration.

---

## 4. Desktop Live Synchronization Architecture

The Desktop Operations Console connects directly to the API Gateway to render live benchmark data:

```
+-----------------------------------------------------------------------------------+
|                    Desktop Console (Tauri v2 + React 19)                          |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   |                  Evaluation View (EvaluationView.tsx)                     |   |
|   |  - Comparative Matrix (CD2F vs Naive Majority vs Single Agent)            |   |
|   |  - Live KPI Cards (Inter-Agent Kappa, Fast-Path P90, Stockout Reduction)  |   |
|   |  - Category Breakdown Matrix (Supplier, Transport, Demand, Weather)       |   |
|   |  - Interactive "Re-run Benchmark" Action with Loading State               |   |
|   +---------------------------------------------------------------------------+   |
|                                        ^                                          |
|                                        | HTTP REST (React Hook: useEffect)        |
|                                        v                                          |
|   +---------------------------------------------------------------------------+   |
|   |                       Desktop API Client (client.ts)                      |   |
|   |  - apiClient.getBenchmark(): Promise<BenchmarkSummaryResponse>            |   |
|   |  - apiClient.getCategoryMetrics(): Promise<CategoryMetricsResponse>       |   |
|   |  - apiClient.runEvaluation(): Promise<BenchmarkSummaryResponse>           |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v HTTP GET/POST (Proxy)
+-----------------------------------------------------------------------------------+
|                            API Gateway (:8000)                                    |
|   - GET /evaluation/benchmark                                                     |
|   - GET /evaluation/categories                                                    |
|   - POST /evaluation/run                                                          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v HTTP Internal
+-----------------------------------------------------------------------------------+
|                        Evaluation Service (:8040)                                 |
|   - Ingests Expanded Multi-Scenario Benchmark Dataset                             |
|   - Computes Real-Time Metrics & Category Aggregates                              |
+-----------------------------------------------------------------------------------+
```

---

## 5. API Data Contracts

### 5.1. Category Breakdown Response (`GET /evaluation/categories`)
```json
{
  "dataset_name": "profiles/mvp-electronics/scenarios/benchmark_suite.json",
  "total_scenarios": 20,
  "categories": [
    {
      "category": "SUPPLIER_DELAY",
      "scenario_count": 5,
      "accuracy": 0.960,
      "wcs_stability": 0.892,
      "latency_p50_ms": 340.0,
      "conflict_intensity": 0.320,
      "fast_path_pct": 60.0
    },
    {
      "category": "TRANSPORTATION_FAILURE",
      "scenario_count": 5,
      "accuracy": 0.940,
      "wcs_stability": 0.880,
      "latency_p50_ms": 360.0,
      "conflict_intensity": 0.380,
      "fast_path_pct": 40.0
    },
    {
      "category": "DEMAND_SPIKE",
      "scenario_count": 5,
      "accuracy": 0.920,
      "wcs_stability": 0.865,
      "latency_p50_ms": 380.0,
      "conflict_intensity": 0.450,
      "fast_path_pct": 40.0
    },
    {
      "category": "ADVERSE_WEATHER",
      "scenario_count": 5,
      "accuracy": 0.950,
      "wcs_stability": 0.910,
      "latency_p50_ms": 320.0,
      "conflict_intensity": 0.250,
      "fast_path_pct": 80.0
    }
  ],
  "status": "VALIDATED"
}
```

---

## 6. Implementation Components

### 6.1. Dataset Expansion
* Create [`profiles/mvp-electronics/scenarios/benchmark_suite.json`](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/scenarios/benchmark_suite.json):
  Comprehensive multi-category benchmark suite containing 20 scenario bundles (5 scenarios per category) covering diverse severity and conflict levels with calibrated ground truth recommendations.

### 6.2. Multi-Scenario Category Evaluator
* Update [`services/evaluation/src/harness.py`](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/src/harness.py) and [`services/evaluation/src/main.py`](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/src/main.py):
  * Add category extraction and stratification logic.
  * Add endpoint `GET /benchmark/categories`.
  * Support running evaluations against `benchmark_suite.json`.

### 6.3. API Gateway Proxy Integration
* Update [`services/api/src/routers/evaluation.py`](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/evaluation.py):
  * Add `GET /evaluation/categories`.

### 6.4. Desktop Console Live Data Binding
* Update [`desktop/src/api/client.ts`](file:///d:/projects/SCOF_V1/SCOF/desktop/src/api/client.ts):
  * Add `getBenchmark()`, `getCategoryMetrics()`, and `runEvaluation()`.
* Update [`desktop/src/views/Evaluation/EvaluationView.tsx`](file:///d:/projects/SCOF_V1/SCOF/desktop/src/views/Evaluation/EvaluationView.tsx):
  * Replace static constants with dynamic `useState` and `useEffect` hooks.
  * Add live "Re-run Benchmark" action with spinner.
  * Add Category Performance Breakdown table.
  * Dynamically populate KPI cards (Kappa, P90, Stockout Reduction).

---

## 7. Verification and Acceptance Criteria

1. **Automated Test Suite**:
   * Unit tests verifying multi-scenario category loader and metric calculation.
   * `python -m pytest services/evaluation/tests/test_multi_scenario_suite.py -v`.
2. **REST API Verification**:
   * `GET http://localhost:8040/benchmark/categories` returns all 4 disruption categories.
   * `GET http://localhost:8000/evaluation/categories` proxies successfully.
3. **Desktop Operations Console Verification**:
   * Launch Tauri app (`cmd /c npm run tauri dev`).
   * Navigate to `Ctrl + 7`.
   * Verify dynamic data loading from the backend.
   * Click "Re-run Benchmark" and confirm live re-evaluation updates without page reload.
