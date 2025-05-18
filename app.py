import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import BytesIO

from utils.spotify_data import coletar_dados_spotify
from utils.youtube_data import coletar_dados_youtube
from utils.sentimentos import analisar_sentimentos
from utils.associacoes import gerar_associacoes
from utils.visualizacoes import gerar_visualizacoes
from utils.filtros import aplicar_filtros

# Configuração inicial da página
st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
st.title("🎧 Radar Cultural Inteligente")
st.markdown("Descubra tendências de temas e sentimentos a partir de dados reais do Spotify e YouTube para criar conteúdos que engajam!")

# Filtros personalizados
with st.sidebar:
    st.header("🎯 Filtros Personalizados")
    pais = st.selectbox("País", ["Todos", "Brasil", "EUA", "Reino Unido", "Canadá", "Outros"])
    regiao = st.selectbox("Região", ["Todas", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
    faixa_etaria = st.selectbox("Faixa Etária", ["Todas", "13-17", "18-24", "25-34", "35-44", "45+"])
    genero = st.selectbox("Gênero", ["Todos", "Masculino", "Feminino", "Outros"])
    modo_rapido = st.checkbox("⚡ Modo Leve (sem análises pesadas)")

# Botão para atualizar dados
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=3600)
def coletar_dados_spotify_cache():
    return coletar_dados_spotify()

@st.cache_data(ttl=3600)
def coletar_dados_youtube_cache():
    return coletar_dados_youtube()

@st.cache_data(ttl=3600)
def processar_sentimentos(df):
    return analisar_sentimentos(df)

@st.cache_data(ttl=3600)
def processar_associacoes(df):
    return gerar_associacoes(df)

# Coleta de dados
with st.spinner("🔍 Coletando dados do Spotify..."):
    df_spotify = coletar_dados_spotify_cache()
with st.spinner("🔍 Coletando dados do YouTube..."):
    df_youtube = coletar_dados_youtube_cache()

# Adiciona coluna de fonte
df_spotify["fonte"] = "Spotify"
df_youtube["fonte"] = "YouTube"

# Simula colunas ausentes
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

# Modo leve usa apenas parte dos dados
if modo_rapido:
    df_dados_filtrado = df_dados_filtrado.sample(min(100, len(df_dados_filtrado)))

# Análise de sentimentos e associações
if not modo_rapido:
    with st.spinner("🧠 Analisando sentimentos..."):
        df_dados_filtrado = processar_sentimentos(df_dados_filtrado)
    with st.spinner("🔗 Detectando tendências e associações..."):
        associacoes, temas = processar_associacoes(df_dados_filtrado)
else:
    associacoes, temas = [], []

# Abas para melhor navegação
aba_tendencias, aba_sentimentos, aba_nuvem, aba_mapa = st.tabs([
    "📊 Tendências Gerais", "😊 Sentimentos", "☁️ Nuvem de Palavras", "🗺️ Mapa de Regiões"
])

with aba_tendencias:
    st.subheader("📈 Tendências Atuais para Seu Público")
    if not modo_rapido and not df_dados_filtrado.empty:
        gerar_visualizacoes(df_dados_filtrado, associacoes, temas)
        st.markdown("### 🔍 Temas Mais Comuns")
        df_temas_freq = pd.Series(temas).value_counts().reset_index()
        df_temas_freq.columns = ["Tema", "Frequência"]
        st.dataframe(df_temas_freq.style.background_gradient(cmap="Blues"), use_container_width=True)

    # Geração de insights automáticos por tema e sentimento
if not modo_rapido and "sentimento" in df_dados_filtrado.columns and "tema" in df_dados_filtrado.columns:

    st.markdown("### 🤖 Insights Estratégicos Automáticos")

    temas_unicos = df_dados_filtrado["tema"].dropna().unique()

    insights = []

    for tema in temas_unicos:
        dados_tema = df_dados_filtrado[df_dados_filtrado["tema"] == tema]
        if not dados_tema.empty:
            resumo = dados_tema.groupby(["fonte", "sentimento"]).size().reset_index(name="quantidade")
            frases = []
            for _, row in resumo.iterrows():
                fonte = row["fonte"]
                sentimento = row["sentimento"]
                qtd = row["quantidade"]
                frases.append(f"{qtd} conteúdo(s) com sentimento **{sentimento}** no **{fonte}**")
            insight = f"🔎 O tema **{tema}** apresenta: " + ", ".join(frases) + "."
            insights.append(insight)

    for frase in insights:
        st.markdown(frase)

    else:
        st.info("Ative o modo completo para ver tendências detalhadas.")

with aba_sentimentos:
    st.markdown("### 💬 Distribuição de Sentimentos por Fonte e Tema")
    if not modo_rapido and "sentimento" in df_dados_filtrado.columns and "tema" in df_dados_filtrado.columns:
        fig = px.histogram(
            df_dados_filtrado,
            x="tema",
            color="sentimento",
            facet_col="fonte",
            barmode="group",
            labels={"tema": "Temas", "count": "Quantidade"},
            title="Sentimentos por Tema nas Fontes (Spotify vs YouTube)"
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados insuficientes para análise de sentimento por tema ou modo leve ativado.")

with aba_nuvem:
    st.markdown("### ☁️ Nuvem de Palavras dos Temas Mais Frequentes")
    if not modo_rapido and temas:
        texto_temas = " ".join(temas)
        wordcloud = WordCloud(width=1000, height=600, background_color='white').generate(texto_temas)
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        st.download_button("📥 Baixar Nuvem de Palavras", data=buf.getvalue(), file_name="nuvem_palavras.png", mime="image/png")
    else:
        st.info("Nuvem de palavras disponível apenas no modo completo com dados suficientes.")

with aba_mapa:
    st.markdown("### 🌍 Mapa de Calor por Região")
    if "regiao" in df_dados_filtrado.columns and not df_dados_filtrado.empty:
        df_regiao = df_dados_filtrado.groupby("regiao").size().reset_index(name="frequencia")
        fig = px.bar(df_regiao, x="regiao", y="frequencia", color="frequencia", 
                     title="Frequência de Conteúdo por Região", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados regionais não disponíveis ou modo leve ativado.")

st.markdown("---")
st.markdown("📌 **Dica:** Use essas visões estratégicas para alinhar sua produção com o que está emocionando e conectando com seu público!")
