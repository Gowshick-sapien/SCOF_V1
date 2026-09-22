# Deliverable D10 (V2): Scientific Benchmarking & Evaluation Suite

## 1. Overview & Objectives

Deliverable D10 replaces the rudimentary test assertions of V1 with an enterprise-grade, publication-ready **Scientific Benchmarking & Evaluation Suite**. The suite empirically measures the efficacy of the SCOF Multi-Agent Cognitive Twin against three competitive baselines across 20 canonical disruption scenarios.

All benchmark runs strictly enforce the **Tripartite State Isolation Model (ADR 015)** to guarantee zero cross-scenario state contamination and 100% deterministic reproducibility.

---

## 2. Research Questions & Formal Hypotheses

* **RQ1 (Resilience & Cost):** Does the SCOF multi-agent consensus architecture achieve statistically significant reductions in Weighted Cost of Disruption ($\text{WCD}$) compared to static heuristics and monolithic LLM baselines?
* **RQ2 (Deliberation Efficiency):** Can the D05 orchestration kernel achieve consensus convergence within real-time operational constraints ($\le 3.5\text{ s}$)?
* **RQ3 (Greedy Bias Mitigation):** Does the CD²F consensus framework (D06) effectively neutralize sub-optimal domain-greedy claims compared to uncoordinated agent panels?
* **RQ4 (Ablation Impact):** What is the marginal contribution of the materialized graph projection (D02) and cross-examination critique rounds (D05) to final decision quality?

---

## 3. Evaluation Metrics

| Metric | Symbol | Definition / Formula | Optimal Direction |
| :--- | :--- | :--- | :--- |
| **Operational Resilience Score** | $\text{ORS}$ | $\text{ORS} = \alpha \frac{\text{FillRate}_{\text{disrupted}}}{\text{FillRate}_{\text{baseline}}} + \beta \left(1 - \frac{T_{\text{recovery}}}{T_{\text{max}}}\right) \times 100$ | Higher ($\to 100$) |
| **Weighted Cost of Disruption** | $\text{WCD}$ | $\text{WCD} = \text{LostRevenue} + \text{ExpeditedFreight} + \text{SpoilageWriteOff} + \text{Penalties}$ | Lower ($\to \$0$) |
| **Deliberation Convergence Time** | $\text{DCT}$ | Total wall-clock time required to transition from Stage 1 to Stage 5 | Lower ($\le 3.5\text{ s}$) |
| **Inter-Agent Agreement** | $\kappa$ | Fleiss' or Cohen's Kappa evaluating agreement across critique rounds | Stable ($0.65 - 0.85$) |

---

## 4. Benchmark Execution Matrix

The harness evaluates the system across four disruption classes (5 scenarios each = 20 total):

1. **Class A (Upstream Supply Shocks):** Supplier lead-time blowouts, raw material stockouts, factory fires.
2. **Class B (Internal Facility & Asset Failures):** Cold-storage unit compressor failures (`AST-0001`), sorting hub conveyor downtime, dock labor strikes.
3. **Class C (Midstream Logistics Disruptions):** Critical corridor flash closures, port terminal congestion, carrier reefer shortages.
4. **Class D (Downstream Demand Shocks):** Unanticipated festival buying spikes, category viral trends, localized extreme weather events.

### Comparative Baseline Roster
* **B0 (Unmitigated Ground Truth):** Zero mitigation intervention; records natural disruption ripple.
* **B1 (Static ERP Rule Engine):** Classical fixed safety stock thresholds and deterministic reorder policies.
* **B2 (Monolithic Single LLM):** A single prompt fed the full problem context without agent role decomposition.
* **B3 (Uncoordinated Multi-Agent Panel):** Specialist agents propose actions independently with no CD²F critique or arbitration.
* **SCOF V2 (Full System):** Complete 4-agent specialist panel + LangGraph deliberation + CD²F consensus.

---

## 5. Execution Protocol & State Isolation

```
           [ Layer 1: Frozen Datasets (datasets/) ] (IMMUTABLE)
                              │
                              ▼
           [ Layer 2: Clean Day-0 Baseline State ]  (READ-ONLY SEED)
                              │
            ┌─────────────────┴─────────────────┐
            │ FORK EPHEMERAL EXECUTION CONTEXT   │
            ▼                                   ▼
[ Scenario 01: Layer 3 Context ]     [ Scenario 02: Layer 3 Context ]
- Execute Deliberation               - Execute Deliberation
- Compute ORS, WCD, DCT              - Compute ORS, WCD, DCT
- Record to run_manifest.json        - Record to run_manifest.json
- PURGE EPHEMERAL STATE              - PURGE EPHEMERAL STATE
```

---

## 6. Acceptance Criteria & Verification Evidence

1. **Automation Gate:** Complete 20-scenario suite executes from a single CLI command (`scof benchmark run --all`) with zero human intervention.
2. **Statistical Significance Gate:** SCOF V2 demonstrates statistically significant ($p < 0.01$) improvements in $\text{ORS}$ over Baselines B1 and B2.
3. **Reproducibility Gate:** Running the benchmark suite twice with the same random seeds produces identical scorecards ($\Delta = 0.000\%$).
4. **State Isolation Gate:** Pre-run and post-run checksums of Layer 1 datasets and Layer 2 baseline tables match exactly.
