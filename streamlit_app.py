import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
import asyncio
from typing import Dict, List, Optional
import os

from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.agents.interaction_agent import InteractionAgent
from app.agents.post_draft_agent import PostDraftAgent
from app.agents.connection_agent import ConnectionAgent
from app.agents.hashtag_agent import HashtagAgent

# Konfiguration
st.set_page_config(
    page_title="LinkedIn Growth Agent",
    page_icon="📈",
    layout="wide"
)

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Services initialisieren
linkedin_service = LinkedInService()
ai_service = AIService()

# Agenten initialisieren
interaction_agent = InteractionAgent(linkedin_service, ai_service)
post_draft_agent = PostDraftAgent(linkedin_service, ai_service)
connection_agent = ConnectionAgent(linkedin_service, ai_service)
hashtag_agent = HashtagAgent(linkedin_service, ai_service)

def get_posts() -> List[Dict]:
    """Posts vom Backend abrufen"""
    try:
        response = requests.get(f"{API_URL}/posts")
        if response.ok:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Posts: {str(e)}")
        return []

def get_interactions() -> List[Dict]:
    """Interaktionen vom Backend abrufen"""
    try:
        response = requests.get(f"{API_URL}/interactions")
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
        response = requests.post(f"{API_URL}/posts", json=data)
        return response.ok
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Posts: {str(e)}")
        return False

# Hauptanwendung
with st.sidebar:
    st.title("LinkedIn Growth Agent")
    st.markdown("---")
    
    # Agenten-Status
    st.subheader("Agenten-Status")
    agent_status = {
        "Interaktions-Agent": "🟢 Aktiv",
        "Post-Draft-Agent": "🟢 Aktiv",
        "Vernetzungs-Agent": "🟢 Aktiv",
        "Hashtag-Agent": "🟢 Aktiv"
    }
    for agent, status in agent_status.items():
        st.text(f"{agent}: {status}")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Post-Erstellung",
    "Vernetzung",
    "Interaktionen",
    "Einstellungen"
])

# Dashboard Tab
with tab1:
    st.header("Dashboard")
    
    # Statistik-Karten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Posts diese Woche",
            value="3",
            delta="2 geplant"
        )
    
    with col2:
        st.metric(
            label="Neue Verbindungen",
            value="28",
            delta="↑ 15%"
        )
    
    with col3:
        st.metric(
            label="Interaktionen",
            value="45",
            delta="↑ 23%"
        )
    
    with col4:
        st.metric(
            label="Hashtag-Kommentare",
            value="32",
            delta="↑ 12%"
        )
    
    # Aktivitäts-Feed
    st.subheader("Letzte Aktivitäten")
    activities = [
        {"time": "Vor 5 Min.", "type": "Post", "description": "Neuer Post-Entwurf erstellt: 'KI im Marketing'"},
        {"time": "Vor 15 Min.", "type": "Vernetzung", "description": "5 neue Verbindungsanfragen gesendet"},
        {"time": "Vor 30 Min.", "type": "Interaktion", "description": "Kommentar auf Post von Max Mustermann"},
        {"time": "Vor 1 Std.", "type": "Hashtag", "description": "3 Kommentare zu #Marketing erstellt"}
    ]
    
    for activity in activities:
        with st.expander(f"{activity['time']} - {activity['type']}"):
            st.write(activity['description'])

# Post-Erstellung Tab
with tab2:
    st.header("Post-Erstellung")
    
    with st.form("post_creation"):
        topic = st.text_input("Thema", placeholder="z.B. KI im Marketing")
        tone = st.selectbox(
            "Tonalität",
            ["Professionell", "Locker", "Technisch", "Inspirierend"]
        )
        length = st.selectbox(
            "Länge",
            ["Kurz (< 1000 Zeichen)", "Mittel (1000-2000 Zeichen)", "Lang (> 2000 Zeichen)"]
        )
        scheduled_for = st.date_input("Geplantes Veröffentlichungsdatum")
        
        if st.form_submit_button("Post generieren"):
            if topic:
                st.success("Post wird generiert...")
                # Hier würde der Post-Draft-Agent aufgerufen
            else:
                st.error("Bitte geben Sie ein Thema ein")
    
    # Geplante Posts
    st.subheader("Geplante Posts")
    scheduled_posts = [
        {"date": "2024-03-20", "title": "KI im Marketing", "status": "Entwurf"},
        {"date": "2024-03-22", "title": "LinkedIn Growth Hacks", "status": "Geplant"},
        {"date": "2024-03-25", "title": "Content Marketing Trends", "status": "Geplant"}
    ]
    
    for post in scheduled_posts:
        with st.expander(f"{post['date']} - {post['title']}"):
            st.write(f"Status: {post['status']}")
            st.button("Bearbeiten", key=f"edit_{post['date']}")
            st.button("Löschen", key=f"delete_{post['date']}")

# Vernetzung Tab
with tab3:
    st.header("Vernetzung")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Neue Verbindungen")
        profile_urls = st.text_area(
            "LinkedIn-Profile (eine URL pro Zeile)",
            placeholder="https://linkedin.com/in/profile1\nhttps://linkedin.com/in/profile2"
        )
        
        include_message = st.checkbox("Personalisierte Nachricht senden")
        
        if st.button("Verbindungen aufbauen"):
            if profile_urls:
                st.success("Verbindungsanfragen werden gesendet...")
                # Hier würde der Connection-Agent aufgerufen
            else:
                st.error("Bitte geben Sie mindestens eine Profil-URL ein")
    
    with col2:
        st.subheader("Follow-ups")
        days = st.slider("Tage seit Verbindung", 1, 14, 3)
        
        if st.button("Follow-ups senden"):
            st.success("Follow-ups werden vorbereitet...")
            # Hier würde der Connection-Agent für Follow-ups aufgerufen

# Interaktionen Tab
with tab4:
    st.header("Interaktionen")
    
    # Hashtag-Konfiguration
    st.subheader("Hashtag-Monitoring")
    hashtags = st.text_input(
        "Hashtags überwachen (durch Kommas getrennt)",
        placeholder="#marketing, #sales, #ai"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_interactions = st.number_input(
            "Maximale Interaktionen pro Tag",
            min_value=1,
            max_value=50,
            value=20
        )
    
    with col2:
        interaction_types = st.multiselect(
            "Interaktionstypen",
            ["Like", "Kommentar"],
            default=["Like", "Kommentar"]
        )
    
    if st.button("Interaktionen starten"):
        if hashtags:
            st.success("Interaktionen werden gestartet...")
            # Hier würden die Interaction- und Hashtag-Agenten aufgerufen
        else:
            st.error("Bitte geben Sie mindestens einen Hashtag ein")

# Einstellungen Tab
with tab5:
    st.header("Einstellungen")
    
    # LinkedIn-Einstellungen
    st.subheader("LinkedIn-Konfiguration")
    linkedin_email = st.text_input("LinkedIn E-Mail")
    linkedin_password = st.text_input("LinkedIn Passwort", type="password")
    
    # OpenAI-Einstellungen
    st.subheader("OpenAI-Konfiguration")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    # Zeitplan-Einstellungen
    st.subheader("Zeitplan")
    posts_per_week = st.slider("Posts pro Woche", 1, 7, 3)
    connections_per_day = st.slider("Verbindungen pro Tag", 1, 50, 39)
    
    # Speichern-Button
    if st.button("Einstellungen speichern"):
        # Hier würden die Einstellungen gespeichert
        st.success("Einstellungen wurden gespeichert") 