# Conteúdo para o arquivo main.py
import streamlit as st
# Ajuste o caminho do import conforme a sua estrutura de pastas
from data.spotify_data import teste_definitivo_api 

st.title("Diagnóstico da API do Spotify")

try:
    # Em vez de chamar coletar_dados_spotify(), chamamos a função de teste
    teste_definitivo_api()
except Exception as e:
    st.error("O teste encontrou um erro crítico.")
    # st.exception(e) # O erro já é mostrado dentro da função de teste
