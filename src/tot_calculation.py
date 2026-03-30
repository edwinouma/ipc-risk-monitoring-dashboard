# src/tot_calculation.py

import pandas as pd


def compute_tot(df, country, config):
    """
    Compute Terms of Trade (ToT) based on config.

    ToT = numerator / denominator

    Returns dataframe with new ToT indicators appended.
    """

    if country not in config:
        return pd.DataFrame()

    country_cfg = config[country]

    if not country_cfg.get("enabled", False):
        return pd.DataFrame()

    results = []

    for definition in country_cfg["definitions"]:

        num = definition["numerator"]
        den = definition["denominator"]
        name = definition["name"]

        # -----------------------------------------
        # Extract numerator & denominator
        # -----------------------------------------
        num_df = df[df["indicator"] == num].copy()
        den_df = df[df["indicator"] == den].copy()

        if num_df.empty or den_df.empty:
            print(f"[ToT WARNING] Skipping '{name}' for {country} (missing data: "
                  f"{'numerator' if num_df.empty else ''}"
                  f"{' & ' if num_df.empty and den_df.empty else ''}"
                  f"{'denominator' if den_df.empty else ''})")
            continue

        # -----------------------------------------
        # Merge on unit + time
        # -----------------------------------------
        merged = num_df.merge(
            den_df,
            on=["adm1_name", "year_month"],
            suffixes=("_num", "_den")
        )

        # -----------------------------------------
        # Compute ToT
        # -----------------------------------------
        merged["value"] = merged["value_num"] / merged["value_den"]

        merged["indicator"] = name

        results.append(
            merged[["adm1_name", "year_month", "indicator", "value"]]
        )

    if not results:
        return pd.DataFrame()

    return pd.concat(results, ignore_index=True)