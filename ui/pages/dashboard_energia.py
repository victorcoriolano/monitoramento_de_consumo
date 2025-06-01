import pandas as pd
import streamlit as st
import plotly.express as px
from db import engine
from util import carregar_dados, dias_monitorados

st.set_page_config(page_title="Monitor de Energia", layout="wide", page_icon="⚡")
st.title("⚡ Dashboard - Consumo de Energia")
dias_mon = dias_monitorados("consumo_energia", engine)

dias = st.sidebar.slider("Últimos dias", 1, dias_mon, 7)
equipamentos = ["Todas"] + pd.read_sql(f"SELECT DISTINCT equipamento FROM consumo_energia", engine)["equipamento"].tolist()
equipamento = st.sidebar.selectbox("equipamento", equipamentos)

df = pd.read_sql("SELECT * FROM consumo_energia", engine)

df["data"] = pd.to_datetime(df["timestamp"])
df.set_index("data", inplace=True)  # Define como índice para usar .resample()

# Agrupa por mês e soma
df_mensal = df.resample("ME").sum(numeric_only=True)  # soma o volume_litros por mês
    

df_mensal["mes"] = df_mensal.index.strftime("%b/%Y")  # 'Mai/2025', 'Jun/2025' etc.


# Cria gráfico com Plotly   
fig_bar_energia = px.bar(
    df_mensal,
    x="mes",
    y="gasto_h",
    labels={"mes": "Mês", "gasto_kwh": "Consumo (litros)"},
    title="📊 Consumo Mensal de Energia",
    color_discrete_sequence=["skyblue"]
)

# Exibe no Streamlit


def calcular_custo(kwh):
    return kwh * 0.656

df_com_filtro = carregar_dados("consumo_energia", dias, engine, "equipamento", equipamento)

if df_com_filtro.empty:
    st.warning("⚠️ Nenhum dado encontrado.")
else:
    total = df_com_filtro["gasto_h"].sum()
    max_equipamento = df_com_filtro.groupby("equipamento")["gasto_h"].sum().idxmax()
    min_equipamento = df_com_filtro.groupby("equipamento")["gasto_h"].sum().idxmin()
    dias_mon = dias_monitorados("consumo_energia", engine)

    col1, col2, col3 = st.columns(3)
    col1.metric("🪫 Total Consumido", f"{total:.1f} Kwh")
    col2.metric("📈 Maior Consumo", max_equipamento)
    col3.metric("📉 Menor Consumo", min_equipamento)

    st.subheader("📅 Consumo ao longo do tempo")
    st.line_chart(df_com_filtro["gasto_h"])


    if equipamento == "Todas":
        st.subheader("🔧🔧 Por Objeto")
        fig_pie = px.pie(df_com_filtro.groupby("equipamento")["gasto_h"].sum().reset_index(),
                     values="gasto_h", names="equipamento")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📊 Por Dia")
    fig_bar = px.bar(df_com_filtro.resample("D").sum(), y="gasto_h", title="Consumo Diário")
    st.plotly_chart(fig_bar, use_container_width=True)

    
    st.subheader("🗓️ Consumo por Mês")
    st.plotly_chart(fig_bar_energia, use_container_width=True, key="grafico_mes_energia")

    st.subheader("💸 Gastos")
    st.write(f"R$ {calcular_custo(total):.2f} nos últimos {dias_mon} dias.")

    with st.expander("📄 Dados Brutos"):
        st.dataframe(df_com_filtro)
