"""Print the numbers quoted in the README, so each one can be checked.

Reads data/processed/weather_clean.csv
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_FILE = BASE_DIR / "data" / "processed" / "weather_clean.csv"


def main():
    weather = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
    years = weather["year"].nunique()

    print("Size")
    print(f"  rows: {len(weather):,}")
    print(f"  cities: {weather['city'].nunique()}")
    print(f"  dates: {weather['date'].min().date()} to {weather['date'].max().date()}")

    print("\nTemperature (daily mean, °C)")
    by_city = weather.groupby("city")["temp_mean_c"].mean().sort_values()
    print(f"  coolest city on average: {by_city.index[0]} {by_city.iloc[0]:.1f}")
    print(f"  warmest city on average: {by_city.index[-1]} {by_city.iloc[-1]:.1f}")

    hottest = weather.loc[weather["temp_max_c"].idxmax()]
    coldest = weather.loc[weather["temp_min_c"].idxmin()]
    print(f"  highest daily maximum: {hottest['temp_max_c']} in {hottest['city']} on {hottest['date'].date()}")
    print(f"  lowest daily minimum: {coldest['temp_min_c']} in {coldest['city']} on {coldest['date'].date()}")

    delhi = weather[weather["city"] == "Delhi"]["temp_mean_c"]
    print(f"  Delhi daily mean, lowest to highest: {delhi.min()} to {delhi.max()}")

    # How far apart the warmest and coolest months are in each city.
    monthly = weather.groupby(["city", "month"])["temp_mean_c"].mean().unstack()
    print(f"  Delhi January and June: {monthly.loc['Delhi', 1]:.1f} and {monthly.loc['Delhi', 6]:.1f}")
    swing = (monthly.max(axis=1) - monthly.min(axis=1)).sort_values()
    print(f"  smallest gap between warmest and coolest month: {swing.index[0]} {swing.iloc[0]:.1f}")
    print(f"  largest gap between warmest and coolest month: {swing.index[-1]} {swing.iloc[-1]:.1f}")

    print("\nRain (mm per year, average)")
    yearly_rain = (weather.groupby("city")["rain_mm"].sum() / years).sort_values()
    print(f"  driest city: {yearly_rain.index[0]} {yearly_rain.iloc[0]:.0f}")
    print(f"  wettest city: {yearly_rain.index[-1]} {yearly_rain.iloc[-1]:.0f}")

    monsoon = weather[weather["season"] == "Monsoon"].groupby("city")["rain_mm"].sum()
    share = (monsoon / weather.groupby("city")["rain_mm"].sum() * 100).sort_values()
    print(f"  share of rain that falls June to September, all cities: "
          f"{monsoon.sum() / weather['rain_mm'].sum() * 100:.0f}%")
    print(f"  lowest monsoon share: {share.index[0]} {share.iloc[0]:.0f}%")
    print(f"  highest monsoon share: {share.index[-1]} {share.iloc[-1]:.0f}%")

    late = weather[weather["month"] >= 10].groupby("city")["rain_mm"].sum()
    late_share = (late / weather.groupby("city")["rain_mm"].sum() * 100).sort_values(ascending=False)
    print(f"  most rain from October to December: {late_share.index[0]} {late_share.iloc[0]:.0f}%, "
          f"{late_share.index[1]} {late_share.iloc[1]:.0f}%")

    monthly_rain = weather.groupby(["city", "month"])["rain_mm"].sum() / years
    city, month = monthly_rain.idxmax()
    print(f"  wettest month on average: {city}, month {month}, {monthly_rain.max():.0f} mm")

    print("\nHumidity (%)")
    humidity = weather.groupby("season")["humidity_pct"].mean()
    for season in ["Winter", "Pre-monsoon", "Monsoon", "Post-monsoon"]:
        print(f"  {season}: {humidity[season]:.0f}")

    print("\nCorrelation between daily values, all cities")
    columns = ["temp_mean_c", "humidity_pct", "pressure_hpa", "wind_speed_kmh", "rain_mm"]
    print(weather[columns].corr().round(2).to_string())

    print("\nShare of days by weather type (%)")
    print((weather["weather"].value_counts(normalize=True) * 100).round(1))


if __name__ == "__main__":
    main()
