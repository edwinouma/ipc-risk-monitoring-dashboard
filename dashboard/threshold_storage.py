import json
import os
import pandas as pd


# ---------------------------------------------------
# File paths
# ---------------------------------------------------
DEFAULT_THRESHOLDS_PATH = "outputs/thresholds_results.csv"
OVERRIDE_PATH = "data/threshold_overrides.json"


# ---------------------------------------------------
# Utility: Ensure override file exists
# ---------------------------------------------------
def _ensure_override_file():
    os.makedirs(os.path.dirname(OVERRIDE_PATH), exist_ok=True)

    if not os.path.exists(OVERRIDE_PATH):
        with open(OVERRIDE_PATH, "w") as f:
            json.dump({}, f)


# ---------------------------------------------------
# Load default thresholds from backend CSV
# ---------------------------------------------------
def load_default_thresholds():
    """
    Load default thresholds computed from backend.
    """
    if not os.path.exists(DEFAULT_THRESHOLDS_PATH):
        raise FileNotFoundError(
            "Default thresholds file not found. Run main.py first."
        )

    df = pd.read_csv(DEFAULT_THRESHOLDS_PATH)
    return df


# ---------------------------------------------------
# Load override thresholds (JSON)
# ---------------------------------------------------
def load_overrides():
    """
    Load stored TWG threshold overrides.
    """
    _ensure_override_file()

    with open(OVERRIDE_PATH, "r") as f:
        overrides = json.load(f)

    return overrides


# ---------------------------------------------------
# Save override for specific indicator + method
# ---------------------------------------------------
def save_override(indicator, method, alarm_value, alert_value):
    """
    Save TWG override threshold.
    """
    _ensure_override_file()

    overrides = load_overrides()

    if indicator not in overrides:
        overrides[indicator] = {}

    overrides[indicator][method] = {
        "alarm": float(alarm_value),
        "alert": float(alert_value)
    }

    with open(OVERRIDE_PATH, "w") as f:
        json.dump(overrides, f, indent=4)


# ---------------------------------------------------
# Reset override for specific indicator + method
# ---------------------------------------------------
def reset_override(indicator, method):
    """
    Remove override and revert to default.
    """
    _ensure_override_file()

    overrides = load_overrides()

    if indicator in overrides and method in overrides[indicator]:
        del overrides[indicator][method]

        # Remove indicator key if empty
        if not overrides[indicator]:
            del overrides[indicator]

    with open(OVERRIDE_PATH, "w") as f:
        json.dump(overrides, f, indent=4)


# ---------------------------------------------------
# Get active thresholds (default + override)
# ---------------------------------------------------
def get_active_thresholds(indicator, method):
    """
    Return active alarm & alert thresholds.
    Override takes precedence over default.
    """

    defaults = load_default_thresholds()
    overrides = load_overrides()

    row = defaults[defaults["indicator"] == indicator]

    if row.empty:
        raise ValueError(f"No default thresholds found for {indicator}")

    row = row.iloc[0]

    # Determine correct default columns
    if method == "percentile":
        default_alarm = row["alarm_percentile"]
        default_alert = row["alert_percentile"]

    elif method == "tukey":
        default_alarm = row["alarm_tukey"]
        default_alert = row["alert_tukey"]

    else:
        raise ValueError("Method must be 'percentile' or 'tukey'")

    # Apply override if exists
    if indicator in overrides and method in overrides[indicator]:
        alarm = overrides[indicator][method]["alarm"]
        alert = overrides[indicator][method]["alert"]
    else:
        alarm = default_alarm
        alert = default_alert

    return alarm, alert