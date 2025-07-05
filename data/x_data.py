import pandas as pd
import tweepy
import logging
import streamlit as st

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_x():
    try:
        # Carregar credenciais do secrets.toml
        bearer_token = st.secrets["x"]["bearer_token"]
        
        # Inicializar cliente Tweepy
        client = tweepy.Client(bearer_token=bearer_token)
        
        logger.info("Tentativa 1/3 de coletar tweets recentes do X")
        query = "from:Brazil -is:retweet"  # Buscar tweets do Brasil, excluindo retweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=100,
            tweet_fields=["public_metrics", "created_at"]
        )
        
        if tweets.data:
            data = []
            for tweet in tweets.data:
                data.append({
                    "assunto": tweet.text,
                    "volume": tweet.public_metrics.get("impression_count", 0),
                    "created_at": tweet.created_at
                })
            df = pd.DataFrame(data)
            logger.info(f"Dados coletados do X: {len(df)} tweets")
            return df
        else:
            logger.warning("Nenhum tweet retornado pela busca")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Falha ao coletar dados do X: {str(e)}")
        return pd.DataFrame()
