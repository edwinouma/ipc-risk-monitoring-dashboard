from .indicators import (
    PRICE_INDICATORS,
    SHOCK_INDICATORS
)

# ==========================================================
# COMMON SEASON DEFINITIONS
# ==========================================================

RAINFALL_SEASONS = {
    "All Months": None,
    "Planting (Mar–Jun)": [3, 4, 5, 6],
    "Off-Season (Jul–Feb)": [7, 8, 9, 10, 11, 12, 1, 2]
}

NDVI_SEASONS = {
    "All Months": None,
    "Growing (Apr–Jul)": [4, 5, 6, 7],
    "Dormant (Aug–Mar)": [8, 9, 10, 11, 12, 1, 2, 3]
}

ALL_MONTHS_ONLY = {
    "All Months": None
}

# ==========================================================
# SEASONAL DEFINITIONS
# ==========================================================

SEASONAL_DEFINITIONS = {

    "rainfall 1-month anomaly [%]": RAINFALL_SEASONS,

    "rainfall 3-month anomaly [%]": RAINFALL_SEASONS,

    "10 day NDVI anomaly": NDVI_SEASONS,
}

# ==========================================================
# AUTO-ASSIGN ALL-MONTHS INDICATORS
# ==========================================================

for indicator in PRICE_INDICATORS:
    SEASONAL_DEFINITIONS[indicator] = ALL_MONTHS_ONLY

for indicator in SHOCK_INDICATORS:
    SEASONAL_DEFINITIONS[indicator] = ALL_MONTHS_ONLY

# ==========================================================
# SPECIAL INDICATORS
# ==========================================================

SEASONAL_DEFINITIONS["percent_area_flooded"] = ALL_MONTHS_ONLY

SEASONAL_DEFINITIONS["rainfall-mm"] = ALL_MONTHS_ONLY

SEASONAL_DEFINITIONS["ndvi_absolute"] = ALL_MONTHS_ONLY

# ==========================================================
# COUNTRY-SPECIFIC SEASONS
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
            "Long Rains (Mar-May)": [3,4,5],
            "Short Rains (Oct-Dec)": [10,11,12]
        }
    },

    "South Sudan": {

        "Rainfall": {
            "All Months": None,
            "Main Rainy Season (May–Oct)": [5,6,7,8,9,10],
            "Dry Season (Nov–Apr)": [11,12,1,2,3,4]
        },

        "NDVI": {
            "All Months": None,
            "Main Growing Season (May–Oct)": [5,6,7,8,9,10],
            "Dry Season (Nov–Apr)": [11,12,1,2,3,4]
        }
    }
}