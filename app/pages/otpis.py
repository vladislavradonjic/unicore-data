import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from db import load, fmt_rsd

st.title("Registar otpisa")

df = load("DISP_t1_T")

# ── sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filteri")
    sel_lifecycle = st.multiselect(
        "Vrsta otpisa",
        sorted(df["lifecycle_status"].dropna().unique()),
        default=list(df["lifecycle_status"].dropna().unique()),
    )
    sel_type = st.multiselect("Tip imovine", sorted(df["asset_type"].dropna().unique()))
    sel_cat = st.multiselect(
        "Kategorija", sorted(df["category_code"].dropna().unique())
    )
    sel_wf = st.multiselect(
        "Status toka odobrenja",
        sorted(df["workflow_status"].dropna().unique()),
    )

flt = df.copy()
if sel_lifecycle:
    flt = flt[flt["lifecycle_status"].isin(sel_lifecycle)]
if sel_type:
    flt = flt[flt["asset_type"].isin(sel_type)]
if sel_cat:
    flt = flt[flt["category_code"].isin(sel_cat)]
if sel_wf:
    flt = flt[flt["workflow_status"].isin(sel_wf)]

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ukupno otpisanih", len(flt))
k2.metric("Nabavna vrednost", fmt_rsd(flt["acquisition_amount"].sum()))
k3.metric("Neto vrednost (otpis)", fmt_rsd(flt["net_book_value_at_disposal"].sum()))
k4.metric("Akumulirana amort.", fmt_rsd(flt["accumulated_depreciation"].sum()))
k5.metric(
    "Čekaju odobrenje",
    int((flt["workflow_status"] == "PENDING").sum())
    if "workflow_status" in flt.columns
    else 0,
)

st.divider()

tab1, tab2 = st.tabs(["Pregled", "Detalji"])

# ── TAB 1: overview charts ────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        by_type = flt.groupby("lifecycle_status", as_index=False).agg(
            count=("asset_id", "count")
        )
        fig = px.pie(
            by_type,
            values="count",
            names="lifecycle_status",
            title="Otpisana sredstva po vrsti otpisa",
            hole=0.45,
            color="lifecycle_status",
            color_discrete_map={
                "DISPOSED": "#e74c3c",
                "SOLD": "#3498db",
                "DONATED": "#2ecc71",
            },
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        by_cat = (
            flt.groupby(["category_code", "category_name"], as_index=False)
            .agg(count=("asset_id", "count"), acq=("acquisition_amount", "sum"))
            .sort_values("acq", ascending=False)
        )
        fig2 = px.bar(
            by_cat,
            x="category_code",
            y="acq",
            color="category_code",
            text="count",
            title="Nabavna vrednost otpisanih po kategoriji",
            labels={
                "category_code": "",
                "acq": "Nabavna vrednost (RSD)",
                "count": "Broj",
            },
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # disposal by year (using disposal_date)
    if "disposal_date" in flt.columns and flt["disposal_date"].notna().any():
        flt_dated = flt[flt["disposal_date"].notna()].copy()
        flt_dated["disposal_year"] = pd.to_datetime(flt_dated["disposal_date"]).dt.year
        by_year = (
            flt_dated.groupby("disposal_year", as_index=False)
            .agg(count=("asset_id", "count"), acq=("acquisition_amount", "sum"))
            .sort_values("disposal_year")
        )
        fig3 = px.bar(
            by_year,
            x="disposal_year",
            y="acq",
            text="count",
            title="Otpisi po godini (nabavna vrednost)",
            labels={
                "disposal_year": "Godina",
                "acq": "Nabavna vrednost (RSD)",
                "count": "Broj",
            },
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(xaxis_type="category")
        st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: detail table ───────────────────────────────────────────────────────
with tab2:
    st.subheader(f"Lista otpisanih sredstava ({len(flt)} zapisa)")

    cols = [
        "asset_number",
        "asset_name",
        "asset_type",
        "category_code",
        "lifecycle_status",
        "activation_date",
        "disposal_date",
        "acquisition_amount",
        "accumulated_depreciation",
        "net_book_value_at_disposal",
        "request_number",
        "workflow_status",
        "maker_username",
        "checker_username",
    ]
    # only keep columns that exist in the dataframe
    cols = [c for c in cols if c in flt.columns]

    display = flt[cols].rename(
        columns={
            "asset_number": "Broj OS",
            "asset_name": "Naziv",
            "asset_type": "Tip",
            "category_code": "Kategorija",
            "lifecycle_status": "Vrsta otpisa",
            "activation_date": "Aktivacija",
            "disposal_date": "Datum otpisa",
            "acquisition_amount": "Nabavna vred.",
            "accumulated_depreciation": "Akum. amort.",
            "net_book_value_at_disposal": "Neto vred. (otpis)",
            "request_number": "Zahtev",
            "workflow_status": "Status odobrenja",
            "maker_username": "Uneo",
            "checker_username": "Odobrio",
        }
    )

    st.dataframe(
        display.sort_values("Datum otpisa", ascending=False)
        if "Datum otpisa" in display.columns
        else display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Nabavna vred.": st.column_config.NumberColumn(format="%.0f RSD"),
            "Akum. amort.": st.column_config.NumberColumn(format="%.0f RSD"),
            "Neto vred. (otpis)": st.column_config.NumberColumn(format="%.0f RSD"),
        },
    )
