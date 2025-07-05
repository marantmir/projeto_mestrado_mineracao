from supabase import create_client
import pandas as pd
import streamlit as st
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inicializar_supabase():
    if "supabase" not in st.secrets or "url" not in st.secrets["supabase"] or "key" not in st.secrets["supabase"]:
        logger.error("Credenciais do Supabase não encontradas em st.secrets")
        st.error("Erro: Credenciais do Supabase ausentes. Verifique o secrets.toml.")
        st.stop()
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def salvar_df_supabase(df, tabela):
    supabase = inicializar_supabase()
    try:
        # Converter DataFrame para lista de dicionários
        data = df.to_dict(orient='records')
        response = supabase.table(tabela).insert(data).execute()
        logger.info(f"Dados salvos em {tabela}: {len(data)} registros")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar em {tabela}: {str(e)}")
        return False

def carregar_df_supabase(tabela, colunas_esperadas=None):
    supabase = inicializar_supabase()
    try:
        response = supabase.table(tabela).select("*").execute()
        registros = response.data
        if not registros:
            logger.warning(f"Nenhum dado encontrado em {tabela}")
            return pd.DataFrame()
        df = pd.DataFrame(registros)
        if colunas_esperadas and not all(col in df.columns for col in colunas_esperadas):
            logger.warning(f"Colunas ausentes em {tabela}: {colunas_esperadas}")
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar de {tabela}: {str(e)}")
        return pd.DataFrame()
