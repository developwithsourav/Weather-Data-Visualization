# How the data flows

This page follows the data from the weather API to the published report. It has two data flow diagrams, a list of the files that hold data between steps, the checks that guard each step, and a dictionary of every column.

## Level 0: the whole system

The project takes data from two sources, checks and analyses it, and hands four things to the reader. IMD reports are read by hand and quoted in the text; no code downloads them.

```mermaid
flowchart LR
  API["Open-Meteo<br/>Historical Weather API"]:::external
  OLD["First version<br/>dataset, May 2025"]:::external
  IMD["IMD reports and<br/>press releases"]:::external
  READER["Reader<br/>browser or GitHub"]:::external
  SYS(("Weather analysis<br/>pipeline")):::process

  API -- "daily weather for 30 cities, JSON" --> SYS
  OLD -- "temperature, humidity and pressure, CSV" --> SYS
  IMD -. "official figures, compared by hand" .-> SYS
  SYS -- "report page, city lookup, charts, notebook, dataset" --> READER

  classDef external fill:#f1efea,stroke:#6b6a66,color:#1d1d1b
  classDef process fill:#dfe7f1,stroke:#1f4e8c,color:#1d1d1b
```

## Level 1: inside the pipeline

Rounded boxes are processes, cylinders are files that hold data between steps, and grey boxes are outside the project. `run_all.py` runs processes 2 to 6 in order, then the tests.

```mermaid
flowchart TB
  API["Open-Meteo API"]:::external
  OLD["First version dataset"]:::external
  READER["Reader"]:::external

  P1(["1 Fetch<br/>fetch_data.py"]):::process
  P2(["2 Check and clean<br/>clean_data.py"]):::process
  P3(["3 Draw charts<br/>make_charts.py"]):::process
  P4(["4 Realism test<br/>realism_check.py"]):::process
  P5(["5 Summarise<br/>summary.py"]):::process
  P6(["6 Build site<br/>build_site.py"]):::process
  P7(["7 Publish<br/>GitHub Actions and Pages"]):::process
  P8(["8 Explore<br/>analysis.ipynb"]):::process
  STOP["Pipeline stops<br/>with the failed check"]:::stop

  D0[("D0 cities.csv")]:::store
  D1[("D1 raw/weather_daily.csv")]:::store
  D2[("D2 processed/weather_clean.csv")]:::store
  D3[("D3 charts/*.png")]:::store
  D4[("D4 processed/realism_check.csv")]:::store
  D5[("D5 first_version/*.csv")]:::store
  D6[("D6 _site/ page, data.json, charts")]:::store

  D0 -- "city, latitude, longitude" --> P1
  API -- "daily JSON, one request per city" --> P1
  P1 -- "54,780 rows" --> D1
  D1 --> P2
  D0 -- "coordinates" --> P2
  P2 -- "rows that pass all 10 checks" --> D2
  P2 -. "any check fails" .-> STOP
  D2 --> P3
  P3 -- "charts 1 to 10" --> D3
  OLD --> D5
  D2 --> P4
  D5 --> P4
  P4 -- "scores and verdicts" --> D4
  P4 -- "chart 11" --> D3
  D2 --> P5
  P5 -- "every figure quoted in the README and report" --> READER
  D2 --> P6
  D3 --> P6
  D4 --> P6
  P6 --> D6
  D6 --> P7
  P7 -- "report page" --> READER
  D2 --> P8
  D5 --> P8
  P8 -- "code, charts and observations" --> READER

  classDef external fill:#f1efea,stroke:#6b6a66,color:#1d1d1b
  classDef process fill:#dfe7f1,stroke:#1f4e8c,color:#1d1d1b
  classDef store fill:#fcfcfb,stroke:#1f4e8c,color:#1d1d1b
  classDef stop fill:#fbe9e7,stroke:#d03b3b,color:#1d1d1b
```

## Processes

