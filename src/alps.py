"""
==============================================================
ALPS (Alert for Price Spikes)
==============================================================

Implementation of the World Food Programme (WFP)
Alert for Price Spikes (ALPS) methodology.

RAAp implementation differences
-------------------------------
1. Expanding historical window
2. No look-ahead bias
3. Optional robust residual standardization (MAD)
4. Modular design for integration with RAAp

Reference
---------
World Food Programme (2009).
The ALPS Approach for Monitoring Food Prices.

Author
------
Edwin Ouma
==============================================================
"""
import numpy as np
import pandas as pd

import statsmodels.api as sm

from scipy.stats import median_abs_deviation
from src.config.thresholds import ALPS_THRESHOLDS

# ==========================================================
# HISTORICAL DATA CHECK
# ==========================================================

def has_minimum_history(
    df,
    minimum_history=36
):
    """
    Check whether sufficient historical observations exist.

    Parameters
    ----------
    df : pandas.DataFrame

    minimum_history : int

    Returns
    -------
    bool
    """

    return len(df) >= minimum_history


# ==========================================================
# DESIGN MATRIX
# ==========================================================

def build_design_matrix(df):
    """
    Build the seasonal regression design matrix.

    Model

        Price ~ Time + Monthly Dummies
    """

    X = pd.DataFrame(index=df.index)

    X["time"] = np.arange(len(df))

    month_dummies = pd.get_dummies(
        df["month"],
        prefix="month",
        drop_first=True,
        dtype=int
    )

    X = pd.concat(
        [X, month_dummies],
        axis=1
    )

    X = sm.add_constant(X)

    return X

# ==========================================================
# FIT REGRESSION
# ==========================================================

def fit_regression(df):
    """
    Fit seasonal trend regression.

    Returns
    -------
    statsmodels RegressionResults
    """

    X = build_design_matrix(df)

    y = df["price"]

    model = sm.OLS(
        y,
        X
    ).fit()

    return model

# ==========================================================
# NEXT MONTH PREDICTION
# ==========================================================

def predict_next_month(
    model,
    history,
    month
):
    """
    Predict expected price for the next observation.
    """

    row = pd.DataFrame()

    row["const"] = [1]

    row["time"] = [len(history)]

    for m in range(2, 13):

        row[f"month_{m}"] = (
            1 if month == m else 0
        )

    row = row.reindex(
        columns=model.model.exog_names,
        fill_value=0
    )

    prediction = model.predict(row)

    return float(prediction.iloc[0])

# ==========================================================
# RESIDUAL STANDARDIZATION
# ==========================================================

def compute_residual_scale(
    residuals,
    standardization_method="sd"
):
    """
    Compute residual standardization factor.

    Parameters
    ----------
    residuals : array-like

    standardization_method : {"sd","mad"}

    Returns
    -------
    float
    """

    residuals = (
        pd.Series(residuals)
        .dropna()
    )

    if standardization_method.lower() == "sd":

        scale = residuals.std()

    elif standardization_method.lower() == "mad":

        scale = median_abs_deviation(
            residuals,
            scale="normal"
        )

    else:

        raise ValueError(
            f"Unknown method: {standardization_method}"
        )

    return scale

# ==========================================================
# ALPS CLASSIFICATION
# ==========================================================

def classify_alps(alps):
    """
    Classify ALPS scores using the RAAp classification
    framework.

    ALPS thresholds are defined centrally in
    config.thresholds to ensure consistency across
    the RAAp framework.
    """

    if pd.isna(alps):
        return np.nan

    thresholds = ALPS_THRESHOLDS["default"]

    if alps < thresholds["alert"]:
        return "No Concern"

    elif alps < thresholds["alarm"]:
        return "Alert"

    else:
        return "Alarm"


# ==========================================================
# COMPUTE ALPS
# ==========================================================

def compute_alps(
    df,
    value_column="value",
    date_column="date",
    minimum_history=36,
    standardization_method="sd",
    classify=True
):
    """
    Compute ALPS using an expanding historical window.

    Parameters
    ----------
    df : pandas.DataFrame
        Input monthly price data.

    value_column : str
        Column containing observed prices.

    date_column : str
        Date column.

    minimum_history : int
        Minimum historical observations required.

    standardization_method : {"sd", "mad"}
        Residual standardization method.

    Returns
    -------
    pandas.DataFrame
    """

    # ------------------------------------------------------
    # Validate required columns
    # ------------------------------------------------------

    required_columns = [value_column, date_column]

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ------------------------------------------------------
    # Copy data
    # ------------------------------------------------------

    results = df.copy()

    results = results.sort_values(date_column).reset_index(drop=True)

    # ------------------------------------------------------
    # Create month if missing
    # ------------------------------------------------------

    if "month" not in results.columns:

        results["month"] = (
            pd.to_datetime(results[date_column])
            .dt.month
        )

    # ------------------------------------------------------
    # Initialize outputs
    # ------------------------------------------------------

    results["expected_price"] = np.nan
    results["residual"] = np.nan
    results["residual_scale"] = np.nan
    results["alps"] = np.nan

    # ------------------------------------------------------
    # Expanding historical window
    # ------------------------------------------------------

    for i in range(len(results)):

        history = results.iloc[:i].copy()

        if not has_minimum_history(
            history,
            minimum_history
        ):
            continue

        # --------------------------------------------------
        # Prepare regression dataset
        # --------------------------------------------------

        regression_data = history.rename(
            columns={
                value_column: "price"
            }
        )

        # --------------------------------------------------
        # Fit regression
        # --------------------------------------------------

        try:

            model = fit_regression(
                regression_data
            )

        except Exception:

            continue

        # --------------------------------------------------
        # Predict current observation
        # --------------------------------------------------

        expected_price = predict_next_month(
            model=model,
            history=regression_data,
            month=results.loc[i, "month"]
        )

        # --------------------------------------------------
        # Residual
        # --------------------------------------------------

        observed_price = results.loc[i, value_column]

        residual = (
            observed_price -
            expected_price
        )

        # --------------------------------------------------
        # Historical residuals
        # --------------------------------------------------

        fitted = model.predict(
            build_design_matrix(
                regression_data
            )
        )

        historical_residuals = (
            regression_data["price"] -
            fitted
        )

        # --------------------------------------------------
        # Residual standardization
        # --------------------------------------------------

        scale = compute_residual_scale(
            historical_residuals,
            standardization_method
        )

        if (
            pd.isna(scale)
            or scale == 0
        ):
            continue

        alps = residual / scale

        # --------------------------------------------------
        # Store results
        # --------------------------------------------------

        results.loc[i, "expected_price"] = expected_price

        results.loc[i, "residual"] = residual

        results.loc[i, "residual_scale"] = scale

        results.loc[i, "alps"] = alps

        results.loc[i, "r_squared"] = model.rsquared

        results.loc[i, "rmse"] = np.sqrt(
            np.mean(
                historical_residuals ** 2
            )
        )

    # ------------------------------------------------------
    # Classification
    # ------------------------------------------------------

    if classify:
        results["classification_alps"] = (
            results["alps"]
            .apply(classify_alps)
        )

    return results