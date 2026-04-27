-- Daily user snapshot used for segment migration, soft-penalty targeting and KPI tracking.

create or replace table analytics.user_agg_daily as
with calendar as (
    select distinct snapshot_date
    from analytics.orders_fact
),
user_returns as (
    select
        c.snapshot_date,
        o.user_id,
        count(*) filter (
            where o.returned_flag = 1
              and o.order_date between c.snapshot_date - interval '89 day' and c.snapshot_date
        ) as quarter_returns_count
    from calendar c
    join analytics.orders_fact o
        on o.order_date <= c.snapshot_date
    group by
        c.snapshot_date,
        o.user_id
)
select
    c.snapshot_date as date,
    c.snapshot_date,
    o.user_id,
    u.user_name,
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
    ) as contribution_margin_last_30d,
    u.segment_label,
    u.primary_device,
    ur.quarter_returns_count,
    case when ur.quarter_returns_count > 2 then 'paid_after_threshold' else 'eligible' end as free_return_eligibility,
    'v2' as user_segment_version
from calendar c
join analytics.orders_fact o
    on o.order_date <= c.snapshot_date
join analytics.user_dim u
    on o.user_id = u.user_id
left join user_returns ur
    on ur.snapshot_date = c.snapshot_date
   and ur.user_id = o.user_id
group by
    c.snapshot_date,
    o.user_id,
    u.user_name,
    u.segment_label,
    u.primary_device,
    ur.quarter_returns_count;
