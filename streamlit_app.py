import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
import asyncio
from typing import Dict, List, Optional
import os
import time
import plotly.express as px
import plotly.graph_objects as go

from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.agents.interaction_agent import InteractionAgent
from app.agents.post_draft_agent import PostDraftAgent
from app.agents.connection_agent import ConnectionAgent
from app.agents.hashtag_agent import HashtagAgent

# Konfiguration
st.set_page_config(
    page_title="LinkedIn Growth Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für moderneres Design
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(90deg, #0077B5 0%, #00A0DC 100%);
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .info-box {
        background: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #0077B5;
        margin: 10px 0;
    }
    .agent-status {
        display: flex;
        align-items: center;
        margin: 10px 0;
        padding: 10px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .status-active {
        background: #4CAF50;
        box-shadow: 0 0 10px rgba(76,175,80,0.5);
    }
    .status-inactive {
        background: #f44336;
    }
    .tab-content {
        padding: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #0077B5 0%, #00A0DC 100%);
    }
</style>
""", unsafe_allow_html=True)

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

# Sidebar mit Agent-Status
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png", width=100)
    st.title("LinkedIn Growth Agent")
    
    st.markdown("### 🤖 Agent Status")
    
    # Agent Status mit Animation
    agents = {
        "Interaction Agent": interaction_agent,
        "Post-Draft Agent": post_draft_agent,
        "Connection Agent": connection_agent,
        "Hashtag Agent": hashtag_agent
    }
    
    for name, agent in agents.items():
        st.markdown(f"""
        <div class="agent-status">
            <div class="status-indicator status-active"></div>
            <div>
                <strong>{name}</strong><br>
                <small>Status: Aktiv</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Statistiken")
    
    # Beispiel-Metriken
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Posts", "12", "+2")
    with col2:
        st.metric("Interaktionen", "156", "+23")

# Hauptbereich
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h1>🚀 LinkedIn Growth Dashboard</h1>
    <p style='color: #666;'>Optimieren Sie Ihr LinkedIn-Wachstum mit KI-gestützten Agenten</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tabs = st.tabs(["📊 Dashboard", "📝 Post-Erstellung", "🤝 Networking", "💬 Interaktionen", "⚙️ Einstellungen"])

# Dashboard Tab
with tabs[0]:
    st.markdown("""
    <div class="info-box">
        <h3>🎯 Willkommen im Dashboard</h3>
        <p>Hier finden Sie eine Übersicht aller wichtigen Metriken und Aktivitäten Ihrer LinkedIn-Agenten.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrik-Karten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Posts</h3>
            <h2>12</h2>
            <p>+2 diese Woche</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤝 Neue Verbindungen</h3>
            <h2>45</h2>
            <p>+8 diese Woche</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>💬 Interaktionen</h3>
            <h2>156</h2>
            <p>+23 heute</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🏷️ Hashtag-Kommentare</h3>
            <h2>89</h2>
            <p>+12 diese Woche</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Aktivitäts-Feed mit Animation
    st.markdown("### 📅 Aktivitäts-Feed")
    
    # Beispiel-Aktivitäten
    activities = [
        {"time": "10:30", "action": "Neuer Post erstellt", "status": "success"},
        {"time": "09:45", "action": "5 neue Verbindungen", "status": "info"},
        {"time": "09:15", "action": "12 Interaktionen", "status": "success"},
        {"time": "08:30", "action": "Hashtag-Kommentare", "status": "info"}
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div style='padding: 10px; margin: 5px 0; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <span style='color: #666;'>{activity['time']}</span>
            <span style='margin-left: 10px;'>{activity['action']}</span>
            <span style='float: right; color: {"#4CAF50" if activity["status"] == "success" else "#2196F3"};'>●</span>
        </div>
        """, unsafe_allow_html=True)

# Post-Erstellung Tab
with tabs[1]:
    st.markdown("""
    <div class="info-box">
        <h3>📝 KI-gestützte Post-Erstellung</h3>
        <p>Der Post-Draft Agent erstellt automatisch ansprechende LinkedIn-Posts basierend auf Ihren Vorgaben.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Post-Parameter")
        topic = st.text_input("Thema", placeholder="z.B. Künstliche Intelligenz in der Geschäftswelt")
        tone = st.selectbox("Ton", ["Professionell", "Persönlich", "Informativ", "Inspirierend"])
        length = st.slider("Länge", 100, 1000, 300)
        scheduled_date = st.date_input("Geplanter Veröffentlichungstermin")
        
        if st.button("✨ Post generieren"):
            with st.spinner("Generiere Post..."):
                # Simuliere Generierung
                time.sleep(2)
                st.success("Post erfolgreich generiert!")
    
    with col2:
        st.markdown("### 📅 Geplante Posts")
        st.markdown("""
        <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h4>KI in der Geschäftswelt 2024</h4>
            <p>Geplant für: 15.02.2024</p>
            <div style='display: flex; gap: 10px;'>
                <button style='background: #0077B5; color: white; border: none; padding: 5px 10px; border-radius: 5px;'>Bearbeiten</button>
                <button style='background: #f44336; color: white; border: none; padding: 5px 10px; border-radius: 5px;'>Löschen</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Networking Tab
with tabs[2]:
    st.markdown("""
    <div class="info-box">
        <h3>🤝 Intelligentes Networking</h3>
        <p>Der Connection Agent findet und verbindet sich automatisch mit relevanten Kontakten in Ihrer Branche.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Neue Verbindungen")
        profile_url = st.text_input("LinkedIn Profil-URL", placeholder="https://linkedin.com/in/...")
        message = st.text_area("Personalisiere Nachricht", placeholder="Hallo! Ich habe gesehen, dass...")
        
        if st.button("🤝 Verbindung anfragen"):
            with st.spinner("Verbindungsanfrage wird gesendet..."):
                time.sleep(1)
                st.success("Verbindungsanfrage erfolgreich gesendet!")
    
    with col2:
        st.markdown("### 📬 Follow-ups")
        st.markdown("""
        <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h4>Max Mustermann</h4>
            <p>Verbunden seit: 5 Tagen</p>
            <button style='background: #0077B5; color: white; border: none; padding: 5px 10px; border-radius: 5px;'>Follow-up senden</button>
        </div>
        """, unsafe_allow_html=True)

# Interaktionen Tab
with tabs[3]:
    st.markdown("""
    <div class="info-box">
        <h3>💬 Automatisierte Interaktionen</h3>
        <p>Der Interaction Agent interagiert automatisch mit relevanten Posts in Ihrer Zielgruppe.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Interaktions-Einstellungen")
        hashtags = st.multiselect(
            "Hashtags überwachen",
            ["#AI", "#DigitalTransformation", "#Innovation", "#Tech", "#Business"],
            default=["#AI", "#DigitalTransformation"]
        )
        
        max_interactions = st.slider("Max. Interaktionen pro Tag", 10, 100, 50)
        interaction_types = st.multiselect(
            "Interaktionstypen",
            ["Like", "Kommentar"],
            default=["Like", "Kommentar"]
        )
        
        if st.button("▶️ Interaktionen starten"):
            with st.spinner("Starte Interaktionen..."):
                time.sleep(1)
                st.success("Interaktionen erfolgreich gestartet!")
    
    with col2:
        st.markdown("### 📊 Interaktions-Statistiken")
        # Beispiel-Chart
        data = pd.DataFrame({
            'Tag': ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'],
            'Interaktionen': [12, 19, 15, 17, 14, 23, 25]
        })
        fig = px.line(data, x='Tag', y='Interaktionen', title='Interaktionen pro Tag')
        st.plotly_chart(fig)

# Einstellungen Tab
with tabs[4]:
    st.markdown("""
    <div class="info-box">
        <h3>⚙️ System-Einstellungen</h3>
        <p>Konfigurieren Sie hier Ihre LinkedIn-Credentials und Agent-Einstellungen.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔑 LinkedIn Credentials")
    linkedin_email = st.text_input("LinkedIn E-Mail", type="password")
    linkedin_password = st.text_input("LinkedIn Passwort", type="password")
    
    st.markdown("### 🤖 OpenAI API")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    st.markdown("### ⏰ Zeitplan")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Post-Erstellung")
        post_days = st.multiselect(
            "Post-Tage",
            ["Montag", "Mittwoch", "Freitag"],
            default=["Montag", "Freitag"]
        )
        post_time = st.time_input("Post-Zeit", value=datetime.strptime("09:00", "%H:%M"))
    
    with col2:
        st.markdown("#### 💬 Interaktionen")
        interaction_days = st.multiselect(
            "Interaktions-Tage",
            ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"],
            default=["Montag", "Mittwoch", "Freitag"]
        )
        interaction_time = st.time_input("Interaktions-Zeit", value=datetime.strptime("10:00", "%H:%M"))
    
    if st.button("💾 Einstellungen speichern"):
        with st.spinner("Speichere Einstellungen..."):
            time.sleep(1)
            st.success("Einstellungen erfolgreich gespeichert!")

# Footer
st.markdown("""
<div style='text-align: center; padding: 20px; margin-top: 50px; color: #666;'>
    <p>Powered by LinkedIn Growth Agent | Version 1.0</p>
</div>
""", unsafe_allow_html=True) 