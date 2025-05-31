import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
import api.models as models
from api.tables import consumo_agua, consumo_energia, compra_tbl, atividade_tbl, produto_tbl
from sqlalchemy import create_engine, Table, MetaData


DATABASE_URL = "sqlite:///../consumo.db"  

app = FastAPI()
engine = create_engine(DATABASE_URL)
metadata = MetaData()

API_URL = "http://127.0.0.1:8000"


# === ENDPOINTS ÁGUA ===
@app.post("/consumo_agua")
def cria_consumo_agua(consumo: models.ConsumoAgua):
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
def cria_consumo_energia(consumo: models.ConsumoEnergia):
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


# === ENDPOINTS HIGIENE ===
@app.post("/produto")
def cria_consumo_higiene(consumo: models.Produto):
    ins = produto_tbl.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}

@app.post("/compra")
def cria_compra(consumo: models.Compra):
    ins = compra_tbl.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}

@app.post("/consumo_higiene")
def cria_atividade(consumo: models.Atividade_gasto):
    ins = atividade_tbl.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}