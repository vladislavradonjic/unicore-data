# unicore-data

Data project for the UniCore fixed assets platform. We consume data produced by the UniCore ERP application (`../unicore_erp/`) and build data products organized as a **data mesh** platform.

## Context

**unicore_erp** is a Java/Spring Boot microservices application (Stage 1 — skeleton only, no business logic yet) for a bank's fixed assets and intangible investments management. It runs on Postgres locally, targets Oracle in production.

**unicore-data** is an independent sub-project. We read from ERP service databases; we do not write back to them.

## Business Domain

**UniCore** manages bank property:
- **OS** (Osnovna sredstva) — fixed/tangible assets
- **NU** (Nematerijalna ulaganja) — intangible investments (software, licenses)
- **IN** (Investicione nekretnine) — investment properties (IAS 40)
- **Ulaganja u tuđa OS** — investments in leased premises

Core processes: asset activation, depreciation calculation (accounting + tax), inventory (barcode scanning), disposal/sale/donation, CORE banking system integration via posting instructions.

**User roles**: Računovodstvo (full access + verification), ICT, RE (Real Estate), Tax, Controlling, Delegirani korisnici (org unit delegates).

**Verification rule**: maker-checker enforced — the user who enters a posting cannot verify it.

## ERP Data Sources

Each service owns its schema:

| Service | Key Tables |
|---|---|
| asset-service | `asset`, `asset_preparation`, `asset_component`, `asset_book_state`, `asset_assignment`, `asset_operation_request`, `inventory_session`, `inventory_item_result` |
| finance-workflow-service | `depreciation_run`, `depreciation_run_item`, `accounting_event`, `workflow_case`, `workflow_action`, `period_calendar` |
| core-integration-service | `posting_instruction`, `posting_attempt`, `delivery_receipt` |
| reference-data-service | `codebook`, `codebook_entry`, `effective_period`, `reference_mapping` |
| reporting-service | `report_query_template`, `report_export_request`, `report_export_result` |
| document-service | `document`, `document_version`, `document_link` |

All services also have `audit_event` and `outbox_event` tables.

## ERP Repo Layout (../unicore_erp/)

```
services/          # Spring Boot microservices
contracts/         # OpenAPI specs + async event schemas
platform/          # Shared Java libraries
gateway/           # FastAPI API gateway
docs/architecture/ # Canonical data model + NFR baseline
```

## Business Specification

Full spec (Serbian): `doc/specification.md`

MVP priorities:
- **MVP1**: OS activation/disposal, monthly depreciation, reference data, RBAC, asset card/base reports
- **MVP2**: NU management, location/custodian changes, leased premises, annual depreciation + projections, CORE posting integration
- **MVP3**: Inventory with barcodes, investment properties (IAS 40), tax depreciation, dynamic reports, SC integration

## Data Platform Architecture

Full spec: `doc/data-platform.md`

### Data Product Types
- **Source data products** — ingest from ERP service databases
- **Consumer data products** — built on source products, shaped for business consumption

### Data Product Components
Every data product consists of:
1. **Relevance matrix** — owner, name, and per-field: technical name, business name, description, lineage
2. **Data** — bi-temporal, insert-only store (see below)
3. **Output ports** — named snapshots consumers read (never raw tables directly)
4. **Data contract** — verbose spec: domain/subdomain, refresh schedule, output port definitions, DQ thresholds
5. **Data quality controls** — checked on every refresh
6. **Code** — pipelines/models that generate and refresh the above

### Data Storage Pattern
- **Bi-temporal**: every record carries a `business_timestamp` (what the record refers to) and `technical_timestamp` (when it was inserted)
- **Insert-only**: no updates or deletes; source deletions are tracked by inserting a new row with `deleted_flag = true`
- **Daily refresh**, holding data up to the previous business day

### Output Ports (standard minimum)
- **t-1** — valid as of previous business day
- **m-1** — valid as of previous end of month

## Naming Conventions

Full detail: `doc/conventions.md`

### Data product codes

| Code | Product |
|------|---------|
| ASST | Assets + current book state |
| ASGN | Asset assignments |
| ASOP | Asset operation requests |
| DEPR | Depreciation run items |
| PCAL | Period calendar |
| WFCS | Workflow cases |
| REFD | Reference data entries (seeds) |

### DB object names
- Pattern: `{CODE}_{OBJECT_TYPE}` — e.g. `ASST_T`
- Output ports: `{CODE}_{PORT}_{OBJECT_TYPE}` — e.g. `ASST_t1_T`, `ASST_m1_T`
- Suffixes: `_T` table, `_V` view, `_M` materialized view, `_SP` stored procedure, `_F` function
- dbt model files and directories use the same names; enforce with `alias` config

### dbt layout
```
models/
  sources/
    ASST/
      ASST_T.sql        ← incremental source product
      ASST_t1_T.sql     ← T-1 output port
      ASST_m1_T.sql     ← M-1 output port
      ASST.yml          ← schema + DQ tests + contract stub
  marts/                ← consumer products (future)
```

### Bi-temporal columns (on every source product table)
- `business_ts` — date the record refers to in business terms
- `technical_ts` — timestamp when the row was inserted into the platform
- `deleted_flag` — true if the source record was absent at load time

### Output port logic
Uses `ROW_NUMBER() OVER (PARTITION BY [key] ORDER BY business_ts DESC, technical_ts DESC)`.
T-1 filters `business_ts <= current_date - 1`, M-1 filters `business_ts <= last day of previous month`.

## Key Constraints

- Production DB is Oracle-compatible; avoid Postgres-specific SQL in portable models
- No writes to ERP service databases
- All monetary/quantity calculations must be numerically exact (no floating point)
