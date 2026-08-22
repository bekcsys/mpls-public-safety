Build the first working version of **mpls-public-safety** using Python and Dagster.

Focus ONLY on:

1. ingesting Minneapolis public-safety incident data from the official API
2. basic processing/cleaning
3. automated scheduled ingestion with Dagster

## Requirements

### API ingestion

Create a reusable Python API client that:

- calls the official Minneapolis public-safety incident API
- supports pagination
- handles request failures and timeouts
- returns records as Python dictionaries
- logs how many records were retrieved

### Basic processing

Create simple processing that:

- selects useful incident fields
- converts timestamps to proper datetime values
- standardizes column names
- removes obvious duplicate records
- handles missing values without crashing
- keeps latitude/longitude fields if available

Keep transformations minimal. Do not build analytical models yet.

### Dagster

Create Dagster assets similar to:

```text
raw_incidents
      ↓
processed_incidents
```

`raw_incidents`

- retrieves data from the API

`processed_incidents`

- performs the basic cleaning described above

Add useful Dagster metadata such as:

- number of records ingested
- number of processed records
- ingestion timestamp

### Scheduled ingestion

Create a Dagster schedule that runs the ingestion pipeline automatically.

Use a reasonable schedule such as:

```text
every 6 hours
```

Keep the scheduling configuration easy to modify.

### Storage

For now, persist data locally using Parquet files.

Example:

```text
data/
├── raw/
│   └── incidents.parquet
└── processed/
    └── incidents.parquet
```

Do not add PostgreSQL, AWS, dbt, dashboards, RAG, LLMs, or other infrastructure yet.

## Project quality

Use:

- Python type hints
- clear module separation
- logging
- environment variables for configurable API settings
- `.gitignore`
- `requirements.txt` or `pyproject.toml`

Keep the project small and understandable.

## Success criteria

I should be able to run Dagster locally, materialize the assets, and see:

```text
Minneapolis API
      ↓
raw_incidents
      ↓
processed_incidents
```

I should also be able to enable the Dagster schedule and have the ingestion run automatically every 6 hours.

Stop after this is working. Do not expand the project beyond ingestion, basic processing, and scheduled orchestration.
