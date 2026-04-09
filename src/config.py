DEFAULT_THRESHOLD_METHOD = "percentile"
# ---------------------------------------------------
# Indicator Groups
# ---------------------------------------------------

CLIMATE_INDICATORS = [
    "rainfall 1-month anomaly [%]",
    "rainfall 3-month anomaly [%]",
    "10 day NDVI anomaly",
    "rainfall-mm",
    "ndvi_absolute"
]

PRICE_INDICATORS = [
    # Afghanistan commodities
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

    # Kenya commodities
    "Goat",
    "Maize",
    "Beans",
    "ToT",

    # South Sudan
    "Fuel (diesel, parallel market)",
    "Fuel (petrol-gasoline, parallel market)",
    "Wage (non-qualified labour, non-agricultural)",
    "Sorghum (local)",
    "Sorghum (red, local)",
    "Sorghum flour",
    "Oil (vegetable, fortified, food aid)",
    "Beans (fava, dry)",
    "Cowpeas",
    "Wage (non-qualified labour, agricultural)",
    "Sorghum (brown)",
    "Exchange rate",
    "Rice",
    "ToT (Labour/Cereal)",
    "ToT (Goat/Cereal)"
]

# ---------------------------------------------------
# Shock Indicators
# ---------------------------------------------------

SHOCK_INDICATORS = [
    "conflict_events",
    "conflict_fatalities",
]

SHOCK_MANMADE = [
    "conflict_events",
    "conflict_fatalities"
]

FLOOD_INDICATORS = [
    "percent_area_flooded"
]

# ---------------------------------------------------
# All Indicators
# ---------------------------------------------------

INDICATORS = (
    CLIMATE_INDICATORS
    + PRICE_INDICATORS
    + SHOCK_INDICATORS
    + FLOOD_INDICATORS
)

# ---------------------------------------------------
# Indicator Country Mapping
# ---------------------------------------------------

INDICATOR_COUNTRY_MAP = {

    # Climate indicators apply everywhere
    "rainfall 1-month anomaly [%]": ["Afghanistan", "South Sudan", "Kenya"],
    "rainfall 3-month anomaly [%]": ["Afghanistan", "South Sudan", "Kenya"],
    "10 day NDVI anomaly": ["Afghanistan", "South Sudan", "Kenya"],
    "rainfall-mm": ["Afghanistan", "South Sudan", "Kenya"],
    "ndvi_absolute": ["Afghanistan", "South Sudan", "Kenya"],

    # Afghanistan price indicators
    "Bread": ["Afghanistan"],
    "Exchange rate": ["Afghanistan", "South Sudan"],
    "Fuel (diesel)": ["Afghanistan", "South Sudan"],
    "Oil (cooking)": ["Afghanistan"],
    "Pulses": ["Afghanistan"],
    "Rice (high quality)": ["Afghanistan"],
    "Rice (low quality)": ["Afghanistan"],
    "Sugar": ["Afghanistan"],
    "Wage (non-qualified labour, non-agricultural)": ["Afghanistan", "South Sudan"],
    "Wheat": ["Afghanistan"],
    "Wheat flour (high quality)": ["Afghanistan"],
    "Wheat flour (low quality)": ["Afghanistan"],
    "ToT (Labour/Cereal)":  ["Afghanistan"],

    # Kenya indicators
    "Goat": ["Kenya"],
    "Maize": ["Kenya"],
    "Beans": ["Kenya"],
    "ToT": ["Kenya"],
    # South Sudan price indicators
    "Fuel (diesel, parallel market)": ["South Sudan"],
    "Fuel (petrol-gasoline, parallel market)": ["South Sudan"],
    "Sorghum (local)": ["South Sudan"],
    "Sorghum (red, local)": ["South Sudan"],
    "Sorghum flour": ["South Sudan"],
    "Oil (vegetable, fortified, food aid)": ["South Sudan"],
    "Beans (fava, dry)": ["South Sudan"],
    "Cowpeas": ["South Sudan"],
    "Wage (non-qualified labour, agricultural)": ["South Sudan"],
    "Sorghum (brown)": ["South Sudan"],
    "Rice": ["South Sudan"],
    "conflict_events": ["South Sudan"],
    "conflict_fatalities": ["South Sudan"],

    # Flood Indicators by country
    "percent_area_flooded": ["South Sudan","Afghanistan"],
}


