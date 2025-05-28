import pandas as pd
import streamlit as st
import plotly.express as px
from db import engine
from util import carregar_dados, dias_monitorados

st.title("💧 Dashboard - Consumo de Água")

dias = st.sidebar.slider("Últimos dias", 1, 30, 7)
atividades = ["Todas"] + pd.read_sql(f"SELECT DISTINCT atividade FROM consumo_agua", engine)["atividade"].tolist()
atividade = st.sidebar.selectbox("Atividade", atividades)

def calcular_custo(litros):
    return 50 if litros <= 10000 else 50 + ((litros - 10000) / 1000) * 2.29

df = carregar_dados("consumo_agua", dias, engine, "atividade", atividade)

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado.")
else:
    total = df["volume_litros"].sum()
    max_atividade = df.groupby("atividade")["volume_litros"].sum().idxmax()
    min_atividade = df.groupby("atividade")["volume_litros"].sum().idxmin()
    dias_mon = dias_monitorados("consumo_agua", engine)

    col1, col2, col3 = st.columns(3)
    col1.metric("💧 Total Consumido", f"{total:.1f} L")
    col2.metric("📈 Maior Consumo", max_atividade)
    col3.metric("📉 Menor Consumo", min_atividade)

    st.subheader("📅 Consumo ao longo do tempo")
    st.line_chart(df["volume_litros"])

    if atividade == "Todas":
        st.subheader("🥧 Por Atividade")
        fig_pie = px.pie(df.groupby("atividade")["volume_litros"].sum().reset_index(),
                     values="volume_litros", names="atividade")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📊 Por Dia")
    fig_bar = px.bar(df.resample("D").sum(), y="volume_litros", title="Consumo Diário")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("💸 Gastos")
    st.write(f"R$ {calcular_custo(total):.2f} nos últimos {dias_mon} dias.")

    with st.expander("📄 Dados Brutos"):
        st.dataframe(df)
