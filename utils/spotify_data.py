import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import streamlit as st

def coletar_dados_spotify(max_itens=50):
    """
    Coleta dados de músicas populares do Spotify.
    
    Args:
        max_itens (int): Número máximo de itens a serem coletados (padrão: 50).
        
    Returns:
        pd.DataFrame: Dados das músicas com título, artista, popularidade, gênero, álbum, etc.
    """
    try:
        # Usando secrets do Streamlit
        auth_manager = SpotifyClientCredentials(
            client_id=st.secrets["spotify"]["client_id"],
            client_secret=st.secrets["spotify"]["client_secret"]
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Exemplo: buscar músicas populares (usando categorias ou busca direta)
        resultados = []
        offset = 0

        while len(resultados) < max_itens:
            limite = min(50, max_itens - len(resultados))  # Máximo por requisição é 50
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
                    'album': album['name'],
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