# ---------------------------------------------------
# Column Definitions (STANDARDIZED PIPELINE COLUMNS)
# ---------------------------------------------------

UNIT_COL = "adm1_name"
DATE_COL = "date"
INDICATOR_COL = "indicator"
VALUE_COL = "value"
COUNTRY_COL = "country"


# ---------------------------------------------------
# Baseline Methods
# ---------------------------------------------------

BASELINE_METHODS = [
    "LTM",
    "YOY",
    "FIVE_YEAR"
]

DEFAULT_BASELINE = "LTM"


# ---------------------------------------------------
# Indicator Risk Direction
# ---------------------------------------------------

INDICATOR_DIRECTION = {

    # Lower-tail risk
    "rainfall 1-month anomaly [%]": "lower",
    "rainfall 3-month anomaly [%]": "lower",
    "10 day NDVI anomaly": "lower",
    "10 day NDVI": "lower",
    # RAW climate indicators
    "rainfall-mm": "lower",
    "ndvi_absolute": "lower",
    "NDVI long term average": "lower",
    "ToT": "lower",
    "ToT (Labour/Cereal)": "lower",
    "ToT (Goat/Cereal)": "lower",

    # Afghanistan prices
    "Bread": "upper",
    "Exchange rate": "upper",
    "Fuel (diesel)": "upper",
    "Oil (cooking)": "upper",
    "Pulses": "upper",
    "Rice (high quality)": "upper",
    "Rice (low quality)": "upper",
    "Sugar": "upper",
    "Wage (non-qualified labour, non-agricultural)": "upper",
    "Wheat": "upper",
    "Wheat flour (high quality)": "upper",
    "Wheat flour (low quality)": "upper",

    # Kenya prices
    "Goat": "lower",
    "ToT": "lower",
    "Maize": "upper",
    "Beans": "upper",

    # South Sudan
    "Fuel (diesel, parallel market)": "upper",
    "Fuel (petrol-gasoline, parallel market)": "upper",
    "Sorghum (local)": "upper",
    "Sorghum (red, local)": "upper",
    "Sorghum flour": "upper",
    "Oil (vegetable, fortified, food aid)": "upper",
    "Beans (fava, dry)": "upper",
    "Cowpeas": "upper",
    "Wage (non-qualified labour, agricultural)": "upper",
    "Sorghum (brown)": "upper",
    "Rice": "upper",

    # Shock indicators
    "conflict_events": "upper",
    "conflict_fatalities": "upper",

    "percent_area_flooded": "upper"
}


# ---------------------------------------------------
# Indicator Threshold Computation Method
# ---------------------------------------------------

# Defines how thresholds are computed for each indicator
# tukey = Tukey IQR method
# percentile = historical percentile thresholds
# event = binary hazard event trigger

INDICATOR_METHOD = {

    # Climate indicators
    "rainfall 1-month anomaly [%]": "tukey",
    "rainfall 3-month anomaly [%]": "tukey",
    "10 day NDVI anomaly": "tukey",
    # 🔥 ADD THESE
    "rainfall-mm": "spi_true",
    "ndvi_absolute": "spi_true",

    # Afghanistan price indicators
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

    # Kenya indicators
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
    "percent_area_flooded": "percentile"
}


# ---------------------------------------------------
# Indicator Type (for future composite risk modelling)
# ---------------------------------------------------

INDICATOR_TYPE = {

    # Climate indicators
    "rainfall 1-month anomaly [%]": "climate",
    "rainfall 3-month anomaly [%]": "climate",
    "10 day NDVI anomaly": "climate",
    "rainfall-mm": "climate",
    "ndvi_absolute": "climate",
    "percent_area_flooded": "climate",

    # Market indicators
    "Bread": "market",
    "Exchange rate": "market",
    "Fuel (diesel)": "market",
    "Oil (cooking)": "market",
    "Pulses": "market",
    "Rice (high quality)": "market",
    "Rice (low quality)": "market",
    "Sugar": "market",
    "Wage (non-qualified labour, non-agricultural)": "market",
    "Wheat": "market",
    "Wheat flour (high quality)": "market",
    "Wheat flour (low quality)": "market",
    "ToT (Labour/Cereal)": "market",
    "ToT (Goat/Cereal)": "market",

    "Goat": "market",
    "Maize": "market",
    "Beans": "market",
    "ToT": "market",

    "Fuel (diesel, parallel market)": "market",
    "Fuel (petrol-gasoline, parallel market)": "market",
    "Sorghum (local)": "market",
    "Sorghum (red, local)": "market",
    "Sorghum flour": "market",
    "Oil (vegetable, fortified, food aid)": "market",
    "Beans (fava, dry)": "market",
    "Cowpeas": "market",
    "Wage (non-qualified labour, agricultural)": "market",
    "Sorghum (brown)": "market",
    "Rice":"market",

    # Shock indicators

    "conflict_events": "shock",
    "conflict_fatalities": "shock",

}


