"""Test whether a weather column behaves like real weather.

Real weather has three habits that random numbers do not:

1. Memory. Today is close to yesterday, so the value on one day predicts the next.
2. Seasons. The month explains a large part of the variation.
3. Places differ. Some cities are hotter, wetter or more humid than others.

The first version of this project used a dataset whose humidity and pressure turned out to fail all
three tests. This script runs the same tests on that old data and on the current data.

Reads  data/processed/weather_clean.csv and data/first_version/*.csv
Writes data/processed/realism_check.csv and charts/11_realism_check.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_FILE = BASE_DIR / "data" / "processed" / "weather_clean.csv"
FIRST_VERSION_DIR = BASE_DIR / "data" / "first_version"
RESULT_FILE = BASE_DIR / "data" / "processed" / "realism_check.csv"
CHART_FILE = BASE_DIR / "charts" / "11_realism_check.png"

# A column must clear all three to look like real weather. Real columns in this project score far
# above these lines and random numbers score close to zero, so the exact values are not delicate.
MIN_MEMORY = 0.2
MIN_SEASON = 0.05
MIN_PLACE = 0.1


def realism_scores(table):
    """Score one variable laid out as one row per date and one column per city."""
    table = table.sort_index()
    months = pd.to_datetime(table.index).month

    memory, season = [], []
    for city in table.columns:
        values = table[city].astype(float)
        # Memory: correlation between each day and the day before.
        memory.append(values.autocorr(lag=1))
        # Season: share of the variation explained by the month of the year.
        monthly_mean = values.groupby(months).transform("mean")
        season.append(1 - (values - monthly_mean).var() / values.var())

    # Place: how far apart the city averages are, compared with the day-to-day spread inside a city.
    place = table.mean().std() / table.std().median()

    return {
        "memory": round(float(pd.Series(memory).median()), 3),
        "season": round(float(pd.Series(season).median()), 3),
        "place": round(float(place), 3),
    }


def verdict(scores):
    """Turn the three scores into a plain answer."""
    passed = [scores["memory"] >= MIN_MEMORY, scores["season"] >= MIN_SEASON, scores["place"] >= MIN_PLACE]
    if all(passed):
        return "looks real"
    if not any(passed):
        return "looks random"
    return "check by hand"


def main():
    rows = []

    first_version = {"temperature": "Temperature", "humidity": "Humidity", "pressure": "Pressure"}
    for file_name, label in first_version.items():
        table = pd.read_csv(FIRST_VERSION_DIR / f"{file_name}.csv", index_col="datetime")
        rows.append({"dataset": "First version", "variable": label, **realism_scores(table)})

    weather = pd.read_csv(CLEAN_FILE)
    current = {"temp_mean_c": "Temperature", "humidity_pct": "Humidity", "pressure_hpa": "Pressure",
               "wind_speed_kmh": "Wind speed", "rain_mm": "Rain"}
    for column, label in current.items():
        table = weather.pivot(index="date", columns="city", values=column)
        rows.append({"dataset": "Current (Open-Meteo)", "variable": label, **realism_scores(table)})

    result = pd.DataFrame(rows)
    result["verdict"] = result.apply(verdict, axis=1)
    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(RESULT_FILE, index=False)
    print(result.to_string(index=False))

    draw_chart(result)
    print(f"Saved {RESULT_FILE.relative_to(BASE_DIR)} and {CHART_FILE.relative_to(BASE_DIR)}")


def draw_chart(result):
    """Bar chart of the memory score, first version against current data."""
    shared = ["Temperature", "Humidity", "Pressure"]
    pivot = result[result["variable"].isin(shared)].pivot(index="variable", columns="dataset", values="memory")
    pivot = pivot.loc[shared[::-1]]

    background, text, muted, grid = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    colours = {"First version": "#eb6834", "Current (Open-Meteo)": "#2a78d6"}

    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=background)
    ax.set_facecolor(background)
    height = 0.36
    for offset, dataset in [(height / 2 + 0.02, "First version"), (-height / 2 - 0.02, "Current (Open-Meteo)")]:
        positions = [index + offset for index in range(len(pivot))]
        bars = ax.barh(positions, pivot[dataset], height=height, color=colours[dataset], label=dataset)
        # abs() on values that round to zero avoids printing "-0.00".
        labels = [f"{abs(value):.2f}" if abs(value) < 0.005 else f"{value:.2f}" for value in pivot[dataset]]
        ax.bar_label(bars, labels=labels, padding=4, color=text)

    ax.axvline(MIN_MEMORY, color=muted, linewidth=1, linestyle="--")
    ax.set_ylim(-0.7, len(pivot) - 0.25)
    ax.annotate("pass line", (MIN_MEMORY, len(pivot) - 0.38), xytext=(4, 0), textcoords="offset points",
                color=muted, va="center")
    ax.set_yticks(range(len(pivot)), pivot.index, color=text)
    ax.set_xlim(-0.05, 1.1)
    ax.set_xlabel("Day-to-day memory (correlation of each day with the day before)", color=muted)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncols=2)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(grid)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(length=0, colors=muted)
    ax.grid(axis="x", color=grid, linewidth=0.8)
    ax.set_axisbelow(True)

    fig.text(0.015, 0.97, "Catching made-up data", ha="left", va="top", fontsize=14, fontweight="bold", color=text)
    fig.text(0.015, 0.915, "Real weather remembers yesterday. The first version's humidity and pressure did not",
             ha="left", va="top", fontsize=10, color=muted)
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    CHART_FILE.parent.mkdir(exist_ok=True)
    fig.savefig(CHART_FILE, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
