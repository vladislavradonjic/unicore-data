import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from db import load, fmt_rsd

st.title("Centri troška")

df = load("CCDA_t1_T")

# ── sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filteri")
    years = sorted(df["fiscal_year"].dropna().unique().astype(int))
    sel_years = st.multiselect("Fiskalna godina", years, default=years)
    sel_cc = st.multiselect(
        "Centar troška", sorted(df["cost_center_code"].dropna().unique())
    )
    sel_cat = st.multiselect(
        "Kategorija", sorted(df["category_code"].dropna().unique())
    )

flt = df.copy()
if sel_years:
    flt = flt[flt["fiscal_year"].isin(sel_years)]
if sel_cc:
    flt = flt[flt["cost_center_code"].isin(sel_cc)]
if sel_cat:
    flt = flt[flt["category_code"].isin(sel_cat)]

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Ukupna amortizacija", fmt_rsd(flt["total_depreciation_amount"].sum()))
k2.metric("Broj centara troška", flt["cost_center_code"].nunique())
k3.metric("Broj perioda", flt["period_code"].nunique())
k4.metric("Ukupno sredstava", int(flt["asset_count"].sum()))

st.divider()

tab1, tab2 = st.tabs(["Pregled po centru", "Mesečni trend"])

# ── TAB 1: by cost centre ─────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        by_cc = (
            flt.groupby(["cost_center_code", "cost_center_name"], as_index=False)
            .agg(
                total=("total_depreciation_amount", "sum"),
                assets=("asset_count", "sum"),
            )
            .sort_values("total", ascending=False)
        )
        fig = px.bar(
            by_cc,
            x="cost_center_code",
            y="total",
            color="cost_center_code",
            text="assets",
            title="Amortizacija po centru troška",
            labels={
                "cost_center_code": "",
                "total": "Amortizacija (RSD)",
                "assets": "Sredstava",
            },
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.pie(
            by_cc,
            values="total",
            names="cost_center_code",
            title="Udeo centara troška u amortizaciji",
            hole=0.4,
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    # cost centre × category heatmap
    pivot = flt.groupby(["cost_center_code", "category_code"], as_index=False).agg(
        total=("total_depreciation_amount", "sum")
    )
    if (
        len(pivot["cost_center_code"].unique()) > 1
        and len(pivot["category_code"].unique()) > 1
    ):
        heat_df = pivot.pivot(
            index="cost_center_code", columns="category_code", values="total"
        ).fillna(0)
        fig3 = px.imshow(
            heat_df,
            title="Amortizacija — centri troška vs. kategorije (RSD)",
            labels={
                "x": "Kategorija",
                "y": "Centar troška",
                "color": "Amortizacija (RSD)",
            },
            color_continuous_scale="Blues",
            aspect="auto",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Summary table
    st.subheader("Pregled po centru troška")
    cc_summary = (
        flt.groupby(
            ["cost_center_code", "cost_center_name", "organization_unit_code"],
            as_index=False,
        )
        .agg(
            periodi=("period_code", "nunique"),
            sredstava=("asset_count", "sum"),
            ukupno=("total_depreciation_amount", "sum"),
        )
        .sort_values("ukupno", ascending=False)
        .rename(
            columns={
                "cost_center_code": "Šifra CT",
                "cost_center_name": "Naziv CT",
                "organization_unit_code": "OJ",
                "periodi": "Periodi",
                "sredstava": "Sredstava",
                "ukupno": "Ukupna amortizacija",
            }
        )
    )
    st.dataframe(
        cc_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ukupna amortizacija": st.column_config.NumberColumn(format="%.2f RSD")
        },
    )

# ── TAB 2: monthly trend ──────────────────────────────────────────────────────
with tab2:
    # monthly total
    monthly = (
        flt.groupby("period_code", as_index=False)
        .agg(total=("total_depreciation_amount", "sum"))
        .sort_values("period_code")
    )
    fig4 = px.bar(
        monthly,
        x="period_code",
        y="total",
        title="Mesečna amortizacija po periodu (svi centri troška)",
        labels={"period_code": "Period", "total": "Amortizacija (RSD)"},
    )
    fig4.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

    # stacked by cost centre
    by_cc_period = (
        flt.groupby(["period_code", "cost_center_code"], as_index=False)
        .agg(total=("total_depreciation_amount", "sum"))
        .sort_values("period_code")
    )
    fig5 = px.bar(
        by_cc_period,
        x="period_code",
        y="total",
        color="cost_center_code",
        title="Amortizacija po centru troška i periodu",
        labels={
            "period_code": "Period",
            "total": "Amortizacija (RSD)",
            "cost_center_code": "Centar troška",
        },
        barmode="stack",
    )
    fig5.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)

    # Detail table
    st.subheader("Mesečni detalj")
    detail = (
        flt.groupby(
            [
                "period_code",
                "fiscal_year",
                "fiscal_period",
                "cost_center_code",
                "cost_center_name",
            ],
            as_index=False,
        )
        .agg(
            sredstava=("asset_count", "sum"),
            ukupno=("total_depreciation_amount", "sum"),
        )
        .sort_values(["period_code", "cost_center_code"])
        .rename(
            columns={
                "period_code": "Period",
                "fiscal_year": "Godina",
                "fiscal_period": "Fisk. period",
                "cost_center_code": "Centar troška",
                "cost_center_name": "Naziv CT",
                "sredstava": "Sredstava",
                "ukupno": "Amortizacija",
            }
        )
    )
    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amortizacija": st.column_config.NumberColumn(format="%.2f RSD")
        },
    )
