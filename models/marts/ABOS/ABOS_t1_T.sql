{{ config(materialized='table') }}

-- Output port: current state of all assets as of T-1.
-- ABOS_T is already built from t-1 output ports, so no additional
-- temporal filtering is required — this is a stable consumer interface.

select * from {{ ref('ABOS_T') }}
