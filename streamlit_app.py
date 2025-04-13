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
from dotenv import load_dotenv
import os

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

def show_post_creation():
    st.markdown("## 📝 Post erstellen")
    
    # Eingabefelder für den Post
    topic = st.text_input("Thema des Posts", placeholder="z.B. KI in der Softwareentwicklung")
    
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Tonalität", ["professionell", "casual", "inspirierend", "technisch"])
        optimize_engagement = st.checkbox("Engagement optimieren", value=True)
    with col2:
        length = st.selectbox("Länge", ["kurz", "mittel", "lang"])
        add_hashtags = st.checkbox("Hashtags hinzufügen", value=True)
    
    # Bild-Upload
    uploaded_file = st.file_uploader("Bild für den Post (optional)", type=["jpg", "jpeg", "png"])
    
    # Generate-Button und Post-Vorschau
    if st.button("Post generieren", type="primary"):
        with st.spinner("Generiere Post..."):
            try:
                post_data = asyncio.run(ai_service.generate_post_content(
                    topic=topic,
                    tone=tone,
                    length=length,
                    optimize_engagement=optimize_engagement,
                    add_hashtags=add_hashtags
                ))
                
                if isinstance(post_data, dict) and all(key in post_data for key in ["title", "content", "hashtags", "optimal_time", "estimated_engagement"]):
                    # Post-Vorschau in einer Card
                    st.markdown("""
                    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='color: #0A66C2; margin-bottom: 15px;'>{title}</h3>
                        <p style='white-space: pre-line; margin-bottom: 20px;'>{content}</p>
                        {hashtags}
                        <div style='color: #666; font-size: 0.9em; margin-top: 15px;'>
                            Optimale Veröffentlichungszeit: {optimal_time} Uhr<br>
                            Geschätztes Engagement: {engagement}%
                        </div>
                    </div>
                    """.format(
                        title=post_data["title"],
                        content=post_data["content"],
                        hashtags=f"<div style='color: #0A66C2; margin-top: 10px;'>{' '.join(post_data['hashtags'])}</div>" if post_data["hashtags"] else "",
                        optimal_time=post_data["optimal_time"],
                        engagement=post_data["estimated_engagement"]
                    ), unsafe_allow_html=True)
                    
                    # Bild-Vorschau
                    if uploaded_file:
                        st.image(uploaded_file, caption="Hochgeladenes Bild", use_column_width=True)
                    
                    # Veröffentlichungs-Bereich
                    st.markdown("---")
                    st.markdown("### Veröffentlichung")
                    
                    # Zeitplanung und Veröffentlichung in Tabs
                    publish_tab, schedule_tab = st.tabs(["Jetzt veröffentlichen", "Zeitlich planen"])
                    
                    with publish_tab:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            confirm_publish = st.checkbox("Ich habe den Post überprüft und möchte ihn jetzt veröffentlichen")
                        with col2:
                            if confirm_publish:
                                if st.button("Jetzt veröffentlichen", type="primary", use_container_width=True):
                                    try:
                                        if not linkedin_service.is_logged_in:
                                            st.error("Nicht bei LinkedIn angemeldet. Bitte melden Sie sich zuerst an.")
                                            return
                                            
                                        with st.spinner("Veröffentliche Post auf LinkedIn..."):
                                            # Post veröffentlichen
                                            success = asyncio.run(linkedin_service.publish_post(
                                                content=post_data["content"],
                                                title=post_data["title"],
                                                hashtags=post_data["hashtags"],
                                                image_path=uploaded_file.name if uploaded_file else None
                                            ))
                                            
                                            if success:
                                                st.success("🎉 Post wurde erfolgreich auf LinkedIn veröffentlicht!")
                                                # Aktivität speichern
                                                post_draft_agent.log_activity("Post veröffentlicht", post_data["title"])
                                            else:
                                                st.error("Post konnte nicht veröffentlicht werden. Bitte überprüfen Sie Ihre LinkedIn-Verbindung.")
                                    except Exception as e:
                                        st.error(f"Fehler bei der Veröffentlichung: {str(e)}")
                    
                    with schedule_tab:
                        col1, col2 = st.columns(2)
                        with col1:
                            post_date = st.date_input("Datum")
                        with col2:
                            post_time = st.time_input("Uhrzeit", value=datetime.strptime(post_data["optimal_time"], "%H:%M").time())
                        
                        confirm_schedule = st.checkbox("Ich habe den Post überprüft und möchte ihn zum gewählten Zeitpunkt veröffentlichen")
                        if confirm_schedule:
                            if st.button("Planung bestätigen", type="primary", use_container_width=True):
                                scheduled_time = datetime.combine(post_date, post_time)
                                try:
                                    # Post planen
                                    success = asyncio.run(linkedin_service.schedule_post(
                                        content=post_data["content"],
                                        title=post_data["title"],
                                        hashtags=post_data["hashtags"],
                                        scheduled_time=scheduled_time,
                                        image_path=uploaded_file.name if uploaded_file else None
                                    ))
                                    
                                    if success:
                                        st.success(f"🎉 Post wurde erfolgreich für {scheduled_time.strftime('%d.%m.%Y um %H:%M')} Uhr geplant!")
                                        # Aktivität speichern
                                        post_draft_agent.log_activity("Post geplant", post_data["title"], scheduled_time)
                                    else:
                                        st.error("Post konnte nicht geplant werden. Bitte überprüfen Sie Ihre LinkedIn-Verbindung.")
                                except LinkedInError as e:
                                    st.error(f"LinkedIn-Fehler: {str(e)}")
                                except Exception as e:
                                    st.error(f"Fehler bei der Planung: {str(e)}")
                
                else:
                    st.error("Fehlerhafte Antwort vom AI-Service. Bitte versuchen Sie es erneut.")
                
            except Exception as e:
                st.error(f"Fehler bei der Post-Generierung: {str(e)}")
                st.error("Bitte versuchen Sie es erneut oder kontaktieren Sie den Support.")

