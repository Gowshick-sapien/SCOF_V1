# Deliverable D4 -- Model Evaluation & Accuracy Metrics Framework

## 1. Evaluation Methodology

The model evaluation framework assesses prediction accuracy, classification precision/recall, prediction interval coverage, and rerouting recommendation validity for the Supplier Intelligence Agent and Transportation Agent against synthetic ground-truth disruption data generated in Deliverable D1.

---

## 2. Evaluation Metrics

### A. Supplier Failure Classification (Supplier Agent)

1. **Failure Detection Recall**:
   $$\text{Recall} = \frac{\text{True Failure Detections}}{\text{Actual Supplier Failures}}$$
   - **Target**: $\text{Recall} \ge 85\%$ on test scenarios with active `supplier_delay` disruptions.
2. **Failure Detection Precision**:
   $$\text{Precision} = \frac{\text{True Failure Detections}}{\text{Total Failure Claims}}$$
   - **Target**: $\text{Precision} \ge 80\%$.
3. **F1-Score**: Harmonic mean of Precision and Recall.

### B. Transit Delay Prediction Accuracy (Transportation Agent)

1. **Mean Absolute Error (MAE)**:
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$
2. **Mean Absolute Percentage Error (MAPE)**:
   $$\text{MAPE} = \frac{100\%}{N} \sum_{i=1}^{N} \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$
   - **Acceptance Threshold**: $\text{MAE} \le 1.0 \text{ days}$ on synthetic shipment delay scenarios.

### C. Prediction Interval Coverage Probability (PICP)

- Measures the proportion of ground-truth delay/reliability points falling within the $90\%$ prediction interval $[L_i, U_i]$ (derived via residual calibration):
  $$\text{PICP} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(L_i \le y_i \le U_i)$$
- **Target**: $\text{PICP} \ge 85\%$ at $\alpha = 0.10$.

### D. Rerouting & Alternate Ranking Validity

- **Top-1 Selection Precision**: Evaluates whether the highest-ranked alternate supplier or route matches the optimal choice under full ground-truth simulation:
  - **Target**: $\ge 85\%$ optimal candidate selection rate.

---

## 3. Benchmark Target Results (D1 Synthetic Validation Dataset)

| Agent | Model Component | Primary Metric | Target | PICP (90% Interval) | Status |
| --- | --- | --- | --- | --- | --- |
| **Supplier Agent** | GradientBoosting (60%) | Failure Recall | 88.0% | 89.5% | Target |
| **Supplier Agent** | Rule Scorer (40%) | Failure Recall | 81.5% | 85.0% | Target |
| **Supplier Agent** | **Ensemble** | **Failure Recall** | **92.0%** | **93.5%** | **Target** |
| **Transport Agent** | GradientBoosting (60%) | Delay MAE | 0.85 days | 91.0% | Target |
| **Transport Agent** | Route Scorer (40%) | Delay MAE | 1.20 days | 86.5% | Target |
| **Transport Agent** | **Ensemble** | **Delay MAE** | **0.65 days** | **94.2%** | **Target** |
