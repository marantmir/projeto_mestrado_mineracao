import streamlit as st
import plotly.express as px

def gerar_visoes(df_spotify, df_youtube, df_trends, df_x):
    st.subheader("Visualizações")
    if not df_spotify.empty:
        fig = px.bar(df_spotify.head(10), x="artista", y="popularidade", title="Popularidade por Artista (Spotify)")
        st.plotly_chart(fig)
    if not df_youtube.empty:
        fig = px.bar(df_youtube.head(10), x="canal", y="visualizacoes", title="Visualizações por Canal (YouTube)")
        st.plotly_chart(fig)
    # Adicione mais visualizações para trends e x conforme necessário
