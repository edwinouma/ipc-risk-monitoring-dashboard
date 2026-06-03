# ==========================================================
# INDICATOR DISPLAY LABELS
# ==========================================================

INDICATOR_LABELS = {

    # Climate
    "rainfall 1-month anomaly [%]": "Rainfall Anomaly (1-month)",
    "rainfall 3-month anomaly [%]": "Rainfall Anomaly (3-month)",
    "10 day NDVI anomaly": "NDVI Anomaly",
    "rainfall-mm": "Rainfall (mm)",
    "ndvi_absolute": "NDVI (Absolute)",

    # Afghanistan
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

    # Kenya
    "Goat": "Goat Price",
    "Maize": "Maize Price",
    "Beans": "Beans Price",
    "ToT": "Terms of Trade",

    # South Sudan
    "Fuel (diesel, parallel market)": "Diesel Price",
    "Fuel (petrol-gasoline, parallel market)": "Petrol Price",
    "Sorghum (local)": "Sorghum Price",
    "Sorghum (red, local)": "Red Sorghum Price",
    "Sorghum flour": "Sorghum Flour Price",
    "Oil (vegetable, fortified, food aid)": "Vegetable Oil Price",
    "Beans (fava, dry)": "Fava Beans Price",
    "Cowpeas": "Cowpeas Price",
    "Wage (non-qualified labour, agricultural)": "Agricultural Wage",
    "Sorghum (brown)": "Brown Sorghum Price",
    "Rice": "Rice Price",

    # Conflict
    "conflict_events": "Conflict Events",
    "conflict_fatalities": "Conflict Fatalities",

    # Flood
    "percent_area_flooded": "Percent Area Flooded"
}


# ==========================================================
# IPC PHASE COLORS
# ==========================================================

IPC_PHASE_COLORS = {
    "phase 1": "green",
    "phase 2": "yellow",
    "phase 3": "orange",
    "phase 4": "red",
    "phase 5": "darkred"
}


# ==========================================================
# CLASSIFICATION LABELS
# ==========================================================

CLASSIFICATION_LABELS = {
    "alarm": "Alarm",
    "alert": "Alert",
    "minimal": "No concern",
    "no_data": "No data"
}


# ==========================================================
# DEFAULT METHOD DESCRIPTIONS
# ==========================================================

DEFAULT_METHOD_DESCRIPTIONS = {

    "percentile": (
        "Using percentile-based thresholds computed from spatial distributions.\n\n"
        "• Alert = moderate deviation from normal\n"
        "• Alarm = extreme deviation from normal\n\n"
        "Useful for detecting relative anomalies across areas."
    ),

    "tukey": (
        "Tukey method — Detects unusually extreme values.\n\n"
        "Uses the interquartile range (IQR) to identify values that fall outside "
        "the normal range of variation."
    ),

    "zscore_true": (
        "True Z-score method — Measures how unusual values are relative to their "
        "historical seasonal average."
    ),

    "spi_true": (
        "SPI method — Detects unusually dry or wet conditions relative to the "
        "historical distribution for that month or season."
    ),

    "categorical": (
        "Categorical method — Classifies risk using predefined event-count thresholds."
    ),

    "hybrid": (
        "Hybrid method — Combines categorical thresholds, anomalies, and trend escalation."
    )
}


# ==========================================================
# INDICATOR-SPECIFIC METHOD DESCRIPTIONS
# ==========================================================

METHOD_DESCRIPTIONS = {

    "ToT (Labour/Cereal)": {
        "percentile": (
            "Using percentile thresholds on Terms of Trade (Wage / Cereal).\n\n"
            "Indicates purchasing power of households.\n\n"
            "Lower values indicate reduced food access."
        )
    },

    "ToT": {
        "percentile": (
            "Using percentile thresholds on Terms of Trade (Goat / Cereal).\n\n"
            "Indicates purchasing power of households.\n\n"
            "Lower values indicate reduced food access."
        )
    }
}