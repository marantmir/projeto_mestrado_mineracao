import streamlit as st
from datetime import datetime

def exibir_layout():
    st.markdown("<style>h1 {color: #1DB954;}</style>", unsafe_allow_html=True)
    st.markdown("<h1>🎧 Radar Cultural Inteligente</h1>", unsafe_allow_html=True)
    st.markdown("Descubra **tendências culturais e sentimentos** com base em dados reais do Spotify e YouTube.")

def exibir_sidebar():
    st.sidebar.header("⚙️ Filtros")
    fonte = st.sidebar.selectbox("Fonte", ["Todos", "Spotify", "YouTube"])
    palavra = st.sidebar.text_input("🔍 Palavra-chave", "")
    data_inicio = st.sidebar.date_input("Data Início", value=datetime(2024, 1, 1))
    data_fim = st.sidebar.date_input("Data Fim")
    regiao = st.sidebar.selectbox("Região", ["Todas", "Brasil", "EUA", "Europa", "Ásia"])
    return {"fonte": fonte, "palavra": palavra, "data_inicio": data_inicio, "data_fim": data_fim, "regiao": regiao}
