from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData

DATABASE_URL = "sqlite:///../consumo.db"  

app = FastAPI()
engine = create_engine(DATABASE_URL)
metadata = MetaData()
consumo_tbl = Table("consumo_agua", metadata, autoload_with=engine)

class Consumo(BaseModel):
    usuario_id: int
    atividade: str
    volume_litros: float
    timestamp: datetime

@app.post("/consumo")
def cria(consumo: Consumo):
    ins = consumo_tbl.insert().values(**consumo.model_dump())
    with engine.begin() as conn:
        conn.execute(ins)
    return {"status":"ok"}

@app.get("/consumo")
def lista(atividade: str):
    sel = consumo_tbl.select()
    if atividade:
        sel = sel.where(consumo_tbl.c.atividade == atividade)
    with engine.connect() as conn:
        rows = conn.execute(sel).fetchall()
    return [dict(row) for row in rows]
