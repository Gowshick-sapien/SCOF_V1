# Enterprise South Indian Supply Chain Scenario Expansion (25 Scenarios)

This directory contains the engineering specification, operational scenario reference book, file-level modifications, impact analysis, and verification suite for expanding the SCOF platform from 5 initial scenarios to a comprehensive suite of **25 production-grade operational scenarios** grounded in the Enterprise South Indian Electronics Manufacturing Topology.

---

## 1. Initiative Overview

The initial transition to the South Indian Electronics Manufacturing Topology established an 18-node, multi-tier industrial network spanning Tamil Nadu, Karnataka, Andhra Pradesh, Kerala, and Telangana. The initial scenario catalog provided 5 baseline operational scenarios (`scen-01` through `scen-05`).

While these 5 scenarios validated core functionality, an enterprise supply chain operating across peninsular India encounters diverse operational failure modes, including:
- Upstream semiconductor packaging halts, wafer fab cleanroom outages, and solder defect lot quarantines.
- Downstream market demand volatility driven by state energy mandates, electric vehicle powertrain ramp-ups, and automotive quarterly pushes.
- Interstate transport failures across national highway spines (NH44, NH48, NH544), border tax checkpost strikes, and mountain pass landslides.
- Facility-level automated warehouse retrieval failures, bonded FTWZ customs audits, and intermodal ICD flatbed shortages.
- Multimodal maritime berth congestion at Coromandel ports and airfreight capacity crunches at international aerotropolises.
- Catastrophic compound weather disruptions and systemic peninsular power grid blackouts.

This initiative introduces **20 new, fully parameterized operational scenarios** (expanding the catalog to 25 total scenarios), complete with mathematical counterfactual parameters, agent deliberation dynamics, and ground-truth consensus benchmarks.

---

## 2. Core Objectives

1. **Comprehensive Operational Coverage**: Expand from 5 scenarios to 25 scenarios, covering all 18 topology entities and 3 product categories across 7 distinct operational failure domains.
2. **Industrial Realism in Peninsular India**: Anchor each scenario to authentic geographical corridors, infrastructure bottlenecks, regulatory frameworks, and weather patterns across South India.
3. **Multi-Agent Deliberation & Stress Testing**: Create challenging conflict scenarios where specialist agents (Demand, Inventory, Supplier, Transportation) have diverging incentives, exercising CD2F competence weighting and policy-based escalation.
4. **Counterfactual Prediction Alignment**: Update the Monte-Carlo simulation lab to enable interactive what-if exploration for all 25 scenarios with localized cost deltas in Indian Rupees (INR).
5. **Zero Kernel Regressions**: Maintain complete backward compatibility with the existing coordinator runtime, PostgreSQL schema, Neo4j graph model, and WebSocket streaming protocols.

---

## 3. Deliverables Structure (S1 to S5)

The scenario expansion initiative is organized into five sequential, testable deliverables:

| Deliverable | Title | Focus Area | Key Output |
| :--- | :--- | :--- | :--- |
| **S1** | **Master Scenario Description Book** | Domain Modeling & Reference | Authoritative reference document (`scenario_description_book.md`) detailing all 25 scenarios, operational use cases, multi-agent conflicts, and resolution mechanics. |
| **S2** | **Synthetic Generator & Disruption Seeding** | Simulation & PostgreSQL | Update `services/simulation/src/disruption_generator.py` and database seeding scripts to generate scenarios `scen-01` through `scen-25` with parameterized disruption events. |
| **S3** | **Counterfactual Simulation Engine Expansion** | Backend API & What-If Logic | Extend `services/api/src/routers/whatif.py` with expanded scenario contexts, multi-node profiles, and dynamic Rupee cost variance calculations. |
| **S4** | **Desktop Operations Console & Scenario Launcher UX** | Frontend Operations Console | Update `desktop/src/views/Scenarios/ScenariosView.tsx` and `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` with all 25 scenarios, rich descriptions, and search/filter controls. |
| **S5** | **Automated Verification, Regression Suite & Sign-Off** | Quality Assurance & Benchmarks | Comprehensive integration tests verifying trigger-to-decision latency, CD2F mathematical stability, and pgvector semantic retrieval. |

---

## 4. Scenario Portfolio Summary (25 Scenarios)

