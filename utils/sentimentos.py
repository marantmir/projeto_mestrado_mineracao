# Simulação da análise de sentimentos

def analisar_sentimentos(df):
    df['sentimento'] = ['positivo' if x > 1000 else 'neutro' for x in df['likes']]
    return df
