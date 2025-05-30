import pandas as pd
import streamlit as st
import plotly.express as px
from db import engine
from util import dias_monitorados

# ---------------------------
# FUNÇÕES
# ---------------------------

def pegar_todos_produtos():
    """Retorna todos os produtos."""
    return pd.read_sql("SELECT * FROM produto", engine)


def pegar_atividades_produto(id_produto, dias):
    """Retorna atividades de um produto específico nos últimos X dias."""
    query = """
        SELECT * FROM atividade 
        WHERE id_produto = ? AND data >= DATE('now', ?)
    """
    params = [id_produto, dias]
    return pd.read_sql(query, engine, params=params, parse_dates=["data"])


def pegar_todas_atividades(dias):
    """Retorna todas as atividades dos últimos X dias."""
    query = """
        SELECT * FROM atividade 
        WHERE data >= DATE('now', ?)
    """
    return pd.read_sql(query, engine, params=[f"-{dias} days"], parse_dates=["data"])


def pegar_quantidade_total_produto(id_produto, dias):
    """Calcula a quantidade total usada de um produto nos últimos X dias."""
    df = pegar_atividades_produto(id_produto, dias)
    return df["quantidade"].sum() if not df.empty else 0


# ---------------------------
# UI
# ---------------------------

st.title("🧼 Dashboard - Consumo de Produtos de Higiene e Limpeza")

dias = st.sidebar.slider("Últimos dias", 1, 30, 7)

# Carrega produtos
produtos_df = pegar_todos_produtos()
produto_opcoes = ["Todos"] + produtos_df["nome"].tolist()
produto_nome = st.sidebar.selectbox("Produto", produto_opcoes)

# ---------------------------
# VISUALIZAÇÃO
# ---------------------------

if produto_nome == "Todos":
    for id_produto in produtos_df["id"]:
        df = pegar_atividades_produto(id_produto, dias)
        # gráfico de linhas com as atividades de cada produto
        fig = px.line(df, x="data", y="quantidade", color="atividade", title=f"Consumo de {produto_nome}")
        st.plotly_chart(fig)
        st.write(f"💧 Restante: {pegar_quantidade_total_produto(id_produto, dias):.1f} mL")
else:
    
    df = pegar_atividades_produto(produtos_df["id"], dias)

    if df.empty:
        st.warning("⚠️ Nenhuma atividade registrada para esse produto.")
    else:
        # ---------------------
        # Métricas
        # ---------------------
        restante_total = df["quantidade"].sum() * 100  # exemplo: 100ml por unidade
        agrupado = df.groupby("atividade")["quantidade"].sum()

        max_atividade = agrupado.idxmax()
        min_atividade = agrupado.idxmin()

        col1, col2, col3 = st.columns(3)
        col1.metric("💧 Restante", f"{restante_total:.1f} mL")
        col2.metric("📈 Maior Consumo", max_atividade)
        col3.metric("📉 Menor Consumo", min_atividade)

        # ---------------------
        # Gráfico de linha
        # ---------------------
        st.subheader("📅 Consumo ao longo do tempo")
        df_ordenado = df.sort_values("data")
        st.line_chart(df_ordenado.set_index("data")["quantidade"])

        # ---------------------
        # Pizza por atividade
        # ---------------------
        st.subheader("🔧 Consumo por Atividade")
        fig_pie = px.pie(
            agrupado.reset_index(),
            values="quantidade",
            names="atividade",
            title="Distribuição do Consumo por Atividade"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # ---------------------
        # Gráfico de barra diário
        # ---------------------
        st.subheader("📊 Consumo Diário")
        df_por_dia = df.set_index("data").resample("D")["quantidade"].sum()
        fig_bar = px.bar(
            df_por_dia.reset_index(),
            x="data",
            y="quantidade",
            labels={"quantidade": "Quantidade (mL)", "data": "Data"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ---------------------
        # Gastos
        # ---------------------
        st.subheader("💸 Gastos")
        st.info("Cálculo de gastos será adicionado em breve.")

        # ---------------------
        # Dados Brutos
        # ---------------------
        with st.expander("📄 Dados Brutos"):
            st.dataframe(df)
