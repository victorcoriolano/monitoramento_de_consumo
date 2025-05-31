from sqlalchemy import Column, Integer, Float, String, Date, MetaData, Table, DateTime


metadata = MetaData()


# produtos higiene limpeza
produto_tbl = Table(
    "produto", metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String, nullable=False),
    Column("unidade", String, nullable=False),
    Column("quantidade_restante", Float, nullable=False),
    Column("preco_unitario", Float, nullable=False),
    Column("data_compra", Date, nullable=False),
)

compra_tbl = Table(
    "compra", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("produto_id", Integer, nullable=False),
    Column("quantidade", Float, nullable=False),
    Column("gasto_total", Float, nullable=False),
    Column("data", Date, nullable=False),
)

atividade_tbl = Table(
    "atividade", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("produto_id", Integer, nullable=False),
    Column("produto_nome", Integer, nullable=False),
    Column("atividade", String, nullable=False),
    Column("porcentagem_gasto", Float, nullable=False),
    Column("consumo", Float, nullable=False),
    Column("data", Date, nullable=False),
)

# agua
consumo_agua = Table(
    "consumo_agua", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("atividade", String, nullable=False),
    Column("volume_litros", Float, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)

#energia 
consumo_energia = Table(
    "consumo_energia", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("equipamento", String, nullable=False),
    Column("potencia_w", Float, nullable=False),
    Column("gasto_h", Float, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)