| # | Process | Reads | Writes | What can stop it |
|---|---|---|---|---|
| 1 | Fetch | D0, Open-Meteo API | D1 | Five failed attempts for one city. A rerun keeps the cities already saved |
| 2 | Check and clean | D1, D0 | D2 | Any of the 10 data checks below |
| 3 | Draw charts | D2 | D3 | A missing D2 |
| 4 | Realism test | D2, D5 | D4, D3 | A missing D2 or D5 |
| 5 | Summarise | D2 | printed figures | A missing D2 |
| 6 | Build site | D2, D3, D4, `site/index.html` | D6 | A missing D2 |
| 7 | Publish | D6 | the live page | Any earlier step or test failing in GitHub Actions |
| 8 | Explore | D2, D5 | the notebook's outputs | Nothing; it is run by hand |

## Data stores

| Store | File | Rows | Kept in git | Made by |
|---|---|---|---|---|
| D0 | `data/cities.csv` | 30 | yes | written by hand from the first version's city list |
| D1 | `data/raw/weather_daily.csv` | 54,780 | yes, so nobody has to download | process 1 |
| D2 | `data/processed/weather_clean.csv` | 54,780 | yes, so Tableau users can open it | process 2 |
| D3 | `charts/*.png` | 11 files | yes, so the README shows them | processes 3 and 4 |
| D4 | `data/processed/realism_check.csv` | 8 | yes | process 4 |
| D5 | `data/first_version/*.csv` | 3,652 days each | yes, so the realism test can be repeated | copied from the first version |
| D6 | `_site/` | 1 page, 1 JSON file, 11 charts | no, rebuilt every run | process 6 |

## Checks in process 2

The cleaning script counts the rows that break each rule. Any count above zero stops the pipeline before a chart is drawn.

| Check | Rule |
|---|---|
| Missing values | no empty cell in any column |
| Duplicates | one row per city per date |
| Complete calendar | every city has every day from the first date to the last |
| Temperature order | minimum is not above maximum |
| Mean temperature | mean lies between minimum and maximum |
| Humidity | between 0 and 100% |
| Rain | never negative |
| Pressure | between 900 and 1,100 hPa |
| Wind direction | between 0 and 360 degrees |
| Weather code | every code has a label |

## Data dictionary

Columns of `data/processed/weather_clean.csv`, one row per city per day.

| Column | Type | Unit | Meaning | From |
|---|---|---|---|---|
| `city` | text | | City name | `cities.csv` |
| `date` | date | | Day, Indian Standard Time | API `time` |
| `temp_mean_c` | number | °C | Mean air temperature at 2 m | API `temperature_2m_mean` |
| `temp_max_c` | number | °C | Highest temperature of the day | API `temperature_2m_max` |
| `temp_min_c` | number | °C | Lowest temperature of the day | API `temperature_2m_min` |
| `humidity_pct` | whole number | % | Mean relative humidity at 2 m | API `relative_humidity_2m_mean` |
| `pressure_hpa` | number | hPa | Mean pressure reduced to sea level | API `pressure_msl_mean` |
| `wind_speed_kmh` | number | km/h | Mean wind speed at 10 m | API `wind_speed_10m_mean` |
| `wind_direction_deg` | whole number | degrees | Dominant wind direction at 10 m | API `wind_direction_10m_dominant` |
| `rain_mm` | number | mm | Total precipitation | API `precipitation_sum` |
| `weather_code` | whole number | WMO code | Most severe weather of the day | API `weather_code` |
| `year` | whole number | | Calendar year | from `date` |
| `month` | whole number | | 1 to 12 | from `date` |
| `season` | text | | Winter, Pre-monsoon, Monsoon or Post-monsoon, as IMD defines them | from `month` |
| `weather` | text | | Readable label for `weather_code`, such as Drizzle | from `weather_code` |
| `latitude` | number | degrees | City latitude | `cities.csv` |
| `longitude` | number | degrees | City longitude | `cities.csv` |
