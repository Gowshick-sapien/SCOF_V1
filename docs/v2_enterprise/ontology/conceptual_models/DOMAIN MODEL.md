# SCOF at Enterprise Scale — The Full Domain Model

**Purpose of this document:** Your ideation/SRS/architecture docs scope the MVP to 5 agents (Supplier, Inventory, Transportation, Demand, Coordinator) with Risk, Finance, Sustainability, Weather deferred. That's a defensible thesis cut. This document ignores that cut and answers a different, harder question: *if SCOF were actually deployed to run a real enterprise's supply chain end-to-end, what domains would have to exist, how do they depend on each other, and what "helper" substrate does each one need to function.*

The frank version: the current 5-domain model captures the **flow of goods** reasonably well but treats the supply chain as a closed system floating in a vacuum — no money beyond a stub, no people, no regulation, no factory, no customer, no failure of the system itself. An enterprise supply chain is not a goods-flow graph. It's a goods-flow graph embedded inside a financial system, a legal/regulatory system, a labor system, and an IT system, any one of which can stop the goods from moving even when every "supply chain" variable looks fine.

---

## 1. Domain Taxonomy — Five Tiers

### TIER 1 — Core Operational Domains (the physical/informational flow of goods)

| # | Domain | What it owns | Status in current SCOF |
|---|---|---|---|
| 1 | **Demand** | Sales forecasting, order intake volume, seasonality, promotions | MVP agent (present) |
| 2 | **Supply / Procurement (physical)** | Supplier relationships, lead times, reliability, raw material sourcing | MVP agent (present) |
| 3 | **Inventory** | Stock levels, safety stock, reorder points, warehouse-level positioning | MVP agent (present) |
| 4 | **Transportation / Logistics** | Routing, carrier selection, freight mode, in-transit visibility | MVP agent (present) |
| 5 | **Production / Manufacturing** | BOM explosion, production scheduling, machine/line capacity, work-in-progress | **Absent entirely.** SCOF treats "manufacturer" as a topology node with a location and a product list — it has no agent that reasons about whether the factory can actually produce what Demand wants in the time Inventory needs it. This is a severe gap for any enterprise that manufactures rather than purely trades. |
| 6 | **Distribution / Order Fulfillment** | Pick-pack-ship execution, order-to-delivery SLA, last-mile | **Absent.** Distinct from Transportation — Transportation moves freight between nodes; Fulfillment is the process of turning a customer order into a shipped, confirmed delivery, including partial fulfillment, backorder handling, and split shipments. |
| 7 | **Returns / Reverse Logistics** | RMAs, refurbishment, disposal, restocking of returned goods | **Absent.** No enterprise supply chain operates without a return path, and reverse flows have their own disruption modes (return fraud, refurb capacity, disposal compliance). |
| 8 | **Quality Assurance / Quality Control** | Incoming inspection, in-process QC, outgoing inspection, defect/recall tracking | **Absent.** A supplier can be "on time" (Supplier Agent happy) and still deliver defective stock — QA is the domain that catches what reliability scoring alone cannot. |

### TIER 2 — Financial & Commercial Domains

| # | Domain | What it owns | Status |
|---|---|---|---|
| 9 | **Finance (operational)** | Procurement cost, storage cost, shipping cost, cost-of-delay, margin impact | Post-MVP concept (Finance Agent exists in ideation §10.6, deferred). Current design is a single flat "cost estimator" — real enterprise finance needs AP/AR cash timing, working capital constraints, and credit exposure to suppliers, none of which are modeled. |
| 10 | **Contracts & Commercial Terms** | Supplier contracts, MOQs, pricing tiers, penalty clauses, SLAs | **Absent.** "Supplier reliability" and "contract terms" are different things — a supplier can be reliable but contractually expensive to reroute around (cancellation penalties, exclusivity clauses). |
| 11 | **Pricing / Revenue Management** | Sell-side pricing, discounting, margin floors | **Absent.** Needed because some mitigation decisions (e.g., expedite freight) only make sense relative to the margin on the product being expedited — SCOF currently has no concept of what a product is *worth* to sell, only what it costs to move. |
| 12 | **Customer / Order Management** | Customer master data, order SLAs, contractual delivery commitments, customer tiering (VIP vs. standard) | **Absent.** Without this, the system cannot know that Customer A's order is contractually penalized if late while Customer B's isn't — a critical input to *priority* in the Structured Claim Contract (Section 13.1), which currently has no data source behind it. |
| 13 | **Trade Compliance / Customs** | HS codes, tariffs, export controls, sanctions screening, denied-party lists | **Absent entirely, and this is a serious omission for any cross-border enterprise.** A rerouting decision that looks operationally optimal (route around Supplier X via Country Y) can be illegal or tariff-catastrophic. No amount of CD²F arbitration sophistication substitutes for a hard compliance gate. |

