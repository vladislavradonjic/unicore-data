{{ config(materialized = 'view') }}

select * from {{ ref('cost_centers') }}
