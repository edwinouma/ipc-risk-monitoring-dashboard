from src.config import (
    INDICATORS,
    INDICATOR_DIRECTION,
    SEASONAL_DEFINITIONS
)

from src.indicator_groups import (
    is_climate_indicator,
    is_price_indicator
)


# ---------------------------------------------------
# Indicator Metadata Builder
# ---------------------------------------------------

def build_indicator_metadata():
    """
    Build metadata dictionary for all indicators.

    Metadata includes:
    - group (climate or price)
    - risk direction (upper/lower)
    - seasonal definitions
    """

    metadata = {}

    for indicator in INDICATORS:

        if is_climate_indicator(indicator):
            group = "climate"
        elif is_price_indicator(indicator):
            group = "price"
        else:
            group = "unknown"

        metadata[indicator] = {
            "group": group,
            "direction": INDICATOR_DIRECTION.get(indicator),
            "seasons": SEASONAL_DEFINITIONS.get(indicator)
        }

    return metadata


# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------

def get_indicator_group(indicator):
    """Return indicator group"""
    metadata = build_indicator_metadata()
    return metadata[indicator]["group"]


def get_indicator_direction(indicator):
    """Return risk direction (upper/lower)"""
    metadata = build_indicator_metadata()
    return metadata[indicator]["direction"]


def get_indicator_seasons(indicator):
    """Return seasonal definitions"""
    metadata = build_indicator_metadata()
    return metadata[indicator]["seasons"]