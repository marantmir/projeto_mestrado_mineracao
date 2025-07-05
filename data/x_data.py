import pandas as pd
import tweepy
import logging
import streamlit as st
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data
def coletar_dados_x(start_time=None, max_retries=3):
    try:
        bearer_token = st.secrets["x"]["bearer_token"]
        client = tweepy.Client(bearer_token=bearer_token)
        query = "from:Brazil (filme OR série OR música) -is:retweet lang:pt"
        params = {"query": query, "max_results": 100, "tweet_fields": ["public_metrics", "created_at"]}
        if start_time:
            params["start_time"] = start_time
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{max_retries}: Coletando tweets")
                tweets = client.search_recent_tweets(**params)
                if tweets.data:
                    data = []
                    for tweet in tweets.data:
                        data.append({
                            "assunto": tweet.text,
                            "volume": tweet.public_metrics.get("impression_count", 0),
                            "created_at": tweet.created_at
                        })
                    df = pd.DataFrame(data)
                    logger.info(f"Dados coletados: {len(df)} tweets")
                    return df
            except Exception as e:
                logger.error(f"Tentativa {attempt} falhou: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                continue
        logger.warning("Nenhum tweet após retries")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Falha na coleta: {str(e)}")
        return pd.DataFrame()
