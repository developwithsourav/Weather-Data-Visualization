"""Draw the charts used in the README and the report.

Reads  data/processed/weather_clean.csv
Writes ten PNG files to charts/
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_FILE = BASE_DIR / "data" / "processed" / "weather_clean.csv"
CHARTS_DIR = BASE_DIR / "charts"

# Colours. The four series colours stay distinguishable for colour-blind readers.
BACKGROUND = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"

# Light to dark blue for "how much", and blue-grey-red for "negative to positive".
BLUES = LinearSegmentedColormap.from_list("blues", ["#eef4fd", "#9ec5f4", "#2a78d6", "#0d366b"])
BLUE_RED = LinearSegmentedColormap.from_list("blue_red", ["#2a78d6", "#f0efec", "#e34948"])

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

plt.rcParams.update({
    "figure.facecolor": BACKGROUND,
    "axes.facecolor": BACKGROUND,
    "savefig.facecolor": BACKGROUND,
    "text.color": TEXT,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": GRID,
    "font.size": 10,
})


def finish(fig, ax, title, subtitle, filename, grid_axis="y"):
    """Add the title, tidy the frame and save the chart."""
    fig.text(0.015, 0.97, title, ha="left", va="top", fontsize=14, fontweight="bold")
    fig.text(0.015, 0.925, subtitle, ha="left", va="top", fontsize=10, color=MUTED)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    ax.tick_params(length=0)
    # Leave the top strip of the figure free for the title and subtitle.
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(CHARTS_DIR / filename, dpi=150)
    plt.close(fig)
    print(f"Saved charts/{filename}")


def monthly_temperature(weather):
    """Line chart: how temperature moves through the year in four different climates."""
    cities = {"Delhi": BLUE, "Mumbai": ORANGE, "Bengaluru": AQUA, "Srinagar": YELLOW}
    monthly = weather.groupby(["city", "month"])["temp_mean_c"].mean().unstack("city")

    fig, ax = plt.subplots(figsize=(9, 5))
    for city, colour in cities.items():
        ax.plot(MONTH_NAMES, monthly[city], color=colour, linewidth=2, label=city)
        # Name each line at its right-hand end so colour is not the only clue.
        ax.annotate(city, (11, monthly[city].iloc[-1]), xytext=(8, 0),
                    textcoords="offset points", va="center", color=TEXT)
    ax.set_ylabel("Mean temperature (°C)")
    ax.set_xlim(-0.3, 12.4)
    ax.legend(frameon=False, ncols=4, loc="lower center")
    finish(fig, ax, "Temperature through the year",
           "Average of daily mean temperature for each month, 2021 to 2025",
           "1_monthly_temperature.png")


def rain_by_month(weather):
    """Heatmap: average rain in each month for every city."""
    years = weather["year"].nunique()
    rain = weather.groupby(["city", "month"])["rain_mm"].sum().unstack("month") / years
    rain = rain.loc[rain.sum(axis=1).sort_values(ascending=False).index]
    rain.columns = MONTH_NAMES

    fig, ax = plt.subplots(figsize=(9, 9))
    sns.heatmap(rain, cmap=BLUES, linewidths=1, linecolor=BACKGROUND, ax=ax,
                cbar_kws={"label": "Rain (mm per month)", "shrink": 0.6})
    ax.set_xlabel("")
    ax.set_ylabel("")
    finish(fig, ax, "When the rain falls",
           "Average rain per month, 2021 to 2025. Cities sorted from wettest to driest",
           "2_rain_by_month.png", grid_axis=None)


def temperature_by_city(weather):
    """Box plot: the spread of daily temperature in every city."""
    order = weather.groupby("city")["temp_mean_c"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(9, 9))
    sns.boxplot(data=weather, x="temp_mean_c", y="city", order=order, color=BLUE,
                width=0.6, linewidth=1, fliersize=1.5, ax=ax,
                boxprops={"edgecolor": BACKGROUND}, medianprops={"color": BACKGROUND, "linewidth": 2},
                whiskerprops={"color": MUTED}, capprops={"color": MUTED},
                flierprops={"markerfacecolor": MUTED, "markeredgecolor": MUTED})
    ax.set_xlabel("Daily mean temperature (°C)")
    ax.set_ylabel("")
    finish(fig, ax, "Temperature range by city",
           "Each box holds the middle half of all days, 2021 to 2025. White line is the median",
           "3_temperature_by_city.png", grid_axis="x")


def temperature_histogram(weather):
    """Histogram: how often each temperature occurs across all cities."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(weather["temp_mean_c"], bins=40, color=BLUE, edgecolor=BACKGROUND, linewidth=1)
    ax.set_xlabel("Daily mean temperature (°C)")
    ax.set_ylabel("Number of city-days")
    finish(fig, ax, "Distribution of daily temperature",
           f"All {weather['city'].nunique()} cities together, 2021 to 2025",
           "4_temperature_histogram.png")


