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