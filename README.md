# mpls-public-safety

![alt text](image.png)

Dagster pipeline that pulls Minneapolis police incidents from the official Open Data API, cleans them, and writes Parquet locally.

Flow: `raw_incidents` → `processed_incidents`. Schedule: every 6 hours.

```bash
make setup
make materialize
```

UI: http://127.0.0.1:3000. Enable the 6-hour schedule there. Data lands in `data/raw` and `data/processed`.

`make down` stops containers. `make logs` tails output. API settings live in `.env`.
