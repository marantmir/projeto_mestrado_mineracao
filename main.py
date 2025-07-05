import streamlit as st
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from data.spotify_data import coletar_dados_spotify
    from data.youtube_data import coletar_dados_youtube
    from data.google_trends import coletar_dados_trends
    from data.x_data import coletar_dados_x
    from data.firebase_manager import salvar_df_firestore, carregar_df_firestore
    from insights.visualizacoes import gerar_visoes
    from insights.aprendizado import analisar_apriori, analisar_clusters
except ImportError as e:
    st.error(f"Erro ao importar módulos: {str(e)}. Verifique os diretórios 'data/' e 'insights/'.")
    if st.button("Mostrar Logs"):
        st.text(logger.handlers[0].stream.getvalue())  # Exibe logs se disponível
    logger.error(f"Erro de importação: {str(e)}")
    st.stop()

st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
st.title("🎧 Radar Cultural Inteligente")
st.markdown("Análise automatizada de tendências culturais com IA aplicada.")

if "dados_carregados" not in st.session_state:
    st.session_state.dados_carregados = False

if st.button("🔄 Coletar Novos Dados"):
    with st.spinner("Coletando dados de todas as plataformas..."):
        try:
            df_spotify = coletar_dados_spotify()
            df_youtube = coletar_dados_youtube()
            df_trends = coletar_dados_trends()
            df_x = coletar_dados_x()

            dataframes = {"spotify": df_spotify, "youtube": df_youtube, "trends": df_trends, "twitter": df_x}
            all_valid = True
            for name, df in dataframes.items():
                if not isinstance(df, pd.DataFrame):
                    st.error(f"Falha ao coletar dados de {name}: Dados inválidos.")
                    all_valid = False
                elif df.empty:
                    st.warning(f"Dados de {name} estão vazios. Verifique APIs ou conexão.")
                else:
                    salvar_df_firestore(df, name)
                    st.success(f"Dados de {name} salvos: {len(df)} registros.")
            if all_valid:
                st.session_state.dados_carregados = True
                st.success("✅ Dados coletados e salvos!")
            else:
                st.session_state.dados_carregados = True
                st.warning("Alguns dados falharam. Visualizações com dados disponíveis.")
        except Exception as e:
            st.error(f"Erro na coleta: {str(e)}. Verifique logs para detalhes.")
            if st.button("Mostrar Logs"):
                st.text(logger.handlers[0].stream.getvalue())
            st.session_state.dados_carregados = False

@st.cache_data
def carregar_tabelas():
    try:
        return {
            "spotify": carregar_df_firestore("spotify"),
            "youtube": carregar_df_firestore("youtube"),
            "trends": carregar_df_firestore("trends"),
            "twitter": carregar_df_firestore("twitter")
        }
    except Exception as e:
        st.error(f"Erro ao carregar tabelas: {str(e)}")
        logger.error(f"Erro ao carregar tabelas: {str(e)}")
        return {"spotify": pd.DataFrame(), "youtube": pd.DataFrame(), "trends": pd.DataFrame(), "twitter": pd.DataFrame()}

tabelas = carregar_df_firestore()
df_spotify, df_youtube, df_trends, df_x = tabelas["spotify"], tabelas["youtube"], tabelas["trends"], tabelas["twitter"]

# Validação de colunas
def validar_dados(df, fonte, colunas_esperadas):
    if not all(col in df.columns for col in colunas_esperadas):
        logger.warning(f"Faltam colunas em {fonte}: {colunas_esperadas}")
        return False
    return True

if not (validar_dados(df_spotify, "Spotify", ["nome", "artista", "popularidade"]) and
        validar_dados(df_youtube, "YouTube", ["titulo", "canal", "visualizacoes"]) and
        validar_dados(df_trends, "Google Trends", ["termo"]) and
        validar_dados(df_x, "X", ["assunto", "volume", "created_at"])):
    st.warning("Dados carregados podem estar incompletos. Verifique a coleta.")

st.header("📊 Dados Coletados")
for table, df in [("Spotify", df_spotify), ("YouTube", df_youtube), ("Google Trends", df_trends), ("X", df_x)]:
    st.subheader(table)
    if isinstance(df, pd.DataFrame) and not df.empty:
        st.dataframe(df)
    else:
        st.info(f"Sem dados para {table}. Clique em '🔄 Coletar Novos Dados'.")

if st.session_state.dados_carregados:
    try:
        st.header("📈 Visualizações e Insights")
        gerar_visoes(df_spotify, df_youtube, df_trends, df_x)

        if isinstance(df_trends, pd.DataFrame) and not df_trends.empty and isinstance(df_x, pd.DataFrame) and not df_x.empty:
            st.header("🧠 Análises Avançadas com IA")
            analisar_apriori(df_trends, df_x)
        if isinstance(df_spotify, pd.DataFrame) and not df_spotify.empty and isinstance(df_youtube, pd.DataFrame) and not df_youtube.empty:
            analisar_clusters(df_spotify, df_youtube)
    except Exception as e:
        st.error(f"Erro em visualizações/análises: {str(e)}. Verifique logs.")
        if st.button("Mostrar Logs"):
            st.text(logger.handlers[0].stream.getvalue())
else:
    st.info("Clique em '🔄 Coletar Novos Dados' para iniciar.")
