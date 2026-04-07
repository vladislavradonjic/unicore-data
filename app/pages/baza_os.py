import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
from db import load, fmt_rsd

st.title("Baza OS")

df = load("ABOS_t1_T")

# ── sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filteri")
    sel_status = st.multiselect(
        "Status", sorted(df["lifecycle_status"].dropna().unique()),
        default=["ACTIVE"],
    )
    sel_type = st.multiselect(
        "Tip imovine", sorted(df["asset_type"].dropna().unique())
    )
    sel_cat = st.multiselect(
        "Kategorija", sorted(df["category_code"].dropna().unique())
    )

flt = df.copy()
if sel_status: flt = flt[flt["lifecycle_status"].isin(sel_status)]
if sel_type:   flt = flt[flt["asset_type"].isin(sel_type)]
if sel_cat:    flt = flt[flt["category_code"].isin(sel_cat)]

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ukupno sredstava",   len(flt))
k2.metric("Aktivnih",           int((flt["lifecycle_status"] == "ACTIVE").sum()))
k3.metric("Nabavna vrednost",   fmt_rsd(flt["acquisition_amount"].sum()))
k4.metric("Sadašnja vrednost",  fmt_rsd(flt["net_amount"].sum()))
k5.metric("Potpuno amortizonih",
          int((flt["net_amount"] == 0).sum()))

st.divider()

# ── charts ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    by_cat = (
        flt.groupby(["category_code", "category_name"], as_index=False)
        .agg(count=("asset_id", "count"), net_amount=("net_amount", "sum"))
        .sort_values("net_amount", ascending=False)
    )
    fig = px.bar(
        by_cat, x="category_code", y="net_amount",
        color="category_code", text="count",
        title="Sadašnja vrednost po kategoriji",
        labels={"category_code": "", "net_amount": "Sadašnja vrednost (RSD)", "count": "Broj"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    by_status = flt.groupby("lifecycle_status", as_index=False).agg(
        count=("asset_id", "count")
    )
    fig2 = px.pie(
        by_status, values="count", names="lifecycle_status",
        title="Sredstva po statusu", hole=0.45,
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

# ── table ─────────────────────────────────────────────────────────────────────
st.subheader("Pregled sredstava")

display = flt[[
    "asset_number", "asset_name", "asset_type", "category_code",
    "lifecycle_status", "activation_date",
    "acquisition_amount", "net_amount",
    "location_name", "cost_center_name", "accountable_person_name",
]].rename(columns={
    "asset_number":           "Broj OS",
    "asset_name":             "Naziv",
    "asset_type":             "Tip",
    "category_code":          "Kategorija",
    "lifecycle_status":       "Status",
    "activation_date":        "Aktivacija",
    "acquisition_amount":     "Nabavna vred.",
    "net_amount":             "Sadašnja vred.",
    "location_name":          "Lokacija",
    "cost_center_name":       "Centar troška",
    "accountable_person_name": "Računopolagač",
})

st.dataframe(
    display.sort_values("Broj OS"),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Nabavna vred.": st.column_config.NumberColumn(format="%.0f RSD"),
        "Sadašnja vred.": st.column_config.NumberColumn(format="%.0f RSD"),
    },
)
