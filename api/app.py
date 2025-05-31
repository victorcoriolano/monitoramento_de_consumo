import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from api.models import ConsumoAgua, ConsumoEnergia
from api.tables import consumo_agua, consumo_energia
from sqlalchemy import create_engine, Table, MetaData


DATABASE_URL = "sqlite:///../consumo.db"  

app = FastAPI()
engine = create_engine(DATABASE_URL)
metadata = MetaData()

API_URL = "http://127.0.0.1:8000"


# === ENDPOINTS ÁGUA ===
@app.post("/consumo_agua")
def cria_consumo_agua(consumo: ConsumoAgua):
    ins = consumo_agua.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}

@app.get("/consumo_agua")
def lista_consumo_agua(atividade: str):
    sel = consumo_agua.select()
    if atividade:
        sel = sel.where(consumo_agua.c.atividade == atividade)
    with engine.connect() as conn:
        rows = conn.execute(sel).fetchall()
    return [dict(row) for row in rows]

# === ENDPOINTS ENERGIA ===
@app.post("/consumo_energia")
def cria_consumo_energia(consumo: ConsumoEnergia):
    ins = consumo_energia.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}

@app.get("/consumo_energia")
def lista_consumo_energia(equipamento: str):
    sel = consumo_energia.select()
    if equipamento:
        sel = sel.where(consumo_energia.c.equipamento == equipamento)
    with engine.connect() as conn:
        rows = conn.execute(sel).fetchall()
    return [dict(row) for row in rows]
