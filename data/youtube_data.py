# data/youtube_data.py
import pandas as pd
from googleapiclient.discovery import build

def coletar_dados_youtube():
    api_key = "AIzaSyC5gbX6ovFO3N5WDhJZH8mTYVYFAjhGn_0"
    youtube = build("youtube", "v3", developerKey=api_key)

    req = youtube.videos().list(part="snippet,statistics", chart="mostPopular", regionCode="BR", maxResults=50)
    res = req.execute()

    videos = [{
        "titulo": item["snippet"]["title"],
        "canal": item["snippet"]["channelTitle"],
        "views": item["statistics"].get("viewCount", 0),
        "categoria": item["snippet"].get("categoryId", "N/A"),
        "likes": item["statistics"].get("likeCount", 0)
    } for item in res["items"]]

    return pd.DataFrame(videos)
