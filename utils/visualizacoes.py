# Visualizações dos dados

import plotly.express as px

def gerar_visualizacoes(df, associacoes, temas):
    if not df.empty:
        if 'fonte' in df.columns and 'sentimento' in df.columns:
            fig = px.histogram(df, x='fonte', color='sentimento', barmode='group',
                               title='Sentimentos por Fonte')
            return fig
    return None
