import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

def coletar_dados_spotify(max_itens=50):
    """
    Coleta dados reais do Spotify com base em lançamentos recentes.
    
    Args:
        max_itens (int): Quantidade máxima de músicas a serem coletadas.
        
    Returns:
        pd.DataFrame: DataFrame com informações das músicas coletadas.
    """
    # Validação de credenciais
    if "SPOTIFY_CLIENT_ID" not in st.secrets or "SPOTIFY_CLIENT_SECRET" not in st.secrets:
        st.error("❌ Credenciais do Spotify não encontradas. Configure-as no arquivo secrets.toml ou nas configurações do app.")
        st.stop()

    try:
        auth_manager = SpotifyClientCredentials(
            client_id=st.secrets["SPOTIFY_CLIENT_ID"],
            client_secret=st.secrets["SPOTIFY_CLIENT_SECRET"]
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        resultados = []
        offset = 0

        while len(resultados) < max_itens:
            limite = min(50, max_itens - len(resultados))
            dados = sp.new_releases(country='BR', limit=limite, offset=offset)
            albuns = dados['albums']['items']

            if not albuns:
                break

            for album in albuns:
