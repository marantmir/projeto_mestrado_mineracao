# main.py
import streamlit as st
from data.spotify_data import coletar_dados_spotify
from data.youtube_data import coletar_dados_youtube
from data.google_trends import coletar_dados_trends
from data.x_data import coletar_dados_x
from data.db_manager import salvar_df_em_tabela, carregar_tabela
from insights.visualizacoes import gerar_visoes

st.title("🎧 Radar Cultural Inteligente")
st.markdown("Análise automatizada de tendências culturais sem filtros manuais.")

if st.button("🔄 Coletar Novos Dados"):
    df_spotify = coletar_dados_spotify()
    df_youtube = coletar_dados_youtube()
    df_trends = coletar_dados_trends()
    df_x = coletar_dados_x()

    salvar_df_em_tabela(df_spotify, "spotify")
    salvar_df_em_tabela(df_youtube, "youtube")
    salvar_df_em_tabela(df_trends, "trends")
    salvar_df_em_tabela(df_x, "twitter")

    st.success("Dados atualizados com sucesso!")

# Carrega e exibe
df_spotify = carregar_tabela("spotify")
df_youtube = carregar_tabela("youtube")
df_trends = carregar_tabela("trends")
df_x = carregar_tabela("twitter")

gerar_visoes(df_spotify, df_youtube, df_trends, df_x)
