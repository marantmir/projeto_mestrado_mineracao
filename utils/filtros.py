import pandas as pd

def aplicar_filtros(df, pais, regiao, faixa_etaria, genero):
    df_filtrado = df.copy()

    if pais != "Todos":
        df_filtrado = df_filtrado[df_filtrado["pais"] == pais]

    if regiao != "Todas":
        df_filtrado = df_filtrado[df_filtrado["regiao"] == regiao]

    if faixa_etaria != "Todas":
        df_filtrado = df_filtrado[df_filtrado["faixa_etaria"] == faixa_etaria]

    if genero != "Todos":
        df_filtrado = df_filtrado[df_filtrado["genero"] == genero]

    return df_filtrado
