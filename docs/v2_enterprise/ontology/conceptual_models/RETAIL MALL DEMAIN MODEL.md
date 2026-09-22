# A Multi-Category Retail Mall — The Full Domain Model

**Case:** A single retail operator (mall-format) selling across four category superclusters — (1) Food/Produce/Grocery, (2) Apparel/Personal Care/Consumables, (3) Home/Appliances/Electronics, (4) Specialty/Misc (~67 category files total). No manufacturing — the enterprise buys finished goods and sells them.

**Frank framing up front:** This is not the same graph as the manufacturing-SCOF model with Production deleted. Retail has domains that don't exist at all in a B2B manufacturing supply chain (Merchandising, Loss Prevention, Promotions-as-a-demand-lever), and it has one problem the manufacturing model never has to face: **the same five domains (Inventory, Supply, Demand, Transport, Finance) must behave in radically different ways depending on which of the four category clusters they're touching.** A demand spike in fresh produce and a demand spike in electronics are not the same *kind* of event — one rots in 72 hours if inventory over-corrects, the other sits on a shelf for a year. Modeling this well means the domains are shared, but their parameters are category-cluster-specific — which maps directly onto your existing Domain Profile mechanism, just nested one level deeper than it currently goes.

---

## 1. Domain Taxonomy — Five Tiers (Retail Version)

### TIER 1 — Core Operational Domains

| # | Domain | What it owns | Manufacturing-SCOF equivalent |
|---|---|---|---|
| 1 | **Demand** | Store-level + channel-level sales forecasting, footfall, basket analysis | Same domain, different data (POS-driven, not order-book-driven) |
| 2 | **Supply / Vendor Management** | Vendor relationships, purchase orders, replenishment terms — split by vendor delivery model (see §2) | Same domain, but "supplier" becomes "vendor" with three distinct delivery patterns instead of one |
| 3 | **Inventory** | DC-level and store-level stock, planogram compliance, shelf-level stockouts | Same domain, but now two-tier (DC + store shelf) instead of one |
| 4 | **Transportation / Logistics** | Vendor→DC inbound freight, DC→store replenishment routing | Same domain, shorter/higher-frequency legs than manufacturing freight |
| 5 | **Merchandising / Category Management** | Assortment planning, planogram design, category mix, private-label sourcing decisions, SKU rationalization | **Replaces Production.** This is the domain that decides *what* gets sold and in what mix — the retail analog of "what do we manufacture," except the decision is "what do we stock," made per category, per season, per store format. |
| 6 | **Store Operations** | Shelf replenishment execution, POS operation, in-store staffing, customer service, shrink counting | **Replaces/extends Distribution.** In manufacturing-SCOF, "Distribution/Fulfillment" ends at a delivery. In retail, it ends at a shelf that a human has to keep full, which is its own execution domain with its own failure modes (understaffed shift → empty shelf despite full DC). |
| 7 | **Omnichannel / E-commerce Fulfillment** | Buy-online-pickup-in-store (BOPIS), ship-from-store, marketplace/delivery-app integration | **New — no equivalent in manufacturing-SCOF.** A parallel fulfillment path that competes with Store Operations for the same inventory pool. |
| 8 | **Returns / Reverse Logistics** | Customer returns (in-store and online), restocking vs. write-off decisioning, vendor return/chargeback processing | Same domain, but retail return *rates* vary enormously by category (apparel/footwear returns can exceed 20-30%; grocery near 0%) — this needs per-cluster parameterization, not a flat rate. |
| 9 | **Quality Assurance / Food Safety** | Expiration date management, food safety compliance, product recall handling, cold-chain integrity checks | Same domain, but split hard by cluster: food safety regulation (health department, FDA-equivalent) applies to Cluster 1 and barely at all to Cluster 3/4; electrical/product safety certification applies to Cluster 3 and barely at all to Cluster 1. |

### TIER 2 — Financial & Commercial Domains

