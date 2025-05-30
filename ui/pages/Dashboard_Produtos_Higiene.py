import streamlit as st
import pandas as pd
from db import engine


# =======================
# Funções auxiliares
# =======================
@st.cache_data
def carregar_dados():
    produto = pd.read_sql("SELECT * FROM produto", engine)
    compra = pd.read_sql("SELECT * FROM compra", engine)
    atividade = pd.read_sql("SELECT * FROM atividade", engine)
    return produto, compra, atividade

def calcular_consumo_mensal(atividade_df, produto_df, compra_df):
    atividade_df['data'] = pd.to_datetime(atividade_df['data'])
    compra_df['data'] = pd.to_datetime(compra_df['data'])

    atividade_df['mes'] = atividade_df['data'].dt.to_period('M')
    compra_df['mes'] = compra_df['data'].dt.to_period('M')

    # Consumo mensal em volume
    consumo_mensal = (
        atividade_df.groupby(['mes', 'produto_id'])['quantidade'].sum().reset_index()
        .merge(produto_df[['id', 'nome', 'unidade']], left_on='produto_id', right_on='id', how='left')
    )

    # Gasto mensal
    gasto_mensal = (
        compra_df.groupby(['mes', 'produto_id'])['gasto_total'].sum().reset_index()
        .merge(produto_df[['id', 'nome']], left_on='produto_id', right_on='id', how='left')
    )

    return consumo_mensal, gasto_mensal

def gasto_por_produto(compra_df, produto_df):
    gasto_total = (
        compra_df.groupby('produto_id')['gasto_total'].sum().reset_index()
        .merge(produto_df[['id', 'nome']], left_on='produto_id', right_on='id', how='left')
        .sort_values(by='gasto_total', ascending=False)
    )
    return gasto_total

# =======================
# Interface do Dashboard
# =======================
st.title("📊 Dashboard de Consumo de Produtos de Higiene e Limpeza")

produto_df, compra_df, atividade_df = carregar_dados()

st.header("1️⃣ Consumo Mensal (volume e valor)")
consumo_mensal, gasto_mensal = calcular_consumo_mensal(atividade_df, produto_df, compra_df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Volume (por produto/mês)")
    st.dataframe(consumo_mensal)

with col2:
    st.subheader("Valor pago (por produto/mês)")
    st.dataframe(gasto_mensal)

st.header("2️⃣ Produtos Registrados")
st.dataframe(produto_df[['nome', 'unidade', 'quantidade_restante', 'preco_unitario']])

st.header("3️⃣ Gasto total por produto")
gasto_produto = gasto_por_produto(compra_df, produto_df)
st.dataframe(gasto_produto)

# Gráfico opcional
st.subheader("🔍 Gráfico de Gasto por Produto")
st.bar_chart(gasto_produto.set_index('nome')['gasto_total'])