### TIER 3 — Risk & External Environment Domains

| # | Domain | What it owns | Status |
|---|---|---|---|
| 14 | **Risk Intelligence** | Composite risk index across domains | Post-MVP (ideation §10.5), GNN-based, correctly designed as a cross-cutting aggregator rather than a peer domain |
| 15 | **Weather** | Weather-driven disruption signals | Post-MVP concept, listed but no agent — currently just a disruption *type*, not a domain with its own data/reasoning |
| 16 | **Geopolitical / Regulatory Change** | Sanctions regimes, trade wars, policy shifts, port closures for political reasons | **Absent.** Distinct from Trade Compliance (which is "are we following the rules") — this is "the rules are about to change." |
| 17 | **Sustainability / ESG** | Carbon footprint, green-supplier scoring, regulatory ESG reporting | Post-MVP concept (ideation §10.7), narrowly scoped to a "toggle" rather than a real constraint domain |
| 18 | **Market Intelligence / Competitive** | Competitor pricing, market share shifts, substitute-goods pressure | **Absent.** Demand forecasting without competitive context misattributes demand shocks to internal causes. |
| 19 | **Currency / FX** | Cross-border cost volatility, hedging exposure | **Absent, and folded incorrectly into a flat "Finance" cost number.** Any enterprise sourcing internationally has FX risk that changes procurement economics week to week. |

### TIER 4 — Human & Organizational Domains

| # | Domain | What it owns | Status |
|---|---|---|---|
| 20 | **Workforce / Labor** | Warehouse labor availability, driver shortages, strikes, shift capacity | **Absent entirely — and this is one of the most consequential omissions.** Labor disruptions (strikes, shortages, absenteeism) are among the most common real-world supply chain disruptions and SCOF's disruption catalog (ideation §17, `disruptions.yaml`) doesn't include them at all — only supplier delay, transport failure, demand spike, adverse weather. |
| 21 | **Facilities / Asset Management** | Warehouse capacity ceilings, equipment maintenance, machine downtime, forklift/dock availability | **Absent.** Inventory Agent assumes warehouse capacity is a static config number (`capacity_units` in `topology.yaml`) — it isn't; it degrades with equipment failure and maintenance windows. |
| 22 | **IT/OT Infrastructure Health** | ERP uptime, sensor/IoT feed health, data pipeline integrity | **Absent as a domain — present only implicitly as "the system works."** If a data feed silently breaks, every downstream agent reasons confidently on stale data. This is a meta-domain: is the data itself trustworthy. |

### TIER 5 — Governance / Meta Domains

| # | Domain | What it owns | Status |
|---|---|---|---|
| 23 | **Master Data Management (MDM)** | SKU master, entity master data (canonical supplier/product/warehouse IDs), data quality/lineage | **Absent as an owned domain — currently implicit in `topology.yaml`.** At enterprise scale, "what is the canonical definition of this SKU" is itself a governance problem (multiple ERPs, multiple naming conventions), not a config file. |
| 24 | **Human Governance / Approval** | Who owns escalation, sign-off authority, audit accountability | Partially present (Human Approval step in the workflow, ideation §9) but not modeled as a domain with its own state — e.g., no concept of *who* is on call, approval delegation, or escalation timeout behavior. |
| 25 | **Data Governance / Privacy** | Access control, especially for Cross-Org Agent Handoff (ideation §14, post-MVP) | **Absent.** The moment an external partner's agent is in the loop (explicitly planned post-MVP), you need a domain governing what that external agent is and isn't allowed to see. |
| 26 | **Security (Supply Chain Cyber Risk)** | Ransomware exposure at logistics providers/suppliers, data integrity attacks on the agent network itself | **Absent.** Increasingly a top-tier real-world disruption category (a logistics provider's TMS getting ransomwared *is* a transport disruption, but SCOF's disruption catalog has no way to represent "the disruption is that our own tooling is compromised"). |

---

## 2. Dependency Logic — Expanded

Your original sketch was directionally right. Expanded to the full domain set, with the reasoning made explicit:

