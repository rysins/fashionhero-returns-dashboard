-- Log of changes and preview rules used to connect observed segment movement to interventions.

create table if not exists analytics.interventions_log (
    intervention_id text primary key,
    type text not null,
    target_type text not null,
    target_id text not null,
    start_date date not null,
    end_date date,
    parameters text not null,
    intervention_code text not null,
    version integer not null default 1,
    status text not null,
    eligibility_rule text not null,
    parameter_json text not null
);
