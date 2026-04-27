-- Runtime fact table contract for FashionHero phase 2.
-- 1 row = 1 order. The pipeline can ingest CSV exports now and switch to SQL later.

create or replace table analytics.orders_fact as
select
    o.id as order_id,
    o.user_id,
    oi.seller_id,
    oi.product_id,
    oi.product_name,
    o.created_at::date as order_date,
    (o.created_at + interval '3 day')::date as delivered_at,
    current_date as snapshot_date,
    sum(oi.price_gross) as gmv,
    sum(oi.price_gross * coalesce(oi.commission_rate, 0.22)) as commission,
    avg(coalesce(oi.commission_rate, 0.22)) as effective_commission_rate,
    case when max(r.order_id) is not null then 1 else 0 end as returned_flag,
    coalesce(sum(r.refund_amount), 0) as return_value,
    case when max(r.order_id) is not null then 14.0 else 0 end as return_shipping_cost,
    max(r.reason_code) as return_reason,
    max(r.created_at)::date as return_date,
    count(oi.id) as items_count,
    max(oi.category_name) as category,
    lower(replace(max(oi.category_name), ' ', '_')) as category_id,
    max(o.device_type) as device,
    max(o.traffic_source) as traffic_source
from raw.orders o
join raw.order_items oi
    on o.id = oi.order_id
left join raw.returns r
    on o.id = r.order_id
group by
    o.id,
    o.user_id,
    oi.seller_id,
    oi.product_id,
    oi.product_name,
    o.created_at::date;
