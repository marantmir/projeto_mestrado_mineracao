# Simulação da aplicação do algoritmo Apriori

from collections import Counter

def gerar_associacoes(df):
    temas = []
    for texto in df['conteudo']:
        if isinstance(texto, str):
            temas.extend([palavra.lower() for palavra in texto.split() if len(palavra) > 3])
    associacoes = Counter(temas).most_common(20)
    return associacoes, temas
