from src.config import INDICATORS

# ---------------------------------------------------
# Indicator Groups
# ---------------------------------------------------
# Used to apply different processing pipelines


# Climate indicators (use spatial percentiles)
CLIMATE_INDICATORS = [
    "rainfall 1-month anomaly [%]",
    "rainfall 3-month anomaly [%]",
    "10 day NDVI anomaly"
]


# Price indicators (use baseline anomalies)
PRICE_INDICATORS = [
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
    "Wheat flour (low quality)"
]


# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------

def get_climate_indicators():
    """Return list of climate indicators"""
    return CLIMATE_INDICATORS


def get_price_indicators():
    """Return list of price indicators"""
    return PRICE_INDICATORS


def is_climate_indicator(indicator):
    """Check if indicator belongs to climate group"""
    return indicator in CLIMATE_INDICATORS


def is_price_indicator(indicator):
    """Check if indicator belongs to price group"""
    return indicator in PRICE_INDICATORS