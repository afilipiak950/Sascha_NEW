# LinkedIn Growth Agent

Ein automatisierter Agent für LinkedIn-Wachstum und Engagement, der verschiedene KI-gestützte Funktionen bietet.

## Features

- **Interaktions-Agent**: Automatisches Liken und Kommentieren von Posts in der Zielgruppe
- **Post-Draft-Agent**: KI-gestützte Erstellung von LinkedIn-Posts
- **Vernetzungs-Agent**: Automatisiertes Aufbauen von Verbindungen mit personalisierten Nachrichten
- **Hashtag-Agent**: Automatisches Kommentieren von Posts mit bestimmten Hashtags

## Technologie-Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Datenbank**: PostgreSQL
- **Browser-Automation**: Playwright
- **KI-Integration**: OpenAI GPT
- **Scheduler**: APScheduler

## Installation

1. Repository klonen:
```bash
git clone https://github.com/yourusername/linkedin-growth-agent.git
cd linkedin-growth-agent
```

2. Python-Umgebung erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. PostgreSQL-Datenbank einrichten:
```bash
createdb linkedin_agent
```

5. `.env`-Datei erstellen:
```env
# Datenbank
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=linkedin_agent

# LinkedIn
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

# OpenAI
OPENAI_API_KEY=your_api_key

# Konfiguration
POSTS_PER_WEEK=3
CONNECTIONS_PER_DAY=39
MAX_INTERACTIONS_PER_DAY=50
TARGET_HASHTAGS=["marketing", "sales", "ai", "digitalmarketing", "business"]
```

## Verwendung

1. Backend starten:
```bash
uvicorn main:app --reload
```

2. Frontend starten:
```bash
streamlit run streamlit_app.py
```

3. Öffnen Sie http://localhost:8501 im Browser

## Konfiguration

### LinkedIn-Einstellungen

- E-Mail und Passwort in der `.env`-Datei konfigurieren
- Browser-Automation-Einstellungen anpassen (Headless-Modus, User-Agent)

### Agent-Einstellungen

- Posts pro Woche (Standard: 3)
- Verbindungen pro Tag (Standard: 39)
- Maximale Interaktionen pro Tag
- Ziel-Hashtags für Monitoring

### Zeitplan-Einstellungen

- Post-Erstellung: Montag, Mittwoch, Freitag um 10:00 Uhr
- Vernetzung: Täglich um 9:00 Uhr
- Follow-ups: Täglich um 14:00 Uhr
- Interaktionen: Mehrmals täglich (11, 13, 15, 17 Uhr)
- Hashtag-Kommentare: Mehrmals täglich (10, 12, 14, 16 Uhr)

## Sicherheitshinweise

- Verwenden Sie sichere Passwörter
- Schützen Sie Ihre API-Keys
- Beachten Sie die LinkedIn-Nutzungsbedingungen
- Setzen Sie angemessene Rate-Limits

## Entwicklung

### Code-Struktur

```
linkedin-growth-agent/
├── app/
│   ├── agents/
│   │   ├── interaction_agent.py
│   │   ├── post_draft_agent.py
│   │   ├── connection_agent.py
│   │   └── hashtag_agent.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   ├── base.py
│   │   ├── post.py
│   │   ├── interaction.py
│   │   ├── connection.py
│   │   └── comment.py
│   ├── services/
│   │   ├── linkedin_service.py
│   │   └── ai_service.py
│   └── scheduler.py
├── main.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

### Neue Features hinzufügen

1. Agent-Klasse in `app/agents/` erstellen
2. Service-Funktionen in `app/services/` implementieren
3. Datenbank-Modelle in `app/models/` definieren
4. Frontend-Komponenten in `streamlit_app.py` hinzufügen
5. Scheduler-Jobs in `app/scheduler.py` konfigurieren

## Lizenz

MIT License

## Beitragen

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen 