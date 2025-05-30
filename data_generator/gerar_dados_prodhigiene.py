import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, MetaData, Table
from sqlalchemy.orm import Session
import time

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
        "gasto_total": [0.017],
        "produtos": ["cotonete"],
        "freq_dia": 0.5,
        "window": [(7, 8), (22, 23)]
    },
    "escovar_dentes": {
        "gasto_total": [0.0167],
        "produtos": ["pasta_dente"],
        "freq_dia": 2,
        "window": [(7, 8), (22, 23)]
    },
    "lavar_roupa": {
        "gasto_total": [0.0333, 0.0167],
        "produtos": ["sabao_em_po", "amaciante"],
        "freq_dia": 0.5,
        "window": [(9, 12), (18, 21)]
    },
    "lavar_louca": {
        "gasto_total": [0.04, 0.05],
        "produtos": ["detergente", "sabao_pedra"],
        "freq_dia": 2,
        "window": [(7, 9), (19, 21)]
    },
    "lavar_maos": {
        "gasto_total": [0.002],
        "produtos": ["sabonete"],
        "freq_dia": 5,
        "window": [(6, 23)]
    },
    "banho": {
        "gasto_total": [0.04, 0.0667, 0.0667],
        "produtos": ["sabonete", "shampoo", "condicionador"],
        "freq_dia": 1,
        "window": [(7, 9), (21, 23)]
    },
    "cagar": {
        "gasto_total": [0.0333],
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
        "gasto_total": [0.025],
        "produtos": ["desodorante"],
        "freq_dia": 1,
        "window": [(7, 9)]
    },
    "assoar_nariz": {
        "gasto_total": [0.0067],
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
    Column("quantidade", Float, nullable=False),
    Column("data", Date, nullable=False),
)


def inserir_produtos(engine):
    produtos = [
        ("rolo_papel", "m", 30, 5.0),
        ("pasta_dente", "g", 70, 7.0),
        ("sabonete", "g", 70, 3.0),
        ("desodorante", "g", 55, 9.0),
        ("condicionador", "ml", 200, 12.0),
        ("shampoo", "ml", 200, 10.0),
        ("sabao_pedra", "g", 200, 2.5),
        ("detergente", "ml", 500, 3.0),
        ("veja", "ml", 500, 6.0),
        ("desinfetante", "ml", 2000, 8.0),
        ("cloro", "ml", 5000, 7.5),
        ("pinho", "ml", 1000, 6.5),
        ("sabao_em_po", "g", 5000, 20.0),
        ("amaciante", "ml", 2000, 11.0),
        ("cotonete", "un", 75, 5.0)
    ]

    with engine.begin() as conn: 
        for nome, unidade, qtd, preco in produtos:
            print(f">> Inserindo produto {nome}...")
            conn.execute(produto_tbl.insert().values(
                nome=nome,
                unidade=unidade,
                quantidade_restante=qtd,
                preco_unitario=preco
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

                for nome_prod, qtd in zip(perfil["produtos"], perfil["gasto_total"]):
                    print(f">> {atividade_nome} em {data} gastando {qtd} de {nome_prod}")
                    result = conn.execute(produto_tbl.select().where(produto_tbl.c.nome == nome_prod)).first()

                    if not result:
                        print(f">> Produto {nome_prod} não encontrado.")
                        continue
                    if result:
                        if result.quantidade_restante < qtd:
                            print(f">> Produto {nome_prod} não tem quantidade suficiente.")
                            continue
                        registros.append({
                            "usuario_id": usuario_id,
                            "produto_id": result.id,
                            "atividade": atividade_nome,
                            "quantidade": qtd,
                            "data": data
                        })
                        nova_qtd = max(result.quantidade_restante - qtd, 0)
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

    
    registros = gerar_gastos(engine, args.dias, args.usuario)

    for registro in registros:
        salvar_consumo(engine, registro)
