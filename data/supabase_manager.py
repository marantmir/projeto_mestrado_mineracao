from supabase import create_client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# Inserir dados
data = {"nome": "Música 1", "artista": "Artista 1", "popularidade": 90}
supabase.table("spotify").insert(data).execute()
