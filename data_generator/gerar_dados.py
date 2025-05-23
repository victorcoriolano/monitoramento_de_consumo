import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData, Table

# === 1) Definição dos perfis de consumo por atividade ===
# média diária total / frequência média → média por vez
PERFIS = {
    "escovar_dentes": {
        "mean_l": 2.0,   # litros por evento
        "std_l": 0.5,
        "freq_dia": 2,
        "window": [(7, 9), (20, 22)]
    },
    "lavar_maos": {
        "mean_l": 2.0,
        "std_l": 0.5,
        "freq_dia": 4,
        "window": [(6, 22)]
    },
    "lavar_rosto": {
        "mean_l": 2.0,
        "std_l": 0.5,
        "freq_dia": 1,
        "window": [(6, 22)]
    },
    "lavar_louca": {
        "mean_l": 15.0,
        "std_l": 3.0,
        "freq_dia": 2.5,
        "window": [(11, 14), (19, 21)]
    },
    "lavar_alimentos": {
        "mean_l": 5.0,
        "std_l": 1.0,
        "freq_dia": 2.5,
        "window": [(11, 14), (19, 21)]
    },
    "agua_cozinhar": {
        "mean_l": 3.0,
        "std_l": 0.5,
        "freq_dia": 2.5,
        "window": [(11, 14), (19, 21)]
    },
    "tanque": {
        "mean_l": 10.0,
        "std_l": 2.0,
        "freq_dia": 1.5,
        "window": [(8, 18)]
    },
    "banho": {
        "mean_l": 45.0,
        "std_l": 10.0,
        "freq_dia": 1.5,
        "window": [(6, 10), (18, 22)]
    },
    "descarga": {
        "mean_l": 6.0,
        "std_l": 1.0,
        "freq_dia": 2,
        "window": [(0, 23)]
    },
    "garrafa_agua": {
        "mean_l": 2.0,
        "std_l": 0.2,
        "freq_dia": 1,
        "window": [(8, 22)]
    },
    "maquina_lavar": {
        "mean_l": 82.0,
        "std_l": 5.0,
        "freq_dia": 2/30,  # 2 vezes ao mês → ~0.066 por dia
        "window": [(7, 20)]
    }
}

# === 2) Setup Faker + Banco via SQLAlchemy ===
fake = Faker()
metadata = MetaData()

consumo_tbl = Table(
    "consumo_agua", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("atividade", String, nullable=False),
    Column("volume_litros", Float, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)

def main(db_url: str, dias: int, usuario_id: int):
    engine = create_engine(db_url)
    metadata.create_all(engine)

    registros = []
    hoje = datetime.now().date()

    for day_offset in range(dias):
        data = hoje - timedelta(days=day_offset)
        for atividade, perfil in PERFIS.items():
            # quantos eventos naquele dia (pode flutuar p/ Poisson)
            lam = perfil["freq_dia"]
            n = np.random.poisson(lam=lam) if lam >= 1 else (1 if np.random.rand() < lam else 0)
            for _ in range(n):
                # volume e horário
                vol = max(0.01, np.random.normal(perfil["mean_l"], perfil["std_l"]))
                janela = fake.random_element(perfil["window"])
                hora = np.random.randint(janela[0], janela[1] + 1)
                minuto = np.random.randint(0, 60)
                ts = datetime.combine(data, time(hora, minuto))
                registros.append({
                    "usuario_id": usuario_id,
                    "atividade": atividade,
                    "volume_litros": float(vol),
                    "timestamp": ts
                })

    # inserir tudo de uma vez
    df = pd.DataFrame(registros)
    df.to_sql("consumo_agua", engine, if_exists="append", index=False)
    print(f">> Inseridos {len(df)} registros para {dias} dias.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sqlite:///./consumo.db",
                        help="URL do banco (ex: sqlite:///./consumo.db ou postgresql://user:pass@host/db)")
    parser.add_argument("--dias", type=int, default=7,
                        help="Quantos dias para gerar retroativamente")
    parser.add_argument("--usuario", type=int, default=1,
                        help="ID do usuário dono dos dados")
    args = parser.parse_args()
    main(args.db, args.dias, args.usuario)
