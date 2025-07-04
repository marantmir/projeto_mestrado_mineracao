# data/google_trends.py
from pytrends.request import TrendReq
import pandas as pd

def coletar_dados_trends():
    pytrends = TrendReq(hl='pt-BR', tz=360)
    trending_df = pytrends.trending_searches(pn="brazil")
    trending_df.columns = ["termo"]
    return trending_df
