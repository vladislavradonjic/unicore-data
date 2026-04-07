{{ config(materialized = 'view') }}

select * from {{ ref('org_units') }}
