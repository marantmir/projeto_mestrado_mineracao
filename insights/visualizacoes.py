import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_visoes(df_spotify, df_youtube, df_trends, df_x):
    """
    Gera visualizações para os dados coletados, adaptando-se a DataFrames vazios.
    """
    st.subheader("Visualizações de Tendências Culturais")

    # Função auxiliar para verificar DataFrame
    def is_valid_df(df, name):
        if not isinstance(df, pd.DataFrame):
            logger.warning(f"{name} não é um DataFrame válido.")
            return False
        if df.empty:
            logger.warning(f"{name} está vazio.")
            return False
        return True

    # 1. Visualização Spotify: Top músicas por popularidade
    if is_valid_df(df_spotify, "Spotify"):
        try:
            st.subheader("🎵 Top Músicas no Spotify (Popularidade)")
            df_spotify_sorted = df_spotify.sort_values(by="popularidade", ascending=False).head(10)
            fig = px.bar(
                df_spotify_sorted,
                x="nome",
                y="popularidade",
                color="artista",
                title="Top 10 Músicas por Popularidade no Spotify",
                labels={"nome": "Música", "popularidade": "Popularidade"},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_layout(xaxis_title="Música", yaxis_title="Popularidade (0-100)", xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insight para produtores**: Músicas com alta popularidade são tendências fortes. Considere criar conteúdo relacionado a esses artistas ou gêneros.")
        except Exception as e:
            st.warning(f"Erro ao gerar visualização do Spotify: {str(e)}")
            logger.error(f"Erro ao gerar visualização do Spotify: {str(e)}")
    else:
        st.info("Nenhum dado do Spotify disponível para visualização.")

    # 2. Visualização YouTube: Top vídeos por visualizações
    if is_valid_df(df_youtube, "YouTube"):
        try:
            st.subheader("📹 Top Vídeos no YouTube (Visualizações)")
            df_youtube_sorted = df_youtube.sort_values(by="visualizacoes", ascending=False).head(10)
            chart = alt.Chart(df_youtube_sorted).mark_bar().encode(
                x=alt.X("titulo:N", title="Vídeo", sort=None),
                y=alt.Y("visualizacoes:Q", title="Visualizações"),
                color=alt.Color("canal:N", title="Canal"),
                tooltip=["titulo", "canal", "visualizacoes"]
            ).properties(
                title="Top 10 Vídeos por Visualizações no YouTube",
                width="container"
            )
            st.altair_chart(chart, use_container_width=True)
            st.markdown("**Insight para produtores**: Vídeos com muitas visualizações indicam temas ou formatos populares. Explore esses tópicos para vídeos ou colaborações.")
        except Exception as e:
            st.warning(f"Erro ao gerar visualização do YouTube: {str(e)}")
            logger.error(f"Erro ao gerar visualização do YouTube: {str(e)}")
    else:
        st.info("Nenhum dado do YouTube disponível para visualização.")

    # 3. Visualização Google Trends: Termos mais pesquisados
    if is_valid_df(df_trends, "Google Trends"):
        try:
            st.subheader("🔍 Termos Populares no Google Trends")
            df_trends_sorted = df_trends.head(10)
            if "termo" in df_trends.columns:
                fig = px.pie(
                    df_trends_sorted,
                    names="termo",
                    title="Top 10 Termos de Pesquisa no Google Trends",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Insight para produtores**: Termos populares no Google Trends refletem o interesse atual do público. Crie conteúdo otimizado para SEO com esses termos.")
            else:
                # Fallback para interest_over_time
                chart = alt.Chart(df_trends_sorted).mark_line().encode(
                    x=alt.X("date:T", title="Data"),
                    y=alt.Y(alt.repeat("column"), type="quantitative"),
                    color=alt.Color(alt.repeat("column"), type="nominal")
                ).repeat(
                    column=df_trends.columns[1:4].tolist()  # Até 3 palavras-chave
                ).properties(
                    title="Interesse ao Longo do Tempo (Google Trends)",
                    width="container"
                )
                st.altair_chart(chart, use_container_width=True)
                st.markdown("**Insight para produtores**: Picos de interesse indicam momentos ideais para publicar conteúdo relacionado a esses temas.")
        except Exception as e:
            st.warning(f"Erro ao gerar visualização do Google Trends: {str(e)}")
            logger.error(f"Erro ao gerar visualização do Google Trends: {str(e)}")
    else:
        st.info("Nenhum dado do Google Trends disponível para visualização.")

    # 4. Visualização X: Assuntos mais discutidos
    if is_valid_df(df_x, "X"):
        try:
            st.subheader("🐦 Assuntos Populares no X")
            df_x_sorted = df_x.sort_values(by="volume", ascending=False).head(10)
            fig = px.bar(
                df_x_sorted,
                x="assunto",
                y="volume",
                title="Top 10 Assuntos no X por Volume de Impressões",
                labels={"assunto": "Assunto", "volume": "Impressões"},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_layout(xaxis_title="Assunto", yaxis_title="Impressões", xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insight para produtores**: Assuntos com alto volume no X são virais. Crie posts ou threads explorando esses temas para engajamento.")
        except Exception as e:
            st.warning(f"Erro ao gerar visualização do X: {str(e)}")
            logger.error(f"Erro ao gerar visualização do X: {str(e)}")
    else:
        st.info("Nenhum dado do X disponível para visualização.")
