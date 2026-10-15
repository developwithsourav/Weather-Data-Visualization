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

    year_by_year(weather)
    rain_pattern(weather)
    pressure_and_humidity(weather)


def year_by_year(weather):
    """Figures for the year-on-year part of the report."""
    print("\nYear by year")
    yearly = weather.groupby("year")["temp_mean_c"].mean()
    print("  mean temperature, all cities:", {year: round(value, 2) for year, value in yearly.items()})

    warmest = weather.groupby(["year", "city"])["temp_mean_c"].mean().unstack().idxmax()
    print("  cities whose warmest year it was:", warmest.value_counts().sort_index().to_dict())

    hot = weather[weather["temp_max_c"] >= 45]
    print("  city-days at 45 °C or more:", hot.groupby("year").size().to_dict())
    may_2024 = hot[(hot["year"] == 2024) & (hot["month"] == 5)]
    print(f"  of those in May 2024: {len(may_2024)} city-days in {may_2024['city'].nunique()} cities")

    delhi = weather[(weather["city"] == "Delhi") & (weather["date"] == "2024-05-28")]
    print(f"  Delhi maximum on 2024-05-28: {delhi['temp_max_c'].iloc[0]}")

    monsoon = weather[weather["season"] == "Monsoon"].groupby(["year", "city"])["rain_mm"].sum().unstack()
    print("  monsoon rain, average of cities (mm):", monsoon.mean(axis=1).round(0).to_dict())
    print(f"  five-year average: {monsoon.mean(axis=1).mean():.0f}")
    compared = (monsoon.loc[2024] / monsoon.mean() * 100).sort_values()
    print(f"  2024 monsoon against each city's own average: from {compared.index[0]} "
          f"{compared.iloc[0]:.0f}% to {compared.index[-1]} {compared.iloc[-1]:.0f}%")
    print(f"  cities more than 20% above their own average in 2024: {(compared > 120).sum()}")
    print(f"  Guwahati 2024: {compared['Guwahati']:.0f}%")


def rain_pattern(weather):
    """How rain is spread over the year: a few big days or many small ones."""
    print("\nHow rain arrives")

    def wettest_ten_share(rain):
        return rain.nlargest(10).sum() / rain.sum() * 100

    share = weather.groupby(["city", "year"])["rain_mm"].apply(wettest_ten_share).groupby("city").mean()
    share = share.sort_values()
    print(f"  share of a year's rain on its 10 wettest days, average of cities: {share.mean():.0f}%")
    print(f"  lowest: {share.index[0]} {share.iloc[0]:.0f}%, highest: {share.index[-1]} {share.iloc[-1]:.0f}%")

    # A day counts as rainy when it gets 2.5 mm or more.
    years = weather["year"].nunique()
    rainy = (weather[weather["rain_mm"] >= 2.5].groupby("city").size() / years).sort_values()
    print(f"  rainy days a year: fewest {rainy.index[0]} {rainy.iloc[0]:.0f}, most {rainy.index[-1]} {rainy.iloc[-1]:.0f}")

    daily_range = (weather["temp_max_c"] - weather["temp_min_c"]).groupby(weather["city"]).mean().sort_values()
    print(f"  gap between day and night: smallest {daily_range.index[0]} {daily_range.iloc[0]:.1f} °C, "
          f"largest {daily_range.index[-1]} {daily_range.iloc[-1]:.1f} °C")


def pressure_and_humidity(weather):
    """Why temperature and pressure move in opposite directions."""
    print("\nPressure and humidity")
    pressure = weather.groupby("month")["pressure_hpa"].mean()
    print(f"  sea-level pressure, all cities: January {pressure[1]:.1f} hPa, July {pressure[7]:.1f} hPa")

    within = weather.groupby("city")[["temp_mean_c", "pressure_hpa"]].corr().xs("pressure_hpa", level=1)
    within = within["temp_mean_c"].sort_values()
    print(f"  temperature and pressure inside one city: from {within.index[0]} {within.iloc[0]:.2f} "
          f"to {within.index[-1]} {within.iloc[-1]:.2f}")

    humidity = weather.groupby(["city", "season"])["humidity_pct"].mean().unstack()
    print(f"  pre-monsoon humidity: Delhi {humidity.loc['Delhi', 'Pre-monsoon']:.0f}%, "
          f"Chennai {humidity.loc['Chennai', 'Pre-monsoon']:.0f}%")


if __name__ == "__main__":
    main()