```
                                   +-----------------------------+
                                   |   MASTER DATA MANAGEMENT     |  <- everything reads canonical
                                   |   (SKU/entity canon, lineage)|     IDs from here; not a "decision"
                                   +-----------------------------+     domain, a substrate domain
                                                  |
        +-----------------------------------------+-----------------------------------------+
        |                                          |                                          |
        v                                          v                                          v
+---------------+                        +------------------+                      +--------------------+
|   PRODUCTION   |<-----------------------|      SUPPLY      |                      |     WORKFORCE       |
| (manufacturing |   raw materials in     | (procurement,    |                      | (labor availability |
|  capacity/BOM) |                        |  producer/broker |                      |  gates Production,  |
+---------------+                        |  network)         |                      |  Inventory, Transport)
        |                                +------------------+                      +--------------------+
        | finished goods out                        |                                          |
        v                                            | inbound flow                            | staffs
+---------------+     supply pull    +------------------+       inbound flow        +--------------------+
|   INVENTORY    |<-------------------|     TRANSPORT     |<--------------------------|  (labor gates ops) |
| (stock, safety |------------------->|  (the connective  |                          +--------------------+
|  stock, WH pos)|   distribution pull|   tissue between   |
+---------------+                    |   every physical    |
        |                            |   node)              |
        | outbound draw              +------------------+
        v                                            |
+---------------+                                    | last-mile
|    DEMAND      |----------------------------------->v
| (forecast,     |                        +--------------------+
|  sales pull)   |                        |  DISTRIBUTION /     |
+---------------+                        |  FULFILLMENT         |
        ^                                +--------------------+
        | sales data feed                          |
+---------------+                                    v
|  CUSTOMER /    |                        +--------------------+
|  ORDER MGMT    |<-----------------------|      RETURNS         |
| (SLAs, tiering)|      returned goods    | (RMA, refurb,        |
+---------------+                        |  disposal)            |
                                          +--------------------+

QUALITY gates every physical handoff above: incoming (Supply->Production/Inventory),
in-process (within Production), outgoing (Distribution->Customer), and return-intake
(Returns). It is not a node in the flow — it's a checkpoint on every arrow.

FINANCE underlies the entire diagram above — every arrow has a cost, and Finance is
what makes "the overall depends on Finance" literally true: no mitigation decision
in CD²F is evaluable without a cost/impact number, and that number comes from Finance.
Finance itself depends on: FX/Currency, Pricing, Contracts & Commercial Terms,
Customer/Order Management (payment terms, credit exposure).

TRADE COMPLIANCE gates SUPPLY and TRANSPORT specifically at every cross-border edge —
not a peer domain, a hard constraint layer that can veto an otherwise-optimal CD²F
recommendation before it's ever surfaced.

RISK / WEATHER / GEOPOLITICAL / SUSTAINABILITY are cross-cutting signal domains —
they inject disruption *into* every node above, they don't sit in the flow themselves.
This is why ideation's Risk Agent design (GNN over the whole graph) is architecturally
correct — it should stay a cross-cutting aggregator, not become a peer node.

IT/OT INFRASTRUCTURE HEALTH and SECURITY sit underneath everything as a reliability
substrate — if this domain fails, every other domain's data becomes untrustworthy,
which is a different failure mode than any disruption in the catalog today.

MASTER DATA MANAGEMENT and HUMAN GOVERNANCE / DATA GOVERNANCE sit above everything as
the substrate that defines what entities mean and who is allowed to decide/see what.
```

### The dependency principle, stated plainly

