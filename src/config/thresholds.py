# ==========================================================
# EVENT / CATEGORICAL THRESHOLDS
# ==========================================================

EVENT_THRESHOLDS = {

    "conflict_events": {
        "alert": 3,
        "alarm": 5
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
        "alert": 3,
        "alarm": 5
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
# INDICATOR-SPECIFIC PERCENTILE CONFIGURATION
# ==========================================================
#
# Used by percentile-based methods.
#
# Lower-direction indicators:
#   Alert = less severe percentile
#   Alarm = more severe percentile
#
# Upper-direction indicators:
#   Alert = lower upper-tail percentile
#   Alarm = higher upper-tail percentile
#
# Examples:
#
# Lower direction:
#   Alert = P50
#   Alarm = P25
#
# Upper direction:
#   Alert = P50
#   Alarm = P75
#
# ==========================================================

INDICATOR_PERCENTILES = {

    # --------------------------------------------------
    # DEFAULTS
    # --------------------------------------------------

    "default_lower": {
        "alert": 50,
        "alarm": 25
    },

    "default_upper": {
        "alert": 50,
        "alarm": 75
    },

    # --------------------------------------------------
    # CLIMATE
    # --------------------------------------------------

    "rainfall 1-month anomaly [%]": {
        "alert": 50,
        "alarm": 25
    },

    "rainfall 3-month anomaly [%]": {
        "alert": 50,
        "alarm": 25
    },

    "10 day NDVI anomaly": {
        "alert": 50,
        "alarm": 25
    },

    # --------------------------------------------------
    # PRICES
    # --------------------------------------------------

    "Maize": {
        "alert": 70,
        "alarm": 90
    }

    #
    # Other price indicators currently inherit
    # default_upper.
    #
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

COUNTRY_THRESHOLDS = {

    "South Sudan": {

        "conflict_events": {
            "alert": 3,
            "alarm": 5
        },

        "conflict_fatalities": {
            "alert": 5,
            "alarm": 20
        }
    },

    "Kenya": {

        "conflict_events": {
            "alert": 3,
            "alarm": 5
        }
    }
}