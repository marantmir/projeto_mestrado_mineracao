import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

def coletar_dados_spotify(max_itens=50):
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
            limite = min(50, max_itens - len(resultados))
            dados = sp.new_releases(country='BR', limit=limite, offset=offset)
            albuns = dados['albums']['items']

            if not albuns:
                break

            for album in albuns:
                artista = album['artists'][0]
                artista_info = sp.artist(artista['id'])

                resultados.append({
                    'conteudo': album['name'],
                    'artista': artista['name'],
                    'popularidade': album['popularity'],
                    'genero': ', '.join(artista_info.get('genres', ['Não informado'])[:3]),
                    'data_lancamento': album['release_date'],
                    'fonte': 'Spotify',
                    'link': album['external_urls']['spotify']
                })

            offset += limite

        df = pd.DataFrame(resultados)
        return df

    except Exception as e:
        st.error(f"Erro ao coletar dados do Spotify: {e}")
        return pd.DataFrame()
