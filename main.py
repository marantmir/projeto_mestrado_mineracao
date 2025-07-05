import streamlit as st
import pandas as pd
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importações com tratamento de erros
try:
    from data.spotify_data import coletar_dados_spotify
    from data.youtube_data import coletar_dados_youtube
    from data.google_trends import coletar_dados_trends
    from data.x_data import coletar_dados_x
    from data.db_manager import salvar_df_em_tabela, carregar_tabela
    from insights.visualizacoes import gerar_visoes
    from insights.aprendizado import analisar_apriori, analisar_clusters
except ImportError as e:
    st.error(f"Erro ao importar módulos: {str(e)}. Verifique a estrutura do projeto no diretório 'data/' e 'insights/'.")
    logger.error(f"Erro de importação: {str(e)}")
    st.stop()

# Configuração da página
st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
st.title("🎧 Radar Cultural Inteligente")
st.markdown("Análise automatizada de tendências culturais com IA aplicada.")

# Inicializar estado da sessão
if "dados_carregados" not in st.session_state:
    st.session_state.dados_carregados = False

# Botão para coletar novos dados
if st.button("🔄 Coletar Novos Dados"):
    with st.spinner("Coletando dados de todas as plataformas..."):
        try:
            # Coletar dados com tratamento de falhas
            df_spotify = coletar_dados_spotify()
            df_youtube = coletar_dados_youtube()
            df_trends = coletar_dados_trends()
            df_x = coletar_dados_x()

            # Verificar e salvar DataFrames
            dataframes = {
                "spotify": df_spotify,
                "youtube": df_youtube,
                "trends": df_trends,
                "twitter": df_x
            }
            all_valid = True
            for name, df in dataframes.items():
                if not isinstance(df, pd.DataFrame):
                    st.error(f"Falha ao coletar dados de {name}: Dados retornados não são um DataFrame.")
                    logger.error(f"Falha ao coletar dados de {name}: Dados retornados não são um DataFrame.")
                    all_valid = False
                elif df.empty:
                    st.warning(f"Dados de {name} estão vazios. Verifique as credenciais da API ou a conexão.")
                    logger.warning(f"Dados de {name} estão vazios.")
                else:
                    salvar_df_em_tabela(df, name)
                    st.success(f"Dados de {name} salvos com sucesso: {len(df)} registros.")
                    logger.info(f"Dados de {name} salvos com sucesso: {len(df)} registros.")

            if all_valid:
                st.session_state.dados_carregados = True
                st.success("✅ Todos os dados foram coletados e salvos com sucesso!")
            else:
                st.warning("Alguns dados não foram coletados corretamente. Verifique os logs para detalhes.")

        except Exception as e:
            st.error(f"Erro durante a coleta de dados: {str(e)}")
            logger.error(f"Erro durante a coleta de dados: {str(e)}")
            st.session_state.dados_carregados = False

# Carregamento seguro dos dados
try:
    df_spotify = carregar_tabela("spotify")
    df_youtube = carregar_tabela("youtube")
    df_trends = carregar_tabela("trends")
    df_x = carregar_tabela("twitter")
except Exception as e:
    st.error(f"Erro ao carregar tabelas: {str(e)}. Verifique a conexão com o banco de dados.")
    logger.error(f"Erro ao carregar tabelas: {str(e)}")
    df_spotify = pd.DataFrame()
    df_youtube = pd.DataFrame()
    df_trends = pd.DataFrame()
    df_x = pd.DataFrame()

# Exibir dados carregados
st.header("📊 Dados Coletados")
for table, df in [("Spotify", df_spotify), ("YouTube", df_youtube), ("Google Trends", df_trends), ("X", df_x)]:
    st.subheader(table)
    if isinstance(df, pd.DataFrame) and not df.empty:
        st.dataframe(df)
    else:
        st.info(f"Sem dados disponíveis para {table}. Clique em '🔄 Coletar Novos Dados' para tentar novamente.")

# Executar análises avançadas apenas se todos os DataFrames forem válidos
if (st.session_state.dados_carregados and 
    isinstance(df_spotify, pd.DataFrame) and not df_spotify.empty and
    isinstance(df_youtube, pd.DataFrame) and not df_youtube.empty and
    isinstance(df_trends, pd.DataFrame) and not df_trends.empty and
    isinstance(df_x, pd.DataFrame) and not df_x.empty):
    try:
        st.header("📈 Visualizações")
        gerar_visoes(df_spotify, df_youtube, df_trends, df_x)

        st.header("🧠 Análises Avançadas com IA")
        analisar_apriori(df_trends, df_x)
        analisar_clusters(df_spotify, df_youtube)
    except Exception as e:
        st.error(f"Erro ao gerar visualizações ou análises: {str(e)}")
        logger.error(f"Erro ao gerar visualizações ou análises: {str(e)}")
else:
    st.info("Clique em '🔄 Coletar Novos Dados' para iniciar as análises.")
