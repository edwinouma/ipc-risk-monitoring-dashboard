# ==========================================================
# INDICATOR GROUPS
# ==========================================================

CLIMATE_INDICATORS = [
    "rainfall 1-month anomaly [%]",
    "rainfall 3-month anomaly [%]",
    "10 day NDVI anomaly",
    "rainfall-mm",
    "ndvi_absolute"
]


PRICE_INDICATORS = [

    # Afghanistan
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

    # Kenya
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
    "Rice",
    "ToT (Labour/Cereal)",
    "ToT (Goat/Cereal)"
]


SHOCK_INDICATORS = [
    "conflict_events",
    "conflict_fatalities"
]


SHOCK_MANMADE = [
    "conflict_events",
    "conflict_fatalities"
]


FLOOD_INDICATORS = [
    "percent_area_flooded",
    "rainfall-mm"
]


# ==========================================================
# MORBIDITY INDICATORS
# ==========================================================

MORBIDITY_INDICATORS = [
    "Malaria",
    "URTI",
    "Diarrhoea"
]


# ==========================================================
# ALL INDICATORS
# ==========================================================

INDICATORS = (
    CLIMATE_INDICATORS
    + PRICE_INDICATORS
    + SHOCK_INDICATORS
    + FLOOD_INDICATORS
    + MORBIDITY_INDICATORS
)


# ==========================================================
# INDICATOR GROUPS (UI / DASHBOARD)
# ==========================================================

INDICATOR_GROUPS = {
    "Climate": CLIMATE_INDICATORS,
    "Flood": FLOOD_INDICATORS,
    "Price / Economic": PRICE_INDICATORS,
    "Shock (Man-made)": SHOCK_MANMADE,
    "Nutrition / Morbidity": MORBIDITY_INDICATORS,
}



# ==========================================================
# INDICATOR TYPE
# ==========================================================

INDICATOR_TYPE = {

    # ------------------------------------------------------
    # Climate
    # ------------------------------------------------------

    "rainfall 1-month anomaly [%]": "climate",
    "rainfall 3-month anomaly [%]": "climate",
    "10 day NDVI anomaly": "climate",
    "rainfall-mm": "climate",
    "ndvi_absolute": "climate",
    "percent_area_flooded": "climate",

    # ------------------------------------------------------
    # Market
    # ------------------------------------------------------

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
    "Rice": "market",

    # ------------------------------------------------------
    # Shock
    # ------------------------------------------------------

    "conflict_events": "shock",
    "conflict_fatalities": "shock",

    # ------------------------------------------------------
    # Morbidity
    # ------------------------------------------------------

    "Malaria": "morbidity",
    "URTI": "morbidity",
    "Diarrhoea": "morbidity",
}


# ==========================================================
# INDICATOR RISK DIRECTION
# ==========================================================

INDICATOR_DIRECTION = {

    # ------------------------------------------------------
    # Lower-tail risk
    # ------------------------------------------------------

    "rainfall 1-month anomaly [%]": "lower",
    "rainfall 3-month anomaly [%]": "lower",
    "10 day NDVI anomaly": "lower",
    "10 day NDVI": "lower",
    "rainfall-mm": "lower",
    "ndvi_absolute": "lower",
    "NDVI long term average": "lower",

    "ToT": "lower",
    "ToT (Labour/Cereal)": "lower",
    "ToT (Goat/Cereal)": "lower",

    # ------------------------------------------------------
    # Afghanistan
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Kenya
    # ------------------------------------------------------

    "Goat": "lower",
    "Maize": "upper",
    "Beans": "upper",

    # ------------------------------------------------------
    # South Sudan
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Shocks
    # ------------------------------------------------------

    "conflict_events": "upper",
    "conflict_fatalities": "upper",

    # ------------------------------------------------------
    # Flood
    # ------------------------------------------------------

    "percent_area_flooded": "upper",

    # ------------------------------------------------------
    # Morbidity
    # Higher case counts = increasing risk
    # ------------------------------------------------------

    "Malaria": "upper",
    "URTI": "upper",
    "Diarrhoea": "upper",
}