import streamlit as st
import requests
from datetime import datetime
from api.app import API_URL
from db import engine
import pandas as pd

def inserir_dados(tabela, dados):
    url = f"{API_URL}/{tabela}"
    
    response = requests.post(url, json=dados)
    if response.status_code == 200:
        st.success("Dados inseridos com sucesso!")
    else:
        st.error("Erro ao inserir dados.")

st.set_page_config(page_title="Inserção de Dados", layout="wide", page_icon="📝")
st.title("📥 Inserção de Dados de Consumo")

TIPOS = ["Escolher","Água", "Energia", "Higiene - Limpeza"]
tipo = st.selectbox("Escolha o tipo de consumo", TIPOS)

usuario_id = st.number_input("ID do Usuário", min_value=1, step=1)
timestamp = st.date_input("Data e Hora do Consumo", value=datetime.now())

# === FORMULÁRIO DE INSERÇÃO PARA CADA TIPO ===
if tipo == "Água":
    st.subheader("💧 Inserir Consumo de Água")
    atividades_padrao = [
        "escovar_dentes", "lavar_maos", "lavar_rosto", "lavar_louca",
        "lavar_alimentos", "agua_cozinhar", "tanque", "banho",
        "descarga", "garrafa_agua", "lavar_roupa", "limpeza_casa", "construcao"
    ]

    atividade = st.selectbox("Atividade", atividades_padrao + ["Outro"])
    if atividade == "Outro":
        atividade = st.text_input("Descreva a nova atividade", max_chars=200)

    volume = st.number_input("Volume (litros)", min_value=0.01, format="%.2f")
    timestamp = st.date_input("Data e hora do consumo", value=datetime.now())

    if st.button("Salvar Dados de Água"):
        payload = {
            "usuario_id": usuario_id,
            "atividade": atividade,
            "volume_litros": volume,
            "timestamp": timestamp.isoformat()
        }
        
        r = requests.post(f"{API_URL}/consumo_agua", json=payload)
        if r.ok:
            st.success("Dados inseridos com sucesso!")
        else:
            st.error("Erro ao inserir dados.")

elif tipo == "Energia":
    st.subheader("⚡ Inserir Consumo de Energia")
    equipamentos_padrao = [
        "geladeira", "microondas", "televisao_30_polegadas",
        "televisao_42_polegadas", "iluminacao_casa", "chuveiro_eletrico",
        "carregador_smartphone", "maquina_lavar_roupa"
    ]

    equipamento = st.selectbox("Equipamento", equipamentos_padrao + ["Outro"])
    if equipamento == "Outro":
        equipamento = st.text_input("Descreva o novo equipamento",max_chars=200)

    potencia = st.number_input("Potência (W)", min_value=1.0, format="%.1f")
    duracao_h = st.number_input("Tempo de uso (horas)", min_value=0.01, format="%.2f")
    #timestamp = st.date_input("Data e hora do uso", value=datetime.now())

    if st.button("Salvar Dados de Energia"):
        payload = {
            "usuario_id": usuario_id,
            "equipamento": equipamento,
            "potencia_w": potencia,
            "gasto_h": round((potencia * duracao_h) / 1000, 3),
            "timestamp": timestamp.isoformat()
        }
        r = requests.post(f"{API_URL}/consumo_energia", json=payload)
        if r.ok:
            st.success("Dados inseridos com sucesso!")
        else:
            st.error("Erro ao inserir dados.")

elif tipo == "Higiene - Limpeza":

    produtos_df = pd.read_sql("SELECT nome FROM produto", engine)
    produtos_nome = produtos_df["nome"].tolist()


    st.subheader("🧼 Inserir Consumo de Higiene e Limpeza")
    atividades_padrao = [
        "escovar_dentes", "lavar_maos", "lavar_louca",
        "lavar_roupa", "banho",
        "cagar", "limpar_ouvidos", "passar_desodorante", "assoar_nariz", "limpar_casa"
    ]
    atividade = st.selectbox("Atividade", atividades_padrao + ["Outro"])
    if atividade == "Outro":
        atividade = st.text_input("Descreva a nova atividade", max_chars=200)
    else:
        atividade = atividade
    produto = st.selectbox("Produto", produtos_nome + ["Outro"])
    if produto == "Outro":
        produto = st.text_input("Descreva o nome do produto", max_chars=200)
        unidade_medida = st.text_input("Unidade de Medida", max_chars=200)
        qnt = st.number_input("Quantidade", min_value=0.01, format="%.2f")
        preco_unitario = st.number_input("Preço Unitário", min_value=0.01, format="%.2f")
        stamp = st.date_input("Data e hora do consumo", value=datetime.now())
        salvar = st.button("Salvar Produto")
        if salvar:
            payload = {
                "usuario_id": usuario_id,
                "prod_nome": produto,
                "unidade": unidade_medida,
                "preco_unitario": preco_unitario,
                "quantidade_restante": qnt,
                "timestamp": stamp
            }
            inserir_dados(payload, "produto")
    else:
        porcent = st.slider("Quantidade Consumida (em porcentagem)", min_value=0.01, max_value=100.0, value=0.5, format="%.2f")
        consumo = produtos_df[produtos_df["nome"] == produto]["quantidade_total"] * porcent 
        if st.button("Salvar Dados de Higiene e Limpeza"):
            payload = {
                "usuario_id": usuario_id,
                "produto_id": produtos_df[produtos_df["nome"] == produto]["id"],
                'produto_nome': produto,
                "atividade": atividade,
                "porcentagem_gasto": porcent,
                "consumo": consumo,
                "timestamp": datetime.now()
            }
            inserir_dados(payload, "consumo_higiene")
    
    

    

    