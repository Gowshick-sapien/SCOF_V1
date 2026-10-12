# SCOF Scenario Description Book: 25 Enterprise Operational Scenarios

This reference book provides exhaustive operational specifications for all 25 disruption scenarios supported by the Supply Chain Cognitive Orchestration Framework (SCOF). All scenarios are contextualized within the **Enterprise South Indian Electronics Manufacturing Topology** (encompassing Sriperumbudur, Maraimalai Nagar, Bengaluru, Mysuru, Bargur, Hosur, Sri City, Kochi, and Hyderabad).

---

## Portfolio Table of Contents

- [Domain 1: Baseline & Core Proof Scenarios (scen-01 to scen-05)](#domain-1-baseline--core-proof-scenarios)
  - [scen-01: Baseline Nominal Operations](#scen-01-baseline-nominal-operations)
  - [scen-02: Tier-1 Semiconductor Packaging Delay (SPEL Chennai)](#scen-02-tier-1-semiconductor-packaging-delay-spel-chennai)
  - [scen-03: Automotive Sensor Demand Surge (Oragadam Hub)](#scen-03-automotive-sensor-demand-surge-oragadam-hub)
  - [scen-04: NH48 Arterial Freight Corridor Monsoon Inundation](#scen-04-nh48-arterial-freight-corridor-monsoon-inundation)
  - [scen-05: Cochin Port Vallarpadam Terminal Cyclonic Stoppage](#scen-05-cochin-port-vallarpadam-terminal-cyclonic-stoppage)
- [Domain 2: Upstream Semiconductor & Component Supplier Shortages (scen-06 to scen-10)](#domain-2-upstream-semiconductor--component-supplier-shortages)
  - [scen-06: Discrete Power Fab Cleanroom Outage (CDIL Bengaluru)](#scen-06-discrete-power-fab-cleanroom-outage-cdil-bengaluru)
  - [scen-07: Automotive Telematics SMT Head Failure (Kaynes Mysuru)](#scen-07-automotive-telematics-smt-head-failure-kaynes-mysuru)
  - [scen-08: Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur)](#scen-08-surface-mount-solder-defect-lot-quarantine-syrma-bargur)
  - [scen-09: Aerospace Sub-Module Allocation Rationing (Centum Yelahanka)](#scen-09-aerospace-sub-module-allocation-rationing-centum-yelahanka)
  - [scen-10: High-Density PCB Copper Laminate Stockout (Sahasra Hyderabad)](#scen-10-high-density-pcb-copper-laminate-stockout-sahasra-hyderabad)
- [Domain 3: Downstream Market Volatility & Demand Shocks (scen-11 to scen-14)](#domain-3-downstream-market-volatility--demand-shocks)
  - [scen-11: Smart Energy IoT Meter Mandate Demand Surge](#scen-11-smart-energy-iot-meter-mandate-demand-surge)
  - [scen-12: Commercial Fleet EV Powertrain Retrofit Spike](#scen-12-commercial-fleet-ev-powertrain-retrofit-spike)
  - [scen-13: Quarter-End Automotive OEM Assembly Ramp-Up](#scen-13-quarter-end-automotive-oem-assembly-ramp-up)
  - [scen-14: Coastal Municipal Sensor Network Renewal Push](#scen-14-coastal-municipal-sensor-network-renewal-push)
- [Domain 4: Highway, Freight Corridor & Transport Disruptions (scen-15 to scen-18)](#domain-4-highway-freight-corridor--transport-disruptions)
  - [scen-15: Attibele Interstate Border Truck Checkpost Strike](#scen-15-attibele-interstate-border-truck-checkpost-strike)
  - [scen-16: Palakkad Gap Western Ghats Landslide Corridor Halt](#scen-16-palakkad-gap-western-ghats-landslide-corridor-halt)
  - [scen-17: NH44 Kurnool Bridge Heavy-Axle Weight Embargo](#scen-17-nh44-kurnool-bridge-heavy-axle-weight-embargo)
  - [scen-18: Chennai Outer Ring Road Heavy Freight Gridlock](#scen-18-chennai-outer-ring-road-heavy-freight-gridlock)
- [Domain 5: Warehouse & FTWZ Facility Logistics Shocks (scen-19 to scen-21)](#domain-5-warehouse--ftwz-facility-logistics-shocks)
  - [scen-19: Hosur Buffer Automated AS/RS Crane System Fault](#scen-19-hosur-buffer-automated-asrs-crane-system-fault)
  - [scen-20: Sri City FTWZ Regulatory Customs Audit Clearance Hold](#scen-20-sri-city-ftwz-regulatory-customs-audit-clearance-hold)
  - [scen-21: Whitefield Inland Container Depot Rail Rake Deficit](#scen-21-whitefield-inland-container-depot-rail-rake-deficit)
- [Domain 6: Multimodal Seaport & Airport Terminal Bottlenecks (scen-22 to scen-23)](#domain-6-multimodal-seaport--airport-terminal-bottlenecks)
  - [scen-22: Chennai Port Shallow Channel Silting Berth Congestion](#scen-22-chennai-port-shallow-channel-silting-berth-congestion)
  - [scen-23: Shamshabad Aerotropolis Airfreight Cargo Crunch](#scen-23-shamshabad-aerotropolis-airfreight-cargo-crunch)
- [Domain 7: Compound Catastrophic & Systemic Crises (scen-24 to scen-25)](#domain-7-compound-catastrophic--systemic-crises)
  - [scen-24: Cyclone Michaung Coromandel Plain Compound Inundation](#scen-24-cyclone-michaung-coromandel-plain-compound-inundation)
  - [scen-25: Peninsular Grid Blackout Sourcing Crisis](#scen-25-peninsular-grid-blackout-sourcing-crisis)

---

## Domain 1: Baseline & Core Proof Scenarios

### scen-01: Baseline Nominal Operations

- **Classification**:
  - Disruption Type: `none`
  - Target Entity: `global` (Peninsular Multi-Tier Network)
  - Default Severity: 1 / 5
  - Duration: 30 days
  - Primary Products: `prod-101`, `prod-102`, `prod-103`
- **Problem Statement & Use Case**:
  Models steady-state industrial operations under standard operating conditions across all 18 network entities. Calibrates baseline throughput, on-time in-full (OTIF) shipping performance, inventory holding costs, and baseline multi-agent consensus confidence.
- **Physical Dynamics & Topology Interaction**:
  Component flows move unimpeded along National Highways NH44, NH48, and NH544. Suppliers maintain scheduled batch output. Sriperumbudur assembly facility operates on nominal two-shift schedule. Buffer stock levels at Hosur (`wh-01`) and Oragadam (`wh-03`) fluctuate within normal safety bands (14 to 21 days coverage).
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `demand-agent`: Forecasts steady seasonal demand with narrow confidence bands (error < 4.5%).
  - `inventory-agent`: Confirms inventory levels exceed target safety stock across all warehouses.
  - `supplier-agent`: Scores primary suppliers between 0.94 and 0.98 reliability.
  - `transport-agent`: Validates highway transit times within standard lead-time thresholds (+/- 2 hours).
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Maintain scheduled production and replenishment cycles across all facilities."`
  - Consensus Status: `RESOLVED` (Unanimous, WCS Stability: 0.985)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+0.0%`
  - Lead Time Impact: `+0.0 days`
  - Cost Delta: `+₹0`

---

### scen-02: Tier-1 Semiconductor Packaging Delay (SPEL Chennai)

- **Classification**:
  - Disruption Type: `supplier_delay`
  - Target Entity: `sup-01` (SPEL Semiconductor, Maraimalai Nagar)
  - Default Severity: 4 / 5
  - Duration: 7 days
  - Primary Products: `prod-101`, `prod-103`
- **Problem Statement & Use Case**:
  A 5-day wafer-level chip scale packaging (WLCSP) bottleneck at SPEL Semiconductor's Maraimalai Nagar cleanroom creates an imminent component stockout hazard for Sriperumbudur SMT lines. Exercises dual-source qualification and regional inventory buffer reallocation.
- **Physical Dynamics & Topology Interaction**:
  Wafers entering packaging lines suffer backlogs. Deliveries scheduled via GST Road to Oragadam (`wh-03`) face complete stoppage for 5 operating days, endangering production of Smart IoT Gateways (`prod-101`).
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Advocates dual-sourcing failover to Continental Device India (`sup-02`, Bengaluru) to absorb 60% volume.
  - `inventory-agent`: Recommends immediate safety stock drawdown from Hosur Buffer Warehouse (`wh-01`) to cover assembly needs for 96 hours.
  - `demand-agent`: Notes downstream automotive telemetry delivery penalties if stockout exceeds 48 hours.
  - `transport-agent`: Confirms expedited road transport available from Hosur to Sriperumbudur on NH48.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Reallocate 60% order volume to Continental Device India (sup-02, Bengaluru) and expedite buffer stock from Hosur Logistics Buffer (wh-01) via NH48."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.924)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+38.5%`
  - Lead Time Impact: `+5.0 days`
  - Cost Delta: `+₹38,400`

---

### scen-03: Automotive Sensor Demand Surge (Oragadam Hub)

- **Classification**:
  - Disruption Type: `demand_spike`
  - Target Entity: `wh-03` (Oragadam JIT Supplier Warehouse)
  - Default Severity: 3 / 5
  - Duration: 14 days
  - Primary Products: `prod-102` (Industrial Automotive Sensor Hub)
- **Problem Statement & Use Case**:
  Chennai automobile cluster OEMs in Oragadam and Sriperumbudur expand weekly vehicle production runs, triggering a sudden 45% demand surge for Automotive Sensor Hubs (`prod-102`). Tests multi-echelon safety stock responsiveness and JIT delivery cycle acceleration.
- **Physical Dynamics & Topology Interaction**:
  Daily consumption rate increases from 800 units/day to 1,160 units/day. Oragadam inventory buffer drops from 18 days to 4.5 days within 72 hours, risking assembly line starvation.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `demand-agent`: Flags sustained upward demand trend and requests immediate doubling of replenishment orders.
  - `inventory-agent`: Warns of severe stockout within 5 days unless cross-docking is activated at Hosur (`wh-01`).
  - `supplier-agent`: Confirms Kaynes Technology (`sup-03`, Mysuru) has 25% surplus SMT line capacity.
  - `transport-agent`: Recommends daily scheduled shuttle runs on NH48 rather than batch consolidation.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Increase JIT delivery frequency to 2-hour intervals from Oragadam (wh-03) and activate auxiliary surface-mount shifts at Kaynes Technology (sup-03)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.912)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+32.2%`
  - Lead Time Impact: `+3.7 days`
  - Cost Delta: `+₹33,465`

---

### scen-04: NH48 Arterial Freight Corridor Monsoon Inundation

- **Classification**:
  - Disruption Type: `transport_failure`
  - Target Entity: `route-wh-01-mfg-01` (Hosur-Sriperumbudur Freight Corridor)
  - Default Severity: 5 / 5
  - Duration: 4 days
  - Primary Products: All Products (`prod-101`, `prod-102`, `prod-103`)
- **Problem Statement & Use Case**:
  Extreme monsoon rainfall inundates the NH48 interstate freight corridor near Vellore and Ranipet, halting heavy commercial vehicle transit from the Hosur logistics hub to Sriperumbudur. Evaluates multi-modal rerouting and regional detour feasibility.
- **Physical Dynamics & Topology Interaction**:
  Over 80 container trucks carrying sub-assemblies and raw microelectronics are stranded along highway stretches. Inbound component flow to Sriperumbudur drops by 85%.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Evaluates alternative state highways: State Highway 9 (SH9) via Arani and Polur vs Southern Railway container service from Jolarpettai.
  - `inventory-agent`: Calculates existing on-site Sriperumbudur inventory reserves at exactly 36 operating hours.
  - `supplier-agent`: Proposes hot-shot air freight from Kempegowda Airport for mission-critical microcontrollers.
  - `demand-agent`: Computes customer contract penalty exposure of ₹18,00,000 if plant halts.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Detour priority truck convoys via Krishnagiri-Tiruvannamalai-Kanchipuram arterial roads and mobilize emergency coastal container rail from Katpadi."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.887)
  - Escalation Tier: `SLOW_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+56.3%`
  - Lead Time Impact: `+9.5 days`
  - Cost Delta: `+₹75,640`

---

### scen-05: Cochin Port Vallarpadam Terminal Cyclonic Stoppage

- **Classification**:
  - Disruption Type: `adverse_weather`
  - Target Entity: `dc-02` (Cochin Port Vallarpadam Terminal)
  - Default Severity: 4 / 5
  - Duration: 8 days
  - Primary Products: `prod-101`, `prod-102` (Export Consignments)
- **Problem Statement & Use Case**:
  Severe cyclonic activity in the Arabian Sea triggers deep-water squalls and gale-force winds, halting seaside gantry crane operations at the Vallarpadam International Container Transshipment Terminal (ICTT). Tests export transshipment diversion to the Coromandel coast.
- **Physical Dynamics & Topology Interaction**:
  Outbound maritime feeder vessels are barred from harbor entrance. Export shipments of finished IoT telematics modules destined for Europe are halted at port gates.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Recommends immediate diversion of Kerala export containers via Southern Railway express freight to Chennai Port Container Terminal (`dc-01`).
  - `demand-agent`: Estimates international maritime transit delay at 11 days unless diverted overland.
  - `inventory-agent`: Advises holding non-critical sub-assemblies at Kakkanad (`sup-07`) until maritime clearance.
  - `supplier-agent`: Confirms packaging and moisture-protection standards permit rail freight.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Reroute European export container volume via electrified rail container shuttle from Ernakulam to Chennai Port Terminal (dc-01)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.931)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+25.8%`
  - Lead Time Impact: `+7.9 days`
  - Cost Delta: `+₹46,256`

---

## Domain 2: Upstream Semiconductor & Component Supplier Shortages

### scen-06: Discrete Power Fab Cleanroom Outage (CDIL Bengaluru)

- **Classification**:
  - Disruption Type: `supplier_delay`
  - Target Entity: `sup-02` (Continental Device India Ltd, Electronic City)
  - Default Severity: 4 / 5
  - Duration: 6 days
  - Primary Products: `prod-101`, `prod-103`
- **Problem Statement & Use Case**:
  An industrial cleanroom HVAC and filtration failure at CDIL's Electronic City fab halts diffusion and epitaxy lines for discrete power transistors and rectifiers. Evaluates alternate discrete component supplier failover to North Bengaluru defense-grade suppliers.
- **Physical Dynamics & Topology Interaction**:
  Production of discrete silicon diodes and power FETs ceases abruptly. Outbound shipments along the Hosur Road bypass to `wh-01` drop to zero.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Queries Neo4j for alternate discrete component manufacturers; identifies Centum Electronics (`sup-05`, Yelahanka) and Syrma SGS (`sup-04`, Bargur).
  - `inventory-agent`: Verifies Whitefield ICD (`wh-02`) maintains 8 days of buffer stock.
  - `transport-agent`: Identifies rapid truck dispatch paths from Yelahanka via Outer Ring Road to Hosur.
  - `demand-agent`: Notes steady demand; advises against slowing assembly lines.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Qualify and transfer discrete component production lots to Centum Electronics (sup-05) and draw safety buffer from Whitefield ICD (wh-02)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.918)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+29.4%`
  - Lead Time Impact: `+5.8 days`
  - Cost Delta: `+₹29,600`

---

### scen-07: Automotive Telematics SMT Head Failure (Kaynes Mysuru)

- **Classification**:
  - Disruption Type: `supplier_delay`
  - Target Entity: `sup-03` (Kaynes Technology India, Koorgalli, Mysuru)
  - Default Severity: 3 / 5
  - Duration: 5 days
  - Primary Products: `prod-102` (Automotive Sensor Hub)
- **Problem Statement & Use Case**:
  A high-speed pick-and-place robotic placement head breakdown on Kaynes's primary surface-mount line in Koorgalli creates an acute 5-day assembly deficit for automotive sensor micro-modules. Exercises local cluster failover within Mysuru.
- **Physical Dynamics & Topology Interaction**:
  SMT line capacity at Koorgalli drops by 65%. Automated optical inspection queues stall, delaying outbound dispatches along the Mysuru-Bengaluru expressway (NH275).
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Proposes immediate dual-sourcing failover to Vinyas Innovative Technologies (`sup-06`, Hebbal Industrial Area, Mysuru), located only 8 km away.
  - `inventory-agent`: Recommends absorbing short-term delay from safety buffer stock at Oragadam JIT (`wh-03`).
  - `transport-agent`: Confirms local truck shuttle between Koorgalli and Hebbal can transfer raw component kits within 3 hours.
  - `demand-agent`: Endorses split allocation to prevent OEM assembly line stoppage.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Transfer 50% automotive sensor sub-assembly runs to Vinyas Innovative (sup-06, Mysuru) and draw buffer stock from Oragadam JIT (wh-03)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.945)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+24.0%`
  - Lead Time Impact: `+5.3 days`
  - Cost Delta: `+₹26,400`

---

### scen-08: Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur)

- **Classification**:
  - Disruption Type: `supplier_delay`
  - Target Entity: `sup-04` (Syrma SGS Technology, Bargur Industrial Estate)
  - Default Severity: 4 / 5
  - Duration: 7 days
  - Primary Products: `prod-101`, `prod-102`
- **Problem Statement & Use Case**:
  Automated X-ray inspection (AXI) detects excessive micro-voiding in BGA (Ball Grid Array) solder joints across a production lot of 14,000 sub-assembly boards, triggering mandatory quality quarantine and re-work. Evaluates safety quarantine protocols and secondary line activation.
- **Physical Dynamics & Topology Interaction**:
  The entire batch of 14,000 boards is placed in bonded quarantine. Shipments scheduled via NH48 Krishnagiri corridor to Sriperumbudur are frozen pending failure analysis.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Requests emergency capacity reservation at Kaynes Technology (`sup-03`, Mysuru) for replacement BGA mounting.
  - `inventory-agent`: Isolates suspect inventory lots across all connected transit nodes to prevent contaminated assemblies reaching mfg-01.
  - `demand-agent`: Analyzes priority orders and authorizes expediting non-quarantined reserve stock.
  - `transport-agent`: Schedules secure reverse-logistics transport for quarantined assemblies.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Isolate quarantined BGA lot, initiate rapid re-solder protocol at Bargur, and commission expedited replacement batch from Kaynes Technology (sup-03)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.908)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+30.7%`
  - Lead Time Impact: `+5.4 days`
  - Cost Delta: `+₹32,800`

---

### scen-09: Aerospace Sub-Module Allocation Rationing (Centum Yelahanka)

- **Classification**:
  - Disruption Type: `supplier_delay`
  - Target Entity: `sup-05` (Centum Electronics, Yelahanka, Bengaluru)
  - Default Severity: 3 / 5
  - Duration: 10 days
  - Primary Products: `prod-103` (High-Density Power Module)
- **Problem Statement & Use Case**:
  Statutory priority defense and satellite payload contracts preempt 40% of Centum's cleanroom line capacity in Yelahanka, forcing allocation rationing on commercial micro-inverter modules. Tests inter-state tier-2 failover to Hyderabad.
- **Physical Dynamics & Topology Interaction**:
  Weekly commercial supply allocation drops from 2,500 units to 1,500 units. Sriperumbudur assembly forecasts a component deficit within 10 days.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Recommends splitting commercial allocation between Continental Device India (`sup-02`) and Sahasra Electronic (`sup-08`, Hyderabad).
  - `inventory-agent`: Suggests drawing down high-density power module stock from Whitefield ICD (`wh-02`).
  - `demand-agent`: Proposes prioritizing telematics gateway production while rationing power modules to tier-1 customers.
  - `transport-agent`: Recommends express trucking from Hyderabad to Sriperumbudur via NH44/NH16.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Split power module shortfall by commissioning auxiliary PCB fabrication runs at Sahasra Electronic (sup-08, Hyderabad) and tap reserves at Whitefield (wh-02)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.899)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+21.1%`
  - Lead Time Impact: `+4.5 days`
  - Cost Delta: `+₹22,800`

---

### scen-10: High-Density PCB Copper Laminate Stockout (Sahasra Hyderabad)

- **Classification**:
  - Disruption Type: `supplier_delay`
  - Target Entity: `sup-08` (Sahasra Electronic Solutions, Shamshabad/Hyderabad)
  - Default Severity: 4 / 5
  - Duration: 8 days
  - Primary Products: `prod-101`, `prod-103`
- **Problem Statement & Use Case**:
  Global raw material shortages cause a 10-day delay in specialized high-frequency copper-clad laminate (CCL) shipments arriving at Hyderabad airport, halting multi-layer PCB fabrication. Evaluates alternative board-fabrication routing.
- **Physical Dynamics & Topology Interaction**:
  Inner-layer etching and laminating presses at Sahasra are paused. Downstream component deliveries to Sri City FTWZ (`wh-04`) are interrupted.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Discovers certified alternate laminate stock available at SPEL Semiconductor (`sup-01`) and Centum Electronics (`sup-05`).
  - `inventory-agent`: Recommends inter-facility raw material transfer to maintain Sahasra's pressing operations.
  - `transport-agent`: Evaluates dedicated air cargo charter from Bengaluru to Hyderabad vs bonded express road transit.
  - `demand-agent`: Confirms assembly schedules can accommodate a 4-day raw material transfer delay.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Execute inter-facility raw material loan from Centum Electronics (sup-05) via air express cargo to resume multi-layer PCB pressing at Sahasra (sup-08)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.915)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+31.1%`
  - Lead Time Impact: `+5.8 days`
  - Cost Delta: `+₹34,000`

---

## Domain 3: Downstream Market Volatility & Demand Shocks

### scen-11: Smart Energy IoT Meter Mandate Demand Surge

- **Classification**:
  - Disruption Type: `demand_spike`
  - Target Entity: `wh-01` (Hosur Logistics Buffer Warehouse)
  - Default Severity: 4 / 5
  - Duration: 21 days
  - Primary Products: `prod-101` (Smart IoT Telematics Gateway)
- **Problem Statement & Use Case**:
  State electricity distribution companies (DISCOMs) in Tamil Nadu and Karnataka issue accelerated deployment mandates for smart energy meters, triggering an 80% demand surge for `prod-101`. Tests long-horizon capacity scaling and multi-supplier expansion.
- **Physical Dynamics & Topology Interaction**:
  Demand backlog grows by 3,200 units/week. Finished goods buffers at Hosur Logistics Warehouse (`wh-01`) are exhausted within 8 days.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `demand-agent`: Recommends doubling manufacturing shifts at Sriperumbudur and raising supplier delivery commitments by 75%.
  - `inventory-agent`: Warns of severe upstream raw component shortages at CDIL (`sup-02`) and SPEL (`sup-01`).
  - `supplier-agent`: Recommends onboarding secondary EMS assembly capacity at Syrma SGS (`sup-04`, Bargur).
  - `transport-agent`: Demands dedicated continuous-loop freight shuttles between Hosur, Bargur, and Sriperumbudur.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Authorize three-shift assembly expansion at Sriperumbudur, activate secondary SMT lines at Syrma SGS (sup-04), and establish daily rolling buffer shuttles."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.884)
  - Escalation Tier: `SLOW_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+40.0%`
  - Lead Time Impact: `+4.4 days`
  - Cost Delta: `+₹42,320`

---

### scen-12: Commercial Fleet EV Powertrain Retrofit Spike

- **Classification**:
  - Disruption Type: `demand_spike`
  - Target Entity: `wh-02` (Whitefield Inland Container Depot)
  - Default Severity: 5 / 5
  - Duration: 28 days
  - Primary Products: `prod-103` (High-Density Power Module)
- **Problem Statement & Use Case**:
  A major commercial logistics fleet operator contracts an emergency retrofit of 10,000 electric delivery vans in Bengaluru, causing a massive 120% demand spike for power electronics modules (`prod-103`). Tests the human escalation threshold under severe supply shortfalls.
- **Physical Dynamics & Topology Interaction**:
  Requested deliveries exceed total peninsular manufacturing capacity by 45%. Whitefield ICD component storage is completely depleted.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `demand-agent`: Advocates accepting full order contract to secure commercial market share.
  - `inventory-agent`: Confirms total stockout within 48 hours for all other commercial customers.
  - `supplier-agent`: Reports Centum (`sup-05`) and Sahasra (`sup-08`) can only meet 55% of required volume even with 24/7 overtime.
  - `transport-agent`: Notes interstate freight capacity will be overwhelmed.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Escalate to Executive Operations: Propose phased customer allocation plan (50% delivery in 14 days, 50% in 45 days) and authorize emergency capacity expansion."`
  - Consensus Status: `ESCALATED_TO_HUMAN` (Disagreement on Customer Rationing vs Stockout Exposure)
  - Escalation Tier: `HUMAN_ESCALATION`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+62.4%`
  - Lead Time Impact: `+7.8 days`
  - Cost Delta: `+₹65,780`

---

### scen-13: Quarter-End Automotive OEM Assembly Ramp-Up

- **Classification**:
  - Disruption Type: `demand_spike`
  - Target Entity: `wh-03` (Oragadam JIT Supplier Warehouse)
  - Default Severity: 3 / 5
  - Duration: 10 days
  - Primary Products: `prod-102` (Automotive Sensor Hub)
- **Problem Statement & Use Case**:
  Chennai automobile assembly plants execute a standard quarter-end production sprint to meet export targets, increasing JIT intake requirements at Oragadam by 35%. Tests high-frequency micro-replenishment logistics.
- **Physical Dynamics & Topology Interaction**:
  Assembly lines at Hyundai, Renault-Nissan, and Daimler in the Oragadam SIPCOT belt increase daily sensor consumption from 1,200 to 1,620 units. JIT warehouse docks experience continuous traffic.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `demand-agent`: Flags predictable quarter-end demand surge lasting exactly 10 days.
  - `inventory-agent`: Recommends pre-positioning finished goods buffer at Sri City FTWZ (`wh-04`) to feed Oragadam.
  - `supplier-agent`: Requests Kaynes Technology (`sup-03`) release safety stock batches.
  - `transport-agent`: Recommends hourly dedicated feeder truck shuttles from Oragadam warehouse to plant gates.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Deploy pre-positioned buffer from Sri City FTWZ (wh-04) and establish hourly dedicated micro-replenishment shuttles into Oragadam plant bays."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.941)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+32.2%`
  - Lead Time Impact: `+3.7 days`
  - Cost Delta: `+₹33,465`

---

### scen-14: Coastal Municipal Sensor Network Renewal Push

- **Classification**:
  - Disruption Type: `demand_spike`
  - Target Entity: `dc-01` (Chennai Port Container Terminal)
  - Default Severity: 3 / 5
  - Duration: 14 days
  - Primary Products: `prod-101` (Smart IoT Telematics Gateway)
- **Problem Statement & Use Case**:
  Smart City infrastructure modernization projects across coastal municipal corporations demand 25,000 environmental telemetry gateways, creating localized distribution center stockout hazards. Tests regional export buffer rebalancing.
- **Physical Dynamics & Topology Interaction**:
  Domestic demand pulls inventory directly from Chennai Port export staging areas, reducing maritime outbound allocations.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `demand-agent`: Proposes diverting 30% of scheduled European export volume to fulfill municipal contracts.
  - `inventory-agent`: Calculates that remaining export buffer at `dc-01` remains above minimum contractual thresholds.
  - `supplier-agent`: Authorizes CDIL (`sup-02`) and SPEL (`sup-01`) to fast-track subsequent replenishment lots.
  - `transport-agent`: Confirms domestic road logistics carriers can handle city distribution.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Reallocate 25% non-critical export staging inventory at Chennai Port (dc-01) to domestic municipal deployment and trigger rapid re-order at SPEL (sup-01)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.927)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+27.5%`
  - Lead Time Impact: `+4.1 days`
  - Cost Delta: `+₹38,640`

---

## Domain 4: Highway, Freight Corridor & Transport Disruptions

### scen-15: Attibele Interstate Border Truck Checkpost Strike

- **Classification**:
  - Disruption Type: `transport_failure`
  - Target Entity: `route-sup-02-wh-01` (Bengaluru Electronic City to Hosur Corridor)
  - Default Severity: 4 / 5
  - Duration: 3 days
  - Primary Products: `prod-101`, `prod-103`
- **Problem Statement & Use Case**:
  An interstate commercial vehicle operators' strike and flash roadblock at the Attibele toll plaza on the Karnataka-Tamil Nadu border halts all container truck traffic on NH44. Evaluates secondary rural arterial detour routing.
- **Physical Dynamics & Topology Interaction**:
  Over 300 transport vehicles are immobilized at the Attibele border crossing. Discrete component flows from CDIL Electronic City (`sup-02`) to Hosur Buffer Warehouse (`wh-01`) cease completely.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Analyzes topographical bypass routes: Detour outbound shipments from Electronic City via Sarjapur-Bagalur rural state highway into Hosur industrial zone.
  - `inventory-agent`: Estimates Hosur warehouse can buffer Sriperumbudur assembly for 48 hours without incoming CDIL stock.
  - `supplier-agent`: Directs CDIL to hold finished goods in secure factory bays until clearance.
  - `demand-agent`: Confirms minimal impact if detour transit delay is capped at 6 hours.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Reroute component transport convoys via Sarjapur-Bagalur arterial detour into Hosur and pre-clear police freight escorts for priority containers."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.938)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+31.3%`
  - Lead Time Impact: `+5.2 days`
  - Cost Delta: `+₹36,112`

---

### scen-16: Palakkad Gap Western Ghats Landslide Corridor Halt

- **Classification**:
  - Disruption Type: `transport_failure`
  - Target Entity: `route-sup-07-mfg-01` (Kochi to Sriperumbudur Intermodal Corridor)
  - Default Severity: 5 / 5
  - Duration: 6 days
  - Primary Products: `prod-101`, `prod-102`
- **Problem Statement & Use Case**:
  Severe monsoon rainfall triggers a major mudslide and boulder collapse in the Palakkad Gap along NH544 between Walayar and Palakkad, completely shutting road and rail transit between Kerala and Tamil Nadu. Tests intermodal coastal maritime rerouting.
- **Physical Dynamics & Topology Interaction**:
  All direct overland freight from SFO Technologies NeST (`sup-07`, Kochi) to Sriperumbudur assembly plant is severed for 6 days. Over 20,000 optical and control sub-assemblies are blocked.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Evaluates alternative routing: Coastal feeder vessel from Cochin Port (`dc-02`) around peninsular India to Chennai Port (`dc-01`) vs Konkan rail route through Mangaluru and Bengaluru.
  - `inventory-agent`: Warns that Sriperumbudur on-site optical inventory will stock out in 4 days.
  - `supplier-agent`: Requests Syrma SGS (`sup-04`, Bargur) produce substitute wire harnesses and control units.
  - `demand-agent`: Endorses high-priority maritime express shuttle.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Commission coastal express container feeder vessel from Cochin Port (dc-02) to Chennai Port (dc-01) and activate substitute wire harness assembly at Syrma (sup-04)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.895)
  - Escalation Tier: `SLOW_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+44.9%`
  - Lead Time Impact: `+8.4 days`
  - Cost Delta: `+₹55,510`

---

### scen-17: NH44 Kurnool Bridge Heavy-Axle Weight Embargo

- **Classification**:
  - Disruption Type: `transport_failure`
  - Target Entity: `route-sup-08-wh-04` (Hyderabad to Sri City Freight Corridor)
  - Default Severity: 3 / 5
  - Duration: 12 days
  - Primary Products: `prod-101`, `prod-103`
- **Problem Statement & Use Case**:
  National Highways Authority of India (NHAI) emergency bridge pier inspection and reinforcement near Kurnool on NH44 restricts freight vehicles with gross weight exceeding 16 tonnes. Evaluates fleet bifurcation and smaller-vehicle logistics.
- **Physical Dynamics & Topology Interaction**:
  Heavy multi-axle 40-tonne container trailers carrying multi-layer PCBs from Sahasra (`sup-08`, Hyderabad) to Sri City FTWZ (`wh-04`) cannot traverse the bridge.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Recommends transloading cargo at Hyderabad into 10-tonne commercial light commercial vehicles (LCVs) or detouring via Guntur and NH16 coastal highway.
  - `inventory-agent`: Calculates cost variance: Coastal detour adds 180 km and 1.5 days transit; transloading adds ₹45,000 handling fees.
  - `supplier-agent`: Approves split dispatch schedules.
  - `demand-agent`: Approves 1.5-day transit variance as buffer stock at `wh-04` is healthy.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Divert freight convoys via Guntur-Nellore NH16 coastal corridor to bypass Kurnool bridge weight restrictions and maintain multi-axle efficiency."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.932)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+24.8%`
  - Lead Time Impact: `+4.5 days`
  - Cost Delta: `+₹31,110`

---

### scen-18: Chennai Outer Ring Road Heavy Freight Gridlock

- **Classification**:
  - Disruption Type: `transport_failure`
  - Target Entity: `route-wh-03-mfg-01` (Oragadam JIT to Sriperumbudur Assembly)
  - Default Severity: 3 / 5
  - Duration: 2 days
  - Primary Products: All Products (`prod-101`, `prod-102`, `prod-103`)
- **Problem Statement & Use Case**:
  A multi-trailer collision and chemical spill on the Chennai Outer Ring Road (CORR) near Mannur halts all commercial transit between Oragadam industrial hub and Sriperumbudur. Tests localized industrial corridor bypasses.
- **Physical Dynamics & Topology Interaction**:
  Continuous JIT component shuttles between Oragadam warehouse (`wh-03`) and Sriperumbudur plant gates are blocked. Assembly plant buffer drops by 4 hours for every hour of blockage.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Immediately routes dedicated small-capacity delivery vans through internal SIPCOT industrial service corridors via Singaperumal Koil and Sriperumbudur back-gate.
  - `inventory-agent`: Signals that Sriperumbudur has only 6 hours of line-side component supply.
  - `supplier-agent`: Alerts SPEL Semiconductor (`sup-01`) to stage direct hot-shot vans.
  - `demand-agent`: Prioritizes high-margin IoT Gateway assembly line continuation.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Deploy internal SIPCOT service road bypass fleet and initiate direct line-side component hot-shot deliveries from SPEL (sup-01) to back receiving gates."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.947)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+30.4%`
  - Lead Time Impact: `+4.9 days`
  - Cost Delta: `+₹35,502`

---

## Domain 5: Warehouse & FTWZ Facility Logistics Shocks

### scen-19: Hosur Buffer Automated AS/RS Crane System Fault

- **Classification**:
  - Disruption Type: `transport_failure` (Internal Facility Logistics)
  - Target Entity: `wh-01` (Hosur Logistics Buffer Warehouse)
  - Default Severity: 4 / 5
  - Duration: 4 days
  - Primary Products: `prod-101`, `prod-102`, `prod-103`
- **Problem Statement & Use Case**:
  A severe programmable logic controller (PLC) failure and mechanical cable derailment paralyzes the automated storage and retrieval system (AS/RS) cranes in Hosur Warehouse's high-bay storage zone, locking 45,000 component totes. Tests secondary warehouse dynamic reassignment.
- **Physical Dynamics & Topology Interaction**:
  Physical access to 60% of inventory stored at `wh-01` is inaccessible. Inbound supplier trucks from Bengaluru and Mysuru face offloading gridlock.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `inventory-agent`: Recommends immediate diversion of inbound shipments to Whitefield ICD (`wh-02`) and Oragadam JIT (`wh-03`).
  - `transport-agent`: Re-routes incoming supplier freight from CDIL (`sup-02`) and Kaynes (`sup-03`) directly to Whitefield.
  - `supplier-agent`: Requests temporary slowdown of palletized deliveries into Hosur.
  - `demand-agent`: Monitors finished product assembly targets at Sriperumbudur.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Divert inbound supplier freight directly to Whitefield ICD (wh-02) and authorize manual staging retrieval for high-priority assembly totes at Hosur."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.916)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+37.7%`
  - Lead Time Impact: `+5.8 days`
  - Cost Delta: `+₹44,896`

---

### scen-20: Sri City FTWZ Regulatory Customs Audit Clearance Hold

- **Classification**:
  - Disruption Type: `supplier_delay` (Regulatory / Bonded FTWZ Hold)
  - Target Entity: `wh-04` (Sri City FTWZ Logistics Center)
  - Default Severity: 4 / 5
  - Duration: 7 days
  - Primary Products: `prod-101`, `prod-103`
- **Problem Statement & Use Case**:
  Customs authorities at the Sri City Free Trade & Warehousing Zone (FTWZ) initiate a mandatory comprehensive compliance audit, placing an administrative hold on all bonded component disbursements for 72 hours. Evaluates duty-paid buffer reallocation and regulatory response.
- **Physical Dynamics & Topology Interaction**:
  Over ₹12,00,00,000 worth of duty-free imported electronic components cannot exit FTWZ gates to reach domestic assembly plants.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `inventory-agent`: Scans the network for non-bonded domestic buffer stock; locates substitute inventory at Oragadam JIT (`wh-03`) and Hosur (`wh-01`).
  - `supplier-agent`: Directs SPEL Semiconductor (`sup-01`) to accelerate domestic duty-paid component release.
  - `transport-agent`: Shifts truck capacity from Sri City to Oragadam routes.
  - `demand-agent`: Computes SLA penalty exposure and supports emergency domestic stock drawdown.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Substitute bonded FTWZ components with domestic safety stock from Oragadam JIT (wh-03) and expedite customs pre-audit reconciliation paperwork."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.892)
  - Escalation Tier: `SLOW_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+25.9%`
  - Lead Time Impact: `+5.7 days`
  - Cost Delta: `+₹29,440`

---

### scen-21: Whitefield Inland Container Depot Rail Rake Deficit

- **Classification**:
  - Disruption Type: `transport_failure` (Intermodal Rail Bottleneck)
  - Target Entity: `wh-02` (Whitefield Inland Container Depot)
  - Default Severity: 3 / 5
  - Duration: 5 days
  - Primary Products: `prod-101`, `prod-102`
- **Problem Statement & Use Case**:
  A regional shortage of specialized container flatbed rail wagons (Container Corporation of India / CONCOR) delays intermodal container movements from Whitefield ICD to Chennai Port. Tests intermodal-to-road freight conversion.
- **Physical Dynamics & Topology Interaction**:
  Over 120 export-bound 40-foot containers accumulate at Whitefield ICD rail sidings. Scheduled rail departures are delayed by 5 days.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Proposes contracting private articulated container tractor-trailers to haul containers along Old Madras Road (NH75) directly to Chennai Port.
  - `inventory-agent`: Calculates holding costs at Whitefield ICD vs road freight premium (+22% per TEU).
  - `demand-agent`: Notes vessel sailing schedules at Chennai Port cannot be missed without severe downstream penalties.
  - `supplier-agent`: Validates container seal integrity and cargo security protocols.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Convert stranded intermodal rail containers to dedicated road freight convoys on NH75 directly to Chennai Port Terminal (dc-01)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.925)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+22.1%`
  - Lead Time Impact: `+3.7 days`
  - Cost Delta: `+₹25,986`

---

## Domain 6: Multimodal Seaport & Airport Terminal Bottlenecks

### scen-22: Chennai Port Shallow Channel Silting Berth Congestion

- **Classification**:
  - Disruption Type: `transport_failure` (Seaport Marine Congestion)
  - Target Entity: `dc-01` (Chennai Port Container Terminal)
  - Default Severity: 3 / 5
  - Duration: 6 days
  - Primary Products: `prod-101`, `prod-102`, `prod-103` (Export Shipments)
- **Problem Statement & Use Case**:
  Post-monsoon littoral sediment drift reduces navigational draft at Chennai Port's Ambedkar Dock container berths, causing maritime vessel queuing and a 4-day discharge delay. Evaluates maritime diversion to Kattupalli/Ennore ports.
- **Physical Dynamics & Topology Interaction**:
  Large mainline container vessels are anchored off Chennai harbor. Container yards exceed 92% yard density, slowing export intake from Sriperumbudur.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Recommends diverting export container trucks from Sriperumbudur to Kattupalli International Container Terminal (35 km north) or Kamarajar Port Ennore.
  - `inventory-agent`: Recommends holding finished goods at Sri City FTWZ (`wh-04`) instead of delivering to congested Chennai port gates.
  - `demand-agent`: Approves vessel feeder transfer to maintain European arrival dates.
  - `supplier-agent`: Verifies export packaging certifications for secondary terminal handling.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Divert outbound container convoys from Chennai Port to Kattupalli Port Terminal and hold intermediate buffers at Sri City FTWZ (wh-04)."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.934)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+25.9%`
  - Lead Time Impact: `+5.4 days`
  - Cost Delta: `+₹40,992`

---

### scen-23: Shamshabad Aerotropolis Airfreight Cargo Crunch

- **Classification**:
  - Disruption Type: `transport_failure` (Airport Airfreight Capacity Crunch)
  - Target Entity: `dc-03` (Hyderabad Air Cargo Gateway, Shamshabad)
  - Default Severity: 4 / 5
  - Duration: 4 days
  - Primary Products: `prod-101`, `prod-103` (High-Value Express Components)
- **Problem Statement & Use Case**:
  A scheduled international widebody freighter cancellation combined with peak pharmaceutical export demand at Hyderabad Rajiv Gandhi International Airport creates a severe 4-day airfreight embargo on electronic micro-modules. Tests airport-to-airport bonded road transfers.
- **Physical Dynamics & Topology Interaction**:
  Express export consignments of IoT gateways and multi-layer PCBs from Sahasra (`sup-08`) are stranded in Shamshabad cargo holding bays.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `transport-agent`: Recommends transferring air cargo consignments via bonded refrigerated trucks along NH44 to Kempegowda International Airport (BLR, Bengaluru) for European flights.
  - `demand-agent`: Confirms transit time to Bengaluru Airport is 11 hours, preserving international delivery commitments.
  - `inventory-agent`: Calculates that air charter freight premiums exceed standard budgets by ₹85,000, but bonded road feeder is cost-effective.
  - `supplier-agent`: Approves tamper-evident GPS container sealing.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Transfer urgent export consignments via bonded GPS-tracked road feeder trucks along NH44 to Bengaluru Kempegowda Airport for onward cargo flight."`
  - Consensus Status: `RESOLVED` (CD2F Competence Weighted: 0.921)
  - Escalation Tier: `FAST_PATH`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+26.7%`
  - Lead Time Impact: `+4.9 days`
  - Cost Delta: `+₹41,000`

---

## Domain 7: Compound Catastrophic & Systemic Crises

### scen-24: Cyclone Michaung Coromandel Plain Compound Inundation

- **Classification**:
  - Disruption Type: `adverse_weather` (Compound Multi-Node Catastrophe)
  - Target Entity: `sup-01` + `dc-01` (Chennai Coastal Belt)
  - Default Severity: 5 / 5
  - Duration: 10 days
  - Primary Products: All Products (`prod-101`, `prod-102`, `prod-103`)
- **Problem Statement & Use Case**:
  A category-4 cyclonic storm makes landfall across the north Tamil Nadu coastline, simultaneously flooding SPEL Semiconductor in Maraimalai Nagar, halting Chennai Port operations, and severing GST Road transit. Tests compound multi-node failure resolution and high-stakes executive escalation.
- **Physical Dynamics & Topology Interaction**:
  Wafer fabrication in Chennai is shut down due to industrial flood barriers. Chennai Port is closed. Sub-assembly inventory at Sriperumbudur drops toward zero while outbound maritime export lanes are completely severed.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `supplier-agent`: Declares total force majeure at `sup-01`; demands complete supplier substitution to Continental Device India (`sup-02`, Bengaluru) and Syrma SGS (`sup-04`, Bargur).
  - `transport-agent`: Reports all Chennai roads flooded; advises rerouting peninsular supply lines through western inland corridors (Salem-Dharmapuri-Bengaluru).
  - `inventory-agent`: Warns that total plant stockout will occur within 36 hours without immediate western sourcing.
  - `demand-agent`: Projects revenue loss exceeding ₹4,50,00,000 across European and North American customer accounts.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Emergency Disaster Protocol: Shift all wafer packaging to CDIL Bengaluru (sup-02), reroute export logistics through Cochin Vallarpadam Port (dc-02), and alert executive operations."`
  - Consensus Status: `ESCALATED_TO_HUMAN` (Severe Enterprise-Level Financial Exposure)
  - Escalation Tier: `HUMAN_ESCALATION`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+68.5%`
  - Lead Time Impact: `+12.5 days`
  - Cost Delta: `+₹98,500`

---

### scen-25: Peninsular Grid Blackout Sourcing Crisis

- **Classification**:
  - Disruption Type: `supplier_delay` (Systemic Infrastructure Blackout)
  - Target Entity: `global` (Peninsular Multi-State Grid)
  - Default Severity: 5 / 5
  - Duration: 5 days
  - Primary Products: All Products (`prod-101`, `prod-102`, `prod-103`)
- **Problem Statement & Use Case**:
  A cascading southern regional power transmission grid failure knocks out industrial electricity across Tamil Nadu, Karnataka, and Andhra Pradesh for 48 hours. Supplier fabs operate on reduced diesel generator capacity (30% to 50% normal throughput). Tests systemic supply rationing and priority order fulfillment.
- **Physical Dynamics & Topology Interaction**:
  Cleanroom wafer fabs, SMT lines, automated warehouses, and port terminals across 18 nodes switch to diesel generator backups. Industrial fuel rationing restricts operations to mission-critical assembly lines.
- **Multi-Agent Deliberation & Fleet Behavior**:
  - `inventory-agent`: Demands freezing all low-margin production and consolidating all remaining component stock behind high-margin Smart IoT Gateways (`prod-101`).
  - `supplier-agent`: Confirms suppliers can maintain only 40% batch output until grid restoration.
  - `transport-agent`: Reports commercial fuel stations facing retail shortages; advises rationing fleet fuel for emergency shuttles.
  - `demand-agent`: Ranks customer contracts by liquidated damages exposure to establish rationing priority.
- **Consensus Arbitration & Action**:
  - Winning Recommendation: `"Executive Sourcing Consensus: Ration component inventory to high-margin contracts (prod-101), consolidate diesel generator reserves at Sriperumbudur, and invoke force majeure clauses."`
  - Consensus Status: `ESCALATED_TO_HUMAN` (Critical Enterprise-Wide Production Rationing)
  - Escalation Tier: `HUMAN_ESCALATION`
- **Outcome Metrics**:
  - Stockout Risk Delta: `+74.2%`
  - Lead Time Impact: `+14.0 days`
  - Cost Delta: `+₹1,25,000`

---

## Performance Benchmark Target Summary

| Metric | Target SLA | Verification Mechanism |
| :--- | :--- | :--- |
| **Fast-Path Latency (P50)** | < 350 ms | Microservice loop benchmark (`scripts/verify_full_loop.py`) |
| **Fast-Path Latency (P90)** | < 500 ms | Automated evaluation suite (`services/evaluation/`) |
| **Consensus Stability (WCS)** | >= 0.880 | CD2F arbitration validator |
| **Inter-Agent Agreement Kappa** | >= 0.850 | Cohen's Kappa score on calibration scenarios |
| **Stockout Risk Delta Range** | +0.0% to +74.2% | Monte-Carlo counterfactual mathematical engine |
| **Cost Variance Unit** | Indian Rupee (₹ / INR) | Formatted via `format_inr` and `en-IN` locale |
