# Visualizações dos dados

def gerar_visualizacoes(df, associacoes, temas):
    import streamlit as st
    st.write(df)
    st.write('Associações:', associacoes)
    st.write('Temas:', temas)
