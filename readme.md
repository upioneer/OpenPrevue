# OpenPrevue

Self-hosted local event aggregator and interactive retro display system styled after 1990s scrolling cable channel guides.

## Overview

OpenPrevue aggregates local event listings across developer ticketing APIs and direct venue sources, normalizes and deduplicates them into an internal SQLite datastore, and renders a split-screen dashboard suitable for wall monitors, smart televisions, tablets, and desktop browsers.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 SPA + Vite + Tailwind CSS v4 |
| Backend | Python 3.12+ with FastAPI (Async REST) |
| Database | SQLite 3 with Write-Ahead Logging (WAL) |
| Scheduler | APScheduler (AsyncIOScheduler) |
| Container | Docker and Docker Compose (Multi-stage build) |
| Testing | pytest + pytest-asyncio (backend), Vitest (frontend) |

## Getting Started

### Prerequisites

* Python >= 3.12
* Node.js >= 20
* Docker and Docker Compose (optional for containerized deployment)

### Local Development Setup

1. Clone repository:

```bash
git clone https://github.com/[USERNAME]/OpenPrevue.git
cd OpenPrevue
```

2. Copy environment template:

```bash
cp .env.example .env
```

3. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

4. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

5. Run backend server:

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
```

6. Run frontend dev server:

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` in your browser.

### Docker Deployment

To build and launch the containerized stack:

```bash
docker compose up -d --build
```

Access the dashboard at `http://localhost:8080`.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── core/            # Config and logging
│   │   ├── db/              # SQLite session and schema
│   │   ├── providers/       # Ingestion adapters (mock, APIs)
│   │   ├── schemas/         # Pydantic data models
│   │   └── services/        # Deduplication, seeder, ingestion
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # HTTP client
│   │   ├── components/      # Spotlight, Ribbon, Timeline
│   │   ├── styles/          # Retro CRT CSS tokens
│   │   ├── types/           # TypeScript interfaces
│   │   └── views/           # Dashboard & Settings views
│   ├── package.json
│   └── vite.config.ts
├── tests/                   # Backend and integration tests
├── project_details/         # Architectural specs and changelogs
├── Dockerfile               # Multi-stage production container build
├── docker-compose.yml       # Production Compose specification
└── pytest.ini               # Test configuration
```

## Running Tests

Execute backend test suite:

```bash
pytest -v
```

Build frontend production bundle:

```bash
cd frontend
npm run build
```

## License

See [LICENSE.md](./LICENSE.md) for license details.
