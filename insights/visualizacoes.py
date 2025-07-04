import streamlit as st
import plotly.express as px
import pandas as pd

def gerar_visoes(df_spotify, df_youtube, df_trends, df_x):
    st.header("🎯 Visões por Plataforma")

    # Spotify
    with st.expander("🎧 Spotify"):
        st.subheader("Top músicas e artistas")
        fig1 = px.bar(df_spotify.head(15), x="musica", y="streams", color="artista", title="Top 15 músicas mais ouvidas")
        st.plotly_chart(fig1)

    # YouTube
    with st.expander("📺 YouTube"):
        st.subheader("Vídeos em alta no Brasil")
        df_youtube["views"] = pd.to_numeric(df_youtube["views"])
        fig2 = px.bar(df_youtube.sort_values("views", ascending=False).head(15), x="titulo", y="views", color="canal", title="Top vídeos")
        st.plotly_chart(fig2)

    # Google Trends
    with st.expander("📊 Google Trends"):
        st.subheader("Principais termos pesquisados")
        st.table(df_trends.head(20))

    # Twitter (X)
    with st.expander("🐦 Twitter (X)"):
        st.subheader("Tópicos em alta no Brasil")
        df_x = df_x.dropna(subset=["volume"])
        df_x["volume"] = pd.to_numeric(df_x["volume"])
        fig3 = px.bar(df_x.sort_values("volume", ascending=False).head(15), x="assunto", y="volume", title="Trending Topics")
        st.plotly_chart(fig3)

    # Visões Combinadas
    st.header("🤖 Visões Integradas e Inferências")

    # Unificação de termos de interesse
    termos_spotify = set(df_spotify["musica"].str.lower().unique())
    termos_youtube = set(df_youtube["titulo"].str.lower().unique())
    termos_trends = set(df_trends["termo"].str.lower().unique())
    termos_twitter = set(df_x["assunto"].str.lower().unique())

    # Interseções
    intersec_spotify_youtube = termos_spotify.intersection(termos_youtube)
    intersec_yt_twitter = termos_youtube.intersection(termos_twitter)
    intersec_all = termos_spotify & termos_youtube & termos_trends & termos_twitter

    # Exibe insights
    if intersec_spotify_youtube:
        st.markdown("🔗 **Músicas/Vídeos populares nas duas plataformas:**")
        st.write(list(intersec_spotify_youtube))

    if intersec_yt_twitter:
        st.markdown("🔥 **Temas de vídeos que também estão em alta no Twitter:**")
        st.write(list(intersec_yt_twitter))

    if intersec_all:
        st.markdown("🚀 **Conteúdos em tendência em todas as plataformas:**")
        st.write(list(intersec_all))

    # Inferência automática simples
    st.subheader("🧠 Recomendações baseadas nos dados")
    if len(intersec_all) > 0:
        st.success(f"🚨 Os conteúdos '{', '.join(list(intersec_all)[:3])}' estão em alta em todas as plataformas! Aposte neles.")
    elif len(intersec_spotify_youtube) > 0:
        st.info(f"🎵 Os conteúdos musicais '{', '.join(list(intersec_spotify_youtube)[:3])}' estão gerando alto engajamento cross-plataforma.")
    else:
        st.warning("Nenhum termo comum identificado entre todas as plataformas. Acompanhe individualmente para insights emergentes.")
