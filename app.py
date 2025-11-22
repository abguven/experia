"""
Experia v2.0 - Carnet d'Expériences Délirantes
Avec authentification, validation Pydantic, upload d'images, édition/suppression
"""

import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import base64
from io import BytesIO
from typing import List, Optional
from pydantic import BaseModel, validator, ValidationError
import os

# ========== MODELS PYDANTIC ==========
class Screenshot(BaseModel):
    name: str
    data: str
    mime_type: str

class Experience(BaseModel):
    title: str
    problem: str
    solution: str
    tags: List[str]
    code_snippet: Optional[str] = ""
    notes: Optional[str] = ""
    screenshots: List[Screenshot] = []
    category: str
    date: str
    
    @validator('category')
    def validate_category(cls, v):
        if v not in ['problème', 'astuce', 'note']:
            raise ValueError('Doit être "problème", "astuce" ou "note"')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Au moins un tag requis')
        return v

# ========== CONFIGURATION ==========
st.set_page_config(page_title="Experia", page_icon="🔥", layout="wide")

MONGO_URI = st.secrets.get("MONGO_URI", os.getenv("MONGO_URI", ""))
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")

# ========== CONNEXION MONGODB ==========
@st.cache_resource
def init_connection():
    client = MongoClient(MONGO_URI)
    return client

@st.cache_resource
def setup_schema_validation(_client):
    """Configure la validation de schéma MongoDB"""
    db = _client.dev_notes
    
    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["title", "problem", "solution", "tags", "date", "category"],
            "properties": {
                "title": {"bsonType": "string"},
                "problem": {"bsonType": "string"},
                "solution": {"bsonType": "string"},
                "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
                "code_snippet": {"bsonType": "string"},
                "notes": {"bsonType": "string"},
                "category": {"enum": ["problème", "astuce", "note"]},
                "date": {"bsonType": "string"},
                "screenshots": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["name", "data", "mime_type"],
                        "properties": {
                            "name": {"bsonType": "string"},
                            "data": {"bsonType": "string"},
                            "mime_type": {"bsonType": "string"}
                        }
                    }
                }
            }
        }
    }
    
    try:
        # Seulement modifier, JAMAIS créer
        db.command("collMod", "experiences", validator=schema, validationLevel="moderate")
    except:
        # Ignore les erreurs (collection n'existe pas encore, pas grave)
        pass

@st.cache_data(ttl=10)
def get_notes(_client):
    db = _client.dev_notes
    notes = list(db.experiences.find().sort("date", -1))
    return notes

def add_note(client, note_data):
    try:
        exp = Experience(**note_data)
        db = client.dev_notes
        db.experiences.insert_one(exp.dict())
        st.cache_data.clear()
        return True, "✅ Expérience ajoutée !"
    except ValidationError as e:
        return False, f"❌ Erreur de validation: {e}"
    except Exception as e:
        return False, f"❌ Erreur MongoDB: {e}"

def update_note(client, note_id, note_data):
    try:
        exp = Experience(**note_data)
        db = client.dev_notes
        result = db.experiences.update_one(
            {"_id": note_id},
            {"$set": exp.dict()}
        )
        st.cache_data.clear()
        return True, "✅ Expérience mise à jour !"
    except ValidationError as e:
        return False, f"❌ Erreur de validation: {e}"
    except Exception as e:
        return False, f"❌ Erreur MongoDB: {e}"

def delete_note(client, note_id):
    try:
        db = client.dev_notes
        db.experiences.delete_one({"_id": note_id})
        st.cache_data.clear()
        return True, "✅ Expérience supprimée !"
    except Exception as e:
        return False, f"❌ Erreur: {e}"

def encode_image(uploaded_file):
    """Encode une image en base64"""
    bytes_data = uploaded_file.read()
    base64_str = base64.b64encode(bytes_data).decode('utf-8')
    return base64_str

# ========== AUTHENTIFICATION ==========
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Connexion à Experia")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Utilisateur", value="abguven")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    st.stop()

# ========== INTERFACE PRINCIPALE ==========
try:
    client = init_connection()
    setup_schema_validation(client)
    notes = get_notes(client)
except Exception as e:
    st.error(f"❌ Erreur connexion MongoDB: {e}")
    st.info("💡 Vérifie ta variable MONGO_URI dans les secrets")
    st.stop()

# Header
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🔥 Experia - Carnet d'Expériences")
with col2:
    if st.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()

# Barre de recherche et bouton ajout
col1, col2 = st.columns([4, 1])
with col1:
    search = st.text_input("🔍 Rechercher", placeholder="Titre, problème, tag, code...", label_visibility="collapsed")
with col2:
    if st.button("➕ Ajouter", use_container_width=True):
        st.session_state.show_form = True
        st.session_state.edit_mode = False
        st.session_state.edit_id = None

