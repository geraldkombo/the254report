# MajiWatch Kenya — Water & Sanitation Intelligence Platform

MajiWatch Kenya is an open-source, desktop-deployable intelligence platform that monitors Kenya’s water and sanitation sector at county level (47 counties). It unifies public WASH datasets into nightly scores, alert thresholds, and map-first operational visibility.

## What You Get
- Nightly county scores (0–100): Water Access, Sanitation Coverage, Water Quality, Utility Performance, Governance, Climate Resilience, and Composite.
- Threshold alerts: Watch / Warning / Emergency, with Emergency auto-generating a PDF county brief.
- REST API + OpenAPI docs and CSV exports.
- Desktop-friendly web dashboard with interactive map (choropleths + water point layer).
- One-command deploy on any modern desktop via Docker Compose.

## Stack (Free / Open Source)
- Gateway (Auth/Admin/Portal): Laravel 13 (PHP)
- Backend API: FastAPI (Python)
- Jobs: Celery + Celery Beat, Redis
- Database: PostgreSQL + PostGIS
- Frontend: React + TypeScript + MapLibre GL
- PDF: WeasyPrint
- Deploy: Docker Compose

## Quickstart
1) Prerequisites
- Docker Desktop (or Docker Engine) with Docker Compose

2) Configure environment
```bash
cp .env.example .env
```
Edit `.env` and set:
- `API_KEY_CHANGE_ME` to a strong value (used for protected endpoints)

3) Start everything
```bash
docker compose up -d --build
```

4) Open
- Portal (Laravel): http://localhost:3000/
- Dashboard (React): http://localhost:3000/app/
- Admin (Laravel): http://localhost:3000/admin
- API docs (Swagger): http://localhost:3000/api/docs

Mobile-first notes:
- Phones on the same Wi‑Fi can open the dashboard at `http://<host-ip>:3000` (where `<host-ip>` is the laptop/desktop running Docker).
- The web UI is installable as a lightweight PWA (Add to Home Screen). It caches key screens and uses an offline fallback map style.

## Contact
- Admin: geraldshikunyi@gmail.com

## Deployment
- [DEPLOYMENT.md](DEPLOYMENT.md)

## Press kit
- [presskit/README.md](presskit/README.md)

## Nightly Pipeline
Celery Beat triggers the nightly pipeline (UTC):
1) Ingest (connectors + baseline bundle)
2) Compute county scores
3) Evaluate alerts (Watch/Warning/Emergency)
4) Generate Emergency PDF reports

Manual trigger (requires API key):
```bash
curl -X POST http://localhost:8000/compute/scores \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $(cat .env | grep API_KEY_CHANGE_ME | cut -d= -f2)" \
  -d '{"year": 2026, "period": "2026-04-30"}'
```

## Scoring (Default Weights)
Composite score = weighted average:
- Water Access: 0.25
- Sanitation: 0.25
- Water Quality: 0.15
- Utility Performance: 0.15
- Governance: 0.10
- Climate Resilience: 0.10

Alert rules:
- Composite < 60 → Watch
- Composite < 45 OR open defecation > 30% OR NRW > 50% OR lpcd < 20 → Warning
- Composite < 30 OR cholera/outbreak signal → Emergency (PDF generated)

## API
Core endpoints:
- `GET /health`
- `GET /counties` (GeoJSON)
- `GET /scores/{county_code}`
- `GET /scores/latest`
- `GET /scores?year=2025`
- `GET /alerts/active`
- `PATCH /alerts/{id}/resolve` (API key)
- `GET /export/scores?year=2025` (CSV)
- `GET /export/waterpoints?county=001` (CSV)
- `POST /compute/scores` (API key)
- `POST /lookup/waterpoint` (lat/lng → nearest)
- `GET /waterpoints` (GeoJSON)
- `GET /tiles/waterpoints/{z}/{x}/{y}.pbf` (vector tiles)
- `GET /datasources`
- `GET /oracle/water-quality/latest` (signed feed; requires `ORACLE_SIGNING_SECRET`)

## Data Sources
Baseline (required by the project brief) and additional high-value sources are documented in:
- [.trae/documents/PRD.md](.trae/documents/PRD.md)

This repository ships with a deterministic baseline bundle for immediate usability, plus connectors and a data model designed to support production ingestion from authoritative public sources (WASREB, WRA, HisKenya/DHIS2, JMP, NDMA, CHIRPS, WPDx, and others).

## Funding Alignment
- [OPPORTUNITIES.md](file:///workspace/OPPORTUNITIES.md)
- [OPPORTUNITIES.md](OPPORTUNITIES.md)
- [FUNDING.md](FUNDING.md)

## Test Script
Run:
```bash
./scripts/test.sh
```
