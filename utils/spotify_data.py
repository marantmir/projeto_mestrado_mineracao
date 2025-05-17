# Função para coletar dados do Spotify automaticamente

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
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
        offset = 0

        while len(resultados) < max_itens:
            limite = min(10, max_itens - len(resultados))
            dados = sp.new_releases(country='BR', limit=limite, offset=offset)
            albuns = dados.get('albums', {}).get('items', [])

            if not albuns:
                break

            for album in albuns:
                artista = album.get('artists', [{}])[0]
                artista_id = artista.get('id')

                artista_info = {}
                if artista_id:
                    try:
                        artista_info = sp.artist(artista_id)
                    except:
                        artista_info = {}

                resultados.append({
                    'conteudo': album.get('name', 'Nome não disponível'),
                    'artista': artista.get('name', 'Artista desconhecido'),
                    'popularidade': album.get('popularity', 0),
                    'genero': ', '.join(artista_info.get('genres', ['Não informado'])[:3]),
                    'data_lancamento': album.get('release_date', 'Data não disponível'),
                    'fonte': 'Spotify',
                    'link': album.get('external_urls', {}).get('spotify', '#')
                })

            offset += limite

        df = pd.DataFrame(resultados)
        return df

    except Exception as e:
        st.warning(f"🚨 Erro ao coletar dados do Spotify: {e}. Retornando dados simulados.")
        return pd.DataFrame({
            'conteudo': ['Liberdade', 'Sucesso'],
            'artista': ['Anavitória', 'Tiago Iorc'],
            'popularidade': [76, 72],
            'genero': ['pop, brega funk', 'rock, indie'],
            'data_lancamento': ['2024-03-15', '2024-03-10'],
            'fonte': ['Spotify', 'Spotify'],
            'link': ['#', '#']
        })
