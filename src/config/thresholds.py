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

    # ------------------------------------------------------
    # Default
    # Lower-tail deterioration
    # ------------------------------------------------------

    "default": {
        "alert": -1.0,
        "alarm": -2.0
    },

    # ------------------------------------------------------
    # Climate
    # Lower values indicate deterioration
    # ------------------------------------------------------

    "ndvi_absolute": {
        "alert": -1.0,
        "alarm": -2.0
    },

    # ------------------------------------------------------
    # Prices
    # Upper values generally indicate deterioration
    # ------------------------------------------------------

    "price_default": {
        "alert": 1.0,
        "alarm": 2.0
    },

    # ------------------------------------------------------
    # Morbidity
    #
    # Seasonal Z-score applied directly to monthly
    # reported/admission case counts.
    #
    # Alert:
    # Cases >= 1 SD above the historical mean for the
    # same calendar month.
    #
    # Alarm:
    # Cases >= 2 SD above the historical mean for the
    # same calendar month.
    # ------------------------------------------------------

    "Malaria": {
        "alert": 1.0,
        "alarm": 2.0
    },

    "URTI": {
        "alert": 1.0,
        "alarm": 2.0
    },

    "Diarrhoea": {
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
        "alert": 70,
        "alarm": 10
    },

    "default_upper": {
        "alert": 50,
        "alarm": 90
    },

    # --------------------------------------------------
    # CLIMATE
    # --------------------------------------------------

    "rainfall 1-month anomaly [%]": {
        "alert": 50,
        "alarm": 10
    },

    "rainfall 3-month anomaly [%]": {
        "alert": 50,
        "alarm": 10
    },

    "10 day NDVI anomaly": {
        "alert": 50,
        "alarm": 10
    },

    # --------------------------------------------------
    # PRICES
    # --------------------------------------------------

    "Maize": {
        "alert": 50,
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

# ==========================================================
# ALPS THRESHOLDS
# ==========================================================

ALPS_THRESHOLDS = {

    "default": {

        "alert": 1.0,

        "alarm": 2.0

    }

}


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

# ==========================================================
# VCI THRESHOLDS
# ==========================================================

VCI_THRESHOLDS = {

    "default": {

        "alert": 35,

        "alarm": 20

    },

    "ndvi_absolute": {

        "alert": 35,

        "alarm": 20

    }

}