# Lade Umgebungsvariablen
load_dotenv()

# LinkedIn-Service initialisieren
linkedin_service = LinkedInService()

async def initialize_linkedin():
    """Initialisiert die LinkedIn-Verbindung mit Credentials aus .env"""
    try:
        # Überprüfe ob die notwendigen Umgebungsvariablen existieren
        required_vars = ['LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET', 'LINKEDIN_EMAIL', 'LINKEDIN_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            st.error(f"Fehlende LinkedIn-Credentials in .env: {', '.join(missing_vars)}")
            return False
            
        if not st.session_state.get('linkedin_initialized', False):
            with st.spinner("Verbinde mit LinkedIn..."):
                await linkedin_service.initialize()
                st.session_state.linkedin_initialized = True
                st.success("🔗 Erfolgreich mit LinkedIn verbunden!")
        return True
    except Exception as e:
        st.error(f"Fehler bei der LinkedIn-Verbindung: {str(e)}")
        return False

# Automatische LinkedIn-Initialisierung beim Start
if 'linkedin_initialized' not in st.session_state:
    st.session_state.linkedin_initialized = asyncio.run(initialize_linkedin())

# Initialisiere Services
ai_service = AIService()

# Initialisiere Agenten
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
    show_post_creation()

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
    st.header("🛠️ Einstellungen")
    
    # LinkedIn-Verbindungsstatus anzeigen
    st.subheader("LinkedIn-Verbindung")
    if st.session_state.get('linkedin_initialized', False):
        st.success("✅ Mit LinkedIn verbunden")
        if st.button("LinkedIn-Verbindung erneuern"):
            st.session_state.linkedin_initialized = asyncio.run(initialize_linkedin())
    else:
        st.error("❌ Nicht mit LinkedIn verbunden")
        if st.button("Mit LinkedIn verbinden"):
            st.session_state.linkedin_initialized = asyncio.run(initialize_linkedin())

    # Automatisierungseinstellungen
    st.subheader("Automatisierungseinstellungen")
    auto_settings = {
        "post_frequency": st.selectbox(
            "Post-Häufigkeit",
            ["Täglich", "Wöchentlich", "Monatlich"],
            index=1
        ),
        "max_posts_per_day": st.number_input(
            "Maximale Posts pro Tag",
            min_value=1,
            max_value=5,
            value=2
        ),
        "working_hours": st.slider(
            "Arbeitszeiten (Stunden)",
            min_value=0,
            max_value=23,
            value=(9, 17)
        )
    }

# Überprüfen Sie den Login-Status
if not linkedin_service.is_logged_in:
    st.error("Nicht bei LinkedIn angemeldet. Bitte überprüfen Sie Ihre Anmeldedaten.")