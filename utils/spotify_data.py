# Função para coletar dados do Spotify automaticamente

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def coletar_dados_spotify_cache():
    return coletar_dados_spotify()

# Coleta com cache
with st.spinner("🔍 Carregando dados do Spotify..."):
    df_spotify = coletar_dados_spotify_cache()

def coletar_dados_spotify(max_itens=10):
    if "SPOTIFY_CLIENT_ID" not in st.secrets or "SPOTIFY_CLIENT_SECRET" not in st.secrets:
        st.error("Credenciais do Spotify não configuradas.")
        st.stop()

    try:
        auth_manager = SpotifyClientCredentials(
            client_id=st.secrets["SPOTIFY_CLIENT_ID"],
            client_secret=st.secrets["SPOTIFY_CLIENT_SECRET"]
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        resultados = []
        dados = sp.new_releases(country='BR', limit=max_itens, offset=0)
        albuns = dados.get('albums', {}).get('items', [])

        for album in albuns:
            artista = album.get('artists', [{}])[0]
            resultados.append({
                'conteudo': album.get('name', 'Nome não disponível'),
                'artista': artista.get('name', 'Artista desconhecido'),
                'popularidade': album.get('popularity', 0),
                'genero': 'Não informado',  # evitamos chamada ao sp.artist
                'data_lancamento': album.get('release_date', 'Data não disponível'),
                'fonte': 'Spotify',
                'link': album.get('external_urls', {}).get('spotify', '#')
            })

        df = pd.DataFrame(resultados)
        return df

    except Exception as e:
        st.warning(f"🚨 Erro ao coletar dados do Spotify: {e}. Retornando dados simulados.")
        return pd.DataFrame({
            'conteudo': ['Liberdade', 'Sucesso'],
            'artista': ['Anavitória', 'Tiago Iorc'],
            'popularidade': [76, 72],
            'genero': ['pop', 'indie'],
            'data_lancamento': ['2024-03-15', '2024-03-10'],
            'fonte': ['Spotify', 'Spotify'],
            'link': ['#', '#']
        })
