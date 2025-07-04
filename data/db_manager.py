import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "database.db"

def conectar_db():
    return sqlite3.connect(DB_PATH)

def salvar_df_em_tabela(df, nome_tabela):
    try:
        conn = conectar_db()
        df.to_sql(nome_tabela, conn, if_exists="replace", index=False)
        st.success(f"Tabela '{nome_tabela}' salva com sucesso.")
    except Exception as e:
        st.error(f"Erro ao salvar tabela '{nome_tabela}': {e}")
    finally:
        conn.close()

def carregar_tabela(nome_tabela):
    conn = conectar_db()
    try:
        # Verifica se a tabela existe
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (nome_tabela,)
        )
        if not cursor.fetchone():
            st.warning(f"A tabela '{nome_tabela}' ainda não foi criada.")
            return pd.DataFrame()

        df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a tabela '{nome_tabela}': {e}")
        return pd.DataFrame()
    finally:
        conn.close()
