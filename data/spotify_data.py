import pandas as pd
import requests
import streamlit as st
import base64
import logging
import time

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

def coletar_dados_spotify(max_retries=3, retry_delay=2, max_tracks=1000):
    """
    Coleta todas as músicas possíveis do Spotify usando busca com paginação.
    Usa múltiplas queries para maximizar o número de faixas coletadas.
    """
    token = autenticar_spotify()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Lista de queries para buscar músicas (ex.: por gênero e ano atual)
    queries = [
        {"query": "year:2025", "nome": "Músicas de 2025", "market": "BR"},
        {"query": "genre:pop", "nome": "Músicas Pop", "market": "BR"},
        {"query": "genre:rock", "nome": "Músicas Rock", "market": "BR"},
        {"query": "*", "nome": "Todas as Músicas (sem filtro)", "market": None}
    ]

    musicas = []
    max_offset = 1000  # Limite máximo de offset da API do Spotify
    limit = 50  # Máximo de faixas por requisição

    for query_info in queries:
        query = query_info["query"]
        query_nome = query_info["nome"]
        market = query_info["market"]

        logger.info(f"Tentando coletar músicas com query: {query_nome} (Query: {query}, Market: {market})")
        st.write(f"Coletando músicas com query: {query_nome} (Market: {market})")

        offset = 0
        while offset < max_offset and len(musicas) < max_tracks:
            params = {
                "q": query,
                "type": "track",
                "limit": limit,
                "offset": offset
            }
            if market:
                params["market"] = market

            url = "https://api.spotify.com/v1/search"
            st.write(f"URL da requisição: {url}?q={query}&type=track&limit={limit}&offset={offset}{'&market=' + market if market else ''}")

            for attempt in range(max_retries):
                response = requests.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    dados = response.json()
                    items = dados.get("tracks", {}).get("items", [])

                    for item in items:
                        if item and len(musicas) < max_tracks:
                            musicas.append({
                                "posição": len(musicas) + 1,
                                "artista": item["artists"][0]["name"] if item["artists"] else "N/A",
                                "musica": item["name"],
                                "url": item["external_urls"]["spotify"]
                            })

                    total_results = dados.get("tracks", {}).get("total", 0)
                    offset += limit
                    if offset >= total_results or offset >= max_offset:
                        break
                    break  # Sucesso, sair do loop de retentativas

                try:
                    error_details = response.json()
                except requests.exceptions.JSONDecodeError:
                    error_details = response.text

                st.error(
                    f"Tentativa {attempt + 1}/{max_retries} falhou para query {query_nome}. "
                    f"Status: {response.status_code}, Detalhes: {error_details}"
                )
                logger.error(f"Tentativa {attempt + 1}/{max_retries} falhou para query {query_nome}: Status {response.status_code}, Detalhes: {error_details}")

                if attempt < max_retries - 1:
                    st.write(f"Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    time.sleep(retry_delay)
                else:
                    st.error(f"Não foi possível coletar dados para query {query_nome} após {max_retries} tentativas.")
                    break

            if len(musicas) >= max_tracks:
                break

        if musicas:
            st.success(f"Dados coletados com sucesso: {len(musicas)} músicas usando query {query_nome}")
            return pd.DataFrame(musicas)

    if musicas:
        st.success(f"Dados coletados com sucesso: {len(musicas)} músicas")
        return pd.DataFrame(musicas)

    st.error(
        "Não foi possível coletar músicas com nenhuma query. Verifique as credenciais do Spotify, "
        "a conectividade com a API, ou contate o suporte do Spotify para desenvolvedores."
    )
    raise Exception("Falha ao coletar músicas com todas as queries tentadas.")