- **Physical flow domains** (Production → Inventory → Transport → Distribution, with Supply feeding Production/Inventory and Demand pulling from the other end) form the graph's *spine*.
- **Gating domains** (Quality, Trade Compliance, Workforce) don't sit in the spine — they sit *on* specific edges of it and can block flow regardless of what the spine's own agents recommend. This is a different relationship than "depends on" — it's "can veto."
- **Financial domains** underlie the entire spine as a *valuation layer* — nothing in the spine is comparable or arbitrable (which is the entire point of CD²F's confidence × impact weighting) without Finance translating physical outcomes into a common unit.
- **Environmental/risk domains** are *injectors* — they don't consume the spine's output, they generate disruption events that the spine has to react to. This matches how Risk is already designed in your architecture (GNN aggregator), but currently the injector list (Weather, supplier delay, transport failure, demand spike) is missing Workforce, Geopolitical, and Security as injector sources.
- **Governance/substrate domains** (MDM, Human Governance, Data Governance, IT/OT Health) don't participate in the goods-flow logic at all — they define whether the rest of the system's outputs can be *trusted and acted on*. This is the layer most enterprise software efforts under-invest in early and pay for later, because it's invisible until it breaks.

---

## 3. Helpers — Per Domain

Helpers are not domains themselves; they're the datasets, external feeds, or subordinate systems a domain needs to reason well. Your examples (Producers/Brokers helping Supply, Sales Data helping Demand, internal factors helping Transport) generalize like this:

| Domain | Helper(s) it needs | Nature of helper |
|---|---|---|
| Supply | Producer/broker registry, sub-tier supplier network (tier-2/3 visibility), supplier financial health feeds, credit rating data | Dataset + external feed |
| Demand | POS/sales data, promotions calendar, marketing spend calendar, macroeconomic indicators | Dataset + external feed |
| Transport | Carrier APIs, GPS/telematics, port congestion feeds, fuel price feeds, route network topology | Live external feed + internal config |
| Production | BOM data, machine maintenance schedules, labor shift rosters (from Workforce), energy cost/availability | Internal system-of-record + cross-domain dependency |
| Inventory | WMS integration, cycle-count data, shrinkage/loss history | Internal system-of-record |
| Finance | ERP general ledger, AP/AR aging, FX rate feed, bank/treasury position | External feed + system-of-record |
| Trade Compliance | HS code database, denied-party/sanctions lists (OFAC-style), tariff schedules | External regulatory dataset, must be kept current |
| Quality | Inspection records, defect taxonomy, recall databases | Internal system-of-record + external (regulatory recall feeds) |
| Customer/Order Mgmt | CRM data, contract SLA database, customer credit terms | System-of-record |
| Workforce | HRIS/labor scheduling system, union contract terms, local labor law/holiday calendars | System-of-record + external regulatory |
| Risk/Geopolitical | News/event feeds, sanctions/policy trackers, insurer risk indices | External feed, high noise, needs its own filtering layer |
| MDM | Canonical ID cross-reference tables, data lineage/quality scoring | Internal governance system |
| IT/OT Health | Pipeline monitoring, sensor heartbeat logs | Internal observability (this overlaps with your existing D7 Observability layer — it's the same *kind* of thing, applied to source systems instead of agent traces) |

Note the pattern: almost every Tier 3–5 domain's "helper" is an **external, authoritative, frequently-changing dataset** (sanctions lists, FX rates, labor law) rather than something SCOF can synthesize — this is a fundamentally different integration burden than Tier 1's helpers, which are mostly internal systems-of-record you already control.

---

## 4. What This Means for SCOF's Actual Architecture (Frank Assessment)

1. **Your Domain Profile mechanism is the right tool for this, and it already generalizes correctly.** Nothing above requires touching the platform engine per `domain_binding_strategy.md` — each new domain is additive: a new agent block in `agents.yaml`, a new set of disruption types in `disruptions.yaml`, new gating logic expressed in `consensus.yaml`. The architecture doesn't need to change to grow into this; the profile does. That's a genuine strength of the design as documented.

2. **But "additive" is doing a lot of work for the gating domains specifically.** Quality, Trade Compliance, and Workforce aren't just more agents casting votes in CD²F's confidence-weighted arbitration — they're closer to hard constraints that should filter the candidate action space *before* arbitration, not compete inside it. Modeling a sanctions violation as "one more agent claim with low confidence" is wrong; it should be a veto gate. Your current CD²F design (confidence × historical accuracy weighting) has no first-class concept of a hard veto — every current MVP agent is a soft voter. This is worth resolving before any of the gating domains get added, because retrofitting a veto mechanism after agents are used to being pure voters is a bigger change than adding the agents themselves.

3. **The disruption catalog (`disruptions.yaml`) is the shallowest part of the current design relative to enterprise reality.** Four disruption types (supplier delay, transport failure, demand spike, adverse weather) is a reasonable MVP fixture set for validating CD²F's arbitration mechanics, but it's missing entire categories that matter more in practice than weather does: labor disruption, compliance/regulatory disruption, financial disruption (credit hold, FX shock), and infrastructure/security disruption (a ransomwared carrier, a broken data feed). None of these require new platform code — they require the profile's disruption catalog to grow, which is exactly the extensibility your architecture already claims to support. Extending it is a good concrete test of that claim.

4. **Finance is under-modeled relative to how load-bearing it actually is.** The dependency logic above ("the overall depends on Finance") isn't decorative — CD²F's entire arbitration mechanism needs a common unit to compare "restock now" vs. "wait for shipment" vs. "switch supplier," and that unit is cost/impact, which only Finance can supply. Right now Finance is deferred to post-MVP as a peer agent alongside Sustainability and Weather. Structurally it isn't a peer of those — it's closer to infrastructure that the impact scale in `consensus.yaml` already depends on today, even in the MVP. Worth treating as a first-class differently from the other three post-MVP agents.

5. **Master Data Management and IT/OT Health are the domains an enterprise deployment will discover it needs the hard way if they're skipped.** They produce no visible feature and no demo-friendly artifact (unlike the AI Meeting Log or Confidence View), so they're the easiest to deprioritize — and also the ones whose absence causes the most confusing failures later (agents confidently reasoning on stale or misaligned data with no domain responsible for catching it).