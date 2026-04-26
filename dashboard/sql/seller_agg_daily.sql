-- Daily seller snapshot for impact ranking and intervention design.

create or replace table analytics.seller_agg_daily as
with dated_orders as (
    select *
    from analytics.orders_fact
),
calendar as (
    select distinct order_date as snapshot_date
    from dated_orders
)
select
    c.snapshot_date as date,
    o.seller_id,
    sum(o.gmv) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as gmv_last_30d,
    avg(o.returned_flag::float) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as return_rate_last_30d,
    count(*) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as orders_count,
    avg(o.gmv) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as avg_order_value,
    sum(o.commission - o.return_value) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as margin_contribution
from calendar c
join dated_orders o
    on o.order_date <= c.snapshot_date
group by
    c.snapshot_date,
    o.seller_id;
