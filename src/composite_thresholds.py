import pandas as pd
from src.config import INDICATOR_DIRECTION


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
    required_cols = ["q25", "q50", "q75"]

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
    if direction == "lower":

        alert = spatial_df["q50"].median(skipna=True)
        alarm = spatial_df["q25"].median(skipna=True)

    elif direction == "upper":

        alert = spatial_df["q50"].median(skipna=True)
        alarm = spatial_df["q75"].median(skipna=True)

    else:
        raise ValueError(
            f"Unknown direction '{direction}' for indicator {indicator_value}"
        )

    # ---------------------------------------------------
    # Return structured result
    # ---------------------------------------------------
    return pd.DataFrame({
        "indicator": [indicator_value],
        "alert_threshold": [alert],
        "alarm_threshold": [alarm]
    })