# monitor_consumo.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Configuração inicial
st.set_page_config(page_title="Monitor de Consumo", layout="wide", page_icon="💧")
st.title("📊 Monitor de Consumo Doméstico")
st.markdown("Visualize o consumo de **água, energia e produtos de higiene/limpeza**.")

# Banco de dados
engine = create_engine("sqlite:///../consumo.db")

# Sidebar
st.sidebar.header("🔍 Filtros")
tipo_consumo = st.sidebar.selectbox("Tipo de Consumo", ["Água", "Energia", "Higiene e Limpeza"])
dias = st.sidebar.slider("Últimos dias", 1, 30, 7)

# Funções utilitárias
def carregar_dados(tabela, dias, filtro_col=None, filtro_valor=None):
    query = f"SELECT * FROM {tabela} WHERE timestamp >= date('now','-{dias} day')"
    if filtro_col and filtro_valor and filtro_valor != "Todas":
        query += f" AND {filtro_col} = '{filtro_valor}'"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    return df.set_index("timestamp").sort_index()

def dias_monitorados(tabela):
    df = pd.read_sql(f"SELECT timestamp FROM {tabela}", engine)
    df['data'] = pd.to_datetime(df['timestamp']).dt.date
    return df['data'].nunique()

# Seção Água
def mostrar_agua():
    tabela = "consumo_agua"
    atividades = ["Todas"] + pd.read_sql(f"SELECT DISTINCT atividade FROM {tabela}", engine)["atividade"].tolist()
    atividade = st.sidebar.selectbox("Atividade", atividades)
    df = carregar_dados(tabela, dias, "atividade", atividade)

    def calcular_custo(litros):
        return 50 if litros <= 10000 else 50 + ((litros - 10000) / 1000) * 2.29

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return

    total = df["volume_litros"].sum()
    max_atividade = df.groupby("atividade")["volume_litros"].sum().idxmax()
    min_atividade = df.groupby("atividade")["volume_litros"].sum().idxmin()
    dias_mon = dias_monitorados(tabela)

    col1, col2, col3 = st.columns(3)
    col1.metric("💧 Total Consumido", f"{total:.1f} L")
    col2.metric("📈 Maior Consumo", max_atividade)
    col3.metric("📉 Menor Consumo", min_atividade)

    st.subheader("📅 Consumo ao longo do tempo")
    st.line_chart(df["volume_litros"])

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

    return df

# Seção Energia
def mostrar_energia():
    tabela = "consumo_energia"
    df = carregar_dados(tabela, dias)

    def calcular_custo(kwh): return kwh * 0.656

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return

    total = df["gasto_h"].sum()
    dias_mon = dias_monitorados(tabela)
    col1, col2 = st.columns(2)
    col1.metric("⚡ Total kWh", f"{total:.2f}")
    col2.metric("📅 Dias", dias_mon)

    st.subheader("📅 Consumo ao longo do tempo")
    st.plotly_chart(px.line(df, y="gasto_h"), use_container_width=True)

    st.subheader("📊 Por Dia")
    st.plotly_chart(px.bar(df.resample("D").sum(), y="gasto_h"), use_container_width=True)

    st.subheader("💸 Gastos")
    st.write(f"R$ {calcular_custo(total):.2f} em {dias_mon} dias.")

    with st.expander("📄 Dados Brutos"):
        st.dataframe(df)

    return df

# Seção Higiene e Limpeza
def mostrar_higiene():
    tabela = "consumo_higiene"
    produtos = ["Todas"] + pd.read_sql(f"SELECT DISTINCT produto FROM {tabela}", engine)["produto"].tolist()
    produto = st.sidebar.selectbox("Produto", produtos)
    df = carregar_dados(tabela, dias, "produto", produto)

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return

    total = df["quantidade"].sum()
    col1, col2 = st.columns(2)
    col1.metric("🧴 Total", f"{total:.2f}")
    col2.metric("🛒 Registros", len(df))

    st.subheader("📅 Compras por Data")
    st.plotly_chart(px.bar(df, y="quantidade"), use_container_width=True)

    st.subheader("📦 Distribuição")
    fig = px.pie(df.groupby("produto")["quantidade"].sum().reset_index(),
                 values="quantidade", names="produto")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 Dados Brutos"):
        st.dataframe(df)

    return df

# Exibição condicional por tipo
if tipo_consumo == "Água":
    df = mostrar_agua()
elif tipo_consumo == "Energia":
    df = mostrar_energia()
elif tipo_consumo == "Higiene e Limpeza":
    df = mostrar_higiene()

# Exportação de dados
if 'df' in locals() and df is not None and not df.empty:
    st.divider()
    st.download_button("📥 Baixar CSV", df.reset_index().to_csv(index=False), file_name="dados_consumo.csv")
