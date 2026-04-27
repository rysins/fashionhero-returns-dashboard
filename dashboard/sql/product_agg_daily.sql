-- Product snapshot used for ranking, product-health analysis and recommendation previews.

create or replace table analytics.product_agg_daily as
select
    snapshot_date as date,
    snapshot_date,
    product_id,
    seller_id,
    product_name,
    category_name as category,
    lower(replace(category_name, ' ', '_')) as category_id,
    views,
    orders,
    returns::float / nullif(orders, 0) as return_rate,
    orders::float / nullif(views, 0) as conversion_rate,
    avg_price,
    product_segment,
    (avg_price * orders * effective_commission_rate) - (avg_price * orders * returns::float / nullif(orders, 1)) as margin_contribution,
    ((1 - returns::float / nullif(orders, 1)) * 100) + (orders::float / nullif(views, 1)) * 1000 as promotion_score
from analytics.product_daily_snapshot_source;
