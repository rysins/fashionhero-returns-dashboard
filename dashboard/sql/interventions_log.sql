-- Log of business changes. This is the minimum event contract required to
-- connect future segment migrations and KPI deltas to what the team changed.

create table if not exists analytics.interventions_log (
    intervention_id text primary key,
    type text not null,           -- e.g. ranking_change, commission_increase
    target_type text not null,    -- user, seller, product
    target_id text not null,
    start_date date not null,
    end_date date,
    parameters text not null
);
