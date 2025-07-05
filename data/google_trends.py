import pandas as pd
import logging
import json
from pytrends.request import TrendReq
import time
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_trends(max_retries=3):
    try:
        # Criar diretórios se não existirem
        os.makedirs('data', exist_ok=True)
        os.makedirs('insights', exist_ok=True)

        # Inicializar pytrends
        pytrends = TrendReq(hl='pt-BR', tz=360)
        
        # Tentar coletar trending searches com retries
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{max_retries} de coletar tendências do Google Trends para o Brasil")
                trending_df = pytrends.trending_searches(pn="brazil")
                trending_df.columns = ["termo"]
                if not trending_df.empty:
                    logger.info(f"Dados coletados do Google Trends: {len(trending_df)} termos")
                    trending_df.to_csv('data/trending_searches.csv', index=False)
                    logger.info("Dados salvos em 'data/trending_searches.csv'")
                    return trending_df
            except Exception as e:
                logger.error(f"Tentativa {attempt}/{max_retries} falhou: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue

        # Fallback para interest_over_time
        logger.info("Tentando fallback com interest_over_time")
        keywords = ["música", "cultura", "tendências"]
        pytrends.build_payload(kw_list=keywords, timeframe='now 7-d', geo='BR')
        df = pytrends.interest_over_time()
        if not df.empty:
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            df = df.reset_index()
            logger.info(f"Dados coletados via interest_over_time: {len(df)} registros")
            logger.info(f"Estrutura do DataFrame: {df.head().to_dict()}")
            df.to_csv('data/interest_over_time.csv', index=False)
            logger.info("Dados salvos em 'data/interest_over_time.csv'")
            return df
        else:
            logger.warning("Nenhum dado retornado por interest_over_time")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Falha ao coletar dados do Google Trends após todas as tentativas: {str(e)}")
        return pd.DataFrame()

def generate_chart_config(df):
    if df.empty or 'date' not in df.columns:
        logger.error("DataFrame vazio ou sem coluna 'date'. Não é possível gerar o gráfico.")
        return None

    # Converter datas para string no formato 'YYYY-MM-DD'
    labels = df['date'].dt.strftime('%Y-%m-%d').tolist()
    
    # Definir cores para cada termo
    colors = [
        {"border": "#FF6384", "background": "rgba(255, 99, 132, 0.2)"},
        {"border": "#36A2EB", "background": "rgba(54, 162, 235, 0.2)"},
        {"border": "#4BC0C0", "background": "rgba(75, 192, 192, 0.2)"}
    ]
    
    # Criar datasets para cada keyword
    datasets = []
    for i, keyword in enumerate([col for col in df.columns if col != 'date']):
        datasets.append({
            "label": keyword,
            "data": df[keyword].tolist(),
            "borderColor": colors[i % len(colors)]["border"],
            "backgroundColor": colors[i % len(colors)]["background"],
            "fill": False
        })

    # Configuração do Chart.js
    chart_config = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "title": {
                "display": True,
                "text": "Google Trends: Interesse ao Longo do Tempo (Últimos 7 Dias)"
            },
            "scales": {
                "xAxes": [
                    {
                        "scaleLabel": {
                            "display": True,
                            "labelString": "Data"
                        }
                    }
                ],
                "yAxes": [
                    {
                        "scaleLabel": {
                            "display": True,
                            "labelString": "Interesse (0-100)"
                        },
                        "ticks": {
                            "beginAtZero": True,
                            "max": 100
                        }
                    }
                ]
            }
        }
    }
    return chart_config

# Exemplo de uso
if __name__ == "__main__":
    df = coletar_dados_trends()
    if not df.empty:
        print("Dados coletados:")
        print(df.head())
        chart_config = generate_chart_config(df)
        if chart_config:
            print("Configuração do gráfico:")
            print(json.dumps(chart_config, indent=2))
            with open('insights/chart_config.json', 'w') as f:
                json.dump(chart_config, f, indent=2)
            logger.info("Configuração do gráfico salva em 'insights/chart_config.json'")
    else:
        print("Nenhum dado coletado.")
