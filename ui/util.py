import pandas as pd

def carregar_dados(tabela, dias, engine, filtro_col=None, filtro_valor=None):
    query = f"SELECT * FROM {tabela} WHERE timestamp >= date('now','-{dias} day')"
    if filtro_col and filtro_valor and filtro_valor != "Todas":
        query += f" AND {filtro_col} = '{filtro_valor}'"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    return df.set_index("timestamp").sort_index()

def dias_monitorados(tabela, engine):
    df = pd.read_sql(f"SELECT timestamp FROM {tabela}", engine)
    df['data'] = pd.to_datetime(df['timestamp']).dt.date
    return df['data'].nunique()
