"""Download daily weather for every city in data/cities.csv.

Source: Open-Meteo Historical Weather API (https://open-meteo.com).
The API is free and needs no key. One request is made per city.
"""
import time
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CITIES_FILE = BASE_DIR / "data" / "cities.csv"
RAW_FILE = BASE_DIR / "data" / "raw" / "weather_daily.csv"

API_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2021-01-01"
END_DATE = "2025-12-31"

# Names the API uses for each daily value we ask for.
DAILY_VALUES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m_mean",
    "pressure_msl_mean",
    "wind_speed_10m_mean",
    "wind_direction_10m_dominant",
    "precipitation_sum",
    "weather_code",
]

# The free API allows a limited number of requests per minute, so wait between cities.
PAUSE_SECONDS = 15

# Status codes that usually clear up if we wait and ask again.
TEMPORARY_ERRORS = {429, 502, 503, 504}


def fetch_city(city, latitude, longitude):
    """Return one DataFrame with a row per day for a single city."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join(DAILY_VALUES),
        "timezone": "Asia/Kolkata",
    }

    for attempt in range(1, 6):
        try:
            response = requests.get(API_URL, params=params, timeout=60)
        except requests.RequestException as error:
            print(f"  network problem ({error.__class__.__name__}), retrying (attempt {attempt})")
            time.sleep(60)
            continue
        if response.status_code in TEMPORARY_ERRORS:
            # Too many requests, or the server is busy. Wait a minute and try again.
            print(f"  server answered {response.status_code}, waiting 60 seconds (attempt {attempt})")
            time.sleep(60)
            continue
        response.raise_for_status()
        break
    else:
        raise RuntimeError(f"Could not download data for {city}")

    daily = pd.DataFrame(response.json()["daily"])
    daily.insert(0, "city", city)
    return daily


def main():
    cities = pd.read_csv(CITIES_FILE)
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)

    # If an earlier run stopped half way, keep what it saved and carry on from there.
    already_saved = set()
    if RAW_FILE.exists():
        already_saved = set(pd.read_csv(RAW_FILE, usecols=["city"])["city"])

    for number, row in enumerate(cities.itertuples(), start=1):
        if row.city in already_saved:
            print(f"[{number}/{len(cities)}] {row.city} (already saved)")
            continue
        print(f"[{number}/{len(cities)}] {row.city}")
        daily = fetch_city(row.city, row.latitude, row.longitude)
        # Add this city to the end of the file straight away.
        daily.to_csv(RAW_FILE, mode="a", header=not RAW_FILE.exists(), index=False)
        time.sleep(PAUSE_SECONDS)

    rows = len(pd.read_csv(RAW_FILE, usecols=["city"]))
    print(f"Saved {rows:,} rows to {RAW_FILE}")


if __name__ == "__main__":
    main()
