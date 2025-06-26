import pandas as pd
import streamlit as st
from utils.spotify_data import coletar_dados_spotify
from utils.youtube_data import coletar_dados_youtube
from utils.sentimentos import analisar_sentimentos
from utils.associacoes import gerar_associacoes

@st.cache_data(show_spinner=False)
def coletar_dados():
    try:
        with st.spinner("🎶 Coletando dados do Spotify..."):
            df_spotify = coletar_dados_spotify()
            df_spotify["fonte"] = "Spotify"
        with st.spinner("📺 Coletando dados do YouTube..."):
            df_youtube = coletar_dados_youtube()
            df_youtube["fonte"] = "YouTube"
        return pd.concat([df_spotify, df_youtube], ignore_index=True)
    except Exception as e:
        st.error(f"Erro na coleta: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def processar_dados(df):
    with st.spinner("🧠 Analisando sentimentos..."):
        df = analisar_sentimentos(df)
    with st.spinner("🔗 Gerando associações com Apriori..."):
        associacoes, temas = gerar_associacoes(df)
    return df, associacoes, temas
