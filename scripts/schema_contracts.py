# Canonical Data Contracts for SCOF V2 Simulation Architecture
# Enforces ID-based relational integrity, uppercase snake_case naming, and strict column specifications.

SCHEMAS = {
    "department_master": {
        "primary_key": "DEPARTMENT_ID",
        "columns": ["DEPARTMENT_ID", "DEPARTMENT_NAME"],
        "types": {"DEPARTMENT_ID": "str", "DEPARTMENT_NAME": "str"}
    },
    "category_master": {
        "primary_key": "CATEGORY_ID",
        "foreign_keys": {"DEPARTMENT_ID": "department_master.DEPARTMENT_ID"},
        "columns": ["CATEGORY_ID", "DEPARTMENT_ID", "CATEGORY_NAME"],
        "types": {"CATEGORY_ID": "str", "DEPARTMENT_ID": "str", "CATEGORY_NAME": "str"}
    },
    "subcategory_master": {
        "primary_key": "SUBCATEGORY_ID",
        "foreign_keys": {"CATEGORY_ID": "category_master.CATEGORY_ID"},
        "columns": ["SUBCATEGORY_ID", "CATEGORY_ID", "SUBCATEGORY_NAME"],
        "types": {"SUBCATEGORY_ID": "str", "CATEGORY_ID": "str", "SUBCATEGORY_NAME": "str"}
    },
    "product_family_master": {
        "primary_key": "FAMILY_ID",
        "foreign_keys": {"SUBCATEGORY_ID": "subcategory_master.SUBCATEGORY_ID"},
        "columns": ["FAMILY_ID", "SUBCATEGORY_ID", "FAMILY_NAME"],
        "types": {"FAMILY_ID": "str", "SUBCATEGORY_ID": "str", "FAMILY_NAME": "str"}
    },
    "product_master": {
        "primary_key": "PRODUCT_ID",
        "foreign_keys": {"FAMILY_ID": "product_family_master.FAMILY_ID"},
        "columns": ["PRODUCT_ID", "FAMILY_ID", "PRODUCT_NAME", "BRAND_ID", "MANUFACTURER_ID", "PRODUCT_TYPE"],
        "types": {
            "PRODUCT_ID": "str", "FAMILY_ID": "str", "PRODUCT_NAME": "str",
            "BRAND_ID": "str", "MANUFACTURER_ID": "str", "PRODUCT_TYPE": "str"
        }
    },
    "sku_master": {
        "primary_key": "SKU_ID",
        "foreign_keys": {"PRODUCT_ID": "product_master.PRODUCT_ID"},
        "columns": [
            "SKU_ID", "PRODUCT_ID", "SKU_NAME", "BASE_UNIT_COST", "BASE_RETAIL_PRICE",
            "UNIT_OF_MEASURE", "PACK_SIZE", "SHELF_LIFE_DAYS", "PERISHABILITY_TIER",
            "DEMAND_VOLATILITY", "SEASONALITY_PROFILE", "WEATHER_SENSITIVITY",
            "FESTIVAL_AFFINITY", "PROMOTION_SENSITIVITY", "PRICE_ELASTICITY", "REGIONAL_AFFINITY"
        ],
        "types": {
            "SKU_ID": "str", "PRODUCT_ID": "str", "SKU_NAME": "str",
            "BASE_UNIT_COST": "float", "BASE_RETAIL_PRICE": "float",
            "UNIT_OF_MEASURE": "str", "PACK_SIZE": "str", "SHELF_LIFE_DAYS": "int",
            "PERISHABILITY_TIER": "str", "DEMAND_VOLATILITY": "float",
            "SEASONALITY_PROFILE": "str", "WEATHER_SENSITIVITY": "str",
            "FESTIVAL_AFFINITY": "str", "PROMOTION_SENSITIVITY": "str",
            "PRICE_ELASTICITY": "float", "REGIONAL_AFFINITY": "str"
        }
    },
    "store_master": {
        "primary_key": "STORE_ID",
        "columns": [
            "STORE_ID", "STORE_NAME", "STORE_FORMAT", "REGION", "STATE", "CITY",
            "TIER", "PRIMARY_DC_ID", "MAX_SHELF_CAPACITY_UNITS"
        ],
        "types": {
            "STORE_ID": "str", "STORE_NAME": "str", "STORE_FORMAT": "str",
            "REGION": "str", "STATE": "str", "CITY": "str", "TIER": "str",
            "PRIMARY_DC_ID": "str", "MAX_SHELF_CAPACITY_UNITS": "int"
        }
    },
    "warehouse_master": {
        "primary_key": "WAREHOUSE_ID",
        "columns": [
            "WAREHOUSE_ID", "WAREHOUSE_NAME", "REGION", "STATE", "CITY",
            "TOTAL_CAPACITY_PALLETS", "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK"
        ],
        "types": {
            "WAREHOUSE_ID": "str", "WAREHOUSE_NAME": "str", "REGION": "str",
            "STATE": "str", "CITY": "str", "TOTAL_CAPACITY_PALLETS": "int",
            "INBOUND_THROUGHPUT_MAX_UNITS_PER_WEEK": "int"
        }
    },
    "store_warehouse_map": {
        "primary_key": ["STORE_ID", "WAREHOUSE_ID"],
        "foreign_keys": {
            "STORE_ID": "store_master.STORE_ID",
            "WAREHOUSE_ID": "warehouse_master.WAREHOUSE_ID"
        },
        "columns": ["STORE_ID", "WAREHOUSE_ID", "ROUTE_PRIORITY", "TRANSIT_TIME_DAYS"],
        "types": {
            "STORE_ID": "str", "WAREHOUSE_ID": "str",
            "ROUTE_PRIORITY": "str", "TRANSIT_TIME_DAYS": "int"
        }
    },
    "supplier_sku_map": {
        "primary_key": ["SUPPLIER_ID", "SKU_ID"],
        "foreign_keys": {
            "SUPPLIER_ID": "suppliers.Supplier_ID",
            "SKU_ID": "sku_master.SKU_ID"
        },
        "columns": [
            "SUPPLIER_ID", "SKU_ID", "SUPPLIER_SKU", "PURCHASE_COST", "MOQ_UNITS",
            "LEAD_TIME_DAYS", "ORDER_MULTIPLE", "PRIMARY_FLAG", "ACTIVE_FLAG"
        ],
        "types": {
            "SUPPLIER_ID": "str", "SKU_ID": "str", "SUPPLIER_SKU": "str",
            "PURCHASE_COST": "float", "MOQ_UNITS": "int", "LEAD_TIME_DAYS": "int",
            "ORDER_MULTIPLE": "int", "PRIMARY_FLAG": "int", "ACTIVE_FLAG": "int"
        }
    },
    "store_sku_assortment": {
        "primary_key": ["STORE_ID", "SKU_ID"],
        "foreign_keys": {
            "STORE_ID": "store_master.STORE_ID",
            "SKU_ID": "sku_master.SKU_ID"
        },
        "columns": [
            "STORE_ID", "SKU_ID", "ASSORTMENT_TIER", "ASSORTMENT_START_WEEK",
            "ASSORTMENT_END_WEEK", "ALLOCATED_SHELF_CAPACITY_UNITS"
        ],
        "types": {
            "STORE_ID": "str", "SKU_ID": "str", "ASSORTMENT_TIER": "str",
            "ASSORTMENT_START_WEEK": "int", "ASSORTMENT_END_WEEK": "int",
            "ALLOCATED_SHELF_CAPACITY_UNITS": "int"
        }
    },
    "replenishment_policy": {
        "primary_key": ["STORE_ID", "SKU_ID"],
        "foreign_keys": {
            "STORE_ID": "store_master.STORE_ID",
            "SKU_ID": "sku_master.SKU_ID"
        },
        "columns": [
            "STORE_ID", "SKU_ID", "REPLENISHMENT_METHOD", "REVIEW_PERIOD_WEEKS",
            "SAFETY_STOCK_WEEKS", "REORDER_POINT_UNITS", "TARGET_MAX_UNITS", "ORDER_QUANTITY_MULTIPLE"
        ],
        "types": {
            "STORE_ID": "str", "SKU_ID": "str", "REPLENISHMENT_METHOD": "str",
            "REVIEW_PERIOD_WEEKS": "int", "SAFETY_STOCK_WEEKS": "int",
            "REORDER_POINT_UNITS": "int", "TARGET_MAX_UNITS": "int",
            "ORDER_QUANTITY_MULTIPLE": "int"
        }
    },
    "weather_weekly": {
        "primary_key": ["WEEK", "REGION"],
        "columns": [
            "WEEK", "REGION", "AVG_TEMPERATURE_C", "TEMP_ANOMALY_C", "RAINFALL_MM",
            "RAINFALL_ANOMALY_MM", "HUMIDITY_PCT", "HEAT_INDEX", "EXTREME_WEATHER_FLAG",
            "DERIVED_REGIME"
        ],
        "types": {
            "WEEK": "int", "REGION": "str", "AVG_TEMPERATURE_C": "float",
            "TEMP_ANOMALY_C": "float", "RAINFALL_MM": "float", "RAINFALL_ANOMALY_MM": "float",
            "HUMIDITY_PCT": "float", "HEAT_INDEX": "float", "EXTREME_WEATHER_FLAG": "int",
            "DERIVED_REGIME": "str"
        }
    },
    "price_history": {
        "primary_key": ["WEEK", "SKU_ID"],
        "foreign_keys": {"SKU_ID": "sku_master.SKU_ID"},
        "columns": [
            "WEEK", "SKU_ID", "BASE_PRICE", "SELLING_PRICE", "DISCOUNT_PCT",
            "PRICE_INDEX", "PRICE_CHANGE_REASON"
        ],
        "types": {
            "WEEK": "int", "SKU_ID": "str", "BASE_PRICE": "float",
            "SELLING_PRICE": "float", "DISCOUNT_PCT": "float",
            "PRICE_INDEX": "float", "PRICE_CHANGE_REASON": "str"
        }
    },
    "promotions": {
        "primary_key": "PROMO_ID",
        "columns": [
            "PROMO_ID", "TARGET_LEVEL", "TARGET_ID", "CAMPAIGN_NAME",
            "START_WEEK", "PEAK_WEEK", "END_WEEK", "DISCOUNT_PCT",
            "PROMOTION_TYPE", "PROMOTION_INTENSITY", "CHANNEL", "REGION"
        ],
        "types": {
            "PROMO_ID": "str", "TARGET_LEVEL": "str", "TARGET_ID": "str",
            "CAMPAIGN_NAME": "str", "START_WEEK": "int", "PEAK_WEEK": "int",
            "END_WEEK": "int", "DISCOUNT_PCT": "float", "PROMOTION_TYPE": "str",
            "PROMOTION_INTENSITY": "str", "CHANNEL": "str", "REGION": "str"
        }
    },
    "event_master": {
        "primary_key": "EVENT_ID",
        "columns": [
            "EVENT_ID", "EVENT_NAME", "EVENT_TYPE", "SUB_TYPE", "REGION",
            "CALENDAR_ANCHOR", "ANNUAL_WEEK_PEAK", "TYPICAL_START_WEEK", "TYPICAL_END_WEEK",
            "LEAD_TIME_WEEKS", "DECAY_WEEKS", "CATEGORY_IMPACT_KEYWORDS", "IMPACT_PROFILE",
            "DEMAND_MULTIPLIER", "WEATHER_SENSITIVITY", "GEOGRAPHY_WEIGHT", "RECURRENCE_TYPE",
            "SOURCE_URL", "NOTES"
        ]
    },
    "event_impact_matrix": {
        "primary_key": ["EVENT_ID", "TARGET_LEVEL", "TARGET_ID"],
        "foreign_keys": {"EVENT_ID": "event_master.EVENT_ID"},
        "columns": [
            "EVENT_ID", "TARGET_LEVEL", "TARGET_ID", "IMPACT_DIRECTION",
            "DEMAND_MULTIPLIER", "IMPACT_STRENGTH", "APPLY_MODE"
        ],
        "types": {
            "EVENT_ID": "str", "TARGET_LEVEL": "str", "TARGET_ID": "str",
            "IMPACT_DIRECTION": "str", "DEMAND_MULTIPLIER": "float",
            "IMPACT_STRENGTH": "str", "APPLY_MODE": "str"
        }
    },
    "event_interactions": {
        "primary_key": ["EVENT_ID_1", "EVENT_ID_2"],
        "foreign_keys": {
            "EVENT_ID_1": "event_master.EVENT_ID",
            "EVENT_ID_2": "event_master.EVENT_ID"
        },
        "columns": ["EVENT_ID_1", "EVENT_ID_2", "INTERACTION_TYPE", "INTERACTION_CAP", "DESCRIPTION"],
        "types": {
            "EVENT_ID_1": "str", "EVENT_ID_2": "str",
            "INTERACTION_TYPE": "str", "INTERACTION_CAP": "float", "DESCRIPTION": "str"
        }
    },
    "regional_event_weights": {
        "primary_key": ["EVENT_ID", "GEOGRAPHIC_LEVEL", "GEOGRAPHIC_TARGET"],
        "foreign_keys": {"EVENT_ID": "event_master.EVENT_ID"},
        "columns": ["EVENT_ID", "GEOGRAPHIC_LEVEL", "GEOGRAPHIC_TARGET", "GEOGRAPHIC_WEIGHT"],
        "types": {
            "EVENT_ID": "str", "GEOGRAPHIC_LEVEL": "str",
            "GEOGRAPHIC_TARGET": "str", "GEOGRAPHIC_WEIGHT": "float"
        }
    }
}
