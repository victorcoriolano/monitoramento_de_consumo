import os

from sqlalchemy import create_engine

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # volta para a raiz
db_path = os.path.join(base_dir, "consumo.db")

# Apenas para debug: veja se o arquivo realmente existe
print("📁 Caminho do banco:", db_path)
print("🗂️ Existe?", os.path.exists(db_path))

engine = create_engine(f"sqlite:///{db_path}")
