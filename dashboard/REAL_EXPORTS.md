# Real Exports Runbook

Instrukcja podpięcia realnych eksportów FashionHero do aktualnego pipeline'u `CSV -> normalize -> SQLite -> Streamlit`.

## Cel

Pipeline w obecnej wersji nie czyta bezpośrednio z produkcyjnej bazy. Oczekuje zestawu dziennych eksportów CSV o stałych nazwach i minimalnym kontrakcie kolumn. Po podmianie plików wejściowych:

- `python -m dashboard.pipeline` buduje nową bazę runtime,
- `python -m dashboard.validate_dashboard` weryfikuje spójność danych,
- Streamlit czyta wyłącznie wynikową bazę SQLite.

## Folder wejściowy

Docelowy zestaw eksportów powinien trafiać do jednego katalogu roboczego, np.:

```text
dashboard/imports/live/
```

Aktualny adapter czyta z `dashboard/seeds/`. Dla realnych danych należy:

1. utworzyć nowy katalog z eksportami,
2. uruchomić pipeline ze wskazaniem tego katalogu jako `source_dir`,
3. nie nadpisywać plików seedowych, jeśli mają zostać jako fallback demo.

Przykład uruchomienia lokalnego:

```bash
python - <<'PY'
from pathlib import Path
from dashboard.pipeline import run_pipeline

run_pipeline(source_dir=Path("dashboard/imports/live"))
PY
```

## Wymagane pliki

Pipeline oczekuje pięciu plików CSV:

- `orders_fact.csv`
- `user_agg_daily.csv`
- `seller_agg_daily.csv`
- `product_agg_daily.csv`
- `interventions_log.csv`

Nazwy plików muszą pozostać dokładnie takie same.

## Minimalny kontrakt kolumn

### `orders_fact.csv`

Wymagane kolumny:

- `order_id`
- `user_id`
- `seller_id`
- `order_date`
- `gmv`
- `commission`
- `returned_flag`
- `return_value`
- `return_reason`
- `return_date`
- `items_count`
- `category`
- `device`
- `traffic_source`

Uwagi:

- `order_date` i `return_date` powinny być w formacie ISO `YYYY-MM-DD`.
- `returned_flag` powinien być `0` albo `1`.
- `gmv`, `commission`, `return_value` muszą być liczbami bez separatorów tysięcy.
- `category` powinna być spójna z kategoriami używanymi w `product_agg_daily.csv`.

### `user_agg_daily.csv`

Wymagane kolumny:

- `user_id`
- `date`
- `user_name`
- `orders_last_30d`
- `gmv_last_30d`
- `return_rate_last_30d`
- `return_cost_last_30d`
- `avg_items_per_order`
- `lifetime_orders`
- `lifetime_return_rate`
- `contribution_margin_last_30d`
- `segment_label`
- `primary_device`

Uwagi:

- `date` to data snapshotu dziennego.
- `segment_label` powinien używać jednej z wartości:
  - `high_value`
  - `toxic`
  - `tryers`
  - `low_value`
- jeśli realne segmenty są liczone gdzie indziej, muszą zostać zmapowane do tych etykiet przed eksportem albo w osobnym kroku transformacji.

### `seller_agg_daily.csv`

Wymagane kolumny:

- `seller_id`
- `date`
- `seller_name`
- `gmv_last_30d`
- `return_rate_last_30d`
- `orders_count`
- `avg_order_value`
- `margin_contribution`
- `seller_segment`
- `top_category`

Uwagi:

- `seller_segment` powinien używać jednej z wartości:
  - `healthy`
  - `warning`
  - `risky`

### `product_agg_daily.csv`

Wymagane kolumny:

- `product_id`
- `seller_id`
- `date`
- `product_name`
- `category`
- `views`
- `orders`
- `return_rate`
- `conversion_rate`
- `avg_price`
- `product_segment`

Uwagi:

- `product_segment` może zostać dowolny, ale rekomendowane wartości to np. `golden`, `high_return`, `watchlist`.
- `category` musi odpowiadać `orders_fact.category`.

### `interventions_log.csv`