# ---------------------------------------------------
# Seasonal Definitions
# ---------------------------------------------------

SEASONAL_DEFINITIONS = {

    # Rainfall
    "rainfall 1-month anomaly [%]": {
        "All Months": None,
        "Planting (Mar–Jun)": [3,4,5,6],
        "Off-Season (Jul–Feb)": [7,8,9,10,11,12,1,2]
    },

    "rainfall 3-month anomaly [%]": {
        "All Months": None,
        "Planting (Mar–Jun)": [3,4,5,6],
        "Off-Season (Jul–Feb)": [7,8,9,10,11,12,1,2]
    },

    # NDVI
    "10 day NDVI anomaly": {
        "All Months": None,
        "Growing (Apr–Jul)": [4,5,6,7],
        "Dormant (Aug–Mar)": [8,9,10,11,12,1,2,3]
    },

    # Afghanistan prices
    "Bread": {"All Months": None},
    "Exchange rate": {"All Months": None},
    "Fuel (diesel)": {"All Months": None},
    "Oil (cooking)": {"All Months": None},
    "Pulses": {"All Months": None},
    "Rice (high quality)": {"All Months": None},
    "Rice (low quality)": {"All Months": None},
    "Sugar": {"All Months": None},
    "Wage (non-qualified labour, non-agricultural)": {"All Months": None},
    "Wheat": {"All Months": None},
    "Wheat flour (high quality)": {"All Months": None},
    "Wheat flour (low quality)": {"All Months": None},
    "ToT (Labour/Cereal)": {"All Months": None},
    "ToT (Goat/Cereal)": {"All Months": None},

    # Kenya indicators
    "Goat": {"All Months": None},
    "Maize": {"All Months": None},
    "Beans": {"All Months": None},
    "ToT": {"All Months": None},

    # South Sudan
    "Fuel (diesel, parallel market)": {"All Months": None},
    "Fuel (petrol-gasoline, parallel market)": {"All Months": None},
    "Sorghum (local)": {"All Months": None},
    "Sorghum (red, local)": {"All Months": None},
    "Sorghum flour": {"All Months": None},
    "Oil (vegetable, fortified, food aid)": {"All Months": None},
    "Beans (fava, dry)": {"All Months": None},
    "Cowpeas": {"All Months": None},
    "Wage (non-qualified labour, agricultural)": {"All Months": None},
    "Sorghum (brown)": {"All Months": None},
    "Rice": {"All Months": None},

    # Shock indicators
    "conflict_events": {"All Months": None},
    "conflict_fatalities": {"All Months": None}
}

# ---------------------------------------------------
# Country Configurations
# ---------------------------------------------------

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
    },

    # Temporarily using adm1_name until dataset changes to county
    "Kenya": {
        "unit_col": "adm1_name",
        "price_file": "data/price_data_kenya.xlsx",
        "rainfall_file": "data/rainfall_ndvi_kenya.xlsx",
        "conflict_file": "data/acled_kenya.xlsx"
    }
}


# ---------------------------------------------------
# Indicator Labels
# ---------------------------------------------------

