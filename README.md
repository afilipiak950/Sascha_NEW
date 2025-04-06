# LinkedIn Growth Agent

Ein Frontend für die Verwaltung und Automatisierung von LinkedIn-Aktivitäten.

## Funktionen

- **Authentifizierung**: Sichere Anmeldung mit Token-basierter Authentifizierung
- **Dashboard**: Übersicht über Beiträge, Interaktionen und Statistiken
- **Beitragsverwaltung**: Erstellen, Bearbeiten und Planen von LinkedIn-Beiträgen
- **Einstellungen**: Konfiguration von LinkedIn-Anmeldedaten, OpenAI API, Automatisierungseinstellungen und mehr

## Installation

1. Klonen Sie das Repository:
   ```bash
   git clone https://github.com/yourusername/linkedin-growth-agent.git
   cd linkedin-growth-agent
   ```

2. Installieren Sie die Abhängigkeiten:
   ```bash
   npm install
   ```

3. Erstellen Sie eine `.env`-Datei im Root-Verzeichnis:
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

## Entwicklung

Starten Sie die Entwicklungsumgebung:
```bash
npm start
```

Die Anwendung ist dann unter `http://localhost:3000` verfügbar.

## Build

Erstellen Sie einen Production-Build:
```bash
npm run build
```

Der Build wird im `build`-Verzeichnis erstellt.

## Deployment

### Vercel

1. Erstellen Sie ein Konto auf [Vercel](https://vercel.com)
2. Verbinden Sie Ihr GitHub-Repository
3. Konfigurieren Sie die Umgebungsvariablen in den Vercel-Projekteinstellungen
4. Deployen Sie die Anwendung

### Streamlit Cloud (Alternative)

1. Erstellen Sie ein Konto auf [Streamlit Cloud](https://streamlit.io/cloud)
2. Verbinden Sie Ihr GitHub-Repository
3. Konfigurieren Sie die Umgebungsvariablen
4. Deployen Sie die Anwendung

## Projektstruktur

```
frontend/
  ├── src/
  │   ├── components/
  │   │   ├── Auth.tsx
  │   │   ├── Dashboard.tsx
  │   │   ├── Layout.tsx
  │   │   ├── PostPreview.tsx
  │   │   └── Settings.tsx
  │   ├── App.tsx
  │   └── index.tsx
  ├── package.json
  └── tsconfig.json
```

## Backend-Integration

Das Frontend kommuniziert mit dem Backend über REST-API-Endpunkte:

- `POST /api/auth/login`: Authentifizierung
- `GET /api/posts`: Beiträge abrufen
- `POST /api/posts`: Neuen Beitrag erstellen
- `GET /api/interactions`: Interaktionen abrufen
- `GET /api/settings`: Einstellungen abrufen
- `PUT /api/settings`: Einstellungen aktualisieren

## Lizenz

MIT 