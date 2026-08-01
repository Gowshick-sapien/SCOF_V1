# Deliverable D3 -- Model Evaluation Framework

## 1. Purpose
This document defines the evaluation metrics and methodology for assessing the Demand Agent and Inventory Agent forecast accuracy against D1's synthetic ground truth data. Evaluation results are recorded in [`acceptance_evidence.md`](./acceptance_evidence.md) after execution.

---

## 2. Evaluation Strategy

Both agents are evaluated on a temporal holdout split of the D1 synthetic data:

- **Training set**: First 80% of the simulation history (by date)
- **Validation set**: Next 10% (used for confidence calibration's `historical_error` component)
- **Test set**: Final 10% (used for evaluation metrics reported here)

The test set is never seen during training or confidence calibration. Evaluation is deterministic via explicit random seeds (`NUMPY_SEED=42`, `XGBOOST_SEED=42`, `PYTHON_RANDOM_SEED=42`).

---

## 3. Demand Agent Metrics

### 3.1 Point Forecast Accuracy

| Metric | Definition | Target (MVP) |
| --- | --- | --- |
| **MAE** (Mean Absolute Error) | `mean(|forecast - actual|)` | < 50% of mean daily demand |
| **MAPE** (Mean Absolute Percentage Error) | `mean(|forecast - actual| / actual) * 100` | < 30% |
| **RMSE** (Root Mean Squared Error) | `sqrt(mean((forecast - actual)^2))` | Reported, no hard target |
| **Bias** (Mean Error) | `mean(forecast - actual)` | Within +/- 10% of mean demand |

Metrics are computed per-product and aggregated across all products.

### 3.2 Prediction Interval Coverage

| Metric | Definition | Target (MVP) |
| --- | --- | --- |
| **Coverage Probability** | Fraction of actual values within the 90% prediction interval | >= 0.80 |
| **Interval Width** | Mean width of prediction intervals | Reported, narrower is better |
| **Interval Sharpness** | Coverage / Width ratio | Higher is better |

### 3.3 Ensemble Contribution Analysis

| Metric | Definition | Purpose |
| --- | --- | --- |
| **Per-Model MAE** | MAE for XGBoost alone vs. Statistical model alone | Validates that ensembling improves over individual models |
| **Ensemble Improvement** | `1 - (ensemble_MAE / best_single_model_MAE)` | Must be >= 0 (ensemble must not be worse) |
| **Agreement Score Distribution** | Histogram of agreement scores across test scenarios | Identifies scenarios where models strongly diverge |

---

## 4. Inventory Agent Metrics

### 4.1 Stock Level Projection Accuracy

| Metric | Definition | Target (MVP) |
| --- | --- | --- |
| **MAE** | `mean(|projected_stock - actual_stock|)` | < 20% of mean stock level |
| **MAPE** | Percentage error on stock projections | < 25% |
| **Days-of-Supply Error** | `|projected_days_to_stockout - actual_days_to_stockout|` | < 3 days |

### 4.2 Stockout Detection Performance

Stockout detection is treated as a binary classification: did the agent correctly identify that a stockout would occur within the forecast horizon?

| Metric | Definition | Target (MVP) |
| --- | --- | --- |
| **Precision** | True stockout alerts / All stockout alerts | >= 0.70 |
| **Recall** | True stockout alerts / All actual stockouts | >= 0.80 |
| **F1 Score** | Harmonic mean of precision and recall | >= 0.75 |
| **False Alarm Rate** | False stockout alerts / All non-stockout periods | < 0.20 |

A stockout is defined as `stock_on_hand = 0` on any day within the forecast horizon.

### 4.3 Priority Assignment Accuracy

| Metric | Definition | Target (MVP) |
| --- | --- | --- |
| **Priority Accuracy** | Fraction of claims where assigned priority matches the severity implied by ground truth | >= 0.75 |
| **HIGH Priority Recall** | Of all cases where stockout occurred, fraction assigned HIGH priority | >= 0.85 |

---

## 5. Confidence Calibration Analysis

### 5.1 Calibration Curve

For both agents, bin predictions by confidence decile (0.0-0.1, 0.1-0.2, ..., 0.9-1.0) and measure the actual accuracy within each bin. A well-calibrated model has actual accuracy approximately equal to stated confidence in each bin.

| Confidence Bin | Expected Accuracy | Actual Accuracy | Calibration Error |
| --- | --- | --- | --- |
| 0.0 - 0.1 | ~5% | _measured_ | _delta_ |
| ... | ... | ... | ... |
| 0.9 - 1.0 | ~95% | _measured_ | _delta_ |

### 5.2 Calibration Metrics

| Metric | Definition | Target (MVP) |
| --- | --- | --- |
| **ECE** (Expected Calibration Error) | Weighted average of `|confidence - accuracy|` across bins | < 0.15 |
| **MCE** (Maximum Calibration Error) | Worst-case bin calibration error | < 0.30 |

### 5.3 Component Contribution Analysis

For the composite confidence formula (`0.4 * agreement + 0.3 * interval + 0.3 * historical`), report the distribution of each component across test scenarios to verify no single component dominates.

---

## 6. Disruption Response Evaluation

### 6.1 Demand Agent Under `demand_spike`
- Inject a `demand_spike` disruption (severity 3-5) targeting a product
- Verify: forecast increases relative to non-disrupted baseline
- Verify: reasoning mentions the disruption
- Measure: forecast delta proportional to disruption severity

### 6.2 Inventory Agent Under `supplier_delay`
- Inject a `supplier_delay` disruption (severity 3-5) targeting a supplier
- Verify: agent detects increased stockout risk for products supplied by that supplier
- Verify: `transit_risk_factor` reduces effective in-transit units
- Verify: reasoning mentions the disruption and affected supplier
- Measure: days-to-stockout estimate decreases compared to non-disrupted baseline

---

## 7. Determinism Verification

| Check | Method | Target |
| --- | --- | --- |
| **Reproducibility** | Call each agent twice with identical `ScenarioContext` and random seeds | Byte-identical JSON output |
| **Cross-Run Stability** | Restart agent container and repeat | Identical output after fresh startup |

---

## 8. Evaluation Execution

```bash
# Run evaluation suite (after agents are running)
python scripts/verify_d3.py --mode evaluation

# Individual agent test suites
pytest services/agents/demand/tests/ -v
pytest services/agents/inventory/tests/ -v
```

Results are recorded in [`acceptance_evidence.md`](./acceptance_evidence.md).

---

## 9. Baseline Comparison (Informational)

For context, the following simple baselines are computed but not required to be beaten for D3 acceptance (formal baseline comparison occurs in D10):

| Baseline | Method |
| --- | --- |
| **Naive Persistence** | Forecast = last observed value |
| **7-Day Moving Average** | Forecast = mean of last 7 values |
| **XGBoost Only** | Single model without ensembling |
| **Statistical Only** | Single model without ensembling |

The ensemble should outperform each individual model. Outperforming naive baselines is expected but not a hard gate.
