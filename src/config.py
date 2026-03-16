DEFAULT_THRESHOLD_METHOD = "percentile"
# ---------------------------------------------------
# Indicator Groups
# ---------------------------------------------------

CLIMATE_INDICATORS = [
    "rainfall 1-month anomaly [%]",
    "rainfall 3-month anomaly [%]",
    "10 day NDVI anomaly"
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
    "ToT"
]

# ---------------------------------------------------
# Shock Indicators
# ---------------------------------------------------

SHOCK_INDICATORS = [
    "conflict_events",
    "flood_occurrence",
    "flood_area"
]

# ---------------------------------------------------
# All Indicators
# ---------------------------------------------------

INDICATORS = CLIMATE_INDICATORS + PRICE_INDICATORS


# ---------------------------------------------------
# Indicator Country Mapping
# ---------------------------------------------------

INDICATOR_COUNTRY_MAP = {

    # Climate indicators apply everywhere
    "rainfall 1-month anomaly [%]": ["Afghanistan", "South Sudan", "Kenya"],
    "rainfall 3-month anomaly [%]": ["Afghanistan", "South Sudan", "Kenya"],
    "10 day NDVI anomaly": ["Afghanistan", "South Sudan", "Kenya"],

    # Afghanistan price indicators
    "Bread": ["Afghanistan"],
    "Exchange rate": ["Afghanistan"],
    "Fuel (diesel)": ["Afghanistan"],
    "Oil (cooking)": ["Afghanistan"],
    "Pulses": ["Afghanistan"],
    "Rice (high quality)": ["Afghanistan"],
    "Rice (low quality)": ["Afghanistan"],
    "Sugar": ["Afghanistan"],
    "Wage (non-qualified labour, non-agricultural)": ["Afghanistan"],
    "Wheat": ["Afghanistan"],
    "Wheat flour (high quality)": ["Afghanistan"],
    "Wheat flour (low quality)": ["Afghanistan"],

    # Kenya indicators
    "Goat": ["Kenya"],
    "Maize": ["Kenya"],
    "Beans": ["Kenya"],
    "ToT": ["Kenya"]
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
    "NDVI long term average": "lower",
    "ToT": "lower",

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
    "Maize": "upper",
    "Beans": "upper",

    # Shock indicators
    "conflict_events": "upper",
    "conflict_fatalities": "upper",
    "flood_area": "upper"
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

    # Kenya indicators
    "Goat": "percentile",
    "Maize": "percentile",
    "Beans": "percentile",
    "ToT": "percentile",

    # Shock indicators
    "conflict_events": "percentile",
    "conflict_fatalities": "percentile",
    "flood_occurrence": "event",
    "flood_area": "percentile"
}


# ---------------------------------------------------
# Indicator Type (for future composite risk modelling)
# ---------------------------------------------------

INDICATOR_TYPE = {

    # Climate indicators
    "rainfall 1-month anomaly [%]": "climate",
    "rainfall 3-month anomaly [%]": "climate",
    "10 day NDVI anomaly": "climate",

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

    "Goat": "market",
    "Maize": "market",
    "Beans": "market",
    "ToT": "market",

    # Shock indicators

    "conflict_events": "shock",
    "conflict_fatalities": "shock",
    "flood_occurrence": "hazard",
    "flood_area": "hazard"
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

    # Kenya indicators
    "Goat": {"All Months": None},
    "Maize": {"All Months": None},
    "Beans": {"All Months": None},
    "ToT": {"All Months": None},

    # Shock indicators
    "conflict_events": {"All Months": None},
    "conflict_fatalities": {"All Months": None},
    "flood_occurrence": {"All Months": None},
    "flood_area": {"All Months": None}
}


# ---------------------------------------------------
# Country Configurations
# ---------------------------------------------------

COUNTRY_CONFIG = {

    "Afghanistan": {
        "unit_col": "adm1_name",
        "price_file": "data/price_data.xlsx",
        "rainfall_file": "data/rainfall_ndvi.xlsx"
    },

    "South Sudan": {
        "unit_col": "admin1",
        "price_file": "data/price_data_south sudan.xlsx",
        "rainfall_file": "data/rainfall_ndvi_South Sudan.xlsx"
    },

    # Temporarily using adm1_name until dataset changes to county
    "Kenya": {
        "unit_col": "adm1_name",
        "price_file": "data/price_data_kenya.xlsx",
        "rainfall_file": "data/rainfall_ndvi_kenya.xlsx"
    }
}


# ---------------------------------------------------
# Indicator Labels
# ---------------------------------------------------

INDICATOR_LABELS = {

    "rainfall 1-month anomaly [%]": "Rainfall Anomaly (1-month)",
    "rainfall 3-month anomaly [%]": "Rainfall Anomaly (3-month)",
    "10 day NDVI anomaly": "NDVI Anomaly",

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
    "conflict_fatalities":"Conflict Fatalities",
    "flood_occurrence": "Flood Occurrence",
    "flood_area": "Flooded Area"
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