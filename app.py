import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(page_title="Carnet d'Expériences", page_icon="🔥", layout="wide")

# ========== CONFIGURATION MONGODB ==========
# Modifie cette ligne avec ton URL Atlas
MONGO_URI = st.secrets.get("MONGO_URI", os.getenv("MONGO_URI"))

# Vérification mot de passe
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if password == st.secrets.get("APP_PASSWORD", ""):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()


# Connexion MongoDB Atlas
@st.cache_resource
def init_connection():
    client = MongoClient(MONGO_URI)
    return client

@st.cache_data(ttl=60)
def get_notes(_client):
    db = _client.dev_notes
    notes = list(db.experiences.find().sort("date", -1))
    return notes

def add_note(client, note_data):
    db = client.dev_notes
    note_data['date'] = datetime.now().strftime("%Y-%m-%d")
    db.experiences.insert_one(note_data)
    st.cache_data.clear()

# ========== INTERFACE PRINCIPALE ==========
st.title("🔥 Carnet d'Expériences Délirantes")

# Connexion MongoDB
try:
    client = init_connection()
    notes = get_notes(client)
except Exception as e:
    st.error(f"Erreur connexion MongoDB: {e}")
    st.info("💡 Configure ta variable d'environnement MONGO_URI ou modifie le code ligne 24")
    st.stop()

# Barre de recherche et bouton ajout
col1, col2 = st.columns([4, 1])
with col1:
    search = st.text_input("🔍 Rechercher", placeholder="Cherche par titre, problème, tag, code...")
with col2:
    st.write("")
    st.write("")
    if st.button("➕ Ajouter", use_container_width=True):
        st.session_state.show_form = True

# Formulaire d'ajout
if st.session_state.get('show_form', False):
    with st.form("add_note_form"):
        st.subheader("Nouvelle expérience")
        
        title = st.text_input("Titre*")
        problem = st.text_area("Problème rencontré*", height=80)
        solution = st.text_area("Solution trouvée*", height=80)
        code_snippet = st.text_area("Code snippet (optionnel)", height=150)
        notes_field = st.text_area("Notes supplémentaires")
        
        col1, col2 = st.columns(2)
        with col1:
            context = st.text_input("Tags (séparés par virgules)", placeholder="docker, postgres, networking")
            time_wasted = st.text_input("Temps perdu", placeholder="2h, 30min")
        with col2:
            criticality = st.selectbox("Criticité", ["chiant", "bloquant"])
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
        
        if submitted and title and problem and solution:
            note_data = {
                "title": title,
                "problem": problem,
                "solution": solution,
                "code_snippet": code_snippet,
                "notes": notes_field,
                "context": [t.strip() for t in context.split(",") if t.strip()],
                "time_wasted": time_wasted,
                "criticality": criticality
            }
            add_note(client, note_data)
            st.session_state.show_form = False
            st.success("✅ Expérience ajoutée !")
            st.rerun()
        
        if cancelled:
            st.session_state.show_form = False
            st.rerun()

# Filtrage des notes
filtered_notes = notes
if search:
    search_lower = search.lower()
    filtered_notes = [
        n for n in notes 
        if search_lower in n.get('title', '').lower()
        or search_lower in n.get('problem', '').lower()
        or search_lower in n.get('solution', '').lower()
        or search_lower in n.get('code_snippet', '').lower()
        or any(search_lower in tag.lower() for tag in n.get('context', []))
    ]

st.markdown(f"**{len(filtered_notes)} expérience(s)**")
st.markdown("---")

# Affichage des notes
for note in filtered_notes:
    with st.expander(f"{'🔴' if note.get('criticality') == 'bloquant' else '🟡'} {note.get('title', 'Sans titre')}", expanded=False):
        
        # Problème
        st.markdown("### ❌ Problème")
        st.error(note.get('problem', 'N/A'))
        
        # Solution
        st.markdown("### ✅ Solution")
        st.success(note.get('solution', 'N/A'))
        
        # Code snippet
        if note.get('code_snippet'):
            st.markdown("### 💻 Code")
            st.code(note['code_snippet'], language="python")
        
        # Notes supplémentaires
        if note.get('notes'):
            st.markdown("### 📝 Notes")
            st.info(note['notes'])
        
        # Métadonnées
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📅 {note.get('date', 'N/A')}")
        with col2:
            st.caption(f"⏱️ {note.get('time_wasted', 'N/A')}")
        with col3:
            st.caption(f"🎯 {note.get('criticality', 'N/A')}")
        
        # Tags
        if note.get('context'):
            st.markdown("**Tags:** " + " ".join([f"`{tag}`" for tag in note['context']]))