
import streamlit as st
from utils.spotify_data import coletar_dados_spotify
from utils.youtube_data import coletar_dados_youtube
from utils.sentimentos import analisar_sentimentos
from utils.associacoes import gerar_associacoes
from utils.visualizacoes import gerar_visualizacoes
import pandas as pd

st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
st.title("🎧 Radar Cultural Inteligente")
st.markdown("Descubra tendências de temas e sentimentos a partir de dados reais do Spotify e YouTube para criar conteúdos que engajam!")

# Coleta de dados
with st.spinner("🔍 Coletando dados do Spotify..."):
    df_spotify = coletar_dados_spotify()
with st.spinner("🔍 Coletando dados do YouTube..."):
    df_youtube = coletar_dados_youtube()

# Unificação
df_spotify["fonte"] = "Spotify"
df_youtube["fonte"] = "YouTube"
df_dados = pd.concat([df_spotify, df_youtube], ignore_index=True)

# Análise de sentimentos
with st.spinner("🧠 Analisando sentimentos..."):
    df_dados = analisar_sentimentos(df_dados)

# Apriori e temas
with st.spinner("🔗 Gerando associações..."):
    associacoes, temas = gerar_associacoes(df_dados)

# Visualizações
st.subheader("🔍 Tendências Detectadas")
gerar_visualizacoes(df_dados, associacoes, temas)