| # | Domain | What it owns | Note |
|---|---|---|---|
| 10 | **Finance (operational)** | Margin by category, markdown cost, shrinkage cost, carrying cost of dead stock | Retail margin structure varies wildly by cluster — grocery runs on thin margin/high velocity, electronics on thicker margin/slower velocity. Finance cannot use one margin model across all 67 categories. |
| 11 | **Vendor Contracts & Trade Terms** | Rebates, co-op advertising funds, volume discounts, chargebacks, vendor scorecards | Retail-specific commercial mechanics that don't exist in B2B manufacturing procurement — co-op ad funds and rebate structures are a major retail profit lever and a major source of vendor-relationship complexity. |
| 12 | **Pricing & Promotions** | Everyday pricing, markdown cadence, seasonal promotions, private-label pricing strategy | **This is the single biggest structural difference from manufacturing-SCOF.** In the manufacturing model, demand spikes are *disruptions the system reacts to*. In retail, most demand spikes are *deliberately engineered by this domain* (a promotion, a markdown, a seasonal push). Promotions & Pricing is therefore not a passive cost input like Finance — it's an active demand-shaping lever that has to coordinate tightly with Inventory and Merchandising *before* the spike happens, not just react after. |
| 13 | **Customer / Loyalty & CRM** | Loyalty program data, membership tiers, omnichannel customer identity, personalized offers | Retail analog of "Customer/Order Management" — but loyalty data is also a demand-forecasting input (member purchase history feeds Demand) and a PCI/privacy-governance concern (feeds Data Governance). |
| 14 | **Trade Compliance / Import Regulation** | Tariffs and customs for imported goods (heavy in Cluster 3 electronics, Cluster 2 apparel), food safety import rules for Cluster 1 | Different flavor than manufacturing's export-control-heavy compliance — retail import compliance is mostly tariff/HS-code and consumer product safety certification (UL, CE, etc.), plus food-specific import rules for grocery. |

### TIER 3 — Risk & External Environment Domains

| # | Domain | What it owns | Note |
|---|---|---|---|
| 15 | **Risk Intelligence** | Composite cross-domain risk aggregator | Same role as manufacturing-SCOF's Risk Agent — cross-cutting, not a peer node |
| 16 | **Weather** | Weather-driven disruption AND weather-driven demand shaping | Dual role in retail: weather disrupts produce supply (Cluster 1) *and* directly drives demand (umbrellas, heaters, patio furniture) — it's both an injector into Supply and an input into Demand, more entangled than in manufacturing. |
| 17 | **Geopolitical / Regulatory Change** | Import tariff shifts, trade policy changes affecting Cluster 2/3 sourcing | Same role, retail-relevant scope narrows mostly to import-heavy categories |
| 18 | **Sustainability / ESG** | Packaging waste, food waste (huge in Cluster 1), private-label sourcing ethics/audits | Retail-specific weight shift: food waste diversion and packaging are a bigger sustainability lever here than carbon-in-freight is |
| 19 | **Market Intelligence / Competitive** | Competitor pricing, local competitor footfall, category-level market share | More load-bearing in retail than in B2B manufacturing — retail pricing decisions are made in near-real-time relative to competitor moves |
| 20 | **Currency / FX** | Import cost volatility for Cluster 2 (apparel) and Cluster 3 (electronics) sourcing | Barely relevant to Cluster 1 (mostly domestic/local sourcing for fresh grocery), highly relevant to Cluster 3 |

### TIER 4 — Human & Organizational Domains

| # | Domain | What it owns | Note |
|---|---|---|---|
| 21 | **Workforce / Labor** | Store staffing levels, seasonal/holiday hiring surges, shift scheduling, high-turnover management | Retail labor has a distinct pattern manufacturing doesn't: extreme seasonality (holiday hiring 2-3x baseline) and high turnover — this is a disruption *category* on its own, not a minor input. |
| 22 | **Facilities / Asset Management** | Store facility upkeep, refrigeration/freezer equipment (Cluster 1 critical — equipment failure = immediate spoilage loss), POS hardware | Refrigeration failure is a Cluster-1-specific catastrophic-and-fast-acting disruption mode with no equivalent severity in Cluster 3/4. |
| 23 | **IT/OT Infrastructure Health** | POS system uptime, e-commerce platform uptime, payment processing uptime | POS downtime is a direct, immediate, store-wide revenue-stop event in a way that's more acute than most manufacturing IT failures. |

### TIER 5 — Governance / Meta Domains

