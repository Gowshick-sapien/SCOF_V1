// =============================================================================
// SCOF Enterprise Ecosystem: Neo4j Schema & Constraint DDL
// Stage 5 Architecture Freeze - Production Cypher Script
// =============================================================================

// -----------------------------------------------------------------------------
// 1. Foundational Platform Uniqueness Constraints
// -----------------------------------------------------------------------------
// Party & Identity
CREATE CONSTRAINT cst_party_id IF NOT EXISTS FOR (p:Party) REQUIRE p.party_id IS UNIQUE;
CREATE CONSTRAINT cst_party_code IF NOT EXISTS FOR (p:Party) REQUIRE p.party_code IS UNIQUE;
CREATE CONSTRAINT cst_role_assignment_id IF NOT EXISTS FOR (pra:Party_Role_Assignment) REQUIRE pra.role_assignment_id IS UNIQUE;
CREATE CONSTRAINT cst_identity_id IF NOT EXISTS FOR (i:Identity) REQUIRE i.identity_id IS UNIQUE;
CREATE CONSTRAINT cst_contact_point_id IF NOT EXISTS FOR (c:Contact_Point) REQUIRE c.contact_point_id IS UNIQUE;
CREATE CONSTRAINT cst_tax_identity_id IF NOT EXISTS FOR (t:Tax_Identity) REQUIRE t.tax_identity_id IS UNIQUE;

// Geography & Facilities
CREATE CONSTRAINT cst_country_id IF NOT EXISTS FOR (c:Country) REQUIRE c.country_id IS UNIQUE;
CREATE CONSTRAINT cst_zone_id IF NOT EXISTS FOR (z:Zone_Macro_Region) REQUIRE z.zone_id IS UNIQUE;
CREATE CONSTRAINT cst_state_id IF NOT EXISTS FOR (s:State_Province) REQUIRE s.state_id IS UNIQUE;
CREATE CONSTRAINT cst_district_id IF NOT EXISTS FOR (d:District) REQUIRE d.district_id IS UNIQUE;
CREATE CONSTRAINT cst_city_id IF NOT EXISTS FOR (cty:City) REQUIRE cty.city_id IS UNIQUE;
CREATE CONSTRAINT cst_postal_area_id IF NOT EXISTS FOR (pa:Postal_Area) REQUIRE pa.postal_area_id IS UNIQUE;
CREATE CONSTRAINT cst_location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE;
CREATE CONSTRAINT cst_facility_id IF NOT EXISTS FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;

// Time & Dual Calendar
CREATE CONSTRAINT cst_calendar_id IF NOT EXISTS FOR (c:Calendar) REQUIRE c.calendar_id IS UNIQUE;
CREATE CONSTRAINT cst_year_id IF NOT EXISTS FOR (y:Calendar_Year) REQUIRE y.year_id IS UNIQUE;
CREATE CONSTRAINT cst_month_id IF NOT EXISTS FOR (m:Month) REQUIRE m.month_id IS UNIQUE;
CREATE CONSTRAINT cst_week_id IF NOT EXISTS FOR (w:Week) REQUIRE w.week_id IS UNIQUE;
CREATE CONSTRAINT cst_date_id IF NOT EXISTS FOR (d:Calendar_Date) REQUIRE d.date_id IS UNIQUE;
CREATE CONSTRAINT cst_holiday_id IF NOT EXISTS FOR (h:Holiday_Instance) REQUIRE h.holiday_instance_id IS UNIQUE;
CREATE CONSTRAINT cst_fiscal_calendar_id IF NOT EXISTS FOR (fc:Fiscal_Calendar) REQUIRE fc.fiscal_calendar_id IS UNIQUE;
CREATE CONSTRAINT cst_fiscal_year_id IF NOT EXISTS FOR (fy:Fiscal_Year) REQUIRE fy.fiscal_year_id IS UNIQUE;
CREATE CONSTRAINT cst_fiscal_quarter_id IF NOT EXISTS FOR (fq:Fiscal_Quarter) REQUIRE fq.fiscal_quarter_id IS UNIQUE;
CREATE CONSTRAINT cst_fiscal_period_id IF NOT EXISTS FOR (fp:Fiscal_Period) REQUIRE fp.fiscal_period_id IS UNIQUE;

