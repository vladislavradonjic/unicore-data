import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

MARTS = "unicore_analytics_marts"
SOURCES = "unicore_analytics"


@st.cache_resource
def _engine():
    return create_engine(
        "postgresql+psycopg2://unicore:unicore@localhost:5433/unicore",
        pool_pre_ping=True,
    )


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


def load(table: str, schema: str = MARTS) -> pd.DataFrame:
    return query(f'SELECT * FROM {schema}."{table}"')


def fmt_rsd(value) -> str:
    return f"{value:,.0f} RSD"
