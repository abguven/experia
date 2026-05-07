"""
Experia v3.0 - Carnet d'Expériences Délirantes
Avec authentification Google, validation Pydantic, upload d'images
"""

import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import base64
from typing import List, Optional
from pydantic import BaseModel, field_validator, ValidationError
import os

# ========== CONFIGURATION ==========
st.set_page_config(page_title="Experia", page_icon="🔥", layout="wide")

# Récupération sécurisée des secrets
try:
    AUTHORIZED_EMAILS = st.secrets["auth"]["authorized_emails"]
    MONGO_URI = st.secrets["mongo"]["uri"]
except Exception as e:
    st.error("❌ Erreur de configuration : Il manque des informations dans secrets.toml")
    st.error(f"Détail : {e}")
    st.stop()

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
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v not in ['problème', 'astuce', 'note']:
            raise ValueError('Doit être "problème", "astuce" ou "note"')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if not v:
            raise ValueError('Au moins un tag requis')
        return v

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
        # Si la collection n'existe pas encore, on ignore
        if "experiences" in db.list_collection_names():
             db.command("collMod", "experiences", validator=schema, validationLevel="moderate")
    except:
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
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.read()
    base64_str = base64.b64encode(bytes_data).decode('utf-8')
    return base64_str

# ========== GESTION AUTHENTIFICATION ==========

# 1. Non connecté
if not st.user.is_logged_in:
    st.title("🔐 Connexion à Experia")
    st.write("Veuillez vous connecter avec votre compte Google autorisé.")
    if st.button("Se connecter avec Google", type="primary"):
        st.login("google")
    st.stop()

# 2. Email non autorisé
if st.user.email not in AUTHORIZED_EMAILS:
    st.title("⛔ Accès refusé")
    st.error(f"L'adresse email **{st.user.email}** n'est pas autorisée à accéder à cette application.")
    if st.button("Se déconnecter"):
        st.logout()
    st.stop()

# 3. Connecté et autorisé -> l'application continue
# ======================================================================

# Initialisation MongoDB (Seulement si autorisé)
try:
    client = init_connection()
    setup_schema_validation(client)
    notes = get_notes(client)
except Exception as e:
    st.error(f"❌ Erreur connexion MongoDB: {e}")
    st.stop()

# Header Application
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🔥 Experia - Carnet d'Expériences")
    st.caption(f"Connecté en tant que : {st.user.name} ({st.user.email})")
with col2:
    if st.button("🚪 Déconnexion"):
        st.logout()

# Initialisation Session State pour UI
if 'show_form' not in st.session_state:
    st.session_state.show_form = False
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

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
            cat_list = ["problème", "astuce", "note"]
            curr_cat = default_data.get('category', 'problème')
            cat_index = cat_list.index(curr_cat) if curr_cat in cat_list else 0
            category = st.selectbox("Catégorie*", cat_list, index=cat_index)
        
        # Upload d'images
        st.markdown("### 📸 Screenshots")
        uploaded_files = st.file_uploader(
            "Ajoute des captures d'écran (PNG, JPG)",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
        
        # Gestion images existantes en mode édition
        existing_screenshots = default_data.get('screenshots', [])
        
        # On utilise des clés dynamiques pour stocker l'état des checkbox
        images_to_keep_temp = []
        if existing_screenshots and edit_mode:
            st.markdown("**Images existantes:**")
            for idx, screenshot in enumerate(existing_screenshots):
                col_img, col_btn = st.columns([4, 1])
                with col_img:
                    st.caption(f"🖼️ {screenshot['name']}")
                with col_btn:
                    # Checkbox pour garder l'image
                    keep = st.checkbox("Garder", value=True, key=f"keep_{st.session_state.edit_id}_{idx}")
                    if keep:
                        images_to_keep_temp.append(screenshot)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
        
        if submitted and title and problem and solution and tags_input:
            # Préparation des screenshots
            final_screenshots = []
            
            # 1. Images conservées
            if edit_mode:
                final_screenshots.extend(images_to_keep_temp)
            
            # 2. Nouvelles images
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    if uploaded_file.size > 5 * 1024 * 1024:
                        st.error(f"❌ {uploaded_file.name} trop volumineux (max 5MB)")
                        continue
                    
                    img_base64 = encode_image(uploaded_file)
                    final_screenshots.append({
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
                "screenshots": final_screenshots,
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

# Affichage conditionnel du formulaire
if st.session_state.get('show_form', False):
    if st.session_state.get('edit_mode', False):
        edit_note = next((n for n in notes if n['_id'] == st.session_state.edit_id), None)
        if edit_note:
            render_form(edit_mode=True, existing_data=edit_note)
    else:
        render_form(edit_mode=False)
    st.markdown("---")

# ========== FILTRAGE ET LISTING ==========
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

for note in filtered_notes:
    category_icons = {"problème": "🔴", "astuce": "💡", "note": "📝"}
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
        
        # Contenu
        if note.get('problem'):
            st.markdown("### ❌ Problème")
            st.error(note.get('problem'))
        
        if note.get('solution'):
            st.markdown("### ✅ Solution")
            st.success(note.get('solution'))
        
        if note.get('code_snippet'):
            st.markdown("### 💻 Code")
            st.code(note['code_snippet'], language="python")
        
        # Screenshots
        if note.get('screenshots'):
            st.markdown("### 📸 Screenshots")
            # Affichage en grille (max 3 par ligne)
            cols = st.columns(3)
            for i, screenshot in enumerate(note['screenshots']):
                with cols[i % 3]:
                    try:
                        img_data = base64.b64decode(screenshot['data'])
                        st.image(img_data, caption=screenshot['name'], use_container_width=True)
                    except:
                        st.error("Image corrompue")
        
        if note.get('notes'):
            st.markdown("### 📝 Notes")
            st.info(note['notes'])
        
        # Footer Note
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📅 {note.get('date', 'N/A')}")
        with col2:
            st.caption(f"🏷️ {note.get('category', 'N/A')}")
        
        if note.get('tags'):
            st.markdown("**Tags:** " + " ".join([f"`{tag}`" for tag in note['tags']]))