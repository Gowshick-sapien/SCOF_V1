# Deliverable D6 — CD²F Consensus Engine

##  Objective
Build and validate the Consensus-Driven Collaborative Decision Framework (CD²F) arbitration engine in isolation against fixture data.

---

##  Requirements Summary (from SRS)
- **FR-6.1**: Confidence-weighted voting arbitration pipeline (stated confidence × rolling historical accuracy).
- **FR-6.2**: Escalation tiering logic (fast path / slow path / human escalation).
- **FR-6.3**: Judge calibration check against hand-labeled scenario set computing Cohen's kappa.
- **FR-6.4**: Naive majority voting baseline comparator.
- **FR-6.5**: Outputs: Final Decision + Reasoning Trail + Escalation Tier.
- **FR-6.6**: Thresholds & rules configured via Domain Profile (`consensus.yaml`).
