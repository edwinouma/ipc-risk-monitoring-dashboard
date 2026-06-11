import pandas as pd
from src.config import (
    INDICATOR_DIRECTION,
    get_percentile_config
)


def compute_composite_thresholds(spatial_df, indicator_value):
    """
    Compute final Alert and Alarm thresholds
    from time series of spatial percentiles.

    Direction-aware:
        - lower tail → drought style
        - upper tail → inflation style
    """

    # ---------------------------------------------------
    # Handle empty input safely
    # ---------------------------------------------------
    if spatial_df.empty:
        return pd.DataFrame({
            "indicator": [indicator_value],
            "alert_threshold": [None],
            "alarm_threshold": [None]
        })

    # ---------------------------------------------------
    # Validate required columns
    # ---------------------------------------------------
    required_cols = [
        col for col in [
            "q05",
            "q10",
            "q25",
            "q50",
            "q70",
            "q75",
            "q80",
            "q90",
            "q95"
        ]
        if col in spatial_df.columns
    ]

    for col in required_cols:
        if col not in spatial_df.columns:
            raise ValueError(
                f"{col} missing from spatial_df while computing thresholds "
                f"for indicator: {indicator_value}"
            )

    # ---------------------------------------------------
    # Determine indicator direction
    # ---------------------------------------------------
    direction = INDICATOR_DIRECTION.get(indicator_value, "lower")

    # ---------------------------------------------------
    # Compute thresholds
    # ---------------------------------------------------

    cfg = get_percentile_config(indicator_value)

    alert_pct = cfg["alert"]
    alarm_pct = cfg["alarm"]

    if direction == "lower":

        alert_col = f"q{int(alert_pct):02d}"
        alarm_col = f"q{int(alarm_pct):02d}"

    elif direction == "upper":

        alert_col = f"q{int(alert_pct):02d}"
        alarm_col = f"q{int(alarm_pct):02d}"

    else:
        raise ValueError(
            f"Unknown direction '{direction}' for indicator {indicator_value}"
        )

    required_cols = [alert_col, alarm_col]

    for col in required_cols:

        if col not in spatial_df.columns:
            raise ValueError(
                f"{col} missing from spatial_df. "
                f"Percentile configuration requires "
                f"monthly percentile column '{col}'."
            )

    alert = spatial_df[alert_col].median(skipna=True)
    alarm = spatial_df[alarm_col].median(skipna=True)

    # ---------------------------------------------------
    # Return structured result
    # ---------------------------------------------------
    return pd.DataFrame({
        "indicator": [indicator_value],
        "alert_threshold": [alert],
        "alarm_threshold": [alarm]
    })