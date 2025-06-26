import streamlit as st
from controller import executar_pipeline
from ui_components import exibir_layout, exibir_sidebar

st.set_page_config(page_title="Radar Cultural Inteligente", layout="wide")
exibir_layout()
filtros = exibir_sidebar()
executar_pipeline(filtros)
