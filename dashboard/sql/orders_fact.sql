-- FashionHero MVP source-of-truth fact table.
-- Adjust source table names and commission logic to match the real warehouse.

create or replace table analytics.orders_fact as
select
    o.id as order_id,
    o.user_id,
    oi.seller_id,
    o.created_at::date as order_date,
    sum(oi.price_gross) as gmv,
    sum(oi.price_gross * coalesce(oi.commission_rate, 0.22)) as commission,
    case when max(r.order_id) is not null then 1 else 0 end as returned_flag,
    coalesce(sum(r.refund_amount), 0) as return_value,
    max(r.reason_code) as return_reason,
    max(r.created_at)::date as return_date,
    count(oi.id) as items_count,
    max(oi.category_name) as category,
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
    o.created_at::date;
