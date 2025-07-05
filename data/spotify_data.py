import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_spotify():
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Exemplo: buscar as 10 músicas mais populares
        results = sp.search(q='top tracks', type='track', limit=10)
        tracks = results['tracks']['items']

        data = []
        for track in tracks:
            data.append({
                "nome": track['name'],
                "artista": track['artists'][0]['name'],
                "popularidade": track['popularity']
            })
        df = pd.DataFrame(data)
        logger.info(f"Dados coletados do Spotify: {len(df)} registros")
        if df.empty:
            logger.warning("Nenhum dado coletado do Spotify")
        return df
    except Exception as e:
        logger.error(f"Erro ao coletar dados do Spotify: {str(e)}")
        return pd.DataFrame()
