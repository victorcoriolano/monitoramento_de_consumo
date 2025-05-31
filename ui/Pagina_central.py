import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

st.set_page_config(page_title="Monitor de Consumo", layout="wide", page_icon="📈")
st.title("📊 Monitor de Consumo Doméstico")
st.markdown("Use o menu lateral para navegar entre dashboards e inserir dados.")
