-- Daily seller snapshot used for impact ranking and dynamic commission preview.

create or replace table analytics.seller_agg_daily as
with calendar as (
    select distinct snapshot_date
    from analytics.orders_fact
)
select
    c.snapshot_date as date,
    c.snapshot_date,
    o.seller_id,
    s.seller_name,
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
    ) as margin_contribution,
    s.seller_segment,
    max(o.category) as top_category,
    avg(o.effective_commission_rate) filter (
        where o.order_date between c.snapshot_date - interval '29 day' and c.snapshot_date
    ) as effective_commission_rate,
    case
        when avg(o.effective_commission_rate) < 0.20 then 'negotiated'
        else 'standard'
    end as commission_tier,
    'v2' as seller_segment_version
from calendar c
join analytics.orders_fact o
    on o.order_date <= c.snapshot_date
join analytics.seller_dim s
    on o.seller_id = s.seller_id
group by
    c.snapshot_date,
    o.seller_id,
    s.seller_name,
    s.seller_segment;
