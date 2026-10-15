# What could come next

Ideas for taking the project further, grouped by size. Each one says what it would add and what it would show about the work. None of them is started.

## The three we would do first

| Idea | Why it matters |
|---|---|
| Measure the model against weather stations | The biggest open question in this project is how far the model's numbers sit from real thermometers. We have one comparison (Delhi, 28 May 2024). Station records from IMD or NOAA's GHCN-Daily for each city would give the gap for every city and every day, and say where the data can and cannot be trusted. |
| Refresh the data every month | A scheduled GitHub Actions run would fetch the newest month, run the same checks and tests, and republish the report. The pipeline would keep itself current instead of being a one-off. |
| Make the realism test a reusable tool | The test that caught the made-up humidity works on any time series laid out by date and place. As a small package with its own tests for more failure types (shuffled days, copied cities, constant columns), it becomes useful outside this project. |

## Small steps

- Store the data as Parquet and query it with DuckDB. The files would be smaller, and types would survive between steps instead of being re-read from text.
- Replace the hand-written checks with a schema library such as pandera, so the rules sit in one declared schema.
- Add the remaining two charts (temperature histogram and weather types) to the report, or drop them.
- Rebuild the Tableau dashboard from the first version on the new data, so the Tableau skills show again.

## Bigger analysis

- A 30-year baseline. Download 1991 to 2020 from the same API and compare each year with that normal, as IMD does. Our percentages would then be directly comparable with IMD's.
- Heat stress. Combine temperature and humidity into a heat index or wet-bulb temperature. Chennai's humid heat and Delhi's dry heat would then be compared on the measure that matters for health.
- Monsoon onset. Detect the start and end of the rainy season in each city from daily rain, and compare the dates with the onset dates IMD announces.
- Extreme rain indices. Measure the heaviest day of each year and the share of rain from very wet days, using the standard ETCCDI definitions. This turns the "a third of the rain falls on ten days" finding into a formal measure.
- Wider coverage. Add Kerala, the Himalayan states and the north-east, which the current 30 cities leave out.

## Larger builds

- A small API. Serve city data and the realism test over HTTP with FastAPI, so another program can ask "is this column real?" and get an answer.
- A heatwave model. Predict the number of 45 °C days in the coming week and judge it against the simplest baseline, which assumes next week looks like this week.
- A map. Show all 30 cities on a map in the report, coloured by whichever measure the reader picks.
