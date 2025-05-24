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
st.markdown("Este painel visualiza dados de **consumo de água**, com filtros por atividade e período.")

# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.header("🔍 Filtros")

tipo_consumo = st.sidebar.selectbox("Tipo de Consumo", ["Água", "Energia (em breve)", "Higiene (em breve)"])

dias = st.sidebar.slider("Últimos dias", min_value=1, max_value=30, value=7)

# Consulta personalizada
if tipo_consumo == "Água":
    tabela = "consumo_agua"
    df_atividades = pd.read_sql(f"SELECT DISTINCT atividade FROM {tabela}", engine)
    atividades = ["Todas"] + df_atividades["atividade"].tolist()
    atividade = st.sidebar.selectbox("Atividade", atividades)

    query = f"""
        SELECT * FROM {tabela}
        WHERE timestamp >= date('now','-{dias} day')
    """
    if atividade != "Todas":
        query += f" AND atividade = '{atividade}'"

    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    df = df.set_index("timestamp").sort_index()

    if not df.empty:
        # ------------------------------
        # MÉTRICAS
        # ------------------------------
        total = df["volume_litros"].sum()
        max_atividade = df.groupby("atividade")["volume_litros"].sum().idxmax()
        min_atividade = df.groupby("atividade")["volume_litros"].sum().idxmin()

        col1, col2, col3 = st.columns(3)
        col1.metric("💧 Total Consumido", f"{total:.1f} L")
        col2.metric("📈 Atividade com Maior Consumo", max_atividade)
        col3.metric("📉 Atividade com Menor Consumo", min_atividade)

        # ------------------------------
        # GRÁFICOS
        # ------------------------------
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

        # ------------------------------
        # DADOS BRUTOS
        # ------------------------------
        with st.expander("📄 Mostrar dados brutos"):
            st.dataframe(df)
    else:
        st.warning("⚠️ Nenhum dado encontrado para os filtros escolhidos.")
else:
    st.info("🔧 Essa funcionalidade ainda está em desenvolvimento.")
