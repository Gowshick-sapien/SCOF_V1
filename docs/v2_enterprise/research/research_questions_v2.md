# SCOF Research Questions & Scientific Objectives (V2)

## 1. Overview

This document formalizes the scientific foundation and empirical Research Questions (RQ1 through RQ4) governing the evaluation of the **Supply Chain Cognitive Orchestration Framework (SCOF)** under the V2 Enterprise Cognitive Twin scope.

---

## 2. Research Questions (RQ1 – RQ4)

### RQ1: Multi-Agent Consensus Stability & Deadlock Elimination
> **Question:** *To what degree does the CD²F dynamic multi-factor weighting algorithm ($W_i = w_i \times c_i$) eliminate arbitration deadlocks and overrule greedy single-agent bias compared to unweighted voting and static priority heuristics?*
* **Metrics:** 
  * Weighted Consensus Stability (WCS) distribution across 20 canonical disruption scenarios.
  * Deadlock frequency (% of scenarios requiring tie-breaking or timing out).
  * Greedy bias override rate (% of scenarios where an isolated, overconfident agent recommendation is correctly overruled by cross-functional consensus).

### RQ2: Decision Latency vs. Operational Risk Under Dual-Path Gating
> **Question:** *Can a dual-path risk-gated routing architecture achieve sub-500ms execution latency for routine disruptions while reliably escalating high-severity, low-consensus disruptions to human operators?*
* **Metrics:**
  * Fast-path round-trip execution latency (P50, P95, P99 in milliseconds).
  * Gating accuracy: False-negative escalation rate (% of high-severity disruptions incorrectly routed to fast-path autonomous execution).
  * Decision throughput under concurrent disruption ingestion.

### RQ3: Business Value & Service Level Preservation
> **Question:** *Does collaborative multi-agent mitigation preserve store-level fill rates, minimize perishable inventory spoilage, and reduce financial exposure compared to single-agent and baseline operational responses?*
* **Metrics:**
  * Store SKU Fill Rate Preservation (% of baseline on-shelf availability maintained post-disruption).
  * Spoilage write-off mitigation (INR saved vs. unmitigated baseline).
  * Total Net Financial Impact: $\text{Revenue Preserved} - (\text{Expedited Freight Cost} + \text{Write-Off Cost})$.

### RQ4: Inter-Agent Deliberation Agreement & Calibration (Cohen's Kappa)
> **Question:** *How does inter-agent agreement evolve across repeated scenario deliberations, and does rolling accuracy calibration ($\kappa$) maintain statistically significant reliability?*
* **Metrics:**
  * Inter-rater agreement score: Cohen's Kappa ($\kappa$) between agent pairs (Demand-Inventory, Inventory-Transport, Supplier-Transport).
  * Rolling judge calibration drift over repeated simulation epochs.
