from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData

DATABASE_URL = "sqlite:///../consumo.db"

app = FastAPI()
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Tabelas
consumo_agua_tbl = Table("consumo_agua", metadata, autoload_with=engine)
consumo_energia_tbl = Table("consumo_energia", metadata, autoload_with=engine)

# === MODELOS Pydantic ===
class ConsumoAgua(BaseModel):
    usuario_id: int
    atividade: str
    volume_litros: float
    timestamp: datetime

class ConsumoEnergia(BaseModel):
    usuario_id: int
    equipamento: str
    potencia_w: float
    gasto_h: float
    timestamp: datetime

# === ENDPOINTS ÁGUA ===
@app.post("/consumo")
def cria_consumo_agua(consumo: ConsumoAgua):
    ins = consumo_agua_tbl.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}

@app.get("/consumo")
def lista_consumo_agua(atividade: str):
    sel = consumo_agua_tbl.select()
    if atividade:
        sel = sel.where(consumo_agua_tbl.c.atividade == atividade)
    with engine.connect() as conn:
        rows = conn.execute(sel).fetchall()
    return [dict(row) for row in rows]

# === ENDPOINTS ENERGIA ===
@app.post("/consumo_energia")
def cria_consumo_energia(consumo: ConsumoEnergia):
    ins = consumo_energia_tbl.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status": "ok"}

@app.get("/consumo_energia")
def lista_consumo_energia(equipamento: str):
    sel = consumo_energia_tbl.select()
    if equipamento:
        sel = sel.where(consumo_energia_tbl.c.equipamento == equipamento)
    with engine.connect() as conn:
        rows = conn.execute(sel).fetchall()
    return [dict(row) for row in rows]
