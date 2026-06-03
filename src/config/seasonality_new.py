from .indicators import (
    PRICE_INDICATORS,
    SHOCK_INDICATORS
)

# ==========================================================
# COUNTRY SEASON DEFINITIONS
# ==========================================================

COUNTRY_SEASONS = {

    "Afghanistan": {

        "Rainfall": {
            "All Months": None,
            "Planting (Mar–Jun)": [3,4,5,6],
            "Off-Season (Jul–Feb)": [7,8,9,10,11,12,1,2]
        },

        "NDVI": {
            "All Months": None,
            "Growing (Apr–Jul)": [4,5,6,7],
            "Dormant (Aug–Mar)": [8,9,10,11,12,1,2,3]
        }
    },

    "Kenya": {

        "Rainfall": {
            "All Months": None,
            "Long Rains (Mar–May)": [3,4,5],
            "Short Rains (Oct–Dec)": [10,11,12]
        },

        "NDVI": {
            "All Months": None,
            "Long Rains (Mar–May)": [3,4,5],
            "Short Rains (Oct–Dec)": [10,11,12]
        }
    },

    "South Sudan": {

        "Rainfall": {
            "All Months": None,
            "Main Rainy Season (Apr–Oct)": [4,5,6,7,8,9,10],
            "Dry Season (Nov–Mar)": [11,12,1,2,3]
        },

        "NDVI": {
            "All Months": None,
            "Growing Season (May–Sep)": [5,6,7,8,9],
            "Dry Season (Oct–Apr)": [10,11,12,1,2,3,4]
        }
    }
}


# ==========================================================
# INDICATOR → SEASON TYPE
# ==========================================================

INDICATOR_SEASON_TYPE = {

    "rainfall 1-month anomaly [%]": "Rainfall",
    "rainfall 3-month anomaly [%]": "Rainfall",

    "10 day NDVI anomaly": "NDVI",

    "rainfall-mm": "All Months",
    "ndvi_absolute": "All Months",

    "percent_area_flooded": "All Months"
}


# ==========================================================
# AUTO-ASSIGN PRICES
# ==========================================================

for indicator in PRICE_INDICATORS:
    INDICATOR_SEASON_TYPE[indicator] = "All Months"


# ==========================================================
# AUTO-ASSIGN SHOCKS
# ==========================================================

for indicator in SHOCK_INDICATORS:
    INDICATOR_SEASON_TYPE[indicator] = "All Months"