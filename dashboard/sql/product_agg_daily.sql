-- Optional product layer for future PDP/content interventions.

create or replace table analytics.product_agg_daily as
select
    snapshot_date as date,
    product_id,
    seller_id,
    product_name,
    category_name as category,
    views,
    orders,
    returns::float / nullif(orders, 0) as return_rate,
    orders::float / nullif(views, 0) as conversion_rate,
    avg_price,
    product_segment
from analytics.product_daily_snapshot_source;
