import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData, Table

# === Perfis de consumo por equipamento ===
PERFIS = {
    "geladeira": {
        "potencia_w": 90.8,
        "mean_h_dia": 24,
        "std_h_dia": 1,
        "freq_dia": 1,
        "window": [(0, 23)]
    },
    "microondas": {
        "potencia_w": 1150,
        "mean_h_dia": 0.1,
        "std_h_dia": 0.05,
        "freq_dia": 3,
        "window": [(18, 23), (9, 12)]
    },
    "televisao_30_polegadas": {
        "potencia_w": 119,
        "mean_h_dia": 3,
        "std_h_dia": 1.5,
        "freq_dia": 1,
        "window": [(18, 23)]
    },
    "televisao_42_polegadas": {
        "potencia_w": 200,
        "mean_h_dia": 6,
        "std_h_dia": 1.5,
        "freq_dia": 1,
        "window": [(18, 23)]
    },
    "iluminacao_casa": {
        "potencia_w": 180,
        "mean_h_dia": 6,
        "std_h_dia": 2,
        "freq_dia": 1,
        "window": [(19, 23)]
    },
    "chuveiro_eletrico": {
        "potencia_w": 5500,
        "mean_h_dia": 0.083,  # 5 minutos
        "std_h_dia": 0.02,
        "freq_dia": 2,
        "window": [(10, 12), (22, 23)]
    },
    "carregador_smartphone": {
        "potencia_w": 10,
        "mean_h_dia": 3,
        "std_h_dia": 2,
        "freq_dia": 1,
        "window": [(22, 24), (7, 8)]
    },
    "maquina_lavar_roupa": {
        "potencia_w": 1500,
        "mean_h_dia": 1.2,
        "std_h_dia": 0.4,
        "freq_dia_semana": 2,
        "window": [(9, 12)]
    },
}

faker = Faker()
metadata = MetaData()



def main(db_url: str, dias: int, usuario_id: int):
    engine = create_engine(db_url)
    metadata.create_all(engine)

    registros = []
    hoje = datetime.now().date()

    # Simular 5% dos dias com queda de energia
    dias_totais = list(range(dias))
    dias_sem_energia = set(np.random.choice(dias_totais, size=int(dias * 0.05), replace=False))

    for day in dias_totais:
        if day in dias_sem_energia:
            continue  # pular geração neste dia (sem energia)

        data = hoje - timedelta(days=day)

        for equipamento, perfil in PERFIS.items():
            # Determinar frequência
            if "freq_dia" in perfil:
                iam = perfil["freq_dia"]
                n = np.random.poisson(lam=iam) if iam >= 1 else (1 if np.random.rand() < iam else 0)
            elif "freq_dia_semana" in perfil:
                # Ativa só em dias aleatórios da semana
                if faker.random_int(1, 7) > perfil["freq_dia_semana"]:
                    continue
                n = 1
            else:
                n = 1

            for _ in range(n):
                duracao = max(0.01, np.random.normal(perfil["mean_h_dia"], perfil.get("std_h_dia", 0.1)))
                potencia = perfil.get("potencia_w", perfil.get("potencia_w_total", 0))
                gasto_h = potencia * duracao / 1000  # kWh

                janela = faker.random_element(perfil["window"])
                hora = np.random.randint(janela[0], min(janela[1] + 1, 23))
                minuto = np.random.randint(0, 60)
                ts = datetime.combine(data, time(hora, minuto))

                registros.append({
                    "usuario_id": usuario_id,
                    "equipamento": equipamento,
                    "potencia_w": potencia,
                    "gasto_h": round(gasto_h, 3),
                    "timestamp": ts
                })

    df = pd.DataFrame(registros)
    df.to_sql("consumo_energia", engine, if_exists="append", index=False)
    print(f">> Inseridos {len(df)} registros para {dias} dias (com {len(dias_sem_energia)} dias sem energia).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sqlite:///./consumo.db",
                        help="URL do banco (ex: sqlite:///./consumo.db ou postgresql://user:pass@host/db)")
    parser.add_argument("--dias", type=int, default=30,
                        help="Quantos dias para gerar retroativamente")
    parser.add_argument("--usuario", type=int, default=1,
                        help="ID do usuário dono dos dados")
    args = parser.parse_args()
    main(args.db, args.dias, args.usuario)
