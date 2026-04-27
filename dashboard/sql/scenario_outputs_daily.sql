-- Estimated or observed scenario outputs used by the dashboard change-tracking section.

create table if not exists analytics.scenario_outputs_daily (
    snapshot_date date not null,
    intervention_code text not null,
    scenario_hash text not null,
    before_window text not null,
    after_window text not null,
    observed_delta numeric not null,
    delta_margin numeric not null,
    delta_gmv numeric not null,
    affected_entities integer not null,
    primary key (snapshot_date, intervention_code, scenario_hash)
);