INDICATOR_LABELS = {

    "rainfall 1-month anomaly [%]": "Rainfall Anomaly (1-month)",
    "rainfall 3-month anomaly [%]": "Rainfall Anomaly (3-month)",
    "10 day NDVI anomaly": "NDVI Anomaly",
    "rainfall-mm": "Rainfall (mm)",
    "ndvi_absolute": "NDVI (Absolute)",

    "Bread": "Bread Price",
    "Exchange rate": "Exchange Rate",
    "Fuel (diesel)": "Diesel Price",
    "Oil (cooking)": "Cooking Oil Price",
    "Pulses": "Pulses Price",
    "Rice (high quality)": "Rice (High Quality)",
    "Rice (low quality)": "Rice (Low Quality)",
    "Sugar": "Sugar Price",
    "Wage (non-qualified labour, non-agricultural)": "Daily Wage",
    "Wheat": "Wheat Price",
    "Wheat flour (high quality)": "Wheat Flour (High Quality)",
    "Wheat flour (low quality)": "Wheat Flour (Low Quality)",

    "Goat": "Goat Price",
    "Maize": "Maize Price",
    "Beans": "Beans Price",
    "ToT": "Terms of Trade",

    # Shock indicators
    "conflict_events": "Conflict Events",
    "conflict_fatalities":"Conflict Fatalities"
}

# ---------------------------------------------------
# Reference Events Configuration
# ---------------------------------------------------

REFERENCE_EVENTS_FILE = "data/reference_events.xlsx"

REFERENCE_EVENTS_COLUMNS = {
    "country": "country",
    "start": "start",
    "end": "end",
    "event": "event",
    "type": "type",
    "show_for": "show_for"
}

INDICATOR_TRANSFORM = {
    "conflict_events": "none",
    "conflict_fatalities": "log"
}

MIN_OBSERVATIONS = {
    "conflict_events": 5,
    "conflict_fatalities": 5
}

# ---------------------------------------------------
# Indicator Allowed Baseline Methods (FLEXIBLE)
# ---------------------------------------------------

INDICATOR_ALLOWED_BASELINES = {

    # Climate (already anomaly-based → no baseline needed)
    "rainfall 1-month anomaly [%]": ["none"],
    "rainfall 3-month anomaly [%]": ["none"],
    "10 day NDVI anomaly": ["none"],
    "rainfall-mm": ["none"],
    "ndvi_absolute": ["none"],

    # Prices → allow full flexibility
    "Bread": ["YOY", "LTM", "FIVE_YEAR"],
    "Exchange rate": ["YOY", "LTM", "FIVE_YEAR"],
    "Fuel (diesel)": ["YOY", "LTM", "FIVE_YEAR"],
    "Oil (cooking)": ["YOY", "LTM", "FIVE_YEAR"],
    "Pulses": ["YOY", "LTM", "FIVE_YEAR"],
    "Rice (high quality)": ["YOY", "LTM", "FIVE_YEAR"],
    "Rice (low quality)": ["YOY", "LTM", "FIVE_YEAR"],
    "Sugar": ["YOY", "LTM", "FIVE_YEAR"],
    "Wage (non-qualified labour, non-agricultural)": ["YOY", "LTM", "FIVE_YEAR"],
    "Wheat": ["YOY", "LTM", "FIVE_YEAR"],
    "Wheat flour (high quality)": ["YOY", "LTM", "FIVE_YEAR"],
    "Wheat flour (low quality)": ["YOY", "LTM", "FIVE_YEAR"],

    "Goat": ["YOY", "LTM", "FIVE_YEAR"],
    "Maize": ["YOY", "LTM", "FIVE_YEAR"],
    "Beans": ["YOY", "LTM", "FIVE_YEAR"],
    "ToT": ["YOY", "LTM", "FIVE_YEAR"],

    "Fuel (diesel, parallel market)": ["YOY", "LTM", "FIVE_YEAR"],
    "Fuel (petrol-gasoline, parallel market)": ["YOY", "LTM", "FIVE_YEAR"],
    "Sorghum (local)": ["YOY", "LTM", "FIVE_YEAR"],
    "Sorghum (red, local)": ["YOY", "LTM", "FIVE_YEAR"],
    "Sorghum flour": ["YOY", "LTM", "FIVE_YEAR"],
    "Oil (vegetable, fortified, food aid)": ["YOY", "LTM", "FIVE_YEAR"],
    "Beans (fava, dry)": ["YOY", "LTM", "FIVE_YEAR"],
    "Cowpeas": ["YOY", "LTM", "FIVE_YEAR"],
    "Wage (non-qualified labour, agricultural)": ["YOY", "LTM", "FIVE_YEAR"],
    "Sorghum (brown)": ["YOY", "LTM", "FIVE_YEAR"],
    "Rice": ["YOY", "LTM", "FIVE_YEAR"],
    "ToT (Labour/Cereal)": ["YOY", "LTM", "FIVE_YEAR"],
    "ToT (Goat/Cereal)": ["YOY", "LTM", "FIVE_YEAR"],

    # 🔥 CONFLICT (KEY PART)
    "conflict_events": ["none"],
    "conflict_fatalities": ["none"],

    # FLOOD INDICATORS
    "percent_area_flooded": ["none"]
}

