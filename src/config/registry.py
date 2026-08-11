# ==========================================================
# IMPORTS
# ==========================================================

from .seasonality import (
    COUNTRY_SEASONS,
    ALL_MONTHS_ONLY
)

from .methods import (
    INDICATOR_METHOD,
    INDICATOR_ALLOWED_METHODS,
    INDICATOR_ALLOWED_BASELINES,
)

from .indicators import (
    INDICATOR_DIRECTION,
    INDICATOR_TYPE,
    MORBIDITY_INDICATORS,
)

from .labels import (
    INDICATOR_LABELS,
    CLASSIFICATION_LABELS,
)

from .thresholds import (
    EVENT_THRESHOLDS,
    CONFLICT_HYBRID_THRESHOLDS,
    ZSCORE_THRESHOLDS,
    SPI_TRUE_THRESHOLDS,
    SPI_TRUE_FLOOD_THRESHOLDS,
    ZSCORE_TRUE_THRESHOLDS,
    ALPS_THRESHOLDS,
    COUNTRY_THRESHOLDS,
    INDICATOR_PERCENTILES,
)

from .countries import (
    INDICATOR_COUNTRY_MAP,
    COUNTRY_CONFIG,
)


# ==========================================================
# INDICATOR METADATA
# ==========================================================

def get_method(indicator):
    return INDICATOR_METHOD.get(indicator)


def get_direction(indicator):
    return INDICATOR_DIRECTION.get(indicator)


def get_indicator_type(indicator):
    return INDICATOR_TYPE.get(indicator)


def get_label(indicator):
    return INDICATOR_LABELS.get(indicator, indicator)


def get_supported_countries(indicator):
    return INDICATOR_COUNTRY_MAP.get(indicator, [])


# ==========================================================
# COUNTRY CONFIGURATION
# ==========================================================

def get_country_config(country):
    return COUNTRY_CONFIG.get(country, {})


# ==========================================================
# METHOD OPTIONS
# ==========================================================

def get_allowed_methods(indicator):
    return INDICATOR_ALLOWED_METHODS.get(indicator, [])


def get_allowed_baselines(indicator):
    return INDICATOR_ALLOWED_BASELINES.get(indicator, [])


# ==========================================================
# CLASSIFICATION LABELS
# ==========================================================

def get_classification_label(classification):

    return CLASSIFICATION_LABELS.get(
        classification,
        classification
    )


# ==========================================================
# THRESHOLDS
# ==========================================================

def get_event_thresholds(indicator):

    return EVENT_THRESHOLDS.get(
        indicator,
        {}
    )


def get_zscore_thresholds(indicator=None):

    return ZSCORE_THRESHOLDS.get(
        indicator,
        ZSCORE_THRESHOLDS["default"]
    )


def get_spi_thresholds(indicator):

    return SPI_TRUE_THRESHOLDS.get(
        indicator,
        SPI_TRUE_THRESHOLDS["default"]
    )


def get_spi_flood_thresholds(indicator):

    return SPI_TRUE_FLOOD_THRESHOLDS.get(
        indicator,
        SPI_TRUE_FLOOD_THRESHOLDS["default"]
    )


def get_zscore_true_thresholds(indicator):

    return ZSCORE_TRUE_THRESHOLDS.get(
        indicator,
        ZSCORE_TRUE_THRESHOLDS["default"]
    )


# ==========================================================
# ALPS THRESHOLDS
# ==========================================================

def get_alps_thresholds():

    return ALPS_THRESHOLDS["default"]


# ==========================================================
# PERCENTILE CONFIGURATION
# ==========================================================

def get_percentile_config(indicator):

    direction = get_direction(indicator)

    if indicator in INDICATOR_PERCENTILES:
        return INDICATOR_PERCENTILES[indicator]

    if direction == "upper":
        return INDICATOR_PERCENTILES["default_upper"]

    return INDICATOR_PERCENTILES["default_lower"]


# ==========================================================
# FUTURE COUNTRY-SPECIFIC THRESHOLDS
# ==========================================================

def get_thresholds(country, indicator):

    # Future override
    if (
        country in COUNTRY_THRESHOLDS
        and indicator in COUNTRY_THRESHOLDS[country]
    ):
        return COUNTRY_THRESHOLDS[country][indicator]

    return EVENT_THRESHOLDS.get(
        indicator,
        {}
    )


# ==========================================================
# COUNTRY HYBRID THRESHOLDS
# ==========================================================

def get_hybrid_thresholds(country, indicator):

    if (
        country in COUNTRY_THRESHOLDS
        and indicator in COUNTRY_THRESHOLDS[country]
    ):
        return COUNTRY_THRESHOLDS[country][indicator]

    return CONFLICT_HYBRID_THRESHOLDS.get(
        indicator,
        {}
    )


# ==========================================================
# SEASONS
# ==========================================================

def get_country_seasons(country, indicator):

    rainfall_indicators = [
        "rainfall 1-month anomaly [%]",
        "rainfall 3-month anomaly [%]",
        "rainfall-mm"
    ]

    ndvi_indicators = [
        "10 day NDVI anomaly",
        "ndvi_absolute"
    ]

    # ------------------------------------------------------
    # Rainfall
    # ------------------------------------------------------

    if indicator in rainfall_indicators:

        return COUNTRY_SEASONS.get(
            country,
            {}
        ).get(
            "Rainfall",
            ALL_MONTHS_ONLY
        )

    # ------------------------------------------------------
    # NDVI
    # ------------------------------------------------------

    if indicator in ndvi_indicators:

        return COUNTRY_SEASONS.get(
            country,
            {}
        ).get(
            "NDVI",
            ALL_MONTHS_ONLY
        )

    # ------------------------------------------------------
    # Morbidity
    #
    # Morbidity is seasonally standardized by calendar month:
    #
    # January  -> historical Januaries
    # February -> historical Februaries
    # ...
    # December -> historical Decembers
    #
    # Therefore no rainfall/NDVI seasonal-window definition
    # is applied.
    # ------------------------------------------------------

    if indicator in MORBIDITY_INDICATORS:
        return ALL_MONTHS_ONLY

    # ------------------------------------------------------
    # Default
    # ------------------------------------------------------

    return ALL_MONTHS_ONLY