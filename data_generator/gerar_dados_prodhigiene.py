import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, MetaData, Table


# === Produtos e perfis de consumo ===
PRODUTOS = [
    "pasta_dente",
    "sabao_em_po",
    "sabao_pedra",
    "detergente",
    "amaciante",
    "sabonete",
    "desinfetante",
    "desodorante",
    "shampoo",
    "condicionador",
    "rolo_papel",
    "veja",
    "pinho",
    "cloro",
    "cotonete"
]

PERFIL_GASTOS = {
    "limpar_ouvidos": {
        "gasto_total": [0.016],
        "produtos": ["cotonete"],
        "freq_dia": 1,
        "window": [(7, 8), (22, 23)]
    },
    "escovar_dentes": {
        "gasto_total": [0.03],
        "produtos": ["pasta_dente"],
        "freq_dia": 2,
        "window": [(7, 8), (22, 23)]
    },
    "lavar_roupa": {
        "gasto_total": [0.03, 0.05],
        "produtos": ["sabao_em_po", "amaciante"],
        "freq_dia": 0.25,
        "window": [(9, 12), (18, 21)]
    },
    "lavar_louca": {
        "gasto_total": [0.08, 0.08],
        "produtos": ["detergente", "sabao_pedra"],
        "freq_dia": 2,
        "window": [(7, 9), (19, 21)]
    },
    "lavar_maos": {
        "gasto_total": [0.03],
        "produtos": ["sabonete"],
        "freq_dia": 5,
        "window": [(6, 23)]
    },
    "banho": {
        "gasto_total": [0.1, 0.08, 0.08],
        "produtos": ["sabonete", "shampoo", "condicionador"],
        "freq_dia": 1,
        "window": [(7, 9), (21, 23)]
    },
    "cagar": {
        "gasto_total": [0.02],
        "produtos": ["rolo_papel"],
        "freq_dia": 1,
        "window": [(7, 9), (12, 13), (18, 20)]
    },
    "limpar_casa": {
        "gasto_total": [0.05, 0.05, 0.06, 0.05],
        "produtos": ["veja", "pinho", "desinfetante", "cloro"],
        "freq_dia": 0.2,
        "window": [(9, 12)]
    },
    "passar_desodorante": {
        "gasto_total": [0.03],
        "produtos": ["desodorante"],
        "freq_dia": 1,
        "window": [(7, 9)]
    },
    "assoar_nariz": {
        "gasto_total": [0.01],
        "produtos": ["rolo_papel"],
        "freq_dia": 5,
        "window": [(6, 23)]
    }
}

faker = Faker()
metadata = MetaData()

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
    Column("atividade", String, nullable=False),
    Column("porcentagem_gasto", Float, nullable=False),
    Column("consumo", Float, nullable=False),
    Column("data", Date, nullable=False),
)


def inserir_produtos(engine):
    hoje = datetime.now().date()
    d = hoje - timedelta(days=100)
    produtos = [
        ("rolo_papel", "m", 30, 5.0, d),
        ("pasta_dente", "g", 70, 7.0, d),
        ("sabonete", "g", 70, 3.0, d),
        ("desodorante", "g", 55, 9.0 , d),
        ("condicionador", "ml", 200, 12.0 , d),
        ("shampoo", "ml", 200, 10.0     , d),
        ("sabao_pedra", "g", 200, 2.5   , d),
        ("detergente", "ml", 500, 3.0 , d),
        ("veja", "ml", 500, 6.0 , d),
        ("desinfetante", "ml", 2000, 8.0 , d),
        ("cloro", "ml", 5000, 7.5   , d),
        ("pinho", "ml", 1000, 6.5   , d),
        ("sabao_em_po", "g", 1000, 20.0 , d),
        ("amaciante", "ml", 2000, 11.0  , d),
        ("cotonete", "un", 75, 5.0      , d),
    ]

    with engine.begin() as conn: 
        for nome, unidade, qtd, preco, data in produtos:
            print(f">> Inserindo produto {nome}...")
            conn.execute(produto_tbl.insert().values(
                nome=nome,
                unidade=unidade,
                quantidade_restante=qtd,
                preco_unitario=preco,
                data_compra=data
            ))
            print(f">> Produto {nome} inserido.")
        print(">> Produtos inseridos com nomes padronizados.")


def gerar_gastos(engine, dias: int, usuario_id: int):
    
    hoje = datetime.now().date()
    registros = []

    with engine.begin() as conn: 
        for day in range(dias):
            data = hoje - timedelta(days=day)

            for atividade_nome, perfil in PERFIL_GASTOS.items():
                if np.random.rand() >= min(perfil["freq_dia"], 1.0):
                    print(f">> {atividade_nome} não realizada em {data}")
                    continue

                for nome_prod, porcent in zip(perfil["produtos"], perfil["gasto_total"]):
                    
                    print(f">> {atividade_nome} em {data} gastando {porcent} porcento de {nome_prod}")
                    result = conn.execute(produto_tbl.select().where(produto_tbl.c.nome == nome_prod)).first()

                    if not result:
                        print(f">> Produto {nome_prod} não encontrado.")
                        continue
                    if result:
                        qtd = round(porcent * result.quantidade_restante, 2) # calculando quantidade de produto gasto
                        if result.quantidade_restante < qtd:
                            print(f">> Produto {nome_prod} não tem quantidade suficiente.")
                            continue
                        registros.append({
                            "usuario_id": usuario_id,
                            "produto_id": result.id,
                            "atividade": atividade_nome,
                            "porcentagem_gasto": porcent,
                            "consumo": qtd,
                            "data": data
                        })
                        nova_qtd = max(result.quantidade_restante - qtd, 0)
                        print (f">> Produto {nome_prod} atualizado para {nova_qtd}")
                        conn.execute(produto_tbl.update().where(produto_tbl.c.id == result.id).values(
                            quantidade_restante=nova_qtd
                        ))
    conn.close()
    return registros




def inserir_compra(engine, usuario_id: int, produto_id: int, quantidade: float, preco_unitario: float, data: datetime.date):
    with engine.begin() as conn: 
        total = round(quantidade * preco_unitario, 2)

        conn.execute(compra_tbl.insert().values(
            usuario_id=usuario_id,
            produto_id=produto_id,
            quantidade=quantidade,
            gasto_total=total,
            data=data
        ))

        produto = conn.execute(produto_tbl.select().where(produto_tbl.c.id == produto_id)).first()
        nova_qtd = produto.quantidade_restante + quantidade
        conn.execute(produto_tbl.update().where(produto_tbl.c.id == produto_id).values(
            quantidade_restante=nova_qtd
        ))
        print(f">> Compra registrada para produto {produto_id}")

def salvar_consumo(engine, registro: dict):
    
    with engine.begin() as conn:
        conn.execute(atividade_tbl.insert().values(**registro))

    conn.close()

if __name__ == "__main__":
    engine = create_engine("sqlite:///consumo.db", connect_args={
        "timeout": 30,
        "check_same_thread": False
    })
    metadata.create_all(engine)

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sqlite:///consumo.db")
    parser.add_argument("--dias", type=int, default=30)
    parser.add_argument("--usuario", type=int, default=1)
    args = parser.parse_args()

    inserir_produtos(engine)
    registros = gerar_gastos(engine, args.dias, args.usuario)

    for registro in registros:
        salvar_consumo(engine, registro)
