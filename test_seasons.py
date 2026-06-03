from src.config import get_country_seasons

print("\nAFGHANISTAN")
print(
    get_country_seasons(
        "Afghanistan",
        "rainfall 1-month anomaly [%]"
    )
)

print("\nKENYA")
print(
    get_country_seasons(
        "Kenya",
        "rainfall 1-month anomaly [%]"
    )
)

print("\nSOUTH SUDAN")
print(
    get_country_seasons(
        "South Sudan",
        "rainfall 1-month anomaly [%]"
    )
)