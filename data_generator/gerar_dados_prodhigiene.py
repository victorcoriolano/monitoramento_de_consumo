import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, MetaData, Table

# === Perfis de consumo por produto ===
PERFIS = {
    "rolo_papel_higienico": {
        "unidade": "unidade",
        "consumo_mensal": 3.9,
        "variacao_diaria": 0.05,
        "freq_compra": 1/2,
        "quantidade_compra": 4,
        "window_compra": [(9, 18)]
    },
    "pasta_de_dente": {
        "unidade": "gramas",
        "consumo_mensal": 45,
        "variacao_diaria": 0.3,
        "freq_compra": 1/4,
        "quantidade_compra": 90,
        "window_compra": [(9, 18)]
    },
    "sabonete": {
        "unidade": "unidade",
        "consumo_mensal": 2.1,
        "variacao_diaria": 0.03,
        "freq_compra": 1/4,
        "quantidade_compra": 4,
        "window_compra": [(9, 18)]
    },
    "creme_antitranspirante": {
        "unidade": "ml",
        "consumo_mensal": 50,
        "variacao_diaria": 0.1,  # Estimativa de variação diária
        "freq_compra": 1/4,
        "quantidade_compra": 50,
        "window_compra": [(9, 18)]
    },
    "condicionador": {
        "unidade": "ml",
        "consumo_mensal": 300,
        "variacao_diaria": 10,   # Estimativa de variação diária
        "freq_compra": 1/2,
        "quantidade_compra": 300,
        "window_compra": [(9, 18)]
    },
    "shampoo": {
        "unidade": "ml",
        "consumo_mensal": 300,
        "variacao_diaria": 10,   # Estimativa de variação diária
        "freq_compra": 1/2,
        "quantidade_compra": 300,
        "window_compra": [(9, 18)]
    },
    "sabao_para_lavar_louca": {
        "unidade": "ml",
        "consumo_mensal": 1000,
        "variacao_diaria": 30,   # Estimativa de variação diária
        "freq_compra": 1/4,
        "quantidade_compra": 500,
        "window_compra": [(9, 18)]
    },
    "detergente": {
        "unidade": "ml",
        "consumo_mensal": 1500,
        "variacao_diaria": 50,   # Estimativa de variação diária
        "freq_compra": 1/3,
        "quantidade_compra": 500,
        "window_compra": [(9, 18)]
    },
    "veja": {
        "unidade": "ml",
        "consumo_mensal": 1500,
        "variacao_diaria": 50,   # Estimativa de variação diária
        "freq_compra": 1/4,
        "quantidade_compra": 500,
        "window_compra": [(9, 18)]
    },
    "desinfetante_veja_2l": {
        "unidade": "ml",
        "consumo_mensal": 4000,
        "variacao_diaria": 100,  # Estimativa de variação diária
        "freq_compra": 1/4,
        "quantidade_compra": 2000,
        "window_compra": [(9, 18)]
    },
    "cloro_5l": {
        "unidade": "ml",
        "consumo_mensal": 5000,
        "variacao_diaria": 150,  # Estimativa de variação diária
        "freq_compra": 1/2,
        "quantidade_compra": 5000,
        "window_compra": [(9, 18)]
    },
    "desinfetante_cheirinho_pinho": {
        "unidade": "ml",
        "consumo_mensal": 500,
        "variacao_diaria": 20,   # Estimativa de variação diária
        "freq_compra": 1/2,
        "quantidade_compra": 500,
        "window_compra": [(9, 18)]
    },
    "sabao_em_po_5k": {
        "unidade": "kg",
        "consumo_mensal": 5,
        "variacao_diaria": 0.2,  # Estimativa de variação diária
        "freq_compra": 1/4,
        "quantidade_compra": 5,
        "window_compra": [(9, 18)]
    },
    "amaciante_2l": {
        "unidade": "ml",
        "consumo_mensal": 2000,
        "variacao_diaria": 80,   # Estimativa de variação diária
        "freq_compra": 1/5,
        "quantidade_compra": 2000,
        "window_compra": [(9, 18)]
    }
}

faker = Faker()
metadata = MetaData()

consumo_tbl = Table(
    "consumo_higiene", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("produto", String, nullable=False),
    Column("quantidade", Float, nullable=False),
    Column("unidade", String, nullable=False),
    Column("tipo", String, nullable=False),  # 'uso' ou 'compra'
    Column("timestamp", Date, nullable=False),
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