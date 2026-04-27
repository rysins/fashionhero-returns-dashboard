# FashionHero Margin Dashboard

Streamlit dashboard focused on margin leakage, return-risk segments and preview interventions for FashionHero.

## Runtime shape

- `app.py` - Streamlit business dashboard v2
- `pipeline.py` - CSV ingest, normalization, aggregate building and SQLite publishing
- `build_database.py` - compatibility wrapper for local rebuilds
- `loaders.py` - runtime DB loaders with schema validation
- `logic.py` - metrics, drill-downs, migrations and intervention simulations
- `data/fashionhero_dashboard.sqlite` - runtime database consumed by Streamlit
- `data/pipeline_manifest.json` - latest pipeline run manifest
- `seeds/` - CSV export fixtures used as the current source adapter
- `sql/` - SQL-ready contracts for future warehouse integration

## Local run

From the repository root:

```bash
pip install -r dashboard/requirements.txt
python -m dashboard.pipeline
python -m dashboard.validate_dashboard
streamlit run dashboard/app.py
```

## Streamlit Community Cloud

- Repository root: this repo
- Entry point: `dashboard/app.py`
- Dependency file: `dashboard/requirements.txt`

The app reads only from the generated SQLite runtime database. It does not require secrets for the current mock/CSV-based phase.

## Daily refresh

- Workflow: `.github/workflows/dashboard-refresh.yml`
- Triggers:
  - scheduled daily run
  - manual `workflow_dispatch`
- Output:
  - rebuilt `dashboard/data/fashionhero_dashboard.sqlite`
  - rebuilt `dashboard/data/pipeline_manifest.json`

## Real exports

The operational runbook for replacing demo seeds with real FashionHero exports is documented in [REAL_EXPORTS.md](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/REAL_EXPORTS.md).

Short version:

1. prepare five CSV files with the expected names and columns,
2. place them in a dedicated source directory such as `dashboard/imports/live/`,
3. run `run_pipeline(source_dir=Path("dashboard/imports/live"))`,
4. validate with `python -m dashboard.validate_dashboard`,
5. publish the rebuilt SQLite database and manifest.

## Current assumptions

- First real pipeline version is `CSV export -> normalize -> aggregate -> publish SQLite`
- Streamlit stays read-only against the published runtime DB
- Scenario outputs are heuristic estimates and should be treated as directional decision support
