import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import streamlit as st
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets:
                if "key" in st.secrets["firebase"]:
                    key_dict = json.loads(st.secrets["firebase"]["key"])
                    cred = credentials.Certificate(key_dict)
                elif "key_path" in st.secrets["firebase"]:
                    cred_path = st.secrets["firebase"]["key_path"]
                    if os.path.exists(cred_path):
                        cred = credentials.Certificate(cred_path)
                    else:
                        raise FileNotFoundError(f"Arquivo de credenciais não encontrado em {cred_path}")
                else:
                    raise KeyError("Nenhuma chave 'key' ou 'key_path' encontrada em st.secrets['firebase']")
                firebase_admin.initialize_app(cred)
                logger.info("Firebase inicializado com sucesso")
            else:
                raise KeyError("Seção 'firebase' não encontrada em st.secrets")
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase: {str(e)}")
            st.error(f"Erro ao inicializar Firebase: {str(e)}. Verifique o secrets.toml ou as configurações do Streamlit Cloud.")
            st.stop()

def salvar_df_firestore(df, colecao):
    inicializar_firebase()
    db = firestore.client()
    batch = db.batch()
    for idx, row in df.iterrows():
        doc_ref = db.collection(colecao).document(str(idx))
        batch.set(doc_ref, row.to_dict())
    batch.commit()
    logger.info(f"Dados salvos em {colecao} em lote")

def carregar_df_firestore(colecao, colunas_esperadas=None):
    inicializar_firebase()
    db = firestore.client()
    docs = db.collection(colecao).stream()
    registros = [doc.to_dict() for doc in docs]
    if not registros:
        logger.warning(f"Nenhum dado encontrado em {colecao}")
        return pd.DataFrame()
    df = pd.DataFrame(registros)
    if colunas_esperadas and not all(col in df.columns for col in colunas_esperadas):
        logger.warning(f"Colunas ausentes em {colecao}: {colunas_esperadas}")
        return pd.DataFrame()
    return df
