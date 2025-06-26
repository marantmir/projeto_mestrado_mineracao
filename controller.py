import streamlit as st
import pandas as pd
from pipeline import coletar_dados, processar_dados
from utils.visualizacoes import gerar_visualizacoes
from utils.estilos import gerar_pdf
from datetime import datetime
import io

def executar_pipeline(filtros):
    df = coletar_dados()
    if df.empty:
        st.warning("⚠️ Nenhum dado disponível.")
        return
    if filtros["fonte"] != "Todos":
        df = df[df["fonte"] == filtros["fonte"]]
    if filtros["palavra"]:
        df = df[df["texto"].str.contains(filtros["palavra"], case=False, na=False)]
    if filtros["data_inicio"] and filtros["data_fim"]:
        df["data"] = pd.to_datetime(df["data"])
        df = df[(df["data"] >= filtros["data_inicio"]) & (df["data"] <= filtros["data_fim"])]
    if filtros["regiao"] != "Todas":
        df = df[df["regiao"] == filtros["regiao"]]
    df, associacoes, temas = processar_dados(df)
    st.subheader("🔍 Tendências Detectadas")
    fig = gerar_visualizacoes(df, associacoes, temas)
    fig.write_image("grafico_tendencias.png")
    col1, col2 = st.columns(2)
    with col1:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
        st.download_button("📥 Baixar Excel", data=excel_buffer.getvalue(), file_name="dados_radar.xlsx", mime="application/vnd.ms-excel")
    with col2:
        pdf = gerar_pdf(df)
        st.download_button("📄 Baixar PDF", data=pdf, file_name="relatorio_radar.pdf", mime="application/pdf")
