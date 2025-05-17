import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from utils.spotify_data import coletar_dados_spotify
from utils.youtube_data import coletar_dados_youtube
from utils.sentimentos import analisar_sentimentos
from utils.associacoes import gerar_associacoes
from utils.visualizacoes import gerar_visualizacoes
from utils.filtros import aplicar_filtros

st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
st.title("🎧 Radar Cultural Inteligente")
st.markdown("Descubra tendências de temas e sentimentos a partir de dados reais do Spotify e YouTube para criar conteúdos que engajam!")

# Filtros personalizados
st.sidebar.header("🎯 Filtros Personalizados")
pais = st.sidebar.selectbox("País", ["Todos", "Brasil", "EUA", "Reino Unido", "Canadá", "Outros"])
regiao = st.sidebar.selectbox("Região", ["Todas", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
faixa_etaria = st.sidebar.selectbox("Faixa Etária", ["Todas", "13-17", "18-24", "25-34", "35-44", "45+"])
genero = st.sidebar.selectbox("Gênero", ["Todos", "Masculino", "Feminino", "Outros"])

# Coleta de dados
with st.spinner("🔍 Coletando dados do Spotify..."):
    df_spotify = coletar_dados_spotify()
with st.spinner("🔍 Coletando dados do YouTube..."):
    df_youtube = coletar_dados_youtube()

# Adiciona coluna de fonte
df_spotify["fonte"] = "Spotify"
df_youtube["fonte"] = "YouTube"

# Unificação e tratamento de colunas obrigatórias
colunas_simuladas = {
    "pais": "Brasil",
    "regiao": "Sudeste",
    "faixa_etaria": "25-34",
    "genero": "Feminino"
}

for coluna, valor_padrao in colunas_simuladas.items():
    if coluna not in df_spotify.columns:
        df_spotify[coluna] = valor_padrao
    if coluna not in df_youtube.columns:
        df_youtube[coluna] = valor_padrao

# Concatenar dados
df_dados = pd.concat([df_spotify, df_youtube], ignore_index=True)

# Aplicar filtros personalizados
df_dados_filtrado = aplicar_filtros(df_dados, pais, regiao, faixa_etaria, genero)

# Análise de sentimentos
with st.spinner("🧠 Analisando sentimentos..."):
    df_dados_filtrado = analisar_sentimentos(df_dados_filtrado)

# Associações e temas
with st.spinner("🔗 Detectando tendências e associações..."):
    associacoes, temas = gerar_associacoes(df_dados_filtrado)

# Visualizações amigáveis para leigos
st.subheader("📈 Tendências Atuais para Seu Público")
gerar_visualizacoes(df_dados_filtrado, associacoes, temas)

# Gráfico de sentimentos
if "sentimento" in df_dados_filtrado.columns:
    st.markdown("### 💬 Distribuição de Sentimentos nos Conteúdos")
    sentimento_fig = px.histogram(df_dados_filtrado, x="sentimento", color="fonte",
                                  barmode="group", text_auto=True,
                                  labels={"sentimento": "Sentimento Detectado"},
                                  title="Frequência de Sentimentos por Fonte")
    st.plotly_chart(sentimento_fig, use_container_width=True)

# Nuvem de palavras com base nos temas
if temas:
    st.markdown("### ☁️ Nuvem de Palavras dos Temas Mais Frequentes")
    texto_temas = " ".join(temas)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto_temas)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# Linha do tempo de temas (se houver coluna de data)
if "data" in df_dados_filtrado.columns and "tema" in df_dados_filtrado.columns:
    st.markdown("### 📅 Evolução dos Temas ao Longo do Tempo")
    df_dados_filtrado["data"] = pd.to_datetime(df_dados_filtrado["data"])
    tema_tempo = df_dados_filtrado.groupby([pd.Grouper(key="data", freq="W"), "tema"]).size().reset_index(name="frequencia")
    linha_fig = px.line(tema_tempo, x="data", y="frequencia", color="tema",
                        labels={"frequencia": "Frequência", "data": "Data"},
                        title="Tendência de Temas por Semana")
    st.plotly_chart(linha_fig, use_container_width=True)

# Dica final
st.markdown("---")
st.markdown("📌 **Dica:** Use as informações abaixo para criar títulos, descrições e conteúdos alinhados com os sentimentos e temas que mais estão engajando no momento!")
