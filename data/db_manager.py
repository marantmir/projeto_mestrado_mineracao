import sqlite3
import pandas as pd

def conectar_db():
    return sqlite3.connect("database.db")

def salvar_df_em_tabela(df, nome_tabela):
    conn = conectar_db()
    df.to_sql(nome_tabela, conn, if_exists="replace", index=False)
    conn.close()

def carregar_tabela(nome_tabela):
    conn = conectar_db()
    try:
        # Verifica se a tabela existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (nome_tabela,))
        if not cursor.fetchone():
            st.warning(f"A tabela '{nome_tabela}' não existe ainda.")
            return pd.DataFrame()
        
        df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)
    except Exception as e:
        st.error(f"Erro ao carregar a tabela '{nome_tabela}': {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df


