import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import KMeans
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analisar_apriori(df_trends, df_x):
    """
    Gera regras de associação entre termos do Google Trends e X.
    """
    try:
        st.subheader("🔗 Regras de Associação (Trends e X)")
        # Combinar dados
        combined_data = []
        if not df_trends.empty and "termo" in df_trends.columns:
            combined_data.extend(df_trends["termo"].tolist())
        if not df_x.empty and "assunto" in df_x.columns:
            combined_data.extend(df_x["assunto"].tolist())
        
        if not combined_data:
            st.warning("Nenhum dado válido para análise de associação.")
            logger.warning("Nenhum dado válido para análise de associação.")
            return
        
        # Criar matriz de presença
        unique_terms = list(set(combined_data))
        presence_matrix = pd.DataFrame(0, index=range(len(combined_data)), columns=unique_terms)
        for i, term in enumerate(combined_data):
            presence_matrix.loc[i, term] = 1
        
        # Aplicar Apriori
        frequent_itemsets = apriori(presence_matrix, min_support=0.01, use_colnames=True)
        if frequent_itemsets.empty:
            st.warning("Nenhum conjunto frequente encontrado.")
            logger.warning("Nenhum conjunto frequente encontrado.")
            return
        
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
        if rules.empty:
            st.warning("Nenhuma regra de associação encontrada.")
            logger.warning("Nenhuma regra de associação encontrada.")
            return
        
        rules = rules.sort_values("lift", ascending=False).head(10)
        st.dataframe(rules[["antecedents", "consequents", "support", "confidence", "lift"]])
        st.markdown("**Insight para produtores**: Use combinações de termos com alto 'lift' (ex.: 'música' → 'festival') para criar conteúdo que conecte temas populares no Google Trends e X.")
    except Exception as e:
        st.warning(f"Erro ao gerar regras de associação: {str(e)}")
        logger.error(f"Erro ao gerar regras de associação: {str(e)}")

def analisar_clusters(df_spotify, df_youtube):
    """
    Gera clusters de músicas e vídeos com base em popularidade e visualizações.
    """
    try:
        st.subheader("🧩 Clusters de Conteúdo (Spotify e YouTube)")
        # Combinar dados
        df_combined = pd.DataFrame()
        if not df_spotify.empty and "popularidade" in df_spotify.columns:
            df_spotify = df_spotify[["popularidade"]].copy()
            df_spotify["fonte"] = "Spotify"
            df_combined = pd.concat([df_combined, df_spotify], ignore_index=True)
        if not df_youtube.empty and "visualizacoes" in df_youtube.columns:
            df_youtube = df_youtube[["visualizacoes"]].copy()
            df_youtube["fonte"] = "YouTube"
            df_youtube = df_youtube.rename(columns={"visualizacoes": "popularidade"})
            df_combined = pd.concat([df_combined, df_youtube], ignore_index=True)
        
        if df_combined.empty:
            st.warning("Nenhum dado válido para clustering.")
            logger.warning("Nenhum dado válido para clustering.")
            return
        
        # Normalizar popularidade
        df_combined["popularidade"] = (df_combined["popularidade"] - df_combined["popularidade"].min()) / (df_combined["popularidade"].max() - df_combined["popularidade"].min())
        
        # Aplicar KMeans
        kmeans = KMeans(n_clusters=3, random_state=42)
        df_combined["cluster"] = kmeans.fit_predict(df_combined[["popularidade"]])
        
        # Visualizar clusters
        chart = alt.Chart(df_combined).mark_circle(size=60).encode(
            x=alt.X("popularidade:Q", title="Popularidade Normalizada"),
            y=alt.Y("fonte:N", title="Fonte"),
            color=alt.Color("cluster:N", title="Cluster"),
            tooltip=["popularidade", "fonte", "cluster"]
        ).properties(
            title="Clusters de Popularidade (Spotify e YouTube)",
            width="container"
        )
        st.altair_chart(chart, use_container_width=True)
        st.markdown("**Insight para produtores**: Clusters com alta popularidade indicam conteúdos de alto impacto. Foque em criar conteúdo semelhante aos itens nos clusters superiores.")
    except Exception as e:
        st.warning(f"Erro ao gerar clusters: {str(e)}")
        logger.error(f"Erro ao gerar clusters: {str(e)}")
