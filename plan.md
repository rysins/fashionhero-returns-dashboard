# Plan: Kopia FashionHero rozwijana w Next.js z workflow GitHub + Vercel

## Summary
Zbudować nową aplikację `Next.js` w tym repo jako wierną wizualnie kopię obecnego storefrontu `fashionhero.aiproductheroes.pl`, ale od początku osadzić development w workflow `GitHub -> Vercel`. Pierwsza iteracja obejmuje tylko storefront i ma działać lokalnie oraz na publicznych preview deploymentach Vercel, tak aby można było udostępniać linki innym osobom przed właściwym wdrożeniem.

## Implementation Changes
- Zainicjalizować aplikację `Next.js` z `App Router`, `TypeScript` i stylingiem zgodnym z obecną platformą.
- Odtworzyć publiczne route'y storefrontu:
  - `/`
  - `/about`
  - `/collections/[slug]`
  - `/products/[slug]`
  - `/wishlist`
  - `/account/login`
- Oprzeć całość na lokalnych mockach danych w repo:
  - produkty
  - kolekcje
  - sellerzy
  - treści marketingowe
  - konfiguracja nawigacji i footerów
- Skopiować assety z live site do lokalnego `public/`, tak aby runtime nie zależał od zewnętrznej domeny.
- Odtworzyć obecne interakcje storefrontowe jako lokalny stan klienta:
  - mobile menu
  - hero carousel
  - listing filters/sort
  - warianty `color/size`
  - wishlist
  - cart drawer
  - login shell bez backendowej autoryzacji
- Uporządkować kod pod późniejszą rozbudowę marketplace:
  - osobne modele danych dla `Product`, `Seller`, `Collection`
  - seller metadata trzymane niezależnie od komponentów UI
  - komponenty wspólne dla nav, listingów, PDP i bloków marketingowych

## Vercel Workflow
- Repo źródłowe utrzymywać w `GitHub` i podłączyć projekt do `Vercel`.
- Przyjąć model branchy:
  - `main` jako główna gałąź z aktualnym środowiskiem bazowym
  - każda gałąź robocza daje osobny preview deployment w Vercel
- Udostępniać innym osobom publiczne preview linki z Vercel, bez dodatkowej ochrony dostępu na starcie.
- Traktować deployment z `main` jako główne współdzielone środowisko robocze, ale nie jako docelową produkcję.
- Nie planować jeszcze custom domain ani rozbudowanej konfiguracji środowisk; zostawić to na etap po zbudowaniu pierwszej kopii.
- Przygotować projekt tak, by nie wymagał sekretów ani zewnętrznego backendu w v1, co upraszcza preview deploymenty i onboarding.

## Public APIs / Interfaces / Types
- Wprowadzić lokalne typy domenowe:
  - `Product`
  - `ProductVariant`
  - `Seller`
  - `Collection`
  - `ReviewSummary`
  - `CartItem`
  - `WishlistItem`
- Ustalić kontrakt v1:
  - listing i PDP czytają tylko z lokalnych danych
  - wishlist i cart są lokalne, najlepiej przez `localStorage`
  - login nie komunikuje się z backendem
  - search może pozostać wyłącznie UI shellem, jeśli nie zostanie objęty pierwszą iteracją

## Test Plan
- Smoke testy dla wszystkich głównych route'ów lokalnie i na preview deployment.
- Testy przejść:
  - homepage -> collection
  - collection -> product
  - PDP variant switching
  - wishlist add/remove
  - cart drawer open/close
- Testy listingu:
  - filtrowanie
  - sortowanie
  - poprawna liczba wyników dla kolekcji
- Testy regresji deploymentu:
  - build przechodzi lokalnie i na Vercel
  - aplikacja działa bez fetchy do `fashionhero.aiproductheroes.pl`
  - brak brakujących assetów po lokalizacji plików
- Testy responsywności dla homepage, listingów i PDP na mobile i desktop.

## Assumptions And Defaults
- Technologia bazowa: `Next.js`.
- Zakres pierwszego etapu: storefront only.
- Priorytet v1: wysoka wierność wizualna obecnej platformie.
- Repo będzie utrzymywane w `GitHub`, a development udostępniany przez publiczne preview deploymenty `Vercel`.
- `main` publikuje główne współdzielone środowisko, a branch previews służą do review i testów.
- Custom domain, auth, backend marketplace, seller panel i checkout produkcyjny są poza v1.
- Plan ma być dalej aktualizowany w tym pliku.

## Status
- 2026-04-26: v1 storefront implemented in `Next.js` with local mock data, local assets, wishlist/cart state in `localStorage`, and the required public routes.
- 2026-04-26: local verification completed with `npm run test` and `npm run build`.
- 2026-04-27: repository pushed to GitHub at `origin/main` and ready for Vercel import.
- 2026-04-27: `Next.js` upgraded to `15.2.8` after Vercel reported a security advisory on the earlier `15.2.x` build.
- 2026-04-27: added a separate `dashboard/` workstream for the Streamlit MVP focused on margin, return-rate diagnosis and heuristic simulation.
- 2026-04-27: implemented the `Streamlit` MVP with mock CSV datasets, SQL-ready dataset specs, explicit segmentation logic and a heuristic top-returner simulation.
- 2026-04-27: local verification completed for the dashboard through `python -m dashboard.validate_dashboard` and a successful `streamlit run dashboard/app.py`.
- 2026-04-27: migrated dashboard runtime data to SQLite and added deterministic synthetic user transaction generation consistent with the seeded mock datasets.
- 2026-04-27: fixed Streamlit Community Cloud startup by bootstrapping repo root into `sys.path` in `dashboard/app.py`, so absolute imports like `from dashboard...` resolve when the app is launched as `dashboard/app.py`.
- Next step: deploy the Streamlit dashboard from `dashboard/app.py` to Streamlit Community Cloud and keep the storefront on Vercel.

## Dashboard MVP Plan

### Summary
- Add a separate Streamlit module in this repo for an internal margin-and-returns dashboard.
- Keep the current `Next.js` storefront unchanged.
- Run the dashboard on SQLite with SQL-ready dataset specs and a heuristic intervention simulator.

### MVP Scope
- Overview: GMV, return rate, margin, contribution per order, health badges.
- Toxic segment card: concentrated loss driver framed for decision-making.
- User segments: scatter by return rate and GMV.
- Seller segments: ranked impact table with risk labels.
- Simulation: top-returner intervention with estimated margin and GMV deltas.
- Tracking readiness: daily snapshots and intervention log to support future migration analysis.

### Dataset Contracts
- SQLite tables:
  - `orders_fact`
  - `user_agg_daily`
  - `seller_agg_daily`
  - `product_agg_daily`
  - `interventions_log`
- Seed CSV fixtures remain in repo only to rebuild the database deterministically.

### Deployment Notes
- Streamlit entrypoint: `dashboard/app.py`
- Dependency file: `dashboard/requirements.txt`
- Sharing mode: internal demo/share link on Streamlit Community Cloud
