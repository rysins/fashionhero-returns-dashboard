# FashionHero Workspace

This repository contains two coordinated app surfaces:

## 1. Storefront Preview (`Next.js`)

Local copy of the FashionHero storefront prepared for collaborative development and preview sharing.

### Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run test`

### Storefront scope

- `/`
- `/about`
- `/collections/[slug]`
- `/products/[slug]`
- `/wishlist`
- `/account/login`

The storefront runs on local mock data and now includes a preview intervention layer:

- soft penalty preview for heavy returners
- dynamic commission preview for risky sellers
- ranking boost for low-return products

Use the floating `Preview Scenarios` panel in the UI to toggle scenarios and adjust the buyer preview state.

## 2. Margin & Returns Dashboard (`Streamlit`)

Internal dashboard for conversations with Maja, Ela and Ola about:

- where FashionHero loses money
- which user, seller and category segments are toxic
- how preview interventions may affect margin and GMV

The dashboard lives in [`dashboard/`](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard) and runs on a local SQLite runtime database built from CSV export fixtures plus deterministic synthetic transactions.

### Local run

```bash
pip install -r dashboard/requirements.txt
python -m dashboard.pipeline
python -m dashboard.validate_dashboard
streamlit run dashboard/app.py
```

### Daily pipeline

- source adapter today: `CSV`
- scheduler: GitHub Actions
- workflow: `.github/workflows/dashboard-refresh.yml`
- outputs:
  - `dashboard/data/fashionhero_dashboard.sqlite`
  - `dashboard/data/pipeline_manifest.json`

### Real export handoff

The concrete runbook for replacing demo seeds with real FashionHero CSV exports is in [dashboard/REAL_EXPORTS.md](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/REAL_EXPORTS.md). It documents:

- required file names
- required columns
- mapping from FashionHero source tables/views
- manual and GitHub Actions refresh flow
- common data-shape failures

### Streamlit Community Cloud

Use `dashboard/app.py` as the entrypoint file and keep `dashboard/requirements.txt` in the repo.
