# Função para coletar dados do YouTube automaticamente

from googleapiclient.discovery import build
import pandas as pd
import streamlit as st

def coletar_dados_youtube(max_itens=50):
    if "YOUTUBE_API_KEY" not in st.secrets:
        st.error("❌ Chave da API do YouTube não configurada.")
        st.stop()

    try:
        youtube = build("youtube", "v3", developerKey=st.secrets["YOUTUBE_API_KEY"])

        resultados = []
        next_page_token = None

        while len(resultados) < max_itens:
            limite = min(50, max_itens - len(resultados))

            request = youtube.search().list(
                part="snippet",
                q="trending brasil",
                regionCode="BR",
                order="date",
                maxResults=limite,
                pageToken=next_page_token
            )

            response = request.execute()

            for item in response.get("items", []):
                video = item.get("snippet", {})

                # Ajuste processando data_publicacao e convertendo para popularidade
                data_pub = video.get("publishedAt", "0")
                try:
                    popularidade_valor = int(data_pub.split("T")[0].replace("-", ""))
                except (ValueError, TypeError):
                    popularidade_valor = 0
                    resultados.append({
                    "conteudo": video.get("title", "Título não disponível"),
                    "descricao": video.get("description", ""),
                    "canal": video.get("channelTitle", "Canal desconhecido"),
                    "tags": ", ".join(video.get("tags", ["Sem tags"])[:3]),
                    "data_publicacao": data_pub,
                    "popularidade": popularidade_valor,  # Usa o valor calculado acima
                    "likes": int(video.get("likeCount", 0)),
                    "fonte": "YouTube",
                    "link": f"https://youtu.be/ {item['id']['videoId']}"
                })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        df = pd.DataFrame(resultados)
        return df

    except Exception as e:
        st.error(f"🚨 Erro ao coletar dados do YouTube: {e}")
        return pd.DataFrame()
