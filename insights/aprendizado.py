import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import KMeans
import logging
import re
from nltk.corpus import stopwords
import nltk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    nltk.download('stopwords')
except:
    st.warning("Falha ao baixar recursos do NLTK.")

def analisar_apriori(df_trends, df_x):
    try:
        st.subheader("🔗 Regras de Associação (Trends e X)")
        combined_data = []
        if not df_trends.empty and "termo" in df_trends.columns:
            combined_data.extend(df_trends["termo"].tolist())
        if not df_x.empty and "assunto" in df_x.columns:
            stop_words = set(stopwords.words('portuguese'))
            df_x["assunto"] = df_x["assunto"].apply(lambda x: ' '.join(word for word in x.lower().split() if word not in stop_words))
            combined_data.extend(df_x["assunto"].tolist())
        
        if not combined_data:
            st.warning("Nenhum dado válido para análise de associação.")
            return
        
        unique_terms = list(set(combined_data))
        presence_matrix = pd.DataFrame(0, index=range(len(combined_data)), columns=unique_terms)
        for i, term in enumerate(combined_data):
            presence_matrix.loc[i, term] = 1
        
        min_support = max(0.01, 1/len(unique_terms))
        frequent_itemsets = apriori(presence_matrix, min_support=min_support, use_colnames=True)
        if frequent_itemsets.empty:
            st.warning("Nenhum conjunto frequente encontrado.")
            return
        
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
        if rules.empty:
            st.warning("Nenhuma regra de associação encontrada.")
            return
        
        rules = rules.sort_values("lift", ascending=False).head(10)
        st.dataframe(rules[["antecedents", "consequents", "support", "confidence", "lift"]])
        st.markdown("**Insight**: Combine termos com alto lift para criar conteúdo viral.")
    except Exception as e:
        st.warning(f"Erro ao gerar regras de associação: {str(e)}")

def analisar_clusters(df_spotify, df_youtube):
    try:
        st.subheader("🧩 Clusters de Conteúdo (Spotify e YouTube)")
        df_combined = pd.DataFrame()
        if not df_spotify.empty and "popularidade" in df_spotify.columns:
            df_spotify = df_spotify[["popularidade", "genero_inferido"]].copy()
            df_spotify["fonte"] = "Spotify"
            df_combined = pd.concat([df_combined, df_spotify], ignore_index=True)
        if not df_youtube.empty and "visualizacoes" in df_youtube.columns:
            df_youtube = df_youtube[["visualizacoes", "genero_inferido"]].copy()
            df_youtube["fonte"] = "YouTube"
            df_youtube = df_youtube.rename(columns={"visualizacoes": "popularidade"})
            df_combined = pd.concat([df_combined, df_youtube], ignore_index=True)
        
        if df_combined.empty:
            st.warning("Nenhum dado válido para clustering.")
            return
        
        df_combined["popularidade"] = (df_combined["popularidade"] - df_combined["popularidade"].min()) / (df_combined["popularidade"].max() - df_combined["popularidade"].min())
        df_combined["genero_code"] = df_combined["genero_inferido"].astype("category").cat.codes
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        df_combined["cluster"] = kmeans.fit_predict(df_combined[["popularidade", "genero_code"]])
        
        chart = alt.Chart(df_combined).mark_circle(size=60).encode(
            x=alt.X("popularidade:Q", title="Popularidade Normalizada"),
            y=alt.Y("genero_inferido:N", title="Gênero"),
            color=alt.Color("cluster:N", title="Cluster"),
            tooltip=["popularidade", "fonte", "genero_inferido", "cluster"]
        ).properties(
            title="Clusters de Popularidade e Gênero (Spotify e YouTube)",
            width="container"
        )
        st.altair_chart(chart, use_container_width=True)
        st.markdown("**Insight**: Clusters com alta popularidade e gêneros específicos indicam tendências.")
    except Exception as e:
        st.warning(f"Erro ao gerar clusters: {str(e)}")
