import streamlit as st
import asyncio
from app.core.config import settings
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.agents.interaction_agent import InteractionAgent
from app.agents.post_draft_agent import PostDraftAgent
from app.agents.connection_agent import ConnectionAgent
from app.agents.hashtag_agent import HashtagAgent
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from app.core.exceptions import LinkedInError, LinkedInAuthError, LinkedInConnectionError, LinkedInRateLimitError

# Konfiguration
st.set_page_config(
    page_title="LinkedIn Agent Orchestrator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Grundlegende Stile */
    .main {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #0077B5, #00A0DC);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2.5rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Metrik-Karten */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        color: #0077B5;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-card p {
        color: #28a745;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Agent-Status */
    .agent-status {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #0077B5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .agent-status:hover {
        transform: translateX(5px);
    }
    
    .agent-status h4 {
        color: #0077B5;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    
    /* Status-Badges */
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .status-active {
        background: #e6f3ff;
        color: #0077B5;
    }
    
    .status-inactive {
        background: #ffe6e6;
        color: #dc3545;
    }
    
    /* Aktivitäts-Feed */
    .activity-item {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid #0077B5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .activity-item:hover {
        transform: translateX(5px);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0077B5, #00A0DC);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,119,181,0.2);
    }
    
    /* Input-Felder */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #0077B5;
        box-shadow: 0 0 0 3px rgba(0,119,181,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #dee2e6;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0077B5, #00A0DC);
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Responsive Anpassungen */
    @media (max-width: 768px) {
        .stApp {
            padding: 1rem;
        }
        
        .header {
            padding: 1.5rem;
        }
        
        .header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Services initialisieren
linkedin_service = LinkedInService()
ai_service = AIService()
interaction_agent = InteractionAgent(linkedin_service, ai_service)
post_draft_agent = PostDraftAgent(linkedin_service, ai_service)
connection_agent = ConnectionAgent(linkedin_service, ai_service)
hashtag_agent = HashtagAgent(linkedin_service, ai_service)

# Header
st.markdown("""
<div class="header">
    <h1>LinkedIn Agent Orchestrator</h1>
    <p>Automatisiere und optimiere deine LinkedIn-Aktivitäten</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/800px-LinkedIn_logo_initials.png", width=100)
    st.markdown("## Navigation")
    
    # Status-Anzeige
    st.markdown("### Agent Status")
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown("""
        <div class="agent-status">
            <h4>Post Agent</h4>
            <span class="status-badge status-active">Aktiv</span>
            <div class="progress-bar">
                <div class="progress" style="width: 75%"></div>
            </div>
            <p>Letzte Aktivität: 2024-04-06 10:15</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-status">
            <h4>Connection Agent</h4>
            <span class="status-badge status-active">Aktiv</span>
            <div class="progress-bar">
                <div class="progress" style="width: 60%"></div>
            </div>
            <p>Letzte Aktivität: 2024-04-06 09:30</p>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col2:
        st.markdown("""
        <div class="agent-status">
            <h4>Engagement Agent</h4>
            <span class="status-inactive">Inaktiv</span>
            <div class="progress-bar">
                <div class="progress" style="width: 0%"></div>
            </div>
            <p>Letzte Aktivität: 2024-04-05 15:45</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-status">
            <h4>Hashtag Monitor</h4>
            <span class="status-badge status-active">Aktiv</span>
            <div class="progress-bar">
                <div class="progress" style="width: 90%"></div>
            </div>
            <p>Letzte Aktivität: 2024-04-06 11:20</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### Menü")
    page = st.selectbox(
        "Wähle eine Funktion",
        ["Dashboard", "Post Erstellung", "Networking", "Interaktionen", "Einstellungen"],
        key="nav_select"
    )
    
    if st.button("Abmelden"):
        asyncio.run(linkedin_service.close())
        st.session_state.is_authenticated = False
        st.rerun()

# Hauptbereich
if page == "Dashboard":
    st.markdown("## Übersicht")
    
    # Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>12</h3>
            <p>Posts erstellt</p>
            <span class="trend positive">+3 diese Woche</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>24</h3>
            <p>Neue Verbindungen</p>
            <span class="trend positive">+8 diese Woche</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>156</h3>
            <p>Engagement Aktionen</p>
            <span class="trend positive">+42 diese Woche</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>8</h3>
            <p>Hashtag Interaktionen</p>
            <span class="trend positive">+2 diese Woche</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Aktivitäts-Graph
    st.markdown("## Aktivitätsverlauf")
    st.markdown("""
    <div class="activity-graph">
        <img src="https://via.placeholder.com/800x400?text=Aktivitätsgraph" alt="Aktivitätsgraph" style="width: 100%; border-radius: 10px;">
    </div>
    """, unsafe_allow_html=True)
    
    # Letzte Aktivitäten
    st.markdown("## Letzte Aktivitäten")
    st.markdown("""
    <div class="activity-feed">
        <div class="activity-item">
            <div class="activity-icon">📝</div>
            <div class="activity-content">
                <h4>Neuer Post erstellt</h4>
                <p>KI-gestützte Automatisierung für LinkedIn</p>
                <span class="activity-time">Vor 2 Stunden</span>
            </div>
            <span class="status-badge status-success">Erfolgreich</span>
        </div>
        
        <div class="activity-item">
            <div class="activity-icon">🤝</div>
            <div class="activity-content">
                <h4>Neue Verbindung</h4>
                <p>Max Mustermann - Tech Lead bei Beispiel GmbH</p>
                <span class="activity-time">Vor 3 Stunden</span>
            </div>
            <span class="status-badge status-success">Erfolgreich</span>
        </div>
        
        <div class="activity-item">
            <div class="activity-icon">💬</div>
            <div class="activity-content">
                <h4>Kommentar gepostet</h4>
                <p>Beitrag von Sarah Schmidt</p>
                <span class="activity-time">Vor 5 Stunden</span>
            </div>
            <span class="status-badge status-success">Erfolgreich</span>
        </div>
        
        <div class="activity-item">
            <div class="activity-icon">🔍</div>
            <div class="activity-content">
                <h4>Hashtag Analyse</h4>
                <p>#DigitalTransformation #Innovation</p>
                <span class="activity-time">Vor 6 Stunden</span>
            </div>
            <span class="status-badge status-pending">In Bearbeitung</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "Post Erstellung":
    st.markdown("## Post Erstellung")
    
    # Post-Typ Auswahl
    post_type = st.selectbox(
        "Wähle den Post-Typ",
        ["Standard Post", "Karriere Update", "Artikel", "Umfrage", "Event"]
    )
    
    # Post-Inhalt
    with st.form("post_form"):
        topic = st.text_input("Thema")
        tone = st.selectbox("Ton", ["Professional", "Casual", "Informativ", "Inspirierend"])
        length = st.selectbox("Länge", ["Kurz", "Mittel", "Lang"])
        
        # KI-Optimierung
        st.markdown("### KI-Optimierung")
        optimize_engagement = st.checkbox("Engagement optimieren")
        add_hashtags = st.checkbox("Relevante Hashtags hinzufügen")
        optimize_timing = st.checkbox("Beste Veröffentlichungszeit berechnen")
        
        if st.form_submit_button("Post generieren"):
            try:
                with st.spinner("Generiere Post..."):
                    post = asyncio.run(post_draft_agent.generate_post_content(
                        topic=topic,
                        tone=tone,
                        length=length,
                        optimize_engagement=optimize_engagement,
                        add_hashtags=add_hashtags,
                        optimize_timing=optimize_timing
                    ))
                    st.success("Post erfolgreich generiert!")
                    
                    # Post-Vorschau
                    st.markdown("### Post-Vorschau")
                    st.markdown(f"""
                    <div class="post-preview">
                        <h3>{post['title']}</h3>
                        <p>{post['content']}</p>
                        <div class="hashtags">
                            {', '.join(post['hashtags'])}
                        </div>
                        <div class="post-meta">
                            <span>Optimale Veröffentlichungszeit: {post['optimal_time']}</span>
                            <span>Geschätztes Engagement: {post['estimated_engagement']}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Post-Veröffentlichung
                    if st.button("Post veröffentlichen"):
                        asyncio.run(post_draft_agent.publish_post(post))
                        st.success("Post erfolgreich veröffentlicht!")
            except LinkedInError as e:
                st.error(f"Fehler beim Generieren des Posts: {str(e)}")

elif page == "Networking":
    st.markdown("## Networking")
    
    # Verbindungsstrategie
    strategy = st.selectbox(
        "Wähle eine Strategie",
        ["Zielgruppen-basiert", "Branchen-spezifisch", "Geografisch", "Skills-basiert"]
    )
    
    # Verbindungsparameter
    with st.form("connection_form"):
        st.markdown("### Verbindungsparameter")
        industry = st.multiselect(
            "Branchen",
            ["IT", "Finanzen", "Marketing", "HR", "Vertrieb", "Engineering"]
        )
        location = st.text_input("Standort")
        skills = st.multiselect(
            "Skills",
            ["Python", "Machine Learning", "Data Science", "Leadership", "Project Management"]
        )
        
        # Personalisierung
        st.markdown("### Personalisierung")
        custom_message = st.text_area("Personalisiertes Anschreiben")
        use_ai_message = st.checkbox("KI-generiertes Anschreiben verwenden")
        
        if st.form_submit_button("Verbindungen suchen"):
            try:
                with st.spinner("Suche passende Profile..."):
                    profiles = asyncio.run(connection_agent.find_profiles(
                        industry=industry,
                        location=location,
                        skills=skills
                    ))
                    
                    st.success(f"{len(profiles)} passende Profile gefunden!")
                    
                    # Profile anzeigen
                    for profile in profiles:
                        st.markdown(f"""
                        <div class="profile-card">
                            <h3>{profile['name']}</h3>
                            <p>{profile['title']}</p>
                            <p>{profile['company']}</p>
                            <button class="connect-button">Verbinden</button>
                        </div>
                        """, unsafe_allow_html=True)
            except LinkedInError as e:
                st.error(f"Fehler bei der Profilsuche: {str(e)}")

elif page == "Interaktionen":
    st.markdown("## Interaktionen")
    
    # Interaktionsstrategie
    strategy = st.selectbox(
        "Wähle eine Strategie",
        ["Hashtag-basiert", "Inhalts-basiert", "Profil-basiert", "Zeit-basiert"]
    )
    
    # Interaktionsparameter
    with st.form("interaction_form"):
        st.markdown("### Interaktionsparameter")
        hashtags = st.multiselect(
            "Hashtags",
            ["#AI", "#Innovation", "#Tech", "#Leadership", "#DigitalTransformation"]
        )
        content_types = st.multiselect(
            "Inhaltstypen",
            ["Artikel", "Posts", "Kommentare", "Umfragen"]
        )
        max_interactions = st.slider("Max. Interaktionen pro Tag", 0, 50, 20)
        interaction_types = st.multiselect(
            "Interaktionstypen",
            ["Likes", "Kommentare", "Teilen", "Speichern"]
        )
        
        # Zeitplanung
        st.markdown("### Zeitplanung")
        schedule_start = st.time_input("Startzeit")
        schedule_end = st.time_input("Endzeit")
        timezone = st.selectbox("Zeitzone", ["UTC", "CET", "EST"])
        
        if st.form_submit_button("Interaktionen starten"):
            try:
                with st.spinner("Starte Interaktionen..."):
                    success = asyncio.run(interaction_agent.start_interactions(
                        hashtags=hashtags,
                        content_types=content_types,
                        max_interactions=max_interactions,
                        interaction_types=interaction_types,
                        schedule_start=schedule_start,
                        schedule_end=schedule_end,
                        timezone=timezone
                    ))
                    if success:
                        st.success("Interaktionen erfolgreich gestartet!")
                    else:
                        st.error("Fehler beim Starten der Interaktionen")
            except LinkedInError as e:
                st.error(f"Fehler bei den Interaktionen: {str(e)}")

elif page == "Einstellungen":
    st.markdown("## Einstellungen")
    
    # LinkedIn Einstellungen
    st.markdown("### LinkedIn Einstellungen")
    with st.form("linkedin_settings"):
        linkedin_email = st.text_input("LinkedIn Email")
        linkedin_password = st.text_input("LinkedIn Passwort", type="password")
        api_key = st.text_input("LinkedIn API Key")
        
        if st.form_submit_button("LinkedIn Einstellungen speichern"):
            # Einstellungen speichern
            st.success("LinkedIn Einstellungen gespeichert!")
    
    # KI Einstellungen
    st.markdown("### KI Einstellungen")
    with st.form("ai_settings"):
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        model = st.selectbox(
            "KI-Modell",
            ["gpt-4", "gpt-3.5-turbo", "claude-2"]
        )
        temperature = st.slider("Kreativität", 0.0, 1.0, 0.7)
        
        if st.form_submit_button("KI Einstellungen speichern"):
            # Einstellungen speichern
            st.success("KI Einstellungen gespeichert!")
    
    # Automatisierungseinstellungen
    st.markdown("### Automatisierungseinstellungen")
    with st.form("automation_settings"):
        daily_limit = st.number_input("Tägliches Limit", 0, 1000, 100)
        cooldown = st.number_input("Abkühlzeit (Minuten)", 0, 60, 15)
        safety_mode = st.checkbox("Sicherheitsmodus aktivieren")
        
        if st.form_submit_button("Automatisierungseinstellungen speichern"):
            # Einstellungen speichern
            st.success("Automatisierungseinstellungen gespeichert!")