from .indicators import CLIMATE_INDICATORS, PRICE_INDICATORS


# ==========================================================
# DEFAULT METHODS
# ==========================================================

DEFAULT_THRESHOLD_METHOD = "percentile"

DEFAULT_BASELINE = "LTM"

BASELINE_METHODS = [
    "LTM",
    "YOY",
    "FIVE_YEAR"
]


# ==========================================================
# INDICATOR → METHOD
# ==========================================================

INDICATOR_METHOD = {

    # Climate indicators
    "rainfall 1-month anomaly [%]": "tukey",
    "rainfall 3-month anomaly [%]": "tukey",
    "10 day NDVI anomaly": "tukey",

    "rainfall-mm": "spi_true",
    "ndvi_absolute": "zscore_true",

    # Afghanistan
    "Bread": "percentile",
    "Exchange rate": "percentile",
    "Fuel (diesel)": "percentile",
    "Oil (cooking)": "percentile",
    "Pulses": "percentile",
    "Rice (high quality)": "percentile",
    "Rice (low quality)": "percentile",
    "Sugar": "percentile",
    "Wage (non-qualified labour, non-agricultural)": "percentile",
    "Wheat": "percentile",
    "Wheat flour (high quality)": "percentile",
    "Wheat flour (low quality)": "percentile",
    "ToT (Labour/Cereal)": "percentile",
    "ToT (Goat/Cereal)": "percentile",

    # Kenya
    "Goat": "percentile",
    "Maize": "percentile",
    "Beans": "percentile",
    "ToT": "percentile",

    # South Sudan
    "Fuel (diesel, parallel market)": "percentile",
    "Fuel (petrol-gasoline, parallel market)": "percentile",
    "Sorghum (local)": "percentile",
    "Sorghum (red, local)": "percentile",
    "Sorghum flour": "percentile",
    "Oil (vegetable, fortified, food aid)": "percentile",
    "Beans (fava, dry)": "percentile",
    "Cowpeas": "percentile",
    "Wage (non-qualified labour, agricultural)": "percentile",
    "Sorghum (brown)": "percentile",
    "Rice": "percentile",

    # Shock indicators
    "conflict_events": "categorical",
    "conflict_fatalities": "categorical",

    # Flood
    "percent_area_flooded": "percentile"
}


# ==========================================================
# METHOD VALUE COLUMN
# ==========================================================

METHOD_VALUE_COLUMN = {
    "percentile": "value",
    "tukey": "value",
    "spi_true": "value",
    "zscore_true": "value_zscore",
    "categorical": "value",
    "hybrid": "value"
}


# ==========================================================
# ALLOWED BASELINES
# ==========================================================

INDICATOR_ALLOWED_BASELINES = {

    # Climate
    "rainfall 1-month anomaly [%]": ["none"],
    "rainfall 3-month anomaly [%]": ["none"],
    "10 day NDVI anomaly": ["none"],
    "rainfall-mm": ["none"],
    "ndvi_absolute": ["none"],

    # Prices
    **{
        ind: ["YOY", "LTM", "FIVE_YEAR"]
        for ind in PRICE_INDICATORS
    },

    # Conflict
    "conflict_events": ["none"],
    "conflict_fatalities": ["none"],

    # Flood
    "percent_area_flooded": ["none"]
}


# ==========================================================
# ALLOWED THRESHOLD METHODS
# ==========================================================

INDICATOR_ALLOWED_METHODS = {}

# Climate
for ind in CLIMATE_INDICATORS:
    INDICATOR_ALLOWED_METHODS[ind] = [
        "tukey",
        "percentile"
    ]

# Prices
for ind in PRICE_INDICATORS:
    INDICATOR_ALLOWED_METHODS[ind] = [
        "percentile",
        "tukey",
        "zscore_true"
    ]

# Conflict
INDICATOR_ALLOWED_METHODS["conflict_events"] = [
    "categorical",
    "hybrid",
    "percentile"
]

INDICATOR_ALLOWED_METHODS["conflict_fatalities"] = [
    "categorical",
    "hybrid",
    "percentile"
]

# Flood
INDICATOR_ALLOWED_METHODS["percent_area_flooded"] = [
    "percentile"
]

# Overrides
INDICATOR_ALLOWED_METHODS["ndvi_absolute"] = [
    "zscore_true"
]

INDICATOR_ALLOWED_METHODS["rainfall-mm"] = [
    "spi_true"
]


# ==========================================================
# TRUE Z-SCORE CONFIG
# ==========================================================

Z_SCORE_TRUE_METHOD = "zscore_true"

ZSCORE_TRUE_GROUP = {

    "ndvi_absolute": "climate",

    **{
        ind: "price"
        for ind in PRICE_INDICATORS
    }
}

ZSCORE_TRUE_REQUIRES_ANOMALY = {
    "price": True,
    "climate": False
}

ZSCORE_TRUE_INDICATORS = [
    "ndvi_absolute",
    *PRICE_INDICATORS
]


# ==========================================================
# SPI CONFIG
# ==========================================================

SPI_TRUE_INDICATORS = [
    "rainfall-mm"
]

SPI_SIGNAL_TYPE = {
    "rainfall-mm": "both",
    "ndvi_absolute": "both"
}


# ==========================================================
# SEASONAL STANDARDIZATION
# ==========================================================

SEASONAL_STANDARDIZATION_METHODS = [
    "spi_true",
    "zscore_true"
]


# ==========================================================
# MONTHLY AGGREGATION RULES
# ==========================================================

Z_AGGREGATION_METHOD = {

    # Climate
    "rainfall 1-month anomaly [%]": "mean",
    "rainfall 3-month anomaly [%]": "mean",
    "10 day NDVI anomaly": "mean",
    "rainfall-mm": "mean",
    "ndvi_absolute": "mean",

    # Prices
    **{
        ind: "mean"
        for ind in PRICE_INDICATORS
    },

    # Conflict
    "conflict_events": "sum",
    "conflict_fatalities": "sum"
}