{{ config(materialized = 'view') }}

select * from {{ ref('locations') }}
