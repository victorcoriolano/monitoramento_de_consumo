import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import engine


# ========== Funções auxiliares ==========
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

    consumo_mensal = (
        atividade_df.groupby(['mes', 'produto_id'])['porcentagem_gasto'].sum().reset_index()
        .merge(produto_df[['id', 'nome', 'unidade']], left_on='produto_id', right_on='id', how='left')
    )

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
st.set_page_config(page_title="Monitor de Produtos", layout="wide", page_icon="🧴")
st.title("🧺🧼 Dashboard de Consumo de Produtos de Higiene e Limpeza")

# Carrega dados
produto_df, compra_df, atividade_df = carregar_dados()
consumo_mensal, gasto_mensal = calcular_consumo_mensal(atividade_df, produto_df, compra_df)

# Seção: Visão Geral
st.markdown("## 📌 Visão Geral")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total de Produtos Cadastrados", produto_df.shape[0])
    st.metric("Total de Atividades Registradas", atividade_df.shape[0])
with col2:
    gasto_total = compra_df['gasto_total'].sum()
    st.metric("💰 Gasto Total Registrado", f"R$ {gasto_total:.2f}")

st.divider()

# Seção: Consumo e Gasto Mensal
st.markdown("## 📈 Consumo e Gasto por Mês")

tab1, tab2 = st.tabs(["📦 Volume Consumido", "💵 Gasto por Produto"])

with tab1:
    st.subheader("Consumo (volume por produto/mês)")
    st.dataframe(consumo_mensal)

with tab2:
    st.subheader("Gasto total (por produto/mês)")
    st.dataframe(gasto_mensal)

st.divider()

# Seção: Produtos Registrados
st.markdown("## 🧴 Produtos Registrados")
st.dataframe(produto_df[['nome', 'unidade', 'quantidade_restante', 'preco_unitario']], use_container_width=True)

st.divider()




# Seção: Preços dos Produtos
st.markdown("## 💲 Preços Unitários dos Produtos")

df_precos = produto_df[['nome', 'preco_unitario']]
st.bar_chart(df_precos.set_index("nome"))

st.divider()

# Seção: Dados Brutos e Exportação
with st.expander("📄 Visualizar Dados Brutos"):
    st.dataframe(atividade_df)
    st.dataframe(produto_df)
    st.dataframe(compra_df)

    st.download_button(
        label="⬇️ Baixar dados em CSV",
        data=pd.concat([atividade_df, produto_df, compra_df]).to_csv(index=False).encode('utf-8'),
        file_name='dados_brutos.csv',
        mime='text/csv',
    )
