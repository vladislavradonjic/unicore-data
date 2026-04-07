import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db import load, fmt_rsd

st.title("Projekcija amortizacije")

df = load("DPRJ_T")

# ── sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filteri")
    sel_type = st.multiselect("Tip imovine", sorted(df["asset_type"].dropna().unique()))
    sel_cat = st.multiselect(
        "Kategorija", sorted(df["category_code"].dropna().unique())
    )
    horizon = st.slider(
        "Horizont projekcije (meseci)", min_value=6, max_value=36, value=36, step=6
    )

flt = df.copy()
if sel_type:
    flt = flt[flt["asset_type"].isin(sel_type)]
if sel_cat:
    flt = flt[flt["category_code"].isin(sel_cat)]
flt = flt[flt["months_from_today"] <= horizon]

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
num_assets = flt["asset_id"].nunique()
total_monthly = (
    flt[flt["months_from_today"] == flt["months_from_today"].min()][
        "monthly_depreciation_amount"
    ].sum()
    if len(flt) > 0
    else 0
)
total_projected = (
    flt.groupby("asset_id").first()["net_amount_today"].sum() if len(flt) > 0 else 0
)
fully_depr = (
    int(
        flt.groupby("asset_id")
        .filter(lambda g: g["projected_net_amount"].min() == 0)["asset_id"]
        .nunique()
    )
    if len(flt) > 0
    else 0
)

k1.metric("Aktivnih sredstava", num_assets)
k2.metric("Mesečna amortizacija (tekući)", fmt_rsd(total_monthly))
k3.metric("Sadašnja neto vrednost", fmt_rsd(total_projected))
k4.metric("Potpuno amortizonih u periodu", fully_depr)

st.divider()

tab1, tab2 = st.tabs(["Pregled projekcije", "Po kategoriji"])

# ── TAB 1: projection overview ────────────────────────────────────────────────
with tab1:
    # aggregated monthly depreciation
    monthly = (
        flt.groupby("projected_period_code", as_index=False)
        .agg(total=("monthly_depreciation_amount", "sum"))
        .sort_values("projected_period_code")
    )
    fig = px.bar(
        monthly,
        x="projected_period_code",
        y="total",
        title=f"Projektovana mesečna amortizacija (narednih {horizon} meseci)",
        labels={"projected_period_code": "Period", "total": "Amortizacija (RSD)"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # cumulative projected net value decline
    net_by_month = (
        flt.groupby("projected_period_code", as_index=False)
        .agg(net_sum=("projected_net_amount", "sum"))
        .sort_values("projected_period_code")
    )
    fig2 = px.line(
        net_by_month,
        x="projected_period_code",
        y="net_sum",
        title="Kretanje ukupne neto vrednosti kroz projekciju",
        labels={"projected_period_code": "Period", "net_sum": "Neto vrednost (RSD)"},
        markers=True,
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

# ── TAB 2: breakdown by category ──────────────────────────────────────────────
with tab2:
    by_cat_period = (
        flt.groupby(["projected_period_code", "category_code"], as_index=False)
        .agg(total=("monthly_depreciation_amount", "sum"))
        .sort_values("projected_period_code")
    )
    fig3 = px.bar(
        by_cat_period,
        x="projected_period_code",
        y="total",
        color="category_code",
        title="Projektovana amortizacija po kategoriji",
        labels={
            "projected_period_code": "Period",
            "total": "Amortizacija (RSD)",
            "category_code": "Kategorija",
        },
        barmode="stack",
    )
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

    # summary table per category
    st.subheader("Pregled po kategoriji")
    cat_summary = (
        flt.groupby("category_code", as_index=False)
        .agg(
            sredstava=("asset_id", "nunique"),
            uk_mesecna_amort=("monthly_depreciation_amount", "mean"),
            sadanja_neto=(
                "net_amount_today",
                lambda x: flt.loc[x.index]
                .groupby("asset_id")["net_amount_today"]
                .first()
                .sum(),
            ),
        )
        .sort_values("sadanja_neto", ascending=False)
        .rename(
            columns={
                "category_code": "Kategorija",
                "sredstava": "Sredstava",
                "uk_mesecna_amort": "Avg. mes. amort.",
                "sadanja_neto": "Ukupna neto vrednost",
            }
        )
    )
    st.dataframe(
        cat_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Avg. mes. amort.": st.column_config.NumberColumn(format="%.2f RSD"),
            "Ukupna neto vrednost": st.column_config.NumberColumn(format="%.0f RSD"),
        },
    )
