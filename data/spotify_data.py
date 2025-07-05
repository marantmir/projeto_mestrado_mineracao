import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import logging
import streamlit as st
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_spotify(max_retries=3):
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{max_retries}: Coletando músicas de 2025 (Market: BR)")
                results = sp.search(q="year:2025 popularity>50", type="track", market="BR", limit=50)
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
                    logger.info(f"Dados coletados: {len(df)} músicas")
                    return df
            except Exception as e:
                logger.error(f"Tentativa {attempt} falhou: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                continue
        logger.warning("Nenhuma música encontrada após retries")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Falha na coleta: {str(e)}")
        return pd.DataFrame()
