{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

with run_items as (

    select * from {{ source('finance_svc', 'depreciation_run_item') }}

),

runs as (

    select * from {{ source('finance_svc', 'depreciation_run') }}

    {% if is_incremental() %}
    where completed_at > (select max(technical_ts) from {{ this }})
    {% endif %}

),

final as (

    select
        i.id                     as run_item_id,
        r.id                     as depreciation_run_id,
        r.run_number,
        r.period_code,
        r.run_status,
        r.completed_at,
        r.initiated_by,
        i.asset_id,
        i.asset_number,
        i.amount                 as depreciation_amount,
        i.status                 as item_status,
        -- bi-temporal
        cast(r.completed_at as date)  as business_ts,
        current_timestamp             as technical_ts,
        'false'                       as deleted_flag
    from run_items      i
    join runs           r on r.id = i.depreciation_run_id

)

select * from final
