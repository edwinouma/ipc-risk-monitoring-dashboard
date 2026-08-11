import pandas as pd

from src.config import COUNTRY_CONFIG
from src.preprocessing import process_conflict_data


# ==========================================================
# RAINFALL DATA
# ==========================================================

def load_rainfall_data(filepath):
    """
    Loads rainfall / climate data.
    """
    df_rainfall = pd.read_excel(filepath)

    return df_rainfall


# ==========================================================
# PRICE DATA
# ==========================================================

def load_price_data(filepath):
    """
    Loads market price data.
    """
    df_price_raw = pd.read_excel(filepath)

    return df_price_raw


# ==========================================================
# CONFLICT DATA
# ==========================================================

def load_conflict_data(filepath, country=None):
    """
    Loads and processes conflict data into standard format.
    """

    df_conflict_raw = pd.read_excel(filepath)

    df_conflict_processed = process_conflict_data(
        df_conflict_raw,
        country=country
    )

    return df_conflict_processed


# ==========================================================
# FLOOD DATA
# ==========================================================

def load_flood_data(filepath):
    """
    Loads flood data.

    Data is expected to already be in standard
    or near-standard RAAp format.
    """

    df_flood = pd.read_excel(filepath)

    return df_flood


# ==========================================================
# MORBIDITY DATA
# ==========================================================

def load_morbidity_data(filepath):
    """
    Loads routine morbidity case data.

    Expected indicators include:
        - Malaria
        - URTI
        - Diarrhoea

    Expected source structure:
        - country
        - adm1_name
        - indicator
        - date
        - value

    Morbidity values represent historical reported/admission
    case counts and are used directly in the RAAp pipeline.

    Seasonal zscore_true is calculated later in the
    indicator pipeline.
    """

    df = pd.read_excel(filepath)

    # ------------------------------------------------------
    # Standardize column names
    # ------------------------------------------------------

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ------------------------------------------------------
    # Required columns
    # ------------------------------------------------------

    required_cols = [
        "adm1_name",
        "indicator",
        "date",
        "value"
    ]

    missing = [
        col
        for col in required_cols
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing morbidity columns: {missing}"
        )

    # ------------------------------------------------------
    # Standardize ADM1
    # ------------------------------------------------------

    df["adm1_name"] = (
        df["adm1_name"]
        .astype(str)
        .str.strip()
    )

    # ------------------------------------------------------
    # Standardize indicator names
    # ------------------------------------------------------

    df["indicator"] = (
        df["indicator"]
        .astype(str)
        .str.strip()
    )

    # ------------------------------------------------------
    # Ensure numeric case counts
    # ------------------------------------------------------

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # ------------------------------------------------------
    # Standardize date
    # ------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # ------------------------------------------------------
    # Remove invalid observations
    # ------------------------------------------------------

    df = df.dropna(
        subset=[
            "adm1_name",
            "indicator",
            "date",
            "value"
        ]
    ).copy()

    # ------------------------------------------------------
    # Create standard RAAp time fields
    # ------------------------------------------------------

    df["year"] = df["date"].dt.year

    df["month"] = df["date"].dt.month

    df["month_name"] = (
        df["date"]
        .dt.strftime("%b")
    )

    df["year_month"] = (
        df["date"]
        .dt.to_period("M")
    )

    df["year_month_str"] = (
        df["year_month"]
        .astype(str)
    )

    # ------------------------------------------------------
    # Sort
    # ------------------------------------------------------

    df = df.sort_values(
        [
            "adm1_name",
            "indicator",
            "date"
        ]
    )

    df = df.reset_index(drop=True)

    return df


# ==========================================================
# LOAD IPC HISTORICAL CLASSIFICATION
# ==========================================================

def load_ipc_data(file_path):
    """
    Loads historical IPC classification data.
    """

    # ------------------------------------------------------
    # Read file
    # ------------------------------------------------------

    df = pd.read_excel(file_path)

    # ------------------------------------------------------
    # Standardize column names
    # ------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # ------------------------------------------------------
    # Required columns check
    # ------------------------------------------------------

    required_cols = [
        "country",
        "adm1_name",
        "year_month",
        "ipc_phase",
        "analysis_type"
    ]

    missing = [
        c
        for c in required_cols
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing IPC columns: {missing}"
        )

    # ------------------------------------------------------
    # Standardize key fields
    # ------------------------------------------------------

    df["country"] = (
        df["country"]
        .astype(str)
        .str.strip()
    )

    df["adm1_name"] = (
        df["adm1_name"]
        .astype(str)
        .str.strip()
    )

    # ------------------------------------------------------
    # Convert to Period[M]
    # ------------------------------------------------------

    df["year_month"] = pd.to_datetime(
        df["year_month"],
        errors="coerce"
    ).dt.to_period("M")

    df = df.dropna(
        subset=["year_month"]
    )

    # ------------------------------------------------------
    # Clean text fields
    # ------------------------------------------------------

    df["ipc_phase"] = (
        df["ipc_phase"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["analysis_type"] = (
        df["analysis_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ------------------------------------------------------
    # Ensure valid IPC phases
    # ------------------------------------------------------

    valid_phases = {
        "phase 1",
        "phase 2",
        "phase 3",
        "phase 4",
        "phase 5"
    }

    df = df[
        df["ipc_phase"].isin(valid_phases)
    ]

    # ------------------------------------------------------
    # Final reset index
    # ------------------------------------------------------

    df = df.reset_index(drop=True)

    return df


# ==========================================================
# COUNTRY LOADER
# ==========================================================

def load_country_data(country):
    """
    Loads all available datasets separately for a country.

    Returns:
        df_rainfall,
        df_price,
        df_conflict,
        df_flood,
        df_ipc,
        df_morbidity
    """

    config = COUNTRY_CONFIG[country]

    # ------------------------------------------------------
    # Initialize datasets
    # ------------------------------------------------------

    df_rainfall = None
    df_price = None
    df_conflict = None
    df_flood = None
    df_ipc = None
    df_morbidity = None

    # ------------------------------------------------------
    # Rainfall / Climate
    # ------------------------------------------------------

    if "rainfall_file" in config:

        df_rainfall = load_rainfall_data(
            config["rainfall_file"]
        )

        df_rainfall["country"] = country

    # ------------------------------------------------------
    # Price
    # ------------------------------------------------------

    if "price_file" in config:

        df_price = load_price_data(
            config["price_file"]
        )

        df_price["country"] = country

    # ------------------------------------------------------
    # Conflict
    # ------------------------------------------------------

    if "conflict_file" in config:

        df_conflict = load_conflict_data(
            config["conflict_file"],
            country=country
        )

    # ------------------------------------------------------
    # Flood
    # ------------------------------------------------------

    if "flood_file" in config:

        df_flood = load_flood_data(
            config["flood_file"]
        )

        df_flood["country"] = country

    # ------------------------------------------------------
    # IPC
    # ------------------------------------------------------

    if "ipc_file" in config:

        df_ipc = load_ipc_data(
            config["ipc_file"]
        )

        df_ipc["country"] = country

    # ------------------------------------------------------
    # Morbidity
    # ------------------------------------------------------

    if "morbidity_file" in config:

        df_morbidity = load_morbidity_data(
            config["morbidity_file"]
        )

        df_morbidity["country"] = country

    # ------------------------------------------------------
    # Return separate datasets
    # ------------------------------------------------------

    return (
        df_rainfall,
        df_price,
        df_conflict,
        df_flood,
        df_ipc,
        df_morbidity
    )