import os
import shutil
import pandas as pd
import numpy as np

def build_event_layer():
    base_dir = r"d:\projects\SCOF_V1\SCOF"
    datasets_dir = os.path.join(base_dir, "datasets")
    adv_dir = os.path.join(datasets_dir, "advanced_events")
    masters_dir = os.path.join(datasets_dir, "masters")
    os.makedirs(adv_dir, exist_ok=True)

    print("Phase 3: Building Event Layer (Canonical Master, Impacts, Interactions, Regional)...")

    # 1. Canonical Event Master
    root_master_path = os.path.join(base_dir, "india_retail_seasonality_event_master_2026.csv")
    ds_master_path = os.path.join(datasets_dir, "india_retail_seasonality_event_master_2026.csv")
    adv_master_path = os.path.join(adv_dir, "event_master.csv")

    shutil.copy2(root_master_path, ds_master_path)
    shutil.copy2(root_master_path, adv_master_path)
    print("Copied canonical 19-column event master to datasets/ and datasets/advanced_events/.")

    df_events = pd.read_csv(root_master_path)
    print(f"Loaded {len(df_events)} events from master.")

    # Load categories and subcategories for stable ID matching
    df_cat = pd.read_csv(os.path.join(masters_dir, "category_master.csv"))
    df_subcat = pd.read_csv(os.path.join(masters_dir, "subcategory_master.csv"))

    # Build lookup dictionaries
    cat_lookup = {row['CATEGORY_NAME'].lower(): row['CATEGORY_ID'] for _, row in df_cat.iterrows()}
    subcat_lookup = {row['SUBCATEGORY_NAME'].lower(): row['SUBCATEGORY_ID'] for _, row in df_subcat.iterrows()}

    # 2. Build Event Impact Matrix with Stable Taxonomy IDs
    impact_rows = []
    
    # Negative impact rules for specific event types
    fasting_negative_subcats = ["meat", "chicken", "seafood", "alcohol", "pork", "beef"]
    heatwave_negative_subcats = ["heaters", "winterwear", "heavy woolens", "quilts", "blankets"]
    coldwave_negative_subcats = ["air conditioners", "coolers", "swimwear", "cold beverages", "ice cream"]
    monsoon_negative_subcats = ["outdoor recreation", "camping", "construction materials"]

    for _, ev in df_events.iterrows():
        ev_id = ev['Event_ID']
        ev_name = ev['Event_Name']
        ev_type = str(ev.get('Event_Type', '')).upper()
        keywords = str(ev.get('Category_Impact_Keywords', ''))
        base_mult = float(ev.get('Demand_Multiplier', 1.5))
        
        strength = "HIGH" if base_mult >= 2.0 else "MEDIUM" if base_mult >= 1.4 else "LOW"
        apply_mode = "MULTIPLICATIVE"

        kw_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]

        matched_targets = set()

        for kw in kw_list:
            # Check direct subcategory match
            for sname, sid in subcat_lookup.items():
                if kw in sname or sname in kw:
                    if sid not in matched_targets:
                        matched_targets.add(sid)
                        impact_rows.append({
                            "EVENT_ID": ev_id,
                            "TARGET_LEVEL": "SUBCATEGORY",
                            "TARGET_ID": sid,
                            "IMPACT_DIRECTION": "POSITIVE",
                            "DEMAND_MULTIPLIER": round(base_mult, 2),
                            "IMPACT_STRENGTH": strength,
                            "APPLY_MODE": apply_mode
                        })

            # Check direct category match
            for cname, cid in cat_lookup.items():
                if kw in cname or cname in kw:
                    if cid not in matched_targets:
                        matched_targets.add(cid)
                        impact_rows.append({
                            "EVENT_ID": ev_id,
                            "TARGET_LEVEL": "CATEGORY",
                            "TARGET_ID": cid,
                            "IMPACT_DIRECTION": "POSITIVE",
                            "DEMAND_MULTIPLIER": round(base_mult, 2),
                            "IMPACT_STRENGTH": strength,
                            "APPLY_MODE": apply_mode
                        })

        # Ensure at least one positive impact if keywords were broad
        if not matched_targets:
            # Fallback to category based on event type
            fallback_cid = "CAT-012" # Festival & Seasonal default
            if "Food" in ev_type or "Harvest" in str(ev.get('Sub_Type', '')): fallback_cid = "CAT-001" # Beverages / Food
            elif "Commercial" in ev_type: fallback_cid = "CAT-005" # Apparel / Electronics
            impact_rows.append({
                "EVENT_ID": ev_id,
                "TARGET_LEVEL": "CATEGORY",
                "TARGET_ID": fallback_cid,
                "IMPACT_DIRECTION": "POSITIVE",
                "DEMAND_MULTIPLIER": round(base_mult, 2),
                "IMPACT_STRENGTH": strength,
                "APPLY_MODE": apply_mode
            })

        # Inject Negative Impacts where semantically required
        ev_text = (ev_name + " " + str(ev.get('Sub_Type', ''))).lower()
        if any(f in ev_text for f in ["fasting", "navratri", "ramadan", "paryushan", "shravan", "ekadashi"]):
            for sname, sid in subcat_lookup.items():
                if any(neg in sname for neg in fasting_negative_subcats):
                    impact_rows.append({
                        "EVENT_ID": ev_id,
                        "TARGET_LEVEL": "SUBCATEGORY",
                        "TARGET_ID": sid,
                        "IMPACT_DIRECTION": "NEGATIVE",
                        "DEMAND_MULTIPLIER": 0.35,
                        "IMPACT_STRENGTH": "HIGH",
                        "APPLY_MODE": "MULTIPLICATIVE"
                    })

        if "heatwave" in ev_text or "peak heat" in ev_text:
            for sname, sid in subcat_lookup.items():
                if any(neg in sname for neg in heatwave_negative_subcats):
                    impact_rows.append({
                        "EVENT_ID": ev_id,
                        "TARGET_LEVEL": "SUBCATEGORY",
                        "TARGET_ID": sid,
                        "IMPACT_DIRECTION": "NEGATIVE",
                        "DEMAND_MULTIPLIER": 0.20,
                        "IMPACT_STRENGTH": "HIGH",
                        "APPLY_MODE": "MULTIPLICATIVE"
                    })

        if "cold wave" in ev_text or "winter peak" in ev_text:
            for sname, sid in subcat_lookup.items():
                if any(neg in sname for neg in coldwave_negative_subcats):
                    impact_rows.append({
                        "EVENT_ID": ev_id,
                        "TARGET_LEVEL": "SUBCATEGORY",
                        "TARGET_ID": sid,
                        "IMPACT_DIRECTION": "NEGATIVE",
                        "DEMAND_MULTIPLIER": 0.30,
                        "IMPACT_STRENGTH": "HIGH",
                        "APPLY_MODE": "MULTIPLICATIVE"
                    })

        if "heavy rain" in ev_text or "flood" in ev_text or "monsoon peak" in ev_text:
            for sname, sid in subcat_lookup.items():
                if any(neg in sname for neg in monsoon_negative_subcats):
                    impact_rows.append({
                        "EVENT_ID": ev_id,
                        "TARGET_LEVEL": "SUBCATEGORY",
                        "TARGET_ID": sid,
                        "IMPACT_DIRECTION": "NEGATIVE",
                        "DEMAND_MULTIPLIER": 0.40,
                        "IMPACT_STRENGTH": "MEDIUM",
                        "APPLY_MODE": "MULTIPLICATIVE"
                    })

    df_impact = pd.DataFrame(impact_rows).drop_duplicates(subset=["EVENT_ID", "TARGET_LEVEL", "TARGET_ID"])
    impact_file = os.path.join(adv_dir, "event_impact_matrix.csv")
    df_impact.to_csv(impact_file, index=False)
    print(f"Created event_impact_matrix.csv ({len(df_impact)} impact mappings).")

    # 3. Build Event Interactions Matrix (Temporal Overlap + Causal Compatibility)
    interaction_rows = []
    num_events = len(df_events)

    for i in range(num_events):
        ev1 = df_events.iloc[i]
        w1_start = max(1, int(ev1.get('Typical_Start_Week', ev1['Annual_Week_Peak'])) - int(ev1.get('Lead_Time_Weeks', 1)))
        w1_end = min(52, int(ev1.get('Typical_End_Week', ev1['Annual_Week_Peak'])) + int(ev1.get('Decay_Weeks', 1)))
        t1 = str(ev1.get('Event_Type', '')).upper()

        for j in range(i + 1, num_events):
            ev2 = df_events.iloc[j]
            w2_start = max(1, int(ev2.get('Typical_Start_Week', ev2['Annual_Week_Peak'])) - int(ev2.get('Lead_Time_Weeks', 1)))
            w2_end = min(52, int(ev2.get('Typical_End_Week', ev2['Annual_Week_Peak'])) + int(ev2.get('Decay_Weeks', 1)))
            t2 = str(ev2.get('Event_Type', '')).upper()

            # Check temporal overlap
            if max(w1_start, w2_start) <= min(w1_end, w2_end):
                # Check causal compatibility
                pair_types = {t1, t2}
                itype = None
                icap = 4.0
                desc = f"{ev1['Event_Name']} + {ev2['Event_Name']}"

                if "COMMERCIAL" in pair_types and ("FESTIVAL" in pair_types or "CALENDAR" in pair_types):
                    itype = "AMPLIFICATION"
                    icap = 5.0
                elif "WEATHER" in pair_types and ("FESTIVAL" in pair_types or "LIFECYCLE" in pair_types):
                    itype = "ATTENUATION"
                    icap = 3.5
                elif "WEATHER" in pair_types and "COMMERCIAL" in pair_types:
                    itype = "AMPLIFICATION"
                    icap = 4.5
                elif len(pair_types) == 1 and ("FESTIVAL" in pair_types or "CALENDAR" in pair_types):
                    itype = "SATURATION"
                    icap = 4.0
                elif "LIFECYCLE" in pair_types and "COMMERCIAL" in pair_types:
                    itype = "AMPLIFICATION"
                    icap = 4.0

                if itype:
                    interaction_rows.append({
                        "EVENT_ID_1": ev1['Event_ID'],
                        "EVENT_ID_2": ev2['Event_ID'],
                        "INTERACTION_TYPE": itype,
                        "INTERACTION_CAP": icap,
                        "DESCRIPTION": desc
                    })

    df_interactions = pd.DataFrame(interaction_rows)
    inter_file = os.path.join(adv_dir, "event_interactions.csv")
    df_interactions.to_csv(inter_file, index=False)
    print(f"Created event_interactions.csv ({len(df_interactions)} validated interactions).")

    # 4. Build Regional Event Weights
    regional_rows = []
    macro_regions = ["North", "South", "East", "West", "Central", "Northeast"]

    for _, ev in df_events.iterrows():
        ev_id = ev['Event_ID']
        geo_scope = str(ev.get('Geography_Weight', 'National')).strip()
        region_desc = str(ev.get('Region', 'India')).lower()

        if geo_scope.lower() == "national" or "pan-india" in region_desc or "india" == region_desc.strip():
            regional_rows.append({
                "EVENT_ID": ev_id,
                "GEOGRAPHIC_LEVEL": "NATIONAL",
                "GEOGRAPHIC_TARGET": "PAN_INDIA",
                "GEOGRAPHIC_WEIGHT": 1.0
            })
        else:
            # Regional event - determine weights for each macro-region
            focal_regions = []
            if "north" in region_desc or "punjab" in region_desc or "delhi" in region_desc or "haryana" in region_desc:
                focal_regions.append("North")
            if "south" in region_desc or "tamil" in region_desc or "kerala" in region_desc or "karnataka" in region_desc or "andhra" in region_desc or "telangana" in region_desc:
                focal_regions.append("South")
            if "east" in region_desc or "bengal" in region_desc or "odisha" in region_desc or "bihar" in region_desc:
                focal_regions.append("East")
            if "west" in region_desc or "maharashtra" in region_desc or "gujarat" in region_desc or "goa" in region_desc:
                focal_regions.append("West")
            if "central" in region_desc or "madhya" in region_desc:
                focal_regions.append("Central")
            if "northeast" in region_desc or "assam" in region_desc:
                focal_regions.append("Northeast")

            if not focal_regions:
                focal_regions = ["North", "South"] # fallback

            for r in macro_regions:
                weight = 1.0 if r in focal_regions else 0.15
                regional_rows.append({
                    "EVENT_ID": ev_id,
                    "GEOGRAPHIC_LEVEL": "REGIONAL",
                    "GEOGRAPHIC_TARGET": r,
                    "GEOGRAPHIC_WEIGHT": weight
                })

    df_regional = pd.DataFrame(regional_rows)
    reg_file = os.path.join(adv_dir, "regional_event_weights.csv")
    df_regional.to_csv(reg_file, index=False)
    print(f"Created regional_event_weights.csv ({len(df_regional)} regional weight rules).")

if __name__ == "__main__":
    build_event_layer()
