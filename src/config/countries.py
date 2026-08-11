# ==========================================================
# COUNTRY CONFIGURATION
# ==========================================================

COUNTRY_CONFIG = {

    "Afghanistan": {
        "unit_col": "adm1_name",
        "price_file": "data/price_data.xlsx",
        "rainfall_file": "data/rainfall_ndvi_afghanistan.xlsx",
        "conflict_file": "data/acled_afghanistan.xlsx",
        "flood_file": "data/flood_afghanistan.xlsx",
    },

    "South Sudan": {
        "unit_col": "adm1_name",
        "price_file": "data/price_data_south sudan.xlsx",
        "rainfall_file": "data/rainfall_ndvi_South Sudan.xlsx",
        "conflict_file": "data/acled_south_sudan.xlsx",
        "flood_file": "data/flood_south_sudan.xlsx",
        "ipc_file": "data/ipc_south_sudan.xlsx",
    },

    "Kenya": {
        "unit_col": "adm1_name",
        "price_file": "data/price_data_kenya.xlsx",
        "rainfall_file": "data/rainfall_ndvi_kenya.xlsx",
        "conflict_file": "data/acled_kenya.xlsx",
        "morbidity_file": "data/morbidity_long_kenya.xlsx",
    }
}


# ==========================================================
# COUNTRY → INDICATORS
# (MASTER REGISTRY)
# ==========================================================

COUNTRY_INDICATORS = {

    "Afghanistan": [

        # Climate
        "rainfall 1-month anomaly [%]",
        "rainfall 3-month anomaly [%]",
        "10 day NDVI anomaly",
        "rainfall-mm",
        "ndvi_absolute",

        # Markets
        "Bread",
        "Exchange rate",
        "Fuel (diesel)",
        "Oil (cooking)",
        "Pulses",
        "Rice (high quality)",
        "Rice (low quality)",
        "Sugar",
        "Wage (non-qualified labour, non-agricultural)",
        "Wheat",
        "Wheat flour (high quality)",
        "Wheat flour (low quality)",
        "ToT (Labour/Cereal)",

        # Flood
        "percent_area_flooded"
    ],

    "Kenya": [

        # Climate
        "rainfall 1-month anomaly [%]",
        "rainfall 3-month anomaly [%]",
        "10 day NDVI anomaly",
        "rainfall-mm",
        "ndvi_absolute",

        # Markets
        "Goat",
        "Maize",
        "Beans",
        "ToT"
    ],

    "South Sudan": [

        # Climate
        "rainfall 1-month anomaly [%]",
        "rainfall 3-month anomaly [%]",
        "10 day NDVI anomaly",
        "rainfall-mm",
        "ndvi_absolute",

        # Markets
        "Exchange rate",
        "Fuel (diesel)",
        "Wage (non-qualified labour, non-agricultural)",

        "Fuel (diesel, parallel market)",
        "Fuel (petrol-gasoline, parallel market)",
        "Sorghum (local)",
        "Sorghum (red, local)",
        "Sorghum flour",
        "Oil (vegetable, fortified, food aid)",
        "Beans (fava, dry)",
        "Cowpeas",
        "Wage (non-qualified labour, agricultural)",
        "Sorghum (brown)",
        "Rice",

        # Conflict
        "conflict_events",
        "conflict_fatalities",

        # Flood
        "percent_area_flooded"
    ]
}


# ==========================================================
# AUTO-GENERATED INDICATOR → COUNTRY MAP
# ==========================================================

INDICATOR_COUNTRY_MAP = {}

for country, indicators in COUNTRY_INDICATORS.items():
    for indicator in indicators:
        INDICATOR_COUNTRY_MAP.setdefault(indicator, []).append(country)


# ==========================================================
# TERMS OF TRADE CONFIGURATION
# ==========================================================

TOT_CONFIG = {

    "Afghanistan": {
        "enabled": True,
        "definitions": [
            {
                "name": "ToT (Labour/Cereal)",
                "numerator": "Wage (non-qualified labour, non-agricultural)",
                "denominator": "Wheat"
            },
            {
                "name": "ToT (Goat/Cereal)",
                "numerator": "Goat",
                "denominator": "Wheat"
            }
        ]
    },

    "Kenya": {
        "enabled": False
    },

    "South Sudan": {
        "enabled": False
    }
}


# ==========================================================
# DERIVED INDICATORS
# ==========================================================

DERIVED_INDICATORS = [
    "ToT (Labour/Cereal)",
    "ToT (Goat/Cereal)"
]