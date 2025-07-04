import streamlit as st
from data.spotify_data import coletar_dados_spotify
from data.youtube_data import coletar_dados_youtube
from data.google_trends import coletar_dados_trends
from data.x_data import coletar_dados_x
from data.db_manager import salvar_df_em_tabela, carregar_tabela
from insights.visualizacoes import gerar_visoes
from insights.aprendizado import analisar_apriori, analisar_clusters

st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
st.title("🎧 Radar Cultural Inteligente")
st.markdown("Análise automatizada de tendências culturais com IA aplicada.")

if "dados_carregados" not in st.session_state:
    st.session_state.dados_carregados = False

if st.button("🔄 Coletar Novos Dados"):
    with st.spinner("Coletando dados de todas as plataformas..."):
        df_spotify = coletar_dados_spotify()
        df_youtube = coletar_dados_youtube()
        df_trends = coletar_dados_trends()
        df_x = coletar_dados_x()

        salvar_df_em_tabela(df_spotify, "spotify")
        salvar_df_em_tabela(df_youtube, "youtube")
        salvar_df_em_tabela(df_trends, "trends")
        salvar_df_em_tabela(df_x, "twitter")

        st.session_state.dados_carregados = True

    st.success("✅ Dados coletados e salvos com sucesso!")

# Carregamento seguro
df_spotify = carregar_tabela("spotify")
df_youtube = carregar_tabela("youtube")
df_trends = carregar_tabela("trends")
df_x = carregar_tabela("twitter")

# Só executa se houver dados
if not df_spotify.empty and not df_youtube.empty and not df_trends.empty and not df_x.empty:
    gerar_visoes(df_spotify, df_youtube, df_trends, df_x)

    st.header("🧠 Análises Avançadas com IA")
    analisar_apriori(df_trends, df_x)
    analisar_clusters(df_spotify, df_youtube)
else:
    st.info("Clique em '🔄 Coletar Novos Dados' para iniciar as análises.")
