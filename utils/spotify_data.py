# utils/spotify_data.py

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

def coletar_dados_spotify(max_itens=50):
    """
    Coleta dados reais do Spotify com base em lançamentos recentes e trata campos ausentes.
    
    Args:
        max_itens (int): Quantidade máxima de músicas a serem coletadas.
        
    Returns:
        pd.DataFrame: DataFrame com informações das músicas coletadas.
    """
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
            albuns = dados.get('albums', {}).get('items', [])

            if not albuns:
                break

            for album in albuns:
                artista = album.get('artists', [{}])[0]
                artista_id = artista.get('id')

                # Pega informações do artista se possível
                artista_info = {}
                if artista_id:
                    try:
                        artista_info = sp.artist(artista_id)
                    except:
                        artista_info = {}

                # Monta os dados do álbum com fallbacks seguros
                resultados.append({
                    'conteudo': album.get('name', 'Nome não disponível'),
                    'artista': artista.get('name', 'Artista desconhecido'),
                    'popularidade': album.get('popularity', None),  # Pode ser None
                    'genero': ', '.join(artista_info.get('genres', ['Não informado'])[:3]),
                    'data_lancamento': album.get('release_date', 'Data não disponível'),
                    'fonte': 'Spotify',
                    'link': album.get('external_urls', {}).get('spotify', '#')
                })

            offset += limite

        df = pd.DataFrame(resultados)
        return df

    except Exception as e:
        st.error(f"Erro ao coletar dados do Spotify: {e}")
        return pd.DataFrame()
