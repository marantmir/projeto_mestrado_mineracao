from pytrends.request import TrendReq
import pandas as pd
import streamlit as st
import time
import logging
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_trends(max_retries=3, retry_delay=5):
    """
    Coleta dados de tendências do Google Trends para o Brasil.
    Implementa retentativas para lidar com limites de taxa ou erros intermitentes.
    """
    try:
        # Inicializar pytrends sem retries internos para evitar conflitos
        pytrends = TrendReq(hl='pt-BR', tz=-180)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{max_retries} de coletar tendências do Google Trends para o Brasil")
                st.write(f"Tentando coletar tendências do Google Trends (Tentativa {attempt + 1}/{max_retries})...")
                
                # Coletar termos de pesquisa em alta no Brasil
                trending_df = pytrends.trending_searches(pn="brazil")
                trending_df.columns = ["termo"]
                
                st.success(f"Dados de tendências coletados com sucesso: {len(trending_df)} termos")
                logger.info(f"Sucesso: {len(trending_df)} termos coletados")
                return trending_df
                
            except (requests.exceptions.RequestException, Exception) as e:
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