| # | Domain | What it owns | Note |
|---|---|---|---|
| 24 | **Master Data Management (MDM)** | SKU/UPC/GTIN master across ~67 category files, cross-vendor product matching, planogram data lineage | This is a much bigger practical burden here than in the manufacturing model — 67 category files across 4 superclusters means an enormous, heterogeneous SKU universe with different attribute schemas per category (a grocery SKU needs expiration/lot data; an apparel SKU needs size/color matrix; an electronics SKU needs serial/warranty data). One flat `topology.yaml`-style schema will not hold all of this cleanly — it needs category-cluster-specific schema extensions. |
| 25 | **Human Governance / Approval** | Store manager vs. regional vs. HQ approval authority for markdowns, reorders, escalations | Same role as manufacturing model, but with a much flatter, higher-frequency approval cadence (store-level decisions happen constantly, at low individual stakes) |
| 26 | **Data Governance / Privacy** | Customer loyalty/PII data, payment data (PCI-DSS), employee data | Materially higher-stakes here than in B2B manufacturing-SCOF because of direct consumer PII and payment data at scale |
| 27 | **Security / Loss Prevention** | Shoplifting, employee theft, organized retail crime, cyber (POS breach, card skimming), e-commerce fraud | **New tier-5 domain with no equivalent in manufacturing-SCOF.** Physical shrinkage from theft is a first-order retail cost category (frequently 1-2% of revenue) that has no analog in a B2B manufacturing supply chain — it deserves to be a named domain, not folded into "Security" as an afterthought. |

### TIER 6 — Real-Estate Layer (only if "mall" means multi-tenant, not single-operator)

Your prompt describes one operator selling across all four category clusters, which reads as a single large-format retailer (hypermarket/department-store), not a landlord leasing space to independent tenants. If it's actually the latter (a mall leasing space to independent stores), an entirely separate domain layer appears that's outside the scope of the above:

| # | Domain | What it owns |
|---|---|---|
| 28 | **Real Estate / Leasing** | Tenant leases, rent structures (base + % of sales), common area maintenance, anchor-tenant relationships |
| 29 | **Tenant Relationship Management** | Tenant mix strategy, tenant sales reporting/compliance, tenant-level risk (a tenant going out of business is a "supplier" disruption at the leasing level) |

Worth confirming which model this actually is before building further, since it changes whether the Domain Profile represents *one retailer's operations* or *a landlord's tenant portfolio* — materially different systems.

---

## 2. The Category-Cluster Differentiation Problem

This is the part that doesn't exist in the manufacturing-SCOF model at all: the same domain needs fundamentally different tuning per cluster. Treating all 67 category files with one set of thresholds will produce a system that's simultaneously too conservative for groceries and too aggressive for electronics.

