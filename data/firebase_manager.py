import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json

def inicializar_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)

def salvar_df_firestore(df, colecao):
    inicializar_firebase()
    db = firestore.client()

    for idx, row in df.iterrows():
        doc_ref = db.collection(colecao).document(str(idx))
        doc_ref.set(row.to_dict())

def carregar_df_firestore(colecao):
    inicializar_firebase()
    db = firestore.client()

    docs = db.collection(colecao).stream()
    registros = [doc.to_dict() for doc in docs]
    return pd.DataFrame(registros)
