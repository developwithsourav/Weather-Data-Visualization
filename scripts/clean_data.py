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

    # Report anything that looks wrong instead of hiding it.
    missing = weather.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("No missing values.")
    else:
        print("Missing values per column:")
        print(missing)

    duplicates = weather.duplicated(subset=["city", "date"]).sum()
    print(f"Duplicate city/date rows: {duplicates}")

    weather = weather.sort_values(["city", "date"])
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    weather.to_csv(CLEAN_FILE, index=False)
    print(f"Saved {len(weather):,} rows and {weather['city'].nunique()} cities to {CLEAN_FILE}")


if __name__ == "__main__":
    main()
