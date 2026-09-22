import os
import re
import glob
import pandas as pd
import numpy as np

def build_merchandise_masters():
    base_dir = r"d:\projects\SCOF_V1\SCOF"
    datasets_dir = os.path.join(base_dir, "datasets")
    masters_dir = os.path.join(datasets_dir, "masters")
    os.makedirs(masters_dir, exist_ok=True)

    print("Phase 2: Building Merchandise Hierarchy Masters...")

    # 1. Macro Departments Mapping
    dept_mapping = {
        "DEP-FNB": ("Food & Beverage", [
            "BEVERAGES", "FOOD & BEVERAGE OUTLETS WITHIN THE COMPLEX", "SNACKS"
        ]),
        "DEP-GRO": ("Grocery & FMCG", [
            "GROCERY & FOOD STAPLES", "HOUSEHOLD CLEANING", 
            "PAPER, DISPOSABLE & CONSUMABLE HOUSEHOLD GOODS"
        ]),
        "DEP-FRE": ("Fresh Produce & Perishables", [
            "FRESH PRODUCE", "MEAT, SEAFOOD & PROTEIN", "DAIRY & REFRIGERATED PRODUCTS",
            "BAKERY & CONFECTIONERY", "FROZEN & READY-TO-EAT"
        ]),
        "DEP-APP": ("Apparel & Fashion", [
            "APPAREL — MEN", "APPAREL — WOMEN", "APPAREL — CHILDREN", "FOOTWEAR",
            "FASHION ACCESSORIES", "JEWELLERY", "WATCHES & TIMEPIECES"
        ]),
        "DEP-ELE": ("Electronics & Computing", [
            "CONSUMER ELECTRONICS", "COMPUTING & MOBILE", "SMART HOME & CONNECTED DEVICES",
            "ELECTRICAL & LIGHTING", "HOME APPLIANCES"
        ]),
        "DEP-HOM": ("Home & Living", [
            "FURNITURE", "HOME FURNISHINGS & DECOR", "KITCHEN & DINING",
            "GARDEN & OUTDOOR LIVING", "SLEEP & WELLNESS LIFESTYLE"
        ]),
        "DEP-HEA": ("Health, Beauty & Personal Care", [
            "BEAUTY & COSMETICS", "PERSONAL CARE", "HEALTH, WELLNESS & PHARMACY",
            "BABY & MATERNITY"
        ]),
        "DEP-TOY": ("Kids, Toys & Entertainment", [
            "TOYS", "GAMES & PUZZLES", "ENTERTAINMENT & MEDIA", "BOOKS",
            "STATIONERY & OFFICE SUPPLIES"
        ]),
        "DEP-SPO": ("Sports, Hobbies & Lifestyle", [
            "SPORTS & FITNESS", "HOBBIES, ARTS & CRAFTS", "ART & DECORATIVE GOODS",
            "MUSICAL INSTRUMENTS", "SEWING, TEXTILE & CRAFT SUPPLIES", "BICYCLES & PERSONAL MOBILITY"
        ]),
        "DEP-HAR": ("Hardware, Auto & Industrial", [
            "HARDWARE & HOME IMPROVEMENT", "AUTOMOTIVE", "PLUMBING & BUILDING SUPPLIES",
            "SOLAR & SUSTAINABILITY PRODUCTS", "SAFETY & SECURITY", "PAINTING & DECORATION MATERIALS"
        ]),
        "DEP-LIF": ("Gifts, Lifestyle & Cultural", [
            "GIFTS & LIFESTYLE", "PARTY & CELEBRATION", "FESTIVAL & SEASONAL",
            "RELIGIOUS & CULTURAL PRODUCTS", "COLLECTIBLES & SPECIALTY MERCHANDISE",
            "FLOWERS & FLORAL PRODUCTS", "PETS & PET SUPPLIES", "BAGS & LUGGAGE",
            "TRAVEL PRODUCTS", "PREMIUM & LUXURY GOODS"
        ]),
        "DEP-SER": ("Services & Specialty", [
            "SERVICES SOLD THROUGH THE RETAIL COMPLEX", "ENTERTAINMENT  EXPERIENCE BUSINESSES",
            "DIGITAL  NON-PHYSICAL RETAIL ITEMS", "OFFICE & BUSINESS CONSUMABLES",
            "PACKAGING & SHIPPING SUPPLIES", "SPECIALIZED ACCESSIBILITY  ASSISTIVE GOODS",
            "SPECIALTY PROFESSIONAL  LIGHT-COMMERCIAL GOODS", "REGULATED  CONTROLLED MERCHANDISE"
        ])
    }

    # Department Master DataFrame
    dept_rows = [{"DEPARTMENT_ID": d_id, "DEPARTMENT_NAME": d_info[0]} for d_id, d_info in dept_mapping.items()]
    df_dept = pd.DataFrame(dept_rows)
    df_dept.to_csv(os.path.join(masters_dir, "department_master.csv"), index=False)
    print(f"Created department_master.csv ({len(df_dept)} departments).")

    # Map filename prefix/base to Department ID
    file_to_dept = {}
    for d_id, (_, file_patterns) in dept_mapping.items():
        for pat in file_patterns:
            file_to_dept[pat] = d_id

    # 2. Parse all 67 category CSVs
    all_files = glob.glob(os.path.join(datasets_dir, "*.csv"))
    product_files = []
    excluded = {
        'categories.csv', 'locations.csv', 'suppliers.csv', 'inventory_state.csv',
        'supplier_product_edges.csv', 'purchase_orders.csv', 'customers.csv',
        'promotions.csv', 'india_retail_seasonality_event_master_2026.csv',
        'weekly_demand_history.csv', 'comprehensive_calendar_events.csv'
    }

    for f in all_files:
        basename = os.path.basename(f)
        if basename not in excluded:
            product_files.append(f)

    print(f"Found {len(product_files)} category files to process.")

    # Data structures for masters
    categories = {}      # cat_name -> CATEGORY_ID
    subcategories = {}   # (cat_id, subcat_name) -> SUBCATEGORY_ID
    families = {}        # (subcat_id, family_name) -> FAMILY_ID
    products = {}        # (family_id, prod_name) -> PRODUCT_ID
    
    sku_master_rows = []
    product_master_rows = []

    # Category margins and parameters by department
    dept_params = {
        "DEP-FNB": {"margin": 0.25, "perish": "MEDIUM", "shelf_days": 180, "season": "SUMMER_PEAK", "weather": "HIGH", "fest": "HIGH", "promo": "HIGH", "elas": -1.5},
        "DEP-GRO": {"margin": 0.18, "perish": "LOW", "shelf_days": 365, "season": "YEAR_ROUND", "weather": "LOW", "fest": "MEDIUM", "promo": "HIGH", "elas": -0.9},
        "DEP-FRE": {"margin": 0.30, "perish": "HIGH", "shelf_days": 10, "season": "SUMMER_PEAK", "weather": "HIGH", "fest": "HIGH", "promo": "MEDIUM", "elas": -1.2},
        "DEP-APP": {"margin": 0.55, "perish": "NON_PERISHABLE", "shelf_days": 730, "season": "FESTIVAL_PEAK", "weather": "MEDIUM", "fest": "HIGH", "promo": "HIGH", "elas": -1.8},
        "DEP-ELE": {"margin": 0.15, "perish": "NON_PERISHABLE", "shelf_days": 1095, "season": "FESTIVAL_PEAK", "weather": "LOW", "fest": "HIGH", "promo": "HIGH", "elas": -1.4},
        "DEP-HOM": {"margin": 0.40, "perish": "NON_PERISHABLE", "shelf_days": 1825, "season": "FESTIVAL_PEAK", "weather": "LOW", "fest": "HIGH", "promo": "MEDIUM", "elas": -1.1},
        "DEP-HEA": {"margin": 0.35, "perish": "LOW", "shelf_days": 540, "season": "YEAR_ROUND", "weather": "MEDIUM", "fest": "HIGH", "promo": "HIGH", "elas": -1.3},
        "DEP-TOY": {"margin": 0.45, "perish": "NON_PERISHABLE", "shelf_days": 1095, "season": "BACK_TO_SCHOOL", "weather": "LOW", "fest": "HIGH", "promo": "HIGH", "elas": -1.6},
        "DEP-SPO": {"margin": 0.40, "perish": "NON_PERISHABLE", "shelf_days": 1095, "season": "YEAR_ROUND", "weather": "MEDIUM", "fest": "MEDIUM", "promo": "MEDIUM", "elas": -1.2},
        "DEP-HAR": {"margin": 0.30, "perish": "NON_PERISHABLE", "shelf_days": 1825, "season": "YEAR_ROUND", "weather": "MEDIUM", "fest": "LOW", "promo": "LOW", "elas": -0.8},
        "DEP-LIF": {"margin": 0.50, "perish": "NON_PERISHABLE", "shelf_days": 730, "season": "FESTIVAL_PEAK", "weather": "LOW", "fest": "HIGH", "promo": "HIGH", "elas": -1.7},
        "DEP-SER": {"margin": 0.50, "perish": "NON_PERISHABLE", "shelf_days": 365, "season": "YEAR_ROUND", "weather": "LOW", "fest": "MEDIUM", "promo": "MEDIUM", "elas": -1.0}
    }

    cat_counter = 1
    subcat_counter = 1
    fam_counter = 1
    prod_counter = 1

    np.random.seed(42)

    for file_path in product_files:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        # Match to Department
        dept_id = "DEP-SER" # default fallback
        for pat, d_id in file_to_dept.items():
            if pat in base_name:
                dept_id = d_id
                break

        params = dept_params.get(dept_id, dept_params["DEP-SER"])

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        if 'SKU' not in df.columns:
            continue

        # Determine Category Name
        section_name = str(df['Section'].iloc[0]).strip() if 'Section' in df.columns and len(df) > 0 else base_name
        if section_name not in categories:
            cat_id = f"CAT-{cat_counter:03d}"
            cat_counter += 1
            categories[section_name] = (cat_id, dept_id)
        else:
            cat_id, _ = categories[section_name]

        for _, row in df.iterrows():
            sku_id = str(row['SKU']).strip()
            subcat_name = str(row.get('Subsection', 'General')).strip()
            fam_name = str(row.get('Product', 'Standard Product')).strip()

            # Subcategory
            subcat_key = (cat_id, subcat_name)
            if subcat_key not in subcategories:
                subcat_id = f"SUBCAT-{subcat_counter:04d}"
                subcat_counter += 1
                subcategories[subcat_key] = subcat_id
            else:
                subcat_id = subcategories[subcat_key]

            # Product Family
            fam_key = (subcat_id, fam_name)
            if fam_key not in families:
                fam_id = f"FAM-{fam_counter:05d}"
                fam_counter += 1
                families[fam_key] = fam_id
            else:
                fam_id = families[fam_key]

            # Product (Logical product variant)
            brand = str(row.get('Brand/Designer', row.get('Brand/Manufacturer', row.get('Brand/Creator', 'Brand X')))).strip()
            manufacturer = str(row.get('Supplier/Distributor', 'Manufacturer Direct')).strip()
            ptype = str(row.get('Category/Genre', row.get('Style/Fit', row.get('Type/Form Factor', 'Standard')))).strip()
            prod_name = f"{fam_name} - {ptype}"

            prod_key = (fam_id, prod_name, brand)
            if prod_key not in products:
                prod_id = f"PRD-{prod_counter:05d}"
                prod_counter += 1
                products[prod_key] = prod_id
                product_master_rows.append({
                    "PRODUCT_ID": prod_id,
                    "FAMILY_ID": fam_id,
                    "PRODUCT_NAME": prod_name,
                    "BRAND_ID": brand,
                    "MANUFACTURER_ID": manufacturer,
                    "PRODUCT_TYPE": ptype
                })
            else:
                prod_id = products[prod_key]

            # SKU Attributes
            uom = "Units"
            pack_size = str(row.get('Pack Size/Weight', row.get('Pack Size/Volume', row.get('Size', row.get('Size/Format', 'Standard'))))).strip()
            if 'kg' in pack_size.lower() or 'g' in pack_size.lower(): uom = "Kg"
            elif 'ml' in pack_size.lower() or 'l' in pack_size.lower(): uom = "Liters"

            # Cost and Price
            cost = float(row.get('Unit_Cost', np.random.uniform(20.0, 500.0)))
            price = round(cost * (1.0 + params["margin"]), 2)
            cost = round(cost, 2)

            volatility = round(float(np.random.uniform(0.08, 0.32)), 3)
            reg_affinity = np.random.choice(["PAN_INDIA", "NORTH", "SOUTH", "EAST", "WEST"], p=[0.5, 0.15, 0.15, 0.1, 0.1])

            sku_master_rows.append({
                "SKU_ID": sku_id,
                "PRODUCT_ID": prod_id,
                "SKU_NAME": f"{brand} {fam_name} ({pack_size})",
                "BASE_UNIT_COST": cost,
                "BASE_RETAIL_PRICE": price,
                "UNIT_OF_MEASURE": uom,
                "PACK_SIZE": pack_size,
                "SHELF_LIFE_DAYS": int(params["shelf_days"]),
                "PERISHABILITY_TIER": params["perish"],
                "DEMAND_VOLATILITY": volatility,
                "SEASONALITY_PROFILE": params["season"],
                "WEATHER_SENSITIVITY": params["weather"],
                "FESTIVAL_AFFINITY": params["fest"],
                "PROMOTION_SENSITIVITY": params["promo"],
                "PRICE_ELASTICITY": params["elas"],
                "REGIONAL_AFFINITY": reg_affinity
            })

    # Save Category Master
    df_cat = pd.DataFrame([
        {"CATEGORY_ID": c_id, "DEPARTMENT_ID": d_id, "CATEGORY_NAME": c_name}
        for c_name, (c_id, d_id) in categories.items()
    ])
    df_cat.to_csv(os.path.join(masters_dir, "category_master.csv"), index=False)
    print(f"Created category_master.csv ({len(df_cat)} categories).")

    # Save Subcategory Master
    df_subcat = pd.DataFrame([
        {"SUBCATEGORY_ID": s_id, "CATEGORY_ID": c_id, "SUBCATEGORY_NAME": s_name}
        for (c_id, s_name), s_id in subcategories.items()
    ])
    df_subcat.to_csv(os.path.join(masters_dir, "subcategory_master.csv"), index=False)
    print(f"Created subcategory_master.csv ({len(df_subcat)} subcategories).")

    # Save Product Family Master
    df_fam = pd.DataFrame([
        {"FAMILY_ID": f_id, "SUBCATEGORY_ID": s_id, "FAMILY_NAME": f_name}
        for (s_id, f_name), f_id in families.items()
    ])
    df_fam.to_csv(os.path.join(masters_dir, "product_family_master.csv"), index=False)
    print(f"Created product_family_master.csv ({len(df_fam)} families).")

    # Save Product Master
    df_prod = pd.DataFrame(product_master_rows)
    df_prod.to_csv(os.path.join(masters_dir, "product_master.csv"), index=False)
    print(f"Created product_master.csv ({len(df_prod)} products).")

    # Save SKU Master
    df_sku = pd.DataFrame(sku_master_rows)
    df_sku.to_csv(os.path.join(masters_dir, "sku_master.csv"), index=False)
    print(f"Created sku_master.csv ({len(df_sku)} SKUs).")

if __name__ == "__main__":
    build_merchandise_masters()
