import requests
import pandas as pd
import streamlit as st
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_x(max_retries=3, retry_delay=5):
    """
    Coleta dados de tendências do X usando a API v1.1.
    Implementa retentativas para lidar com limites de taxa ou erros intermitentes.
    """
    try:
        # Configurar credenciais da API do X
        bearer_token = st.secrets["x"]["bearer_token"]
    except KeyError:
        st.error("A secret 'bearer_token' do X não foi configurada corretamente no Streamlit Cloud.")
        raise Exception("Secret do X ausente. Verifique a configuração em 'Manage app'.")

    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    # Endpoint de tendências do X v1.1 (WOEID 23424768 é Brasil)
    url = "https://api.twitter.com/1.1/trends/place.json?id=23424768"
    params = {}

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{max_retries} de coletar tendências do X")
            st.write(f"Tentando coletar tendências do X (Tentativa {attempt + 1}/{max_retries})...")

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                # Verificar se a resposta contém a estrutura esperada
                if isinstance(data, list) and len(data) > 0 and "trends" in data[0]:
                    trends = data[0]["trends"]
                    trends_list = [
                        {
                            "termo": trend.get("name", "N/A"),
                            "volume": trend.get("tweet_volume", 0)
                        }
                        for trend in trends
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

            try:
                error_details = response.json()
            except requests.exceptions.JSONDecodeError:
                error_details = response.text

            st.error(f"Tentativa {attempt + 1}/{max_retries} falhou: Status {response.status_code}, Detalhes: {error_details}")
            logger.error(f"Tentativa {attempt + 1}/{max_retries} falhou: Status {response.status_code}, Detalhes: {error_details}")

            if attempt < max_retries - 1:
                st.write(f"Aguardando {retry_delay} segundos antes da próxima tentativa...")
                time.sleep(retry_delay)

        except Exception as e:
            st.error(f"Erro inesperado na tentativa {attempt + 1}/{max_retries}: {str(e)}")
            logger.error(f"Erro inesperado na tentativa {attempt + 1}/{max_retries}: {str(e)}")

    st.error(
        "Não foi possível coletar dados do X após várias tentativas. "
        "Verifique as credenciais da API do X ou contate o suporte."
    )
    logger.error("Falha ao coletar dados do X após todas as tentativas")
    return pd.DataFrame(columns=["termo", "volume"])  # Retorna DataFrame vazio como fallback
