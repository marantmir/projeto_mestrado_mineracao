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
    from data.supabase_manager import salvar_df_supabase, carregar_df_supabase
    from insights.visualizacoes import gerar_visoes
    from insights.aprendizado import analisar_apriori, analisar_clusters
except ImportError as e:
    st.error(f"Erro ao importar módulos: {str(e)}. Verifique os diretórios 'data/' e 'insights/'.")
    if st.button("Mostrar Logs"):
        st.text(logger.handlers[0].stream.getvalue())
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
                    salvar_df_supabase(df, name)
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
            "spotify": carregar_df_supabase("spotify", ["nome", "artista", "popularidade"]),
            "youtube": carregar_df_supabase("youtube", ["titulo", "canal", "visualizacoes"]),
            "trends": carregar_df_supabase("trends", ["termo"]),
            "twitter": carregar_df_supabase("twitter", ["assunto", "volume", "created_at"])
        }
    except Exception as e:
        st.error(f"Erro ao carregar tabelas: {str(e)}")
        logger.error(f"Erro ao carregar tabelas: {str(e)}")
        return {"spotify": pd.DataFrame(), "youtube": pd.DataFrame(), "trends": pd.DataFrame(), "twitter": pd.DataFrame()}

tabelas = carregar_tabelas()
df_spotify, df_youtube, df_trends, df_x = tabelas["spotify"], tabelas["youtube"], tabelas["trends"], tabelas["twitter"]

def validar_dados(df, fonte, colunas_esperadas):
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning(f"Dados de {fonte} estão vazios ou inválidos")
        return False
    if not all(col in df.columns for col in colunas_esperadas):
        logger.warning(f"Faltam colunas em {fonte}: {colunas_esperadas}")
        return False
    return True

if not (validar_dados(df_spotify, "Spotify", ["nome", "artista", "popularidade"]) or
        validar_dados(df_youtube, "YouTube", ["titulo", "canal", "visualizacoes"]) or
        validar_dados(df_trends, "Google Trends", ["termo"]) or
        validar_dados(df_x, "X", ["assunto", "volume", "created_at"])):
    st.warning("Dados carregados podem estar incompletos. Verifique a coleta.")

st.header("📊 Dados Coletados")
for table, df in [("Spotify", df_spotify), ("YouTube", df_youtube), ("Google Trends", df_trends), ("X", df_x)]:
    st.subheader(table)
    if isinstance(df, pd.DataFrame) and not df.empty:
        st.dataframe(df.head(10))  # Mostrar apenas 10 linhas para legibilidade
    else:
        st.info(f"Sem dados para {table}. Clique em '🔄 Coletar Novos Dados'.")

if st.session_state.dados_carregados:
    try:
        st.header("📈 Visualizações e Insights")
        if validar_dados(df_spotify, "Spotify", ["nome", "artista", "popularidade"]) or \
           validar_dados(df_youtube, "YouTube", ["titulo", "canal", "visualizacoes"]) or \
           validar_dados(df_trends, "Google Trends", ["termo"]) or \
           validar_dados(df_x, "X", ["assunto", "volume", "created_at"]):
            gerar_visoes(df_spotify, df_youtube, df_trends, df_x)
        else:
            st.warning("Sem dados válidos para gerar visualizações.")

        if validar_dados(df_trends, "Google Trends", ["termo"]) and validar_dados(df_x, "X", ["assunto", "volume", "created_at"]):
            st.subheader("🧠 Análise de Regras de Associação (Apriori)")
            analisar_apriori(df_trends, df_x)
        else:
            st.warning("Sem dados suficientes para análise Apriori.")

        if validar_dados(df_spotify, "Spotify", ["nome", "artista", "popularidade"]) and \
           validar_dados(df_youtube, "YouTube", ["titulo", "canal", "visualizacoes"]):
            st.subheader("🧠 Análise de Clusters")
            analisar_clusters(df_spotify, df_youtube)
        else:
            st.warning("Sem dados suficientes para análise de clusters.")
    except Exception as e:
        st.error(f"Erro em visualizações/análises: {str(e)}. Verifique logs.")
        if st.button("Mostrar Logs"):
            st.text(logger.handlers[0].stream.getvalue())

    # Pesquisa Operacional para Recomendação de Conteúdo
    st.header("🤖 Recomendações para Produção de Conteúdo")
    if not df_spotify.empty and not df_youtube.empty and not df_trends.empty and not df_x.empty:
        # Normalizar popularidade (0-100) e volume (ponderar por tendência)
        df_spotify['score'] = df_spotify['popularidade']
        df_youtube['score'] = df_youtube['visualizacoes'] / 1000  # Aproximar escala
        df_trends_weight = df_trends['termo'].value_counts().head(10).to_dict()
        df_x_weight = df_x['assunto'].value_counts().head(10).to_dict()

        # Combinar scores com pesos de tendências
        recommendations = {}
        for idx, row in df_spotify.iterrows():
            termo = row['nome']
            score = row['score'] * 0.5  # Peso para popularidade
            if termo in df_trends_weight:
                score += df_trends_weight[termo] * 0.3  # Peso para tendências
            if termo in df_x_weight:
                score += df_x_weight[termo] * 0.2  # Peso para volume no X
            recommendations[termo] = score

        for idx, row in df_youtube.iterrows():
            termo = row['titulo']
            score = row['score'] * 0.5
            if termo in df_trends_weight:
                score += df_trends_weight[termo] * 0.3
            if termo in df_x_weight:
                score += df_x_weight[termo] * 0.2
            recommendations[termo] = score

        # Ordenar e exibir top 5 recomendações
        top_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:5]
        st.subheader("Top 5 Conteúdos Sugeridos")
        for conteudo, score in top_recommendations:
            st.write(f"- {conteudo} (Pontuação: {score:.2f})")
    else:
        st.warning("Sem dados suficientes para recomendar conteúdo.")
else:
    st.info("Clique em '🔄 Coletar Novos Dados' para iniciar.")
