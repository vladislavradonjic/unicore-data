# Streamlit Dashboards

The `app/` directory contains a multi-page Streamlit application that exposes the
consumer data products (marts) to business users. The application is read-only — it
never writes to any database.

## Running the App

```bash
# Ensure the mock-source Postgres is up and dbt models are built first:
make reset        # full teardown → up → seed → dbt-run

# Then start the app:
streamlit run app/app.py
```

The app connects to `postgresql+psycopg2://unicore:unicore@localhost:5433/unicore`
(same as the dbt dev profile). Results are cached for 5 minutes (`TTL=300s`).

## Application Structure

```
app/
  app.py           ← entry point; registers all pages with st.navigation
  db.py            ← SQLAlchemy engine, query helpers, RSD formatter
  pages/
    baza_os.py     ← Baza OS
    amortizacija.py
    projekcija.py
    otpis.py
    kartica_os.py
    centri_troska.py
```

### `app/db.py`

| Symbol | Description |
|--------|-------------|
| `MARTS` | Schema constant: `unicore_analytics_marts` |
| `SOURCES` | Schema constant: `unicore_analytics` |
| `load(table, schema=MARTS)` | `SELECT * FROM <schema>."<table>"` → `pd.DataFrame` |
| `query(sql)` | Arbitrary SQL → `pd.DataFrame`; cached 300 s |
| `fmt_rsd(value)` | Formats a number as `"1,234,567 RSD"` |

## Pages

### Baza OS (`pages/baza_os.py`)

**Backing mart:** `ABOS_t1_T` (T-1 output port of the ABOS consumer mart)

Provides a bird's-eye view of the entire fixed-asset register as of the previous
business day.

**Sidebar filters:** lifecycle status, asset type, category code.

**KPIs (5):** total assets · active assets · acquisition value · net book value ·
count of fully depreciated assets.

**Charts:**
- Bar — net book value by category (colour per category, text = asset count)
- Pie (donut) — asset count by lifecycle status

**Table:** sortable asset list with columns: asset number, name, type, category,
status, activation date, acquisition value, net value, location, cost centre,
accountable person.

---

### Amortizacija (`pages/amortizacija.py`)

**Backing marts:** `AMRT_t1_T` (depreciation schedule) · `AMRC_T` (reconciliation)

Depreciation analysis split across two tabs.

**Sidebar filters:** fiscal year (multi), category code (multi). Filters are applied
to both tabs.

**KPIs (3):** total bookings · total depreciation for the selected periods · number
of distinct periods.

**Tab 1 — Pregled:**
- Bar — monthly depreciation totals by period
- Bar (stacked) — depreciation by category and period
- Summary table — per-category: distinct periods, asset count, total depreciation

**Tab 2 — Kontrola obračuna:**

Reads `AMRC_T`, which independently recalculates straight-line depreciation from
first principles and compares it to the ERP amount, producing one of three statuses:

| Status | Meaning |
|--------|---------|
| `MATCH` | Platform recalculation equals ERP amount |
| `MISMATCH` | Amounts differ by more than rounding tolerance |
| `ERP_MISSING` | Period exists on the platform but not in the ERP depreciation run |

Displays: three metric tiles (count per status) · pie chart by status count · detail
table for MISMATCH and ERP_MISSING records (asset number, category, period, platform
amount, ERP amount, variance).

---

### Projekcija (`pages/projekcija.py`)

**Backing mart:** `DPRJ_T`

Forward-looking 36-month depreciation projection for all active assets with
`net_amount > 0` and `depreciation_rate > 0`. The mart uses `generate_series`
(Postgres-specific) and is built as a static table on each dbt run.

**Sidebar filters:** asset type (multi) · category (multi) · horizon slider 6–36
months (step 6).

**KPIs (4):** active assets in selection · monthly depreciation (first projected
month) · total net value today · assets reaching full depreciation within the horizon.

**Tab 1 — Pregled projekcije:**
- Bar — projected monthly depreciation totals across the horizon
- Line — trajectory of aggregate net book value through the projection

**Tab 2 — Po kategoriji:**
- Bar (stacked) — projected depreciation by category and month
- Summary table — per category: asset count, average monthly depreciation, total net
  value today

