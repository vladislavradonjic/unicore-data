import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from db import load, fmt_rsd

st.title("Amortizacija")

amrt = load("AMRT_t1_T")
amrc = load("AMRC_T")

# ── sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filteri")
    years = sorted(amrt["fiscal_year"].dropna().unique().astype(int))
    sel_years = st.multiselect("Fiskalna godina", years, default=years)
    sel_cat = st.multiselect(
        "Kategorija", sorted(amrt["category_code"].dropna().unique())
    )

flt = amrt.copy()
if sel_years: flt = flt[flt["fiscal_year"].isin(sel_years)]
if sel_cat:   flt = flt[flt["category_code"].isin(sel_cat)]

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
k1.metric("Ukupno knjiženja",          len(flt))
k2.metric("Ukupna amortizacija (period)", fmt_rsd(flt["depreciation_amount"].sum()))
k3.metric("Broj perioda",              flt["period_code"].nunique())

st.divider()

tab1, tab2 = st.tabs(["Pregled", "Kontrola obračuna"])

# ── TAB 1: overview ───────────────────────────────────────────────────────────
with tab1:
    # monthly totals bar chart
    monthly = (
        flt.groupby("period_code", as_index=False)
        .agg(total=("depreciation_amount", "sum"))
        .sort_values("period_code")
    )
    fig = px.bar(
        monthly, x="period_code", y="total",
        title="Mesečna amortizacija po periodu",
        labels={"period_code": "Period", "total": "Amortizacija (RSD)"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # stacked by category
    by_cat_period = (
        flt.groupby(["period_code", "category_code"], as_index=False)
        .agg(total=("depreciation_amount", "sum"))
        .sort_values("period_code")
    )
    fig2 = px.bar(
        by_cat_period, x="period_code", y="total", color="category_code",
        title="Amortizacija po kategoriji i periodu",
        labels={"period_code": "Period", "total": "Amortizacija (RSD)", "category_code": "Kategorija"},
        barmode="stack",
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # summary table by category
    st.subheader("Pregled po kategoriji")
    summary = (
        flt.groupby(["category_code", "category_name"], as_index=False)
        .agg(
            periodi=("period_code", "nunique"),
            sredstava=("asset_id", "nunique"),
            ukupno=("depreciation_amount", "sum"),
        )
        .sort_values("ukupno", ascending=False)
        .rename(columns={
            "category_code": "Kategorija",
            "category_name": "Naziv",
            "periodi":       "Periodi",
            "sredstava":     "Sredstava",
            "ukupno":        "Ukupna amortizacija",
        })
    )
    st.dataframe(
        summary, use_container_width=True, hide_index=True,
        column_config={"Ukupna amortizacija": st.column_config.NumberColumn(format="%.2f RSD")},
    )

# ── TAB 2: reconciliation ─────────────────────────────────────────────────────
with tab2:
    st.subheader("Platforma vs. ERP — status usaglašenosti")

    # apply same year/cat filters to AMRC
    flt_amrc = amrc.copy()
    if sel_years: flt_amrc = flt_amrc[flt_amrc["fiscal_year"].isin(sel_years)]
    if sel_cat:   flt_amrc = flt_amrc[flt_amrc["category_code"].isin(sel_cat)]

    status_counts = (
        flt_amrc.groupby("reconciliation_status", as_index=False)
        .agg(count=("asset_id", "count"), variance=("variance", "sum"))
    )

    r1, r2, r3 = st.columns(3)
    match_n    = int(status_counts.loc[status_counts["reconciliation_status"] == "MATCH",    "count"].sum())
    mismatch_n = int(status_counts.loc[status_counts["reconciliation_status"] == "MISMATCH", "count"].sum())
    missing_n  = int(status_counts.loc[status_counts["reconciliation_status"] == "ERP_MISSING", "count"].sum())

    r1.metric("MATCH",       match_n,    delta=None)
    r2.metric("MISMATCH",    mismatch_n, delta=f"{mismatch_n} neslaganja" if mismatch_n else None,
              delta_color="inverse")
    r3.metric("ERP_MISSING", missing_n,  delta=f"{missing_n} nedostaje u ERP" if missing_n else None,
              delta_color="inverse")

    # pie chart
    fig3 = px.pie(
        status_counts, values="count", names="reconciliation_status",
        title="Usaglašenost po broju zapisa", hole=0.4,
        color="reconciliation_status",
        color_discrete_map={"MATCH": "#2ecc71", "MISMATCH": "#e74c3c", "ERP_MISSING": "#f39c12"},
    )
    st.plotly_chart(fig3, use_container_width=True)

    # mismatch detail
    mismatches = flt_amrc[flt_amrc["reconciliation_status"].isin(["MISMATCH", "ERP_MISSING"])]
    if len(mismatches) > 0:
        st.subheader(f"Detalji neslaganja ({len(mismatches)} zapisa)")
        st.dataframe(
            mismatches[[
                "asset_number", "category_code", "period_code",
                "calculated_amount", "erp_amount", "variance", "reconciliation_status",
            ]].rename(columns={
                "asset_number":           "Broj OS",
                "category_code":          "Kategorija",
                "period_code":            "Period",
                "calculated_amount":      "Obračunato",
                "erp_amount":             "ERP",
                "variance":               "Razlika",
                "reconciliation_status":  "Status",
            }).sort_values("Razlika", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Obračunato": st.column_config.NumberColumn(format="%.2f"),
                "ERP":        st.column_config.NumberColumn(format="%.2f"),
                "Razlika":    st.column_config.NumberColumn(format="%.2f"),
            },
        )
    else:
        st.success("Sva knjiženja su usaglašena sa ERP sistemom.")
