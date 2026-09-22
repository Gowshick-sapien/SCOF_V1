import os
import pandas as pd
import numpy as np

def build_exogenous_commercial():
    base_dir = r"d:\projects\SCOF_V1\SCOF"
    datasets_dir = os.path.join(base_dir, "datasets")
    masters_dir = os.path.join(datasets_dir, "masters")

    print("Phase 4: Building Exogenous & Commercial Signals (Weather, Promotions, Price History)...")

    # 1. Build weather_weekly.csv
    # Regions: North, South, East, West, Central, Northeast across 52 weeks
    regions = ["North", "South", "East", "West", "Central", "Northeast"]
    weeks = list(range(1, 53))

    weather_rows = []
    np.random.seed(42)

    for w in weeks:
        for r in regions:
            # Base temperature curves
            if r == "North":
                # Winter W1-8 (12-18C), Summer W16-24 (38-44C), Monsoon W26-36 (28-34C), Post-monsoon/Winter W37-52 (15-28C)
                if w <= 8 or w >= 48:
                    base_temp = 14.0 + np.sin(w / 8.0) * 4.0
                    rainfall = np.random.uniform(2.0, 15.0)
                    humidity = np.random.uniform(65.0, 85.0)
                elif 16 <= w <= 24:
                    base_temp = 40.0 + np.random.uniform(-2.0, 4.0)
                    rainfall = np.random.uniform(0.0, 5.0)
                    humidity = np.random.uniform(25.0, 45.0)
                elif 26 <= w <= 36:
                    base_temp = 31.0 + np.random.uniform(-1.5, 2.0)
                    rainfall = np.random.uniform(80.0, 220.0)
                    humidity = np.random.uniform(75.0, 95.0)
                else:
                    base_temp = 26.0 + np.random.uniform(-2.0, 3.0)
                    rainfall = np.random.uniform(5.0, 25.0)
                    humidity = np.random.uniform(45.0, 65.0)
            elif r == "South":
                # Warm/Tropical 27-35C year-round, Monsoon peak in W23-34 and W42-46
                base_temp = 29.0 + np.sin(w / 12.0) * 3.5 + np.random.uniform(-1.0, 1.5)
                if 23 <= w <= 34 or 42 <= w <= 46:
                    rainfall = np.random.uniform(90.0, 250.0)
                    humidity = np.random.uniform(80.0, 95.0)
                else:
                    rainfall = np.random.uniform(5.0, 30.0)
                    humidity = np.random.uniform(60.0, 75.0)
            elif r == "West":
                # Hot summer W14-22 (34-39C), heavy monsoon W24-35 (150-350mm)
                if 14 <= w <= 22:
                    base_temp = 36.0 + np.random.uniform(-1.5, 3.0)
                    rainfall = np.random.uniform(0.0, 10.0)
                    humidity = np.random.uniform(55.0, 70.0)
                elif 24 <= w <= 35:
                    base_temp = 29.0 + np.random.uniform(-1.0, 1.5)
                    rainfall = np.random.uniform(140.0, 350.0)
                    humidity = np.random.uniform(85.0, 98.0)
                else:
                    base_temp = 28.0 + np.random.uniform(-1.5, 2.0)
                    rainfall = np.random.uniform(0.0, 15.0)
                    humidity = np.random.uniform(50.0, 65.0)
            elif r == "East" or r == "Northeast":
                # Humid, early monsoon W20-36
                if 15 <= w <= 22:
                    base_temp = 34.0 + np.random.uniform(-1.5, 2.5)
                    rainfall = np.random.uniform(20.0, 60.0)
                    humidity = np.random.uniform(65.0, 80.0)
                elif 23 <= w <= 36:
                    base_temp = 30.0 + np.random.uniform(-1.0, 1.5)
                    rainfall = np.random.uniform(160.0, 400.0)
                    humidity = np.random.uniform(85.0, 99.0)
                else:
                    base_temp = 22.0 + np.random.uniform(-2.0, 2.0)
                    rainfall = np.random.uniform(5.0, 25.0)
                    humidity = np.random.uniform(60.0, 75.0)
            else: # Central
                # Extreme summer W16-23 (40-45C), moderate winter W48-6 (14-20C)
                if 16 <= w <= 23:
                    base_temp = 42.0 + np.random.uniform(-2.0, 3.5)
                    rainfall = np.random.uniform(0.0, 5.0)
                    humidity = np.random.uniform(20.0, 35.0)
                elif 26 <= w <= 35:
                    base_temp = 30.0 + np.random.uniform(-1.5, 2.0)
                    rainfall = np.random.uniform(100.0, 260.0)
                    humidity = np.random.uniform(75.0, 92.0)
                elif w <= 6 or w >= 48:
                    base_temp = 16.0 + np.random.uniform(-2.0, 2.0)
                    rainfall = np.random.uniform(0.0, 8.0)
                    humidity = np.random.uniform(40.0, 60.0)
                else:
                    base_temp = 28.0 + np.random.uniform(-1.5, 2.0)
                    rainfall = np.random.uniform(5.0, 20.0)
                    humidity = np.random.uniform(35.0, 50.0)

            temp_anomaly = round(float(np.random.normal(0.0, 1.2)), 2)
            avg_temp = round(base_temp + temp_anomaly, 1)
            rainfall_anomaly = round(float(np.random.normal(0.0, 15.0)), 1)
            actual_rain = max(0.0, round(rainfall + rainfall_anomaly, 1))
            humidity_val = min(100.0, max(15.0, round(humidity + np.random.normal(0.0, 3.0), 1)))

            # Heat index calculation approximation
            heat_index = round(avg_temp + (0.5555 * (6.11 * np.exp(5417.7530 * (1/273.16 - 1/(273.15 + avg_temp))) * (humidity_val/100.0) - 10)), 1)

            # Derived regimes
            derived_regime = "NORMAL"
            extreme_flag = 0

            if avg_temp >= 41.0:
                derived_regime = "HEATWAVE"
                extreme_flag = 1
            elif avg_temp <= 11.0:
                derived_regime = "COLD_WAVE"
                extreme_flag = 1
            elif actual_rain >= 250.0:
                derived_regime = "FLOOD_RISK"
                extreme_flag = 1
            elif actual_rain >= 150.0:
                derived_regime = "HEAVY_RAIN"
            elif 23 <= w <= 25 and actual_rain >= 80.0:
                derived_regime = "MONSOON_ONSET"

            weather_rows.append({
                "WEEK": w,
                "REGION": r,
                "AVG_TEMPERATURE_C": avg_temp,
                "TEMP_ANOMALY_C": temp_anomaly,
                "RAINFALL_MM": actual_rain,
                "RAINFALL_ANOMALY_MM": rainfall_anomaly,
                "HUMIDITY_PCT": humidity_val,
                "HEAT_INDEX": heat_index,
                "EXTREME_WEATHER_FLAG": extreme_flag,
                "DERIVED_REGIME": derived_regime
            })

    df_weather = pd.DataFrame(weather_rows)
    weather_file = os.path.join(datasets_dir, "weather_weekly.csv")
    df_weather.to_csv(weather_file, index=False)
    print(f"Created weather_weekly.csv ({len(df_weather)} regional weekly records).")

    # 2. Build promotions.csv
    promotions_data = [
        {"PROMO_ID": "PRM-NY-01", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-APP", "CAMPAIGN_NAME": "New Year Apparel Clearance", "START_WEEK": 1, "PEAK_WEEK": 1, "END_WEEK": 3, "DISCOUNT_PCT": 35.0, "PROMOTION_TYPE": "CLEARANCE", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-REP-02", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-ELE", "CAMPAIGN_NAME": "Republic Day Electronics Bash", "START_WEEK": 3, "PEAK_WEEK": 4, "END_WEEK": 4, "DISCOUNT_PCT": 25.0, "PROMOTION_TYPE": "FESTIVAL_SPECIAL", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-VAL-03", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-LIF", "CAMPAIGN_NAME": "Valentine's Gifting & Lifestyle", "START_WEEK": 5, "PEAK_WEEK": 6, "END_WEEK": 7, "DISCOUNT_PCT": 20.0, "PROMOTION_TYPE": "BUNDLE", "PROMOTION_INTENSITY": "MEDIUM", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-HOL-04", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-GRO", "CAMPAIGN_NAME": "Holi Colors & Grocery Dhamaka", "START_WEEK": 10, "PEAK_WEEK": 11, "END_WEEK": 12, "DISCOUNT_PCT": 20.0, "PROMOTION_TYPE": "FESTIVAL_SPECIAL", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "North,West,Central"},
        {"PROMO_ID": "PRM-SUM-05", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-ELE", "CAMPAIGN_NAME": "Summer Cooling Appliances Fest", "START_WEEK": 16, "PEAK_WEEK": 19, "END_WEEK": 22, "DISCOUNT_PCT": 22.0, "PROMOTION_TYPE": "PERCENTAGE_OFF", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-BTS-06", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-TOY", "CAMPAIGN_NAME": "Back to School Stationery & Bags", "START_WEEK": 21, "PEAK_WEEK": 24, "END_WEEK": 26, "DISCOUNT_PCT": 25.0, "PROMOTION_TYPE": "BUNDLE", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-EOSS-07", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-APP", "CAMPAIGN_NAME": "End of Season Sale - Summer", "START_WEEK": 26, "PEAK_WEEK": 28, "END_WEEK": 30, "DISCOUNT_PCT": 45.0, "PROMOTION_TYPE": "CLEARANCE", "PROMOTION_INTENSITY": "VERY_HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-IND-08", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-HOM", "CAMPAIGN_NAME": "Independence Day Home & Living Sale", "START_WEEK": 31, "PEAK_WEEK": 33, "END_WEEK": 33, "DISCOUNT_PCT": 30.0, "PROMOTION_TYPE": "FESTIVAL_SPECIAL", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-ONAM-09", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-APP", "CAMPAIGN_NAME": "Onam Traditional Shopping Festival", "START_WEEK": 34, "PEAK_WEEK": 35, "END_WEEK": 36, "DISCOUNT_PCT": 30.0, "PROMOTION_TYPE": "FESTIVAL_SPECIAL", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "STORE", "REGION": "South"},
        {"PROMO_ID": "PRM-GAN-10", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-LIF", "CAMPAIGN_NAME": "Ganesh Chaturthi Pooja & Decor Special", "START_WEEK": 36, "PEAK_WEEK": 37, "END_WEEK": 38, "DISCOUNT_PCT": 20.0, "PROMOTION_TYPE": "FESTIVAL_SPECIAL", "PROMOTION_INTENSITY": "MEDIUM", "CHANNEL": "STORE", "REGION": "West,South"},
        {"PROMO_ID": "PRM-BBD-11", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-ELE", "CAMPAIGN_NAME": "Mega Festive Electronics Carnival", "START_WEEK": 39, "PEAK_WEEK": 41, "END_WEEK": 42, "DISCOUNT_PCT": 40.0, "PROMOTION_TYPE": "FLASH_SALE", "PROMOTION_INTENSITY": "VERY_HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-DIW-12", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-APP", "CAMPAIGN_NAME": "Diwali Grand Festive Mega Sale", "START_WEEK": 42, "PEAK_WEEK": 44, "END_WEEK": 45, "DISCOUNT_PCT": 35.0, "PROMOTION_TYPE": "FESTIVAL_SPECIAL", "PROMOTION_INTENSITY": "VERY_HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-BF-13", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-ELE", "CAMPAIGN_NAME": "Black Friday Cyber Tech Week", "START_WEEK": 46, "PEAK_WEEK": 47, "END_WEEK": 48, "DISCOUNT_PCT": 45.0, "PROMOTION_TYPE": "FLASH_SALE", "PROMOTION_INTENSITY": "VERY_HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"},
        {"PROMO_ID": "PRM-WED-14", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-APP", "CAMPAIGN_NAME": "Winter Wedding & Luxury Gala", "START_WEEK": 47, "PEAK_WEEK": 49, "END_WEEK": 51, "DISCOUNT_PCT": 25.0, "PROMOTION_TYPE": "BUNDLE", "PROMOTION_INTENSITY": "HIGH", "CHANNEL": "STORE", "REGION": "North,Central,West"},
        {"PROMO_ID": "PRM-XMAS-15", "TARGET_LEVEL": "DEPARTMENT", "TARGET_ID": "DEP-LIF", "CAMPAIGN_NAME": "Christmas & Year End Mega Bash", "START_WEEK": 50, "PEAK_WEEK": 51, "END_WEEK": 52, "DISCOUNT_PCT": 35.0, "PROMOTION_TYPE": "CLEARANCE", "PROMOTION_INTENSITY": "VERY_HIGH", "CHANNEL": "OMNICHANNEL", "REGION": "PAN_INDIA"}
    ]

    df_promos = pd.DataFrame(promotions_data)
    promo_file = os.path.join(datasets_dir, "promotions.csv")
    df_promos.to_csv(promo_file, index=False)
    print(f"Created promotions.csv ({len(df_promos)} promotional campaigns).")

    # 3. Build price_history.csv
    print("Building price_history.csv for 49,616 SKUs over 52 weeks...")
    df_skus = pd.read_csv(os.path.join(masters_dir, "sku_master.csv"))
    df_prod = pd.read_csv(os.path.join(masters_dir, "product_master.csv"))
    df_fam = pd.read_csv(os.path.join(masters_dir, "product_family_master.csv"))
    df_subcat = pd.read_csv(os.path.join(masters_dir, "subcategory_master.csv"))
    df_cat = pd.read_csv(os.path.join(masters_dir, "category_master.csv"))

    # Build SKU -> Department mapping for promo matching
    m1 = pd.merge(df_skus[['SKU_ID', 'PRODUCT_ID', 'BASE_RETAIL_PRICE']], df_prod[['PRODUCT_ID', 'FAMILY_ID']], on="PRODUCT_ID", how="left")
    m2 = pd.merge(m1, df_fam[['FAMILY_ID', 'SUBCATEGORY_ID']], on="FAMILY_ID", how="left")
    m3 = pd.merge(m2, df_subcat[['SUBCATEGORY_ID', 'CATEGORY_ID']], on="SUBCATEGORY_ID", how="left")
    sku_full = pd.merge(m3, df_cat[['CATEGORY_ID', 'DEPARTMENT_ID']], on="CATEGORY_ID", how="left")

    sku_ids = sku_full['SKU_ID'].values
    base_prices = sku_full['BASE_RETAIL_PRICE'].values
    dept_ids = sku_full['DEPARTMENT_ID'].values
    n_skus = len(sku_full)

    # Precalculate active promos by week and department
    promo_by_week_dept = {}
    for _, p in df_promos.iterrows():
        p_dept = p['TARGET_ID']
        discount = float(p['DISCOUNT_PCT'])
        ptype = p['PROMOTION_TYPE']
        for wk in range(int(p['START_WEEK']), int(p['END_WEEK']) + 1):
            key = (wk, p_dept)
            if key not in promo_by_week_dept or discount > promo_by_week_dept[key][0]:
                promo_by_week_dept[key] = (discount, ptype)

    price_history_file = os.path.join(datasets_dir, "price_history.csv")

    for w in weeks:
        # Vectorized price calculation for week w
        discounts = np.zeros(n_skus)
        reasons = np.full(n_skus, "NORMAL", dtype=object)

        for d_id in np.unique(dept_ids):
            key = (w, d_id)
            if key in promo_by_week_dept:
                disc, ptype = promo_by_week_dept[key]
                mask = (dept_ids == d_id)
                discounts[mask] = disc
                reasons[mask] = "CLEARANCE" if ptype == "CLEARANCE" else "FESTIVAL" if ptype == "FESTIVAL_SPECIAL" else "PROMOTION"

        selling_prices = np.round(base_prices * (1.0 - (discounts / 100.0)), 2)
        price_indices = np.round(selling_prices / np.maximum(base_prices, 0.01), 3)

        df_week_price = pd.DataFrame({
            "WEEK": w,
            "SKU_ID": sku_ids,
            "BASE_PRICE": base_prices,
            "SELLING_PRICE": selling_prices,
            "DISCOUNT_PCT": discounts,
            "PRICE_INDEX": price_indices,
            "PRICE_CHANGE_REASON": reasons
        })

        if w == 1:
            df_week_price.to_csv(price_history_file, index=False, mode='w')
        else:
            df_week_price.to_csv(price_history_file, index=False, mode='a', header=False)

    print(f"Created price_history.csv ({n_skus * 52} price records over 52 weeks).")

if __name__ == "__main__":
    build_exogenous_commercial()