# ========== FORMULAIRE AJOUT/ÉDITION ==========
def render_form(edit_mode=False, existing_data=None):
    form_title = "✏️ Modifier l'expérience" if edit_mode else "➕ Nouvelle expérience"
    
    with st.form("experience_form", clear_on_submit=False):
        st.subheader(form_title)
        
        # Pré-remplir si mode édition
        default_data = existing_data if existing_data else {}
        
        title = st.text_input("Titre*", value=default_data.get('title', ''))
        problem = st.text_area("Problème rencontré*", value=default_data.get('problem', ''), height=80)
        solution = st.text_area("Solution trouvée*", value=default_data.get('solution', ''), height=80)
        code_snippet = st.text_area("Code snippet", value=default_data.get('code_snippet', ''), height=150)
        notes_field = st.text_area("Notes supplémentaires", value=default_data.get('notes', ''), height=80)
        
        col1, col2 = st.columns(2)
        with col1:
            tags_str = ', '.join(default_data.get('tags', []))
            tags_input = st.text_input("Tags* (séparés par virgules)", value=tags_str, placeholder="docker, postgres, networking")
        with col2:
            category = st.selectbox("Catégorie*", ["problème", "astuce", "note"], 
                                   index=["problème", "astuce", "note"].index(default_data.get('category', 'problème')) if default_data.get('category') in ["problème", "astuce", "note"] else 0)
        
        # Upload d'images
        st.markdown("### 📸 Screenshots")
        uploaded_files = st.file_uploader(
            "Ajoute des captures d'écran (PNG, JPG)",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
        
        # Afficher images existantes en mode édition
        existing_screenshots = default_data.get('screenshots', [])
        if existing_screenshots and edit_mode:
            st.markdown("**Images existantes:**")
            images_to_keep = []
            for idx, screenshot in enumerate(existing_screenshots):
                col_img, col_btn = st.columns([4, 1])
                with col_img:
                    st.caption(f"🖼️ {screenshot['name']}")
                with col_btn:
                    if st.checkbox("Garder", value=True, key=f"keep_img_{idx}"):
                        images_to_keep.append(screenshot)
            # Stocker dans session state pour utilisation après submit
            st.session_state[f'images_to_keep_{st.session_state.edit_id}'] = images_to_keep
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
        
        if submitted and title and problem and solution and tags_input:
            # Préparation des screenshots
            screenshots = []
            
            # Récupérer les images à garder en mode édition
            if edit_mode:
                screenshots = st.session_state.get(f'images_to_keep_{st.session_state.edit_id}', [])
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    # Vérifier la taille (max 5MB)
                    if uploaded_file.size > 5 * 1024 * 1024:
                        st.error(f"❌ {uploaded_file.name} trop volumineux (max 5MB)")
                        continue
                    
                    img_base64 = encode_image(uploaded_file)
                    screenshots.append({
                        "name": uploaded_file.name,
                        "data": img_base64,
                        "mime_type": uploaded_file.type
                    })
            
            note_data = {
                "title": title,
                "problem": problem,
                "solution": solution,
                "code_snippet": code_snippet,
                "notes": notes_field,
                "tags": [t.strip() for t in tags_input.split(",") if t.strip()],
                "category": category,
                "screenshots": screenshots,
                "date": default_data.get('date', datetime.now().strftime("%Y-%m-%d"))
            }
            
            if edit_mode:
                success, message = update_note(client, st.session_state.edit_id, note_data)
            else:
                success, message = add_note(client, note_data)
            
            if success:
                st.success(message)
                st.session_state.show_form = False
                st.session_state.edit_mode = False
                st.session_state.edit_id = None
                st.rerun()
            else:
                st.error(message)
        
        if cancelled:
            st.session_state.show_form = False
            st.session_state.edit_mode = False
            st.session_state.edit_id = None
            st.rerun()

# Afficher le formulaire si demandé
if st.session_state.get('show_form', False):
    if st.session_state.get('edit_mode', False):
        # Charger les données à éditer
        edit_note = next((n for n in notes if n['_id'] == st.session_state.edit_id), None)
        if edit_note:
            render_form(edit_mode=True, existing_data=edit_note)
    else:
        render_form(edit_mode=False)
    st.markdown("---")

# ========== FILTRAGE ET AFFICHAGE ==========
filtered_notes = notes
if search:
    search_lower = search.lower()
    filtered_notes = [
        n for n in notes 
        if search_lower in n.get('title', '').lower()
        or search_lower in n.get('problem', '').lower()
        or search_lower in n.get('solution', '').lower()
        or search_lower in n.get('code_snippet', '').lower()
        or any(search_lower in tag.lower() for tag in n.get('tags', []))
    ]

st.markdown(f"**{len(filtered_notes)} expérience(s)**")
st.markdown("---")

# Affichage des expériences
for note in filtered_notes:
    # Icônes par catégorie
    category_icons = {
        "problème": "🔴",
        "astuce": "💡", 
        "note": "📝"
    }
    category_icon = category_icons.get(note.get('category', 'note'), "📝")
    
    with st.expander(f"{category_icon} {note.get('title', 'Sans titre')}", expanded=False):
        
        # Boutons d'action
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            if st.button("✏️ Modifier", key=f"edit_{note['_id']}"):
                st.session_state.show_form = True
                st.session_state.edit_mode = True
                st.session_state.edit_id = note['_id']
                st.rerun()
        with col2:
            if st.button("🗑️ Supprimer", key=f"delete_{note['_id']}"):
                success, message = delete_note(client, note['_id'])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown("---")
        
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
        
        # Screenshots
        if note.get('screenshots'):
            st.markdown("### 📸 Screenshots")
            for screenshot in note['screenshots']:
                try:
                    img_data = base64.b64decode(screenshot['data'])
                    st.image(img_data, caption=screenshot['name'], use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Erreur affichage image: {screenshot['name']}")
        
        # Notes supplémentaires
        if note.get('notes'):
            st.markdown("### 📝 Notes")
            st.info(note['notes'])
        
        # Métadonnées
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📅 {note.get('date', 'N/A')}")
        with col2:
            st.caption(f"🏷️ {note.get('category', 'N/A')}")
        
        # Tags
        if note.get('tags'):
            st.markdown("**Tags:** " + " ".join([f"`{tag}`" for tag in note['tags']]))