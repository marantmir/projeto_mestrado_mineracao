import pandas as pd
import requests
import streamlit as st
import base64

def autenticar_spotify():
    client_id = st.secrets["spotify"]["client_id"]
    client_secret = st.secrets["spotify"]["client_secret"]

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}"
    }
    data = {
        "grant_type": "client_credentials"
    }

    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception("Falha na autenticação com o Spotify")

    token = response.json()["access_token"]
    return token

def coletar_dados_spotify():
    token = autenticar_spotify()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Playlist Top 50 Global
    url = "https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Falha ao buscar dados do Spotify")

    dados = response.json()["tracks"]["items"]

    musicas = []
    for item in dados:
        track = item["track"]
        musicas.append({
            "posição": len(musicas) + 1,
            "artista": track["artists"][0]["name"],
            "musica": track["name"],
            "streams": 0,  # A API não fornece este dado diretamente
            "url": track["external_urls"]["spotify"]
        })

    return pd.DataFrame(musicas)
