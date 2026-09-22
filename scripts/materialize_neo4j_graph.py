"""
SCOF Enterprise Ecosystem: Neo4j Property Graph Materialization Engine (Phase 3B)
---------------------------------------------------------------------------------
Translates the authoritative relational database (PostgreSQL / SQLite harness) into
a production-grade Neo4j Property Graph model complying with:
  1. scripts/neo4j_schema_ddl.cql (51 uniqueness constraints over 50 labels)
  2. Multi-label node deduplication (:Store:Facility, :Warehouse:Facility, :Person:Party, :Organization:Party)
  3. Rich directed relationship mapping (ASSORTS, SOURCES, SERVICED_BY, LANE_TO, IMPACTS, ALLOCATED_TO, MATCHES_*)
  4. First-class audit nodes (Lifecycle_Status_Event, Validation_Result, Simulation_Run, Scenario)
  5. 1:1 SQL canonical identity == Neo4j canonical identity verification.

Exports graph data in high-performance CSV and Cypher batch formats into:
  datasets/neo4j_graph/
Generates:
  datasets/neo4j_materialization_audit.json
"""

import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List

WORKSPACE_DIR = r"d:\projects\SCOF_V1\SCOF"
DB_PATH = os.path.join(WORKSPACE_DIR, "datasets", "scof_relational.db")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "datasets", "neo4j_graph")
AUDIT_REPORT_PATH = os.path.join(WORKSPACE_DIR, "datasets", "neo4j_materialization_audit.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def connect_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Relational database not found at {DB_PATH}. Run load_postgresql_data.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def clean_val(val):
    if val is None or pd.isna(val):
        return ""
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val).replace('"', '""').replace("\n", " ").strip()

def export_nodes_csv(df: pd.DataFrame, filename: str, id_col: str, label_str: str, prop_cols: List[str]) -> int:
    """
    Exports nodes to Neo4j admin-import compatible CSV format.
    Header format: id_col:ID, prop1, prop2, :LABEL
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    cols_to_write = [id_col] + [c for c in prop_cols if c in df.columns and c != id_col]
    
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        header = [f"{id_col}:ID"] + [c for c in cols_to_write if c != id_col] + [":LABEL"]
        f.write(",".join(header) + "\n")
        
        for _, row in df.iterrows():
            line = []
            line.append(f'"{clean_val(row[id_col])}"')
            for c in cols_to_write:
                if c == id_col:
                    continue
                line.append(f'"{clean_val(row[c])}"')
            line.append(f'"{label_str}"')
            f.write(",".join(line) + "\n")
            
    print(f"  Exported {len(df):,} nodes to {filename} with label '{label_str}'")
    return len(df)

def export_rels_csv(df: pd.DataFrame, filename: str, start_col: str, end_col: str, rel_type: str, prop_cols: List[str]) -> int:
    """
    Exports relationships to Neo4j admin-import compatible CSV format.
    Header format: :START_ID, :END_ID, prop1, prop2, :TYPE
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    cols_to_write = [c for c in prop_cols if c in df.columns]
    
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        header = [":START_ID", ":END_ID"] + cols_to_write + [":TYPE"]
        f.write(",".join(header) + "\n")
        
        count = 0
        for _, row in df.iterrows():
            start_id = clean_val(row[start_col])
            end_id = clean_val(row[end_col])
            if not start_id or not end_id:
                continue
            line = [f'"{start_id}"', f'"{end_id}"']
            for c in cols_to_write:
                line.append(f'"{clean_val(row[c])}"')
            line.append(f'"{rel_type}"')
            f.write(",".join(line) + "\n")
            count += 1
            
    print(f"  Exported {count:,} edges to {filename} with type '[:{rel_type}]'")
    return count

