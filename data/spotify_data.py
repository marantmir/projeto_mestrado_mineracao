import pandas as pd
import requests
import streamlit as st
import base64

def autenticar_spotify():
    """
    Autentica com a API do Spotify usando Client Credentials e st.secrets.
    Lança uma exceção detalhada em caso de falha.
    """
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
    except KeyError:
        st.error("As secrets do Spotify (client_id, client_secret) não foram configuradas corretamente no Streamlit Cloud.")
        raise Exception("Secrets do Spotify ausentes. Verifique a configuração em 'Manage app'.")

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, headers=headers, data=data)

    # Tratamento de erro aprimorado
    if response.status_code != 200:
        error_details = response.json()
        st.error(f"Falha na autenticação com o Spotify. Status: {response.status_code}, Detalhes: {error_details}")
        raise Exception(f"Falha na autenticação com o Spotify. Status: {response.status_code}, Detalhes: {error_details}")

    token = response.json()["access_token"]
    return token

def coletar_dados_spotify():
    """
    Coleta dados da playlist Top 50 Global do Spotify.
    Lança uma exceção detalhada em caso de falha.
    """
    token = autenticar_spotify()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Playlist Top 50 Global
    # playlist_id = "37i9dQZEVXbMDoHDwVN2tF"
    playlist_id = "37i9dQZEVXbMXbN3EUUhlg"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

    # --- INÍCIO DA CORREÇÃO ---
    # A API do Spotify exige um parâmetro de mercado para retornar os dados da playlist.
    # Sem ele, a API retorna 404 Not Found.
    params = {
        "market": "BR"
    }
    # Adicionamos o parâmetro 'params' à nossa requisição
    response = requests.get(url, headers=headers, params=params)
    # --- FIM DA CORREÇÃO ---

    # Tratamento de erro aprimorado
    if response.status_code != 200:
        try:
            error_details = response.json()
        except requests.exceptions.JSONDecodeError:
            error_details = response.text
            
        st.error(f"Falha ao buscar dados do Spotify. Status: {response.status_code}, Detalhes: {error_details}")
        raise Exception(f"Falha ao buscar dados do Spotify. Status: {response.status_code}, Detalhes: {error_details}")

    dados = response.json()["tracks"]["items"]

    musicas = []
    for i, item in enumerate(dados):
        if item and item.get("track"):
            track = item["track"]
            # Adicionando uma verificação para o caso de uma música não estar disponível no mercado BR
            if track:
                musicas.append({
                    "posição": len(musicas) + 1, # Usar len() garante a posição correta se houver faixas nulas
                    "artista": track["artists"][0]["name"] if track["artists"] else "N/A",
                    "musica": track["name"],
                    "url": track["external_urls"]["spotify"]
                })

    return pd.DataFrame(musicas)
