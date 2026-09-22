import os
import time
import pandas as pd
import numpy as np

def run_v2_simulation():
    base_dir = r"d:\projects\SCOF_V1\SCOF"
    datasets_dir = os.path.join(base_dir, "datasets")
    masters_dir = os.path.join(datasets_dir, "masters")
    adv_dir = os.path.join(datasets_dir, "advanced_events")
    output_file = os.path.join(datasets_dir, "weekly_demand_history_v2.csv")

    print("Initializing Highly-Optimized V2 Multi-Signal Demand & Physical Supply Chain Engine...", flush=True)
    start_time = time.time()

    # 1. LOAD MASTERS & CONTRACTS
    print("Loading masters, contracts, and matrices...", flush=True)
    df_cat = pd.read_csv(os.path.join(masters_dir, "category_master.csv"))
    df_subcat = pd.read_csv(os.path.join(masters_dir, "subcategory_master.csv"))
    df_fam = pd.read_csv(os.path.join(masters_dir, "product_family_master.csv"))
    df_prod = pd.read_csv(os.path.join(masters_dir, "product_master.csv"))
    df_sku = pd.read_csv(os.path.join(masters_dir, "sku_master.csv"))
    
    df_store = pd.read_csv(os.path.join(masters_dir, "store_master.csv"))
    df_assort = pd.read_csv(os.path.join(masters_dir, "store_sku_assortment.csv"))
    df_replen = pd.read_csv(os.path.join(masters_dir, "replenishment_policy.csv"))
    df_supp_sku = pd.read_csv(os.path.join(masters_dir, "supplier_sku_map.csv"))

    df_events = pd.read_csv(os.path.join(adv_dir, "event_master.csv"))
    df_impact = pd.read_csv(os.path.join(adv_dir, "event_impact_matrix.csv"))
    df_interact = pd.read_csv(os.path.join(adv_dir, "event_interactions.csv"))
    df_region = pd.read_csv(os.path.join(adv_dir, "regional_event_weights.csv"))

    df_weather = pd.read_csv(os.path.join(datasets_dir, "weather_weekly.csv"))
    df_promos = pd.read_csv(os.path.join(datasets_dir, "promotions.csv"))

    # Primary supplier lead time lookup for SKUs
    prim_supp = df_supp_sku[df_supp_sku['PRIMARY_FLAG'] == 1].drop_duplicates(subset=['SKU_ID'])
    sku_lead_days = dict(zip(prim_supp['SKU_ID'], prim_supp['LEAD_TIME_DAYS']))
    sku_moq = dict(zip(prim_supp['SKU_ID'], prim_supp['MOQ_UNITS']))

    # SKU taxonomy mapping
    m1 = pd.merge(df_sku, df_prod[['PRODUCT_ID', 'FAMILY_ID']], on="PRODUCT_ID", how="left")
    m2 = pd.merge(m1, df_fam[['FAMILY_ID', 'SUBCATEGORY_ID']], on="FAMILY_ID", how="left")
    m3 = pd.merge(m2, df_subcat[['SUBCATEGORY_ID', 'CATEGORY_ID']], on="SUBCATEGORY_ID", how="left")
    sku_taxonomy = pd.merge(m3, df_cat[['CATEGORY_ID', 'DEPARTMENT_ID']], on="CATEGORY_ID", how="left")

    store_region_map = dict(zip(df_store['STORE_ID'], df_store['REGION']))
    store_format_map = dict(zip(df_store['STORE_ID'], df_store['STORE_FORMAT']))

    # Merge assortment with replenishment and taxonomy
    print("Joining assortment and physical supply parameters...", flush=True)
    df_active = pd.merge(df_assort, df_replen, on=["STORE_ID", "SKU_ID"], how="inner")
    df_active = pd.merge(df_active, sku_taxonomy[[
        'SKU_ID', 'CATEGORY_ID', 'SUBCATEGORY_ID', 'DEPARTMENT_ID',
        'BASE_UNIT_COST', 'BASE_RETAIL_PRICE', 'DEMAND_VOLATILITY',
        'PERISHABILITY_TIER', 'SEASONALITY_PROFILE', 'WEATHER_SENSITIVITY',
        'FESTIVAL_AFFINITY', 'PROMOTION_SENSITIVITY', 'PRICE_ELASTICITY', 'REGIONAL_AFFINITY'
    ]], on="SKU_ID", how="left")

    df_active['REGION'] = df_active['STORE_ID'].map(store_region_map)
    df_active['STORE_FORMAT'] = df_active['STORE_ID'].map(store_format_map)

    # Lead time in weeks (min 1 week)
    df_active['LEAD_TIME_WEEKS'] = df_active['SKU_ID'].map(lambda s: max(1, int(round(sku_lead_days.get(s, 14) / 7.0))))
    df_active['MOQ_UNITS'] = df_active['SKU_ID'].map(lambda s: sku_moq.get(s, 20))

    # Baseline demand per store-SKU
    format_map = {"HYPERMARKET": 1.3, "SUPERMARKET": 1.0, "EXPRESS": 0.6}
    format_mult = np.array([format_map.get(str(f), 1.0) for f in df_active['STORE_FORMAT'].tolist()], dtype=np.float64)
    cost_val = np.array(pd.to_numeric(df_active['BASE_UNIT_COST'], errors='coerce').fillna(50.0).tolist(), dtype=np.float64)
    base_demand = np.clip(1200.0 / (cost_val + 2.0), 4.0, 180.0) * format_mult
    df_active['BASELINE_DEMAND'] = np.round(base_demand).astype(int)

    n_pairings = len(df_active)
    print(f"Total active Store-SKU pairings: {n_pairings}", flush=True)

    # 2. FAST PRE-INDEXING USING PANDAS GROUPBY (INSTANT)
    print("Pre-indexing static impact targets using fast grouping...", flush=True)
    df_active['ROW_INDEX'] = np.arange(n_pairings)
    
    subcat_to_indices = df_active.groupby('SUBCATEGORY_ID')['ROW_INDEX'].apply(np.array).to_dict()
    cat_to_indices = df_active.groupby('CATEGORY_ID')['ROW_INDEX'].apply(np.array).to_dict()
    dept_to_indices = df_active.groupby('DEPARTMENT_ID')['ROW_INDEX'].apply(np.array).to_dict()
    sku_to_indices = df_active.groupby('SKU_ID')['ROW_INDEX'].apply(np.array).to_dict()

    subcat_ids = df_active['SUBCATEGORY_ID'].to_numpy()
    cat_ids = df_active['CATEGORY_ID'].to_numpy()
    dept_ids = df_active['DEPARTMENT_ID'].to_numpy()
    sku_ids = df_active['SKU_ID'].to_numpy()
    store_ids = df_active['STORE_ID'].to_numpy()
    regions = df_active['REGION'].to_numpy()
    b_demands = df_active['BASELINE_DEMAND'].to_numpy(dtype=np.int64)
    volatilities = df_active['DEMAND_VOLATILITY'].to_numpy(dtype=np.float64)
    shelf_capacities = df_active['ALLOCATED_SHELF_CAPACITY_UNITS'].to_numpy(dtype=np.int64)
    reorder_points = df_active['REORDER_POINT_UNITS'].to_numpy(dtype=np.int64)
    target_maxs = df_active['TARGET_MAX_UNITS'].to_numpy(dtype=np.int64)
    lead_times = df_active['LEAD_TIME_WEEKS'].to_numpy(dtype=np.int64)
    moqs = df_active['MOQ_UNITS'].to_numpy(dtype=np.int64)
    perish_tiers = df_active['PERISHABILITY_TIER'].to_numpy()
    elasticities = df_active['PRICE_ELASTICITY'].to_numpy(dtype=np.float64)

    regional_weights = {}
    for _, row in df_region.iterrows():
        regional_weights[(row['EVENT_ID'], row['GEOGRAPHIC_TARGET'])] = float(row['GEOGRAPHIC_WEIGHT'])

    # Pre-build active events per week
    events_by_week = {w: [] for w in range(1, 53)}
    for _, ev in df_events.iterrows():
        ev_id = ev['Event_ID']
        ev_type = str(ev.get('Event_Type', '')).upper()
        p_wk = int(ev['Annual_Week_Peak'])
        lead = max(1, int(ev.get('Lead_Time_Weeks', 1)))
        decay = max(1, int(ev.get('Decay_Weeks', 1)))
        is_national = (str(ev.get('Geography_Weight', '')).lower() == 'national')

        ev_impacts = df_impact[df_impact['EVENT_ID'] == ev_id]
        if ev_impacts.empty:
            continue

        compiled_impacts = []
        for _, imp in ev_impacts.iterrows():
            t_lvl = imp['TARGET_LEVEL']
            t_id = imp['TARGET_ID']
            mult = float(imp['DEMAND_MULTIPLIER'])
            direction = imp['IMPACT_DIRECTION']

            idx = None
            if t_lvl == 'SUBCATEGORY': idx = subcat_to_indices.get(t_id)
            elif t_lvl == 'CATEGORY': idx = cat_to_indices.get(t_id)
            elif t_lvl == 'DEPARTMENT': idx = dept_to_indices.get(t_id)
            else: idx = sku_to_indices.get(t_id)

            if idx is None or len(idx) == 0:
                continue

            target_regions = regions[idx]
            geo_w = np.array([regional_weights.get((ev_id, r), 1.0 if is_national else 0.15) for r in target_regions], dtype=np.float32)

            compiled_impacts.append({
                "indices": idx,
                "multiplier": mult,
                "direction": direction,
                "geo_weights": geo_w
            })

        for w in range(max(1, p_wk - lead), min(53, p_wk + decay + 1)):
            if (p_wk - lead) <= w <= p_wk:
                act = 1.0 - (p_wk - w) / lead
            else:
                act = 1.0 - (w - p_wk) / decay
            
            if act > 0:
                events_by_week[w].append({
                    "event_id": ev_id,
                    "event_type": ev_type,
                    "activation": np.float32(act),
                    "impacts": compiled_impacts
                })

    # Interaction caps lookup
    interact_caps = {}
    for _, row in df_interact.iterrows():
        interact_caps[f"{row['EVENT_ID_1']}_{row['EVENT_ID_2']}"] = float(row['INTERACTION_CAP'])
        interact_caps[f"{row['EVENT_ID_2']}_{row['EVENT_ID_1']}"] = float(row['INTERACTION_CAP'])

    # Weather lookup
    weather_by_week_reg = {}
    for _, wrow in df_weather.iterrows():
        weather_by_week_reg[(int(wrow['WEEK']), wrow['REGION'])] = wrow

    # Promotion lookup
    promo_by_week_dept = {}
    for _, prow in df_promos.iterrows():
        t_id = prow['TARGET_ID']
        disc = float(prow['DISCOUNT_PCT'])
        for wk in range(int(prow['START_WEEK']), int(prow['END_WEEK']) + 1):
            key = (wk, t_id)
            if key not in promo_by_week_dept or disc > promo_by_week_dept[key]:
                promo_by_week_dept[key] = disc

    # 3. INITIALIZE INVENTORY PIPELINE
    current_inventory = (target_maxs * np.random.uniform(0.65, 0.95, n_pairings)).astype(int)
    in_transit_pipeline = {w: np.zeros(n_pairings, dtype=int) for w in range(1, 65)}
    in_transit_pipeline[1] = (reorder_points * np.random.uniform(0.5, 1.0, n_pairings)).astype(int)
    in_transit_pipeline[2] = (reorder_points * np.random.uniform(0.3, 0.8, n_pairings)).astype(int)

    np.random.seed(42)

    print(f"Pre-indexing complete ({time.time() - start_time:.2f}s). Beginning 52-week longitudinal simulation...", flush=True)

    for w in range(1, 53):
        t_w_start = time.time()
        # A. Calculate Active Demand Multipliers for Week w
        F_festival = np.ones(n_pairings, dtype=np.float32)
        F_commercial = np.ones(n_pairings, dtype=np.float32)
        F_lifecycle = np.ones(n_pairings, dtype=np.float32)
        F_weather = np.ones(n_pairings, dtype=np.float32)

        active_ev_ids = []
        for ev in events_by_week[w]:
            ev_id = ev['event_id']
            ev_type = ev['event_type']
            act = ev['activation']
            active_ev_ids.append(ev_id)

            for imp in ev['impacts']:
                idx = imp['indices']
                mult = imp['multiplier']
                direction = imp['direction']
                geo_w = imp['geo_weights']

                if direction == 'NEGATIVE':
                    adj = 1.0 - ((1.0 - mult) * act * geo_w)
                    adj = np.clip(adj, 0.15, 1.0)
                    if ev_type == 'COMMERCIAL': F_commercial[idx] = np.minimum(F_commercial[idx], adj)
                    elif ev_type == 'LIFECYCLE': F_lifecycle[idx] = np.minimum(F_lifecycle[idx], adj)
                    else: F_festival[idx] = np.minimum(F_festival[idx], adj)
                else:
                    adj = 1.0 + ((mult - 1.0) * act * geo_w)
                    if ev_type == 'COMMERCIAL': F_commercial[idx] = np.maximum(F_commercial[idx], adj)
                    elif ev_type == 'LIFECYCLE': F_lifecycle[idx] = np.maximum(F_lifecycle[idx], adj)
                    else: F_festival[idx] = np.maximum(F_festival[idx], adj)

        # Weather Signals (Derived Regimes)
        for r in np.unique(regions):
            w_info = weather_by_week_reg.get((w, r))
            if w_info is not None:
                regime = w_info['DERIVED_REGIME']
                temp = w_info['AVG_TEMPERATURE_C']
                rain = w_info['RAINFALL_MM']

                if regime == 'HEATWAVE' or temp >= 38.0:
                    for d_target, boost in [('DEP-ELE', 2.2), ('DEP-FNB', 1.8)]:
                        d_idx = dept_to_indices.get(d_target)
                        if d_idx is not None:
                            sub_idx = d_idx[regions[d_idx] == r]
                            F_weather[sub_idx] = np.maximum(F_weather[sub_idx], boost)
                elif regime == 'COLD_WAVE' or temp <= 13.0:
                    d_idx = dept_to_indices.get('DEP-APP')
                    if d_idx is not None:
                        sub_idx = d_idx[regions[d_idx] == r]
                        F_weather[sub_idx] = np.maximum(F_weather[sub_idx], 2.0)
                elif regime in ['HEAVY_RAIN', 'FLOOD_RISK'] or rain >= 120.0:
                    d_idx = dept_to_indices.get('DEP-LIF')
                    if d_idx is not None:
                        sub_idx = d_idx[regions[d_idx] == r]
                        F_weather[sub_idx] = np.maximum(F_weather[sub_idx], 2.4)

        # Promotions & Price Index
        F_price = np.ones(n_pairings, dtype=np.float32)
        for d_id in np.unique(dept_ids):
            disc = promo_by_week_dept.get((w, d_id), 0.0)
            if disc > 0:
                d_idx = dept_to_indices.get(d_id)
                if d_idx is not None:
                    p_idx = 1.0 - (disc / 100.0)
                    promo_lift = np.clip(np.power(p_idx, elasticities[d_idx]), 1.0, 3.5)
                    F_price[d_idx] = promo_lift

        # Interaction Capping
        interaction_factor = np.ones(n_pairings, dtype=np.float32)
        if len(active_ev_ids) >= 2:
            combined = F_festival * F_commercial * F_lifecycle * F_weather
            for i in range(len(active_ev_ids)):
                for j in range(i + 1, len(active_ev_ids)):
                    pair_key = f"{active_ev_ids[i]}_{active_ev_ids[j]}"
                    if pair_key in interact_caps:
                        cap = interact_caps[pair_key]
                        interaction_factor = np.where(combined > cap, cap / np.maximum(combined, 0.01), interaction_factor)

        # Stochastic Noise
        noise = np.random.normal(1.0, volatilities).astype(np.float32)
        noise = np.clip(noise, 0.5, 1.6)

        # Latent Demand (Layer A)
        combined_factors = F_festival * F_commercial * F_lifecycle * F_weather * F_price * interaction_factor
        latent_demand = np.maximum(0, np.round(b_demands * combined_factors * noise).astype(int))

        # B. Physical Inventory Simulation (Layer B)
        opening_inventory = current_inventory.copy()
        inbound_arrived = in_transit_pipeline.get(w, np.zeros(n_pairings, dtype=int))

        available_shelf = np.maximum(0, shelf_capacities - opening_inventory)
        received_inbound = np.minimum(inbound_arrived, available_shelf)

        spoilage_rate = np.where(perish_tiers == 'HIGH', 0.06, np.where(perish_tiers == 'MEDIUM', 0.015, 0.0))
        spoiled_units = np.round(opening_inventory * spoilage_rate).astype(int)

        available_inventory = np.maximum(0, opening_inventory + received_inbound - spoiled_units)
        observed_sales = np.minimum(latent_demand, available_inventory)
        lost_sales = np.maximum(0, latent_demand - observed_sales)
        stockout_flag = np.where(available_inventory <= 0, 1, 0)
        closing_inventory = available_inventory - observed_sales

        # Replenishment Order Decision
        future_pipeline = np.zeros(n_pairings, dtype=int)
        for fw in range(w + 1, w + 8):
            if fw in in_transit_pipeline:
                future_pipeline += in_transit_pipeline[fw]

        inventory_position = closing_inventory + future_pipeline
        reorder_mask = (inventory_position <= reorder_points)
        reorder_qty = np.where(reorder_mask, np.maximum(target_maxs - inventory_position, moqs), 0)
        reorder_flag = np.where(reorder_mask, 1, 0)

        for lt in np.unique(lead_times):
            arr_week = w + lt
            lt_mask = (lead_times == lt) & reorder_mask
            if arr_week not in in_transit_pipeline:
                in_transit_pipeline[arr_week] = np.zeros(n_pairings, dtype=int)
            in_transit_pipeline[arr_week][lt_mask] += reorder_qty[lt_mask]

        in_transit_now = future_pipeline.copy()
        current_inventory = closing_inventory

        service_level = np.where(latent_demand > 0, np.round(observed_sales / np.maximum(latent_demand, 1), 3), 1.0)
        fill_rate = np.round(observed_sales / np.maximum(observed_sales + lost_sales, 1), 3)

        # Log results
        df_week_out = pd.DataFrame({
            "Week": w,
            "Store_ID": store_ids,
            "Region": regions,
            "SKU_ID": sku_ids,
            "Baseline_Demand": b_demands,
            "Seasonality_Factor": 1.0,
            "Festival_Factor": np.round(F_festival, 2),
            "Commercial_Factor": np.round(F_commercial, 2),
            "Lifecycle_Factor": np.round(F_lifecycle, 2),
            "Weather_Factor": np.round(F_weather, 2),
            "Competitor_Factor": 1.0,
            "Interaction_Factor": np.round(interaction_factor, 2),
            "Random_Factor": np.round(noise, 3),
            "LATENT_DEMAND": latent_demand,
            "Opening_Inventory": opening_inventory,
            "PO_Units": reorder_qty,
            "PO_Receipt_Units": received_inbound,
            "In_Transit_Inventory": in_transit_now,
            "Available_Inventory": available_inventory,
            "Expired_Units": 0,
            "Spoiled_Units": spoiled_units,
            "OBSERVED_SALES": observed_sales,
            "LOST_SALES": lost_sales,
            "Stockout_Flag": stockout_flag,
            "Closing_Inventory": closing_inventory,
            "Reorder_Flag": reorder_flag,
            "Reorder_Quantity": reorder_qty,
            "Lead_Time_Weeks": lead_times,
            "Service_Level": service_level,
            "Fill_Rate": fill_rate
        })

        if w == 1:
            df_week_out.to_csv(output_file, index=False, mode='w')
        else:
            df_week_out.to_csv(output_file, index=False, mode='a', header=False)

        print(f"Week {w:02d}/52 finished in {time.time() - t_w_start:.2f}s (Cumulative: {time.time() - start_time:.1f}s)", flush=True)

    print(f"V2 Simulation completed successfully in {time.time() - start_time:.2f} seconds.", flush=True)
    print(f"Authoritative ground truth exported to: {output_file}", flush=True)

if __name__ == "__main__":
    run_v2_simulation()
