import streamlit as st

st.set_page_config(
    page_title="UniCore Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/baza_os.py",       title="Baza OS"),
    st.Page("pages/amortizacija.py",  title="Amortizacija"),
    st.Page("pages/projekcija.py",    title="Projekcija"),
    st.Page("pages/otpis.py",         title="Otpis"),
    st.Page("pages/kartica_os.py",    title="Kartica OS"),
    st.Page("pages/centri_troska.py", title="Centri troška"),
]

pg = st.navigation(pages)
pg.run()
