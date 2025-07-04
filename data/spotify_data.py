import pandas as pd
import requests
import streamlit as st
import base64
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    if response.status_code != 200:
        error_details = response.json()
        st.error(f"Falha na autenticação com o Spotify. Status: {response.status_code}, Detalhes: {error_details}")
        raise Exception(f"Falha na autenticação com o Spotify. Status: {response.status_code}, Detalhes: {error_details}")

    token = response.json()["access_token"]
    return token

def coletar_dados_spotify():
    """
    Coleta todas as músicas de uma playlist do Spotify, lidando com paginação.
    Tenta múltiplas playlists como fallback em caso de falha.
    """
    token = autenticar_spotify()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Lista de playlists para tentar
    playlists = [
        {"id": "37i9dQZEVXbMDoHDwVN2tF", "nome": "Top 50 Global", "market": "BR"},
        {"id": "37i9dQZF1DX0FOF1IUWK1W", "nome": "Top Brasil", "market": "BR"},
        {"id": "37i9dQZEVXbMDoHDwVN2tF", "nome": "Top 50 Global (sem market)", "market": None}
    ]

    for playlist in playlists:
        playlist_id = playlist["id"]
        playlist_nome = playlist["nome"]
        market = playlist["market"]

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {"market": market} if market else {}
        musicas = []

        # Log e exibir URL inicial da requisição
        logger.info(f"Tentando coletar dados da playlist: {playlist_nome} (ID: {playlist_id}, Market: {market})")
        st.write(f"URL inicial da requisição: {url}{'?market=' + market if market else ''}")

        while url:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                dados = response.json()
                items = dados.get("items", [])
                
                for item in items:
                    if item and item.get("track"):
                        track = item["track"]
                        if track:
                            musicas.append({
                                "posição": len(musicas) + 1,
                                "artista": track["artists"][0]["name"] if track["artists"] else "N/A",
                                "musica": track["name"],
                                "url": track["external_urls"]["spotify"]
                            })

                # Verificar se há mais páginas
                url = dados.get("next")
                if url:
                    params = {}  # Limpar params para usar o URL de next diretamente
                    logger.info(f"Buscando próxima página: {url}")
                    st.write(f"Buscando próxima página: {url}")
                continue

            try:
                error_details = response.json()
            except requests.exceptions.JSONDecodeError:
                error_details = response.text

            st.error(
                f"Falha ao buscar dados da playlist {playlist_nome} (ID: {playlist_id}). "
                f"Status: {response.status_code}, Detalhes: {error_details}"
            )
            logger.error(f"Falha na playlist {playlist_nome}: Status {response.status_code}, Detalhes: {error_details}")
            break  # Sair do loop de paginação e tentar a próxima playlist

        if musicas:
            st.success(f"Dados coletados com sucesso da playlist: {playlist_nome} ({len(musicas)} músicas)")
            return pd.DataFrame(musicas)

    st.error(
        "Não foi possível coletar dados de nenhuma playlist. Verifique os IDs das playlists no Spotify "
        "ou tente com uma conta brasileira. Alternativamente, contate o suporte do Spotify para desenvolvedores."
    )
    raise Exception("Falha ao coletar dados de todas as playlists tentadas.")