# ---------------------------------------------------
# Indicator Threshold Override (ADVANCED)
# ---------------------------------------------------

INDICATOR_THRESHOLD_OVERRIDE = {

    "conflict_fatalities": "anomaly_zscore"
}

# ---------------------------------------------------
# Conflict Threshold Rules
# ---------------------------------------------------

CONFLICT_ZSCORE_THRESHOLDS = {

    "conflict_events": {
        "alert": 1.0,
        "alarm": 2.0
    },

    "conflict_fatalities": {
        "alert": 1.0,
        "alarm": 2.5
    }
}

INDICATOR_GROUPS = {
    "Climate": CLIMATE_INDICATORS,
    "Flood": FLOOD_INDICATORS,
    "Price / Economic": PRICE_INDICATORS,
    "Shock (Man-made)": SHOCK_MANMADE,
}


# ---------------------------------------------------
# Conflict Combined Rules (Events + Fatalities)
# ---------------------------------------------------

CONFLICT_USE_COMBINED = True   # 🔥 master switch

CONFLICT_COMBINED_RULES = {
    "conflict_events": {
        "event_alert_threshold": 1,
        "event_alarm_threshold": 2,
        "fatality_alarm_threshold": 5
    }
}

EVENT_THRESHOLDS = {
    "conflict_events": {
        "alert": 1,
        "alarm": 2
    },

    # 🔥 ADD THIS BLOCK
    "conflict_fatalities": {
        "alert": 5,
        "alarm": 20
    }
}

# ---------------------------------------------------
# Combined Indicator Definitions (GENERIC)
# ---------------------------------------------------

COMBINED_INDICATORS = {
    "conflict_events": {
        "components": ["conflict_events", "conflict_fatalities"],
        "suffixes": ["events", "fatalities"]
    }
}

# ---------------------------------------------------
# Z-SCORE THRESHOLDS (GLOBAL DEFAULT)
# ---------------------------------------------------

ZSCORE_THRESHOLDS = {
    "default": {
        "alert": 1.0,
        "alarm": 2.0
    }
}

# ---------------------------------------------------
# Indicator Allowed Threshold Methods (CLEAN & SCALABLE)
# ---------------------------------------------------

INDICATOR_ALLOWED_METHODS = {}

# Climate → full methods
for ind in CLIMATE_INDICATORS:
    INDICATOR_ALLOWED_METHODS[ind] = ["tukey", "percentile", "zscore"]

# Prices → percentile + tukey
for ind in PRICE_INDICATORS:
    INDICATOR_ALLOWED_METHODS[ind] = ["percentile", "tukey", "zscore"]

# Shock indicators → special handling
INDICATOR_ALLOWED_METHODS["conflict_events"] = ["percentile", "categorical"]
INDICATOR_ALLOWED_METHODS["conflict_fatalities"] = ["percentile", "categorical"]


INDICATOR_ALLOWED_METHODS["percent_area_flooded"] = ["percentile"]

# ---------------------------------------------------
# Z-score Aggregation Method (Monthly Level)
# ---------------------------------------------------

