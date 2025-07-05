from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import pandas as pd
import streamlit as st

def analisar_apriori(df_trends, df_x):
    # Combinar termos e assuntos em uma matriz binária
    combined = pd.concat([df_trends['termo'], df_x['assunto']]).value_counts().head(10).index
    data = pd.DataFrame(index=range(len(combined)), columns=combined).fillna(0)
    st.write("Regras de Associação (Apriori):", association_rules(apriori(data, min_support=0.1), metric="confidence"))

def analisar_clusters(df_spotify, df_youtube):
    # Exemplo básico de clustering (substitua por KMeans real)
    combined = pd.concat([df_spotify[['popularidade']], df_youtube[['visualizacoes']]]).dropna()
    st.write("Clusters (exemplo):", combined.describe())
