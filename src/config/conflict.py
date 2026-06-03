# ==========================================================
# CONFLICT PIPELINE CONFIGURATION
# ==========================================================

# Master switch:
# True  = use combined events + fatalities logic
# False = treat each indicator independently

CONFLICT_USE_COMBINED = True


# ==========================================================
# CONFLICT COMBINATION RULES
# ==========================================================

CONFLICT_COMBINED_RULES = {

    "conflict_events": {

        # Number of event alerts required
        "event_alert_threshold": 1,

        # Number of event alarms required
        "event_alarm_threshold": 2,

        # Fatality escalation trigger
        "fatality_alarm_threshold": 5
    }
}


# ==========================================================
# COMBINED INDICATOR DEFINITIONS
# ==========================================================

COMBINED_INDICATORS = {

    "conflict_events": {

        "components": [
            "conflict_events",
            "conflict_fatalities"
        ],

        "suffixes": [
            "events",
            "fatalities"
        ]
    }
}


# ==========================================================
# DATA TRANSFORMATION
# ==========================================================

INDICATOR_TRANSFORM = {

    "conflict_events": "none",

    "conflict_fatalities": "log"
}


# ==========================================================
# MINIMUM DATA REQUIREMENTS
# ==========================================================

MIN_OBSERVATIONS = {

    "conflict_events": 5,

    "conflict_fatalities": 5
}