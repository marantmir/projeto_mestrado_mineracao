import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import KMeans
import logging
import re
from nltk.corpus import stopwords
import nltk
from sklearn.metrics import silhouette_score

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
            st.warning("Nenhum dado válido para análise.")
            return
        
        unique_terms = list(set(combined_data))
        term_counts = pd.Series(combined_data).value_counts()
        presence_matrix = pd.DataFrame(0, index=range(len(combined_data)), columns=unique_terms)
        for i, term in enumerate(combined_data):
            presence_matrix.loc[i, term] = term_counts[term] / len(combined_data)  # Peso baseado em frequência
        
        min_support = max(0.01, 1/len(unique_terms))
        frequent_itemsets = apriori(presence_matrix, min_support=min_support, use_colnames=True)
        if frequent_itemsets.empty:
            st.warning("Nenhum conjunto frequente.")
            return
        
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
        if rules.empty:
            st.warning("Nenhuma regra encontrada.")
            return
        
        rules = rules.sort_values("lift", ascending=False).head(10)
        st.dataframe(rules[["antecedents", "consequents", "support", "confidence", "lift"]])
        st.markdown("**Insight**: Combine termos com alto lift para conteúdo viral.")
    except Exception as e:
        st.warning(f"Erro na associação: {str(e)}")

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
            st.warning("Nenhum dado para clustering.")
            return
        
        df_combined["popularidade"] = (df_combined["popularidade"] - df_combined["popularidade"].min()) / (df_combined["popularidade"].max() - df_combined["popularidade"].min())
        df_combined["genero_code"] = df_combined["genero_inferido"].astype("category").cat.codes
        
        # Determinar número ideal de clusters com silhouette score
        max_clusters = min(10, len(df_combined) // 10)  # Limite razoável
        silhouette_scores = []
        for n in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=n, random_state=42)
            cluster_labels = kmeans.fit_predict(df_combined[["popularidade", "genero_code"]])
            score = silhouette_score(df_combined[["popularidade", "genero_code"]], cluster_labels)
            silhouette_scores.append((n, score))
        n_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df_combined["cluster"] = kmeans.fit_predict(df_combined[["popularidade", "genero_code"]])
        
        chart = alt.Chart(df_combined).mark_circle(size=60).encode(
            x=alt.X("popularidade:Q", title="Popularidade Normalizada"),
            y=alt.Y("genero_inferido:N", title="Gênero"),
            color=alt.Color("cluster:N", title="Cluster"),
            tooltip=["popularidade", "fonte", "genero_inferido", "cluster"]
        ).properties(
            title=f"Clusters de Popularidade e Gênero (n={n_clusters})",
            width="container",
            description="Gráfico de dispersão mostrando clusters de popularidade e gênero."
        )
        st.altair_chart(chart, use_container_width=True)
        st.markdown(f"**Insight**: Clusters com alta popularidade e gêneros específicos (n={n_clusters}) indicam tendências.")
    except Exception as e:
        st.warning(f"Erro no clustering: {str(e)}")
