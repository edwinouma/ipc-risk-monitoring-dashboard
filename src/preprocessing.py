import pandas as pd
from src.config import DATE_COL


def preprocess_data(df, date_col):
    """
    Basic preprocessing for all indicators.

    Tasks:
    - Convert date column to datetime
    - Remove rows with invalid dates
    - Extract year, month
    - Create month name for visualization
    - Create year_month period for aggregation
    - Create year_month_str for plotting
    - Sort data for time-series consistency
    """

    # ---------------------------------------------------
    # 1. Ensure datetime (safe conversion)
    # ---------------------------------------------------
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")

    # Drop rows where date could not be parsed
    df = df.dropna(subset=[DATE_COL]).copy()

    # ---------------------------------------------------
    # 2. Time Components
    # ---------------------------------------------------
    df["year"] = df[DATE_COL].dt.year
    df["month"] = df[DATE_COL].dt.month
    df["month_name"] = df[DATE_COL].dt.strftime("%b")

    # ---------------------------------------------------
    # 3. Monthly Aggregation Key
    # ---------------------------------------------------
    df["year_month"] = df[DATE_COL].dt.to_period("M")

    # Useful for charts
    df["year_month_str"] = df["year_month"].astype(str)

    # ---------------------------------------------------
    # 4. Sort for time series stability
    # ---------------------------------------------------
    df = df.sort_values(DATE_COL)

    return df


# ---------------------------------------------------
# Conflict Data Processing (NEW - Modular Addition)
# ---------------------------------------------------

def process_conflict_data(df, country=None):
    """
    Processes raw conflict event data into indicator format.

    Outputs:
    - conflict_events (count of events per unit-month)
    - conflict_fatalities (sum per unit-month)

    Returns standardized dataframe:
    country | adm1_name | year_month | indicator | value
    """

    # ---------------------------------------------------
    # 1. Ensure datetime
    # ---------------------------------------------------
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.dropna(subset=["event_date"]).copy()

    # ---------------------------------------------------
    # 2. Optional: filter relevant conflict types
    # ---------------------------------------------------
    if "disorder_type" in df.columns:
        df = df[df["disorder_type"] == "Political violence"].copy()

    # ---------------------------------------------------
    # 3. Create year_month (IMPORTANT: keep as Period)
    # ---------------------------------------------------
    df["year_month"] = df["event_date"].dt.to_period("M")

    # ---------------------------------------------------
    # 4. Conflict events (count)
    # ---------------------------------------------------
    df_events = (
        df.groupby(["adm1_name", "year_month"])
        .size()
        .reset_index(name="value")
    )
    df_events["indicator"] = "conflict_events"

    # ---------------------------------------------------
    # 5. Conflict fatalities (sum)
    # ---------------------------------------------------
    df_fatalities = (
        df.groupby(["adm1_name", "year_month"])["conflict_fatalities"]
        .sum()
        .reset_index(name="value")
    )
    df_fatalities["indicator"] = "conflict_fatalities"

    # ---------------------------------------------------
    # 6. Combine
    # ---------------------------------------------------
    df_final = pd.concat([df_events, df_fatalities], ignore_index=True)

    # ---------------------------------------------------
    # 🔥 FIX: Recreate date column from year_month
    # ---------------------------------------------------
    df_final["date"] = df_final["year_month"].dt.to_timestamp()

    # ---------------------------------------------------
    # 7. Add country
    # ---------------------------------------------------
    if country is not None:
        df_final["country"] = country

    return df_final