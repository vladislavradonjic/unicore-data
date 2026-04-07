import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db import load, query, fmt_rsd

st.title("Kartica OS")

# Load asset list for selector (from ABOS for enriched names)
assets_df = load("ABOS_t1_T")

# ── asset selector ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Odabir sredstva")

    sel_type = st.multiselect(
        "Tip imovine", sorted(assets_df["asset_type"].dropna().unique())
    )
    sel_cat = st.multiselect(
        "Kategorija", sorted(assets_df["category_code"].dropna().unique())
    )

    asset_flt = assets_df.copy()
    if sel_type:
        asset_flt = asset_flt[asset_flt["asset_type"].isin(sel_type)]
    if sel_cat:
        asset_flt = asset_flt[asset_flt["category_code"].isin(sel_cat)]

    asset_options = {
        f"{row['asset_number']} — {row['asset_name']}": row["asset_id"]
        for _, row in asset_flt.sort_values("asset_number").iterrows()
    }

    if not asset_options:
        st.warning("Nema sredstava za odabrane filtere.")
        st.stop()

    selected_label = st.selectbox("Sredstvo", list(asset_options.keys()))
    selected_asset_id = asset_options[selected_label]

# ── load asset card events ────────────────────────────────────────────────────
kart = load("KART_T")
kart_asset = kart[kart["asset_id"] == selected_asset_id].copy()

# ── asset header info ─────────────────────────────────────────────────────────
asset_row = assets_df[assets_df["asset_id"] == selected_asset_id]
if len(asset_row) > 0:
    ar = asset_row.iloc[0]
    st.subheader(f"{ar['asset_number']} — {ar['asset_name']}")

    h1, h2, h3, h4, h5 = st.columns(5)
    h1.metric("Status", ar["lifecycle_status"])
    h2.metric("Kategorija", ar["category_code"])
    h3.metric("Nabavna vrednost", fmt_rsd(ar["acquisition_amount"]))
    h4.metric("Sadašnja vrednost", fmt_rsd(ar["net_amount"]))
    h5.metric("Lokacija", ar.get("location_name", "—") or "—")

st.divider()

if len(kart_asset) == 0:
    st.info("Nema istorije događaja za odabrano sredstvo.")
    st.stop()

# ── event type badges (counts) ────────────────────────────────────────────────
event_counts = kart_asset["event_type"].value_counts()
cols = st.columns(len(event_counts))
event_colors = {
    "ACTIVATION": "#2ecc71",
    "DISPOSAL": "#e74c3c",
    "LOCATION_CHANGE": "#3498db",
    "CUSTODIAN_CHANGE": "#9b59b6",
    "DEPRECIATION": "#f39c12",
}
for i, (etype, cnt) in enumerate(event_counts.items()):
    cols[i].metric(etype.replace("_", " "), cnt)

st.divider()

tab1, tab2 = st.tabs(["Hronologija događaja", "Amortizacija"])

# ── TAB 1: event timeline ─────────────────────────────────────────────────────
with tab1:
    non_depr = kart_asset[kart_asset["event_type"] != "DEPRECIATION"].copy()
    non_depr["event_date"] = pd.to_datetime(non_depr["event_date"], errors="coerce")

    if len(non_depr) > 0:
        # Timeline scatter plot
        fig = px.scatter(
            non_depr.sort_values("event_date"),
            x="event_date",
            y="event_type",
            color="event_type",
            symbol="event_type",
            hover_data=["reference_number", "actor", "from_value", "to_value", "note"],
            title="Hronologija događaja (bez amortizacije)",
            labels={"event_date": "Datum", "event_type": "Tip događaja"},
            color_discrete_map=event_colors,
            size_max=12,
        )
        fig.update_traces(marker=dict(size=12))
        fig.update_layout(yaxis_title="", xaxis_title="Datum događaja")
        st.plotly_chart(fig, use_container_width=True)

    # Full event table
    st.subheader("Svi događaji")
    display_cols = [
        "event_date",
        "event_type",
        "reference_number",
        "actor",
        "from_value",
        "to_value",
        "note",
    ]
    display_cols = [c for c in display_cols if c in kart_asset.columns]

    st.dataframe(
        non_depr[display_cols]
        .sort_values("event_date")
        .rename(
            columns={
                "event_date": "Datum",
                "event_type": "Tip događaja",
                "reference_number": "Referenca",
                "actor": "Korisnik",
                "from_value": "Iz",
                "to_value": "U",
                "note": "Napomena",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ── TAB 2: depreciation history ────────────────────────────────────────────────
with tab2:
    depr_events = kart_asset[kart_asset["event_type"] == "DEPRECIATION"].copy()
    depr_events["event_date"] = pd.to_datetime(
        depr_events["event_date"], errors="coerce"
    )
    depr_events["depreciation_amount"] = pd.to_numeric(
        depr_events["to_value"], errors="coerce"
    )
    depr_events = depr_events.sort_values("event_date")

    if len(depr_events) == 0:
        st.info("Nema knjiženja amortizacije za ovo sredstvo.")
    else:
        depr_events["cumulative"] = depr_events["depreciation_amount"].cumsum()

        fig_d = px.bar(
            depr_events,
            x="note",
            y="depreciation_amount",
            title="Mesečna amortizacija po periodu",
            labels={"note": "Period", "depreciation_amount": "Amortizacija (RSD)"},
        )
        fig_d.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_d, use_container_width=True)

        fig_cum = px.line(
            depr_events,
            x="note",
            y="cumulative",
            title="Kumulativna amortizacija",
            labels={"note": "Period", "cumulative": "Kumulativna amortizacija (RSD)"},
            markers=True,
        )
        fig_cum.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cum, use_container_width=True)

        st.subheader(f"Pregled knjiženja ({len(depr_events)} perioda)")
        st.dataframe(
            depr_events[
                [
                    "note",
                    "depreciation_amount",
                    "cumulative",
                    "reference_number",
                    "actor",
                ]
            ].rename(
                columns={
                    "note": "Period",
                    "depreciation_amount": "Amortizacija",
                    "cumulative": "Kumulativ",
                    "reference_number": "Broj obračuna",
                    "actor": "Pokrenuo",
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amortizacija": st.column_config.NumberColumn(format="%.2f RSD"),
                "Kumulativ": st.column_config.NumberColumn(format="%.2f RSD"),
            },
        )
