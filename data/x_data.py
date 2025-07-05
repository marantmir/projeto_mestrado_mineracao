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
    Coleta dados de tendências do X usando a API v2.
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

    # Endpoint de tendências do X (usando API v2, ajustar WOEID para Brasil)
    url = "https://api.twitter.com/2/trends/place?id=23424768"  # WOEID 23424768 é Brasil
    params = {}

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{max_retries} de coletar tendências do X")
            st.write(f"Tentando coletar tendências do X (Tentativa {attempt + 1}/{max_retries})...")

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                # Verificar se a resposta contém a estrutura esperada
                trends = data.get("data", {}).get("trends", [])
                if not trends:
                    # Tentar endpoint v1.1 como fallback
                    url_v1 = "https://api.twitter.com/1.1/trends/place.json?id=23424768"
                    response_v1 = requests.get(url_v1, headers=headers, params=params)
                    if response_v1.status_code == 200:
                        data_v1 = response_v1.json()
                        if isinstance(data_v1, list) and len(data_v1) > 0 and "trends" in data_v1[0]:
                            trends = data_v1[0]["trends"]
                        else:
                            st.error("Resposta da API v1.1 do X não contém 'trends' ou está vazia.")
                            logger.error("Resposta da API v1.1 do X não contém 'trends' ou está vazia.")
                            return pd.DataFrame(columns=["termo", "volume"])
                    else:
                        st.error(f"Falha no endpoint v1.1: Status {response_v1.status_code}")
                        logger.error(f"Falha no endpoint v1.1: Status {response_v1.status_code}")
                        return pd.DataFrame(columns=["termo", "volume"])

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
