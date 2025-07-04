# Conteúdo para o arquivo data/spotify_data.py (temporário para teste)

import requests
import streamlit as st
import base64

def autenticar_spotify():
    """Autentica com a API do Spotify."""
    try:
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
    except KeyError:
        st.error("As secrets do Spotify não foram encontradas. Verifique sua configuração.")
        raise Exception("Secrets do Spotify ausentes.")

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        error_details = response.json()
        st.error(f"Falha na autenticação. Status: {response.status_code}, Detalhes: {error_details}")
        raise Exception(f"Falha na autenticação. Status: {response.status_code}, Detalhes: {error_details}")

    return response.json()["access_token"]

def teste_definitivo_api():
    """
    Realiza o teste mais simples possível: buscar dados de um único artista.
    Isso vai nos dizer se o token tem permissão para LER QUALQUER DADO.
    """
    st.info("Iniciando o teste definitivo da API...")
    token = autenticar_spotify()
    st.success("Token de autenticação obtido com sucesso!")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # ID do artista Daft Punk: 4tZwfgrHOc3mvqYlEYSvVi
    artist_id = "4tZwfgrHOc3mvqYlEYSvVi"
    url = f"https://api.spotify.com/v1/artists/{artist_id}"

    st.write(f"Tentando acessar a URL: {url}")
    
    response = requests.get(url, headers=headers)

    st.write(f"Resposta da API recebida com status: {response.status_code}")

    if response.status_code == 200:
        st.success("TESTE BEM-SUCEDIDO! Acesso à API confirmado.")
        artist_data = response.json()
        st.write("Dados do Artista:")
        st.json(artist_data)
        return artist_data
    else:
        error_details = response.json()
        st.error(f"TESTE FALHOU. O token não pode ler recursos da API. Status: {response.status_code}, Detalhes: {error_details}")
        raise Exception(f"Falha no teste definitivo. Status: {response.status_code}, Detalhes: {error_details}")
