# FashionHero Workspace

This repository now contains two separate app surfaces for FashionHero:

## 1. Storefront Preview (`Next.js`)

Local copy of the FashionHero storefront prepared for collaborative development and Vercel preview deployments.

### Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run test`

### Storefront Scope

- `/`
- `/about`
- `/collections/[slug]`
- `/products/[slug]`
- `/wishlist`
- `/account/login`

The storefront runs entirely on local mock data and local assets. No external API or auth backend is required.

## 2. Margin & Returns Dashboard (`Streamlit`)

Internal MVP dashboard for conversations with Maja, Ela and Ola about:

- where FashionHero loses money
- which user and seller segments are toxic
- how simple interventions may affect margin and GMV

The dashboard lives in [`dashboard/`](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard) and runs on a local SQLite database seeded from curated CSV fixtures plus deterministic synthetic transaction data.

### Local run

```bash
pip install -r dashboard/requirements.txt
python -m dashboard.build_database
streamlit run dashboard/app.py
```

### Streamlit Community Cloud

Use `dashboard/app.py` as the entrypoint file. Keep `dashboard/requirements.txt` in the repo and configure the app from the repository root.
