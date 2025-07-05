import pandas as pd
import googleapiclient.discovery
import streamlit as st
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_youtube():
    try:
        # Carregar credenciais do secrets.toml
        api_key = st.secrets["youtube"]["api_key"]
        
        # Inicializar cliente YouTube
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        
        # Busca por vídeos populares
        logger.info("Coletando vídeos populares no YouTube (região: BR)")
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode="BR",
            maxResults=50
        )
        response = request.execute()
        
        if response["items"]:
            videos = []
            for item in response["items"]:
                videos.append({
                    "titulo": item["snippet"]["title"],
                    "canal": item["snippet"]["channelTitle"],
                    "visualizacoes": int(item["statistics"].get("viewCount", 0))
                })
            df = pd.DataFrame(videos)
            logger.info(f"Dados coletados do YouTube: {len(df)} vídeos")
            return df
        else:
            logger.warning("Nenhum vídeo encontrado no YouTube.")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Falha ao coletar dados do YouTube: {str(e)}")
        return pd.DataFrame()
