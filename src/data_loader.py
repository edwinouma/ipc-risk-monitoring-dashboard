import pandas as pd
from src.config import COUNTRY_CONFIG
from src.preprocessing import process_conflict_data

# ---------------------------------------------------
# Rainfall Data
# ---------------------------------------------------

def load_rainfall_data(filepath):
    df_rainfall = pd.read_excel(filepath)
    return df_rainfall


# ---------------------------------------------------
# Price Data
# ---------------------------------------------------

def load_price_data(filepath):
    df_price_raw = pd.read_excel(filepath)
    return df_price_raw


# ---------------------------------------------------
# Conflict Data
# ---------------------------------------------------

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


# ---------------------------------------------------
# Flood Data (NEW)
# ---------------------------------------------------

def load_flood_data(filepath):
    """
    Loads flood data (already expected in standard format or near-standard).
    """
    df_flood = pd.read_excel(filepath)
    return df_flood


# -----------------------------------------
# LOAD IPC HISTORICAL CLASSIFICATION
# -----------------------------------------
def load_ipc_data(file_path):
    import pandas as pd

    # Read file
    df = pd.read_excel(file_path)

    # -------------------------------------
    # Standardize column names
    # -------------------------------------
    df.columns = df.columns.str.strip().str.lower()

    # -------------------------------------
    # Required columns check
    # -------------------------------------
    required_cols = [
        "country",
        "adm1_name",
        "year_month",
        "ipc_phase",
        "analysis_type"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing IPC columns: {missing}")

    # -------------------------------------
    # Standardize key fields
    # -------------------------------------
    df["country"] = df["country"].astype(str).str.strip()
    df["adm1_name"] = df["adm1_name"].astype(str).str.strip()

    # -------------------------------------
    # Convert to Period[M] (CRITICAL)
    # -------------------------------------
    df["year_month"] = pd.to_datetime(
        df["year_month"],
        errors="coerce"
    ).dt.to_period("M")

    # Drop rows with invalid dates
    df = df.dropna(subset=["year_month"])

    # -------------------------------------
    # Clean text fields
    # -------------------------------------
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

    # -------------------------------------
    # Optional: ensure valid IPC phases
    # -------------------------------------
    valid_phases = {
        "phase 1", "phase 2", "phase 3", "phase 4", "phase 5"
    }

    df = df[df["ipc_phase"].isin(valid_phases)]

    # -------------------------------------
    # Final reset index
    # -------------------------------------
    df = df.reset_index(drop=True)

    return df

# ---------------------------------------------------
# Country Loader (UPDATED - RETURNS SEPARATE DATASETS)
# ---------------------------------------------------

def load_country_data(country):
    """
    Loads datasets separately for a given country.

    Returns:
        df_rainfall, df_price, df_conflict, df_flood
    """

    config = COUNTRY_CONFIG[country]

    df_rainfall = None
    df_price = None
    df_conflict = None
    df_flood = None

    # -------------------------
    # Rainfall
    # -------------------------
    if "rainfall_file" in config:
        df_rainfall = load_rainfall_data(config["rainfall_file"])
        df_rainfall["country"] = country

    # -------------------------
    # Price
    # -------------------------
    if "price_file" in config:
        df_price = load_price_data(config["price_file"])
        df_price["country"] = country

    # -------------------------
    # Conflict
    # -------------------------
    if "conflict_file" in config:
        df_conflict = load_conflict_data(
            config["conflict_file"],
            country=country
        )

    # -------------------------
    # Flood (NEW)
    # -------------------------
    if "flood_file" in config:
        df_flood = load_flood_data(config["flood_file"])
        df_flood["country"] = country

    # -------------------------
    # IPC (NEW)
    # -------------------------
    df_ipc = None

    if "ipc_file" in config:
        df_ipc = load_ipc_data(config["ipc_file"])
        df_ipc["country"] = country

    return df_rainfall, df_price, df_conflict, df_flood, df_ipc