// Reference Dimensions
CREATE CONSTRAINT cst_currency_id IF NOT EXISTS FOR (curr:Currency) REQUIRE curr.currency_id IS UNIQUE;
CREATE CONSTRAINT cst_uom_id IF NOT EXISTS FOR (u:Unit_of_Measure) REQUIRE u.uom_id IS UNIQUE;
CREATE CONSTRAINT cst_payment_term_id IF NOT EXISTS FOR (pt:Payment_Terms) REQUIRE pt.payment_term_id IS UNIQUE;
CREATE CONSTRAINT cst_incoterm_id IF NOT EXISTS FOR (inco:Incoterm) REQUIRE inco.incoterm_id IS UNIQUE;

// -----------------------------------------------------------------------------
// 2. Core Business Domains Uniqueness Constraints
// -----------------------------------------------------------------------------
// Merchandise Hierarchy
CREATE CONSTRAINT cst_sku_id IF NOT EXISTS FOR (s:SKU) REQUIRE s.sku_id IS UNIQUE;
CREATE CONSTRAINT cst_product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE;
CREATE CONSTRAINT cst_product_family_id IF NOT EXISTS FOR (pf:Product_Family) REQUIRE pf.product_family_id IS UNIQUE;
CREATE CONSTRAINT cst_subcategory_id IF NOT EXISTS FOR (sc:Subcategory) REQUIRE sc.subcategory_id IS UNIQUE;
CREATE CONSTRAINT cst_category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.category_id IS UNIQUE;
CREATE CONSTRAINT cst_department_id IF NOT EXISTS FOR (d:Merchandise_Department) REQUIRE d.department_id IS UNIQUE;
CREATE CONSTRAINT cst_brand_id IF NOT EXISTS FOR (b:Brand) REQUIRE b.brand_id IS UNIQUE;
CREATE CONSTRAINT cst_batch_id IF NOT EXISTS FOR (bat:Batch) REQUIRE bat.batch_id IS UNIQUE;
CREATE CONSTRAINT cst_lot_id IF NOT EXISTS FOR (lot:Lot) REQUIRE lot.lot_id IS UNIQUE;
CREATE CONSTRAINT cst_serial_id IF NOT EXISTS FOR (ser:Serial_Item) REQUIRE ser.serial_id IS UNIQUE;

// Sourcing, Procurement & Logistics
CREATE CONSTRAINT cst_supplier_profile_id IF NOT EXISTS FOR (sp:Supplier_Profile) REQUIRE sp.supplier_profile_id IS UNIQUE;
CREATE CONSTRAINT cst_carrier_profile_id IF NOT EXISTS FOR (cp:Carrier_Profile) REQUIRE cp.carrier_profile_id IS UNIQUE;
CREATE CONSTRAINT cst_po_id IF NOT EXISTS FOR (po:Purchase_Order) REQUIRE po.po_id IS UNIQUE;
CREATE CONSTRAINT cst_po_line_id IF NOT EXISTS FOR (pol:PO_Line) REQUIRE pol.po_line_id IS UNIQUE;
CREATE CONSTRAINT cst_grn_id IF NOT EXISTS FOR (grn:Goods_Receipt) REQUIRE grn.goods_receipt_id IS UNIQUE;
CREATE CONSTRAINT cst_gr_line_id IF NOT EXISTS FOR (grl:Goods_Receipt_Line) REQUIRE grl.gr_line_id IS UNIQUE;
CREATE CONSTRAINT cst_shipment_id IF NOT EXISTS FOR (s:Shipment) REQUIRE s.shipment_id IS UNIQUE;
CREATE CONSTRAINT cst_shipment_line_id IF NOT EXISTS FOR (sl:Shipment_Line) REQUIRE sl.shipment_line_id IS UNIQUE;
CREATE CONSTRAINT cst_transport_order_id IF NOT EXISTS FOR (tord:Transport_Order) REQUIRE tord.transport_order_id IS UNIQUE;

