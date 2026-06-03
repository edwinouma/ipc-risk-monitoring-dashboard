# ==========================================================
# EVENT / CATEGORICAL THRESHOLDS
# ==========================================================

EVENT_THRESHOLDS = {

    "conflict_events": {
        "alert": 5,
        "alarm": 10
    },

    "conflict_fatalities": {
        "alert": 5,
        "alarm": 20
    }
}


# ==========================================================
# HYBRID CONFLICT THRESHOLDS
# ==========================================================

CONFLICT_HYBRID_THRESHOLDS = {

    "conflict_events": {
        "alert": 5,
        "alarm": 10
    },

    "conflict_fatalities": {
        "alert": 5,
        "alarm": 20
    }
}


# ==========================================================
# CONFLICT TREND ESCALATION RULES
# ==========================================================

CONFLICT_TREND_RULES = {

    "yoy_abs": {
        "alert": 2,
        "alarm": 3
    },

    "yoy_ratio": {
        "alert": 1.5,
        "alarm": 2.0
    }
}


# ==========================================================
# CONFLICT ANOMALY RULES
# ==========================================================

CONFLICT_ANOMALY_RULES = {

    "anomaly_abs": {
        "alert": 2,
        "alarm": 5
    },

    "anomaly_ratio": {
        "alert": 1.5,
        "alarm": 2.0
    }
}


# ==========================================================
# GENERIC Z-SCORE THRESHOLDS
# ==========================================================

ZSCORE_THRESHOLDS = {

    "default": {
        "alert": 1.0,
        "alarm": 2.0
    }
}


# ==========================================================
# SPI DROUGHT THRESHOLDS
# ==========================================================

SPI_TRUE_THRESHOLDS = {

    "default": {
        "alert": -1.0,
        "alarm": -2.0
    },

    "rainfall-mm": {
        "alert": -1.0,
        "alarm": -2.0
    },

    "ndvi_absolute": {
        "alert": -1.0,
        "alarm": -2.0
    }
}


# ==========================================================
# SPI FLOOD THRESHOLDS
# ==========================================================

SPI_TRUE_FLOOD_THRESHOLDS = {

    "default": {
        "alert": 1.0,
        "alarm": 2.0
    },

    "rainfall-mm": {
        "alert": 1.0,
        "alarm": 2.0
    },

    "ndvi_absolute": {
        "alert": 1.0,
        "alarm": 2.0
    }
}


# ==========================================================
# TRUE Z-SCORE THRESHOLDS
# ==========================================================

ZSCORE_TRUE_THRESHOLDS = {

    "default": {
        "alert": -1.0,
        "alarm": -2.0
    },

    # Climate indicators
    "ndvi_absolute": {
        "alert": -1.0,
        "alarm": -2.0
    },

    # Price indicators
    "price_default": {
        "alert": 1.0,
        "alarm": 2.0
    }
}


# ==========================================================
# FUTURE COUNTRY-SPECIFIC THRESHOLDS
# ==========================================================
#
# Reserved for future implementation.
#
# Example:
#
# COUNTRY_THRESHOLDS = {
#
#     "Kenya": {
#         "conflict_events": {
#             "alert": 3,
#             "alarm": 7
#         }
#     },
#
#     "South Sudan": {
#         "conflict_events": {
#             "alert": 10,
#             "alarm": 25
#         }
#     }
# }
#
# ==========================================================

COUNTRY_THRESHOLDS = {}