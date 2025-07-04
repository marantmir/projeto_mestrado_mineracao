import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def analisar_apriori(df_trends, df_x):
    st.subheader("📌 Associações com Apriori (Google Trends + Twitter)")
    termos = list(df_trends["termo"].str.lower()) + list(df_x["assunto"].str.lower())
    baskets = []
    for i in range(0, len(termos)-1, 2):
        baskets.append([termos[i], termos[i+1]])

    all_items = sorted(set([item for sublist in baskets for item in sublist]))
    df_apriori = pd.DataFrame([[item in basket for item in all_items] for basket in baskets], columns=all_items)
    frequentes = apriori(df_apriori, min_support=0.2, use_colnames=True)
    regras = association_rules(frequentes, metric="lift", min_threshold=1.0)

    if regras.empty:
        st.warning("Nenhuma associação forte foi encontrada.")
    else:
        st.dataframe(regras[["antecedents", "consequents", "support", "confidence", "lift"]])

def analisar_clusters(df_spotify, df_youtube):
    st.subheader("📊 Clusterização de Conteúdos Populares (Spotify + YouTube)")
    df_spotify["streams"] = pd.to_numeric(df_spotify["streams"], errors="coerce")
    df_youtube["views"] = pd.to_numeric(df_youtube["views"], errors="coerce")

    dados = pd.DataFrame({
        "streams_spotify": df_spotify["streams"].fillna(0).head(50),
        "views_youtube": df_youtube["views"].fillna(0).head(50)
    })

    scaler = StandardScaler()
    dados_scaled = scaler.fit_transform(dados)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(dados_scaled)

    dados["cluster"] = labels
    for i in range(3):
        st.markdown(f"### 🎯 Cluster {i}")
        cluster = dados[dados["cluster"] == i]
        st.dataframe(cluster)