import pandas as pd
import os

from src.config import DATE_COL, STANDARD_ADM1, ADMIN_REPLACEMENTS
from difflib import get_close_matches

# ---------------------------------------------------
# 🔥 ADD THIS FUNCTION HERE (⬇️ RIGHT HERE)
# ---------------------------------------------------
def suggest_closest(name, valid_list, cutoff=0.7):
    """
    Suggest closest match using fuzzy logic.
    """
    matches = get_close_matches(name, valid_list, n=1, cutoff=cutoff)
    return matches[0] if matches else None

# ---------------------------------------------------
# 🔥 ADMIN VALIDATION (SHARED FUNCTION)
# ---------------------------------------------------
def enforce_admin_standard(df, country_col="country", adm_col="adm1_name"):
    df = df.copy()

    # 🔹 Clean text (important for real-world data)
    df[adm_col] = df[adm_col].astype(str).str.strip().str.title()

    invalid_tracker = {}

    for country, valid_units in STANDARD_ADM1.items():
        mask = df[country_col] == country

        # Apply replacements
        replacements = ADMIN_REPLACEMENTS.get(country, {})
        df.loc[mask, adm_col] = df.loc[mask, adm_col].replace(replacements)

        # Detect invalid
        subset = df.loc[mask, adm_col]
        invalid = subset[~subset.isin(valid_units)]

        if len(invalid) > 0:
            suggestions = {}

            print(f"\n⚠ {country} - INVALID ADMIN NAMES FOUND:")

            for val in invalid.unique():
                suggestion = suggest_closest(val, valid_units)
                suggestions[val] = suggestion

                print(f"{val} → Suggested: {suggestion}")

            invalid_tracker[country] = suggestions

        # Enforce valid names only
        df.loc[mask, adm_col] = df.loc[mask, adm_col].where(
            df.loc[mask, adm_col].isin(valid_units),
            other=None
        )

    return df, invalid_tracker


# ---------------------------------------------------
# 🔥 HELPER: EXPORT INVALIDS (WITH SUGGESTIONS)
# ---------------------------------------------------
def export_invalid_names(invalid_tracker, filename):
    if invalid_tracker:
        import os
        os.makedirs("outputs", exist_ok=True)

        rows = []

        for country, mapping in invalid_tracker.items():
            for invalid_name, suggestion in mapping.items():
                rows.append({
                    "country": country,
                    "invalid_name": invalid_name,
                    "suggested_name": suggestion
                })

        pd.DataFrame(rows).to_excel(filename, index=False)

# ---------------------------------------------------
# 🔥 PREPROCESS (CLIMATE / PRICE)
# ---------------------------------------------------
def preprocess_data(df, date_col):

    # Ensure datetime
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df = df.dropna(subset=[DATE_COL]).copy()

    # Admin validation
    df, invalid_tracker = enforce_admin_standard(df)
    export_invalid_names(invalid_tracker, "outputs/invalid_admin_names.xlsx")

    # Drop invalid
    df = df.dropna(subset=["adm1_name"])

    # Time features
    df["year"] = df[DATE_COL].dt.year
    df["month"] = df[DATE_COL].dt.month
    df["month_name"] = df[DATE_COL].dt.strftime("%b")

    df["year_month"] = df[DATE_COL].dt.to_period("M")
    df["year_month_str"] = df["year_month"].astype(str)

    # Sort
    df = df.sort_values(DATE_COL)

    return df


# ---------------------------------------------------
# 🔥 CONFLICT PROCESSING
# ---------------------------------------------------
def process_conflict_data(df, country=None):

    # Ensure datetime
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.dropna(subset=["event_date"]).copy()

    # Optional filtering
    if "disorder_type" in df.columns:
        df = df[df["disorder_type"] == "Political violence"].copy()

    # Create month
    df["year_month"] = df["event_date"].dt.to_period("M")

    # Events
    df_events = (
        df.groupby(["adm1_name", "year_month"])
        .size()
        .reset_index(name="value")
    )
    df_events["indicator"] = "conflict_events"

    # Fatalities
    df_fatalities = (
        df.groupby(["adm1_name", "year_month"])["conflict_fatalities"]
        .sum()
        .reset_index(name="value")
    )
    df_fatalities["indicator"] = "conflict_fatalities"

    # Combine
    df_final = pd.concat([df_events, df_fatalities], ignore_index=True)

    # Restore date
    df_final["date"] = df_final["year_month"].dt.to_timestamp()

    # Add country
    if country is not None:
        df_final["country"] = country

    # Admin validation
    df_final, invalid_tracker = enforce_admin_standard(df_final)
    export_invalid_names(invalid_tracker, "outputs/invalid_admin_names_conflict.xlsx")

    # Drop invalid
    df_final = df_final.dropna(subset=["adm1_name"])

    return df_final