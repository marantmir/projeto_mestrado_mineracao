# projeto_mestrado_mineracao

# 📊 YouTube + Spotify Trends Dashboard

Bem-vindo à aplicação **YouTube + Spotify Trends**, um painel interativo construído com [Streamlit](https://streamlit.io/) para:

- 🔍 Coletar **comentários do YouTube** com análise de sentimentos.
- 📈 Identificar **palavras-chave em alta** via Google Trends.
- 🎶 Buscar as **músicas mais populares** de qualquer artista no Spotify.
- ☁️ Gerar nuvem de palavras, dashboards interativos e filtros customizáveis.
- ☁️ Armazenar e recuperar dados via **Firebase Firestore**.

---

## 🚀 Demonstração

Acesse o app publicado (exemplo):

👉 [https://seu-usuario.streamlit.app](https://seu-usuario.streamlit.app)

---

## 🧠 Funcionalidades

### 🎥 YouTube

- Conecta com a **API oficial do YouTube**.
- Analisa os **comentários dos vídeos mais populares** por palavra-chave.
- Gera **análise de sentimentos** usando TextBlob.
- Visualiza:
  - Métricas e KPIs
  - Distribuição de sentimentos
  - Nuvem de palavras
  - Tabela interativa de comentários

### 🔍 Google Trends

- Integra com **pytrends** para identificar palavras-chave em alta por região.
- Permite análise contínua com termos atualizados automaticamente.

### 🎧 Spotify

- Busca por artista.
- Exibe suas **5 músicas mais populares** no Brasil.
- Mostra nome, álbum, data de lançamento, popularidade e duração.

---

## ⚙️ Tecnologias e Pacotes

- `streamlit`
- `pytrends`
- `google-api-python-client`
- `textblob`
- `firebase-admin`
- `spotipy`
- `plotly`, `matplotlib`, `wordcloud`
- `pandas`, `tenacity`, `pydantic`

---

## 🛠️ Instalação Local

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/youtube-spotify-trends.git
cd youtube-spotify-trends
