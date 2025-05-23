import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ajuste a URL conforme seu DB ou aponte pra API:
engine = create_engine("sqlite:///../consumo.db")

st.title("🏠 Monitor de Consumo de Água")

atividades = ["todas"] + [row[0] for row in pd.read_sql("SELECT DISTINCT atividade FROM consumo_agua", engine).values]
escolha = st.sidebar.selectbox("Atividade", atividades)
dias = st.sidebar.slider("Ultimos dias", 1, 30, 7)

query = "SELECT * FROM consumo_agua WHERE timestamp >= date('now','-{} day')".format(dias)
if escolha != "todas":
    query += f" AND atividade = '{escolha}'"

df = pd.read_sql(query, engine, parse_dates=["timestamp"])
df = df.set_index("timestamp")

st.line_chart(df["volume_litros"])
st.write("Dados brutos:", df)
