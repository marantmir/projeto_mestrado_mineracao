import streamlit as st
import pandas as pd

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

# Unificação
df_spotify["fonte"] = "Spotify"
df_youtube["fonte"] = "YouTube"
df_dados = pd.concat([df_spotify, df_youtube], ignore_index=True)

# Aplicar filtros
df_dados_filtrado = aplicar_filtros(df_dados, pais, regiao, faixa_etaria, genero)

# Análise de sentimentos
with st.spinner("🧠 Analisando sentimentos..."):
    df_dados_filtrado = analisar_sentimentos(df_dados_filtrado)

# Apriori e temas
with st.spinner("🔗 Detectando tendências e associações..."):
    associacoes, temas = gerar_associacoes(df_dados_filtrado)

# Visualizações
st.subheader("📈 Tendências Atuais para Seu Público")
gerar_visualizacoes(df_dados_filtrado, associacoes, temas)

st.markdown("---")
st.markdown("📌 **Dica:** Use as informações abaixo para criar títulos, descrições e conteúdos alinhados com os sentimentos e temas que mais estão engajando no momento!")
