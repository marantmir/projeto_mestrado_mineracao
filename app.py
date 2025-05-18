import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud

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

# Coleta de dados
with st.spinner("🔍 Coletando dados do Spotify..."):
    df_spotify = coletar_dados_spotify()
with st.spinner("🔍 Coletando dados do YouTube..."):
    df_youtube = coletar_dados_youtube()

# Adiciona coluna de fonte
df_spotify["fonte"] = "Spotify"
df_youtube["fonte"] = "YouTube"

# Simula colunas ausentes para compatibilidade
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

# Abas para melhor navegação
aba_tendencias, aba_sentimentos, aba_nuvem, aba_mapa = st.tabs([
    "📊 Tendências Gerais", "😊 Sentimentos", "☁️ Nuvem de Palavras", "🗺️ Mapa de Regiões"
])

# Aba de tendências gerais
with aba_tendencias:
    st.subheader("📈 Tendências Atuais para Seu Público")
    gerar_visualizacoes(df_dados_filtrado, associacoes, temas)

    # Exibir tabela de temas e associações de forma visualmente clara
    st.markdown("### 🔍 Temas Mais Comuns")
    df_temas_freq = pd.Series(temas).value_counts().reset_index()
    df_temas_freq.columns = ["Tema", "Frequência"]
    st.dataframe(df_temas_freq.style.background_gradient(cmap="Blues"), use_container_width=True)

# Aba de sentimentos
with aba_sentimentos:
    st.markdown("### 💬 Distribuição de Sentimentos por Fonte e Tema")

    if "sentimento" in df_dados_filtrado.columns and "tema" in df_dados_filtrado.columns:
        fig = px.histogram(
            df_dados_filtrado,
            x="tema",
            color="sentimento",
            facet_col="fonte",
            barmode="group",
            text_auto=True,
            labels={"tema": "Temas", "count": "Quantidade"},
            title="Sentimentos por Tema nas Fontes (Spotify vs YouTube)"
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados insuficientes para análise de sentimento por tema.")

# Aba de nuvem de palavras
with aba_nuvem:
    st.markdown("### ☁️ Nuvem de Palavras dos Temas Mais Frequentes")
    if temas:
        texto_temas = " ".join(temas)
        wordcloud = WordCloud(width=1000, height=600, background_color='white').generate(texto_temas)
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # Botão de download da imagem
        from io import BytesIO
        import base64
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        byte_im = buf.getvalue()
        btn = st.download_button(
            label="📥 Baixar Nuvem de Palavras",
            data=byte_im,
            file_name="nuvem_palavras.png",
            mime="image/png"
        )

# Aba de mapa de calor por região
with aba_mapa:
    st.markdown("### 🌍 Mapa de Calor por Região")
    if "regiao" in df_dados_filtrado.columns:
        df_regiao = df_dados_filtrado.groupby("regiao").size().reset_index(name="frequencia")
        fig = px.bar(df_regiao, x="regiao", y="frequencia", color="frequencia", 
                     title="Frequência de Conteúdo por Região", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados regionais não disponíveis.")

import base64
from io import BytesIO

def gerar_pdf_storytelling(df, titulo="Análise de Tendências"):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, titulo, ln=True)

    pdf.set_font("Arial", '', 12)
    for i, row in df.iterrows():
        texto = f"{row['conteudo']} - {row['artista']} | Gênero: {row['genero']} | Popularidade: {row['popularidade']}"
        pdf.multi_cell(0, 10, texto)

    # Salvar em memória
    buf = BytesIO()
    pdf.output(buf)
    byte_pdf = buf.getvalue()
    return byte_pdf

# Uso no Streamlit
pdf_bytes = gerar_pdf_storytelling(df_dados_filtrado)
st.download_button("📄 Baixar Relatório em PDF", data=pdf_bytes, file_name="analise_tendencias.pdf", mime="application/pdf")


# Dica final
st.markdown("---")
st.markdown("📌 **Dica:** Use essas visões estratégicas para alinhar sua produção com o que está emocionando e conectando com seu público!")
