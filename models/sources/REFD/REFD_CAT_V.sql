{{ config(materialized = 'view') }}

select * from {{ ref('asset_categories') }}
