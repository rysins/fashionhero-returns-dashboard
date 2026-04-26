# FashionHero Margin Dashboard

Streamlit MVP for diagnosing margin erosion, toxic return segments and likely impact of simple interventions.

## Files

- `app.py` - Streamlit entrypoint
- `build_database.py` - SQLite builder and synthetic transaction generator
- `config.py` - thresholds, labels and visual constants
- `loaders.py` - SQLite loaders and schema validation
- `logic.py` - segmentation, summaries, migrations and simulation
- `data/` - SQLite runtime database
- `seeds/` - source CSV fixtures used to rebuild the database
- `sql/` - SQL-ready specs for future real-data integration

## Local run

From the repository root:

```bash
pip install -r dashboard/requirements.txt
python -m dashboard.build_database
streamlit run dashboard/app.py
python -m dashboard.validate_dashboard
```

## Streamlit Community Cloud

- Repository: this repo
- Branch: `main`
- Entry point: `dashboard/app.py`
- Dependency file: `dashboard/requirements.txt`

Configure the app from the repository root and point Streamlit Community Cloud to `dashboard/app.py`.

## Model assumptions

- Runtime data source is SQLite. Seed CSVs are kept only to rebuild the database deterministically.
- Synthetic orders expand transaction-level test coverage while staying consistent with seeded user and seller profiles.
- Data is mock-first and meant to sell the decision problem before real data is connected.
- Thresholds are explicit in `config.py` and are not hardcoded in visual components.
- Simulation output is heuristic and should be treated as directional, not forecast-grade.
