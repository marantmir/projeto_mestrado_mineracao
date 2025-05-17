import pandas as pd

def aplicar_filtros(df, pais, regiao, faixa_etaria, genero):
    if pais != "Todos" and 'pais' in df.columns:
        df = df[df['pais'] == pais]
    if regiao != "Todas" and 'regiao' in df.columns:
        df = df[df['regiao'] == regiao]
    if faixa_etaria != "Todas" and 'faixa_etaria' in df.columns:
        df = df[df['faixa_etaria'] == faixa_etaria]
    if genero != "Todos" and 'genero' in df.columns:
        df = df[df['genero'] == genero]
    return df
