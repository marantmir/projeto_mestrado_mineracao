import pandas as pd
import requests

def coletar_dados_youtube():
    # Simulação de chamada real (substitua com sua chave e parâmetros)
    # Exemplo: https://www.googleapis.com/youtube/v3/search
    response = requests.get("https://api.mocki.io/v2/01047e91")  # Exemplo de mock JSON
    if response.status_code == 200:
        dados = response.json()
        return pd.DataFrame(dados)
    else:
        return pd.DataFrame()