// Warehousing & Inventory
CREATE CONSTRAINT cst_zone_wh_id IF NOT EXISTS FOR (z:Zone) REQUIRE z.zone_id IS UNIQUE;
CREATE CONSTRAINT cst_waisle_id IF NOT EXISTS FOR (wa:Warehouse_Aisle) REQUIRE wa.aisle_id IS UNIQUE;
CREATE CONSTRAINT cst_rack_id IF NOT EXISTS FOR (rk:Rack) REQUIRE rk.rack_id IS UNIQUE;
CREATE CONSTRAINT cst_wshelf_id IF NOT EXISTS FOR (ws:Warehouse_Shelf) REQUIRE ws.shelf_id IS UNIQUE;
CREATE CONSTRAINT cst_bin_id IF NOT EXISTS FOR (bn:Bin) REQUIRE bn.bin_id IS UNIQUE;
CREATE CONSTRAINT cst_inv_position_id IF NOT EXISTS FOR (ip:Inventory_Position) REQUIRE ip.position_id IS UNIQUE;

// Commerce, Orders & Sales
CREATE CONSTRAINT cst_customer_profile_id IF NOT EXISTS FOR (cp:Customer_Profile) REQUIRE cp.customer_profile_id IS UNIQUE;
CREATE CONSTRAINT cst_cart_id IF NOT EXISTS FOR (crt:Cart) REQUIRE crt.cart_id IS UNIQUE;
CREATE CONSTRAINT cst_basket_id IF NOT EXISTS FOR (bsk:Basket) REQUIRE bsk.basket_id IS UNIQUE;
CREATE CONSTRAINT cst_transaction_id IF NOT EXISTS FOR (st:Sales_Transaction) REQUIRE st.transaction_id IS UNIQUE;
CREATE CONSTRAINT cst_sales_line_id IF NOT EXISTS FOR (sl:Sales_Line) REQUIRE sl.sales_line_id IS UNIQUE;
CREATE CONSTRAINT cst_sales_order_id IF NOT EXISTS FOR (so:Sales_Order) REQUIRE so.order_id IS UNIQUE;
CREATE CONSTRAINT cst_order_line_id IF NOT EXISTS FOR (ol:Order_Line) REQUIRE ol.order_line_id IS UNIQUE;
CREATE CONSTRAINT cst_order_allocation_id IF NOT EXISTS FOR (oa:Order_Allocation) REQUIRE oa.allocation_id IS UNIQUE;
CREATE CONSTRAINT cst_price_record_id IF NOT EXISTS FOR (pr:Price_Record) REQUIRE pr.price_record_id IS UNIQUE;

// Finance & Treasury
CREATE CONSTRAINT cst_bank_account_id IF NOT EXISTS FOR (ba:Bank_Account) REQUIRE ba.bank_account_id IS UNIQUE;
CREATE CONSTRAINT cst_invoice_id IF NOT EXISTS FOR (inv:Invoice) REQUIRE inv.invoice_id IS UNIQUE;
CREATE CONSTRAINT cst_supplier_invoice_line_id IF NOT EXISTS FOR (sil:Supplier_Invoice_Line) REQUIRE sil.invoice_line_id IS UNIQUE;
CREATE CONSTRAINT cst_payment_id IF NOT EXISTS FOR (pay:Payment) REQUIRE pay.payment_id IS UNIQUE;
CREATE CONSTRAINT cst_credit_note_id IF NOT EXISTS FOR (crn:Credit_Note) REQUIRE crn.credit_note_id IS UNIQUE;
CREATE CONSTRAINT cst_debit_note_id IF NOT EXISTS FOR (dbn:Debit_Note) REQUIRE dbn.debit_note_id IS UNIQUE;
CREATE CONSTRAINT cst_journal_entry_id IF NOT EXISTS FOR (je:Journal_Entry) REQUIRE je.journal_entry_id IS UNIQUE;
CREATE CONSTRAINT cst_journal_line_id IF NOT EXISTS FOR (jl:Journal_Line) REQUIRE jl.journal_line_id IS UNIQUE;
CREATE CONSTRAINT cst_gl_account_id IF NOT EXISTS FOR (gla:GL_Account) REQUIRE gla.gl_account_id IS UNIQUE;
CREATE CONSTRAINT cst_match_id IF NOT EXISTS FOR (twm:Three_Way_Match_Record) REQUIRE twm.match_id IS UNIQUE;

