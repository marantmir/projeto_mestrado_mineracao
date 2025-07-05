import pandas as pd
import googleapiclient.discovery
import streamlit as st
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_youtube(max_retries=3):
    try:
        api_key = st.secrets["youtube"]["api_key"]
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{max_retries}: Coletando vídeos populares (BR)")
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
                            "visualizacoes": int(item["statistics"].get("viewCount", 0)),
                            "likes": int(item["statistics"].get("likeCount", 0))
                        })
                    df = pd.DataFrame(videos)
                    logger.info(f"Dados coletados: {len(df)} vídeos")
                    return df
            except Exception as e:
                logger.error(f"Tentativa {attempt} falhou: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                continue
        logger.warning("Nenhum vídeo após retries")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Falha na coleta: {str(e)}")
        return pd.DataFrame()
