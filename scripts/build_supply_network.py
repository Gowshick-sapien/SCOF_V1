import os
import pandas as pd
import numpy as np

def build_supply_network():
    base_dir = r"d:\projects\SCOF_V1\SCOF"
    datasets_dir = os.path.join(base_dir, "datasets")
    masters_dir = os.path.join(datasets_dir, "masters")

    print("Phase 5: Building Supply Network (Store Master, Warehouses, Routing, Assortments, Sourcing)...")

    # 1. Warehouse Master (5 Regional Distribution Centers)
    warehouses = [
        {"WAREHOUSE_ID": "wh-001", "WAREHOUSE_NAME": "National Northern DC", "REGION": "North", "STATE": "Haryana", "CITY": "Gurugram", "TOTAL_CAPACITY_PALLETS": 50000, "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK": 500000},
        {"WAREHOUSE_ID": "wh-002", "WAREHOUSE_NAME": "Western Regional DC", "REGION": "West", "STATE": "Maharashtra", "CITY": "Bhiwandi", "TOTAL_CAPACITY_PALLETS": 60000, "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK": 600000},
        {"WAREHOUSE_ID": "wh-003", "WAREHOUSE_NAME": "Southern Regional DC", "REGION": "South", "STATE": "Karnataka", "CITY": "Bengaluru", "TOTAL_CAPACITY_PALLETS": 55000, "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK": 550000},
        {"WAREHOUSE_ID": "wh-004", "WAREHOUSE_NAME": "Eastern Regional DC", "REGION": "East", "STATE": "West Bengal", "CITY": "Kolkata", "TOTAL_CAPACITY_PALLETS": 40000, "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK": 400000},
        {"WAREHOUSE_ID": "wh-005", "WAREHOUSE_NAME": "Central Hub DC", "REGION": "Central", "STATE": "Madhya Pradesh", "CITY": "Indore", "TOTAL_CAPACITY_PALLETS": 35000, "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK": 350000}
    ]
    df_wh = pd.DataFrame(warehouses)
    df_wh.to_csv(os.path.join(masters_dir, "warehouse_master.csv"), index=False)
    print(f"Created warehouse_master.csv ({len(df_wh)} DCs).")

    # 2. Store Master (16 Stores across 6 Regions)
    stores = [
        {"STORE_ID": "str-001", "STORE_NAME": "Delhi National Mall Hypermarket", "STORE_FORMAT": "HYPERMARKET", "REGION": "North", "STATE": "Delhi", "CITY": "Delhi", "TIER": "Tier-1", "PRIMARY_DC_ID": "wh-001", "MAX_SHELF_CAPACITY_UNITS": 250000},
        {"STORE_ID": "str-002", "STORE_NAME": "Mumbai Flagship Hypermarket", "STORE_FORMAT": "HYPERMARKET", "REGION": "West", "STATE": "Maharashtra", "CITY": "Mumbai", "TIER": "Tier-1", "PRIMARY_DC_ID": "wh-002", "MAX_SHELF_CAPACITY_UNITS": 300000},
        {"STORE_ID": "str-003", "STORE_NAME": "Bengaluru Tech Hub Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "South", "STATE": "Karnataka", "CITY": "Bengaluru", "TIER": "Tier-1", "PRIMARY_DC_ID": "wh-003", "MAX_SHELF_CAPACITY_UNITS": 150000},
        {"STORE_ID": "str-004", "STORE_NAME": "Chennai Metro Express", "STORE_FORMAT": "EXPRESS", "REGION": "South", "STATE": "Tamil Nadu", "CITY": "Chennai", "TIER": "Tier-1", "PRIMARY_DC_ID": "wh-003", "MAX_SHELF_CAPACITY_UNITS": 30000},
        {"STORE_ID": "str-005", "STORE_NAME": "Kolkata City Center Hypermarket", "STORE_FORMAT": "HYPERMARKET", "REGION": "East", "STATE": "West Bengal", "CITY": "Kolkata", "TIER": "Tier-1", "PRIMARY_DC_ID": "wh-004", "MAX_SHELF_CAPACITY_UNITS": 200000},
        {"STORE_ID": "str-006", "STORE_NAME": "Hyderabad Central Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "South", "STATE": "Telangana", "CITY": "Hyderabad", "TIER": "Tier-1", "PRIMARY_DC_ID": "wh-003", "MAX_SHELF_CAPACITY_UNITS": 120000},
        {"STORE_ID": "str-007", "STORE_NAME": "Ahmedabad West Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "West", "STATE": "Gujarat", "CITY": "Ahmedabad", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-002", "MAX_SHELF_CAPACITY_UNITS": 90000},
        {"STORE_ID": "str-008", "STORE_NAME": "Pune Deccan Express", "STORE_FORMAT": "EXPRESS", "REGION": "West", "STATE": "Maharashtra", "CITY": "Pune", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-002", "MAX_SHELF_CAPACITY_UNITS": 25000},
        {"STORE_ID": "str-009", "STORE_NAME": "Jaipur Pink City Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "North", "STATE": "Rajasthan", "CITY": "Jaipur", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-001", "MAX_SHELF_CAPACITY_UNITS": 80000},
        {"STORE_ID": "str-010", "STORE_NAME": "Lucknow Gomti Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "North", "STATE": "Uttar Pradesh", "CITY": "Lucknow", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-001", "MAX_SHELF_CAPACITY_UNITS": 85000},
        {"STORE_ID": "str-011", "STORE_NAME": "Chandigarh Sector Express", "STORE_FORMAT": "EXPRESS", "REGION": "North", "STATE": "Punjab", "CITY": "Chandigarh", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-001", "MAX_SHELF_CAPACITY_UNITS": 30000},
        {"STORE_ID": "str-012", "STORE_NAME": "Kochi Marine Drive Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "South", "STATE": "Kerala", "CITY": "Kochi", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-003", "MAX_SHELF_CAPACITY_UNITS": 75000},
        {"STORE_ID": "str-013", "STORE_NAME": "Indore Palasia Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "Central", "STATE": "Madhya Pradesh", "CITY": "Indore", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-005", "MAX_SHELF_CAPACITY_UNITS": 70000},
        {"STORE_ID": "str-014", "STORE_NAME": "Bhopal New Market Express", "STORE_FORMAT": "EXPRESS", "REGION": "Central", "STATE": "Madhya Pradesh", "CITY": "Bhopal", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-005", "MAX_SHELF_CAPACITY_UNITS": 25000},
        {"STORE_ID": "str-015", "STORE_NAME": "Patna Bailey Road Supermarket", "STORE_FORMAT": "SUPERMARKET", "REGION": "East", "STATE": "Bihar", "CITY": "Patna", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-004", "MAX_SHELF_CAPACITY_UNITS": 80000},
        {"STORE_ID": "str-016", "STORE_NAME": "Guwahati Gateway Express", "STORE_FORMAT": "EXPRESS", "REGION": "Northeast", "STATE": "Assam", "CITY": "Guwahati", "TIER": "Tier-2", "PRIMARY_DC_ID": "wh-004", "MAX_SHELF_CAPACITY_UNITS": 35000}
    ]
    df_stores = pd.DataFrame(stores)
    df_stores.to_csv(os.path.join(masters_dir, "store_master.csv"), index=False)
    print(f"Created store_master.csv ({len(df_stores)} retail stores).")

    # Also update locations.csv to remain consistent with both DCs and stores
    loc_rows = []
    for wh in warehouses:
        loc_rows.append({"Location_ID": wh["WAREHOUSE_ID"], "Type": "DC", "Capacity_Units": wh["TOTAL_CAPACITY_PALLETS"] * 10, "Safety_Stock_Policy": "dynamic"})
    for st in stores:
        loc_rows.append({"Location_ID": st["STORE_ID"], "Type": "Store", "Capacity_Units": st["MAX_SHELF_CAPACITY_UNITS"], "Safety_Stock_Policy": "static"})
    pd.DataFrame(loc_rows).to_csv(os.path.join(datasets_dir, "locations.csv"), index=False)
    print(f"Synchronized locations.csv ({len(loc_rows)} locations).")

    # 3. Store Warehouse Map (Primary & Secondary Routing)
    routes = []
    secondary_dc_map = {"wh-001": "wh-005", "wh-002": "wh-005", "wh-003": "wh-005", "wh-004": "wh-005", "wh-005": "wh-001"}
    for st in stores:
        p_dc = st["PRIMARY_DC_ID"]
        s_dc = secondary_dc_map.get(p_dc, "wh-005")
        routes.append({"STORE_ID": st["STORE_ID"], "WAREHOUSE_ID": p_dc, "ROUTE_PRIORITY": "PRIMARY", "TRANSIT_TIME_DAYS": 1 if st["TIER"] == "Tier-1" else 2})
        routes.append({"STORE_ID": st["STORE_ID"], "WAREHOUSE_ID": s_dc, "ROUTE_PRIORITY": "SECONDARY", "TRANSIT_TIME_DAYS": 4})
    pd.DataFrame(routes).to_csv(os.path.join(masters_dir, "store_warehouse_map.csv"), index=False)
    print(f"Created store_warehouse_map.csv ({len(routes)} routes).")

    # 4. Supplier SKU Map
    df_edges = pd.read_csv(os.path.join(datasets_dir, "supplier_product_edges.csv"))
    df_skus = pd.read_csv(os.path.join(masters_dir, "sku_master.csv"))
    sku_cost_dict = dict(zip(df_skus['SKU_ID'], df_skus['BASE_UNIT_COST']))

    supplier_sku_rows = []
    np.random.seed(42)

    for _, row in df_edges.iterrows():
        s_id = str(row['Supplier_ID'])
        sku = str(row['SKU'])
        rank = str(row.get('Sourcing_Rank', 'Primary'))
        markup = float(row.get('Unit_Cost_Markup', 1.0))
        lead_days = int(row.get('Supplier_Lead_Time_Days', 14))

        base_cost = sku_cost_dict.get(sku, 50.0)
        purchase_cost = round(base_cost * markup, 2)
        moq = int(np.random.choice([25, 50, 100, 200]))

        supplier_sku_rows.append({
            "SUPPLIER_ID": s_id,
            "SKU_ID": sku,
            "SUPPLIER_SKU": f"VND-{s_id}-{sku[:8]}",
            "PURCHASE_COST": purchase_cost,
            "MOQ_UNITS": moq,
            "LEAD_TIME_DAYS": lead_days,
            "ORDER_MULTIPLE": 10,
            "PRIMARY_FLAG": 1 if rank.lower() == "primary" else 0,
            "ACTIVE_FLAG": 1
        })

    df_supp_sku = pd.DataFrame(supplier_sku_rows)
    df_supp_sku.to_csv(os.path.join(masters_dir, "supplier_sku_map.csv"), index=False)
    print(f"Created supplier_sku_map.csv ({len(df_supp_sku)} sourcing edges).")

    # 5. Store SKU Assortment & Replenishment Policy
    # Formats carry different fractions of the catalog:
    # HYPERMARKET: 75% of SKUs (~37,000 SKUs)
    # SUPERMARKET: 40% of SKUs (~20,000 SKUs)
    # EXPRESS: 18% of SKUs (~9,000 SKUs)
    all_sku_ids = df_skus['SKU_ID'].values
    n_all_skus = len(all_sku_ids)

    assortment_rows = []
    replenish_rows = []

    # Map department info to SKUs for logical format assortment
    df_prod = pd.read_csv(os.path.join(masters_dir, "product_master.csv"))
    df_fam = pd.read_csv(os.path.join(masters_dir, "product_family_master.csv"))
    df_subcat = pd.read_csv(os.path.join(masters_dir, "subcategory_master.csv"))
    df_cat = pd.read_csv(os.path.join(masters_dir, "category_master.csv"))

    m1 = pd.merge(df_skus[['SKU_ID', 'PRODUCT_ID', 'SEASONALITY_PROFILE', 'BASE_UNIT_COST']], df_prod[['PRODUCT_ID', 'FAMILY_ID']], on="PRODUCT_ID", how="left")
    m2 = pd.merge(m1, df_fam[['FAMILY_ID', 'SUBCATEGORY_ID']], on="FAMILY_ID", how="left")
    m3 = pd.merge(m2, df_subcat[['SUBCATEGORY_ID', 'CATEGORY_ID']], on="SUBCATEGORY_ID", how="left")
    sku_full = pd.merge(m3, df_cat[['CATEGORY_ID', 'DEPARTMENT_ID']], on="CATEGORY_ID", how="left")

    fnb_gro_fre = set(sku_full[sku_full['DEPARTMENT_ID'].isin(['DEP-FNB', 'DEP-GRO', 'DEP-FRE', 'DEP-HEA'])]['SKU_ID'])

    for st in stores:
        st_id = st["STORE_ID"]
        s_format = st["STORE_FORMAT"]

        if s_format == "HYPERMARKET":
            # 75% random sample
            chosen_skus = np.random.choice(all_sku_ids, size=int(n_all_skus * 0.75), replace=False)
        elif s_format == "SUPERMARKET":
            # Essentials (FNB, GRO, FRE) + 30% of other
            other_skus = [s for s in all_sku_ids if s not in fnb_gro_fre]
            chosen_other = np.random.choice(other_skus, size=int(len(other_skus) * 0.25), replace=False)
            chosen_skus = np.array(list(fnb_gro_fre) + list(chosen_other))
        else: # EXPRESS
            # 50% of essentials only
            fnb_list = list(fnb_gro_fre)
            chosen_skus = np.random.choice(fnb_list, size=min(len(fnb_list), int(n_all_skus * 0.18)), replace=False)

        # Build rows for this store
        sub_info = sku_full[sku_full['SKU_ID'].isin(chosen_skus)]
        for _, srow in sub_info.iterrows():
            sku_id = srow['SKU_ID']
            season = str(srow['SEASONALITY_PROFILE'])
            cost = float(srow['BASE_UNIT_COST'])

            # Seasonal active window
            start_wk = 1
            end_wk = 52
            tier = "CORE"
            if "WINTER" in season:
                start_wk = 40
                end_wk = 8
                tier = "SEASONAL"
            elif "SUMMER" in season:
                start_wk = 14
                end_wk = 30
                tier = "SEASONAL"
            elif "BACK_TO_SCHOOL" in season:
                start_wk = 20
                end_wk = 32
                tier = "SEASONAL"

            shelf_cap = int(np.clip(1000 / (cost + 1), 5, 80))

            assortment_rows.append({
                "STORE_ID": st_id,
                "SKU_ID": sku_id,
                "ASSORTMENT_TIER": tier,
                "ASSORTMENT_START_WEEK": start_wk,
                "ASSORTMENT_END_WEEK": end_wk,
                "ALLOCATED_SHELF_CAPACITY_UNITS": shelf_cap
            })

            # Replenishment Policy
            rop = max(5, int(shelf_cap * 0.35))
            target_max = shelf_cap
            method = "ORDER_UP_TO" if s_format == "HYPERMARKET" else "MIN_MAX" if s_format == "SUPERMARKET" else "ROP_QTY"

            replenish_rows.append({
                "STORE_ID": st_id,
                "SKU_ID": sku_id,
                "REPLENISHMENT_METHOD": method,
                "REVIEW_PERIOD_WEEKS": 1,
                "SAFETY_STOCK_WEEKS": 2,
                "REORDER_POINT_UNITS": rop,
                "TARGET_MAX_UNITS": target_max,
                "ORDER_QUANTITY_MULTIPLE": 5
            })

    df_assort = pd.DataFrame(assortment_rows)
    df_assort.to_csv(os.path.join(masters_dir, "store_sku_assortment.csv"), index=False)
    print(f"Created store_sku_assortment.csv ({len(df_assort)} store-SKU pairings).")

    df_replen = pd.DataFrame(replenish_rows)
    df_replen.to_csv(os.path.join(masters_dir, "replenishment_policy.csv"), index=False)
    print(f"Created replenishment_policy.csv ({len(df_replen)} replenishment policies).")

if __name__ == "__main__":
    build_supply_network()