---

### Otpis (`pages/otpis.py`)

**Backing mart:** `DISP_t1_T` (T-1 output port of the DISP consumer mart)

Register of all disposed, sold, and donated assets, joined with the originating
operation request and workflow approval case.

**Sidebar filters:** disposal type (`DISPOSED` / `SOLD` / `DONATED`) · asset type ·
category · workflow approval status.

**KPIs (5):** total disposed · acquisition value · net book value at disposal ·
accumulated depreciation · count pending approval.

**Tab 1 — Pregled:**
- Pie (donut) — count by disposal type (DISPOSED red · SOLD blue · DONATED green)
- Bar — acquisition value by category (text = asset count)
- Bar — acquisition value by disposal year (only rendered when disposal dates are
  present)

**Tab 2 — Detalji:**

Full sortable table: asset number, name, type, category, disposal type, activation
date, disposal date, acquisition value, accumulated depreciation, net book value at
disposal, request number, workflow status, maker, checker.

---

### Kartica OS (`pages/kartica_os.py`)

**Backing marts:** `KART_T` (event history) · `ABOS_t1_T` (asset header enrichment)

Per-asset event card showing the full lifecycle history of a single selected asset.
This is a drill-down page — the user selects one asset at a time.

**Sidebar:** type and category filters narrow the dropdown list; the selectbox
displays `{asset_number} — {asset_name}`.

**Asset header strip (5 columns):** lifecycle status · category · acquisition value ·
net book value · location.

**Event type badge row:** metric tiles showing the count of each event type present
for the selected asset.

**Tab 1 — Hronologija događaja:**
- Scatter timeline — one point per non-depreciation event, coloured and shaped by
  event type; hover shows reference number, actor, from/to values and notes
- Event table — all non-depreciation events sorted chronologically

**Tab 2 — Amortizacija:**
- Bar — depreciation amount by period code
- Line — cumulative depreciation through time
- Period table — period, amount, running cumulative, run number, initiator

Event types surfaced by `KART_T`:

| Event type | Source |
|------------|--------|
| `ACTIVATION` | `ASOP_t1_T` where `operation_type = 'ACTIVATION'` |
| `DISPOSAL` | `ASOP_t1_T` where `operation_type = 'DISPOSAL'` |
| `LOCATION_CHANGE` / `CUSTODIAN_CHANGE` | `MOVE_T` (non-initial assignments) |
| `DEPRECIATION` | `AMRT_T` (one row per completed depreciation period) |

---

### Centri troška (`pages/centri_troska.py`)

**Backing mart:** `CCDA_t1_T` (T-1 output port of the CCDA consumer mart)

Depreciation allocation by cost centre. `CCDA_T` matches each depreciation run item
to the assignment active at the start of that period and aggregates by
`(cost_center, category, period)`.

**Sidebar filters:** fiscal year (multi) · cost centre (multi) · category (multi).

**KPIs (4):** total depreciation · distinct cost centres · distinct periods · total
asset count (sum of `asset_count`).

**Tab 1 — Pregled po centru:**
- Bar — total depreciation per cost centre (text = asset count)
- Pie (donut) — cost centre share of total depreciation
- Heatmap — cost centre × category depreciation matrix (rendered only when ≥ 2 cost
  centres and ≥ 2 categories are present after filtering)
- Summary table — per cost centre: org unit, period count, asset count, total
  depreciation

**Tab 2 — Mesečni trend:**
- Bar — monthly depreciation totals (all cost centres combined)
- Bar (stacked) — monthly depreciation by cost centre
- Detail table — one row per (period, cost centre): fiscal year, fiscal period, cost
  centre code/name, asset count, depreciation amount

## Mart → Page Mapping

| Page | Primary mart | Secondary mart(s) |
|------|-------------|-------------------|
| Baza OS | `ABOS_t1_T` | — |
| Amortizacija | `AMRT_t1_T` | `AMRC_T` |
| Projekcija | `DPRJ_T` | — |
| Otpis | `DISP_t1_T` | — |
| Kartica OS | `KART_T` | `ABOS_t1_T` |
| Centri troška | `CCDA_t1_T` | — |
