import tweepy
import pandas as pd
import streamlit as st
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_x(max_retries=3, retry_delay=5):
    """
    Coleta dados de tendências do X usando a API v1.1 via tweepy.
    """
    try:
        # Configurar credenciais
        bearer_token = st.secrets["x"]["bearer_token"]
        client = tweepy.Client(bearer_token=bearer_token)
    except KeyError:
        st.error("A secret 'bearer_token' do X não foi configurada corretamente no Streamlit Cloud.")
        logger.error("Secret do X ausente.")
        return pd.DataFrame(columns=["termo", "volume"])

    woeid = 23424768  # WOEID do Brasil
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{max_retries} de coletar tendências do X")
            st.write(f"Tentando coletar tendências do X (Tentativa {attempt + 1}/{max_retries})...")

            trends = client.get_place_trends(woeid)
            if trends and isinstance(trends, list) and len(trends) > 0 and "trends" in trends[0]:
                trends_list = [
                    {
                        "termo": trend.get("name", "N/A"),
                        "volume": trend.get("tweet_volume", 0)
                    }
                    for trend in trends[0]["trends"]
                    if trend.get("name")
                ]
                df = pd.DataFrame(trends_list)
                st.success(f"Dados de tendências do X coletados com sucesso: {len(df)} termos")
                logger.info(f"Sucesso: {len(df)} termos coletados do X")
                return df
            else:
                st.error("Resposta da API do X não contém 'trends' ou está vazia.")
                logger.error("Resposta da API do X não contém 'trends' ou está vazia.")
                return pd.DataFrame(columns=["termo", "volume"])

        except tweepy.TweepyException as e:
            st.error(f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}")
            logger.error(f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}")
            if attempt < max_retries - 1:
                st.write(f"Aguardando {retry_delay} segundos antes da próxima tentativa...")
                time.sleep(retry_delay)

    st.error(
        "Não foi possível coletar dados do X após várias tentativas. "
        "Verifique as credenciais da API do X ou contate o suporte."
    )
    logger.error("Falha ao coletar dados do X após todas as tentativas")
    return pd.DataFrame(columns=["termo", "volume"])
