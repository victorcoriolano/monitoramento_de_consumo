import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, MetaData, Table

# === Perfis de consumo por produto ===


faker = Faker()
metadata = MetaData()


compra_tbl = Table(
    "compra_higiene", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("produto", String, nullable=False),
    Column("quantidade", Float, nullable=False),
    Column("unidade", String, nullable=False),
    Column("gasto_total", Float, nullable=False),
    Column("timestamp", Date, nullable=False),
)

atividade_gasto_tbl = Table(
    "atividade_gasto", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("atividade", String, nullable=False),
    Column("quantidade", Float, nullable=False),
    Column("timestamp", Date, nullable=False),
)

produto_tbl = Table(
    "produto", metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String, nullable=False),
    Column("unidade", String, nullable=False),
    Column("quantidade_restante", Float, nullable=False),
    Column("preco_unitario", Float, nullable=False),
)




def main(db_url: str, dias: int, usuario_id: int):
    engine = create_engine(db_url)
    metadata.create_all(engine)
    
    registros = []
    hoje = datetime.now().date()
    
    # Simular 10% de dias fora de casa
    dias_totais = list(range(dias))
    dias_fora_casa = set(np.random.choice(dias_totais, size=int(dias * 0.1), replace=False))

    for day in dias_totais:
        data = hoje - timedelta(days=day)
        
        if day in dias_fora_casa:
            continue  # pular dia fora de casa
        
        for produto, perfil in PERFIS.items():
            # Simular uso diário
            consumo_dia = max(0, np.random.normal(
                perfil["consumo_mensal"], 
                perfil["variacao_diaria"]
            ))
            
            registros.append({
                "usuario_id": usuario_id,
                "produto": produto,
                "quantidade": round(consumo_dia, 2),
                "unidade": perfil["unidade"],
                "tipo": "uso",
                "timestamp": data
            })
            
            # Simular compras
            if day % perfil["freq_compra"] == 0:
                hora_compra = np.random.randint(
                    perfil["window_compra"][0][0],
                    perfil["window_compra"][0][1] + 1
                )
                
                registros.append({
                    "usuario_id": usuario_id,
                    "produto": produto,
                    "quantidade": perfil["quantidade_compra"],
                    "unidade": perfil["unidade"],
                    "tipo": "compra",
                    "timestamp": data
                })

    df = pd.DataFrame(registros)
    df.to_sql("consumo_higiene", engine, if_exists="append", index=False)
    print(f">> Inseridos {len(df)} registros para {dias} dias. Dias fora de casa: {len(dias_fora_casa)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sqlite:///consumo.db",
                        help="URL do banco (ex: sqlite:///consumo.db)")
    parser.add_argument("--dias", type=int, default=30,
                        help="Quantos dias para gerar retroativamente")
    parser.add_argument("--usuario", type=int, default=1,
                        help="ID do usuário")
    args = parser.parse_args()
    
    main(args.db, args.dias, args.usuario)