Z_AGGREGATION_METHOD = {

    # -----------------------------------------
    # Climate Indicators → mean
    # -----------------------------------------
    "rainfall 1-month anomaly [%]": "mean",
    "rainfall 3-month anomaly [%]": "mean",
    "10 day NDVI anomaly": "mean",
    "rainfall-mm": "mean",
    "ndvi_absolute": "mean",

    # -----------------------------------------
    # Price Indicators → mean
    # -----------------------------------------

    # Afghanistan
    "Bread": "mean",
    "Exchange rate": "mean",
    "Fuel (diesel)": "mean",
    "Oil (cooking)": "mean",
    "Pulses": "mean",
    "Rice (high quality)": "mean",
    "Rice (low quality)": "mean",
    "Sugar": "mean",
    "Wage (non-qualified labour, non-agricultural)": "mean",
    "Wheat": "mean",
    "Wheat flour (high quality)": "mean",
    "Wheat flour (low quality)": "mean",

    # Kenya
    "Goat": "mean",
    "Maize": "mean",
    "Beans": "mean",
    "ToT": "mean",

    # South Sudan
    "Fuel (diesel, parallel market)": "mean",
    "Fuel (petrol-gasoline, parallel market)": "mean",
    "Wage (non-qualified labour, non-agricultural)": "mean",
    "Sorghum (local)": "mean",
    "Sorghum (red, local)": "mean",
    "Sorghum flour": "mean",
    "Oil (vegetable, fortified, food aid)": "mean",
    "Beans (fava, dry)": "mean",
    "Cowpeas": "mean",
    "Wage (non-qualified labour, agricultural)": "mean",
    "Sorghum (brown)": "mean",
    "Rice": "mean",

    # -----------------------------------------
    # Shock Indicators (NOT USED for Z-score)
    # Included for completeness / future-proofing
    # -----------------------------------------
    "conflict_events": "sum",
    "conflict_fatalities": "sum"
}


# ---------------------------------------------------
# Terms of Trade (ToT) Configuration
# ---------------------------------------------------

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
        "enabled": False  # Already exists in data
    },

    "South Sudan": {
        "enabled": False
    }
}

DERIVED_INDICATORS = [
    "ToT (Labour/Cereal)",
    "ToT (Goat/Cereal)"
]

DEFAULT_METHOD_DESCRIPTIONS = {

    "percentile": (
        "Using percentile-based thresholds computed from spatial distributions.\n\n"
        "• Alert = moderate deviation from normal\n"
        "• Alarm = extreme deviation from normal\n\n"
        "Useful for detecting relative anomalies across areas."
    ),

    "tukey": (
        "Using Tukey IQR method:\n\n"
        "• Alert = Q1 - 1.0 × IQR\n"
        "• Alarm = Q1 - 1.5 × IQR\n\n"
        "Robust method for detecting extreme deviations."
    ),

    "zscore": (
        "Using Z-score standardization:\n\n"
        "• Alert ≈ 1 standard deviation\n"
        "• Alarm ≈ 2 standard deviations\n\n"
        "Measures how far values deviate from the mean."
    ),

    "categorical": (
        "Using fixed rule-based thresholds defined in configuration.\n\n"
        "Useful for event-based indicators."
    ),

    "spi_true": (
        "Using Standardized Precipitation Index (SPI - Gamma distribution):\n\n"
        "• Fits rainfall distribution using Gamma model\n"
        "• Converts rainfall to probability\n"
        "• Transforms to standard normal scale\n\n"
        "• Alert ≈ -1 (moderate drought)\n"
        "• Alarm ≈ -2 (severe drought)\n\n"
        "Scientifically robust method for drought detection."
    )
}


# ----------------------------------------------------------------------
# Method Descriptions (UI messaging – FULLY CONTROLLABLE) - special cases
# ----------------------------------------------------------------------

METHOD_DESCRIPTIONS = {

    "conflict_events": {
        "categorical": (
            "Using categorical rule:\n\n"
            "• Alert ≥ 1 event\n"
            "• Alarm ≥ 2 events\n\n"
            "Switch to 'percentile' method for spatial thresholding."
        ),
        "percentile": (
            "Using percentile-based thresholds computed from spatial distributions.\n\n"
            "Allows detection of relative anomalies across areas."
        )
    },

    "conflict_fatalities": {
        "categorical": (
            "Using categorical rule:\n\n"
            "• Alert ≥ 5 fatalities\n"
            "• Alarm ≥ 20 fatalities\n\n"
            "Switch to 'percentile' for anomaly-based detection."
        ),
        "percentile": (
            "Using percentile-based thresholds computed from spatial distributions.\n\n"
            "Allows detection of relative anomalies across areas."
        )
    },

    "ToT (Labour/Cereal)": {
        "percentile": (
            "Using percentile thresholds on Terms of Trade (Wage / Cereal).\n\n"
            "Indicates purchasing power of households.\n\n"
            "Lower values indicate reduced access to food."
        )
    },

    "ToT": {
            "percentile": (
                "Using percentile thresholds on Terms of Trade (Goat / Cereal).\n\n"
                "Indicates purchasing power of households.\n\n"
                "Lower values indicate reduced access to food."
            )
        }
}

