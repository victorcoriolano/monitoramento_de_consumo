import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Banco de dados local SQLite
engine = create_engine("sqlite:///../consumo.db")

# ------------------------------
# TÍTULO E CONFIG
# ------------------------------
st.set_page_config(
    page_title="Monitor de Consumo",
    layout="wide",
    page_icon="💧"
)

st.title("📊 Monitor de Consumo Doméstico")
st.markdown("Este painel visualiza dados de **consumo doméstico**, incluindo água, energia e produtos de higiene e limpeza.")

# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.header("🔍 Filtros")

tipo_consumo = st.sidebar.selectbox("Tipo de Consumo", ["Água", "Energia", "Higiene e Limpeza"])
dias = st.sidebar.slider("Últimos dias", min_value=1, max_value=90, value=7)

# ------------------------------
# FUNÇÃO UTILITÁRIA
# ------------------------------
def carregar_dados(tabela, dias, filtro_col=None, filtro_valor=None):
    query = f"SELECT * FROM {tabela} WHERE timestamp >= date('now','-{dias} day')"
    if filtro_col and filtro_valor and filtro_valor != "Todas":
        query += f" AND {filtro_col} = '{filtro_valor}'"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    return df.set_index("timestamp").sort_index()

# ------------------------------
# CONSUMO DE ÁGUA
# ------------------------------
if tipo_consumo == "Água":
    tabela = "consumo_agua"
    df_atividades = pd.read_sql(f"SELECT DISTINCT atividade FROM {tabela}", engine)
    atividades = ["Todas"] + df_atividades["atividade"].tolist()
    atividade = st.sidebar.selectbox("Atividade", atividades)

    df = carregar_dados(tabela, dias, "atividade", atividade)

    if not df.empty:
        total = df["volume_litros"].sum()
        max_atividade = df.groupby("atividade")["volume_litros"].sum().idxmax()
        min_atividade = df.groupby("atividade")["volume_litros"].sum().idxmin()

        col1, col2, col3 = st.columns(3)
        col1.metric("💧 Total Consumido", f"{total:.1f} L")
        col2.metric("📈 Atividade com Maior Consumo", max_atividade)
        col3.metric("📉 Atividade com Menor Consumo", min_atividade)

        st.subheader("📅 Consumo ao longo do tempo")
        st.line_chart(df["volume_litros"])

        st.subheader("🥧 Distribuição por atividade")
        graf_pizza = df.groupby("atividade")["volume_litros"].sum().reset_index()
        fig = px.pie(graf_pizza, values="volume_litros", names="atividade", title="Porcentagem de Consumo")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Volume por dia")
        df_diario = df.resample("D").sum()
        fig_barra = px.bar(df_diario, y="volume_litros", title="Consumo Diário")
        st.plotly_chart(fig_barra, use_container_width=True)

        with st.expander("📄 Mostrar dados brutos"):
            st.dataframe(df)
    else:
        st.warning("⚠️ Nenhum dado encontrado para os filtros escolhidos.")

# ------------------------------
# CONSUMO DE ENERGIA
# ------------------------------
elif tipo_consumo == "Energia":
    tabela = "consumo_energia"
    df = carregar_dados(tabela, dias)

    if not df.empty:
        total = df["gasto_h"].sum()
        col1, col2 = st.columns(2)
        col1.metric("⚡ Energia Total", f"{total:.2f} kWh")
        col2.metric("📅 Dias Monitorados", df.index.nunique())

        st.subheader("📅 Consumo de Energia ao longo do tempo")
        fig = px.line(df, y="gasto_h", title="Consumo de Energia")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Mostrar dados brutos"):
            st.dataframe(df)
    else:
        st.warning("⚠️ Nenhum dado de energia encontrado.")

# ------------------------------
# CONSUMO DE HIGIENE E LIMPEZA
# ------------------------------
elif tipo_consumo == "Higiene e Limpeza":
    tabela = "consumo_higiene"
    df_produtos = pd.read_sql(f"SELECT DISTINCT produto FROM {tabela}", engine)
    produtos = ["Todos"] + df_produtos["produto"].tolist()
    produto = st.sidebar.selectbox("Produto", produtos)

    df = carregar_dados(tabela, dias, "produto", produto)

    if not df.empty:
        total = df["quantidade"].sum()
        col1, col2 = st.columns(2)
        col1.metric("🧴 Total Comprado", f"{total:.2f}")
        col2.metric("🛒 Compras registradas", len(df))

        st.subheader("📅 Compras ao longo do tempo")
        fig = px.bar(df, y="quantidade", title="Compras por Data")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📦 Distribuição por Produto")
        dist = df.groupby("produto")["quantidade"].sum().reset_index()
        fig2 = px.pie(dist, values="quantidade", names="produto")
        st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📄 Mostrar dados brutos"):
            st.dataframe(df)
    else:
        st.warning("⚠️ Nenhum dado de higiene/limpeza encontrado.")
