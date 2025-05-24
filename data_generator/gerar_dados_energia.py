import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData, Table

# === 1 Definição dos perfis de consumo por atividade ===


PERFIS = {
    
    "geladeira": {
        "potencia_w": 150,  # Potência média em Watts
        "mean_h_dia": 24,
        "freq_dia": 1,      # Consideramos como um evento contínuo por dia
        "duracao_dia_h": 24, # Horas de funcionamento por dia
        "std_duracao_h": 1   # Desvio padrão na duração (pode variar um pouco dependendo de aberturas, etc.)
    },
    "microondas": {
        "potencia_w": 50,  # Potência média em Watts
        "mean_h_dia": 24,
        "freq_dia": 1,      # Consideramos como um evento contínuo por dia
        "duracao_dia_h": 24, # Horas de funcionamento por dia
        "std_duracao_h": 1   # Desvio padrão na duração (pode variar um pouco dependendo de aberturas, etc.)
    },
    "televisao": {
        "potencia_w": 100,  # Potência média em Watts
        "mean_h_dia": 4,    # Média de horas de uso por dia
        "std_h_dia": 1.5,   # Desvio padrão nas horas de uso
        "freq_dia": 1,      # Número de vezes que é ligada (agrupando sessões)
        "window": [(18, 23)] # Janela de tempo mais provável de uso (18h às 23h)
    },
    "iluminacao_sala": {
        "potencia_w_total": 60, # Potência total das lâmpadas da sala
        "mean_h_dia": 5,    # Média de horas de uso por dia
        "std_h_dia": 2,     # Desvio padrão nas horas de uso
        "freq_dia": 1,      # Assumindo um período principal de uso
        "window": [(19, 23)] # Janela de tempo mais provável de uso noturno
    },
    "chuveiro_eletrico": {
        "potencia_w": 5500, # Potência em Watts
        "mean_min_uso": 7,  # Média de minutos por banho
        "std_min_uso": 3,   # Desvio padrão nos minutos por banho
        "freq_dia": 2,      # Frequência de banhos por dia
        "window": [(7, 9), (18, 21)] # Janelas de tempo mais prováveis para banhos
    },
    "carregador_smartphone": {
        "potencia_w": 10,   # Potência média em Watts
        "mean_h_dia": 3,    # Média de horas conectado por dia (nem sempre carregando)
        "std_h_dia": 2,     # Desvio padrão nas horas conectado
        "freq_dia": 1,      # Geralmente conectado uma vez ao dia
        "window": [(22, 24), (7, 8)] # Janelas de tempo prováveis (noite e manhã)
    }

}

faker = Faker()
metadata = MetaData()

consumo_tbl = Table(
    "consumo_energia", metadata,
    Column("id", Integer, primary_key=True),
    Column("usuario_id", Integer, nullable=False),
    Column("equipamento", String, nullable=False),
    Column("potencia_w", Float, nullable=False),
    Column("gasto_h", Float, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)

def main (db_url: str, dias: int, usuario_id: int):
    engine = create_engine(db_url)
    metadata.create_all(engine)

    registros = []
    hoje = datetime.now().date()

    # Geração de dados
    for day in range(dias):
        data = hoje - timedelta(days=day)

        for equipamento, perfil in PERFIS.items():
            iam = perfil["freq_dia"]
            n = np.random.poisson(lam=iam) if iam >= 1 else (1 if np.random.rand() < iam else 0)

            for _ in range(n):
                # pegando a duração do uso do equipamento
                duracao = max(0.01, np.random.normal(perfil["mean_h_dia"], perfil["std_h_dia"]))
                # calculando o gasto de energia 
                gasto_h = perfil["potencia_w"] * duracao / 1000
                
                janela = faker.random_element(perfil["window"])
                hora = np.random.randint(janela[0], janela[1] + 1)
                minuto = np.random.randint(0, 60)
                ts = datetime.combine(data, time(hora, minuto))
                registros.append({
                    "usuario_id": usuario_id,
                    "equipamento": equipamento,
                    "potencia_w": perfil["potencia_w"],
                    "gasto_h": round(gasto_h, 3),
                    "timestamp": ts
                })

    # inserir dados 
    df = pd.DataFrame(registros)
    df.to_sql("consumo_energia", engine, if_exists="append", index=False)
    print(f">> Inseridos {len(df)} registros para {dias} dias.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sqlite:///./consumo.db",
                        help="URL do banco (ex: sqlite:///./consumo.db ou postgresql://user:pass@host/db)")
    parser.add_argument("--dias", type=int, default=90,
                        help="Quantos dias para gerar retroativamente")
    parser.add_argument("--usuario", type=int, default=1,
                        help="ID do usuário dono dos dados")
    args = parser.parse_args()
    main(args.db, args.dias, args.usuario)
