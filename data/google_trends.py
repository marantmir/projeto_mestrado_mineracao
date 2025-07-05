import pandas as pd
import logging
import json
from pytrends.request import TrendReq
import time
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coletar_dados_trends(max_retries=3):
    try:
        pytrends = TrendReq(hl='pt-BR', tz=360)
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{max_retries} de coletar tendências do Google Trends para o Brasil")
                trending_df = pytrends.trending_searches(pn="brazil")
                trending_df.columns = ["termo"]
                if not trending_df.empty:
                    logger.info(f"Dados coletados: {len(trending_df)} termos")
                    st.session_state["trends_data"] = trending_df
                    return trending_df
            except Exception as e:
                logger.error(f"Tentativa {attempt} falhou: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                continue

        logger.info("Tentando fallback com interest_over_time")
        keywords = ["música", "cultura", "tendências"]
        pytrends.build_payload(kw_list=keywords, timeframe='now 7-d', geo='BR')
        df = pytrends.interest_over_time()
        if not df.empty:
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            df = df.reset_index()
            logger.info(f"Dados via interest_over_time: {len(df)} registros")
            st.session_state["trends_data"] = df
            return df
        logger.warning("Nenhum dado retornado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Falha na coleta: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def generate_chart_config(df):
    if df.empty or 'date' not in df.columns:
        logger.error("DataFrame vazio ou sem 'date'.")
        return None
    labels = df['date'].dt.strftime('%Y-%m-%d').tolist()
    colors = [
        {"border": "#FF6384", "background": "rgba(255, 99, 132, 0.2)"},
        {"border": "#36A2EB", "background": "rgba(54, 162, 235, 0.2)"},
        {"border": "#4BC0C0", "background": "rgba(75, 192, 192, 0.2)"}
    ]
    datasets = [
        {
            "label": col,
            "data": df[col].tolist(),
            "borderColor": colors[i % len(colors)]["border"],
            "backgroundColor": colors[i % len(colors)]["background"],
            "fill": False
        }
        for i, col in enumerate(df.columns) if col != 'date'
    ]
    chart_config = {
        "type": "line",
        "data": {"labels": labels, "datasets": datasets},
        "options": {
            "title": {"display": True, "text": "Google Trends: Interesse ao Longo do Tempo (Últimos 7 Dias)"},
            "scales": {
                "xAxes": [{"scaleLabel": {"display": True, "labelString": "Data"}}],
                "yAxes": [{"scaleLabel": {"display": True, "labelString": "Interesse (0-100)"}, "ticks": {"beginAtZero": True, "max": 100}}]
            }
        }
    }
    return chart_config

if __name__ == "__main__":
    df = coletar_dados_trends()
    if not df.empty:
        st.write("Dados coletados:")
        st.dataframe(df.head())
        chart_config = generate_chart_config(df)
        if chart_config:
            st.json(chart_config)
            logger.info("Gráfico configurado")
