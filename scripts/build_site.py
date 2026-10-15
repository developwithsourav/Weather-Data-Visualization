"""Put the report page together in _site/, ready to open or publish.

Copies site/index.html and the charts, and writes _site/data.json for the city explorer.
"""
import json
import shutil
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_FILE = BASE_DIR / "data" / "processed" / "weather_clean.csv"
REALISM_FILE = BASE_DIR / "data" / "processed" / "realism_check.csv"
SITE_DIR = BASE_DIR / "_site"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def monthly(days, column, how="mean"):
    """Twelve values, one per month, averaged over the years."""
    years = days["year"].nunique()
    if how == "total":
        values = days.groupby("month")[column].sum() / years
    else:
        values = days.groupby("month")[column].mean()
    return [round(float(value), 1) for value in values.reindex(range(1, 13))]


def city_profile(days):
    """Everything the explorer shows for one city."""
    years = days["year"].nunique()
    hottest = days.loc[days["temp_max_c"].idxmax()]
    coldest = days.loc[days["temp_min_c"].idxmin()]
    monsoon_rain = days.loc[days["season"] == "Monsoon", "rain_mm"].sum()
    rain_by_month = monthly(days, "rain_mm", "total")
    temp_by_month = monthly(days, "temp_mean_c")

    return {
        "monthly": {
            "temp_mean": temp_by_month,
            "temp_max": monthly(days, "temp_max_c"),
            "temp_min": monthly(days, "temp_min_c"),
            "rain": rain_by_month,
            "humidity": monthly(days, "humidity_pct"),
        },
        "stats": {
            "average_temperature": round(float(days["temp_mean_c"].mean()), 1),
            "hottest": {"value": float(hottest["temp_max_c"]), "date": hottest["date"].strftime("%d %b %Y")},
            "coldest": {"value": float(coldest["temp_min_c"]), "date": coldest["date"].strftime("%d %b %Y")},
            "yearly_rain": round(float(days["rain_mm"].sum() / years)),
            "rainy_days": round(float((days["rain_mm"] >= 2.5).sum() / years)),
            "days_45": int((days["temp_max_c"] >= 45).sum()),
            "monsoon_share": round(float(monsoon_rain / days["rain_mm"].sum() * 100)),
            "warmest_month": MONTH_NAMES[temp_by_month.index(max(temp_by_month))],
            "wettest_month": MONTH_NAMES[rain_by_month.index(max(rain_by_month))],
        },
    }


def main():
    weather = pd.read_csv(CLEAN_FILE, parse_dates=["date"])

    data = {
        "months": MONTH_NAMES,
        "period": f"{weather['date'].min():%d %b %Y} to {weather['date'].max():%d %b %Y}",
        "all_cities": {
            "temp_mean": monthly(weather, "temp_mean_c"),
            "rain": [round(value / weather["city"].nunique(), 1) for value in monthly(weather, "rain_mm", "total")],
        },
        "cities": {city: city_profile(days) for city, days in weather.groupby("city")},
    }
    if REALISM_FILE.exists():
        data["realism"] = pd.read_csv(REALISM_FILE).to_dict(orient="records")

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    (SITE_DIR / "charts").mkdir(parents=True)
    shutil.copy(BASE_DIR / "site" / "index.html", SITE_DIR / "index.html")
    for chart in (BASE_DIR / "charts").glob("*.png"):
        shutil.copy(chart, SITE_DIR / "charts" / chart.name)
    (SITE_DIR / "data.json").write_text(json.dumps(data), encoding="utf-8")

    print(f"Built {SITE_DIR.relative_to(BASE_DIR)}/ with {len(data['cities'])} cities "
          f"and {len(list((SITE_DIR / 'charts').glob('*.png')))} charts")


if __name__ == "__main__":
    main()
