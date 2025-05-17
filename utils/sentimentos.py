# Simulação da análise de sentimentos

# utils/sentimentos.py

import pandas as pd
import streamlit as st

def analisar_sentimentos(df):
    """
    Analisa sentimentos com base em popularidade (Spotify) ou likes (YouTube).
    """
    def classificar(row):
        if row['fonte'] == 'YouTube':
            likes = row.get('likes', 0)
            if likes > 1000:
                return 'positivo'
            elif likes > 100:
                return 'neutro'
            else:
                return 'negativo'
        else:
            # Para Spotify, usa 'popularidade' (escala 0-100)
            pop = row.get('popularidade', 0)
            if pop > 70:
                return 'positivo'
            elif pop > 40:
                return 'neutro'
            else:
                return 'negativo'

    df['sentimento'] = df.apply(classificar, axis=1)
    return df
