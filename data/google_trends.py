from pytrends.request import TrendReq
import pandas as pd
import streamlit as st
import time
import logging
import requests
try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = requests  # Fallback para requests padrão se curl_cffi não estiver disponível

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_google_cookies(impersonate_version='chrome110'):
    """Obtém cookies para simular um navegador."""
    try:
        session = cffi_requests.Session()
        response = session.get("https://www.google.com", impersonate=impersonate_version)
        return session.cookies.get_dict()
    except Exception as e:
        logger.error(f"Erro ao obter cookies: {str(e)}")
        return {}

def coletar_dados_trends(max_retries=3, retry_delay=5):
    """
    Coleta dados de tendências do Google Trends para o Brasil.
    Usa cookies e retentativas para evitar bloqueios e erros de endpoint.
    """
    try:
        # Inicializar pytrends com cookies
        requests_args = {'cookies': get_google_cookies()}
        pytrends = TrendReq(hl='pt-BR', tz=-180, requests_args=requests_args)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{max_retries} de coletar tendências do Google Trends para o Brasil")
                st.write(f"Tentando coletar tendências do Google Trends (Tentativa {attempt + 1}/{max_retries})...")
                
                # Tentar coletar termos de pesquisa em alta
                trending_df = pytrends.trending_searches(pn="brazil")
                trending_df.columns = ["termo"]
                
                # Se trending_searches falhar, tentar interest_over_time
                if trending_df.empty or len(trending_df) == 0:
                    logger.warning("trending_searches retornou DataFrame vazio. Tentando interest_over_time...")
                    pytrends.build_payload(kw_list=["música"], timeframe="now 7-d", geo="BR")
                    trending_df = pytrends.interest_over_time()
                    if not trending_df.empty:
                        trending_df = pd.DataFrame({"termo": ["música"]})
                    else:
                        trending_df = pd.DataFrame(columns=["termo"])
                
                st.success(f"Dados de tendências coletados com sucesso: {len(trending_df)} termos")
                logger.info(f"Sucesso: {len(trending_df)} termos coletados")
                return trending_df
                
            except Exception as e:
                st.error(f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}")
                logger.error(f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}")
                
                if attempt < max_retries - 1:
                    st.write(f"Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    time.sleep(retry_delay)
                continue

        st.error(
            "Não foi possível coletar dados do Google Trends após várias tentativas. "
            "Verifique a conexão com a API ou contate o suporte do Google Trends."
        )
        logger.error("Falha ao coletar dados do Google Trends após todas as tentativas")
        return pd.DataFrame(columns=["termo"])  # Retorna DataFrame vazio como fallback

    except Exception as e:
        st.error(f"Erro ao inicializar o Google Trends: {str(e)}")
        logger.error(f"Erro ao inicializar o Google Trends: {str(e)}")
        return pd.DataFrame(columns=["termo"])  # Retorna DataFrame vazio como fallback
