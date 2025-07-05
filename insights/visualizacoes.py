import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import logging
import re
from nltk.corpus import stopwords
import nltk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GENEROS_MUSICA = ["rock", "pop", "sertanejo", "rap", "jazz", "eletrônica", "forró", "mpb", "funk", "clássica"]
GENEROS_FILMES_SERIES = ["drama", "comédia", "ação", "suspense", "terror", "romance", "ficção científica", "fantasia", "documentário", "animação"]

try:
    nltk.download('stopwords')
except:
    st.warning("Falha ao baixar recursos do NLTK.")

@st.cache_data
def inferir_generos(df, text_column, fonte):
    try:
        stop_words = set(stopwords.words('portuguese'))
        generos = GENEROS_MUSICA if fonte == "Spotify" else GENEROS_FILMES_SERIES
        
        custom_generos = st.session_state.get(f"custom_{fonte}_generos", [])
        if st.button(f"Adicionar Gêneros Personalizados para {fonte}", key=f"add_{fonte}"):
            new_generos = st.text_input(f"Insira gêneros para {fonte} (separados por vírgula)", key=f"input_{fonte}")
            if new_generos:
                custom_generos.extend([g.strip() for g in new_generos.split(",") if g.strip()])
                st.session_state[f"custom_{fonte}_generos"] = custom_generos
                st.success("Gêneros adicionados!")
        generos.extend(custom_generos)
        
        def detectar_genero(texto):
            texto = texto.lower()
            texto = ' '.join(word for word in texto.split() if word not in stop_words)
            for genero in generos:
                if re.search(rf'\b{genero}\b', texto, re.IGNORECASE):
                    return genero
            return "outro"
        
        df["genero_inferido"] = df[text_column].apply(detectar_genero)
        return df
    except Exception as e:
        logger.error(f"Erro ao inferir gêneros para {fonte}: {str(e)}")
        return df

def gerar_visoes(df_spotify, df_youtube, df_trends, df_x):
    st.subheader("Visualizações de Tendências Culturais")

    def is_valid_df(df, name):
        if not isinstance(df, pd.DataFrame):
            logger.warning(f"{name} não é um DataFrame válido.")
            return False
        if df.empty:
            logger.warning(f"{name} está vazio.")
            return False
        return True

    if is_valid_df(df_spotify, "Spotify"):
        try:
            df_spotify = inferir_generos(df_spotify, "nome", "Spotify")
            st.subheader("🎵 Top Músicas no Spotify por Gênero")
            df_spotify_sorted = df_spotify.sort_values(by="popularidade", ascending=False).head(10)
            fig = px.bar(
                df_spotify_sorted,
                x="nome",
                y="popularidade",
                color="genero_inferido",
                title="Top 10 Músicas por Popularidade e Gênero no Spotify",
                labels={"nome": "Música", "popularidade": "Popularidade"},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_layout(xaxis_title="Música", yaxis_title="Popularidade (0-100)", xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insight**: Gêneros dominantes indicam preferências.")
        except Exception as e:
            st.warning(f"Erro no Spotify: {str(e)}")

    if is_valid_df(df_youtube, "YouTube"):
        try:
            df_youtube = inferir_generos(df_youtube, "titulo", "YouTube")
            st.subheader("📹 Top Vídeos no YouTube por Gênero")
            df_youtube_sorted = df_youtube.sort_values(by="visualizacoes", ascending=False).head(10)
            chart = alt.Chart(df_youtube_sorted).mark_bar().encode(
                x=alt.X("titulo:N", title="Vídeo", sort=None),
                y=alt.Y("visualizacoes:Q", title="Visualizações"),
                color=alt.Color("genero_inferido:N", title="Gênero"),
                tooltip=["titulo", "genero_inferido", "visualizacoes"]
            ).properties(
                title="Top 10 Vídeos por Visualizações e Gênero no YouTube",
                width="container",
                description="Gráfico de barras mostrando os 10 vídeos mais vistos no YouTube por gênero."
            )
            st.altair_chart(chart, use_container_width=True)
            st.markdown("**Insight**: Vídeos de gêneros populares são tendências.")
        except Exception as e:
            st.warning(f"Erro no YouTube: {str(e)}")

    if is_valid_df(df_trends, "Google Trends"):
        try:
            st.subheader("🔍 Termos Populares no Google Trends")
            df_trends_sorted = df_trends.head(10)
            if "termo" in df_trends.columns:
                df_trends = inferir_generos(df_trends, "termo", "Google Trends")
                fig = px.pie(
                    df_trends_sorted,
                    names="genero_inferido",
                    title="Distribuição de Gêneros nos Top 10 Termos do Google Trends",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Insight**: Gêneros populares indicam interesses atuais.")
            else:
                chart = alt.Chart(df_trends_sorted).mark_line().encode(
                    x=alt.X("date:T", title="Data"),
                    y=alt.Y(alt.repeat("column"), type="quantitative"),
                    color=alt.Color(alt.repeat("column"), type="nominal")
                ).repeat(
                    column=[col for col in df_trends.columns if col != "date"][:min(3, len(df_trends.columns) - 1)]
                ).properties(
                    title="Interesse ao Longo do Tempo (Google Trends)",
                    width="container",
                    description="Gráfico de linhas mostrando o interesse ao longo do tempo para termos do Google Trends."
                )
                st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.warning(f"Erro no Google Trends: {str(e)}")

    if is_valid_df(df_x, "X"):
        try:
            df_x = inferir_generos(df_x, "assunto", "X")
            st.subheader("🐦 Assuntos Populares no X por Gênero")
            df_x_sorted = df_x.sort_values(by="volume", ascending=False).head(10)
            fig = px.bar(
                df_x_sorted,
                x="assunto",
                y="volume",
                color="genero_inferido",
                title="Top 10 Assuntos no X por Volume de Impressões e Gênero",
                labels={"assunto": "Assunto", "volume": "Impressões"},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_layout(xaxis_title="Assunto", yaxis_title="Impressões", xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Insight**: Gêneros com alto volume são virais.")
        except Exception as e:
            st.warning(f"Erro no X: {str(e)}")
