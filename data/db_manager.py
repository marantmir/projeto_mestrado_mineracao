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
        df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)
    except Exception as e:
        st.error(f"Erro ao carregar tabela '{nome_tabela}': {e}")
        df = pd.DataFrame()  # Retorna dataframe vazio para evitar travamento do app
    finally:
        conn.close()
    return df