| ID | Title | Disruption Category | Target Entity | Severity | Escalation Tier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **scen-01** | Baseline Nominal Operations | Nominal Baseline (`none`) | Global Topology (`global`) | 1 / 5 | Fast-Path |
| **scen-02** | Tier-1 Semiconductor Packaging Delay (SPEL Chennai) | Supplier Delay (`supplier_delay`) | `sup-01` (SPEL Semiconductor) | 4 / 5 | Fast-Path |
| **scen-03** | Automotive Sensor Demand Surge (Oragadam Hub) | Demand Spike (`demand_spike`) | `wh-03` (Oragadam JIT Warehouse) | 3 / 5 | Fast-Path |
| **scen-04** | NH48 Arterial Freight Corridor Monsoon Inundation | Transport Failure (`transport_failure`) | `route-wh-01-mfg-01` (Hosur-Sriperumbudur) | 5 / 5 | Slow-Path |
| **scen-05** | Cochin Port Vallarpadam Terminal Cyclonic Stoppage | Adverse Weather (`adverse_weather`) | `dc-02` (Cochin Port Terminal) | 4 / 5 | Fast-Path |
| **scen-06** | Discrete Power Fab Cleanroom Outage (CDIL Bengaluru) | Supplier Delay (`supplier_delay`) | `sup-02` (Continental Device India) | 4 / 5 | Fast-Path |
| **scen-07** | Automotive Telematics SMT Head Failure (Kaynes Mysuru) | Supplier Delay (`supplier_delay`) | `sup-03` (Kaynes Technology) | 3 / 5 | Fast-Path |
| **scen-08** | Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur) | Supplier Delay (`supplier_delay`) | `sup-04` (Syrma SGS Technology) | 4 / 5 | Fast-Path |
| **scen-09** | Aerospace Sub-Module Allocation Rationing (Centum) | Supplier Delay (`supplier_delay`) | `sup-05` (Centum Electronics) | 3 / 5 | Fast-Path |
| **scen-10** | High-Density PCB Copper Laminate Stockout (Sahasra) | Supplier Delay (`supplier_delay`) | `sup-08` (Sahasra Electronic) | 4 / 5 | Fast-Path |
| **scen-11** | Smart Energy IoT Meter Mandate Demand Surge | Demand Spike (`demand_spike`) | `wh-01` (Hosur Logistics Buffer) | 4 / 5 | Slow-Path |
| **scen-12** | Commercial Fleet EV Powertrain Retrofit Spike | Demand Spike (`demand_spike`) | `wh-02` (Whitefield ICD) | 5 / 5 | Human Escalation |
| **scen-13** | Quarter-End Automotive OEM Assembly Ramp-Up | Demand Spike (`demand_spike`) | `wh-03` (Oragadam JIT Warehouse) | 3 / 5 | Fast-Path |
| **scen-14** | Coastal Municipal Sensor Network Renewal Push | Demand Spike (`demand_spike`) | `dc-01` (Chennai Port Gateway) | 3 / 5 | Fast-Path |
| **scen-15** | Attibele Interstate Border Truck Checkpost Strike | Transport Failure (`transport_failure`) | `route-sup-02-wh-01` (Electronic City-Hosur) | 4 / 5 | Fast-Path |
| **scen-16** | Palakkad Gap Western Ghats Landslide Corridor Halt | Transport Failure (`transport_failure`) | `route-sup-07-mfg-01` (Kochi-Sriperumbudur) | 5 / 5 | Slow-Path |
| **scen-17** | NH44 Kurnool Bridge Heavy-Axle Freight Weight Embargo | Transport Failure (`transport_failure`) | `route-sup-08-wh-04` (Hyderabad-Sri City) | 3 / 5 | Fast-Path |
| **scen-18** | Chennai Outer Ring Road Heavy Freight Gridlock | Transport Failure (`transport_failure`) | `route-wh-03-mfg-01` (Oragadam-Sriperumbudur) | 3 / 5 | Fast-Path |
| **scen-19** | Hosur Buffer Automated AS/RS Crane System Fault | Facility Failure (`transport_failure`) | `wh-01` (Hosur Buffer Warehouse) | 4 / 5 | Fast-Path |
| **scen-20** | Sri City FTWZ Regulatory Customs Audit Clearance Hold | Regulatory Hold (`supplier_delay`) | `wh-04` (Sri City FTWZ Hub) | 4 / 5 | Slow-Path |
| **scen-21** | Whitefield Inland Container Depot Rail Rake Deficit | Intermodal Bottleneck (`transport_failure`) | `wh-02` (Whitefield ICD) | 3 / 5 | Fast-Path |
| **scen-22** | Chennai Port Shallow Channel Silting Berth Congestion | Seaport Congestion (`transport_failure`) | `dc-01` (Chennai Port Gateway) | 3 / 5 | Fast-Path |
| **scen-23** | Shamshabad Aerotropolis Airfreight Cargo Crunch | Airport Bottleneck (`transport_failure`) | `dc-03` (Hyderabad Air Gateway) | 4 / 5 | Fast-Path |
| **scen-24** | Cyclone Michaung Coromandel Plain Compound Inundation | Compound Catastrophe (`adverse_weather`) | `sup-01` + `dc-01` (Chennai Coast) | 5 / 5 | Human Escalation |
| **scen-25** | Peninsular Grid Blackout Sourcing Crisis | Systemic Failure (`supplier_delay`) | Global Topology (`global`) | 5 / 5 | Human Escalation |

---

## 5. Documentation Index

- **Scenario Description Book**: [`scenario_description_book.md`](scenario_description_book.md)  
  Comprehensive operational manual detailing each scenario, real-world context, multi-agent conflict mechanics, consensus actions, and performance targets.
- **Master Implementation Plan**: [`implementation_plan.md`](implementation_plan.md)  
  Technical engineering roadmap specifying file modifications, architectural impact, test suites, and acceptance gates.
