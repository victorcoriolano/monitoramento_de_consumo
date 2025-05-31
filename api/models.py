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
    nome: str
    unidade: str
    quantidade_restante: float
    quantidade_total: float
    quantidade_estoque: int
    preco_unitario: float
    data_compra: datetime

class Compra(BaseModel):
    usuario_id: int
    produto_id: int
    produto_nome: str
    quantidade: float
    gasto_total: float
    data: datetime

class Atividade_gasto(BaseModel):
    usuario_id: int
    produto_id: int
    produto_nome: str
    atividade: str
    porcentagem_gasto: float
    consumo: float
    data: datetime

 