# Simulação da análise de sentimentos

import pandas as pd

def analisar_sentimentos(df):
    """
    Analisa sentimentos com base em popularidade (Spotify) ou likes (YouTube).
    Garante que os valores sejam numéricos antes da comparação.
    """

    def classificar(row):
        if row['fonte'] == 'YouTube':
            likes = row.get('likes', 0)
            try:
                likes = int(likes)
            except (ValueError, TypeError):
                likes = 0
            if likes > 1000:
                return 'positivo'
            elif likes > 100:
                return 'neutro'
            else:
                return 'negativo'
        else:
            # Spotify
            pop = row.get('popularidade', 0)
            try:
                pop = int(pop)
            except (ValueError, TypeError):
                pop = 0
            if pop > 70:
                return 'positivo'
            elif pop > 40:
                return 'neutro'
            else:
                return 'negativo'

    df['sentimento'] = df.apply(classificar, axis=1)
    return df
