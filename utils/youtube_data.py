# Função para coletar dados do YouTube automaticamente

from googleapiclient.discovery import build
import pandas as pd
import streamlit as st
import time

@st.cache_data(ttl=3600, show_spinner=False)
def coletar_dados_youtube_cache():
    return coletar_dados_youtube()
    
def coletar_dados_youtube(max_itens=10):
    if "YOUTUBE_API_KEY" not in st.secrets:
        st.error("❌ Chave da API do YouTube não configurada.")
        st.stop()

    try:
        youtube = build("youtube", "v3", developerKey=st.secrets["YOUTUBE_API_KEY"])

        resultados = []
        next_page_token = None
        tentativas = 0

        while len(resultados) < max_itens and tentativas < 2:  # Máximo de 2 páginas
            limite = min(10, max_itens - len(resultados))

            request = youtube.search().list(
                part="snippet",
                q="trending brasil",
                regionCode="BR",
                order="date",
                maxResults=limite,
                pageToken=next_page_token
            )

            try:
                response = request.execute()
            except Exception as e:
                if 'quotaExceeded' in str(e):
                    st.warning("⚠️ Cota da API do YouTube excedida. Usando dados simulados temporariamente.")
                    return pd.DataFrame({
                        'conteudo': ['Treino', 'Motivação'],
                        'descricao': ['', ''],
                        'canal': ['Canal Exemplo', 'Canal Treino'],
                        'tags': ['treino, academia', 'motivação, força'],
                        'data_publicacao': ['2024-01-01T00:00:00Z', '2024-01-02T00:00:00Z'],
                        'popularidade': [75, 80],
                        'likes': [1200, 900],
                        'fonte': ['YouTube', 'YouTube'],
                        'link': ['https://youtu.be/exemplo1 ', 'https://youtu.be/exemplo2 ']
                    })
                else:
                    raise

            for item in response.get("items", []):
                video = item.get("snippet", {})

                data_pub = video.get("publishedAt", "0")
                try:
                    popularidade_valor = int(data_pub.split("T")[0].replace("-", ""))
                except (ValueError, TypeError):
                    popularidade_valor = 0

                likes_str = video.get("likeCount", "0")
                try:
                    likes_valor = int(likes_str)
                except (ValueError, TypeError):
                    likes_valor = 0

                resultados.append({
                    "conteudo": video.get("title", "Título não disponível"),
                    "descricao": video.get("description", ""),
                    "canal": video.get("channelTitle", "Canal desconhecido"),
                    "tags": ", ".join(video.get("tags", ["Sem tags"])[:3]),
                    "data_publicacao": data_pub,
                    "popularidade": popularidade_valor,
                    "likes": likes_valor,
                    "fonte": "YouTube",
                    "link": f"https://youtu.be/ {item['id']['videoId']}"
                })

            next_page_token = response.get("nextPageToken")
            tentativas += 1
            time.sleep(1)  # Evita flood de requisições

        df = pd.DataFrame(resultados)
        return df

    except Exception as e:
        st.warning(f"🚨 Erro ao coletar dados do YouTube: {e}. Retornando dados simulados.")
        return pd.DataFrame({
            'conteudo': ['Treino', 'Motivação'],
            'descricao': ['', ''],
            'canal': ['Canal Exemplo', 'Canal Treino'],
            'tags': ['treino, academia', 'motivação, força'],
            'data_publicacao': ['2024-01-01T00:00:00Z', '2024-01-02T00:00:00Z'],
            'popularidade': [75, 80],
            'likes': [1200, 900],
            'fonte': ['YouTube', 'YouTube'],
            'link': ['https://youtu.be/exemplo1 ', 'https://youtu.be/exemplo2 ']
        })
