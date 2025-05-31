from pydantic import BaseModel
from datetime import datetime

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


class Produto(BaseModel):
    usuario_id: int
    prod_nome: str
    unidade: str
    preco_unitario: float
    quantidade_restante: float
    quantidade_total: float
    quantidade_estoque: int
    timestamp: datetime

class Compra(BaseModel):
    usuario_id: int
    produto_id: int
    quantidade: float
    gasto_total: float
    timestamp: datetime

class Atividade_gasto(BaseModel):
    usuario_id: int
    produto_id: int
    produto_nome: str
    atividade: str
    porcentagem_gasto: float
    consumo: float
    timestamp: datetime

 