import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import logging
import streamlit as st

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_spotify():
    try:
        # Carregar credenciais do secrets.toml
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        
        # Inicializar cliente Spotify
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Busca genérica por músicas de 2025
        logger.info("Tentando coletar músicas com query: Músicas de 2025 (Query: year:2025, Market: BR)")
        results = sp.search(q="year:2025", type="track", market="BR", limit=50)
        
        if results["tracks"]["items"]:
            tracks = []
            for item in results["tracks"]["items"]:
                tracks.append({
                    "nome": item["name"],
                    "artista": item["artists"][0]["name"],
                    "popularidade": item["popularity"],
                    "id_musica": item["id"]
                })
            df = pd.DataFrame(tracks)
            logger.info(f"Dados coletados do Spotify: {len(df)} músicas")
            return df
        else:
            logger.warning("Nenhuma música encontrada para a query year:2025")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Falha ao coletar dados do Spotify: {str(e)}")
        return pd.DataFrame()
