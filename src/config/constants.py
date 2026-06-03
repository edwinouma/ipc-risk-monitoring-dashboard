# ==========================================================
# STANDARD PIPELINE COLUMN NAMES
# ==========================================================

UNIT_COL = "adm1_name"
DATE_COL = "date"
INDICATOR_COL = "indicator"
VALUE_COL = "value"
COUNTRY_COL = "country"


# ==========================================================
# REFERENCE EVENTS CONFIGURATION
# ==========================================================

REFERENCE_EVENTS_FILE = "data/reference_events.xlsx"

REFERENCE_EVENTS_COLUMNS = {
    "country": "country",
    "start": "start",
    "end": "end",
    "event": "event",
    "type": "type",
    "show_for": "show_for"
}