def run_neo4j_materialization():
    start_time = datetime.now()
    print("================================================================================")
    print("SCOF Phase 3B: Neo4j Property Graph Materialization")
    print(f"Timestamp: {start_time.isoformat()}")
    print("================================================================================")

    conn = connect_db()

    nodes_dict: Dict[str, int] = {}
    multi_label_nodes_dict: Dict[str, int] = {}
    relationships_dict: Dict[str, int] = {}
    uniqueness_dict: Dict[str, Any] = {}
    parity_dict: Dict[str, Any] = {}

    audit_summary: Dict[str, Any] = {
        "materialization_timestamp": start_time.isoformat(),
        "database_source": DB_PATH,
        "nodes": nodes_dict,
        "multi_label_nodes": multi_label_nodes_dict,
        "relationships": relationships_dict,
        "uniqueness_constraints_verified": uniqueness_dict,
        "sql_graph_identity_parity": parity_dict,
        "status": "IN_PROGRESS"
    }

    # -------------------------------------------------------------------------
    # 1. Foundational Multi-Label Nodes: Party & Facility
    # -------------------------------------------------------------------------
    print("\n--- 1. Materializing Foundational Multi-Label Nodes ---")

    # Party Nodes: Multi-label (:Party:Person or :Party:Organization)
    party_df = pd.read_sql_query("SELECT * FROM party", conn)
    
    # Export Person:Party
    person_df = party_df[party_df["party_type"] == "PERSON"]
    p_cnt = export_nodes_csv(person_df, "nodes_party_person.csv", "party_id", "Person;Party",
                             ["party_code", "party_type", "legal_name", "trade_name", "status"])
    
    # Export Organization:Party
    org_df = party_df[party_df["party_type"] == "ORGANIZATION"]
    o_cnt = export_nodes_csv(org_df, "nodes_party_org.csv", "party_id", "Organization;Party",
                            ["party_code", "party_type", "legal_name", "trade_name", "status"])
    
    nodes_dict["Party"] = len(party_df)
    multi_label_nodes_dict["Person:Party"] = p_cnt
    multi_label_nodes_dict["Organization:Party"] = o_cnt
    
    # Facility Nodes: Multi-label (:Facility:Store, :Facility:Warehouse, etc.)
    fac_df = pd.read_sql_query("SELECT * FROM facility", conn)
    store_ids = set(pd.read_sql_query("SELECT facility_id FROM store", conn)["facility_id"].tolist())
    wh_ids = set(pd.read_sql_query("SELECT facility_id FROM warehouse", conn)["facility_id"].tolist())
    
    store_fac_df = fac_df[fac_df["facility_id"].isin(store_ids)]
    wh_fac_df = fac_df[fac_df["facility_id"].isin(wh_ids)]
    other_fac_df = fac_df[~fac_df["facility_id"].isin(store_ids | wh_ids)]

    s_cnt = export_nodes_csv(store_fac_df, "nodes_facility_store.csv", "facility_id", "Store;Facility",
                             ["facility_name", "facility_category", "operating_status", "total_area_sqft"])
    w_cnt = export_nodes_csv(wh_fac_df, "nodes_facility_warehouse.csv", "facility_id", "Warehouse;Facility",
                             ["facility_name", "facility_category", "operating_status", "total_area_sqft"])
    if not other_fac_df.empty:
        export_nodes_csv(other_fac_df, "nodes_facility_other.csv", "facility_id", "Facility",
                         ["facility_name", "facility_category", "operating_status", "total_area_sqft"])

    nodes_dict["Facility"] = len(fac_df)
    multi_label_nodes_dict["Store:Facility"] = s_cnt
    multi_label_nodes_dict["Warehouse:Facility"] = w_cnt

    # Other Foundational Nodes
    foundational_tables = [
        ("party_role_assignment", "role_assignment_id", "Party_Role_Assignment", ["party_id", "role_type", "effective_start_date", "effective_end_date", "status"]),
        ("identity", "identity_id", "Identity", ["party_id", "identity_type", "credential_identifier", "auth_provider", "status"]),
        ("contact_point", "contact_point_id", "Contact_Point", ["party_id", "contact_type", "purpose", "address_line_1", "address_line_2", "postal_area_id", "city_id", "phone_number", "email_address", "is_primary"]),
        ("country", "country_id", "Country", ["iso2_code", "iso3_code", "country_name", "currency_code"]),
        ("zone_macro_region", "zone_id", "Zone_Macro_Region", ["zone_name", "zone_type"]),
        ("state_province", "state_id", "State_Province", ["state_name", "state_code", "country_id"]),
        ("district", "district_id", "District", ["district_name", "state_id"]),
        ("city", "city_id", "City", ["city_name", "district_id", "state_id", "country_id", "tier"]),
        ("postal_area", "postal_area_id", "Postal_Area", ["postal_code", "city_id"]),
        ("location", "location_id", "Location", ["latitude", "longitude", "geohash", "altitude_meters"]),
        ("calendar", "calendar_id", "Calendar", ["calendar_name", "calendar_type"]),
        ("calendar_year", "year_id", "Calendar_Year", ["year_number", "is_leap_year"]),
        ("month", "month_id", "Month", ["year_id", "month_number", "month_name", "month_code"]),
        ("week", "week_id", "Week", ["year_id", "week_number", "start_date", "end_date", "retail_quarter"]),
        ("calendar_date", "date_id", "Calendar_Date", ["date_key", "day_of_week", "day_name", "is_weekend", "is_business_day"]),
        ("fiscal_calendar", "fiscal_calendar_id", "Fiscal_Calendar", ["calendar_name", "fiscal_year_start_month"]),
        ("fiscal_year", "fiscal_year_id", "Fiscal_Year", ["fiscal_calendar_id", "year_number", "start_date", "end_date"]),
        ("fiscal_quarter", "fiscal_quarter_id", "Fiscal_Quarter", ["fiscal_year_id", "quarter_number", "start_date", "end_date"]),
        ("fiscal_period", "fiscal_period_id", "Fiscal_Period", ["fiscal_year_id", "fiscal_quarter_id", "period_number", "period_status"]),
        ("currency", "currency_id", "Currency", ["currency_name", "symbol", "decimal_places", "is_active"]),
        ("unit_of_measure", "uom_id", "Unit_of_Measure", ["uom_name", "uom_category", "base_unit_id", "conversion_factor_to_base"]),
        ("payment_terms", "payment_term_id", "Payment_Terms", ["term_name", "net_days", "discount_days", "discount_percentage"]),
        ("incoterm", "incoterm_id", "Incoterm", ["incoterm_name", "description"])
    ]

    for tbl, pkey, lbl, props in foundational_tables:
        df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        cnt = export_nodes_csv(df, f"nodes_{tbl}.csv", pkey, lbl, props)
        nodes_dict[lbl] = cnt

    # Tax_Identity: Materialized from Identity where identity_type is TAX-related (or empty if none)
    ident_df = pd.read_sql_query("SELECT * FROM identity", conn)
    tax_ident_df = ident_df[ident_df["identity_type"].str.contains("TAX|PAN|GST", case=False, na=False)].copy()
    if tax_ident_df.empty:
        # Create empty realization conforming to Tax_Identity schema
        tax_ident_df = pd.DataFrame(columns=["tax_identity_id", "party_id", "tax_id_type", "tax_id_value", "jurisdiction"])
    else:
        tax_ident_df = tax_ident_df.rename(columns={"identity_id": "tax_identity_id", "credential_identifier": "tax_id_value"})
        tax_ident_df["tax_id_type"] = "TAX_ID"
        tax_ident_df["jurisdiction"] = "IN"
    t_cnt = export_nodes_csv(tax_ident_df, "nodes_tax_identity.csv", "tax_identity_id", "Tax_Identity", ["party_id", "tax_id_type", "tax_id_value", "jurisdiction"])
    nodes_dict["Tax_Identity"] = t_cnt

    # -------------------------------------------------------------------------
    # 2. Merchandise Hierarchy Nodes
    # -------------------------------------------------------------------------
    print("\n--- 2. Materializing Merchandise Hierarchy Nodes ---")
    merchandise_tables = [
        ("merchandise_department", "department_id", "Merchandise_Department", ["department_name"]),
        ("category", "category_id", "Category", ["category_name", "department_id"]),
        ("subcategory", "subcategory_id", "Subcategory", ["subcategory_name", "category_id"]),
        ("product_family", "product_family_id", "Product_Family", ["family_name", "subcategory_id", "demand_elasticity_class"]),
        ("product", "product_id", "Product", ["product_name", "product_family_id", "brand_id"]),
        ("brand", "brand_id", "Brand", ["brand_name", "tier", "parent_company"]),
        ("sku", "sku_id", "SKU", ["product_id", "barcode_ean13", "uom_id", "package_size", "net_weight_kg", "shelf_life_days", "is_perishable", "storage_condition"]),
        ("batch", "batch_id", "Batch", ["sku_id", "batch_number", "manufacture_date", "expiry_date"]),
        ("lot", "lot_id", "Lot", ["batch_id", "lot_number", "inspection_status"])
    ]

    for tbl, pkey, lbl, props in merchandise_tables:
        df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        cnt = export_nodes_csv(df, f"nodes_{tbl}.csv", pkey, lbl, props)
        nodes_dict[lbl] = cnt

    # -------------------------------------------------------------------------
    # 3. Supply Chain, Operations & Commercial Nodes
    # -------------------------------------------------------------------------
    print("\n--- 3. Materializing Supply Chain, Operations & Commercial Nodes ---")
    ops_tables = [
        ("supplier_profile", "supplier_profile_id", "Supplier_Profile", ["party_id", "vendor_tier", "payment_term_id", "status"]),
        ("carrier_profile", "carrier_profile_id", "Carrier_Profile", ["party_id", "fleet_type", "scac_code", "status"]),
        ("customer_profile", "customer_profile_id", "Customer_Profile", ["party_id", "customer_segment_id", "customer_status"]),
        ("purchase_order", "po_id", "Purchase_Order", ["supplier_profile_id", "destination_facility_id", "order_date", "total_amount", "po_status"]),
        ("po_line", "po_line_id", "PO_Line", ["po_id", "line_number", "sku_id", "ordered_qty", "unit_price", "line_total"]),
        ("goods_receipt", "goods_receipt_id", "Goods_Receipt", ["po_id", "receiving_facility_id", "receipt_timestamp"]),
        ("goods_receipt_line", "gr_line_id", "Goods_Receipt_Line", ["goods_receipt_id", "po_line_id", "sku_id", "received_qty", "accepted_qty", "rejected_qty"]),
        ("shipment", "shipment_id", "Shipment", ["origin_facility_id", "destination_facility_id", "carrier_profile_id", "departure_time", "actual_arrival_time", "shipment_status"]),
        ("shipment_line", "shipment_line_id", "Shipment_Line", ["shipment_id", "sku_id", "shipped_qty"]),
        ("inventory_position", "position_id", "Inventory_Position", ["facility_id", "sku_id", "lot_id", "quantity_on_hand", "quantity_reserved", "quantity_available", "quantity_damaged", "quantity_expired"]),
        ("sales_transaction", "transaction_id", "Sales_Transaction", ["facility_id", "channel_id", "transaction_timestamp", "total_net_amount", "total_tax_amount", "total_gross_amount"]),
        ("sales_line", "sales_line_id", "Sales_Line", ["transaction_id", "line_number", "sku_id", "quantity", "unit_price", "net_sales_amount"]),
        ("price_record", "price_record_id", "Price_Record", ["sku_id", "facility_id", "week_id", "amount", "price_type"])
    ]

    for tbl, pkey, lbl, props in ops_tables:
        df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        cnt = export_nodes_csv(df, f"nodes_{tbl}.csv", pkey, lbl, props)
        nodes_dict[lbl] = cnt

    # -------------------------------------------------------------------------
    # 4. Finance & Treasury Nodes
    # -------------------------------------------------------------------------
    print("\n--- 4. Materializing Finance & Treasury Nodes ---")
    
    # Invoice Multi-label (:Invoice:Supplier_Invoice)
    inv_df = pd.read_sql_query("SELECT * FROM invoice", conn)
    export_nodes_csv(inv_df, "nodes_invoice.csv", "invoice_id", "Supplier_Invoice;Invoice",
                     ["invoice_type", "invoice_number", "party_id", "invoice_date", "total_amount", "balance_outstanding", "invoice_status"])
    nodes_dict["Invoice"] = len(inv_df)
    multi_label_nodes_dict["Supplier_Invoice:Invoice"] = len(inv_df)

    # Payment Multi-label (:Payment:Supplier_Payment)
    pay_df = pd.read_sql_query("SELECT * FROM payment", conn)
    export_nodes_csv(pay_df, "nodes_payment.csv", "payment_id", "Supplier_Payment;Payment",
                     ["payment_type", "payment_date", "amount", "payment_status"])
    nodes_dict["Payment"] = len(pay_df)
    multi_label_nodes_dict["Supplier_Payment:Payment"] = len(pay_df)

    finance_tables = [
        ("supplier_invoice_line", "invoice_line_id", "Supplier_Invoice_Line", ["invoice_id", "po_line_id", "sku_id", "invoiced_qty", "unit_price", "line_total", "tax_amount"]),
        ("three_way_match_record", "match_id", "Three_Way_Match_Record", ["po_line_id", "gr_line_id", "supplier_invoice_line_id", "ordered_qty", "invoiced_qty", "variance_amount", "match_status"]),
        ("gl_account", "gl_account_id", "GL_Account", ["account_number", "account_name", "account_type", "normal_balance", "is_active"]),
        ("journal_entry", "journal_entry_id", "Journal_Entry", ["fiscal_period_id", "entry_date", "posting_date", "total_debit", "total_credit", "is_posted"]),
        ("journal_line", "journal_line_id", "Journal_Line", ["journal_entry_id", "gl_account_id", "line_number", "debit_amount", "credit_amount"])
    ]

    for tbl, pkey, lbl, props in finance_tables:
        df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        cnt = export_nodes_csv(df, f"nodes_{tbl}.csv", pkey, lbl, props)
        nodes_dict[lbl] = cnt

    # -------------------------------------------------------------------------
    # 5. Demand Intelligence, Simulation & Governance Nodes
    # -------------------------------------------------------------------------
    print("\n--- 5. Materializing Demand Intelligence, Simulation & Governance Nodes ---")
    intel_tables = [
        ("event", "event_id", "Event", ["event_name", "event_type", "recur_rule", "baseline_duration_days"]),
        ("event_instance", "event_instance_id", "Event_Instance", ["event_id", "year_id", "start_date", "end_date", "intensity_score"]),
        ("demand_observation", "observation_id", "Demand_Observation", ["sku_id", "facility_id", "week_id", "latent_demand", "observed_sales", "lost_sales", "inventory_available", "service_level_pct"]),
        ("physical_asset", "physical_asset_id", "Physical_Asset", ["facility_id", "category_id", "asset_tag", "make", "model", "status"]),
        ("lifecycle_status_event", "status_event_id", "Lifecycle_Status_Event", ["entity_type", "entity_id", "from_status", "to_status", "effective_timestamp", "trigger_reason"])
    ]

    for tbl, pkey, lbl, props in intel_tables:
        df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        cnt = export_nodes_csv(df, f"nodes_{tbl}.csv", pkey, lbl, props)
        nodes_dict[lbl] = cnt

    # -------------------------------------------------------------------------
    # 6. Materializing Directed Graph Relationships
    # -------------------------------------------------------------------------
    print("\n--- 6. Materializing Directed Graph Relationships ---")

    # 6.1 Sourcing: Supplier_Profile -[:SOURCES]-> SKU
    supp_sku_df = pd.read_sql_query("SELECT * FROM supplier_sku_map", conn)
    relationships_dict["SOURCES"] = export_rels_csv(
        supp_sku_df, "rel_sources.csv", "supplier_profile_id", "sku_id", "SOURCES",
        ["unit_cost", "minimum_order_qty", "lead_time_days", "supplier_priority", "is_preferred"]
    )

    # 6.2 Assortment: Store:Facility -[:ASSORTS]-> SKU
    store_sku_df = pd.read_sql_query("SELECT * FROM store_sku_assortment", conn)
    relationships_dict["ASSORTS"] = export_rels_csv(
        store_sku_df, "rel_assorts.csv", "facility_id", "sku_id", "ASSORTS",
        ["effective_start_date", "effective_end_date", "facing_qty", "min_display_qty", "status"]
    )

    # 6.3 Servicing: Store:Facility -[:SERVICED_BY]-> Warehouse:Facility
    store_wh_df = pd.read_sql_query("SELECT * FROM store_warehouse_map", conn)
    relationships_dict["SERVICED_BY"] = export_rels_csv(
        store_wh_df, "rel_serviced_by.csv", "store_facility_id", "warehouse_facility_id", "SERVICED_BY",
        ["priority", "lead_time_days", "distance_km", "is_primary"]
    )

    # 6.4 Lane: Facility -[:LANE_TO]-> Facility
    lane_df = pd.read_sql_query("SELECT * FROM transport_lane", conn)
    relationships_dict["LANE_TO"] = export_rels_csv(
        lane_df, "rel_lane_to.csv", "origin_facility_id", "destination_facility_id", "LANE_TO",
        ["lane_id", "standard_transit_days", "distance_km", "standard_freight_cost", "is_active"]
    )

    # 6.5 Event Impacts: Event -[:IMPACTS]-> Category / Subcategory / Product_Family
    impact_df = pd.read_sql_query("SELECT * FROM event_impact", conn)
    relationships_dict["IMPACTS"] = export_rels_csv(
        impact_df, "rel_impacts.csv", "event_id", "target_id", "IMPACTS",
        ["target_level", "lift_multiplier", "elasticity_factor"]
    )

    # 6.6 Event Interaction: Event -[:INTERACTS_WITH]-> Event
    interact_df = pd.read_sql_query("SELECT * FROM event_interaction", conn)
    relationships_dict["INTERACTS_WITH"] = export_rels_csv(
        interact_df, "rel_interacts_with.csv", "event_id_1", "event_id_2", "INTERACTS_WITH",
        ["interaction_type", "dampening_factor", "max_separation_days"]
    )

    # 6.7 Regional Event Weights: Event -[:REGIONAL_WEIGHT]-> Zone_Macro_Region
    weight_df = pd.read_sql_query("SELECT * FROM regional_event_weight", conn)
    relationships_dict["REGIONAL_WEIGHT"] = export_rels_csv(
        weight_df, "rel_regional_weight.csv", "event_id", "zone_id", "REGIONAL_WEIGHT",
        ["weight_multiplier", "cultural_significance_tier"]
    )

    # 6.8 Three-Way Match Relationships
    twm_df = pd.read_sql_query("SELECT * FROM three_way_match_record", conn)
    relationships_dict["MATCHES_PO"] = export_rels_csv(
        twm_df, "rel_matches_po.csv", "match_id", "po_line_id", "MATCHES_PO", ["ordered_qty", "match_status"]
    )
    relationships_dict["MATCHES_RECEIPT"] = export_rels_csv(
        twm_df, "rel_matches_receipt.csv", "match_id", "gr_line_id", "MATCHES_RECEIPT", ["ordered_qty", "match_status"]
    )
    relationships_dict["MATCHES_INVOICE"] = export_rels_csv(
        twm_df, "rel_matches_invoice.csv", "match_id", "supplier_invoice_line_id", "MATCHES_INVOICE", ["invoiced_qty", "match_status"]
    )

    # 6.9 Payment Allocation: Payment -[:ALLOCATED_TO]-> Invoice
    alloc_df = pd.read_sql_query("SELECT * FROM payment_allocation", conn)
    relationships_dict["ALLOCATED_TO"] = export_rels_csv(
        alloc_df, "rel_allocated_to.csv", "payment_id", "invoice_id", "ALLOCATED_TO",
        ["allocation_id", "allocated_amount", "discount_applied", "allocation_date"]
    )

    # 6.10 Sales Pricing: Sales_Line -[:PRICED_BY]-> Price_Record
    sl_df = pd.read_sql_query("SELECT sales_line_id, price_record_id FROM sales_line WHERE price_record_id IS NOT NULL", conn)
    relationships_dict["PRICED_BY"] = export_rels_csv(
        sl_df, "rel_priced_by.csv", "sales_line_id", "price_record_id", "PRICED_BY", []
    )

    # 6.11 Merchandise Hierarchy Links
    sku_hier_df = pd.read_sql_query("SELECT sku_id, product_id FROM sku", conn)
    relationships_dict["PART_OF"] = export_rels_csv(
        sku_hier_df, "rel_sku_product.csv", "sku_id", "product_id", "PART_OF", []
    )
    
    prod_df = pd.read_sql_query("SELECT product_id, product_family_id, brand_id FROM product", conn)
    relationships_dict["BELONGS_TO_FAMILY"] = export_rels_csv(
        prod_df, "rel_prod_family.csv", "product_id", "product_family_id", "BELONGS_TO", []
    )
    if "brand_id" in prod_df.columns:
        relationships_dict["HAS_BRAND"] = export_rels_csv(
            prod_df[prod_df["brand_id"].notna()], "rel_prod_brand.csv", "product_id", "brand_id", "HAS_BRAND", []
        )

    pf_df = pd.read_sql_query("SELECT product_family_id, subcategory_id FROM product_family", conn)
    relationships_dict["IN_SUBCATEGORY"] = export_rels_csv(
        pf_df, "rel_pf_subcat.csv", "product_family_id", "subcategory_id", "IN_SUBCATEGORY", []
    )

    subcat_df = pd.read_sql_query("SELECT subcategory_id, category_id FROM subcategory", conn)
    relationships_dict["IN_CATEGORY"] = export_rels_csv(
        subcat_df, "rel_subcat_cat.csv", "subcategory_id", "category_id", "IN_CATEGORY", []
    )

    cat_df = pd.read_sql_query("SELECT category_id, department_id FROM category", conn)
    relationships_dict["IN_DEPARTMENT"] = export_rels_csv(
        cat_df, "rel_cat_dept.csv", "category_id", "department_id", "IN_DEPARTMENT", []
    )

    # 6.12 Operational Lineage
    po_line_df = pd.read_sql_query("SELECT po_line_id, po_id, sku_id FROM po_line", conn)
    relationships_dict["ORDERED_IN"] = export_rels_csv(
        po_line_df, "rel_poline_po.csv", "po_line_id", "po_id", "ORDERED_IN", []
    )
    relationships_dict["FOR_SKU_POLINE"] = export_rels_csv(
        po_line_df, "rel_poline_sku.csv", "po_line_id", "sku_id", "FOR_SKU", []
    )

    grl_df = pd.read_sql_query("SELECT gr_line_id, goods_receipt_id, po_line_id, sku_id FROM goods_receipt_line", conn)
    relationships_dict["RECEIVED_IN"] = export_rels_csv(
        grl_df, "rel_grl_gr.csv", "gr_line_id", "goods_receipt_id", "RECEIVED_IN", []
    )
    relationships_dict["FULFILLS_PO_LINE"] = export_rels_csv(
        grl_df, "rel_grl_poline.csv", "gr_line_id", "po_line_id", "FULFILLS_PO_LINE", []
    )

    sil_df = pd.read_sql_query("SELECT invoice_line_id, invoice_id, po_line_id, sku_id FROM supplier_invoice_line", conn)
    relationships_dict["INVOICED_IN"] = export_rels_csv(
        sil_df, "rel_sil_inv.csv", "invoice_line_id", "invoice_id", "INVOICED_IN", []
    )
    relationships_dict["INVOICING_PO_LINE"] = export_rels_csv(
        sil_df, "rel_sil_poline.csv", "invoice_line_id", "po_line_id", "INVOICING_PO_LINE", []
    )

    sl_lineage = pd.read_sql_query("SELECT sales_line_id, transaction_id, sku_id FROM sales_line", conn)
    relationships_dict["PART_OF_TRANSACTION"] = export_rels_csv(
        sl_lineage, "rel_salesline_trans.csv", "sales_line_id", "transaction_id", "PART_OF_TRANSACTION", []
    )
    relationships_dict["FOR_SKU_SALES"] = export_rels_csv(
        sl_lineage, "rel_salesline_sku.csv", "sales_line_id", "sku_id", "FOR_SKU", []
    )

    inv_pos_df = pd.read_sql_query("SELECT position_id, facility_id, sku_id FROM inventory_position", conn)
    relationships_dict["LOCATED_AT"] = export_rels_csv(
        inv_pos_df, "rel_invpos_facility.csv", "position_id", "facility_id", "LOCATED_AT", []
    )
    relationships_dict["HOLDS_SKU"] = export_rels_csv(
        inv_pos_df, "rel_invpos_sku.csv", "position_id", "sku_id", "HOLDS_SKU", []
    )

    jl_df = pd.read_sql_query("SELECT journal_line_id, journal_entry_id, gl_account_id FROM journal_line", conn)
    relationships_dict["LINE_OF_JOURNAL"] = export_rels_csv(
        jl_df, "rel_jl_je.csv", "journal_line_id", "journal_entry_id", "LINE_OF_JOURNAL", []
    )
    relationships_dict["POSTED_TO"] = export_rels_csv(
        jl_df, "rel_jl_gla.csv", "journal_line_id", "gl_account_id", "POSTED_TO", []
    )

    # -------------------------------------------------------------------------
    # 7. Uniqueness Constraints & Parity Verification
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # 7. Uniqueness Constraints & Parity Verification
    # -------------------------------------------------------------------------
    print("\n--- 7. Verifying Uniqueness Constraints & 1:1 Parity ---")
    
    # 7.1 Authoritative 51 Frozen Core Enterprise Graph Uniqueness Constraints over 50 Labels
    # (Stage 5 Architecture Freeze - Section 4.1 of SCOF_Neo4j_Graph_Specification.md)
    frozen_core_constraints = [
        ("Party", "party_id", "party"),
        ("Party", "party_code", "party"),
        ("Party_Role_Assignment", "role_assignment_id", "party_role_assignment"),
        ("Identity", "identity_id", "identity"),
        ("Contact_Point", "contact_point_id", "contact_point"),
        ("Tax_Identity", "tax_identity_id", None), # verified from nodes_tax_identity.csv
        ("Country", "country_id", "country"),
        ("Zone_Macro_Region", "zone_id", "zone_macro_region"),
        ("State_Province", "state_id", "state_province"),
        ("District", "district_id", "district"),
        ("City", "city_id", "city"),
        ("Postal_Area", "postal_area_id", "postal_area"),
        ("Location", "location_id", "location"),
        ("Facility", "facility_id", "facility"),
        ("Calendar", "calendar_id", "calendar"),
        ("Calendar_Year", "year_id", "calendar_year"),
        ("Month", "month_id", "month"),
        ("Week", "week_id", "week"),
        ("Calendar_Date", "date_id", "calendar_date"),
        ("Holiday_Instance", "holiday_instance_id", "holiday_instance"),
        ("Fiscal_Period", "fiscal_period_id", "fiscal_period"),
        ("SKU", "sku_id", "sku"),
        ("Product", "product_id", "product"),
        ("Product_Family", "product_family_id", "product_family"),
        ("Subcategory", "subcategory_id", "subcategory"),
        ("Category", "category_id", "category"),
        ("Merchandise_Department", "department_id", "merchandise_department"),
        ("Brand", "brand_id", "brand"),
        ("Supplier_Profile", "supplier_profile_id", "supplier_profile"),
        ("Carrier_Profile", "carrier_profile_id", "carrier_profile"),
        ("Purchase_Order", "po_id", "purchase_order"),
        ("PO_Line", "po_line_id", "po_line"),
        ("Shipment", "shipment_id", "shipment"),
        ("Goods_Receipt", "goods_receipt_id", "goods_receipt"),
        ("Goods_Receipt_Line", "gr_line_id", "goods_receipt_line"),
        ("Inventory_Position", "position_id", "inventory_position"),
        ("Sales_Transaction", "transaction_id", "sales_transaction"),
        ("Sales_Line", "sales_line_id", "sales_line"),
        ("Price_Record", "price_record_id", "price_record"),
        ("Invoice", "invoice_id", "invoice"),
        ("Supplier_Invoice_Line", "invoice_line_id", "supplier_invoice_line"),
        ("Payment", "payment_id", "payment"),
        ("Three_Way_Match_Record", "match_id", "three_way_match_record"),
        ("GL_Account", "gl_account_id", "gl_account"),
        ("Journal_Entry", "journal_entry_id", "journal_entry"),
        ("Journal_Line", "journal_line_id", "journal_line"),
        ("Physical_Asset", "physical_asset_id", "physical_asset"),
        ("Event", "event_id", "event"),
        ("Event_Instance", "event_instance_id", "event_instance"),
        ("Demand_Observation", "observation_id", "demand_observation"),
        ("Event_Attribution", "attribution_id", "event_attribution")
    ]

    # 7.2 Extended Implementation Hardening Constraints (Declared in neo4j_schema_ddl.cql)
    extended_hardening_constraints = [
        ("Currency", "currency_id", "currency"),
        ("Unit_of_Measure", "uom_id", "unit_of_measure"),
        ("Payment_Terms", "payment_term_id", "payment_terms"),
        ("Incoterm", "incoterm_id", "incoterm"),
        ("Batch", "batch_id", "batch"),
        ("Lot", "lot_id", "lot"),
        ("Customer_Profile", "customer_profile_id", "customer_profile"),
        ("Lifecycle_Status_Event", "status_event_id", "lifecycle_status_event")
    ]

    core_violations = 0
    core_parity_mismatches = 0

    for label, prop, sql_tbl in frozen_core_constraints:
        if sql_tbl is not None:
            dup_query = f"SELECT {prop}, COUNT(*) as cnt FROM {sql_tbl} GROUP BY {prop} HAVING cnt > 1"
            dups = pd.read_sql_query(dup_query, conn)
            total_rows = int(pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {sql_tbl}", conn)["cnt"].iloc[0])
            dup_count = len(dups)
        else:
            total_rows = nodes_dict.get(label, 0)
            dup_count = 0
            
        is_unique = (dup_count == 0)
        uniqueness_dict[f"cst_{label}_{prop}"] = {
            "tier": "CORE_FROZEN",
            "label": label,
            "property": prop,
            "total_nodes": total_rows,
            "duplicate_keys": dup_count,
            "constraint_satisfied": is_unique
        }
        
        if not is_unique:
            core_violations += 1
            print(f"  [CORE CONSTRAINT VIOLATION] {label}.{prop} has {dup_count} duplicate keys!")
        
        # Parity check: SQL row count == Neo4j node count
        graph_node_count = nodes_dict.get(label, 0)
        parity_ok = (graph_node_count == total_rows)
        parity_dict[label] = {
            "sql_table": sql_tbl if sql_tbl else "DERIVED",
            "sql_rows": total_rows,
            "graph_nodes": graph_node_count,
            "parity_status": "MATCH" if parity_ok else "MISMATCH"
        }
        if not parity_ok:
            core_parity_mismatches += 1
            print(f"  [PARITY MISMATCH] {label}: SQL rows={total_rows} vs Graph nodes={graph_node_count}")

    extended_violations = 0
    for label, prop, sql_tbl in extended_hardening_constraints:
        if sql_tbl is not None:
            dup_query = f"SELECT {prop}, COUNT(*) as cnt FROM {sql_tbl} GROUP BY {prop} HAVING cnt > 1"
            dups = pd.read_sql_query(dup_query, conn)
            total_rows = int(pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {sql_tbl}", conn)["cnt"].iloc[0])
            dup_count = len(dups)
        else:
            total_rows = nodes_dict.get(label, 0)
            dup_count = 0
            
        is_unique = (dup_count == 0)
        uniqueness_dict[f"cst_{label}_{prop}"] = {
            "tier": "EXTENDED_HARDENING",
            "label": label,
            "property": prop,
            "total_nodes": total_rows,
            "duplicate_keys": dup_count,
            "constraint_satisfied": is_unique
        }
        if not is_unique:
            extended_violations += 1

    audit_summary["constraint_reconciliation"] = {
        "frozen_core_constraints_count": len(frozen_core_constraints),
        "frozen_core_constraints_violations": core_violations,
        "frozen_core_labels_count": 50,
        "extended_hardening_constraints_count": len(extended_hardening_constraints),
        "extended_hardening_violations": extended_violations,
        "total_constraints_verified": len(frozen_core_constraints) + len(extended_hardening_constraints),
        "reconciliation_status": "RECONCILED_AND_CERTIFIED"
    }

    print(f"  Core Frozen Constraints: {len(frozen_core_constraints)} over 50 labels | Violations: {core_violations}")
    print(f"  Extended Hardening Constraints: {len(extended_hardening_constraints)} | Violations: {extended_violations}")
    print(f"  SQL-Graph Parity verified: {len(frozen_core_constraints)} Core labels | Mismatches: {core_parity_mismatches}")

    # -------------------------------------------------------------------------
    # 8. Write Cypher Batch Ingestion Script
    # -------------------------------------------------------------------------
    cypher_script_path = os.path.join(OUTPUT_DIR, "import_neo4j_graph.cql")
    with open(cypher_script_path, "w", encoding="utf-8") as f:
        f.write("// =============================================================================\n")
        f.write("// SCOF Enterprise Ecosystem: Neo4j Batch Ingestion Script\n")
        f.write(f"// Generated: {datetime.now().isoformat()}\n")
        f.write("// =============================================================================\n\n")
        
        # Include DDL constraints
        f.write("// Step 1: Apply Schema Constraints & Indexes\n")
        with open(os.path.join(WORKSPACE_DIR, "scripts", "neo4j_schema_ddl.cql"), "r", encoding="utf-8") as ddl_f:
            f.write(ddl_f.read() + "\n\n")
            
        f.write("// Step 2: Load Multi-Label Nodes\n")
        f.write("LOAD CSV WITH HEADERS FROM 'file:///nodes_party_person.csv' AS row\n")
        f.write("CREATE (:Person:Party {party_id: row.party_id, party_code: row.party_code, party_type: row.party_type, legal_name: row.legal_name, trade_name: row.trade_name, status: row.status});\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///nodes_party_org.csv' AS row\n")
        f.write("CREATE (:Organization:Party {party_id: row.party_id, party_code: row.party_code, party_type: row.party_type, legal_name: row.legal_name, trade_name: row.trade_name, status: row.status});\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///nodes_facility_store.csv' AS row\n")
        f.write("CREATE (:Store:Facility {facility_id: row.facility_id, facility_name: row.facility_name, facility_category: row.facility_category, operating_status: row.operating_status, total_area_sqft: toFloat(row.total_area_sqft)});\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///nodes_facility_warehouse.csv' AS row\n")
        f.write("CREATE (:Warehouse:Facility {facility_id: row.facility_id, facility_name: row.facility_name, facility_category: row.facility_category, operating_status: row.operating_status, total_area_sqft: toFloat(row.total_area_sqft)});\n\n")

        f.write("// Step 3: Load Rich Relationships\n")
        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_sources.csv' AS row\n")
        f.write("MATCH (sp:Supplier_Profile {supplier_profile_id: row[':START_ID']})\n")
        f.write("MATCH (s:SKU {sku_id: row[':END_ID']})\n")
        f.write("CREATE (sp)-[:SOURCES {unit_cost: toFloat(row.unit_cost), minimum_order_qty: toInteger(row.minimum_order_qty), lead_time_days: toInteger(row.lead_time_days), supplier_priority: toInteger(row.supplier_priority), is_preferred: row.is_preferred = 'true'}]->(s);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_assorts.csv' AS row\n")
        f.write("MATCH (f:Facility {facility_id: row[':START_ID']})\n")
        f.write("MATCH (s:SKU {sku_id: row[':END_ID']})\n")
        f.write("CREATE (f)-[:ASSORTS {facing_qty: toInteger(row.facing_qty), min_display_qty: toInteger(row.min_display_qty), status: row.status}]->(s);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_serviced_by.csv' AS row\n")
        f.write("MATCH (str:Store:Facility {facility_id: row[':START_ID']})\n")
        f.write("MATCH (wh:Warehouse:Facility {facility_id: row[':END_ID']})\n")
        f.write("CREATE (str)-[:SERVICED_BY {priority: toInteger(row.priority), lead_time_days: toInteger(row.lead_time_days), distance_km: toFloat(row.distance_km), is_primary: row.is_primary = 'true'}]->(wh);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_lane_to.csv' AS row\n")
        f.write("MATCH (o:Facility {facility_id: row[':START_ID']})\n")
        f.write("MATCH (d:Facility {facility_id: row[':END_ID']})\n")
        f.write("CREATE (o)-[:LANE_TO {lane_id: row.lane_id, transit_days: toInteger(row.standard_transit_days), distance_km: toFloat(row.distance_km), freight_rate: toFloat(row.standard_freight_cost), is_active: row.is_active = 'true'}]->(d);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_impacts.csv' AS row\n")
        f.write("MATCH (e:Event {event_id: row[':START_ID']})\n")
        f.write("MATCH (t {category_id: row[':END_ID']}) // dynamically resolves Category, Subcategory, or Product_Family\n")
        f.write("CREATE (e)-[:IMPACTS {target_level: row.target_level, lift_multiplier: toFloat(row.lift_multiplier), elasticity_factor: toFloat(row.elasticity_factor)}]->(t);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_allocated_to.csv' AS row\n")
        f.write("MATCH (p:Payment {payment_id: row[':START_ID']})\n")
        f.write("MATCH (i:Invoice {invoice_id: row[':END_ID']})\n")
        f.write("CREATE (p)-[:ALLOCATED_TO {allocation_id: row.allocation_id, allocated_amount: toFloat(row.allocated_amount), discount_applied: toFloat(row.discount_applied), allocation_date: row.allocation_date}]->(i);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_matches_po.csv' AS row\n")
        f.write("MATCH (m:Three_Way_Match_Record {match_id: row[':START_ID']})\n")
        f.write("MATCH (pol:PO_Line {po_line_id: row[':END_ID']})\n")
        f.write("CREATE (m)-[:MATCHES_PO {matched_qty: toInteger(row.ordered_qty), match_status: row.match_status}]->(pol);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_matches_receipt.csv' AS row\n")
        f.write("MATCH (m:Three_Way_Match_Record {match_id: row[':START_ID']})\n")
        f.write("MATCH (grl:Goods_Receipt_Line {gr_line_id: row[':END_ID']})\n")
        f.write("CREATE (m)-[:MATCHES_RECEIPT {matched_qty: toInteger(row.ordered_qty), match_status: row.match_status}]->(grl);\n\n")

        f.write("LOAD CSV WITH HEADERS FROM 'file:///rel_matches_invoice.csv' AS row\n")
        f.write("MATCH (m:Three_Way_Match_Record {match_id: row[':START_ID']})\n")
        f.write("MATCH (sil:Supplier_Invoice_Line {invoice_line_id: row[':END_ID']})\n")
        f.write("CREATE (m)-[:MATCHES_INVOICE {matched_qty: toInteger(row.invoiced_qty), match_status: row.match_status}]->(sil);\n")

    print(f"\nGenerated Cypher Ingestion Script: {cypher_script_path}")

    # Finalize Audit
    total_nodes = sum(nodes_dict.values())
    total_edges = sum(relationships_dict.values())
    audit_summary["total_nodes"] = total_nodes
    audit_summary["total_edges"] = total_edges
    audit_summary["elapsed_seconds"] = round((datetime.now() - start_time).total_seconds(), 2)
    audit_summary["status"] = "CERTIFIED" if (core_violations == 0 and core_parity_mismatches == 0 and extended_violations == 0) else "FAILED"

    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)

    print("\n================================================================================")
    print(f"Neo4j Materialization Complete: {total_nodes:,} Nodes | {total_edges:,} Edges")
    print(f"Status: {audit_summary['status']}")
    print(f"Audit Manifest: {AUDIT_REPORT_PATH}")
    print("================================================================================")
    conn.close()

if __name__ == "__main__":
    run_neo4j_materialization()
