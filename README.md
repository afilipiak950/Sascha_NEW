# LinkedIn Agent Orchestrator

Eine Streamlit-basierte Anwendung zur Automatisierung von LinkedIn-Aktivitäten.

## Features

- Automatische Post-Erstellung und -Veröffentlichung
- Intelligentes Networking und Verbindungsaufbau
- Automatisierte Interaktionen und Engagement
- Hashtag-basierte Content-Strategie
- Echtzeit-Analytics und Reporting

## Installation

1. Repository klonen:
```bash
git clone https://github.com/your-username/linkedin-agent-orchestrator.git
cd linkedin-agent-orchestrator
```

2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Umgebungsvariablen konfigurieren:
- Kopiere `.env.example` zu `.env`
- Fülle die notwendigen Umgebungsvariablen aus

## Verwendung

1. App lokal starten:
```bash
streamlit run streamlit_app.py
```

2. Auf Streamlit Cloud deployen:
- Repository auf GitHub pushen
- Auf [Streamlit Cloud](https://streamlit.io/cloud) anmelden
- Neues Projekt erstellen und Repository verbinden
- Umgebungsvariablen in den Streamlit Cloud Einstellungen konfigurieren

## Sicherheit

- Alle sensiblen Daten werden in Umgebungsvariablen gespeichert
- Rate-Limiting für API-Aufrufe implementiert
- Sichere Authentifizierung über OAuth2

## Lizenz

MIT License 