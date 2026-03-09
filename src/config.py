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
# All Indicators
# ---------------------------------------------------

INDICATORS = CLIMATE_INDICATORS + PRICE_INDICATORS


# ---------------------------------------------------
# Indicator Country Mapping
# ---------------------------------------------------

INDICATOR_COUNTRY_MAP = {

    # Climate indicators apply everywhere
    "rainfall 1-month anomaly [%]": ["Afghanistan", "Somalia", "Kenya"],
    "rainfall 3-month anomaly [%]": ["Afghanistan", "Somalia", "Kenya"],
    "10 day NDVI anomaly": ["Afghanistan", "Somalia", "Kenya"],

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
    "Goat": "upper",
    "Maize": "upper",
    "Beans": "upper"
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
    "ToT": {"All Months": None}
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

    "Somalia": {
        "unit_col": "admin1",
        "price_file": "data/price_data_somalia.xlsx",
        "rainfall_file": "data/rainfall_ndvi_somalia.xlsx"
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
    "ToT": "Terms of Trade"
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