# ---------------------------------------------------
# SPI-STYLE Z-SCORE THRESHOLDS (SEASONALLY ADJUSTED)
# ---------------------------------------------------


SPI_TRUE_THRESHOLDS = {
    "default": {"alert": -1.0, "alarm": -2.0},
    "rainfall-mm": {"alert": -1.0, "alarm": -2.0},
    "ndvi_absolute": {"alert": -1.0, "alarm": -2.0}
}

# ---------------------------------------------------
# METHODS THAT REQUIRE SEASONAL STANDARDIZATION
# ---------------------------------------------------

SEASONAL_STANDARDIZATION_METHODS = ["spi_true"]

# ---------------------------------------------------
# SPI REQUIRES RAW CLIMATE DATA (CRITICAL CONTROL)
# ---------------------------------------------------

SPI_TRUE_INDICATORS = [
    "rainfall-mm",
    "ndvi_absolute"
]

# ---------------------------------------------------
# 🌍 STANDARD ADMIN UNITS (MASTER LIST)
# ---------------------------------------------------

STANDARD_ADM1 = {
    "South Sudan": [
        "Abyei", "Juba", "Kajo-keji", "Lainya", "Morobo", "Terekeka", "Yei",
        "Budi", "Ikotos", "Kapoeta East", "Kapoeta North", "Kapoeta South",
        "Lafon", "Magwi", "Torit", "Akobo", "Ayod", "Bor South", "Canal/Pigi",
        "Duk", "Fangak", "Nyirol", "Pibor", "Pochalla", "Twic East", "Uror",
        "Awerial", "Cueibet", "Rumbek Centre", "Rumbek East", "Rumbek North",
        "Wulu", "Yirol East", "Yirol West", "Aweil Centre", "Aweil East",
        "Aweil North", "Aweil South", "Aweil West", "Abiemnhom", "Guit",
        "Koch", "Leer", "Mayendit", "Mayom", "Panyijiar", "Pariang",
        "Rubkona", "Baliet", "Fashoda", "Longochuk", "Luakpiny/Nasir",
        "Maban", "Maiwut", "Malakal", "Manyo", "Melut", "Panyikang",
        "Renk", "Ulang", "Gogrial East", "Gogrial West", "Tonj East",
        "Tonj North", "Tonj South", "Twic", "Jur River", "Raja", "Wau",
        "Ezo", "Ibba", "Maridi", "Mundri East", "Mundri West", "Mvolo",
        "Nagero", "Nzara", "Tambura", "Yambio", "Akoka"
    ],

    "Kenya": [
        "Baringo", "Embu", "Garissa", "Isiolo", "Kajiado", "Kilifi", "Kitui",
        "Kwale", "Laikipia", "Lamu", "Makueni", "Mandera", "Marsabit",
        "Meru", "Narok", "Nyeri", "Samburu", "Taita Taveta", "Tana River",
        "Tharaka Nithi", "Turkana", "Wajir", "West Pokot"
    ],

    "Afghanistan": [
        "Badakhshan", "Badghis", "Baghlan", "Balkh", "Bamyan", "Daykundi",
        "Farah", "Faryab", "Ghazni", "Ghor", "Hilmand", "Hirat",
        "Jawzjan", "Kabul", "Kandahar", "Kapisa", "Khost", "Kunar",
        "Kunduz", "Laghman", "Logar", "Maidan Wardak", "Nangarhar",
        "Nimroz", "Nuristan", "Paktika", "Paktya", "Panjsher",
        "Parwan", "Samangan", "Sar-e-Pul", "Takhar", "Uruzgan", "Zabul"
    ]
}


ADMIN_REPLACEMENTS = {
    "Kenya": {
        "Nairob": "Nairobi",
        "Mombassa": "Mombasa",
        "Kisum": "Kisumu"
    },
    "Afghanistan": {
        "Wardak": "Maidan Wardak",
        "Sar-e-pul": "Sar-e-Pul",
        "Sar-E Pol": "Sar-e-Pul"

}
}