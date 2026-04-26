-- Daily snapshot for behavior tracking and segment migration.
-- Build this for every reporting date, not only "today".

create or replace table analytics.user_agg_daily as
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
    o.user_id,
    count(*) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as orders_last_30d,
    sum(o.gmv) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as gmv_last_30d,
    avg(o.returned_flag::float) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as return_rate_last_30d,
    sum(o.return_value) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as return_cost_last_30d,
    avg(o.items_count) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as avg_items_per_order,
    count(*) filter (where o.order_date <= c.snapshot_date) as lifetime_orders,
    avg(o.returned_flag::float) filter (where o.order_date <= c.snapshot_date) as lifetime_return_rate,
    sum(o.commission - o.return_value) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as contribution_margin_last_30d
from calendar c
join dated_orders o
    on o.order_date <= c.snapshot_date
group by
    c.snapshot_date,
    o.user_id;
