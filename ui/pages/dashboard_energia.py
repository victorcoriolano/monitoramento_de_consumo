import pandas as pd
import streamlit as st
import plotly.express as px
from db import engine
from util import carregar_dados, dias_monitorados

st.title("💧 Dashboard - Consumo de Energia")

dias = st.sidebar.slider("Últimos dias", 1, 30, 7)
equipamentos = ["Todas"] + pd.read_sql(f"SELECT DISTINCT equipamento FROM consumo_energia", engine)["equipamento"].tolist()
equipamento = st.sidebar.selectbox("equipamento", equipamentos)

def calcular_custo(kwh):
    return kwh * 0.656

df = carregar_dados("consumo_energia", dias, engine, "equipamento", equipamento)

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado.")
else:
    total = df["gasto_h"].sum()
    max_equipamento = df.groupby("equipamento")["gasto_h"].sum().idxmax()
    min_equipamento = df.groupby("equipamento")["gasto_h"].sum().idxmin()
    dias_mon = dias_monitorados("consumo_energia", engine)

    col1, col2, col3 = st.columns(3)
    col1.metric("💧 Total Consumido", f"{total:.1f} L")
    col2.metric("📈 Maior Consumo", max_equipamento)
    col3.metric("📉 Menor Consumo", min_equipamento)

    st.subheader("📅 Consumo ao longo do tempo")
    st.line_chart(df["gasto_h"])

    if equipamento == "Todas":
        st.subheader("🔧🔧 Por Objeto")
        fig_pie = px.pie(df.groupby("equipamento")["gasto_h"].sum().reset_index(),
                     values="gasto_h", names="equipamento")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📊 Por Dia")
    fig_bar = px.bar(df.resample("D").sum(), y="gasto_h", title="Consumo Diário")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("💸 Gastos")
    st.write(f"R$ {calcular_custo(total):.2f} nos últimos {dias_mon} dias.")

    with st.expander("📄 Dados Brutos"):
        st.dataframe(df)
