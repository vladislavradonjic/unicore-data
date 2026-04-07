{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

with source as (

    select * from {{ source('finance_svc', 'workflow_case') }}

    {% if is_incremental() %}
    where submitted_at > (select max(technical_ts) from {{ this }})
    {% endif %}

),

final as (

    select
        id                       as case_id,
        case_number,
        aggregate_type,
        aggregate_id,
        operation_type,
        workflow_status,
        maker_user_id,
        maker_username,
        checker_user_id,
        checker_username,
        submitted_at,
        verified_at,
        returned_at,
        comment_text,
        -- bi-temporal
        cast(
            coalesce(verified_at, submitted_at) as date
        )                        as business_ts,
        current_timestamp        as technical_ts,
        'false'                  as deleted_flag
    from source

)

select * from final
