import pandas as pd
from src.config import REFERENCE_EVENTS_FILE


# ---------------------------------------------------
# Load reference events from Excel
# ---------------------------------------------------

def load_reference_events():

    df = pd.read_excel(REFERENCE_EVENTS_FILE)

    # Standardize country names
    df["country"] = df["country"].str.strip()

    # Convert show_for into list
    df["show_for"] = df["show_for"].apply(
        lambda x: [i.strip() for i in str(x).split(",")]
    )

    return df


# ---------------------------------------------------
# Filter events for dashboard
# ---------------------------------------------------

def get_reference_events(df, country, indicator_type):

    events = df[
        (df["country"].isin(["GLOBAL", country])) &
        (df["show_for"].apply(lambda x: indicator_type in x))
    ]

    return events