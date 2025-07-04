import pandas as pd
import requests
from bs4 import BeautifulSoup

def coletar_dados_spotify():
    url = "https://spotifycharts.com/regional/global/daily/latest"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"class": "chart-table"})
    linhas = table.find_all("tr")[1:]  # ignora header

    dados = []
    for linha in linhas:
        pos = linha.find("td", {"class": "chart-table-position"}).text.strip()
        nome = linha.find("strong").text.strip()
        artista = linha.find("span").text.strip().replace("by ", "")
        streams = linha.find("td", {"class": "chart-table-streams"}).text.strip().replace(",", "")
        link = linha.find("a")["href"]

        dados.append({
            "posição": int(pos),
            "artista": artista,
            "musica": nome,
            "streams": int(streams),
            "url": link
        })

    return pd.DataFrame(dados)
