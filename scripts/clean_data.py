"""Turn the raw download into one tidy table for charts and Tableau.

Reads  data/raw/weather_daily.csv
Writes data/processed/weather_clean.csv
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "weather_daily.csv"
CITIES_FILE = BASE_DIR / "data" / "cities.csv"
CLEAN_FILE = BASE_DIR / "data" / "processed" / "weather_clean.csv"

# Shorter column names with the unit in the name.
NEW_NAMES = {
    "time": "date",
    "temperature_2m_mean": "temp_mean_c",
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "relative_humidity_2m_mean": "humidity_pct",
    "pressure_msl_mean": "pressure_hpa",
    "wind_speed_10m_mean": "wind_speed_kmh",
    "wind_direction_10m_dominant": "wind_direction_deg",
    "precipitation_sum": "rain_mm",
}

# WMO weather codes, grouped into a few readable labels.
WEATHER_LABELS = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow",
    80: "Rain showers",
    81: "Rain showers",
    82: "Rain showers",
    85: "Snow",
    86: "Snow",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}

# Seasons as the India Meteorological Department defines them.
SEASONS = {
    1: "Winter", 2: "Winter",
    3: "Pre-monsoon", 4: "Pre-monsoon", 5: "Pre-monsoon",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-monsoon", 11: "Post-monsoon", 12: "Post-monsoon",
}


def check_quality(weather):
    """Stop with an error if the data breaks any basic rule.

    Each check is a name and the number of rows that break it. Zero means the check passed.
    """
    days_per_city = weather.groupby("city")["date"].nunique()
    expected_days = (weather["date"].max() - weather["date"].min()).days + 1

    checks = {
        "missing values": int(weather.isna().any(axis=1).sum()),
        "duplicate city and date": int(weather.duplicated(subset=["city", "date"]).sum()),
        "cities with days missing": int((days_per_city != expected_days).sum()),
        "minimum above maximum temperature": int((weather["temp_min_c"] > weather["temp_max_c"]).sum()),
        "mean outside minimum to maximum": int(((weather["temp_mean_c"] < weather["temp_min_c"])
                                                | (weather["temp_mean_c"] > weather["temp_max_c"])).sum()),
        "humidity outside 0 to 100": int((~weather["humidity_pct"].between(0, 100)).sum()),
        "negative rain": int((weather["rain_mm"] < 0).sum()),
        "pressure outside 900 to 1100 hPa": int((~weather["pressure_hpa"].between(900, 1100)).sum()),
        "wind direction outside 0 to 360": int((~weather["wind_direction_deg"].between(0, 360)).sum()),
        "unknown weather code": int(weather["weather"].isna().sum()),
    }

    print("Data checks:")
    for name, failures in checks.items():
        print(f"  {'ok  ' if failures == 0 else 'FAIL'}  {name}: {failures}")

    if any(checks.values()):
        raise SystemExit("Data checks failed. Fix the data before drawing charts.")


def main():
    weather = pd.read_csv(RAW_FILE).rename(columns=NEW_NAMES)
    cities = pd.read_csv(CITIES_FILE)

    weather["date"] = pd.to_datetime(weather["date"])
    weather["year"] = weather["date"].dt.year
    weather["month"] = weather["date"].dt.month
    weather["season"] = weather["month"].map(SEASONS)
    weather["weather"] = weather["weather_code"].map(WEATHER_LABELS)

    # Add latitude and longitude so Tableau can draw a map.
    weather = weather.merge(cities, on="city", how="left")

    check_quality(weather)

    weather = weather.sort_values(["city", "date"])
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    weather.to_csv(CLEAN_FILE, index=False)
    print(f"Saved {len(weather):,} rows and {weather['city'].nunique()} cities to {CLEAN_FILE}")


if __name__ == "__main__":
    main()
