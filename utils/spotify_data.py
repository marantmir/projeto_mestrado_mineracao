import pandas as pd
import requests

def coletar_dados_spotify():
    # Simulação de coleta real (substitua com lógica de autenticação e chamada real)
    # Exemplo: https://api.spotify.com/v1/search?q=top&type=track
    response = requests.get("https://api.mocki.io/v2/79fb05cb")  # Exemplo de mock JSON
    if response.status_code == 200:
        dados = response.json()
        return pd.DataFrame(dados)
    else:
        return pd.DataFrame()
