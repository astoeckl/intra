# Atikon CRM/Intranet System

Ein modernes CRM/Intranet-System für Lead-Management, Kundenbetreuung und Vertriebssteuerung.

## Tech Stack

### Backend
- **Python 3.12** mit **FastAPI**
- **SQLAlchemy 2.0** (async) mit **PostgreSQL**
- **Alembic** für Datenbankmigrationen
- **Pydantic** für Validierung

### Frontend
- **React 18** mit **TypeScript**
- **Vite** als Build-Tool
- **Tailwind CSS** für Styling
- **Shadcn UI** Komponenten
- **TanStack Query** für Data Fetching

### Infrastruktur
- **Docker** und **Docker Compose**
- **PostgreSQL 16**
- **Redis** für Caching

## Schnellstart

### Voraussetzungen
- Docker und Docker Compose
- Node.js 20+ (für lokale Frontend-Entwicklung)
- Python 3.12+ (für lokale Backend-Entwicklung)

### Mit Docker starten

```bash
# Services starten
docker compose up -d

# Logs anzeigen
docker compose logs -f
```

Die Anwendung ist dann erreichbar unter:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Dokumentation**: http://localhost:8000/docs

### Lokale Entwicklung

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # oder `venv\Scripts\activate` auf Windows
pip install -r requirements.txt

# Datenbankmigrationen ausführen
alembic upgrade head

# Server starten
uvicorn src.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Projektstruktur

```
intra/
├── backend/
│   ├── src/
│   │   ├── api/routes/      # API Endpoints
│   │   ├── core/            # Konfiguration, Datenbank
│   │   ├── models/          # SQLAlchemy Models
│   │   ├── schemas/         # Pydantic Schemas
│   │   ├── services/        # Business Logic
│   │   └── main.py          # FastAPI App
│   ├── alembic/             # Migrationen
│   └── tests/               # Tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React Komponenten
│   │   ├── pages/           # Seiten
│   │   ├── hooks/           # Custom Hooks
│   │   └── lib/             # Utilities
│   └── public/              # Static Files
└── docker-compose.yml
```

## Features (MVP)

- ✅ **Lead-Import**: CSV/Excel Import, automatische Erfassung
- ✅ **Kontaktsuche**: Schnelle Autocomplete-Suche (<200ms)
- ✅ **Callcenter-Ansicht**: Zentrale Arbeitsübersicht
- ✅ **Kontaktverlauf**: Timeline aller Interaktionen
- ✅ **Aufgabenverwaltung**: Mit Folgeaufgaben
- ✅ **E-Mail-Vorlagen**: Template-basierter Versand
- ✅ **Lead-Übersicht**: Tabellarisch mit Filtern
- ✅ **Landing Page**: Lead-Formular mit Auto-Erfassung

## API Endpoints

### Kontakte
- `GET /api/contacts` - Liste mit Pagination
- `GET /api/contacts/search?q=` - Autocomplete
- `GET /api/contacts/{id}` - Detail
- `POST /api/contacts` - Erstellen
- `PUT /api/contacts/{id}` - Bearbeiten

### Leads
- `GET /api/leads` - Liste mit Filtern
- `POST /api/leads/import` - CSV/Excel Import
- `PUT /api/leads/{id}` - Status ändern

### Aufgaben
- `GET /api/tasks` - Alle Aufgaben
- `GET /api/tasks/my` - Meine Aufgaben
- `POST /api/tasks/{id}/complete` - Abschließen + Folgeaufgabe

### Öffentlich (Landing Pages)
- `POST /api/public/leads` - Lead-Formular Submit

## Umgebungsvariablen

Backend (`.env`):
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:5173
```

Frontend (`.env`):
```env
VITE_API_URL=http://localhost:8000
```

## Lizenz

Proprietary - Atikon Marketing & Werbung GmbH