Wymagane kolumny:

- `intervention_id`
- `type`
- `target_type`
- `target_id`
- `start_date`
- `end_date`
- `parameters`

Uwagi:

- `type` powinien mapować się do znanych interwencji, np.:
  - `ranking_change`
  - `commission_increase`
  - `soft_penalty`
- `end_date` może być puste dla aktywnej interwencji.

## Mapowanie z realnych tabel FashionHero

Jeśli eksporty powstają z wewnętrznych tabel lub widoków, zalecane źródła logiczne są następujące:

- `orders_fact.csv`
  - zamówienia
  - pozycje zamówień
  - zwroty
- `user_agg_daily.csv`
  - agregacja user + dzień na bazie `orders_fact`
- `seller_agg_daily.csv`
  - agregacja seller + dzień na bazie `orders_fact`
- `product_agg_daily.csv`
  - agregacja product + dzień z wyświetleń, zamówień i zwrotów
- `interventions_log.csv`
  - ręcznie utrzymywana tabela operacyjna lub eksport z narzędzia eksperymentowego

SQL-ready kontrakty są opisane w:

- [orders_fact.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/orders_fact.sql)
- [user_agg_daily.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/user_agg_daily.sql)
- [seller_agg_daily.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/seller_agg_daily.sql)
- [product_agg_daily.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/product_agg_daily.sql)
- [category_agg_daily.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/category_agg_daily.sql)
- [interventions_log.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/interventions_log.sql)
- [scenario_outputs_daily.sql](/Users/marcin/Documents/Codex_projects/FashionHero/dashboard/sql/scenario_outputs_daily.sql)

## Codzienna procedura zasilania

### Wariant ręczny

1. Wygenerować komplet eksportów CSV za najnowszy snapshot.
2. Wrzucić je do `dashboard/imports/live/`.
3. Uruchomić:

```bash
python - <<'PY'
from pathlib import Path
from dashboard.pipeline import run_pipeline

run_pipeline(source_dir=Path("dashboard/imports/live"))
PY
python -m dashboard.validate_dashboard
```

4. Sprawdzić wynik w:
  - `dashboard/data/fashionhero_dashboard.sqlite`
  - `dashboard/data/pipeline_manifest.json`

### Wariant przez GitHub Actions

Docelowy przepływ:

1. Eksporty są publikowane do katalogu roboczego lub pobierane przez workflow.
2. Workflow wywołuje `run_pipeline(source_dir=...)`.
3. Workflow uruchamia `python -m dashboard.validate_dashboard`.
4. Workflow commit/pushuje:
  - `dashboard/data/fashionhero_dashboard.sqlite`
  - `dashboard/data/pipeline_manifest.json`

Jeśli eksporty będą pobierane z prywatnego źródła, sekret powinien trafić tylko do workflow, nie do aplikacji Streamlit.

## Najczęstsze problemy

### Brakująca kolumna

Objaw:

- pipeline kończy się wyjątkiem `is missing required columns`

Działanie:

- sprawdzić nagłówek CSV,
- zmapować nazwę kolumny do oczekiwanego kontraktu przed uruchomieniem pipeline'u.

### Rozjazd kategorii między orders i products

Objaw:

- produkty wpadają do niewłaściwego drill-downu albo dostają fallbackowe mapowanie

Działanie:

- ujednolicić `category` pomiędzy `orders_fact.csv` i `product_agg_daily.csv`

### Dane tylko za jeden dzień bez snapshot history

Objaw:

- dashboard działa, ale sekcje `before/after` i migracje segmentów są ubogie albo puste

Działanie:

- dostarczać co najmniej dwa snapshoty dzienne w agregatach `user_agg_daily`, `seller_agg_daily`, `product_agg_daily`

## Rekomendacja operacyjna

Na start najbezpieczniej utrzymać dwa zestawy wejścia:

- `dashboard/seeds/` jako stabilny demo fallback
- `dashboard/imports/live/` jako bieżący kanał realnych eksportów

To pozwala testować pipeline na realnych danych bez psucia wersji demonstracyjnej.