// Demand Intelligence & Simulation
CREATE CONSTRAINT cst_event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE;
CREATE CONSTRAINT cst_event_instance_id IF NOT EXISTS FOR (ei:Event_Instance) REQUIRE ei.event_instance_id IS UNIQUE;
CREATE CONSTRAINT cst_observation_id IF NOT EXISTS FOR (dobs:Demand_Observation) REQUIRE dobs.observation_id IS UNIQUE;
CREATE CONSTRAINT cst_attribution_id IF NOT EXISTS FOR (ea:Event_Attribution) REQUIRE ea.attribution_id IS UNIQUE;

// Assets, Quality & Governance
CREATE CONSTRAINT cst_physical_asset_id IF NOT EXISTS FOR (pa:Physical_Asset) REQUIRE pa.physical_asset_id IS UNIQUE;
CREATE CONSTRAINT cst_work_order_id IF NOT EXISTS FOR (wo:Work_Order) REQUIRE wo.work_order_id IS UNIQUE;
CREATE CONSTRAINT cst_qinspection_id IF NOT EXISTS FOR (qi:Quality_Inspection) REQUIRE qi.inspection_id IS UNIQUE;
CREATE CONSTRAINT cst_scenario_id IF NOT EXISTS FOR (sc:Scenario) REQUIRE sc.scenario_id IS UNIQUE;
CREATE CONSTRAINT cst_sim_run_id IF NOT EXISTS FOR (sr:Simulation_Run) REQUIRE sr.sim_run_id IS UNIQUE;
CREATE CONSTRAINT cst_val_result_id IF NOT EXISTS FOR (vr:Validation_Result) REQUIRE vr.val_result_id IS UNIQUE;
CREATE CONSTRAINT cst_status_event_id IF NOT EXISTS FOR (lse:Lifecycle_Status_Event) REQUIRE lse.status_event_id IS UNIQUE;

// -----------------------------------------------------------------------------
// 3. Composite & Full-Text Traversal Indexes
// -----------------------------------------------------------------------------
// Assortment & Sourcing Relationship Indexes
CREATE INDEX idx_rel_sources IF NOT EXISTS FOR ()-[r:SOURCES]-() ON (r.priority, r.unit_cost);
CREATE INDEX idx_rel_assorts IF NOT EXISTS FOR ()-[r:ASSORTS]-() ON (r.status, r.facing_qty);
CREATE INDEX idx_rel_serviced_by IF NOT EXISTS FOR ()-[r:SERVICED_BY]-() ON (r.is_primary, r.lead_time_days);
CREATE INDEX idx_rel_lane_to IF NOT EXISTS FOR ()-[r:LANE_TO]-() ON (r.transit_days, r.distance_km);

// Demand Causal & Attribution Indexes
CREATE INDEX idx_rel_impacts IF NOT EXISTS FOR ()-[r:IMPACTS]-() ON (r.target_level, r.lift_multiplier);
CREATE INDEX idx_rel_attributed IF NOT EXISTS FOR ()-[r:ATTRIBUTED_TO]-() ON (r.attribution_weight);

// Operational Node Indexes
CREATE INDEX idx_sku_search IF NOT EXISTS FOR (s:SKU) ON (s.barcode_ean13, s.storage_condition);
CREATE INDEX idx_facility_geo IF NOT EXISTS FOR (f:Facility) ON (f.facility_category, f.operating_status);
CREATE INDEX idx_dobs_grain IF NOT EXISTS FOR (d:Demand_Observation) ON (d.facility_id, d.sku_id, d.week_id);
CREATE INDEX idx_price_record_grain IF NOT EXISTS FOR (pr:Price_Record) ON (pr.facility_id, pr.sku_id, pr.week_id);
CREATE INDEX idx_status_event_query IF NOT EXISTS FOR (lse:Lifecycle_Status_Event) ON (lse.entity_type, lse.entity_id, lse.effective_timestamp);