| Dimension | Cluster 1: Food/Grocery | Cluster 2: Apparel/Personal Care | Cluster 3: Home/Electronics | Cluster 4: Specialty/Misc |
|---|---|---|---|---|
| **Shelf life / obsolescence** | Hours to weeks (extreme) | Seasonal (weeks to months) | Slow (years), but tech obsolescence risk | Long tail, mixed (garden = seasonal, hardware = evergreen) |
| **Replenishment frequency** | Daily, sometimes multiple/day | Weekly | Weekly to monthly | Highly variable |
| **Vendor delivery model** | Mostly Direct-Store-Delivery (DSD) — vendor trucks straight to store, bypassing DC | Mostly DC-distributed | Mostly DC-distributed, drop-ship common for large appliances | Mixed — drop-ship common for long-tail SKUs |
| **Demand volatility driver** | Weather, spoilage-driven markdowns, local events | Season/fashion cycle, trend | Promotions, new product launches, holiday gifting | Hobby seasonality (garden = spring, toys = holiday) |
| **Return rate** | Near zero | High (20-30%+, size/fit driven) | Moderate (defect/buyer's-remorse driven) | Low-moderate, category-dependent |
| **Primary QA concern** | Food safety, cold chain, expiration | Fit/defect, sizing accuracy | Product safety certification, warranty/serial tracking | Category-specific (auto parts fitment, pet food safety) |
| **Shrinkage risk profile** | Spoilage-dominated | Theft-dominated (small, high-value items) | Theft-dominated (highest per-unit-value theft target) | Mixed |
| **Import/FX exposure** | Low (mostly domestic/local) | High | Very high | Mixed |
| **Margin structure** | Thin, high-velocity | Moderate, markdown-heavy | Thick, promotion-sensitive | Highly variable |

**Implication for the platform architecture:** Your existing Domain Profile pattern (`profiles/<name>/topology.yaml`, `agents.yaml`, `consensus.yaml`, etc.) is designed for *one profile per deployment*. A retail enterprise like this needs the profile concept to go one level deeper — either (a) four sub-profiles (one per cluster) composed under one enterprise profile, each with its own `consensus.yaml` thresholds and disruption catalog, or (b) a single profile where every relevant YAML file is keyed by category-cluster rather than flat. Option (a) is cleaner and matches your "profile is additive, not a rewrite" principle better — it lets a grocery-specific consensus tuning (narrow fast-path, aggressive spoilage escalation) coexist with an electronics-specific one (wide fast-path, promotion-driven demand tolerance) without either domain's agents needing to reason about the other cluster's rules.

---

## 3. Dependency Logic — Retail Version

```
                          +------------------------------+
                          |   MASTER DATA MANAGEMENT       |  <- canonical SKU/UPC/GTIN across
                          |   (per-cluster schema exts)     |     all 4 clusters; substrate, not
                          +------------------------------+     a decision domain
                                          |
     +-------------------------------------+-------------------------------------+
     |                                     |                                     |
     v                                     v                                     v
+---------------+          +------------------------+                +--------------------+
| MERCHANDISING /|         |     SUPPLY / VENDOR      |                |      WORKFORCE       |
| CATEGORY MGMT  |-------->|     MANAGEMENT           |                | (staffs Store Ops,   |
| (assortment,   | assort- | (DSD / DC-distributed /  |                |  gates seasonal       |
|  planogram)    | ment    |  drop-ship, per cluster) |                |  surge capacity)      |
+---------------+ decision +------------------------+                +--------------------+
     |                                     |                                     |
     | planogram                           | inbound flow                       | staffs
     v                                     v                                     v
+---------------+          +------------------------+                +--------------------+
|   INVENTORY    |<---------|      TRANSPORT           |<---------------|  (labor gates all     |
| (DC + store-   |--------->|  (vendor->DC, DC->store, |                |   downstream exec)    |
|  shelf, 2-tier)|          |   or DSD direct-to-store)|                +--------------------+
+---------------+          +------------------------+
     |            \
     | outbound     \ shelf execution
     | draw          v
     v          +----------------+        +--------------------------+
+---------------+| STORE          |        |  OMNICHANNEL /            |
|    DEMAND      || OPERATIONS     |------->|  E-COMMERCE FULFILLMENT   |
| (POS, footfall,|| (shelf stock,  |        |  (competes for same       |
|  forecast)     || staffing exec) |        |   inventory pool)         |
+---------------+ +----------------+        +--------------------------+
     ^                     |                              |
     |                     v                              v
+---------------+   +----------------+          +--------------------+
| PRICING &      |   |    RETURNS      |<---------|    CUSTOMER /        |
| PROMOTIONS     |   | (rate varies    |          |    LOYALTY & CRM     |
| (ACTIVE demand |   |  hugely by      |          | (identity, history,  |
|  lever, not    |   |  cluster)       |          |  feeds Demand)       |
|  passive input)|   +----------------+          +--------------------+
+---------------+
     ^
     | drives (not reacts to)
     +---------------- DEMAND (feedback loop — this is the retail-specific
                        inversion: Promotions deliberately creates the spike
                        that manufacturing-SCOF's Demand Agent only detects)

QUALITY / FOOD SAFETY gates every physical handoff, but its intensity is cluster-
dependent: near-mandatory hard gate on Cluster 1 inbound/shelf, lighter-touch
certification check on Cluster 3, largely absent on most of Cluster 2/4.

FINANCE underlies everything, but margin/markdown/shrinkage math must be evaluated
per-cluster — a single blended margin number across all 67 categories would make
CD²F-style impact scoring meaningless (a $500 electronics markdown and a $500
produce write-off are very different signals).

LOSS PREVENTION / SECURITY gates Inventory (shrinkage adjustment) and Finance
(loss cost) — heaviest on Cluster 2 (small/valuable apparel accessories) and
Cluster 3 (high-value electronics), lightest on Cluster 1.

TRADE COMPLIANCE / IMPORT REGULATION gates Supply specifically for Cluster 2 and
Cluster 3 vendors sourcing overseas — largely irrelevant to Cluster 1's typically
domestic/local produce and grocery vendors.

WEATHER is unusual here: it's simultaneously a disruption injector into SUPPLY
(Cluster 1 crop/produce disruption) and a direct driver of DEMAND (seasonal goods
across Cluster 2-4) — it touches the graph at two different points, not one.

RISK, GEOPOLITICAL, FX, MARKET INTELLIGENCE remain cross-cutting injectors, same
role as in the manufacturing model, but their relevance weight differs sharply by
cluster (FX matters enormously to Cluster 3, barely at all to Cluster 1).
```

---

## 4. Helpers — Per Domain (Retail-Specific)

| Domain | Helper(s) it needs | Nature |
|---|---|---|
| Supply / Vendor Mgmt | Vendor master (per delivery model: DSD/DC/drop-ship), vendor scorecards, vendor financial health | Dataset + internal system-of-record |
| Demand | POS transaction feed, loyalty/CRM purchase history, footfall counters, local event calendar | Live internal feed + external (foot traffic sensors) |
| Merchandising | Planogram software data, category performance analytics, competitive assortment scans | Internal system-of-record + external market intel |
| Pricing & Promotions | Competitor price feeds, elasticity models per category, promo calendar | External feed + internal analytics |
| Inventory | WMS (DC level) + store-level perpetual inventory / cycle counts | Internal system-of-record, two-tier |
| Transport | Carrier APIs (for DC-distributed), DSD vendor delivery schedules, route optimization for store network | External feed + internal scheduling |
| Quality / Food Safety | Health department inspection records, expiration/lot tracking, recall notification feeds (FDA-equivalent) | External regulatory feed, must-be-current |
| Trade Compliance | HS code / tariff schedule database, product safety certification registries (UL/CE-equivalent) | External regulatory dataset |
| Workforce | Labor scheduling system, local labor law/holiday calendars, seasonal hiring pipeline data | Internal system-of-record + external regulatory |
| Loss Prevention / Security | POS exception reporting, CCTV/EAS (electronic article surveillance) event logs, known-offender databases | Internal system-of-record + external (law enforcement/industry shared databases) |
| Facilities | Refrigeration/HVAC monitoring (IoT sensors), maintenance ticketing system | Internal IoT/observability feed |
| MDM | Vendor product catalogs (GS1/UPC registries), category-specific attribute schemas | External standards registry + internal governance |
| Customer/Loyalty | CRM platform, payment processor data (PCI-scoped) | Internal system-of-record, privacy-sensitive |
| Sustainability/ESG | Food waste diversion tracking, packaging material sourcing data | Internal system-of-record + external certification bodies |

---

## 5. Frank Assessment — What This Case Changes Structurally

1. **The demand-disruption relationship inverts for large parts of the business.** In manufacturing-SCOF, a demand spike is something that happens *to* the system. In retail, a large share of demand spikes are *caused by* the Pricing & Promotions domain on purpose. Any consensus/arbitration mechanism built assuming demand is exogenous will misclassify a deliberate, planned promotional spike as an anomaly requiring escalation — that's a false-positive generator if not handled as a distinct signal type from the start.

2. **Perishability makes Cluster 1 fundamentally time-critical in a way nothing in the manufacturing model is.** A fast-path/slow-path escalation tiering tuned around cost impact and confidence (as in your existing CD²F design) needs a genuinely different clock for spoiling produce than for a slow-moving appliance — the "impact" isn't just magnitude, it's magnitude *decaying against a countdown*, which isn't well captured by a static impact scale (`negligible/low/medium/high/critical`) alone.

3. **Loss Prevention/Shrinkage is a first-order cost category here with no equivalent weight in B2B manufacturing.** It deserves the same seriousness as Supplier reliability got in the original SCOF design — it's not a footnote under "Security."

4. **MDM is harder here, not easier, despite retail feeling "simpler" than manufacturing on the surface.** 67 category files across 4 structurally different superclusters is a wider, messier SKU universe than a manufacturer's typically narrower, more controlled product line (SCOF's own MVP profile example is 3-5 products). This is worth taking seriously before assuming the retail case is a simplification of the manufacturing one — in the MDM/category-heterogeneity dimension, it's actually harder.

5. **The "mall" framing needs resolving before further design.** If this is genuinely a single retailer running all four clusters, the model above holds as-is. If it's a landlord leasing to independent tenant retailers, an entirely separate Real Estate/Leasing domain layer (Tier 6 above) becomes primary and most of Tiers 1-2 belong to the *tenants*, not the platform operator — a materially different system to design for.