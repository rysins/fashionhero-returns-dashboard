-- Category snapshot for dashboard drill-down and executive category health scoring.

create or replace table analytics.category_agg_daily as
select
    snapshot_date as date,
    snapshot_date,
    category_id,
    initcap(replace(category_id, '_', ' ')) as category_name,
    sum(gmv_last_30d) as gmv_last_30d,
    sum(returned_orders)::float / nullif(sum(orders_count), 0) as return_rate_last_30d,
    sum(margin_contribution) as margin_contribution,
    sum(orders_count) as orders_count,
    sum(margin_contribution) / nullif(sum(orders_count), 0) as contribution_per_order,
    sum(toxic_orders)::float / nullif(sum(orders_count), 0) as toxic_share
from analytics.category_daily_snapshot_source
group by
    snapshot_date,
    category_id;