def humidity_vs_temperature(weather):
    """Scatter plot: humidity against temperature for three contrasting cities."""
    cities = {"Delhi": BLUE, "Chennai": ORANGE, "Srinagar": AQUA}

    fig, ax = plt.subplots(figsize=(9, 6))
    for city, colour in cities.items():
        days = weather[weather["city"] == city]
        ax.scatter(days["temp_mean_c"], days["humidity_pct"], s=10, color=colour,
                   alpha=0.35, linewidths=0, label=city)
    ax.set_xlabel("Daily mean temperature (°C)")
    ax.set_ylabel("Mean relative humidity (%)")
    legend = ax.legend(frameon=False, markerscale=2.5, loc="lower left")
    for handle in legend.legend_handles:
        handle.set_alpha(1)
    finish(fig, ax, "Humidity against temperature",
           "One dot per day, 2021 to 2025", "5_humidity_vs_temperature.png", grid_axis="both")


def weather_types(weather):
    """Bar chart: share of days with each type of weather."""
    share = (weather["weather"].value_counts(normalize=True) * 100).sort_values()

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(share.index, share.values, color=BLUE, height=0.7)
    ax.bar_label(bars, labels=[f"{value:.1f}%" for value in share.values], padding=4, color=TEXT)
    ax.set_xlabel("Share of all city-days (%)")
    ax.set_xlim(0, share.max() * 1.12)
    finish(fig, ax, "What the weather was",
           "Most severe weather type recorded each day, all cities, 2021 to 2025",
           "6_weather_types.png", grid_axis="x")


def correlation(weather):
    """Heatmap: how the daily values move together."""
    labels = {
        "temp_mean_c": "Temperature",
        "humidity_pct": "Humidity",
        "pressure_hpa": "Pressure",
        "wind_speed_kmh": "Wind speed",
        "rain_mm": "Rain",
    }
    table = weather[list(labels)].rename(columns=labels).corr()

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(table, cmap=BLUE_RED, vmin=-1, vmax=1, annot=True, fmt=".2f",
                linewidths=2, linecolor=BACKGROUND, square=True, ax=ax,
                annot_kws={"color": TEXT}, cbar_kws={"label": "Correlation", "shrink": 0.7})
    finish(fig, ax, "How the daily values move together",
           "Correlation across all cities and days, 2021 to 2025",
           "7_correlation.png", grid_axis=None)


def yearly_temperature(weather):
    """Line chart: average temperature of all cities, one point per year."""
    yearly = weather.groupby("year")["temp_mean_c"].mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(yearly.index, yearly.values, color=BLUE, linewidth=2, marker="o", markersize=8)
    for year, value in yearly.items():
        ax.annotate(f"{value:.2f}", (year, value), xytext=(0, 10), textcoords="offset points",
                    ha="center", color=TEXT)
    ax.set_xticks(yearly.index)
    ax.set_ylabel("Mean temperature (°C)")
    ax.set_ylim(yearly.min() - 0.3, yearly.max() + 0.3)
    finish(fig, ax, "Average temperature rose every year",
           "Average daily mean temperature across all 30 cities. The axis does not start at zero",
           "8_yearly_temperature.png")


def heat_days(weather):
    """Bar chart: how many city-days reached 45 °C in each year."""
    hot = weather[weather["temp_max_c"] >= 45].groupby("year").size()
    hot = hot.reindex(sorted(weather["year"].unique()), fill_value=0)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(hot.index.astype(str), hot.values, color=BLUE, width=0.6)
    ax.bar_label(bars, padding=4, color=TEXT)
    ax.set_ylabel("City-days with a maximum of 45 °C or more")
    ax.set_ylim(0, hot.max() * 1.15)
    finish(fig, ax, "The 2024 heatwave",
           "Days when the maximum reached 45 °C, counted across all 30 cities",
           "9_heat_days.png")


def monsoon_by_year(weather):
    """Bar chart: June to September rain each year, averaged over the cities."""
    monsoon = weather[weather["season"] == "Monsoon"]
    by_year = monsoon.groupby(["year", "city"])["rain_mm"].sum().groupby("year").mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(by_year.index.astype(str), by_year.values, color=BLUE, width=0.6)
    # Values sit inside the top of each bar so they never collide with the average line.
    ax.bar_label(bars, labels=[f"{value:.0f}" for value in by_year.values], padding=-18,
                 color=BACKGROUND, fontweight="bold")
    ax.axhline(by_year.mean(), color=MUTED, linewidth=1, linestyle="--")
    ax.annotate(f"5-year average {by_year.mean():.0f} mm", (-0.45, by_year.mean()), xytext=(0, 6),
                textcoords="offset points", ha="left", color=MUTED)
    ax.set_ylabel("Rain, June to September (mm)")
    ax.set_ylim(0, by_year.max() * 1.15)
    finish(fig, ax, "Monsoon rain by year",
           "Rain from June to September, averaged over the 30 cities",
           "10_monsoon_by_year.png")


def main():
    weather = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
    CHARTS_DIR.mkdir(exist_ok=True)

    monthly_temperature(weather)
    rain_by_month(weather)
    temperature_by_city(weather)
    temperature_histogram(weather)
    humidity_vs_temperature(weather)
    weather_types(weather)
    correlation(weather)
    yearly_temperature(weather)
    heat_days(weather)
    monsoon_by_year(weather)


if __name__ == "__main__":
    main()
