import pandas as pd
import logging
from pytrends.request import TrendReq
import time
import backoff

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função com retry para lidar com falhas transitórias
@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def coletar_dados_trends():
    try:
        # Inicializar pytrends
        pytrends = TrendReq(hl='pt-BR', tz=360)
        
        # Tentar coletar trending searches
        logger.info("Tentativa de coletar tendências do Google Trends para o Brasil")
        trending_df = pytrends.trending_searches(pn="brazil")
        trending_df.columns = ["termo"]
        if not trending_df.empty:
            logger.info(f"Dados coletados do Google Trends: {len(trending_df)} termos")
            return trending_df
        else:
            logger.warning("Nenhum dado retornado por trending_searches")

        # Adicionar pequeno atraso para evitar rate-limiting
        time.sleep(2)

        # Fallback para interest_over_time com termos genéricos
        logger.info("Tentando fallback com interest_over_time")
        keywords = ["música", "cultura", "tendências"]
        pytrends.build_payload(kw_list=keywords, timeframe='now 7-d', geo='BR')
        df = pytrends.interest_over_time()
        if not df.empty:
            # Remover coluna 'isPartial' se existir
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            df = df.reset_index()
            logger.info(f"Dados coletados via interest_over_time: {len(df)} registros")
            logger.info(f"Estrutura do DataFrame: {df.head().to_dict()}")
            return df
        else:
            logger.warning("Nenhum dado retornado por interest_over_time")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Falha ao coletar dados do Google Trends após todas as tentativas: {str(e)}")
        return pd.DataFrame()

# Exemplo de uso
if __name__ == "__main__":
    df = coletar_dados_trends()
    if not df.empty:
        print(df.head())
    else:
        print("Nenhum dado coletado.")
