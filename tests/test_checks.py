"""Tests for the data checks and the realism check."""
import numpy as np
import pandas as pd
import pytest

from clean_data import check_quality
from realism_check import realism_scores, verdict

DATES = pd.date_range("2021-01-01", "2022-12-31")


def good_rows():
    """Two cities with a full set of sensible values for every day."""
    rows = []
    for city in ["Delhi", "Mumbai"]:
        for date in DATES:
            rows.append({
                "city": city, "date": date, "temp_mean_c": 25.0, "temp_max_c": 30.0, "temp_min_c": 20.0,
                "humidity_pct": 60, "pressure_hpa": 1010.0, "wind_speed_kmh": 8.0,
                "wind_direction_deg": 180, "rain_mm": 0.0, "weather_code": 0, "weather": "Clear",
                "latitude": 28.6, "longitude": 77.2,
            })
    return pd.DataFrame(rows)


def test_good_data_passes():
    check_quality(good_rows())


@pytest.mark.parametrize("column, bad_value", [
    ("humidity_pct", 120),
    ("rain_mm", -1.0),
    ("pressure_hpa", 500.0),
    ("temp_min_c", 35.0),
    ("weather", None),
])
def test_one_bad_value_stops_the_pipeline(column, bad_value):
    rows = good_rows()
    rows.loc[5, column] = bad_value
    with pytest.raises(SystemExit):
        check_quality(rows)


def test_missing_day_stops_the_pipeline():
    rows = good_rows().drop(index=10)
    with pytest.raises(SystemExit):
        check_quality(rows)


def test_duplicate_day_stops_the_pipeline():
    rows = good_rows()
    rows = pd.concat([rows, rows.iloc[[0]]], ignore_index=True)
    with pytest.raises(SystemExit):
        check_quality(rows)


def fake_weather(seed):
    """Three cities with seasons, day-to-day memory and different averages."""
    rng = np.random.default_rng(seed)
    season = 8 * np.sin(2 * np.pi * (DATES.dayofyear - 100) / 365)
    table = {}
    for city, average in [("A", 20), ("B", 25), ("C", 30)]:
        noise = np.zeros(len(DATES))
        for day in range(1, len(DATES)):
            noise[day] = 0.8 * noise[day - 1] + rng.normal(0, 1)
        table[city] = average + season + noise
    return pd.DataFrame(table, index=DATES.strftime("%Y-%m-%d"))


def random_numbers(seed):
    """Three cities of independent random numbers around the same average."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.normal(60, 15, (len(DATES), 3)), index=DATES.strftime("%Y-%m-%d"),
                        columns=["A", "B", "C"])


def test_weather_like_data_looks_real():
    assert verdict(realism_scores(fake_weather(seed=1))) == "looks real"


def test_random_numbers_look_random():
    assert verdict(realism_scores(random_numbers(seed=1))) == "looks random"
