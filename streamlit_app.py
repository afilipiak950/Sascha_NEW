import streamlit as st
import pandas as pd
from datetime import datetime
import json
import requests
from typing import Dict, List, Optional
import os

# Konfiguration
st.set_page_config(
    page_title="LinkedIn Growth Agent",
    page_icon="📈",
    layout="wide"
)

# Session State initialisieren
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = None

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

def login(email: str, password: str) -> bool:
    """Benutzeranmeldung"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.ok:
            data = response.json()
            st.session_state.token = data["token"]
            st.session_state.authenticated = True
            return True
        return False
    except Exception as e:
        st.error(f"Anmeldung fehlgeschlagen: {str(e)}")
        return False

def logout():
    """Benutzerabmeldung"""
    st.session_state.authenticated = False
    st.session_state.token = None

def get_posts() -> List[Dict]:
    """Posts vom Backend abrufen"""
    try:
        response = requests.get(
            f"{API_URL}/posts",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.ok:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Posts: {str(e)}")
        return []

def get_interactions() -> List[Dict]:
    """Interaktionen vom Backend abrufen"""
    try:
        response = requests.get(
            f"{API_URL}/interactions",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.ok:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Interaktionen: {str(e)}")
        return []

def create_post(title: str, content: str, hashtags: List[str], scheduled_for: Optional[datetime] = None):
    """Neuen Post erstellen"""
    try:
        data = {
            "title": title,
            "content": content,
            "hashtags": hashtags,
            "scheduled_for": scheduled_for.isoformat() if scheduled_for else None
        }
        response = requests.post(
            f"{API_URL}/posts",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            json=data
        )
        return response.ok
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Posts: {str(e)}")
        return False

# Login-Seite
if not st.session_state.authenticated:
    st.title("LinkedIn Growth Agent")
    st.subheader("Anmeldung")
    
    with st.form("login_form"):
        email = st.text_input("E-Mail")
        password = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Anmelden")
        
        if submit:
            if login(email, password):
                st.success("Anmeldung erfolgreich!")
                st.experimental_rerun()
            else:
                st.error("Anmeldung fehlgeschlagen!")

# Hauptanwendung
else:
    # Sidebar
    with st.sidebar:
        st.title("LinkedIn Growth Agent")
        if st.button("Abmelden"):
            logout()
            st.experimental_rerun()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Neuer Post", "Einstellungen", "Statistiken"])
    
    # Dashboard Tab
    with tab1:
        st.header("Dashboard")
        
        # Posts
        st.subheader("Letzte Posts")
        posts = get_posts()
        if posts:
            for post in posts[:5]:  # Zeige die letzten 5 Posts
                with st.expander(f"{post['title']} - {post['status']}"):
                    st.write(post['content'])
                    st.write(f"Hashtags: {', '.join(post['hashtags'])}")
                    if post.get('scheduled_for'):
                        st.write(f"Geplant für: {post['scheduled_for']}")
        
        # Interaktionen
        st.subheader("Letzte Interaktionen")
        interactions = get_interactions()
        if interactions:
            for interaction in interactions[:5]:  # Zeige die letzten 5 Interaktionen
                with st.expander(f"{interaction['type']} - {interaction['status']}"):
                    st.write(f"Ziel: {interaction['target_name']}")
                    st.write(f"Titel: {interaction['target_title']}")
                    if interaction.get('content'):
                        st.write(f"Inhalt: {interaction['content']}")
    
    # Neuer Post Tab
    with tab2:
        st.header("Neuer Post")
        
        with st.form("new_post"):
            title = st.text_input("Titel")
            content = st.text_area("Inhalt")
            hashtags = st.text_input("Hashtags (durch Kommas getrennt)")
            scheduled_for = st.date_input("Veröffentlichungsdatum")
            
            if st.form_submit_button("Post erstellen"):
                if title and content:
                    hashtag_list = [tag.strip() for tag in hashtags.split(",") if tag.strip()]
                    if create_post(title, content, hashtag_list, scheduled_for):
                        st.success("Post erfolgreich erstellt!")
                    else:
                        st.error("Fehler beim Erstellen des Posts")
                else:
                    st.error("Bitte fülle alle Pflichtfelder aus")
    
    # Einstellungen Tab
    with tab3:
        st.header("Einstellungen")
        # TODO: Implementiere Einstellungen
    
    # Statistiken Tab
    with tab4:
        st.header("Statistiken")
        # TODO: Implementiere Statistiken 