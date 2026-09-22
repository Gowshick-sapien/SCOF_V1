# SCOF — Practical Six-Domain Scope

**Domains in scope:** Demand · Supply/Vendor Management · Inventory · Transportation · Finance · Risk & Environment

**Frank framing:** This is a deliberate narrowing from the 26+ domain enterprise model to something actually buildable inside SCOF's existing architecture. Each of the six stays a single agent/claim-source in the CD²F sense. Everything else — pricing, vendor contracts, weather, trade compliance, seasonality — lives as an **internal sublayer** feeding that agent's structured claim, not as a new agent. This keeps the claim bundle small (CD²F's arbitration math and the LangGraph graph size both depend on that) while still letting each domain reason with real depth internally.

One flag before the detail: your project memory currently shows four built specialist agents — Transport, Financial, Inventory, Supplier — with no Demand agent yet in place. This document treats Demand as a full sixth domain per your instruction, but that's a live gap between what's documented here and what's actually running.

---

## 1. The Six Domains, Each With Its Internal Sublayers

### 1.1 DEMAND

| Sublayer | What it reasons about |
|---|---|
| Sales/Transaction Layer | Raw volume by SKU/category/channel, the ground-truth signal everything else in Demand is built from |
| Forecasting Layer | Statistical + ML prediction — baseline trend, decomposed seasonality, confidence bounds |
| Customer Behavior & Segmentation Layer | Purchase pattern, repeat-buy frequency, basket composition, loyalty-tier behavior differences |
| Seasonal / Cultural Calendar Layer | Maps calendar events (festivals, holidays, regional observances) to category-level demand shifts — detailed in §3 below |
| Promotional Response Layer | How demand elasticity responds to a price/promo signal coming from Finance's Pricing sublayer — this is a *response* model, not the pricing decision itself |
| Channel Split Layer | In-store vs. online demand split, kept as a signal inside Demand rather than a separate fulfillment domain |

**Internal helpers** (owned/generated inside Demand): POS/transaction archive, loyalty/CRM purchase history, internal promo-response history.
**External helpers** (Demand consumes but doesn't own): festival/holiday calendar data, weather forecast (from Risk & Environment), competitor pricing signal (from Risk & Environment's Market Intelligence sublayer), macro indicators.

**Connects to:**
- → **Supply**: forecast sizes procurement volume and timing
- → **Inventory**: forecast sets safety stock and reorder targets
- → **Transportation**: anticipated demand surges require pre-booked capacity
- ↔ **Finance**: Pricing/Promotions sublayer and Demand's Promotional Response Layer are a closed loop — Finance proposes a price/promo, Demand predicts the response, and that response feeds back into Finance's margin math
- ← **Risk & Environment**: weather and calendar-correlated risk modulate the confidence of Demand's own forecast

---

### 1.2 SUPPLY / VENDOR MANAGEMENT

| Sublayer | What it reasons about |
|---|---|
| Vendor Master/Registry | Vendor identity, category coverage, delivery model (direct, DC-routed, drop-ship) |
| Vendor Reliability & Performance Scoring | On-time %, defect rate, rolling historical accuracy — the input CD²F's confidence-weighting already expects |
| Procurement / Purchase Order Layer | PO lifecycle, quantities, lead times |
| Vendor Capacity & Flex Layer | How much a given vendor can scale up/down on short notice — critical for seasonal surge planning (see §3) |
| Alternate Sourcing Layer | Backup/substitute vendor options if the primary is constrained |
| Trade/Import Sub-Check | A lightweight tariff/customs applicability lookup per vendor — kept as a check *within* Supply, not a standalone compliance domain, per current scope |

**Internal helpers:** vendor scorecards, PO system, delivery history log.
**External helpers:** producer/broker network data, supplier financial-health signals, tariff/customs schedule lookup (external dataset, referenced not owned).

**Connects to:**
- ← **Demand**: receives the forecast that sizes purchase orders
- → **Inventory**: fulfills replenishment pulls
- → **Transportation**: PO schedule drives inbound freight booking
- ↔ **Finance**: Vendor Contracts & Trade Terms sublayer (rebates, payment terms, penalty clauses) lives conceptually at this boundary — owned by Finance, read by Supply
- ← **Risk & Environment**: vendor-region weather/geopolitical disruption injects directly into Supply's reliability scoring

---

### 1.3 INVENTORY

| Sublayer | What it reasons about |
|---|---|
| Stock Position Layer | Current on-hand position — single- or multi-echelon depending on deployment (one warehouse tier for pure B2B, DC+shelf for retail-flavored deployments) |
| Safety Stock & Reorder Point Layer | Thresholds that trigger replenishment, tunable per SKU/category |
| Perishability / Shelf-Life Layer | Expiration-driven urgency adjustment — matters enormously for short-shelf-life goods (directly relevant to the festival example in §3) |
| Shrinkage/Loss Adjustment Layer | A correction factor for loss (theft, spoilage, damage) applied to stated stock — kept as an adjustment inside Inventory, not a standalone Loss Prevention domain |
| Storage Capacity Layer | Physical ceiling constraints on how much can actually be held |

**Internal helpers:** WMS/perpetual inventory system, cycle-count data.
**External helpers:** minimal — Inventory is mostly fed by Supply (inbound) and Demand (outbound draw) rather than external data sources of its own.

**Connects to:**
- ← **Supply**: inbound replenishment
- ← **Demand**: outbound draw, stockout risk signal
- ↔ **Transportation**: movement of stock between storage echelons
- → **Finance**: carrying cost, markdown/write-off cost feed directly into Finance's cost-margin sublayer
- → **Risk & Environment**: current stock position is itself an input to the Risk Intelligence aggregator (a thin-inventory position raises composite risk)

---

### 1.4 TRANSPORTATION

| Sublayer | What it reasons about |
|---|---|
| Route Network Layer | Nodes, lanes, mode options (road/air/sea/rail as relevant) |
| Carrier/Fleet Management Layer | Which carriers are available, their reliability, contracted capacity |
| In-Transit Visibility Layer | Live tracking, ETA prediction |
| Peak/Surge Capacity Layer | Pre-booking capacity ahead of anticipated demand spikes — the transportation-side twin of Supply's Vendor Capacity & Flex Layer |
| Delay/Disruption Prediction Layer | Route-level delay forecasting, rerouting option generation |

**Internal helpers:** TMS, route optimization engine, historical transit-time log.
**External helpers:** carrier APIs/GPS telematics, port/road congestion feeds, fuel price feed (read from Finance).

**Connects to:**
- ← **Supply**: inbound leg (vendor → warehouse)
- ↔ **Inventory**: inter-warehouse/replenishment leg
- ← **Demand**: anticipated surge drives capacity pre-booking
- → **Finance**: freight cost, fuel price exposure
- ← **Risk & Environment**: weather and geopolitical disruption to specific routes

---

### 1.5 FINANCE

| Sublayer | What it reasons about |
|---|---|
| Core Finance / Cost-Margin Layer | Procurement cost, storage cost, shipping cost, margin by category — the base valuation math |
| Vendor Contracts & Trade Terms Layer | Rebates, payment terms, penalty clauses, MOQ commitments — the commercial terms Supply operates under |
| Pricing & Promotions Layer | Sell-side pricing, markdown cadence, promo funding decisions |
| Working Capital / Cash Flow Layer | Funding capacity for bulk/seasonal buying, credit exposure to vendors |
| Cost-of-Delay / Impact Valuation Layer | Converts every other domain's physical outcome into the common cost unit CD²F's impact scoring actually consumes |

**Internal helpers:** ERP general ledger, margin calculators, AP/AR aging.
**External helpers:** FX rate feed (from Risk & Environment's Currency sublayer), competitor pricing intelligence (from Risk & Environment's Market Intelligence sublayer).

**Connects to:** all five other domains. This is the one domain where "connects to everything" is structurally correct rather than sloppy scoping — Finance is the valuation layer every other domain's decision has to pass through before CD²F can compare it against alternatives at all. This matches what you originally stated: "the overall depends on Finance."

---

### 1.6 RISK & ENVIRONMENT

| Sublayer | What it reasons about |
|---|---|
| Risk Intelligence Layer | Composite aggregator pulling signal from the other five domains into a single risk index (the GNN-based design your architecture doc already specifies) |
| Weather Layer | Forecast-driven disruption injection — and, as noted in the retail case, a direct demand driver in its own right |
| Geopolitical/Regulatory Layer | Trade policy and tariff shifts, feeding Supply's Trade/Import Sub-Check |
| Market Intelligence / Competitive Layer | Competitor pricing and positioning, feeding both Demand's forecast and Finance's Pricing sublayer |
| Currency/FX Layer | Cross-border cost volatility, feeding Finance directly |
| Calendar/Event Risk Layer | The risk-side counterpart to Demand's Seasonal/Cultural Calendar Layer — e.g., the stockout or overstock risk correlated with a known upcoming festival, not the demand shift itself |

**Internal helpers:** risk-scoring model (GNN over the cross-domain signal graph).
**External helpers:** weather API, geopolitical/news feed, FX rate feed, competitor price signal feed.

**Connects to:** all five other domains, but as an **injector**, not a consumer — Risk & Environment generates disruption/context signals that the other five react to; it doesn't have physical or financial state of its own to protect.

---

## 2. Cross-Domain Relationship Map (Six Domains Only)

```
                         +-------------------------+
                         |   RISK & ENVIRONMENT      |
                         |  (Weather, Geopolitical,   |
                         |   FX, Market Intel,        |
                         |   Calendar/Event Risk)     |
                         +-------------------------+
                          |     |      |      |     |
              injects     |     |      |      |     |   injects
        into Demand       |     |      |      |     |   into Transport
         forecast conf.   v     |      |      v     |
+---------------+   +-----------+   +------------+   +---------------+
|    DEMAND      |   |   SUPPLY    |   | INVENTORY   |   | TRANSPORTATION |
| (Sales,        |-->| (Vendor     |-->| (Stock,     |<->| (Routes,       |
|  Forecast,     |   |  Mgmt, PO,  |   |  Safety     |   |  Carriers,     |
|  Seasonal/     |   |  Reliability|   |  Stock,     |   |  Surge         |
|  Cultural cal.)|   |  Scoring)   |   |  Perishab.) |   |  Capacity)     |
+---------------+   +-----------+   +------------+   +---------------+
        ^                  ^               |                  |
        | promo response   | contract terms| cost              | freight cost
        |                  |               v                  v
        +------------------+------->  +-------------------------+
                                       |         FINANCE           |
                                       | (Cost/Margin, Vendor       |
                                       |  Contracts, Pricing/Promo, |
                                       |  Working Capital,          |
                                       |  Impact Valuation)         |
                                       +-------------------------+

Notes on the diagram:
- Demand -> Supply -> Inventory -> Transportation is the physical/informational
  spine, same as the manufacturing model, just with Supply relabeled Vendor Mgmt.
- Finance sits underneath all four spine domains as the valuation layer every
  claim gets costed through before CD2F can arbitrate between them.
- Risk & Environment sits above all five as a signal injector, touching Demand
  (forecast confidence), Supply (vendor-region disruption), Transportation
  (route disruption), Inventory (indirectly, via stockout/overstock risk
  scoring), and Finance (FX, competitive pricing pressure).
- Finance <-> Demand and Finance <-> Supply are drawn as closed loops
  deliberately: Pricing/Promotions (Finance) <-> Promotional Response (Demand)
  is one loop; Vendor Contracts (Finance) <-> Vendor Reliability (Supply) is
  the other. Both are two-way, not one-way dependencies.
```

---

## 3. Seasonal / Cultural Behavior — Deep Dive on Demand, With Propagation

This is the sublayer you specifically called out, and it deserves to be modeled as a first-class internal mechanism inside Demand's Seasonal/Cultural Calendar Layer, not a one-off adjustment.

### 3.1 The core mechanism

A **Calendar-to-Category Demand Map** — a structured table, not a black-box model — that associates upcoming calendar events with expected category-level demand multipliers, region-specific and lead-time-aware:

| Event | Category most affected | Typical demand behavior | Lead time before event demand builds |
|---|---|---|---|
| Diwali | Sweets/confectionery, gifting items, electronics, home decor/lighting | Sharp multi-week ramp, peaks 2-3 days before, near-zero after | 2-4 weeks |
| Regional festival season (e.g., Pongal, Onam, Eid, Christmas) | Apparel, footwear | Sustained multi-week elevation, less spike-shaped than Diwali sweets | 3-6 weeks |
| Monsoon onset | Umbrellas, rainwear, waterproofing goods (and, on the Supply side, produce disruption risk) | Regional, weather-triggered rather than calendar-fixed — needs the Weather sublayer's forecast, not just the calendar date | Days, not weeks — much shorter lead time than a fixed festival |
| Back-to-school / academic calendar | Stationery, bags, uniforms | Sharp, narrow window, tightly bound to a fixed regional academic calendar date | 2-3 weeks |

The key modeling point: **this is not one universal seasonality curve** — it's a category-specific, event-specific, lead-time-specific table, and the lead time before demand builds is itself a critical parameter (a festival with a 4-week demand ramp needs Supply and Transport decisions made a month out; a monsoon-triggered spike needs decisions made in days).

### 3.2 The propagation chain — worked example (Diwali, sweets)

This is the piece worth being explicit about, because it's exactly the kind of thing CD²F's escalation tiering (fast-path/slow-path, ADR 005) needs to handle differently from a reactive disruption:

1. **Demand** (Seasonal/Cultural Calendar Layer): 3-4 weeks out, the calendar map flags a known, high-confidence demand ramp for sweets/confectionery. Unlike a disruption, this claim starts with *high* confidence and *long* lead time — a fundamentally different profile from "supplier just failed."
2. **Supply**: receives the elevated forecast and checks Vendor Capacity & Flex — can the sweets vendor(s) actually scale production that much on 3-4 weeks' notice? If not, Alternate Sourcing Layer needs to identify secondary vendors *before* the peak, not react during it.
3. **Inventory**: Perishability/Shelf-Life Layer is the binding constraint here — sweets have a short shelf life, so Inventory can't simply pre-build stock weeks early the way it could for a durable good. This changes the shape of the whole chain: the safety-stock response has to be timed tightly against the event date, not just sized larger.
4. **Transportation**: Peak/Surge Capacity Layer needs freight capacity pre-booked for the compressed delivery window right before the event — generic route capacity assumptions from the rest of the year don't hold.
5. **Finance**: Working Capital layer needs to fund the bulk seasonal buy ahead of the revenue it generates (cash goes out weeks before the peak sales come in), and Pricing/Promotions may run a festival-specific promotional plan that feeds back into Demand's Promotional Response Layer, adjusting the forecast further.
6. **Risk & Environment**: Calendar/Event Risk Layer tracks the downside — what happens if the forecast overshoots (unsold, spoiled sweets post-Diwali) or undershoots (stockout during peak, lost revenue and customer goodwill) — and feeds that risk back into the Risk Intelligence composite score, which should modulate how aggressively CD²F treats this claim (a known, recurring, well-characterized seasonal event should arguably sit toward the fast-path end of escalation, precisely *because* it's high-confidence and well-understood — the opposite of a novel disruption, which starts low-confidence and needs slow-path discussion).

### 3.3 The same mechanism, briefly, for the other five domains

You asked for "similarly for other domains too" — each of the other five has its own contextual/behavioral sublayer that responds to the same calendar signal, but from its own angle rather than duplicating Demand's forecast:

- **Supply's behavioral analog:** vendors have *their own* seasonal capacity constraints independent of your demand forecast — a sweets vendor is also fielding surge orders from other retailers at the same time. Vendor Capacity & Flex needs its own seasonal profile, not just a pass-through of Demand's number.
- **Inventory's behavioral analog:** perishability interacts with seasonality directly — the same calendar event that spikes demand for a short-shelf-life good (sweets) has a completely different inventory posture than one that spikes demand for a durable good (festival-season clothing, which can be pre-built weeks out without spoilage risk).
- **Transportation's behavioral analog:** peak-season freight rates and congestion rise independent of your specific order volume — a shared, market-wide seasonal effect Transportation's Peak/Surge layer needs to price in even before your own booking adds to it.
- **Finance's behavioral analog:** working capital needs its own seasonal cash-flow curve — cash goes out ahead of festival buying and comes back after, and this rhythm repeats predictably year over year, which is itself a plannable pattern rather than a one-off spike.
- **Risk & Environment's behavioral analog:** the Calendar/Event Risk Layer isn't just downside risk on Demand's forecast — recurring seasonal events also correlate with their *own* known disruption patterns (e.g., festival-season transport congestion, monsoon-season produce disruption), which is why this sublayer sits in Risk & Environment as a peer to Weather rather than being folded entirely into Demand.

The general principle across all six: **a recurring, well-characterized seasonal pattern is a different kind of signal than a novel disruption**, even though both eventually show up as a claim in the same CD²F arbitration pipeline. The former should arrive with high confidence and long lead time; the latter with lower confidence and short lead time. Building the Seasonal/Cultural Calendar Layer as a distinct, named sublayer (rather than letting seasonality just be absorbed into the general forecasting model) is what preserves that distinction all the way through to the Coordinator.