# data/spotify_data.py
import pandas as pd
import requests

def coletar_dados_spotify():
    url = "https://spotifycharts.com/regional/global/daily/latest/download"
    df = pd.read_csv(url, skiprows=1)
    df.columns = ["posição", "artista_musica", "streams", "url"]
    df["artista"] = df["artista_musica"].apply(lambda x: x.split(" - ")[0])
    df["musica"] = df["artista_musica"].apply(lambda x: x.split(" - ")[-1])
    return df[["posição", "artista", "musica", "streams", "url"]]

