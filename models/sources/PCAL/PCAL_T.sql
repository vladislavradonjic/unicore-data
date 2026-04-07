{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

with source as (

    -- period_calendar is append-only in practice; reload rows not yet seen
    select * from {{ source('finance_svc', 'period_calendar') }}

    {% if is_incremental() %}
    where starts_on > (select max(business_ts) from {{ this }})
    {% endif %}

),

final as (

    select
        id               as period_id,
        period_code,
        fiscal_year,
        fiscal_period,
        starts_on,
        ends_on,
        locked_flag,
        lock_reason,
        -- bi-temporal
        starts_on        as business_ts,
        current_timestamp as technical_ts,
        'false'          as deleted_flag
    from source

)

select * from final
