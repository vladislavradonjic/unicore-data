# unicore-data Conventions

## Data Product Codes

Each data product has a 4-character uppercase code. All database objects and dbt model files
belonging to a product are prefixed with that code.

| Code | Product | Source(s) | Type |
|------|---------|-----------|------|
| ASST | Assets + current book state | asset_svc.asset + asset_book_state | Source |
| ASGN | Asset assignments | asset_svc.asset_assignment | Source |
| ASOP | Asset operation requests | asset_svc.asset_operation_request | Source |
| DEPR | Depreciation run items | finance_svc.depreciation_run_item + depreciation_run | Source |
| PCAL | Period calendar | finance_svc.period_calendar | Source |
| WFCS | Workflow cases | finance_svc.workflow_case | Source |
| REFD | Reference data entries | seeds (CSV) | Source |

## Database Object Naming

```
{CODE}_{OBJECT_TYPE}
```

Object type suffixes:

| Suffix | Type |
|--------|------|
| `_T`   | Table |
| `_V`   | View |
| `_M`   | Materialized view |
| `_SP`  | Stored procedure |
| `_F`   | Function |

Output ports append the port identifier between the code and the object type:

```
{CODE}_{PORT}_{OBJECT_TYPE}
```

| Example | Meaning |
|---------|---------|
| `ASST_T`     | ASST source product table |
| `ASST_t1_T`  | ASST T-1 output port table |
| `ASST_m1_T`  | ASST M-1 output port table |
| `REFD_t1_V`  | REFD T-1 output port view (seeds — no incremental table) |

## dbt Project Structure

Model files and directories follow the same naming convention:

```
models/
  sources/
    ASST/
      ASST_T.sql         ← incremental source product table
      ASST_t1_T.sql      ← T-1 output port
      ASST_m1_T.sql      ← M-1 output port
      ASST.yml           ← schema, data contract, DQ tests
    ASGN/
      ASGN_T.sql
      ASGN_t1_T.sql
      ASGN_m1_T.sql
      ASGN.yml
    ASOP/
    DEPR/
    PCAL/
    WFCS/
    REFD/
      REFD_t1_V.sql      ← view over seeds; no incremental table
      REFD.yml
  marts/                  ← consumer data products (future)
```

Seeds (in `/seeds/`) keep their current descriptive names since they are not DB objects
managed by the naming convention — they feed `REFD_T` indirectly via seed tables.

dbt uses `alias` config to enforce the uppercase object name in the database:

```sql
{{ config(alias='ASST_T', ...) }}
```

This ensures consistency between Postgres (dev) and Oracle (prod), both of which are
case-insensitive but conventionally uppercase in enterprise environments.

## Bi-Temporal Columns

Every source product table (`*_T`) carries these three columns:

| Column | Type | Description |
|--------|------|-------------|
| `business_ts` | date | The business date the record refers to (e.g. activation_date for assets, effective_from for assignments) |
| `technical_ts` | timestamp | When this row was inserted into the data platform (set to `current_timestamp` at load time) |
| `deleted_flag` | boolean | `true` if the source record no longer exists at load time |

Records are **never updated or deleted** from source product tables. Changes in the source
produce new rows with a new `technical_ts`.

## Incremental Load Pattern

Source product tables use `materialized='incremental'`, `incremental_strategy='append'`.

- **Full refresh**: loads all rows from source, stamps `technical_ts = current_timestamp`
- **Incremental run**: filters source to rows where `created_at` or `updated_at >
  MAX(technical_ts)` from the target table; appends only new/changed rows

Deletion detection is deferred until live ERP integration.

## Output Port Logic

Output ports expose a deduplicated, point-in-time view of the source product table.
The standard pattern using `ROW_NUMBER()`:

```sql
select * from (
    select *,
        row_number() over (
            partition by [key_columns]
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('ASST_T') }}
    where business_ts <= current_date - 1  -- T-1; use last day of prev month for M-1
)
where rn = 1
```

`key_columns` per product:

| Code | Partition key | Rationale |
|------|--------------|-----------|
| ASST | `asset_id` | One current state per asset |
| ASGN | `assignment_id` | Deduplicates loads; preserves full assignment history |
| ASOP | `request_number` | One row per operation request |
| DEPR | `run_item_id` | One row per asset per period |
| PCAL | `period_code` | One row per fiscal period |
| WFCS | `case_number` | One row per workflow case |

M-1 ports replace the `current_date - 1` filter with the last calendar day of the
previous month:

```sql
where business_ts <= (date_trunc('month', current_date) - interval '1 day')::date
```
