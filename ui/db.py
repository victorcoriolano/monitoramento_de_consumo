import os

from sqlalchemy import create_engine

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # volta para a raiz
db_path = os.path.join(base_dir, "consumo.db")

engine = create_engine(f"sqlite:///../{db_path}")
