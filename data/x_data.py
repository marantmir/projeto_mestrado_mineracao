import pandas as pd
import requests

def coletar_dados_x():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAG6lIQEAAAAA3e7vVMNvDlxYGZs0Ou4XnpvwxOo%3D7PuaRxgFL9YgJJeEjoDtmWSKEt51gV6Acy3RNTnZn1gNEup3iq"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    url = "https://api.twitter.com/1.1/trends/place.json?id=23424768"

    res = requests.get(url, headers=headers)
    trends = res.json()[0]["trends"]

    df = pd.DataFrame(trends)[["name", "tweet_volume"]]
    df.rename(columns={"name": "assunto", "tweet_volume": "volume"}, inplace=True)
    return df
